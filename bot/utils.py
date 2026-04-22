from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message
from src.image_handler import decompress_image


def escape(text: str) -> str:
    for ch in r"\_*[]()~`>#+-=|{}.!":
        text = text.replace(ch, f"\\{ch}")
    return text


def build_question_text(q: dict, chosen: str | None = None) -> str:
    body = f"🔭 *Question:*\n\n{escape(q['question'])}\n\n"
    for letter, text in q["options"].items():
        if chosen is None:
            body += f"{letter}\\. {escape(text)}\n"
        elif letter == q["answer"]:
            body += f"*{letter}\\. {escape(text)}* ✅\n"
        elif letter == chosen:
            body += f"*{letter}\\. {escape(text)}* ❌\n"
        else:
            body += f"{letter}\\. {escape(text)}\n"
    if chosen is not None:
        body += f"\n💡 *Explanation*\n\n{escape(q['explanation'])}"
    return body


def question_keyboard(letters: list[str]) -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(l, callback_data=f"ans_{l}") for l in letters]
    return InlineKeyboardMarkup([buttons])



def build_tf_question_text(q: dict, chosen: str | None = None) -> str:
    body = f"🔭 *Question:*\n\n{escape(q['question'])}\n\n"
    for option in ["True", "False"]:
        if chosen is None:
            body += f"\\- {option}\n"
        elif option == q["answer"]:
            body += f"*\\- {option}* ✅\n"
        elif option == chosen:
            body += f"*\\- {option}* ❌\n"
        else:
            body += f"\\- {option}\n"
    return body


def tf_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("True", callback_data="ans_True"),
        InlineKeyboardButton("False", callback_data="ans_False"),
    ]])


async def send_question(message: Message, q: dict) -> None:
    text = build_question_text(q)
    keyboard = question_keyboard(list(q["options"].keys())) if q["type"] == "MC" else tf_keyboard()
    image_path = q.get("image")

    if image_path:
        temp_path = decompress_image(image_path)
        try:
            with open(temp_path, "rb") as img:
                await message.reply_photo(photo=img)
        finally:
            temp_path.unlink(missing_ok=True)

    await message.reply_text(
        text,
        parse_mode="MarkdownV2",
        reply_markup=keyboard,
    )


def build_explanation_text(q: dict) -> str:
    return f"💡 *Explanation*\n\n{escape(q['explanation'])}"


def explanation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("Next Question", callback_data="next"),
    ]])
