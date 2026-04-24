# AST201 Practice Bot

A Telegram bot for University of Toronto students preparing for the AST201 (Stars and Galaxies) final exam. The bot sends multiple-choice astronomy questions daily within a configurable time window, tracks your performance, and uses machine learning to prioritize the topics you struggle with most.

> **Disclaimer:** All questions are generated from general course concepts. They are not guaranteed to appear on the actual final exam.

---

## Features

- **580 questions** across 23 topics and 93 subtopics
- **Daily pop-questions** automatically sent within your active window
- **On-demand questions** via `/ask`
- **Smart scheduling** — questions cluster around your historically active times using a gravitational force field model
- **Tiered question selection** — starts with new subtopics, gradually shifts toward weak areas
- **ML-based weakness detection** — when all subtopics are covered, uses scikit-learn to score and prioritize weak topics
- **Performance stats** via `/stats` — progress, top 3 strongest/weakest subtopics, recent accuracy, exam countdown
- **HR diagram questions** with programmatically generated images
- **Auto-shutdown** at exam deadline

---

## Requirements

- Python 3.12+
- A Telegram Bot token
- Telegram Chat IDs for each user

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/<your_username>/<your_repo>.git
cd AST201_practice_bot
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Create your `.env` file

Create a file named `.env` in the project root:

```
BOT_TOKEN=your_telegram_bot_token
CHAT_ID_USER1=123456789
CHAT_ID_USER2=987654321
```

Add or remove `CHAT_ID_USER*` lines for each user.

---

## Getting the Required Tokens

### Telegram Bot Token

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and follow the prompts
3. Copy the token it gives you — this is your `BOT_TOKEN`

### Telegram Chat IDs

1. Have each user open your bot on Telegram and tap **Start**
2. Run the helper script:
   ```bash
   python get_chat_id.py
   ```
3. Each user's **Chat ID** will print to the terminal when they message the bot
4. Press `Ctrl+C` to stop, then add the IDs to your `.env`

---

## Configuration

Edit `config.py` to configure schedules and the exam deadline:

```python
# Add one entry per user — must match CHAT_IDS order
USER_SCHEDULES = {
    CHAT_IDS[0]: {
        "window_start": "12:00",   # Start of daily question window (HH:MM)
        "window_end":   "23:59",   # End of daily question window (HH:MM)
        "n":            5,         # Number of questions per day
    },
    CHAT_IDS[1]: {
        "window_start": "10:00",
        "window_end":   "22:00",
        "n":            5,
    },
}

# Bot shuts down automatically at this date/time
EXAM_DEADLINE = datetime(2026, 4, 28, 14, 0, 0, tzinfo=ZoneInfo("America/Toronto"))
```

---

## Running the Bot

```bash
python main.py
```

On startup the bot will:
1. Initialize the SQLite database
2. Compress any new images in `database/imgs/`
3. Schedule daily question windows for each user
4. Begin polling for Telegram commands

---

## Bot Commands

| Command | Description |
|---|---|
| `/ask` | Get a question on demand |
| `/stats` | View your progress and performance stats |

---

## Question Pool Schema

Questions are stored in `database/question_pool.json` as a JSON array. Each question follows this schema:

```json
{
  "id": 1,
  "type": "MC",
  "topic": "TOPIC 4: MODELS OF GRAVITY",
  "sub_topic": "4.3 General Relativity (Curved Spacetime)",
  "question": "According to General Relativity, why does Earth orbit the Sun?",
  "options": {
    "A": "Option A text",
    "B": "Option B text",
    "C": "Option C text",
    "D": "Option D text",
    "E": "Option E text"
  },
  "answer": "D",
  "explanation": "Explanation of the correct answer.",
  "image": "database/imgs/id_1.png"
}
```

The `image` field is optional. It stores the **original** (uncompressed) path — the bot derives the compressed path automatically at runtime.

---

## Project Structure

```
AST201_practice_bot/
├── bot/
│   ├── handlers.py          # Telegram command handlers and scheduling
│   └── utils.py             # Message formatting, keyboards, image sending
├── database/
│   ├── db_handler.py        # SQLite connection and queries
│   ├── schema.sql           # Database schema
│   ├── question_pool.json   # All questions
│   ├── imgs/                # Compressed question images
│   └── temp/                # Temporary decompressed images (auto-cleaned)
├── logic/
│   ├── question_engine.py   # Question selection and delay calculation
│   ├── ml_picker.py         # ML-based weakness scoring
│   └── stats.py             # User statistics
├── src/
│   ├── img_gen.py           # HR diagram image generator
│   └── image_handler.py     # Image compression and decompression
├── logs/
│   └── logger.py            # Rotating file logger
├── test/
│   ├── testing_questions.py      # Validate question pool integrity
│   └── generate_hr_questions.py  # Generate HR diagram questions
├── main.py                  # Entry point
├── config.py                # All configuration constants
├── get_chat_id.py           # Helper to find Telegram Chat IDs
└── requirements.txt         # Python dependencies
```

---

## Logging

Logs are written to `logs/astrobot.log` with automatic rotation (200KB max, 3 backups). Each entry records:

- Bot startup
- User commands and answers
- Image compression / decompression status
- Warnings and errors

---

## Deploying to a Server (Digital Ocean)

1. Create a Ubuntu 24.04 droplet (1GB RAM / 1 vCPU is sufficient)
2. SSH in: `ssh root@<your_droplet_ip>`
3. Install dependencies:
   ```bash
   apt update && apt upgrade -y
   apt install python3-pip python3-venv -y
   ```
4. Clone the repo and follow the setup steps above
5. Run with a process manager so it stays alive after disconnect:
   ```bash
   apt install supervisor -y
   ```

---

## Adding More Questions

1. Add questions to `database/question_pool.json` following the schema above
2. Run the integrity check:
   ```bash
   python -m test.testing_questions
   ```
3. For HR diagram questions, run:
   ```bash
   python -m test.generate_hr_questions
   ```
   Then merge `test/temp.json` into the question pool manually

---

## Dependencies

| Package | Purpose |
|---|---|
| `python-telegram-bot` | Telegram bot framework |
| `pandas` | User history analysis |
| `scikit-learn` | ML-based weakness detection |
| `matplotlib` | HR diagram generation |
| `Pillow` | Image compression |
| `numpy` | Numerical computing |
| `python-dotenv` | `.env` file loading |
