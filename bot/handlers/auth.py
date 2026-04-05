from __future__ import annotations

from aiogram import F, Router, types

from bot.helpers import ensure_user
from bot.keyboards import GET_WEB_CODE_BUTTON, get_web_access_keyboard
from core.services.users import generate_web_login_code
from core.settings import settings


router = Router()


@router.message(F.text == GET_WEB_CODE_BUTTON)
async def send_web_login_code(message: types.Message):
    user = ensure_user(message.from_user)
    login_code = generate_web_login_code(user.id)
    await message.answer(
        "Код для входа на сайт:\n"
        f"`{login_code.code}`\n\n"
        f"Он действует {settings.login_code_ttl_minutes} минут.\n"
        f"Страница входа: {settings.web_base_url}/login",
        parse_mode="Markdown",
        reply_markup=get_web_access_keyboard(),
    )
