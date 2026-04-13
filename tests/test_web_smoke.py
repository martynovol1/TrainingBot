from __future__ import annotations

from datetime import date

from core.services.days import get_day_statistics
from core.services.tasks import list_tasks


def test_anonymous_user_is_redirected_to_login(web_client):
    response = web_client.get("/", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_logged_in_user_can_open_main_pages(logged_in_web_client):
    for path in ("/", "/tasks", "/calories", "/statistics"):
        response = logged_in_web_client.get(path)
        assert response.status_code == 200, path


def test_web_day_flow_does_not_crash(logged_in_web_client, app_user):
    start_day_response = logged_in_web_client.post("/calories/day/start", follow_redirects=False)
    create_task_response = logged_in_web_client.post(
        "/tasks",
        data={
            "name": "Read book",
            "description": "15 minutes",
            "period": "daily",
        },
        follow_redirects=False,
    )

    assert start_day_response.status_code == 303
    assert create_task_response.status_code == 303

    tasks = list_tasks(app_user.id, active_only=False)
    assert len(tasks) == 1
    task = tasks[0]

    complete_task_response = logged_in_web_client.post(
        f"/tasks/{task.id}/complete",
        follow_redirects=False,
    )
    add_food_response = logged_in_web_client.post(
        "/calories/food",
        data={
            "name": "Salad",
            "count": "1 bowl",
            "total_calories": "350",
        },
        follow_redirects=False,
    )
    add_exercise_response = logged_in_web_client.post(
        "/calories/exercise",
        data={
            "name": "Walk",
            "burned_calories": "200",
        },
        follow_redirects=False,
    )
    finish_day_response = logged_in_web_client.post("/calories/day/finish", follow_redirects=False)
    statistics_response = logged_in_web_client.get(f"/statistics?target_date={date.today():%Y-%m-%d}")

    assert complete_task_response.status_code == 303
    assert add_food_response.status_code == 303
    assert add_exercise_response.status_code == 303
    assert finish_day_response.status_code == 303
    assert statistics_response.status_code == 200

    statistics = get_day_statistics(app_user.id, date.today())
    assert statistics is not None
    assert statistics["day"]["is_finished"] is True
    assert statistics["foods"][0]["name"] == "Salad"
    assert statistics["exercises"][0]["name"] == "Walk"
    assert statistics["completed_tasks"][0]["name"] == "Read book"
