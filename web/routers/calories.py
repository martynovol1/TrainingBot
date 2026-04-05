from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from core.services.days import (
    add_exercise_entry,
    add_food_entry,
    finish_day,
    get_active_day,
    get_day_statistics,
    start_day,
)
from core.services.users import format_user_name
from web.dependencies.auth import get_current_user, redirect_to_login
from web.forms.calories import parse_exercise_form, parse_food_form
from web.services.flash import push_flash
from web.services.template import render_template


router = APIRouter()


@router.get("/calories", response_class=HTMLResponse)
async def calories_page(request: Request, user=Depends(get_current_user)):
    if user is None:
        return redirect_to_login()

    active_day = get_active_day(user.id)
    today_stats = get_day_statistics(user.id, date.today())
    return render_template(
        request,
        "calories/index.html",
        title="Калории",
        active_page="calories",
        user=user,
        user_name=format_user_name(user),
        active_day=active_day,
        today_stats=today_stats,
    )


@router.post("/calories/day/start")
async def start_day_action(request: Request, user=Depends(get_current_user)):
    if user is None:
        return redirect_to_login()

    day, status = start_day(user.id)
    messages = {
        "created": f"День {day.date:%d.%m.%Y} начат.",
        "active": f"У тебя уже есть активный день за {day.date:%d.%m.%Y}.",
        "already_exists": f"День за {day.date:%d.%m.%Y} уже был начат раньше.",
    }
    push_flash(request, messages[status], "success" if status == "created" else "error")
    return RedirectResponse("/calories", status_code=303)


@router.post("/calories/day/finish")
async def finish_day_action(request: Request, user=Depends(get_current_user)):
    if user is None:
        return redirect_to_login()

    day = finish_day(user.id)
    if day is None:
        push_flash(request, "Сейчас нет активного дня.", "error")
    else:
        push_flash(request, f"День {day.date:%d.%m.%Y} завершён.", "success")
    return RedirectResponse("/calories", status_code=303)


@router.post("/calories/food")
async def add_food_action(request: Request, user=Depends(get_current_user)):
    if user is None:
        return redirect_to_login()

    food_form = await parse_food_form(request)
    if not food_form.is_valid:
        push_flash(request, "Проверь название, количество и калории.", "error")
        return RedirectResponse("/calories", status_code=303)

    entry = add_food_entry(user.id, food_form.name, food_form.count, food_form.total_calories)
    push_flash(
        request,
        "Еда добавлена." if entry else "Сначала начни день.",
        "success" if entry else "error",
    )
    return RedirectResponse("/calories", status_code=303)


@router.post("/calories/exercise")
async def add_exercise_action(request: Request, user=Depends(get_current_user)):
    if user is None:
        return redirect_to_login()

    exercise_form = await parse_exercise_form(request)
    if not exercise_form.is_valid:
        push_flash(request, "Проверь название и калории.", "error")
        return RedirectResponse("/calories", status_code=303)

    entry = add_exercise_entry(user.id, exercise_form.name, exercise_form.burned_calories)
    push_flash(
        request,
        "Движение добавлено." if entry else "Сначала начни день.",
        "success" if entry else "error",
    )
    return RedirectResponse("/calories", status_code=303)
