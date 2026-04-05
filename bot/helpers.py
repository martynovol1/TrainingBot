from __future__ import annotations

import re
from datetime import datetime

from aiogram import types

from core.services.users import get_or_create_telegram_user


def ensure_user(telegram_user: types.User):
    return get_or_create_telegram_user(
        telegram_id=telegram_user.id,
        username=telegram_user.username,
        first_name=telegram_user.first_name,
        last_name=telegram_user.last_name,
    )


def parse_positive_int(value: str | None) -> int | None:
    if value is None:
        return None

    try:
        parsed_value = int(value.strip())
    except ValueError:
        return None

    return parsed_value if parsed_value > 0 else None


def parse_date(value: str | None):
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


def format_balance(balance: int) -> str:
    if balance > 0:
        return f"дефицит {balance} ккал"
    if balance < 0:
        return f"профицит {abs(balance)} ккал"
    return "баланс 0 ккал"
