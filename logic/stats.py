import json
from datetime import datetime
from zoneinfo import ZoneInfo
from config import POOL_PATH, EXAM_DEADLINE
from database.db_handler import get_user_data

with open(POOL_PATH, encoding="utf-8") as f:
    _pool = json.load(f)

_all_subtopics     = {q["sub_topic"] for q in _pool}
_total_subtopics   = len(_all_subtopics)
_total_questions   = len(_pool)
_MIN_ATTEMPTS      = 3


def _pct(value: float) -> str:
    return f"{value * 100:.0f}%"


def _recent_accuracy(df, n: int) -> str:
    """Accuracy over last n unique questions answered."""
    if len(df) == 0:
        return "N/A"
    recent = df.tail(n)
    if len(recent) == 0:
        return "N/A"
    return _pct(recent["is_correct"].mean())


def _exam_countdown() -> str:
    now = datetime.now(tz=ZoneInfo("America/Toronto"))
    delta = EXAM_DEADLINE - now
    if delta.total_seconds() <= 0:
        return "Exam has passed"
    days  = delta.days
    hours = delta.seconds // 3600
    return f"{days}d {hours}h"


def build_stats_text(user_id: int) -> str:
    from bot.utils import escape

    df_full = get_user_data(user_id, unique=False)

    # Deduplicate by question_id keeping last answer — used for progress + recent accuracy
    df_uniq = df_full.drop_duplicates(subset="question_id", keep="last").sort_values("answered_at")

    n_subtopics_seen = df_uniq["sub_topic"].nunique() if not df_uniq.empty else 0
    n_questions_seen = len(df_uniq)

    # Top 3 strongest / weakest: per subtopic accuracy over full history, min 3 attempts
    top_strongest = []
    top_weakest   = []

    if not df_full.empty:
        subtopic_stats = (
            df_full.groupby("sub_topic")["is_correct"]
            .agg(["mean", "count"])
            .rename(columns={"mean": "accuracy", "count": "attempts"})
        )
        qualified = subtopic_stats[subtopic_stats["attempts"] >= _MIN_ATTEMPTS]

        if not qualified.empty:
            top_strongest = qualified.nlargest(3, "accuracy")[["accuracy"]].reset_index().values.tolist()
            top_weakest   = qualified.nsmallest(3, "accuracy")[["accuracy"]].reset_index().values.tolist()

    def _rank_lines(entries: list, label: str) -> list[str]:
        if not entries:
            return [f"*{label}* — _Not ready to assess_"]
        result = [f"*{label}*"]
        medals = ["🥇", "🥈", "🥉"]
        for i, (name, acc) in enumerate(entries):
            result.append(f"  {medals[i]} {escape(name)} `{_pct(acc)}`")
        return result

    lines = [
        "*📊 Your Stats*",
        "",
        "*Progress*",
        f"  Subtopics: `{n_subtopics_seen} / {_total_subtopics}`",
        f"  Questions: `{n_questions_seen} / {_total_questions}`",
        "",
        *_rank_lines(top_strongest, "Strongest"),
        "",
        *_rank_lines(top_weakest, "Weakest"),
        "",
        "*Recent Accuracy*",
        f"  Last 10:  `{_recent_accuracy(df_uniq, 10)}`",
        f"  Last 20:  `{_recent_accuracy(df_uniq, 20)}`",
        f"  Last 50:  `{_recent_accuracy(df_uniq, 50)}`",
        "",
        f"⏳ `{_exam_countdown()}` until exam",
    ]

    return "\n".join(lines)
