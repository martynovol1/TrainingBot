from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int | None] = mapped_column(Integer, unique=True, nullable=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    tasks: Mapped[list["Task"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    days: Mapped[list["Day"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    web_login_codes: Mapped[list["WebLoginCode"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, default=1)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    period: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None)

    user: Mapped["User"] = relationship(back_populates="tasks")
    task_completions: Mapped[list["TaskCompletion"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
    )


class Day(Base):
    __tablename__ = "days"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, default=1)
    date: Mapped[date] = mapped_column(Date, default=date.today)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_finished: Mapped[bool] = mapped_column(Boolean, default=False)
    total_consumed_calories: Mapped[int] = mapped_column(Integer, default=0)
    total_burned_calories: Mapped[int] = mapped_column(Integer, default=0)
    calorie_balance: Mapped[int] = mapped_column(Integer, default=0)

    user: Mapped["User"] = relationship(back_populates="days")
    food_entries: Mapped[list["FoodEntry"]] = relationship(
        back_populates="day",
        cascade="all, delete-orphan",
    )
    exercise_entries: Mapped[list["ExerciseEntry"]] = relationship(
        back_populates="day",
        cascade="all, delete-orphan",
    )
    task_completions: Mapped[list["TaskCompletion"]] = relationship(
        back_populates="day",
        cascade="all, delete-orphan",
    )


class FoodEntry(Base):
    __tablename__ = "food_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    day_id: Mapped[int] = mapped_column(ForeignKey("days.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    count: Mapped[str] = mapped_column(String, nullable=False)
    total_calories: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    day: Mapped["Day"] = relationship(back_populates="food_entries")


class ExerciseEntry(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    day_id: Mapped[int] = mapped_column(ForeignKey("days.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    burned_calories: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    day: Mapped["Day"] = relationship(back_populates="exercise_entries")


class TaskCompletion(Base):
    __tablename__ = "completing_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    day_id: Mapped[int] = mapped_column(ForeignKey("days.id"), nullable=False)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    day: Mapped["Day"] = relationship(back_populates="task_completions")
    task: Mapped["Task"] = relationship(back_populates="task_completions")


class WebLoginCode(Base):
    __tablename__ = "web_login_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="web_login_codes")
