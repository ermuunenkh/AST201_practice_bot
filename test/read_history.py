import sqlite3
import sys
from config import DB_PATH


def read_history(user_id: int) -> None:
    if not DB_PATH.exists():
        print("Database not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM user_history WHERE user_id = ? ORDER BY answered_at",
        (user_id,),
    ).fetchall()
    conn.close()

    if not rows:
        print(f"No history found for user {user_id}.")
        return

    print(f"History for user {user_id} — {len(rows)} answer(s):\n")
    for row in rows:
        result = "✅" if row["is_correct"] else "❌"
        print(
            f"[{row['answered_at']}] "
            f"Q{row['question_id']} | {row['topic']} > {row['sub_topic']} | "
            f"Chose: {row['chosen']} {result}"
        )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test/read_history.py <user_id>")
        sys.exit(1)
    read_history(int(sys.argv[1]))
