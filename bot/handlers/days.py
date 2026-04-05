from __future__ import annotations

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.helpers import ensure_user, format_balance, parse_date, parse_positive_int
from bot.keyboards import (
    ADD_EXERCISE_BUTTON,
    ADD_FOOD_BUTTON,
    CANCEL_BUTTON,
    DAY_STATISTICS_BUTTON,
    FINISH_DAY_BUTTON,
    START_DAY_BUTTON,
    get_calories_keyboard,
    get_cancel_keyboard,
    get_main_keyboard,
    get_statistics_date_keyboard,
    get_statistics_keyboard,
)
from core.services.days import (
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
async def handle_start_day(message: types.Message, state: FSMContext):
    user = ensure_user(message.from_user)
    await state.clear()
    day, status = start_day(user.id)

    if status == "created":
        await message.answer(
            f"🌅 День начат: {day.date:%d.%m.%Y}\nМожно добавлять еду, движение и выполнять задачи.",
            reply_markup=get_main_keyboard(is_day_started=True),
        )
        return

    if status == "already_exists":
        await message.answer(
            f"🟡 День за {day.date:%d.%m.%Y} уже был начат.\nПовторно начать день за ту же дату нельзя.",
            reply_markup=get_main_keyboard(is_day_started=get_active_day(user.id) is not None),
        )
        return

    await message.answer(
        f"🟡 Уже есть активный день за {day.date:%d.%m.%Y}.\nСначала заверши его.",
        reply_markup=get_main_keyboard(is_day_started=True),
    )


@router.message(F.text == FINISH_DAY_BUTTON)
async def handle_finish_day(message: types.Message, state: FSMContext):
    user = ensure_user(message.from_user)
    await state.clear()
    day = finish_day(user.id)

    if day is None:
        await message.answer(
            "Сейчас нет активного дня. Сначала нажми «Начать день».",
            reply_markup=get_main_keyboard(is_day_started=False),
        )
        return

    balance_text = format_balance(day.calorie_balance)
    await message.answer(
        f"🌙 День {day.date:%d.%m.%Y} завершён.\n\n"
        f"🍽 Съедено: {day.total_consumed_calories} ккал\n"
        f"⚙️ Базовый обмен: {BASE_METABOLISM_CALORIES} ккал\n"
        f"🏃 Всего расход: {day.total_burned_calories} ккал\n"
        f"⚖️ Итог: {balance_text}",
        reply_markup=get_main_keyboard(is_day_started=False),
    )


@router.message(F.text == ADD_FOOD_BUTTON)
async def start_add_food(message: types.Message, state: FSMContext):
    user = ensure_user(message.from_user)
    if get_active_day(user.id) is None:
        await message.answer(
            "Сначала начни день, потом можно добавлять еду.",
            reply_markup=get_main_keyboard(is_day_started=False),
        )
        return

    await state.set_state(AddFoodFSM.waiting_for_name)
    await message.answer("Введи название еды:", reply_markup=get_cancel_keyboard())


@router.message(AddFoodFSM.waiting_for_name)
async def process_food_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(AddFoodFSM.waiting_for_count)
    await message.answer("Введи количество, например: `2 шт` или `250 г`.", parse_mode="Markdown", reply_markup=get_cancel_keyboard())


@router.message(AddFoodFSM.waiting_for_count)
async def process_food_count(message: types.Message, state: FSMContext):
    await state.update_data(count=message.text.strip())
    await state.set_state(AddFoodFSM.waiting_for_calories)
    await message.answer("Введи общую калорийность числом:", reply_markup=get_cancel_keyboard())


@router.message(AddFoodFSM.waiting_for_calories)
async def process_food_calories(message: types.Message, state: FSMContext):
    user = ensure_user(message.from_user)
    total_calories = parse_positive_int(message.text)
    if total_calories is None:
        await message.answer("Калории нужно ввести положительным числом, например `350`.", parse_mode="Markdown", reply_markup=get_cancel_keyboard())
        return

    data = await state.get_data()
    food_entry = add_food_entry(
        user_id=user.id,
        name=data["name"],
        count=data["count"],
        total_calories=total_calories,
    )
    await state.clear()

    if food_entry is None:
        await message.answer(
            "Активный день не найден. Сначала начни день.",
            reply_markup=get_main_keyboard(is_day_started=False),
        )
        return

    await message.answer(
        f"✅ Еда добавлена:\n{food_entry.name} ({food_entry.count}) - {food_entry.total_calories} ккал",
        reply_markup=get_calories_keyboard(),
    )


@router.message(F.text == ADD_EXERCISE_BUTTON)
async def start_add_exercise(message: types.Message, state: FSMContext):
    user = ensure_user(message.from_user)
    if get_active_day(user.id) is None:
        await message.answer(
            "Сначала начни день, потом можно добавлять движение.",
            reply_markup=get_main_keyboard(is_day_started=False),
        )
        return

    await state.set_state(AddExerciseFSM.waiting_for_name)
    await message.answer("Введи название упражнения или активности:", reply_markup=get_cancel_keyboard())


@router.message(AddExerciseFSM.waiting_for_name)
async def process_exercise_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(AddExerciseFSM.waiting_for_calories)
    await message.answer("Введи потраченные калории числом:", reply_markup=get_cancel_keyboard())


@router.message(AddExerciseFSM.waiting_for_calories)
async def process_exercise_calories(message: types.Message, state: FSMContext):
    user = ensure_user(message.from_user)
    burned_calories = parse_positive_int(message.text)
    if burned_calories is None:
        await message.answer("Калории нужно ввести положительным числом, например `200`.", parse_mode="Markdown", reply_markup=get_cancel_keyboard())
        return

    data = await state.get_data()
    exercise_entry = add_exercise_entry(
        user_id=user.id,
        name=data["name"],
        burned_calories=burned_calories,
    )
    await state.clear()

    if exercise_entry is None:
        await message.answer(
            "Активный день не найден. Сначала начни день.",
            reply_markup=get_main_keyboard(is_day_started=False),
        )
        return

    await message.answer(
        f"✅ Движение добавлено:\n{exercise_entry.name} - {exercise_entry.burned_calories} ккал",
        reply_markup=get_calories_keyboard(),
    )


@router.message(F.text == DAY_STATISTICS_BUTTON)
async def start_day_statistics(message: types.Message, state: FSMContext):
    ensure_user(message.from_user)
    await state.set_state(DayStatisticsFSM.waiting_for_date)
    await message.answer(
        "Введи дату в формате `ДД.ММ.ГГГГ` или выбери подсказку ниже.",
        parse_mode="Markdown",
        reply_markup=get_statistics_date_keyboard(),
    )


@router.message(DayStatisticsFSM.waiting_for_date)
async def process_day_statistics(message: types.Message, state: FSMContext):
    user = ensure_user(message.from_user)
    target_date = parse_date(message.text)
    if target_date is None:
        await message.answer(
            "Не получилось распознать дату. Используй формат `ДД.ММ.ГГГГ`.",
            parse_mode="Markdown",
            reply_markup=get_statistics_date_keyboard(),
        )
        return

    statistics = get_day_statistics(user.id, target_date)
    await state.clear()

    if statistics is None:
        await message.answer(
            f"За {target_date:%d.%m.%Y} данных нет.",
            reply_markup=get_statistics_keyboard(),
        )
        return

    foods_text = _format_foods(statistics["foods"])
    exercises_text = _format_exercises(statistics["exercises"])
    tasks_text = _format_completed_tasks(statistics["completed_tasks"])
    totals = statistics["totals"]
    balance_text = format_balance(totals["balance"])
    status_text = "день завершён" if statistics["day"]["is_finished"] else "день ещё активен"

    await message.answer(
        f"📊 Статистика за {target_date:%d.%m.%Y} ({status_text})\n\n"
        f"✅ Выполненные задачи:\n{tasks_text}\n\n"
        f"🍽 Еда:\n{foods_text}\n\n"
        f"🏃 Движение:\n{exercises_text}\n\n"
        f"🍽 Всего съедено: {totals['consumed']} ккал\n"
        f"🔥 Расход на движение: {totals['exercise_burned']} ккал\n"
        f"⚙️ Базовый обмен: {totals['base_metabolism']} ккал\n"
        f"🏃 Общий расход: {totals['burned']} ккал\n"
        f"⚖️ Итог: {balance_text}",
        reply_markup=get_statistics_keyboard(),
    )


@router.message(F.text == CANCEL_BUTTON)
async def cancel_action(message: types.Message, state: FSMContext):
    user = ensure_user(message.from_user)
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(
            "Сейчас нечего отменять.",
            reply_markup=get_main_keyboard(is_day_started=get_active_day(user.id) is not None),
        )
        return

    await state.clear()
    await message.answer("Действие отменено.", reply_markup=get_main_keyboard(is_day_started=get_active_day(user.id) is not None))


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


def _format_completed_tasks(tasks: list[dict]) -> str:
    if not tasks:
        return "За этот день ещё нет выполненных задач."
    return "\n".join(
        f"{index}. {task['name']}"
        for index, task in enumerate(tasks, start=1)
    )
