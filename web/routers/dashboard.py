from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from core.services.days import get_day_statistics
from core.services.tasks import get_task_day_overview, list_tasks
from core.services.users import format_user_name
from web.dependencies.auth import get_current_user, redirect_to_login
from web.services.template import render_template


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def dashboard_page(request: Request, user=Depends(get_current_user)):
    if user is None:
        return redirect_to_login()

    overview = get_task_day_overview(user.id)
    today_stats = get_day_statistics(user.id, date.today())
    tasks = list_tasks(user.id, active_only=True)
    return render_template(
        request,
        "dashboard/index.html",
        title="Панель",
        active_page="dashboard",
        user=user,
        user_name=format_user_name(user),
        overview=overview,
        today_stats=today_stats,
        tasks_count=len(tasks),
    )
