import json
import math
import random
import pandas as pd
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


def calculate_delays(chat_id: int, n: int, window_start: str, window_end: str) -> list[int]:
    """
    Returns a list of n gap durations (seconds) for sequential scheduling:
      delays[0] = gap from window start → Q1
      delays[i] = gap from Q(i) → Q(i+1)

    Uses gravitational force field over 10-min bins: each bin attracts slots
    proportional to its answer mass and inversely proportional to distance².
    Slots are placed greedily at force peaks with 10-min suppression zones.
    Falls back to equal spacing if no in-window history exists.
    """
    MIN_GAP_MIN = 10  # minutes
    BIN_SIZE    = 10  # minutes

    sh, sm = map(int, window_start.split(":"))
    eh, em = map(int, window_end.split(":"))
    window_start_min = sh * 60 + sm
    window_end_min   = eh * 60 + em
    window_len_min   = window_end_min - window_start_min

    def _equal_spacing() -> list[int]:
        slot = (window_len_min * 60) // n
        return [max(MIN_GAP_MIN * 60, slot + random.randint(-slot // 6, slot // 6)) for _ in range(n)]

    df = get_user_data(chat_id)
    if df.empty:
        return _equal_spacing()

    df["answered_at"]  = pd.to_datetime(df["answered_at"])
    df["minute_of_day"] = df["answered_at"].dt.hour * 60 + df["answered_at"].dt.minute

    # --- Build 10-min bin masses (relative to window start) ---
    n_bins = max(1, window_len_min // BIN_SIZE)
    masses = [0] * n_bins
    for mod in df["minute_of_day"]:
        if window_start_min <= mod < window_end_min:
            idx = min((mod - window_start_min) // BIN_SIZE, n_bins - 1)
            masses[idx] += 1

    if sum(masses) == 0:
        return _equal_spacing()

    # --- Compute gravitational force field over every minute in the window ---
    force = [0.0] * window_len_min
    for t in range(window_len_min):
        for b, mass in enumerate(masses):
            if mass == 0:
                continue
            bin_center = b * BIN_SIZE + BIN_SIZE // 2
            dist = abs(t - bin_center)
            force[t] += mass / max(1, dist ** 2)

    # --- Greedy slot placement with mass decay ---
    DECAY = 0.1  # bin mass multiplier after a slot is placed near it
    masses_live = masses[:]
    offsets_min = []

    for _ in range(n):
        # Recompute force field from current (decayed) masses
        force_field = [0.0] * window_len_min
        for t in range(window_len_min):
            for b, mass in enumerate(masses_live):
                if mass == 0:
                    continue
                bin_center = b * BIN_SIZE + BIN_SIZE // 2
                dist = abs(t - bin_center)
                force_field[t] += mass / max(1, dist ** 2)

        max_force = max(force_field)
        candidates = [t for t, f in enumerate(force_field) if f >= max_force * 0.99]
        peak = random.choice(candidates)
        offsets_min.append(min(peak + random.randint(0, BIN_SIZE - 1), window_len_min - 1))

        # Decay bins within MIN_GAP of the placed slot
        for b in range(len(masses_live)):
            bin_center = b * BIN_SIZE + BIN_SIZE // 2
            if abs(peak - bin_center) <= MIN_GAP_MIN:
                masses_live[b] *= DECAY

    offsets_min = sorted(offsets_min)

    # --- Convert absolute offsets → sequential gap durations ---
    delays = []
    prev = 0
    for o in offsets_min:
        gap = max(MIN_GAP_MIN * 60, (o - prev) * 60)
        delays.append(gap)
        prev = o
    return delays

