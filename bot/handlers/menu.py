from __future__ import annotations

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.helpers import ensure_user
from bot.keyboards import (
    BACK_BUTTON,
    CALORIES_MENU_BUTTON,
    STATISTICS_MENU_BUTTON,
    TASKS_MENU_BUTTON,
    WEB_ACCESS_BUTTON,
    get_calories_keyboard,
    get_main_keyboard,
    get_statistics_keyboard,
    get_tasks_keyboard,
    get_web_access_keyboard,
)
from core.services.days import get_active_day


router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user = ensure_user(message.from_user)
    await state.clear()
    await message.answer(
        "Привет!\nЯ помогу вести задачи, калории и статистику. "
        "Для входа на сайт можно получить одноразовый код в разделе «Веб-доступ».",
        reply_markup=get_main_keyboard(is_day_started=get_active_day(user.id) is not None),
    )


@router.message(F.text == TASKS_MENU_BUTTON)
async def open_tasks_menu(message: types.Message, state: FSMContext):
    ensure_user(message.from_user)
    await state.clear()
    await message.answer("Раздел задач.", reply_markup=get_tasks_keyboard())


@router.message(F.text == CALORIES_MENU_BUTTON)
async def open_calories_menu(message: types.Message, state: FSMContext):
    ensure_user(message.from_user)
    await state.clear()
    await message.answer("Раздел учёта калорий.", reply_markup=get_calories_keyboard())


@router.message(F.text == STATISTICS_MENU_BUTTON)
async def open_statistics_menu(message: types.Message, state: FSMContext):
    ensure_user(message.from_user)
    await state.clear()
    await message.answer("Раздел статистики.", reply_markup=get_statistics_keyboard())


@router.message(F.text == WEB_ACCESS_BUTTON)
async def open_web_access_menu(message: types.Message, state: FSMContext):
    ensure_user(message.from_user)
    await state.clear()
    await message.answer(
        "Здесь можно получить одноразовый код для входа на сайт.",
        reply_markup=get_web_access_keyboard(),
    )


@router.message(F.text == BACK_BUTTON)
async def back_to_main_menu(message: types.Message, state: FSMContext):
    user = ensure_user(message.from_user)
    await state.clear()
    await message.answer(
        "Главное меню.",
        reply_markup=get_main_keyboard(is_day_started=get_active_day(user.id) is not None),
    )
