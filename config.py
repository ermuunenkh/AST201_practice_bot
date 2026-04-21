import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "YOUR_TOKEN_HERE")
DB_PATH: str = os.getenv("DB_PATH", "data/astrobot.db")

# Study group: name → Telegram chat_id (comment out missing users in .env)
_RAW_USERS = {
    "user1": os.getenv("CHAT_ID_USER1"),
    "user2": os.getenv("CHAT_ID_USER2"),
    "user3": os.getenv("CHAT_ID_USER3"),
}
USERS: dict[str, int] = {
    name: int(chat_id)
    for name, chat_id in _RAW_USERS.items()
    if chat_id is not None
}

SCHEDULER_INTERVAL_HOURS: int = 1
QUESTIONS_PER_DAY_DEFAULT: int = 3
MIN_RESPONSE_RATE_THRESHOLD: float = 0.2
SPACED_REPEAT_DAYS: int = 3
USE_RL_SCHEDULER: bool = False
USE_ML_DIFFICULTY: bool = False

MIN_QUESTIONS_PER_BATCH: int = 5
MAX_QUESTIONS_PER_BATCH: int = 20
DEFAULT_QUESTIONS_PER_BATCH: int = 5

QUESTION_IMAGE_DIR: str = "data/images/"
BATCH_SEND_INTERVAL_SEC: int = 30
