import json
import random
from config import POOL_PATH, USER_SCHEDULES

with open(POOL_PATH, encoding="utf-8") as f:
    _question_pool: list[dict] = json.load(f)


def pick_question() -> dict:
    # TODO
    return random.choice(_question_pool)


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

