from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from core.db import init_db
from core.services.days import (
    add_exercise_entry,
    add_food_entry,
    finish_day,
    get_active_day,
    get_day_statistics,
    start_day,
)
from core.services.tasks import (
    complete_task_for_active_day,
    create_task,
    deactivate_task,
    get_task_day_overview,
    list_tasks,
)
from core.services.users import consume_web_login_code, format_user_name, get_user_by_id
from core.settings import settings


BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="Training Bot Web")
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if _get_current_user(request) is not None:
        return RedirectResponse("/", status_code=303)
    return _render(request, "login.html", title="Вход", active_page="login")


@app.post("/login")
async def login_action(request: Request):
    form = await request.form()
    code = str(form.get("code", "")).strip()
    user = consume_web_login_code(code)
    if user is None:
        _push_flash(request, "Код недействителен или истёк.", "error")
        return RedirectResponse("/login", status_code=303)

    request.session["user_id"] = user.id
    _push_flash(request, f"Вход выполнен. Привет, {format_user_name(user)}.", "success")
    return RedirectResponse("/", status_code=303)


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


@app.get("/", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    user = _require_user(request)
    if user is None:
        return RedirectResponse("/login", status_code=303)

    overview = get_task_day_overview(user.id)
    today_stats = get_day_statistics(user.id, date.today())
    tasks = list_tasks(user.id, active_only=True)
    return _render(
        request,
        "dashboard.html",
        title="Панель",
        active_page="dashboard",
        user=user,
        user_name=format_user_name(user),
        overview=overview,
        today_stats=today_stats,
        tasks_count=len(tasks),
    )


@app.get("/tasks", response_class=HTMLResponse)
async def tasks_page(request: Request):
    user = _require_user(request)
    if user is None:
        return RedirectResponse("/login", status_code=303)

    overview = get_task_day_overview(user.id)
    tasks = list_tasks(user.id, active_only=False)
    return _render(
        request,
        "tasks.html",
        title="Задачи",
        active_page="tasks",
        user=user,
        user_name=format_user_name(user),
        overview=overview,
        tasks=tasks,
    )


@app.post("/tasks")
async def create_task_action(request: Request):
    user = _require_user(request)
    if user is None:
        return RedirectResponse("/login", status_code=303)

    form = await request.form()
    name = str(form.get("name", "")).strip()
    description = str(form.get("description", "")).strip()
    period = str(form.get("period", "")).strip()

    if not name or not period:
        _push_flash(request, "Название и периодичность обязательны.", "error")
        return RedirectResponse("/tasks", status_code=303)

    create_task(user.id, name, description or None, period)
    _push_flash(request, "Задача добавлена.", "success")
    return RedirectResponse("/tasks", status_code=303)


@app.post("/tasks/{task_id}/complete")
async def complete_task_action(task_id: int, request: Request):
    user = _require_user(request)
    if user is None:
        return RedirectResponse("/login", status_code=303)

    status, task = complete_task_for_active_day(user.id, task_id)
    messages = {
        "completed": f"Задача «{task.name}» отмечена." if task else "Задача отмечена.",
        "no_active_day": "Сначала начни день в разделе калорий.",
        "not_found": "Задача не найдена.",
        "already_completed": "Эта задача уже выполнена сегодня.",
    }
    _push_flash(request, messages.get(status, "Не удалось отметить задачу."), "success" if status == "completed" else "error")
    return RedirectResponse("/tasks", status_code=303)


@app.post("/tasks/{task_id}/deactivate")
async def deactivate_task_action(task_id: int, request: Request):
    user = _require_user(request)
    if user is None:
        return RedirectResponse("/login", status_code=303)

    if deactivate_task(user.id, task_id):
        _push_flash(request, "Задача отключена.", "success")
    else:
        _push_flash(request, "Задача не найдена.", "error")
    return RedirectResponse("/tasks", status_code=303)


@app.get("/calories", response_class=HTMLResponse)
async def calories_page(request: Request):
    user = _require_user(request)
    if user is None:
        return RedirectResponse("/login", status_code=303)

    active_day = get_active_day(user.id)
    today_stats = get_day_statistics(user.id, date.today())
    return _render(
        request,
        "calories.html",
        title="Калории",
        active_page="calories",
        user=user,
        user_name=format_user_name(user),
        active_day=active_day,
        today_stats=today_stats,
    )


@app.post("/calories/day/start")
async def start_day_action(request: Request):
    user = _require_user(request)
    if user is None:
        return RedirectResponse("/login", status_code=303)

    day, status = start_day(user.id)
    messages = {
        "created": f"День {day.date:%d.%m.%Y} начат.",
        "active": f"У тебя уже есть активный день за {day.date:%d.%m.%Y}.",
        "already_exists": f"День за {day.date:%d.%m.%Y} уже был начат раньше.",
    }
    _push_flash(request, messages[status], "success" if status == "created" else "error")
    return RedirectResponse("/calories", status_code=303)


@app.post("/calories/day/finish")
async def finish_day_action(request: Request):
    user = _require_user(request)
    if user is None:
        return RedirectResponse("/login", status_code=303)

    day = finish_day(user.id)
    if day is None:
        _push_flash(request, "Сейчас нет активного дня.", "error")
    else:
        _push_flash(request, f"День {day.date:%d.%m.%Y} завершён.", "success")
    return RedirectResponse("/calories", status_code=303)


@app.post("/calories/food")
async def add_food_action(request: Request):
    user = _require_user(request)
    if user is None:
        return RedirectResponse("/login", status_code=303)

    form = await request.form()
    name = str(form.get("name", "")).strip()
    count = str(form.get("count", "")).strip()
    calories_value = str(form.get("total_calories", "")).strip()

    try:
        total_calories = int(calories_value)
    except ValueError:
        total_calories = 0

    if not name or not count or total_calories <= 0:
        _push_flash(request, "Проверь название, количество и калории.", "error")
        return RedirectResponse("/calories", status_code=303)

    entry = add_food_entry(user.id, name, count, total_calories)
    _push_flash(request, "Еда добавлена." if entry else "Сначала начни день.", "success" if entry else "error")
    return RedirectResponse("/calories", status_code=303)


@app.post("/calories/exercise")
async def add_exercise_action(request: Request):
    user = _require_user(request)
    if user is None:
        return RedirectResponse("/login", status_code=303)

    form = await request.form()
    name = str(form.get("name", "")).strip()
    calories_value = str(form.get("burned_calories", "")).strip()

    try:
        burned_calories = int(calories_value)
    except ValueError:
        burned_calories = 0

    if not name or burned_calories <= 0:
        _push_flash(request, "Проверь название и калории.", "error")
        return RedirectResponse("/calories", status_code=303)

    entry = add_exercise_entry(user.id, name, burned_calories)
    _push_flash(request, "Движение добавлено." if entry else "Сначала начни день.", "success" if entry else "error")
    return RedirectResponse("/calories", status_code=303)


@app.get("/statistics", response_class=HTMLResponse)
async def statistics_page(request: Request, target_date: str | None = None):
    user = _require_user(request)
    if user is None:
        return RedirectResponse("/login", status_code=303)

    parsed_date = _parse_web_date(target_date) if target_date else date.today()
    if target_date and parsed_date is None:
        _push_flash(request, "Не удалось распознать дату. Используй формат ГГГГ-ММ-ДД.", "error")
        return RedirectResponse("/statistics", status_code=303)

    statistics = get_day_statistics(user.id, parsed_date)
    return _render(
        request,
        "statistics.html",
        title="Статистика",
        active_page="statistics",
        user=user,
        user_name=format_user_name(user),
        selected_date=parsed_date,
        statistics=statistics,
    )


def _render(request: Request, template_name: str, **context):
    flashes = request.session.pop("_flash", [])
    payload = {"request": request, "flashes": flashes, "today": date.today()}
    payload.update(context)
    return templates.TemplateResponse(template_name, payload)


def _push_flash(request: Request, message: str, category: str):
    flashes = request.session.get("_flash", [])
    flashes.append({"message": message, "category": category})
    request.session["_flash"] = flashes


def _get_current_user(request: Request):
    user_id = request.session.get("user_id")
    if user_id is None:
        return None
    return get_user_by_id(int(user_id))


def _require_user(request: Request):
    return _get_current_user(request)


def _parse_web_date(value: str | None):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None
