from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from core.services.tasks import (
    complete_task_for_active_day,
    create_task,
    deactivate_task,
    get_task_day_overview,
    list_tasks,
)
from core.services.users import format_user_name
from web.dependencies.auth import get_current_user, redirect_to_login
from web.forms.tasks import parse_create_task_form
from web.services.flash import push_flash
from web.services.template import render_template


router = APIRouter()


@router.get("/tasks", response_class=HTMLResponse)
async def tasks_page(request: Request, user=Depends(get_current_user)):
    if user is None:
        return redirect_to_login()

    overview = get_task_day_overview(user.id)
    tasks = list_tasks(user.id, active_only=False)
    return render_template(
        request,
        "tasks/index.html",
        title="Задачи",
        active_page="tasks",
        user=user,
        user_name=format_user_name(user),
        overview=overview,
        tasks=tasks,
    )


@router.post("/tasks")
async def create_task_action(request: Request, user=Depends(get_current_user)):
    if user is None:
        return redirect_to_login()

    task_form = await parse_create_task_form(request)
    if not task_form.is_valid:
        push_flash(request, "Название и периодичность обязательны.", "error")
        return RedirectResponse("/tasks", status_code=303)

    create_task(user.id, task_form.name, task_form.description, task_form.period)
    push_flash(request, "Задача добавлена.", "success")
    return RedirectResponse("/tasks", status_code=303)


@router.post("/tasks/{task_id}/complete")
async def complete_task_action(task_id: int, request: Request, user=Depends(get_current_user)):
    if user is None:
        return redirect_to_login()

    status, task = complete_task_for_active_day(user.id, task_id)
    messages = {
        "completed": f"Задача «{task.name}» отмечена." if task else "Задача отмечена.",
        "no_active_day": "Сначала начни день в разделе калорий.",
        "not_found": "Задача не найдена.",
        "already_completed": "Эта задача уже выполнена сегодня.",
    }
    push_flash(
        request,
        messages.get(status, "Не удалось отметить задачу."),
        "success" if status == "completed" else "error",
    )
    return RedirectResponse("/tasks", status_code=303)


@router.post("/tasks/{task_id}/deactivate")
async def deactivate_task_action(task_id: int, request: Request, user=Depends(get_current_user)):
    if user is None:
        return redirect_to_login()

    if deactivate_task(user.id, task_id):
        push_flash(request, "Задача отключена.", "success")
    else:
        push_flash(request, "Задача не найдена.", "error")
    return RedirectResponse("/tasks", status_code=303)
