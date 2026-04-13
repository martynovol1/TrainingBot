from __future__ import annotations

import asyncio

from sqlalchemy import select

from bot.app import build_dispatcher
from bot.handlers.auth import send_web_login_code
from bot.handlers.days import handle_finish_day, handle_start_day
from bot.handlers.menu import cmd_start
from bot.handlers.tasks import show_all_tasks
from core.db import session_scope
from core.models import WebLoginCode
from core.services.tasks import create_task


class FakeFSMContext:
    def __init__(self):
        self.current_state = None
        self.data = {}

    async def clear(self):
        self.current_state = None
        self.data = {}

    async def set_state(self, value):
        self.current_state = value

    async def update_data(self, **kwargs):
        self.data.update(kwargs)

    async def get_data(self):
        return dict(self.data)

    async def get_state(self):
        return self.current_state


class FakeMessage:
    def __init__(self, from_user, text: str = ""):
        self.from_user = from_user
        self.text = text
        self.answers = []

    async def answer(self, text, reply_markup=None, parse_mode=None):
        self.answers.append(
            {
                "text": text,
                "reply_markup": reply_markup,
                "parse_mode": parse_mode,
            }
        )


def test_dispatcher_is_built_with_message_and_callback_handlers():
    dispatcher = build_dispatcher()
    update_types = dispatcher.resolve_used_update_types()

    assert "message" in update_types
    assert "callback_query" in update_types


def test_start_command_handler_replies_without_crashing(telegram_user):
    message = FakeMessage(telegram_user, text="/start")
    state = FakeFSMContext()

    asyncio.run(cmd_start(message, state))

    assert len(message.answers) == 1
    assert message.answers[0]["reply_markup"] is not None


def test_web_code_handler_creates_login_code(telegram_user):
    message = FakeMessage(telegram_user)

    asyncio.run(send_web_login_code(message))

    with session_scope() as session:
        codes = list(
            session.scalars(
                select(WebLoginCode).where(WebLoginCode.code.is_not(None))
            )
        )

    assert len(codes) == 1
    assert "/login" in message.answers[0]["text"]


def test_tasks_handler_lists_existing_tasks(app_user, telegram_user):
    create_task(app_user.id, "Stretching", "10 minutes", "daily")
    message = FakeMessage(telegram_user)
    state = FakeFSMContext()

    asyncio.run(show_all_tasks(message, state))

    assert len(message.answers) == 2
    assert "Stretching" in message.answers[1]["text"]


def test_day_handlers_can_start_and_finish_day(telegram_user):
    start_message = FakeMessage(telegram_user)
    finish_message = FakeMessage(telegram_user)
    state = FakeFSMContext()

    asyncio.run(handle_start_day(start_message, state))
    asyncio.run(handle_finish_day(finish_message, state))

    assert len(start_message.answers) == 1
    assert len(finish_message.answers) == 1
