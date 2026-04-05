from __future__ import annotations

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.helpers import ensure_user
from bot.keyboards import (
    ADD_TASK_BUTTON,
    VIEW_ALL_TASKS_BUTTON,
    VIEW_PENDING_TASKS_BUTTON,
    get_cancel_keyboard,
    get_complete_task_keyboard,
    get_main_keyboard,
    get_task_manage_keyboard,
    get_tasks_keyboard,
)
from core.services.days import get_active_day
from core.services.tasks import (
    complete_task_for_active_day,
    create_task,
    deactivate_task,
    get_task_day_overview,
    list_tasks,
)


router = Router()


class AddTaskFSM(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_period = State()


@router.message(F.text == ADD_TASK_BUTTON)
async def start_add_task(message: types.Message, state: FSMContext):
    ensure_user(message.from_user)
    await state.set_state(AddTaskFSM.waiting_for_name)
    await message.answer("Введи название задачи:", reply_markup=get_cancel_keyboard())


@router.message(AddTaskFSM.waiting_for_name)
async def process_task_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(AddTaskFSM.waiting_for_description)
    await message.answer(
        "Введи описание задачи или `-`, если без описания.",
        parse_mode="Markdown",
        reply_markup=get_cancel_keyboard(),
    )


@router.message(AddTaskFSM.waiting_for_description)
async def process_task_description(message: types.Message, state: FSMContext):
    description = message.text.strip()
    await state.update_data(description=None if description == "-" else description)
    await state.set_state(AddTaskFSM.waiting_for_period)
    await message.answer(
        "Введи периодичность, например: ежедневно, будни, 3 раза в неделю.",
        reply_markup=get_cancel_keyboard(),
    )


@router.message(AddTaskFSM.waiting_for_period)
async def process_task_period(message: types.Message, state: FSMContext):
    user = ensure_user(message.from_user)
    await state.update_data(period=message.text.strip())
    data = await state.get_data()

    task = create_task(
        user_id=user.id,
        name=data["name"],
        description=data["description"],
        period=data["period"],
    )
    await state.clear()
    await message.answer(
        f"✅ Задача добавлена.\n\n"
        f"Название: {task.name}\n"
        f"Описание: {task.description or 'без описания'}\n"
        f"Периодичность: {task.period}",
        reply_markup=get_tasks_keyboard(),
    )


@router.message(F.text == VIEW_PENDING_TASKS_BUTTON)
async def show_pending_tasks(message: types.Message, state: FSMContext):
    user = ensure_user(message.from_user)
    await state.clear()
    overview = get_task_day_overview(user.id)
    active_day = overview["active_day"]

    if active_day is None:
        await message.answer(
            "Сначала начни день, чтобы отмечать выполненные задачи.",
            reply_markup=get_main_keyboard(is_day_started=False),
        )
        return

    pending_tasks = overview["pending_tasks"]
    if not pending_tasks:
        await message.answer(
            "На сегодня невыполненных задач не осталось.",
            reply_markup=get_tasks_keyboard(),
        )
        return

    await message.answer(
        f"Невыполненные задачи за {active_day.date:%d.%m.%Y}:",
        reply_markup=get_tasks_keyboard(),
    )
    for index, task in enumerate(pending_tasks, start=1):
        description = task.description or "без описания"
        await message.answer(
            f"{index}. {task.name}\n"
            f"Описание: {description}\n"
            f"Периодичность: {task.period}",
            reply_markup=get_complete_task_keyboard(task.id),
        )


@router.message(F.text == VIEW_ALL_TASKS_BUTTON)
async def show_all_tasks(message: types.Message, state: FSMContext):
    user = ensure_user(message.from_user)
    await state.clear()
    tasks = list_tasks(user.id, active_only=False)
    if not tasks:
        await message.answer("Пока нет задач.", reply_markup=get_tasks_keyboard())
        return

    await message.answer("Все задачи:", reply_markup=get_tasks_keyboard())
    for task in tasks:
        status = "активна" if task.is_active else "отключена"
        description = task.description or "без описания"
        reply_markup = get_task_manage_keyboard(task.id) if task.is_active else None
        await message.answer(
            f"{task.name}\n"
            f"Описание: {description}\n"
            f"Периодичность: {task.period}\n"
            f"Статус: {status}",
            reply_markup=reply_markup,
        )


@router.callback_query(F.data.startswith("complete_task:"))
async def complete_task_callback(callback_query: types.CallbackQuery):
    user = ensure_user(callback_query.from_user)
    task_id = int(callback_query.data.split(":", 1)[1])
    status, task = complete_task_for_active_day(user.id, task_id)

    if status == "completed" and task is not None:
        await callback_query.answer("Задача отмечена")
        await callback_query.message.edit_reply_markup(reply_markup=None)
        await callback_query.message.answer(
            f"✅ Выполнено: {task.name}",
            reply_markup=get_tasks_keyboard(),
        )
        return

    messages = {
        "no_active_day": "Сначала начни день.",
        "not_found": "Задача не найдена или уже отключена.",
        "already_completed": "Эта задача уже отмечена сегодня.",
    }
    await callback_query.answer(messages.get(status, "Не удалось отметить задачу"), show_alert=True)


@router.callback_query(F.data.startswith("deactivate_task:"))
async def deactivate_task_callback(callback_query: types.CallbackQuery):
    user = ensure_user(callback_query.from_user)
    task_id = int(callback_query.data.split(":", 1)[1])
    is_deactivated = deactivate_task(user.id, task_id)
    if not is_deactivated:
        await callback_query.answer("Задача не найдена", show_alert=True)
        return

    await callback_query.answer("Задача отключена")
    await callback_query.message.edit_reply_markup(reply_markup=None)
    reply_markup = get_tasks_keyboard() if get_active_day(user.id) is not None else get_main_keyboard(is_day_started=False)
    await callback_query.message.answer("Задача переведена в неактивные.", reply_markup=reply_markup)
