from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request


@dataclass(slots=True)
class CreateTaskForm:
    name: str
    description: str | None
    period: str

    @property
    def is_valid(self) -> bool:
        return bool(self.name and self.period)


async def parse_create_task_form(request: Request) -> CreateTaskForm:
    form = await request.form()
    name = str(form.get("name", "")).strip()
    description = str(form.get("description", "")).strip()
    period = str(form.get("period", "")).strip()
    return CreateTaskForm(
        name=name,
        description=description or None,
        period=period,
    )
