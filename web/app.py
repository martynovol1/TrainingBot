from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from core.db import init_db
from core.settings import settings
from web.routers import include_routers


BASE_DIR = Path(__file__).resolve().parent


def create_app() -> FastAPI:
    app = FastAPI(title="Training Bot Web")
    app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
    include_routers(app)

    @app.on_event("startup")
    def on_startup():
        init_db()

    return app


app = create_app()
