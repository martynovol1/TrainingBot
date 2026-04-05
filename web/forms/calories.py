from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request


def _parse_positive_int(value: str) -> int:
    try:
        parsed_value = int(value)
    except ValueError:
        return 0
    return parsed_value if parsed_value > 0 else 0


@dataclass(slots=True)
class FoodForm:
    name: str
    count: str
    total_calories: int

    @property
    def is_valid(self) -> bool:
        return bool(self.name and self.count and self.total_calories > 0)


@dataclass(slots=True)
class ExerciseForm:
    name: str
    burned_calories: int

    @property
    def is_valid(self) -> bool:
        return bool(self.name and self.burned_calories > 0)


async def parse_food_form(request: Request) -> FoodForm:
    form = await request.form()
    return FoodForm(
        name=str(form.get("name", "")).strip(),
        count=str(form.get("count", "")).strip(),
        total_calories=_parse_positive_int(str(form.get("total_calories", "")).strip()),
    )


async def parse_exercise_form(request: Request) -> ExerciseForm:
    form = await request.form()
    return ExerciseForm(
        name=str(form.get("name", "")).strip(),
        burned_calories=_parse_positive_int(str(form.get("burned_calories", "")).strip()),
    )
