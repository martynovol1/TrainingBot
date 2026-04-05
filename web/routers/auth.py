from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from core.services.users import consume_web_login_code, format_user_name
from web.dependencies.auth import get_current_user
from web.forms.auth import parse_login_form
from web.services.flash import push_flash
from web.services.template import render_template


router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, user=Depends(get_current_user)):
    if user is not None:
        return RedirectResponse("/", status_code=303)
    return render_template(request, "auth/login.html", title="Вход", active_page="login")


@router.post("/login")
async def login_action(request: Request):
    login_form = await parse_login_form(request)
    user = consume_web_login_code(login_form.code)
    if user is None:
        push_flash(request, "Код недействителен или истёк.", "error")
        return RedirectResponse("/login", status_code=303)

    request.session["user_id"] = user.id
    push_flash(
        request,
        f"Вход выполнен. Привет, {format_user_name(user)}.",
        "success",
    )
    return RedirectResponse("/", status_code=303)


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
