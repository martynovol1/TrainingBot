from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.db import session_scope
from core.models import Day, Task, TaskCompletion


def create_task(user_id: int, name: str, description: str | None, period: str) -> Task:
    with session_scope() as session:
        task = Task(
            user_id=user_id,
            name=name.strip(),
            description=(description or "").strip() or None,
            period=period.strip(),
        )
        session.add(task)
        session.flush()
        return task


def list_tasks(user_id: int, active_only: bool = False) -> list[Task]:
    with session_scope() as session:
        query = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
        if active_only:
            query = query.where(Task.is_active.is_(True))
        return list(session.scalars(query))


def deactivate_task(user_id: int, task_id: int) -> bool:
    with session_scope() as session:
        task = session.scalar(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        if task is None:
            return False
        task.is_active = False
        session.flush()
        return True


def get_task_day_overview(user_id: int) -> dict:
    with session_scope() as session:
        active_day = session.scalar(
            select(Day)
            .options(
                selectinload(Day.task_completions).selectinload(TaskCompletion.task)
            )
            .where(Day.user_id == user_id, Day.is_finished.is_(False))
            .order_by(Day.started_at.desc())
        )

        tasks = list(
            session.scalars(
                select(Task)
                .where(Task.user_id == user_id, Task.is_active.is_(True))
                .order_by(Task.created_at.desc())
            )
        )
        if active_day is None:
            return {
                "active_day": None,
                "pending_tasks": tasks,
                "completed_tasks": [],
            }

        completed_map = {
            completion.task_id: completion
            for completion in active_day.task_completions
        }
        pending_tasks = [task for task in tasks if task.id not in completed_map]
        completed_tasks = [completed_map[task.id].task for task in tasks if task.id in completed_map]

        return {
            "active_day": active_day,
            "pending_tasks": pending_tasks,
            "completed_tasks": completed_tasks,
        }


def complete_task_for_active_day(user_id: int, task_id: int) -> tuple[str, Task | None]:
    with session_scope() as session:
        active_day = session.scalar(
            select(Day)
            .options(selectinload(Day.task_completions))
            .where(Day.user_id == user_id, Day.is_finished.is_(False))
            .order_by(Day.started_at.desc())
        )
        if active_day is None:
            return "no_active_day", None

        task = session.scalar(
            select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id,
                Task.is_active.is_(True),
            )
        )
        if task is None:
            return "not_found", None

        existing_completion = next(
            (completion for completion in active_day.task_completions if completion.task_id == task.id),
            None,
        )
        if existing_completion is not None:
            return "already_completed", task

        completion = TaskCompletion(day_id=active_day.id, task_id=task.id)
        session.add(completion)
        task.last_completed_at = datetime.utcnow()
        session.flush()
        return "completed", task
