import re
from datetime import datetime

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.task_keyboards import (
    ADD_EXERCISE_BUTTON,
    ADD_FOOD_BUTTON,
    BACK_BUTTON,
    CANCEL_BUTTON,
    DAY_STATISTICS_BUTTON,
    FINISH_DAY_BUTTON,
    START_DAY_BUTTON,
    STATISTICS_BUTTON,
    get_cancel_keyboard,
    get_main_keyboard,
    get_statistics_date_keyboard,
    get_statistics_keyboard,
)
from repository.day_repository import (
    BASE_METABOLISM_CALORIES,
    add_exercise_entry,
    add_food_entry,
    finish_day,
    get_active_day,
    get_day_statistics,
    start_day,
)

router = Router()


class AddFoodFSM(StatesGroup):
    waiting_for_name = State()
    waiting_for_count = State()
    waiting_for_calories = State()


class AddExerciseFSM(StatesGroup):
    waiting_for_name = State()
    waiting_for_calories = State()


class DayStatisticsFSM(StatesGroup):
    waiting_for_date = State()


@router.message(F.text == START_DAY_BUTTON)
@router.message(F.text == "Начать день")
async def handle_start_day(message: types.Message, state: FSMContext):
    await state.clear()
    day, created = start_day()

    if created:
        await message.answer(
            f"🌅 День начат: {day.date.strftime('%d.%m.%Y')}\n"
            "Можно добавлять еду, движение и смотреть статистику.",
            reply_markup=_main_menu_keyboard(),
        )
        return

    await message.answer(
        f"🟡 Уже есть активный день за {day.date.strftime('%d.%m.%Y')}.\n"
        "Сначала закончи его, потом можно начать новый.",
        reply_markup=_main_menu_keyboard(),
    )


@router.message(F.text == FINISH_DAY_BUTTON)
@router.message(F.text == "Закончить день")
async def handle_finish_day(message: types.Message, state: FSMContext):
    await state.clear()
    day = finish_day()

    if day is None:
        await message.answer(
            "⚠️ Сейчас нет активного дня. Сначала нажми «Начать день».",
            reply_markup=_main_menu_keyboard(),
        )
        return

    balance_text = _format_balance(day.calorie_balance)
    await message.answer(
        f"🌙 День {day.date.strftime('%d.%m.%Y')} завершён.\n\n"
        f"🍽️ Съедено: {day.total_consumed_calories} ккал\n"
        f"⚙️ Базовый обмен: {BASE_METABOLISM_CALORIES} ккал\n"
        f"🏃 Всего расход: {day.total_burned_calories} ккал\n"
        f"⚖️ Итог: {balance_text}",
        reply_markup=_main_menu_keyboard(),
    )


@router.message(F.text == ADD_FOOD_BUTTON)
@router.message(F.text == "Добавить еду")
async def start_add_food(message: types.Message, state: FSMContext):
    if get_active_day() is None:
        await message.answer(
            "⚠️ Сначала начни день, потом можно добавлять еду.",
            reply_markup=_main_menu_keyboard(),
        )
        return

    await state.set_state(AddFoodFSM.waiting_for_name)
    await message.answer(
        "🍽️ Введи название еды:",
        reply_markup=get_cancel_keyboard(),
    )


@router.message(AddFoodFSM.waiting_for_name)
async def process_food_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(AddFoodFSM.waiting_for_count)
    await message.answer(
        "📦 Введи количество, например: `2 шт` или `250 г`.",
        reply_markup=get_cancel_keyboard(),
    )


@router.message(AddFoodFSM.waiting_for_count)
async def process_food_count(message: types.Message, state: FSMContext):
    await state.update_data(count=message.text.strip())
    await state.set_state(AddFoodFSM.waiting_for_calories)
    await message.answer(
        "🔥 Введи общую калорийность этой позиции числом:",
        reply_markup=get_cancel_keyboard(),
    )


@router.message(AddFoodFSM.waiting_for_calories)
async def process_food_calories(message: types.Message, state: FSMContext):
    total_calories = _parse_positive_int(message.text)
    if total_calories is None:
        await message.answer(
            "⚠️ Калории нужно ввести положительным числом, например: `350`.",
            reply_markup=get_cancel_keyboard(),
        )
        return

    data = await state.get_data()
    food_entry = add_food_entry(
        name=data["name"],
        count=data["count"],
        total_calories=total_calories,
    )

    if food_entry is None:
        await state.clear()
        await message.answer(
            "⚠️ Активный день не найден. Сначала нажми «Начать день».",
            reply_markup=_main_menu_keyboard(),
        )
        return

    await state.clear()
    await message.answer(
        f"✅ Еда добавлена:\n"
        f"{food_entry.name} ({food_entry.count}) - {food_entry.total_calories} ккал",
        reply_markup=_main_menu_keyboard(),
    )


@router.message(F.text == ADD_EXERCISE_BUTTON)
@router.message(F.text == "Добавить движение")
async def start_add_exercise(message: types.Message, state: FSMContext):
    if get_active_day() is None:
        await message.answer(
            "⚠️ Сначала начни день, потом можно добавлять движение.",
            reply_markup=_main_menu_keyboard(),
        )
        return

    await state.set_state(AddExerciseFSM.waiting_for_name)
    await message.answer(
        "🏃 Введи, какое движение или упражнение ты сделал:",
        reply_markup=get_cancel_keyboard(),
    )


