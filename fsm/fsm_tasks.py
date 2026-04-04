from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.task_keyboards import CANCEL_BUTTON, get_cancel_keyboard, get_main_keyboard
from repository.day_repository import get_active_day
from repository.task_repository import add_task

router = Router()


class AddTaskFSM(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_period = State()


@router.message(F.text == "Добавить задачу")
async def start_add_task(message: types.Message, state: FSMContext):
    await state.set_state(AddTaskFSM.waiting_for_name)
    await message.answer(
        "Введите название задачи:",
        reply_markup=get_cancel_keyboard()
    )


@router.message(F.text == CANCEL_BUTTON)
@router.message(F.text == "Отмена")
async def cancel_action(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state is None:
        await message.answer(
            "Сейчас нечего отменять.",
            reply_markup=_main_menu_keyboard()
        )
        return

    await state.clear()
    await message.answer(
        "❌ Действие отменено.",
        reply_markup=_main_menu_keyboard()
    )


@router.message(AddTaskFSM.waiting_for_name)
async def process_task_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddTaskFSM.waiting_for_description)
    await message.answer(
        "Введите описание задачи:",
        reply_markup=get_cancel_keyboard()
    )


@router.message(AddTaskFSM.waiting_for_description)
async def process_task_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddTaskFSM.waiting_for_period)
    await message.answer(
        "Введите периодичность задачи:",
        reply_markup=get_cancel_keyboard()
    )


@router.message(AddTaskFSM.waiting_for_period)
async def process_task_period(message: types.Message, state: FSMContext):
    await state.update_data(period=message.text)

    data = await state.get_data()

    task = add_task(
        name=data["name"],
        description=data["description"],
        period=data["period"]
    )

    await message.answer(
        f"✅ Задача добавлена\n\n"
        f"ID: {task.id}\n"
        f"Название: {task.name}\n"
        f"Описание: {task.description}\n"
        f"Период: {task.period}",
        reply_markup=_main_menu_keyboard()
    )

    await state.clear()


    
@router.message(F.text == "Вывести все задачи")
async def start_get_tasks(message: types.Message, state: FSMContext):
    await state.set_state(AddTaskFSM.waiting_for_name)
    await message.answer(
        "Введите название задачи:",
        reply_markup=get_cancel_keyboard()
    )


def _main_menu_keyboard():
    return get_main_keyboard(is_day_started=get_active_day() is not None)
