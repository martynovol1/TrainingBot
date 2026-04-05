from __future__ import annotations

from datetime import date
from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

from web.services.flash import pop_flashes


BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def render_template(request: Request, template_name: str, **context):
    payload = {
        "request": request,
        "flashes": pop_flashes(request),
        "today": date.today(),
    }
    payload.update(context)
    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context=payload,
    )
