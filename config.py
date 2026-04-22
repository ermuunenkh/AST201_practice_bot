import os
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_IDS = [
    int(os.environ['CHAT_ID_USER1']),
]

# Need to modify this code by hand.
USER_SCHEDULES = {
    CHAT_IDS[0]: {
        "window_start_hour": '12:00:00',  # 12:00:00
        "window_end_hour":   '23:59:00',  # 23:00:00
    }
}

# Exam deadline — Set the exam date and time here
EXAM_DEADLINE = datetime(2026, 4, 28, 14, 0, 0, tzinfo=ZoneInfo("America/Toronto"))

# Paths - Don't touch here
DB_PATH       = Path("database/astrobot.db")
SCHEMA_PATH   = Path("database/schema.sql")
POOL_PATH     = Path("database/question_pool.json")
RAW_POOL_PATH = Path("database/question_pool.json")
IMGS_DIR      = Path("database/imgs")
TEMP_DIR      = Path("database/temp")