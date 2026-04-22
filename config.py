import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_IDS = [
    int(os.environ['CHAT_ID_USER1']),
]

# Paths
DB_PATH       = Path("database/astrobot.db")
SCHEMA_PATH   = Path("database/schema.sql")
POOL_PATH     = Path("database/question_pool.json")
IMGS_DIR      = Path("database/imgs")
TEMP_DIR      = Path("database/temp")