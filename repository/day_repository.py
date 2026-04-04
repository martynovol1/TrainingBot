from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from database.db import SessionLocal
from database.db_models import Day, ExerciseEntry, FoodEntry

BASE_METABOLISM_CALORIES = 1800


def get_active_day() -> Day | None:
    session = SessionLocal()

    try:
        return session.scalar(
            select(Day)
            .where(Day.is_finished.is_(False))
            .order_by(Day.started_at.desc())
        )
    finally:
        session.close()


def start_day() -> tuple[Day, bool]:
    session = SessionLocal()

    try:
        active_day = session.scalar(
            select(Day)
            .where(Day.is_finished.is_(False))
            .order_by(Day.started_at.desc())
        )
        if active_day is not None:
            session.expunge(active_day)
            return active_day, False

        day = Day()
        session.add(day)
        session.commit()
        session.refresh(day)
        session.expunge(day)
        return day, True
    finally:
        session.close()


def finish_day() -> Day | None:
    session = SessionLocal()

    try:
        day = session.scalar(
            select(Day)
            .where(Day.is_finished.is_(False))
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

        session.commit()
        session.refresh(day)
        session.expunge(day)
        return day
    finally:
        session.close()


def add_food_entry(name: str, count: str, total_calories: int) -> FoodEntry | None:
    session = SessionLocal()

    try:
        active_day = session.scalar(
            select(Day)
            .where(Day.is_finished.is_(False))
            .order_by(Day.started_at.desc())
        )
        if active_day is None:
            return None

        food_entry = FoodEntry(
            day_id=active_day.id,
            name=name,
            count=count,
            total_calories=total_calories,
        )
        session.add(food_entry)
        session.commit()
        session.refresh(food_entry)
        session.expunge(food_entry)
        return food_entry
    finally:
        session.close()


def add_exercise_entry(name: str, burned_calories: int) -> ExerciseEntry | None:
    session = SessionLocal()

    try:
        active_day = session.scalar(
            select(Day)
            .where(Day.is_finished.is_(False))
            .order_by(Day.started_at.desc())
        )
        if active_day is None:
            return None

        exercise_entry = ExerciseEntry(
            day_id=active_day.id,
            name=name,
            burned_calories=burned_calories,
        )
        session.add(exercise_entry)
        session.commit()
        session.refresh(exercise_entry)
        session.expunge(exercise_entry)
        return exercise_entry
    finally:
        session.close()


def get_day_statistics(target_date: date) -> dict | None:
    session = SessionLocal()

    try:
        day = session.scalar(
            select(Day)
            .options(
                selectinload(Day.food_entries),
                selectinload(Day.exercise_entries),
            )
            .where(Day.date == target_date)
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

        exercise_burned = sum(
            exercise["burned_calories"]
            for exercise in exercises
        )

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
            "totals": {
                "consumed": total_consumed,
                "exercise_burned": exercise_burned,
                "base_metabolism": BASE_METABOLISM_CALORIES,
                "burned": total_burned,
                "balance": balance,
            },
        }
    finally:
        session.close()
