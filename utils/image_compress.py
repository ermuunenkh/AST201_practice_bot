import os
import logging
from pathlib import Path
from PIL import Image

logger = logging.getLogger(__name__)


def get_image_size_kb(path: str) -> float:
    return os.path.getsize(path) / 1024


def compress_image(
    input_path: str,
    output_path: str = None,
    max_size_kb: int = 200,
    max_dimension: int = 1280,
) -> str:
    if output_path is None:
        p = Path(input_path)
        output_path = str(p.with_suffix(".jpg"))

    original_kb = get_image_size_kb(input_path)

    with Image.open(input_path) as img:
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        w, h = img.size
        if w > max_dimension or h > max_dimension:
            ratio = min(max_dimension / w, max_dimension / h)
            img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

        quality = 85
        img.save(output_path, "JPEG", quality=quality)

        while get_image_size_kb(output_path) > max_size_kb and quality > 30:
            quality -= 10
            img.save(output_path, "JPEG", quality=quality)

    compressed_kb = get_image_size_kb(output_path)
    logger.info(
        "Compressed %s: %.1f KB → %.1f KB (quality=%d)",
        input_path,
        original_kb,
        compressed_kb,
        quality,
    )
    return output_path


def compress_for_telegram(image_path: str) -> str:
    p = Path(image_path)
    output_path = str(p.parent / f"{p.stem}_tg.jpg")
    return compress_image(
        image_path,
        output_path=output_path,
        max_size_kb=200,
        max_dimension=1280,
    )


if __name__ == "__main__":
    import sys

    sample = "data/images/hr_diagram_basic.png"
    if not os.path.exists(sample):
        print(f"Sample image not found at {sample}. Run: python -m utils.image_gen first.")
        sys.exit(1)

    before_kb = get_image_size_kb(sample)
    out = compress_for_telegram(sample)
    after_kb = get_image_size_kb(out)
    print(f"Input:  {sample}  ({before_kb:.1f} KB)")
    print(f"Output: {out}  ({after_kb:.1f} KB)")
