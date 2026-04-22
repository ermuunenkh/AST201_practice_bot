import json
import random
from config import POOL_PATH

with open(POOL_PATH, encoding="utf-8") as f:
    _question_pool: list[dict] = json.load(f)


def pick_question() -> dict:
    return random.choice(_question_pool)

