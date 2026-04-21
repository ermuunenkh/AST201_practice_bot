-- AstroBot database schema (SQLite)
-- This file is documentation only; tables are created by SQLAlchemy in database.py.

CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id       INTEGER UNIQUE NOT NULL,   -- Telegram chat_id (BigInt in Python)
    name          TEXT,                      -- Display name from Telegram
    timezone      TEXT DEFAULT 'UTC',        -- IANA timezone string
    registered_at TEXT DEFAULT (datetime('now')),
    is_active     INTEGER DEFAULT 1          -- 0 = soft-deleted / blocked
);

CREATE TABLE questions (
    id           TEXT PRIMARY KEY,           -- e.g. "AST_001"
    topic        TEXT NOT NULL,              -- e.g. "Stellar Evolution"
    subtopic     TEXT,                       -- e.g. "HR Diagram"
    q_type       TEXT NOT NULL,              -- "MCQ" or "TrueFalse"
    difficulty   INTEGER DEFAULT 2,          -- 1=easy, 2=medium, 3=hard
    text         TEXT NOT NULL,              -- Question body
    choices_json TEXT,                       -- JSON array ["A) ...", "B) ..."] for MCQ
    answer       TEXT NOT NULL,              -- Correct option letter, e.g. "A" or "True"
    explanation  TEXT,                       -- Shown after answer is revealed
    image_path   TEXT,                       -- Relative path to image file, or NULL
    created_at   TEXT DEFAULT (datetime('now'))
);

CREATE TABLE answers (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id           INTEGER NOT NULL REFERENCES users(chat_id),
    question_id       TEXT    NOT NULL REFERENCES questions(id),
    chosen            TEXT,                  -- Option the user picked
    is_correct        INTEGER,               -- 1=correct, 0=wrong, NULL=unanswered
    response_time_sec REAL,                  -- Seconds from send to reply; NULL if no reply
    asked_at          TEXT,                  -- When the question was sent
    answered_at       TEXT                   -- When the user replied
);

CREATE TABLE topic_scores (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL REFERENCES users(chat_id),
    topic         TEXT    NOT NULL,
    correct       INTEGER DEFAULT 0,         -- Cumulative correct answers for this topic
    total         INTEGER DEFAULT 0,         -- Cumulative questions attempted
    last_asked_at TEXT,                      -- Used for spaced-repetition scheduling
    UNIQUE (user_id, topic)
);

CREATE TABLE send_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(chat_id),
    question_id TEXT    NOT NULL REFERENCES questions(id),
    sent_at     TEXT DEFAULT (datetime('now')),
    was_answered INTEGER DEFAULT 0          -- 1 once user replies
);

CREATE TABLE user_activity (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER NOT NULL REFERENCES users(chat_id),
    hour_of_day      INTEGER NOT NULL,       -- 0–23 (UTC)
    day_of_week      INTEGER NOT NULL,       -- 0=Monday … 6=Sunday
    avg_response_sec REAL,                   -- Running average response latency
    response_rate    REAL,                   -- 0.0–1.0 fraction of questions answered
    sample_count     INTEGER DEFAULT 0,      -- Number of observations in the averages
    UNIQUE (user_id, hour_of_day, day_of_week)
);
