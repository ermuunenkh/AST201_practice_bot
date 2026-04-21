import os
import logging
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import FancyArrowPatch

logger = logging.getLogger(__name__)

IMAGE_DIR = "data/images"
DARK_BG = "#1a1a2e"
AXIS_COLOR = "white"
FIG_SIZE = (8, 6)
DPI = 100


def ensure_image_dir():
    os.makedirs(IMAGE_DIR, exist_ok=True)
    os.makedirs("data/models", exist_ok=True)


def _apply_dark_theme(fig, ax):
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)
    ax.spines[:].set_color(AXIS_COLOR)
    ax.tick_params(colors=AXIS_COLOR, labelcolor=AXIS_COLOR)
    ax.xaxis.label.set_color(AXIS_COLOR)
    ax.yaxis.label.set_color(AXIS_COLOR)
    ax.title.set_color(AXIS_COLOR)


def generate_hr_diagram(highlight_point=None, output_path=None) -> str:
    ensure_image_dir()
    if output_path is None:
        output_path = os.path.join(IMAGE_DIR, "hr_diagram.png")

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    _apply_dark_theme(fig, ax)

    rng = np.random.default_rng(42)

    # Temperature colormap: blue (hot) → red (cool)
    temp_norm = mcolors.LogNorm(vmin=3000, vmax=30000)
    cmap = plt.cm.RdYlBu_r

    def scatter_region(temps, lums, label, size=20, alpha=0.7):
        colors = [cmap(temp_norm(t)) for t in temps]
        ax.scatter(temps, lums, c=colors, s=size, alpha=alpha, label=label, zorder=3)

    # Main sequence diagonal band
    ms_temps = np.logspace(np.log10(3500), np.log10(25000), 80)
    ms_lums = (ms_temps / 5778) ** 4 * rng.uniform(0.7, 1.3, len(ms_temps))
    scatter_region(ms_temps, ms_lums, "Main Sequence", size=25)
    ax.text(4500, 0.05, "Main Sequence", color="white", fontsize=8, alpha=0.8)

    # Giants upper right
    g_temps = rng.uniform(3500, 6000, 30)
    g_lums = rng.uniform(10, 200, 30)
    scatter_region(g_temps, g_lums, "Giants", size=60)
    ax.text(3700, 150, "Giants", color="white", fontsize=8, alpha=0.8)

    # Supergiants top band
    sg_temps = rng.uniform(3500, 20000, 15)
    sg_lums = rng.uniform(10000, 500000, 15)
    scatter_region(sg_temps, sg_lums, "Supergiants", size=120)
    ax.text(8000, 200000, "Supergiants", color="white", fontsize=8, alpha=0.8)

    # White dwarfs lower left
    wd_temps = rng.uniform(8000, 25000, 20)
    wd_lums = rng.uniform(0.001, 0.01, 20)
    scatter_region(wd_temps, wd_lums, "White Dwarfs", size=15)
    ax.text(9000, 0.002, "White Dwarfs", color="white", fontsize=8, alpha=0.8)

    if highlight_point is not None:
        temp, lum, label = highlight_point
        ax.scatter([temp], [lum], marker="*", color="red", s=300, zorder=5, label=label)
        ax.annotate(
            label,
            xy=(temp, lum),
            xytext=(temp * 1.4, lum * 3),
            color="red",
            fontsize=9,
            arrowprops=dict(arrowstyle="->", color="red"),
        )

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(30000, 3000)  # reversed: hot left, cool right
    ax.set_ylim(0.001, 1_000_000)
    ax.set_xlabel("Temperature (K)", color=AXIS_COLOR)
    ax.set_ylabel("Luminosity (L/L☉)", color=AXIS_COLOR)
    ax.set_title("Hertzsprung-Russell Diagram", color=AXIS_COLOR)

    plt.tight_layout()
    plt.savefig(output_path, facecolor=DARK_BG)
    plt.close(fig)
    logger.info("Generated HR diagram: %s", output_path)
    return output_path


def generate_light_curve(data_points: list, title: str, output_path=None) -> str:
    ensure_image_dir()
    if output_path is None:
        output_path = os.path.join(IMAGE_DIR, "light_curve.png")

    times = [p[0] for p in data_points]
    mags = [p[1] for p in data_points]

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    _apply_dark_theme(fig, ax)

    ax.plot(times, mags, color="cyan", linewidth=1.5, marker="o", markersize=3)
    ax.invert_yaxis()  # brighter = smaller magnitude = higher on plot
    ax.set_xlabel("Time (days)", color=AXIS_COLOR)
    ax.set_ylabel("Magnitude", color=AXIS_COLOR)
    ax.set_title(title, color=AXIS_COLOR)

    plt.tight_layout()
    plt.savefig(output_path, facecolor=DARK_BG)
    plt.close(fig)
    logger.info("Generated light curve: %s", output_path)
    return output_path


