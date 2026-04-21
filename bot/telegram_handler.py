import asyncio
from datetime import datetime, timezone

from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

import config
from bot import keyboards, sender
from logs.logger import BotLogger

# ── helpers ───────────────────────────────────────────────────────────────────

def _chat_id(update: Update) -> int:
    return update.effective_chat.id


# ── command handlers ──────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = _chat_id(update)
    username = update.effective_user.username or update.effective_user.first_name

    # STUB: persist user in DB
    # TODO: replace with real call after db/ session
    # db.queries.register_user(chat_id, username)

    BotLogger.info(f"User registered: {username} ({chat_id})")
    await update.message.reply_text(
        "Welcome! You're registered. I'll send you astronomy questions to help you ace the exam."
    )


async def cmd_ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = _chat_id(update)
    try:
        n = int(context.args[0]) if context.args else 1
    except (ValueError, IndexError):
        n = 1

    for _ in range(n):
        # STUB: pick a question
        # TODO: replace with real call after logic/ session
        # question = logic.question_picker.pick_question(chat_id)
        question = _stub_question()  # STUB
        await sender.send_question(context.bot, chat_id, question)


async def cmd_batch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "How many questions would you like?",
        reply_markup=keyboards.make_batch_size_keyboard(),
    )


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = _chat_id(update)

    # STUB: fetch topic scores
    # TODO: replace with real call after db/ session
    # scores = db.queries.get_topic_scores(chat_id)
    scores = []  # STUB

    if not scores:
        await update.message.reply_text("No stats yet — answer some questions first!")
        return

    header = f"{'Topic':<22} | {'Correct':>7} | {'Total':>5} | Accuracy\n"
    separator = "-" * 55 + "\n"
    rows = ""
    for row in scores:
        acc = int(row["correct"] / row["total"] * 100) if row["total"] else 0
        flag = "  ← weak" if acc < 50 else ""
        rows += f"{row['topic']:<22} | {row['correct']:>7} | {row['total']:>5} | {acc}%{flag}\n"

    await update.message.reply_text(f"```\n{header}{separator}{rows}```", parse_mode="Markdown")


async def cmd_topics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # STUB: fetch distinct topics from DB
    # TODO: replace with real call after db/ session
    # topics = db.queries.get_all_topics()
    topics = ["Stellar Evolution", "Cosmology", "Solar System", "Galaxies", "Instrumentation"]  # STUB

    await update.message.reply_text(
        "Choose a topic:",
        reply_markup=keyboards.make_topic_keyboard(topics),
    )


# ── callback handler ──────────────────────────────────────────────────────────

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data: str = query.data
    chat_id = query.message.chat_id

    # answer callback  →  "{question_id}|{choice}"
    if "|" in data and not data.startswith("explain|") and not data.startswith("topic|") and not data.startswith("batch|"):
        question_id, chosen = data.split("|", 1)

        # STUB: record answer and fetch correctness
        # TODO: replace with real calls after db/ session
        # sent_at = db.queries.get_sent_at(chat_id, question_id)
        # response_time = (datetime.now(timezone.utc) - sent_at).total_seconds()
        # is_correct = db.queries.record_answer(chat_id, question_id, chosen, response_time)
        # db.queries.update_topic_score(chat_id, topic, is_correct)
        is_correct = False  # STUB

        result_icon = "✅" if is_correct else "❌"
        new_text = f"{query.message.text}\n\n{result_icon} You answered: *{chosen}*"
        await query.edit_message_text(
            text=new_text,
            parse_mode="Markdown",
            reply_markup=keyboards.make_post_answer_keyboard(question_id),
        )
        BotLogger.info(f"Answer from {chat_id}: q={question_id} choice={chosen} correct={is_correct}")
        return

    # explain callback  →  "explain|{question_id}"
    if data.startswith("explain|"):
        question_id = data.split("|", 1)[1]

        # STUB: fetch question from DB
        # TODO: replace with real call after db/ session
        # question = db.queries.get_question(question_id)
        question = _stub_question()  # STUB

        await sender.send_explanation(context.bot, chat_id, question)
        return

    # next callback  →  "next"
    if data == "next":
        # STUB: pick next question
        # TODO: replace with real call after logic/ session
        # question = logic.question_picker.pick_question(chat_id)
        question = _stub_question()  # STUB
        await sender.send_question(context.bot, chat_id, question)
        return

    # batch callback  →  "batch|{n}"
    if data.startswith("batch|"):
        n = int(data.split("|", 1)[1])
        await query.edit_message_text(f"Sending {n} questions, one every {config.BATCH_SEND_INTERVAL_SEC}s...")
        for i in range(n):
            # STUB: pick question
            # TODO: replace with real call after logic/ session
            # question = logic.question_picker.pick_question(chat_id)
            question = _stub_question()  # STUB
            await sender.send_question(context.bot, chat_id, question)
            if i < n - 1:
                await asyncio.sleep(config.BATCH_SEND_INTERVAL_SEC)
        return

    # topic callback  →  "topic|{topic_name}"
    if data.startswith("topic|"):
        topic = data.split("|", 1)[1]
        # STUB: pick question by topic
        # TODO: replace with real call after logic/ session
        # question = logic.question_picker.pick_question(chat_id, topic=None if topic == "__random__" else topic)
        question = _stub_question()  # STUB
        await sender.send_question(context.bot, chat_id, question)
        return


# ── error handler ─────────────────────────────────────────────────────────────

async def handle_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    BotLogger.error(f"Exception while handling update: {context.error}", exc_info=context.error)
    if isinstance(update, Update) and update.effective_chat:
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Something went wrong, please try again.",
            )
        except Exception:
            pass


# ── stub helper (removed after db/ session) ───────────────────────────────────

def _stub_question() -> dict:  # STUB
    return {
        "id": "AST_000",
        "topic": "Stellar Evolution",
        "subtopic": "HR Diagram",
        "type": "MCQ",
        "difficulty": 1,
        "text": "(stub) Where do main sequence stars spend most of their life?",
        "choices": ["A. Core", "B. Shell", "C. Surface", "D. Corona"],
        "answer": "A",
        "explanation": "Main sequence stars fuse hydrogen in their cores.",
        "image": None,
    }


# ── application factory ───────────────────────────────────────────────────────

def build_application() -> Application:
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("ask", cmd_ask))
    app.add_handler(CommandHandler("batch", cmd_batch))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("topics", cmd_topics))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_error_handler(handle_error)

    BotLogger.info("All handlers registered.")
    return app


if __name__ == "__main__":
    build_application()
    print("Bot handlers registered OK")
