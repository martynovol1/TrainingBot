from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///tasks.db"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def init_db():
    from database import db_models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _ensure_schema()


def _ensure_schema():
    inspector = inspect(engine)

    if "days" not in inspector.get_table_names():
        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("days")
    }

    required_columns = {
        "total_consumed_calories": "ALTER TABLE days ADD COLUMN total_consumed_calories INTEGER NOT NULL DEFAULT 0",
        "total_burned_calories": "ALTER TABLE days ADD COLUMN total_burned_calories INTEGER NOT NULL DEFAULT 0",
        "calorie_balance": "ALTER TABLE days ADD COLUMN calorie_balance INTEGER NOT NULL DEFAULT 0",
    }

    with engine.begin() as connection:
        for column_name, statement in required_columns.items():
            if column_name not in existing_columns:
                connection.execute(text(statement))
