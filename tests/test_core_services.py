from __future__ import annotations

from datetime import date

from core.services.days import (
    BASE_METABOLISM_CALORIES,
    add_exercise_entry,
    add_food_entry,
    finish_day,
    get_day_closure_snapshot,
    get_day_statistics,
    start_day,
)
from core.services.tasks import (
    complete_task_for_active_day,
    create_task,
    get_task_day_overview,
)
from core.services.users import consume_web_login_code, generate_web_login_code


def test_day_lifecycle_and_statistics(app_user):
    task = create_task(app_user.id, "Workout", "Morning session", "daily")

    day, status = start_day(app_user.id)
    assert status == "created"
    assert day.user_id == app_user.id

    food_entry = add_food_entry(app_user.id, "Oatmeal", "250 g", 450)
    exercise_entry = add_exercise_entry(app_user.id, "Run", 300)
    completion_status, completed_task = complete_task_for_active_day(app_user.id, task.id)

    assert food_entry is not None
    assert exercise_entry is not None
    assert completion_status == "completed"
    assert completed_task is not None
    assert completed_task.id == task.id

    overview = get_task_day_overview(app_user.id)
    assert overview["active_day"] is not None
    assert [item.id for item in overview["completed_tasks"]] == [task.id]
    assert overview["pending_tasks"] == []

    closure_snapshot = get_day_closure_snapshot(app_user.id)
    assert closure_snapshot is not None
    assert closure_snapshot["day"]["id"] == day.id
    assert closure_snapshot["counts"] == {
        "foods": 1,
        "exercises": 1,
        "completed_tasks": 1,
    }
    assert closure_snapshot["totals"] == {
        "consumed": 450,
        "exercise_burned": 300,
        "base_metabolism": BASE_METABOLISM_CALORIES,
        "burned": BASE_METABOLISM_CALORIES + 300,
        "balance": BASE_METABOLISM_CALORIES + 300 - 450,
    }

    finished_day = finish_day(app_user.id)
    assert finished_day is not None
    assert finished_day.is_finished is True
    assert finished_day.total_consumed_calories == 450
    assert finished_day.total_burned_calories == BASE_METABOLISM_CALORIES + 300
    assert finished_day.calorie_balance == BASE_METABOLISM_CALORIES + 300 - 450

    statistics = get_day_statistics(app_user.id, date.today())
    assert statistics is not None
    assert statistics["day"]["is_finished"] is True
    assert statistics["foods"][0]["name"] == "Oatmeal"
    assert statistics["exercises"][0]["name"] == "Run"
    assert statistics["completed_tasks"][0]["name"] == "Workout"
    assert statistics["totals"] == {
        "consumed": 450,
        "exercise_burned": 300,
        "base_metabolism": BASE_METABOLISM_CALORIES,
        "burned": BASE_METABOLISM_CALORIES + 300,
        "balance": BASE_METABOLISM_CALORIES + 300 - 450,
        "completed_tasks": 1,
    }


def test_task_day_overview_is_empty_without_active_day(app_user):
    create_task(app_user.id, "Read", "10 pages", "daily")

    overview = get_task_day_overview(app_user.id)

    assert overview["active_day"] is None
    assert overview["pending_tasks"] == []
    assert overview["completed_tasks"] == []


def test_web_login_codes_are_single_use(app_user):
    login_code = generate_web_login_code(app_user.id)

    consumed_user = consume_web_login_code(login_code.code.lower())
    consumed_twice = consume_web_login_code(login_code.code)

    assert consumed_user is not None
    assert consumed_user.id == app_user.id
    assert consumed_twice is None
