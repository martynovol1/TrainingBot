from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from core.db import session_scope
from core.models import Day, ExerciseEntry, FoodEntry, TaskCompletion
from core.settings import settings


BASE_METABOLISM_CALORIES = settings.base_metabolism_calories


def get_active_day(user_id: int) -> Day | None:
    with session_scope() as session:
        return session.scalar(
            select(Day)
            .where(Day.user_id == user_id, Day.is_finished.is_(False))
            .order_by(Day.started_at.desc())
        )


def start_day(user_id: int) -> tuple[Day, str]:
    with session_scope() as session:
        active_day = session.scalar(
            select(Day)
            .where(Day.user_id == user_id, Day.is_finished.is_(False))
            .order_by(Day.started_at.desc())
        )
        if active_day is not None:
            return active_day, "active"

        existing_day = session.scalar(
            select(Day)
            .where(Day.user_id == user_id, Day.date == date.today())
            .order_by(Day.started_at.desc())
        )
        if existing_day is not None:
            return existing_day, "already_exists"

        day = Day(user_id=user_id)
        session.add(day)
        session.flush()
        return day, "created"


def finish_day(user_id: int) -> Day | None:
    with session_scope() as session:
        day = session.scalar(
            select(Day)
            .where(Day.user_id == user_id, Day.is_finished.is_(False))
            .order_by(Day.started_at.desc())
        )
        if day is None:
            return None

        total_consumed = session.scalar(
            select(func.coalesce(func.sum(FoodEntry.total_calories), 0))
            .where(FoodEntry.day_id == day.id)
        ) or 0
        exercise_burned = session.scalar(
            select(func.coalesce(func.sum(ExerciseEntry.burned_calories), 0))
            .where(ExerciseEntry.day_id == day.id)
        ) or 0
        total_burned = int(exercise_burned) + BASE_METABOLISM_CALORIES

        day.finished_at = datetime.utcnow()
        day.is_finished = True
        day.total_consumed_calories = int(total_consumed)
        day.total_burned_calories = total_burned
        day.calorie_balance = int(total_burned - total_consumed)
        session.flush()
        return day


def add_food_entry(user_id: int, name: str, count: str, total_calories: int) -> FoodEntry | None:
    with session_scope() as session:
        active_day = session.scalar(
            select(Day)
            .where(Day.user_id == user_id, Day.is_finished.is_(False))
            .order_by(Day.started_at.desc())
        )
        if active_day is None:
            return None

        food_entry = FoodEntry(
            day_id=active_day.id,
            name=name.strip(),
            count=count.strip(),
            total_calories=total_calories,
        )
        session.add(food_entry)
        session.flush()
        return food_entry


def add_exercise_entry(user_id: int, name: str, burned_calories: int) -> ExerciseEntry | None:
    with session_scope() as session:
        active_day = session.scalar(
            select(Day)
            .where(Day.user_id == user_id, Day.is_finished.is_(False))
            .order_by(Day.started_at.desc())
        )
        if active_day is None:
            return None

        exercise_entry = ExerciseEntry(
            day_id=active_day.id,
            name=name.strip(),
            burned_calories=burned_calories,
        )
        session.add(exercise_entry)
        session.flush()
        return exercise_entry


def get_day_statistics(user_id: int, target_date: date) -> dict | None:
    with session_scope() as session:
        day = session.scalar(
            select(Day)
            .options(
                selectinload(Day.food_entries),
                selectinload(Day.exercise_entries),
                selectinload(Day.task_completions).selectinload(TaskCompletion.task),
            )
            .where(Day.user_id == user_id, Day.date == target_date)
            .order_by(Day.started_at.desc())
        )
        if day is None:
            return None

        foods = [
            {
                "name": food.name,
                "count": food.count,
                "total_calories": food.total_calories,
            }
            for food in day.food_entries
        ]
        exercises = [
            {
                "name": exercise.name,
                "burned_calories": exercise.burned_calories,
            }
            for exercise in day.exercise_entries
        ]
        completed_tasks = [
            {
                "name": completion.task.name if completion.task else "Без названия",
                "completed_at": completion.completed_at,
            }
            for completion in day.task_completions
        ]

        exercise_burned = sum(exercise["burned_calories"] for exercise in exercises)
        if day.is_finished:
            total_consumed = day.total_consumed_calories
            total_burned = day.total_burned_calories
            balance = day.calorie_balance
        else:
            total_consumed = sum(food["total_calories"] for food in foods)
            total_burned = exercise_burned + BASE_METABOLISM_CALORIES
            balance = total_burned - total_consumed

        return {
            "day": {
                "id": day.id,
                "date": day.date,
                "started_at": day.started_at,
                "finished_at": day.finished_at,
                "is_finished": day.is_finished,
            },
            "foods": foods,
            "exercises": exercises,
            "completed_tasks": completed_tasks,
            "totals": {
                "consumed": total_consumed,
                "exercise_burned": exercise_burned,
                "base_metabolism": BASE_METABOLISM_CALORIES,
                "burned": total_burned,
                "balance": balance,
            },
        }
