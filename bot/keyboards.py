from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def make_answer_keyboard(question_id: str, choices: list[str]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(choice, callback_data=f"{question_id}|{choice}")]
        for choice in choices
    ]
    return InlineKeyboardMarkup(buttons)


def make_post_answer_keyboard(question_id: str) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton("See explanation", callback_data=f"explain|{question_id}"),
            InlineKeyboardButton("Next question", callback_data="next"),
        ]
    ]
    return InlineKeyboardMarkup(buttons)


def make_batch_size_keyboard() -> InlineKeyboardMarkup:
    sizes = [5, 10, 15, 20]
    buttons = [
        [InlineKeyboardButton(str(n), callback_data=f"batch|{n}") for n in sizes]
    ]
    return InlineKeyboardMarkup(buttons)


def make_topic_keyboard(topics: list[str]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(topic, callback_data=f"topic|{topic}")]
        for topic in topics
    ]
    buttons.append([InlineKeyboardButton("Surprise me", callback_data="topic|__random__")])
    return InlineKeyboardMarkup(buttons)
