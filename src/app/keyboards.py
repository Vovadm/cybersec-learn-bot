from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from app.lessons import lessons


def start_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Изучать теорию")],
            [KeyboardButton(text="Смотреть достижения")]
        ],
        resize_keyboard=True
    )


def lessons_keyboard() -> ReplyKeyboardMarkup:
    buttons = []

    for i in range(0, len(lessons), 2):
        row = []

        row.append(KeyboardButton(text=lessons[i].name))

        if i + 1 < len(lessons):
            row.append(KeyboardButton(text=lessons[i + 1].name))

        buttons.append(row)

    buttons.append([KeyboardButton(text="⬅ Вернуться в главное меню")])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
