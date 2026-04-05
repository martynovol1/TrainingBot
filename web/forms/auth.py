from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request


@dataclass(slots=True)
class LoginForm:
    code: str


async def parse_login_form(request: Request) -> LoginForm:
    form = await request.form()
    return LoginForm(
        code=str(form.get("code", "")).strip(),
    )
