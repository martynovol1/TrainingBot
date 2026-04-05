from __future__ import annotations

from fastapi import FastAPI

from web.routers.auth import router as auth_router
from web.routers.calories import router as calories_router
from web.routers.dashboard import router as dashboard_router
from web.routers.statistics import router as statistics_router
from web.routers.tasks import router as tasks_router


def include_routers(app: FastAPI):
    app.include_router(auth_router)
    app.include_router(dashboard_router)
    app.include_router(tasks_router)
    app.include_router(calories_router)
    app.include_router(statistics_router)
