import os
from telegram import Bot, InputFile

import config
from bot.keyboards import make_answer_keyboard
from logs.logger import BotLogger


async def send_question(bot: Bot, chat_id: int, question: dict) -> int:
    q_id = question["id"]
    choices = question.get("choices", [])
    keyboard = make_answer_keyboard(q_id, choices)
    text = f"*{question['text']}*"

    if question.get("image"):
        image_path = os.path.join(config.QUESTION_IMAGE_DIR, question["image"])
        msg = await send_photo(bot, chat_id, image_path, caption=text, reply_markup=keyboard)
    else:
        msg = await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )

    BotLogger.info(f"Sent question {q_id} to {chat_id}")

    # STUB: record send event in DB
    # TODO: replace with real call after db/ session
    # db.queries.record_send_event(chat_id, q_id, msg.message_id)

    return msg.message_id


async def send_text(bot: Bot, chat_id: int, text: str) -> None:
    await bot.send_message(chat_id=chat_id, text=text)


async def send_photo(
    bot: Bot,
    chat_id: int,
    image_path: str,
    caption: str = "",
    reply_markup=None,
):
    # STUB: compress before sending
    # TODO: replace with real call after utils/ session
    # compressed = utils.image_compress.compress_image(image_path)
    compressed = image_path

    with open(compressed, "rb") as f:
        return await bot.send_photo(
            chat_id=chat_id,
            photo=InputFile(f),
            caption=caption,
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )


async def send_explanation(bot: Bot, chat_id: int, question: dict) -> None:
    explanation = question.get("explanation", "No explanation available.")
    text = f"*Explanation:*\n{explanation}"

    if question.get("image"):
        image_path = os.path.join(config.QUESTION_IMAGE_DIR, question["image"])
        await send_photo(bot, chat_id, image_path, caption=text)
    else:
        await send_text(bot, chat_id, text)


async def broadcast(bot: Bot, question: dict) -> None:
    for name, chat_id in config.USERS.items():
        try:
            await send_question(bot, chat_id, question)
        except Exception as exc:
            BotLogger.error(f"broadcast failed for {name} ({chat_id}): {exc}")
