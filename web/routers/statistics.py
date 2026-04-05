from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from core.services.days import get_day_statistics
from core.services.users import format_user_name
from web.dependencies.auth import get_current_user, redirect_to_login
from web.forms.statistics import parse_statistics_query
from web.services.flash import push_flash
from web.services.template import render_template


router = APIRouter()


@router.get("/statistics", response_class=HTMLResponse)
async def statistics_page(request: Request, target_date: str | None = None, user=Depends(get_current_user)):
    if user is None:
        return redirect_to_login()

    statistics_query = parse_statistics_query(target_date)
    if target_date and statistics_query.target_date is None:
        push_flash(request, "Не удалось распознать дату. Используй формат ГГГГ-ММ-ДД.", "error")
        return RedirectResponse("/statistics", status_code=303)

    statistics = get_day_statistics(user.id, statistics_query.target_date)
    return render_template(
        request,
        "statistics/index.html",
        title="Статистика",
        active_page="statistics",
        user=user,
        user_name=format_user_name(user),
        selected_date=statistics_query.target_date,
        statistics=statistics,
    )
