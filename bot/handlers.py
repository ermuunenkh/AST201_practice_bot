from telegram import Update
from telegram.ext import ContextTypes
from bot.utils import build_question_text, explanation_keyboard, send_question
from logic.question_engine import pick_question
from database.db_handler import record_answer


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
