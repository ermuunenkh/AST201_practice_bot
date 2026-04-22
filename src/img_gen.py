import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.collections import LineCollection
from pathlib import Path
from config import IMGS_DIR

# Realistic main sequence (temp K, luminosity L/Lsun)
_MS = np.array([
    (42000, 8.0e5),
    (30000, 1.5e5),
    (20000, 1.0e4),
    (10000, 60.0),
    ( 8000, 8.0),
    ( 7500, 5.0),
    ( 6500, 2.0),
    ( 5778, 1.0),
    ( 5000, 0.35),
    ( 4000, 0.06),
    ( 3500, 0.02),
    ( 3000, 0.004),
])

# Spectral types: (label, T_low, T_high, hex_color)
_SPECTRAL = [
    ("O", 30000, 42000, "#6666ff"),
    ("B", 10000, 30000, "#aaccff"),
    ("A",  7500, 10000, "#ffffff"),
    ("F",  6000,  7500, "#ffffcc"),
    ("G",  5000,  6000, "#ffdd66"),
    ("K",  3500,  5000, "#ff9933"),
    ("M",  2500,  3500, "#ff3311"),
]

# Solar radii lines: L/Lsun = (R/Rsun)^2 * (T/5778)^4
_SOLAR_RADII = [0.01, 0.1, 1, 10, 100, 1000]


def _ms_curve(n: int = 600):
    # Polynomial fit in log-log space for a smooth, natural curve
    log_T = np.log10(_MS[:, 0])
    log_L = np.log10(_MS[:, 1])
    coeffs = np.polyfit(log_T, log_L, deg=4)
    poly   = np.poly1d(coeffs)

    temps = np.logspace(np.log10(3000), np.log10(42000), n)
    lums  = 10 ** poly(np.log10(temps))
    return temps, lums


def _spectral_color(temp: float) -> tuple:
    """Return an RGB color matching the star's spectral class."""
    knots = {
        42000: (0.45, 0.55, 1.00),
        30000: (0.60, 0.75, 1.00),
        10000: (0.90, 0.92, 1.00),
         7500: (1.00, 1.00, 0.95),
         6000: (1.00, 0.92, 0.60),
         5000: (1.00, 0.70, 0.30),
         3500: (1.00, 0.35, 0.10),
         2500: (0.80, 0.10, 0.05),
    }
    keys = sorted(knots.keys(), reverse=True)
    for i in range(len(keys) - 1):
        t_hi, t_lo = keys[i], keys[i + 1]
        if t_hi >= temp >= t_lo:
            frac = (temp - t_lo) / (t_hi - t_lo)
            c0, c1 = np.array(knots[t_hi]), np.array(knots[t_lo])
            return tuple(frac * c0 + (1 - frac) * c1)
    return knots[keys[-1]]


