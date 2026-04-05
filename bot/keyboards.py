from __future__ import annotations

from datetime import date, timedelta

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


START_DAY_BUTTON = "🌅 Начать день"
FINISH_DAY_BUTTON = "🌙 Завершить день"
TASKS_MENU_BUTTON = "📋 Задачи"
CALORIES_MENU_BUTTON = "🍽 Учёт калорий"
STATISTICS_MENU_BUTTON = "📊 Статистика"
WEB_ACCESS_BUTTON = "🔐 Веб-доступ"

ADD_TASK_BUTTON = "➕ Добавить задачу"
VIEW_PENDING_TASKS_BUTTON = "🕒 Невыполненные за день"
VIEW_ALL_TASKS_BUTTON = "🗂 Все задачи"

ADD_FOOD_BUTTON = "🍽 Добавить еду"
ADD_EXERCISE_BUTTON = "🏃 Добавить движение"

DAY_STATISTICS_BUTTON = "📅 Статистика за день"
GET_WEB_CODE_BUTTON = "🔑 Получить код"

BACK_BUTTON = "⬅️ Назад"
CANCEL_BUTTON = "❌ Отмена"


def get_main_keyboard(is_day_started: bool) -> ReplyKeyboardMarkup:
    day_action = FINISH_DAY_BUTTON if is_day_started else START_DAY_BUTTON
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=TASKS_MENU_BUTTON), KeyboardButton(text=CALORIES_MENU_BUTTON)],
            [KeyboardButton(text=STATISTICS_MENU_BUTTON), KeyboardButton(text=WEB_ACCESS_BUTTON)],
            [KeyboardButton(text=day_action)],
        ],
        resize_keyboard=True,
    )


def get_tasks_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=ADD_TASK_BUTTON)],
            [KeyboardButton(text=VIEW_PENDING_TASKS_BUTTON)],
            [KeyboardButton(text=VIEW_ALL_TASKS_BUTTON)],
            [KeyboardButton(text=BACK_BUTTON)],
        ],
        resize_keyboard=True,
    )


def get_calories_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=ADD_FOOD_BUTTON)],
            [KeyboardButton(text=ADD_EXERCISE_BUTTON)],
            [KeyboardButton(text=BACK_BUTTON)],
        ],
        resize_keyboard=True,
    )


def get_statistics_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=DAY_STATISTICS_BUTTON)],
            [KeyboardButton(text=BACK_BUTTON)],
        ],
        resize_keyboard=True,
    )


def get_web_access_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=GET_WEB_CODE_BUTTON)],
            [KeyboardButton(text=BACK_BUTTON)],
        ],
        resize_keyboard=True,
    )


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=CANCEL_BUTTON)]],
        resize_keyboard=True,
    )


def get_statistics_date_keyboard() -> ReplyKeyboardMarkup:
    today = date.today()
    yesterday = today - timedelta(days=1)
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"Сегодня: {today:%d.%m.%Y}")],
            [KeyboardButton(text=f"Вчера: {yesterday:%d.%m.%Y}")],
            [KeyboardButton(text=CANCEL_BUTTON)],
        ],
        resize_keyboard=True,
    )


def get_complete_task_keyboard(task_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Выполнить", callback_data=f"complete_task:{task_id}")]
        ]
    )


def get_task_manage_keyboard(task_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛌 Отключить", callback_data=f"deactivate_task:{task_id}")]
        ]
    )
