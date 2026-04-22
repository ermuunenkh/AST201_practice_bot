import sys
from database.db_handler import get_user_data

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test/read_history.py <user_id> [--unique]")
        sys.exit(1)

    user_id = int(sys.argv[1])
    unique = "--unique" in sys.argv

    df = get_user_data(user_id, unique=unique)

    if df.empty:
        print(f"No history found for user {user_id}.")
    else:
        print(f"History for user {user_id} — {len(df)} row(s):\n")
        print(df.to_string(index=False))
