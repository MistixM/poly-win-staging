from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_inline_keyboard(buttons: list[list[tuple[str, str]]]) -> InlineKeyboardMarkup:
    keyboard = []

    for row in buttons:
        keyboard.append([
            InlineKeyboardButton(text=text, callback_data=cb)
            for text, cb in row
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)