from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_reply_keyboard(buttons: list[list[str]], resize: bool = True) -> ReplyKeyboardMarkup:
    """
    buttons = [["Option 1", "Option 2"], ["Cancel"]]
    """
    keyboard = []
    for row in buttons:
        keyboard.append([KeyboardButton(text=b) for b in row])
    
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=resize)