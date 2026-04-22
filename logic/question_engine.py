import json
import math
import random
from config import POOL_PATH, USER_SCHEDULES
from database.db_handler import get_user_data

with open(POOL_PATH, encoding="utf-8") as f:
    _question_pool: list[dict] = json.load(f)

_all_subtopics = {q["sub_topic"] for q in _question_pool}
_n_subtopics   = len(_all_subtopics)
_TIER1         = math.ceil(_n_subtopics * 0.33)  # 33% of subtopics seen
_TIER2         = math.ceil(_n_subtopics * 0.66)  # 66% of subtopics seen


def _weighted_pick(new_pool: list, wrong_pool: list, p_new: float) -> dict:
    """Pick from new_pool with probability p_new, wrong_pool otherwise.
    Falls back gracefully if either pool is empty."""
    if not new_pool and not wrong_pool:
        return random.choice(_question_pool)
    if not new_pool:
        return random.choice(wrong_pool)
    if not wrong_pool:
        return random.choice(new_pool)
    return random.choice(new_pool) if random.random() < p_new else random.choice(wrong_pool)


def pick_question(user_id: int) -> dict:
    from logic.ml_picker import ml_pick

    df      = get_user_data(user_id, unique=False)
    df_uniq = df.drop_duplicates(subset="question_id", keep="last")
    n       = len(df_uniq)

    if n == 0:
        return random.choice(_question_pool)

    seen_subtopics  = set(df_uniq["sub_topic"].unique())
    wrong_subtopics = set(df_uniq[df_uniq["is_correct"] == 0]["sub_topic"].unique())

    new_pool   = [q for q in _question_pool if q["sub_topic"] not in seen_subtopics]
    wrong_pool = [q for q in _question_pool if q["sub_topic"] in wrong_subtopics]

    if seen_subtopics >= _all_subtopics:
        return ml_pick(df, _question_pool)

    if n <= _TIER1:
        return random.choice(new_pool) if new_pool else random.choice(_question_pool)

    if n <= _TIER2:
        return _weighted_pick(new_pool, wrong_pool, p_new=0.8)

    return _weighted_pick(new_pool, wrong_pool, p_new=0.6)


def get_user_schedule(chat_id: int) -> dict:
    return  USER_SCHEDULES[chat_id]


def calculate_delays(chat_id: int, n: int, window_seconds: int) -> list[int]:
    """
    Returns a list of n gap durations (seconds) for sequential scheduling:
      delays[0] = gap from window start → Q1
      delays[i] = gap from Q(i) → Q(i+1)

    TODO: use get_user_data(chat_id) to identify the user's most active
          periods and cluster questions around those times instead of
          distributing them evenly.
    """
    slot = window_seconds // n
    delays = []
    for _ in range(n):
        jitter = random.randint(0, slot // 3)
        delays.append(max(60, slot - slot // 6 + jitter))
    return delays

