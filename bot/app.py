from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher

from bot.handlers.auth import router as auth_router
from bot.handlers.days import router as days_router
from bot.handlers.menu import router as menu_router
from bot.handlers.tasks import router as tasks_router
from core.db import init_db
from core.settings import settings


def build_dispatcher() -> Dispatcher:
    dispatcher = Dispatcher()
    dispatcher.include_router(menu_router)
    dispatcher.include_router(auth_router)
    dispatcher.include_router(tasks_router)
    dispatcher.include_router(days_router)
    return dispatcher


async def main():
    if not settings.bot_token:
        raise RuntimeError("BOT_API_TOKEN is not configured")

    init_db()
    bot = Bot(token=settings.bot_token)
    dispatcher = build_dispatcher()

    try:
        me = await bot.get_me()
        print(f"Bot started: @{me.username}")
        await bot.delete_webhook(drop_pending_updates=True)
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
