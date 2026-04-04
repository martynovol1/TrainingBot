from datetime import date, timedelta

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

START_DAY_BUTTON = "🌅 Начать день"
FINISH_DAY_BUTTON = "🌙 Закончить день"
ADD_FOOD_BUTTON = "🍽️ Добавить еду"
ADD_EXERCISE_BUTTON = "🏃 Добавить движение"
STATISTICS_BUTTON = "📊 Статистика"
DAY_STATISTICS_BUTTON = "📅 Статистика за день"
BACK_BUTTON = "⬅️ Назад"
CANCEL_BUTTON = "❌ Отмена"


def get_main_keyboard(is_day_started: bool = False):
    keyboard = (
        [
            [KeyboardButton(text=START_DAY_BUTTON)],
        ]
        if not is_day_started
        else [
            [
                KeyboardButton(text=ADD_FOOD_BUTTON),
                KeyboardButton(text=ADD_EXERCISE_BUTTON),
            ],
            [
                KeyboardButton(text=STATISTICS_BUTTON),
                KeyboardButton(text=FINISH_DAY_BUTTON),
            ],
        ]
    )

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
    )


def get_cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=CANCEL_BUTTON)]
        ],
        resize_keyboard=True,
    )


def get_statistics_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=DAY_STATISTICS_BUTTON)],
            [KeyboardButton(text=BACK_BUTTON)],
        ],
        resize_keyboard=True,
    )


def get_statistics_date_keyboard():
    today = date.today()
    yesterday = today - timedelta(days=1)

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"📅 Сегодня: {today.strftime('%d.%m.%Y')}")],
            [KeyboardButton(text=f"🗓️ Вчера: {yesterday.strftime('%d.%m.%Y')}")],
            [KeyboardButton(text=CANCEL_BUTTON)],
        ],
        resize_keyboard=True,
    )
