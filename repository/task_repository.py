from database.db import SessionLocal
from database.db_models import Task


def add_task(name: str, description: str, period: str) -> Task:
    session = SessionLocal()

    try:
        task = Task(
            name=name,
            description=description,
            period=period
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        return task
    finally:
        session.close()