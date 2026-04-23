from pathlib import Path
from PIL import Image
from config import IMGS_DIR, TEMP_DIR


def compress_images(quality: int = 60) -> None:
    IMGS_DIR.mkdir(parents=True, exist_ok=True)

    for src in IMGS_DIR.iterdir():
        if not src.is_file():
            continue
        if "_compressed" in src.name:
            continue
        if src.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            continue

        dest = IMGS_DIR / f"{src.stem}_compressed.jpg"
        with Image.open(src) as img:
            img.convert("RGB").save(dest, format="JPEG", quality=quality, optimize=True)
        src.unlink()


def decompress_image(original_path: str) -> Path:
    """Receives the original (uncompressed) image path from the question pool,
    derives the compressed filename, decompresses to temp, and returns the temp path."""
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    original = Path(original_path)
    compressed = original.parent / f"{original.stem}_compressed.jpg"
    temp_path  = TEMP_DIR / compressed.name

    with Image.open(compressed) as img:
        img.convert("RGB").save(temp_path, format="JPEG", quality=95)

    return temp_path
