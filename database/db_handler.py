import sqlite3
from config import DB_PATH, SCHEMA_PATH


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    if DB_PATH.exists():
        return
    with _connect() as conn:
        conn.executescript(SCHEMA_PATH.read_text())


def record_answer(user_id: int, question_id: int, topic: str, sub_topic: str, chosen: str, is_correct: bool) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO user_history (user_id, question_id, topic, sub_topic, chosen, is_correct) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, question_id, topic, sub_topic, chosen, int(is_correct)),
        )
