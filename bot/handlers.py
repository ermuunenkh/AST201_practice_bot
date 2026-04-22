from telegram import Update
from telegram.ext import ContextTypes
from bot.utils import build_question_text, explanation_keyboard, stats_keyboard, send_question, push_send_question
from logic.question_engine import pick_question, get_user_schedule, calculate_delays
from logic.stats import build_stats_text
from database.db_handler import record_answer
from config import CHAT_IDS


async def daily_schedule_refresh(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Runs at the start of each user's daily window. Computes delays for the day
    and schedules the first question. Each fired question schedules the next."""
    chat_id  = context.job.data["chat_id"]
    config   = get_user_schedule(chat_id)
    window_s = (config["window_end_hour"] - config["window_start_hour"]) * 3600
    delays   = calculate_delays(chat_id, config["n"], window_s)

    context.bot_data[chat_id] = {"delays": delays, "index": 0}
    context.job_queue.run_once(push_question, when=delays[0],
                               data={"chat_id": chat_id})

    # Reschedule this refresh for the same window start tomorrow
    context.job_queue.run_once(daily_schedule_refresh, when=24 * 3600,
                               data={"chat_id": chat_id})


async def push_question(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends one question, then schedules the next using the precomputed delay list."""
    chat_id   = context.job.data["chat_id"]
    state     = context.bot_data.get(chat_id, {})
    delays    = state.get("delays", [])
    index     = state.get("index", 0)

    question  = pick_question()
    await push_send_question(context, chat_id, question)

    next_index = index + 1
    if next_index < len(delays):
        context.bot_data[chat_id]["index"] = next_index
        context.job_queue.run_once(push_question, when=delays[next_index],
                                   data={"chat_id": chat_id})


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = build_stats_text(update.effective_user.id)
    await update.message.reply_text(
        text,
        parse_mode="MarkdownV2",
        reply_markup=stats_keyboard(),
    )


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = pick_question()
    context.user_data["question"] = question
    await send_question(update.message, question)


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    question = context.user_data.get("question", {})

    if data.startswith("ans_"):
        chosen = data[4:]
        is_correct = chosen == question.get("answer")

        record_answer(query.from_user.id, question["id"], question["topic"], question["sub_topic"], chosen, is_correct)

        await query.edit_message_text(
            build_question_text(question, chosen=chosen),
            parse_mode="MarkdownV2",
            reply_markup=explanation_keyboard(),
        )

    elif data == "next":
        await query.edit_message_reply_markup(reply_markup=None)
        question = pick_question()
        context.user_data["question"] = question
        await send_question(query.message, question)
