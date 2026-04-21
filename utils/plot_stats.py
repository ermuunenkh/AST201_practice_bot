import os
import logging
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

IMAGE_DIR = "data/images"
DARK_BG = "#1a1a2e"
AXIS_COLOR = "white"


def _apply_dark_theme(fig, ax):
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)
    ax.spines[:].set_color(AXIS_COLOR)
    ax.tick_params(colors=AXIS_COLOR, labelcolor=AXIS_COLOR)
    ax.xaxis.label.set_color(AXIS_COLOR)
    ax.yaxis.label.set_color(AXIS_COLOR)
    ax.title.set_color(AXIS_COLOR)


def plot_topic_accuracy(
    user_id: int,
    topic_scores: list[dict],
    output_path: str = None,
) -> str:
    """
    topic_scores: list of dicts with keys 'topic', 'correct', 'total'
    """
    os.makedirs(IMAGE_DIR, exist_ok=True)
    if output_path is None:
        output_path = os.path.join(IMAGE_DIR, f"stats_topics_{user_id}.png")

    topics = [s["topic"] for s in topic_scores]
    accuracies = [
        (s["correct"] / s["total"] * 100) if s["total"] > 0 else 0.0
        for s in topic_scores
    ]

    colors = []
    for acc in accuracies:
        if acc >= 70:
            colors.append("limegreen")
        elif acc >= 40:
            colors.append("gold")
        else:
            colors.append("tomato")

    fig, ax = plt.subplots(figsize=(8, max(4, len(topics) * 0.5 + 1)), dpi=100)
    _apply_dark_theme(fig, ax)

    y_pos = range(len(topics))
    ax.barh(list(y_pos), accuracies, color=colors, edgecolor="none")
    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(topics, color=AXIS_COLOR)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Accuracy (%)", color=AXIS_COLOR)
    ax.set_title("Your Performance by Topic", color=AXIS_COLOR)

    for i, acc in enumerate(accuracies):
        ax.text(acc + 1, i, f"{acc:.0f}%", va="center", color=AXIS_COLOR, fontsize=8)

    plt.tight_layout()
    plt.savefig(output_path, facecolor=DARK_BG)
    plt.close(fig)
    logger.info("Generated topic accuracy chart: %s", output_path)
    return output_path


def plot_activity_heatmap(
    user_id: int,
    activity_data: list[dict],
    output_path: str = None,
) -> str:
    """
    activity_data: list of dicts with keys 'dow' (0=Mon), 'hour_of_day', 'response_rate'
    """
    os.makedirs(IMAGE_DIR, exist_ok=True)
    if output_path is None:
        output_path = os.path.join(IMAGE_DIR, f"stats_heatmap_{user_id}.png")

    grid = np.full((7, 24), np.nan)
    for row in activity_data:
        dow = int(row["dow"])
        hour = int(row["hour_of_day"])
        rate = float(row.get("response_rate", 0.0))
        if 0 <= dow < 7 and 0 <= hour < 24:
            grid[dow, hour] = rate

    fig, ax = plt.subplots(figsize=(12, 4), dpi=100)
    _apply_dark_theme(fig, ax)

    # Custom colormap: grey for no-data, blue→green for rate
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "activity", ["#1a3a5c", "#00bfff", "#00e676"]
    )
    cmap.set_bad(color="#333333")

    masked = np.ma.masked_invalid(grid)
    im = ax.imshow(masked, aspect="auto", cmap=cmap, vmin=0, vmax=1, interpolation="nearest")

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    ax.set_yticks(range(7))
    ax.set_yticklabels(days, color=AXIS_COLOR)
    ax.set_xticks(range(0, 24, 2))
    ax.set_xticklabels([f"{h:02d}:00" for h in range(0, 24, 2)], color=AXIS_COLOR, fontsize=7)
    ax.set_xlabel("Hour of Day", color=AXIS_COLOR)
    ax.set_title("Your Response Patterns", color=AXIS_COLOR)

    cbar = plt.colorbar(im, ax=ax, fraction=0.02, pad=0.02)
    cbar.set_label("Response Rate", color=AXIS_COLOR)
    cbar.ax.yaxis.set_tick_params(color=AXIS_COLOR, labelcolor=AXIS_COLOR)

    plt.tight_layout()
    plt.savefig(output_path, facecolor=DARK_BG)
    plt.close(fig)
    logger.info("Generated activity heatmap: %s", output_path)
    return output_path