@router.message(AddExerciseFSM.waiting_for_name)
async def process_exercise_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(AddExerciseFSM.waiting_for_calories)
    await message.answer(
        "🔥 Введи, сколько калорий потрачено числом:",
        reply_markup=get_cancel_keyboard(),
    )


@router.message(AddExerciseFSM.waiting_for_calories)
async def process_exercise_calories(message: types.Message, state: FSMContext):
    burned_calories = _parse_positive_int(message.text)
    if burned_calories is None:
        await message.answer(
            "⚠️ Калории нужно ввести положительным числом, например: `200`.",
            reply_markup=get_cancel_keyboard(),
        )
        return

    data = await state.get_data()
    exercise_entry = add_exercise_entry(
        name=data["name"],
        burned_calories=burned_calories,
    )

    if exercise_entry is None:
        await state.clear()
        await message.answer(
            "⚠️ Активный день не найден. Сначала нажми «Начать день».",
            reply_markup=_main_menu_keyboard(),
        )
        return

    await state.clear()
    await message.answer(
        f"✅ Движение добавлено:\n"
        f"{exercise_entry.name} - {exercise_entry.burned_calories} ккал",
        reply_markup=_main_menu_keyboard(),
    )


@router.message(F.text == STATISTICS_BUTTON)
@router.message(F.text == "Статистика")
async def open_statistics_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "📊 Выбери нужный раздел статистики:",
        reply_markup=get_statistics_keyboard(),
    )


@router.message(F.text == DAY_STATISTICS_BUTTON)
@router.message(F.text == "Статистика за день")
async def start_day_statistics(message: types.Message, state: FSMContext):
    await state.set_state(DayStatisticsFSM.waiting_for_date)
    await message.answer(
        "📅 Введи дату в формате `ДД.ММ.ГГГГ`.\n"
        "Можно нажать одну из кнопок-подсказок ниже.",
        reply_markup=get_statistics_date_keyboard(),
    )


@router.message(F.text == BACK_BUTTON)
@router.message(F.text == "Назад")
async def go_back_to_main_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "⬅️ Главное меню.",
        reply_markup=_main_menu_keyboard(),
    )


@router.message(DayStatisticsFSM.waiting_for_date)
async def process_day_statistics(message: types.Message, state: FSMContext):
    target_date = _parse_date(message.text)
    if target_date is None:
        await message.answer(
            "⚠️ Не получилось распознать дату. Используй формат `ДД.ММ.ГГГГ` или кнопки-подсказки.",
            reply_markup=get_statistics_date_keyboard(),
        )
        return

    statistics = get_day_statistics(target_date)
    await state.clear()

    if statistics is None:
        await message.answer(
            f"📭 За {target_date.strftime('%d.%m.%Y')} данных нет.",
            reply_markup=_main_menu_keyboard(),
        )
        return

    foods_text = _format_foods(statistics["foods"])
    exercises_text = _format_exercises(statistics["exercises"])
    totals = statistics["totals"]
    balance_text = _format_balance(totals["balance"])
    status_text = "день завершён" if statistics["day"]["is_finished"] else "день ещё активен"

    await message.answer(
        f"📊 Статистика за {target_date.strftime('%d.%m.%Y')} ({status_text})\n\n"
        f"🍽️ Еда:\n{foods_text}\n\n"
        f"🏃 Движение:\n{exercises_text}\n\n"
        f"🍽️ Всего съедено: {totals['consumed']} ккал\n"
        f"🔥 Расход на движение: {totals['exercise_burned']} ккал\n"
        f"⚙️ Базовый обмен: {totals['base_metabolism']} ккал\n"
        f"🏃 Общий расход: {totals['burned']} ккал\n"
        f"⚖️ Итог: {balance_text}",
        reply_markup=_main_menu_keyboard(),
    )


def _parse_positive_int(value: str | None) -> int | None:
    if value is None:
        return None

    try:
        parsed_value = int(value.strip())
    except ValueError:
        return None

    return parsed_value if parsed_value > 0 else None


def _parse_date(value: str | None):
    if value is None:
        return None

    cleaned_value = value.strip()
    match = re.search(r"\d{2}\.\d{2}\.\d{4}", cleaned_value)
    if match:
        cleaned_value = match.group(0)

    for date_format in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(cleaned_value, date_format).date()
        except ValueError:
            continue

    return None


def _format_foods(foods: list[dict]) -> str:
    if not foods:
        return "Пока ничего не добавлено."

    return "\n".join(
        f"{index}. {food['name']} ({food['count']}) - {food['total_calories']} ккал"
        for index, food in enumerate(foods, start=1)
    )


def _format_exercises(exercises: list[dict]) -> str:
    if not exercises:
        return "Пока ничего не добавлено."

    return "\n".join(
        f"{index}. {exercise['name']} - {exercise['burned_calories']} ккал"
        for index, exercise in enumerate(exercises, start=1)
    )


def _format_balance(balance: int) -> str:
    if balance > 0:
        return f"дефицит {balance} ккал"
    if balance < 0:
        return f"профицит {abs(balance)} ккал"
    return "баланс 0 ккал"


def _main_menu_keyboard():
    return get_main_keyboard(is_day_started=get_active_day() is not None)
