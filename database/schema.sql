CREATE TABLE IF NOT EXISTS user_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    topic       TEXT    NOT NULL,
    sub_topic   TEXT    NOT NULL,
    chosen      TEXT    NOT NULL,
    is_correct  INTEGER NOT NULL,  -- 1 = correct, 0 = wrong
    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
