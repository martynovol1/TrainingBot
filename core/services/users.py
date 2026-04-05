from __future__ import annotations

import secrets
import string
from datetime import datetime, timedelta

from sqlalchemy import select

from core.db import session_scope
from core.models import User, WebLoginCode
from core.settings import settings


def get_or_create_telegram_user(
    telegram_id: int,
    username: str | None,
    first_name: str | None,
    last_name: str | None,
) -> User:
    with session_scope() as session:
        user = session.scalar(
            select(User).where(User.telegram_id == telegram_id)
        )
        if user is None:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
            session.add(user)
            session.flush()
            return user

        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        session.flush()
        return user


def get_user_by_id(user_id: int) -> User | None:
    with session_scope() as session:
        return session.get(User, user_id)


def get_user_by_telegram_id(telegram_id: int) -> User | None:
    with session_scope() as session:
        return session.scalar(
            select(User).where(User.telegram_id == telegram_id)
        )


def generate_web_login_code(user_id: int) -> WebLoginCode:
    alphabet = string.ascii_uppercase + string.digits
    code = "".join(secrets.choice(alphabet) for _ in range(8))
    expires_at = datetime.utcnow() + timedelta(minutes=settings.login_code_ttl_minutes)

    with session_scope() as session:
        session.query(WebLoginCode).filter(
            WebLoginCode.user_id == user_id,
            WebLoginCode.used_at.is_(None),
        ).delete()

        login_code = WebLoginCode(
            user_id=user_id,
            code=code,
            expires_at=expires_at,
        )
        session.add(login_code)
        session.flush()
        return login_code


def consume_web_login_code(code: str) -> User | None:
    normalized_code = code.strip().upper()
    now = datetime.utcnow()

    with session_scope() as session:
        login_code = session.scalar(
            select(WebLoginCode).where(WebLoginCode.code == normalized_code)
        )
        if login_code is None:
            return None
        if login_code.used_at is not None or login_code.expires_at < now:
            return None

        login_code.used_at = now
        session.flush()
        return session.get(User, login_code.user_id)


def format_user_name(user: User) -> str:
    parts = [user.first_name, user.last_name]
    full_name = " ".join(part for part in parts if part)
    if full_name:
        return full_name
    if user.username:
        return f"@{user.username}"
    return f"Пользователь #{user.id}"
