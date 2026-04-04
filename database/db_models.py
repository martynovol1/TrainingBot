from datetime import date
from datetime import datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.db import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    period: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None)


class Day(Base):
    __tablename__ = "days"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, default=date.today)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_finished: Mapped[bool] = mapped_column(Boolean, default=False)
    total_consumed_calories: Mapped[int] = mapped_column(Integer, default=0)
    total_burned_calories: Mapped[int] = mapped_column(Integer, default=0)
    calorie_balance: Mapped[int] = mapped_column(Integer, default=0)

    food_entries: Mapped[list["FoodEntry"]] = relationship(
        back_populates="day",
        cascade="all, delete-orphan",
    )
    exercise_entries: Mapped[list["ExerciseEntry"]] = relationship(
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
