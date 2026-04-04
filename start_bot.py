import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from tokens.bot_token import BOT_API
from database.db import init_db
from fsm.fsm_day import router as day_router
from fsm.fsm_tasks import router as tasks_router
from keyboards.task_keyboards import get_main_keyboard
from repository.day_repository import get_active_day

dp = Dispatcher()
dp.include_router(tasks_router)
dp.include_router(day_router)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет 👋\n"
        "Я помогу вести день, еду, движение и смотреть статистику.",
        reply_markup=get_main_keyboard(is_day_started=get_active_day() is not None)
    )


async def main():
    bot = Bot(token=BOT_API)

    try:
        init_db()

        me = await bot.get_me()
        print(f"✅ Бот запущен: @{me.username}")

        await bot.delete_webhook(drop_pending_updates=True)
        print("🚀 Polling started...")

        await dp.start_polling(bot)
    except Exception as e:
        print("❌ Ошибка запуска:", repr(e))
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
