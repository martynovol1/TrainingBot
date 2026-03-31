import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from tokens.bot_token import BOT_API
from database.db import init_db
from fsm.fsm_tasks import router as tasks_router
from keyboards.task_keyboards import get_main_keyboard

dp = Dispatcher()
dp.include_router(tasks_router)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет 👋\n"
        "Я бот для ежедневных задач.",
        reply_markup=get_main_keyboard()
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