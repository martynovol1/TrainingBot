from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from core.settings import settings


engine = create_engine(settings.database_url, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)


class Base(DeclarativeBase):
    pass


@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    from core import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _migrate_legacy_schema()


def _migrate_legacy_schema():
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    if not table_names:
        return

    with engine.begin() as connection:
        _ensure_default_user(connection)
        _ensure_column(
            inspector,
            connection,
            "days",
            "user_id",
            "INTEGER NOT NULL DEFAULT 1",
        )
        _ensure_column(
            inspector,
            connection,
            "tasks",
            "user_id",
            "INTEGER NOT NULL DEFAULT 1",
        )
        _ensure_column(
            inspector,
            connection,
            "days",
            "total_consumed_calories",
            "INTEGER NOT NULL DEFAULT 0",
        )
        _ensure_column(
            inspector,
            connection,
            "days",
            "total_burned_calories",
            "INTEGER NOT NULL DEFAULT 0",
        )
        _ensure_column(
            inspector,
            connection,
            "days",
            "calorie_balance",
            "INTEGER NOT NULL DEFAULT 0",
        )
        _ensure_column(
            inspector,
            connection,
            "users",
            "created_at",
            "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
        )

        if "tasks" in table_names:
            connection.execute(text("UPDATE tasks SET user_id = 1 WHERE user_id IS NULL"))
        if "days" in table_names:
            connection.execute(text("UPDATE days SET user_id = 1 WHERE user_id IS NULL"))


def _ensure_default_user(connection):
    existing_user_id = connection.execute(text("SELECT id FROM users LIMIT 1")).scalar()
    if existing_user_id is not None:
        return existing_user_id

    connection.execute(
        text(
            """
            INSERT INTO users (telegram_id, username, first_name, last_name, created_at)
            VALUES (NULL, 'legacy', 'Legacy', 'Import', :created_at)
            """
        ),
        {"created_at": datetime.utcnow()},
    )
    return connection.execute(text("SELECT id FROM users LIMIT 1")).scalar()


def _ensure_column(inspector, connection, table_name: str, column_name: str, definition: str):
    table_names = set(inspector.get_table_names())
    if table_name not in table_names:
        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns(table_name)
    }
    if column_name in existing_columns:
        return

    connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}"))
