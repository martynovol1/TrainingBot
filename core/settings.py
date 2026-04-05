from __future__ import annotations

import os
from dataclasses import dataclass


def _load_bot_token() -> str:
    token = os.getenv("BOT_API_TOKEN")
    if token:
        return token

    try:
        from tokens.bot_token import BOT_API
    except Exception:
        return ""

    return BOT_API


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///tasks.db")
    bot_token: str = _load_bot_token()
    secret_key: str = os.getenv(
        "APP_SECRET_KEY",
        "change-me-in-production-training-bot-secret",
    )
    web_base_url: str = os.getenv("WEB_BASE_URL", "http://127.0.0.1:8000")
    base_metabolism_calories: int = int(os.getenv("BASE_METABOLISM_CALORIES", "1800"))
    login_code_ttl_minutes: int = int(os.getenv("LOGIN_CODE_TTL_MINUTES", "10"))


settings = Settings()
