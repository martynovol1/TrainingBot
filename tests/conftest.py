from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import core.db as core_db
from core.services.users import generate_web_login_code, get_or_create_telegram_user
from web.app import create_app


@pytest.fixture(autouse=True)
def isolated_database(tmp_path, monkeypatch):
    database_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{database_path}", future=True)
    session_local = sessionmaker(bind=engine, expire_on_commit=False, future=True)

    monkeypatch.setattr(core_db, "engine", engine)
    monkeypatch.setattr(core_db, "SessionLocal", session_local)

    core_db.init_db()
    yield
    engine.dispose()


@pytest.fixture
def telegram_user():
    return SimpleNamespace(
        id=123456789,
        username="tester",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def app_user(telegram_user):
    return get_or_create_telegram_user(
        telegram_id=telegram_user.id,
        username=telegram_user.username,
        first_name=telegram_user.first_name,
        last_name=telegram_user.last_name,
    )


@pytest.fixture
def web_client():
    app = create_app()
    with TestClient(app) as client:
        yield client


@pytest.fixture
def logged_in_web_client(web_client, app_user):
    login_code = generate_web_login_code(app_user.id)
    response = web_client.post(
        "/login",
        data={"code": login_code.code},
        follow_redirects=False,
    )
    assert response.status_code == 303
    return web_client