def generate_hr_diagram(
    filename: str,
    dot: tuple[float, float] | None = None,
    highlight_region: str | None = None,
) -> Path:
    """
    Generate a clean HR diagram and save to IMGS_DIR/<filename>.png.

    Parameters
    ----------
    filename         : output filename without extension
    dot              : optional red dot at (temperature_K, luminosity_solar)
    highlight_region : optional region label to highlight —
                       "main_sequence" | "red_giants" | "supergiants" | "white_dwarfs"
    """
    IMGS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = IMGS_DIR / f"{filename}.png"

    BG = "#000000"
    fig = plt.figure(figsize=(10, 10), facecolor=BG)
    gs  = gridspec.GridSpec(2, 1, height_ratios=[22, 1], hspace=0.18)
    ax  = fig.add_subplot(gs[0])
    axb = fig.add_subplot(gs[1])

    ax.set_facecolor(BG)
    axb.set_facecolor(BG)

    # ── Axes limits & scale ──────────────────────────────────────────────────
    T_MIN, T_MAX = 2500, 45000
    L_MIN, L_MAX = 3e-5, 3e6
    ax.set_xlim(T_MAX, T_MIN)
    ax.set_ylim(L_MIN, L_MAX)
    ax.set_xscale("log")
    ax.set_yscale("log")

    # ── Solar radii lines ────────────────────────────────────────────────────
    T_grid = np.logspace(np.log10(T_MIN), np.log10(T_MAX), 300)
    for R in _SOLAR_RADII:
        L_r = R**2 * (T_grid / 5778)**4
        mask = (L_r > L_MIN) & (L_r < L_MAX)
        if mask.sum() < 2:
            continue
        ax.plot(T_grid[mask], L_r[mask], color="#333333", linewidth=0.7,
                linestyle="--", zorder=1)
        # label at the top edge
        idx = np.argmax(mask)
        lbl = f"{R} R☉" if R != 1 else "1 R☉"
        ax.text(T_grid[mask][0] * 0.97, L_r[mask][0] * 1.1, lbl,
                color="#555555", fontsize=7, rotation=-30, zorder=2)

    # ── Region labels ────────────────────────────────────────────────────────
    _regions = {
        "supergiants":  (12000, 3e5,  "S U P E R G I A N T S"),
        "red_giants":   ( 5000, 5e2,  "G I A N T S"),
        "main_sequence":(16000, 4e2,  "M A I N   S E Q U E N C E"),
        "white_dwarfs": (14000, 3e-3, "W H I T E   D W A R F S"),
    }
    for key, (tx, ty, label) in _regions.items():
        weight = "bold" if key == highlight_region else "normal"
        color  = "white" if key == highlight_region else "#aaaaaa"
        rot    = -50 if key == "main_sequence" else 0
        ax.text(tx, ty, label, color=color, fontsize=9.5,
                fontweight=weight, rotation=rot,
                ha="center", va="center", zorder=5,
                alpha=1.0 if key == highlight_region else 0.6)

    # ── Main sequence glow ───────────────────────────────────────────────────
    temps, lums = _ms_curve()

    # Outer glow layers (white-blue, wide)
    for lw, alpha in [(28, 0.025), (18, 0.05), (10, 0.10), (5, 0.18)]:
        ax.plot(temps, lums, color="#aac8ff", linewidth=lw,
                alpha=alpha, zorder=3, solid_capstyle="round")

    # Core: color gradient from blue (hot) to red (cool) using LineCollection
    points   = np.array([temps, lums]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    colors   = [_spectral_color(t) for t in temps[:-1]]
    lc = LineCollection(segments, colors=colors, linewidth=2.2, zorder=4,
                        capstyle="round")
    ax.add_collection(lc)

    # Bright white inner core for the glow highlight
    ax.plot(temps, lums, color="white", linewidth=0.6,
            alpha=0.5, zorder=5, solid_capstyle="round")

    # ── Optional red dot ─────────────────────────────────────────────────────
    if dot is not None:
        ax.scatter(*dot, color="red", s=120, zorder=10,
                   edgecolors="white", linewidths=0.8)

    # ── Axes styling ─────────────────────────────────────────────────────────
    ax.tick_params(axis="both", colors="#888888", which="both", labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor("#333333")

    ax.set_ylabel("Luminosity  (L / L☉)", color="#aaaaaa", fontsize=11)
    ax.set_xlabel("")
    ax.set_title("Hertzsprung – Russell Diagram",
                 color="white", fontsize=14, fontweight="bold", pad=14)

    # Y-axis: explicit ticks including 1 (Sun's luminosity)
    ax.set_yticks([1e-4, 1e-3, 1e-2, 1e-1, 1, 1e1, 1e2, 1e3, 1e4, 1e5, 1e6])
    ax.set_yticklabels(
        ["10⁻⁴", "10⁻³", "10⁻²", "10⁻¹", "1", "10", "10²", "10³", "10⁴", "10⁵", "10⁶"],
        color="#888888", fontsize=8,
    )
    # Highlight the Sun's luminosity tick
    for label in ax.get_yticklabels():
        if label.get_text() == "1":
            label.set_color("white")
            label.set_fontweight("bold")

    ax.set_xticks([])  # temperature labels shown on the color bar below

    # ── Spectral type color bar ───────────────────────────────────────────────
    # Build a gradient image across the temperature range
    bar_temps  = np.linspace(T_MAX, T_MIN, 512)
    spec_colors = {
        42000: (0.3, 0.3, 1.0),
        30000: (0.5, 0.6, 1.0),
        10000: (0.9, 0.9, 1.0),
        7500:  (1.0, 1.0, 0.85),
        6000:  (1.0, 0.9, 0.4),
        5000:  (1.0, 0.65, 0.2),
        3500:  (1.0, 0.3, 0.1),
        2500:  (0.8, 0.1, 0.05),
    }
    knots = sorted(spec_colors.keys(), reverse=True)
    gradient = np.zeros((1, 512, 3))
    for i, t in enumerate(bar_temps):
        # linear interp between knot colors
        for j in range(len(knots) - 1):
            if knots[j] >= t >= knots[j + 1]:
                frac = (t - knots[j + 1]) / (knots[j] - knots[j + 1])
                c0, c1 = np.array(spec_colors[knots[j]]), np.array(spec_colors[knots[j + 1]])
                gradient[0, i] = frac * c0 + (1 - frac) * c1
                break

    axb.imshow(gradient, aspect="auto",
               extent=[T_MAX, T_MIN, 0, 1])
    axb.set_xlim(T_MAX, T_MIN)
    axb.set_xscale("log")
    axb.set_yticks([])
    axb.set_xticks([40000, 30000, 10000, 7000, 6000, 5000, 4000, 3000])
    axb.set_xticklabels(
        ["40,000", "30,000", "10,000", "7,000", "6,000", "5,000", "4,000", "3,000"],
        color="#aaaaaa", fontsize=8,
    )
    axb.tick_params(axis="x", colors="#aaaaaa", length=4)

    # Spectral type letters
    for label, t_lo, t_hi, _ in _SPECTRAL:
        mid = np.exp((np.log(t_lo) + np.log(t_hi)) / 2)
        axb.text(mid, 0.5, label, ha="center", va="center",
                 color="black", fontsize=11, fontweight="bold")
        if t_hi < T_MAX:
            axb.axvline(t_hi, color="#00000055", linewidth=0.8)

    axb.set_xlabel("Surface Temperature (Kelvin)", color="#aaaaaa",
                   fontsize=10, labelpad=6)

    plt.savefig(output_path, dpi=150, bbox_inches="tight",
                facecolor=BG)
    plt.close(fig)
    return output_path