def generate_spectrum_plot(
    wavelengths: list,
    intensities: list,
    absorption_lines: list = None,
    output_path=None,
) -> str:
    ensure_image_dir()
    if output_path is None:
        output_path = os.path.join(IMAGE_DIR, "spectrum.png")

    wl = np.array(wavelengths)
    intensity = np.array(intensities)

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    _apply_dark_theme(fig, ax)

    # Color line by wavelength
    norm = mcolors.Normalize(vmin=wl.min(), vmax=wl.max())
    cmap = plt.cm.rainbow
    for i in range(len(wl) - 1):
        ax.plot(wl[i : i + 2], intensity[i : i + 2], color=cmap(norm(wl[i])), linewidth=2)

    if absorption_lines:
        for line_wl in absorption_lines:
            ax.axvline(line_wl, color="white", linestyle="--", alpha=0.6, linewidth=1)

    ax.set_xlabel("Wavelength (nm)", color=AXIS_COLOR)
    ax.set_ylabel("Intensity", color=AXIS_COLOR)
    ax.set_title("Stellar Spectrum", color=AXIS_COLOR)

    plt.tight_layout()
    plt.savefig(output_path, facecolor=DARK_BG)
    plt.close(fig)
    logger.info("Generated spectrum plot: %s", output_path)
    return output_path


def generate_solar_system_diagram(highlight_planet=None, output_path=None) -> str:
    ensure_image_dir()
    if output_path is None:
        output_path = os.path.join(IMAGE_DIR, "solar_system.png")

    planets = [
        ("Mercury", 1.0),
        ("Venus", 1.7),
        ("Earth", 2.4),
        ("Mars", 3.1),
        ("Jupiter", 4.2),
        ("Saturn", 5.5),
        ("Uranus", 6.8),
        ("Neptune", 8.0),
    ]

    fig, ax = plt.subplots(figsize=(8, 8), dpi=DPI)
    _apply_dark_theme(fig, ax)

    # Sun
    ax.scatter([0], [0], s=800, color="yellow", zorder=5)
    ax.text(0, 0.3, "Sun", color="yellow", ha="center", fontsize=9)

    for name, radius in planets:
        theta = np.linspace(0, 2 * np.pi, 300)
        ax.plot(radius * np.cos(theta), radius * np.sin(theta), color="grey", linewidth=0.8)
        color = "red" if name == highlight_planet else "steelblue"
        ax.scatter([radius], [0], s=60, color=color, zorder=4)
        ax.text(radius, 0.25, name, color=AXIS_COLOR, ha="center", fontsize=7)

    ax.set_aspect("equal")
    ax.set_xlim(-9, 9)
    ax.set_ylim(-9, 9)
    ax.axis("off")
    ax.set_title("Solar System (Schematic)", color=AXIS_COLOR)

    plt.tight_layout()
    plt.savefig(output_path, facecolor=DARK_BG)
    plt.close(fig)
    logger.info("Generated solar system diagram: %s", output_path)
    return output_path


def generate_all_sample_images() -> list[str]:
    ensure_image_dir()
    paths = []

    paths.append(
        generate_hr_diagram(output_path=os.path.join(IMAGE_DIR, "hr_diagram_basic.png"))
    )
    paths.append(
        generate_hr_diagram(
            highlight_point=(4000, 50, "Giant Star"),
            output_path=os.path.join(IMAGE_DIR, "hr_diagram_giants.png"),
        )
    )

    # Variable star light curve (Cepheid-like)
    t = np.linspace(0, 30, 200)
    mags = 8.0 + 0.5 * np.sin(2 * np.pi * t / 5.4) + 0.05 * np.random.randn(len(t))
    lc_data = list(zip(t.tolist(), mags.tolist()))
    paths.append(
        generate_light_curve(
            lc_data,
            "Cepheid Variable Star",
            output_path=os.path.join(IMAGE_DIR, "light_curve_variable.png"),
        )
    )

    # Solar spectrum (approximate visible range)
    wl = np.linspace(380, 700, 300)
    intensity = np.exp(-((wl - 550) ** 2) / (2 * 80**2)) + 0.02 * np.random.randn(len(wl))
    absorption = [393, 397, 430, 486, 527, 589, 656, 687]
    paths.append(
        generate_spectrum_plot(
            wl.tolist(),
            intensity.tolist(),
            absorption_lines=absorption,
            output_path=os.path.join(IMAGE_DIR, "spectrum_solar.png"),
        )
    )

    paths.append(
        generate_solar_system_diagram(
            output_path=os.path.join(IMAGE_DIR, "solar_system_basic.png")
        )
    )

    return paths


if __name__ == "__main__":
    generated = generate_all_sample_images()
    print("\nGenerated sample images:")
    for p in generated:
        size_kb = os.path.getsize(p) / 1024
        print(f"  {p}  ({size_kb:.1f} KB)")
