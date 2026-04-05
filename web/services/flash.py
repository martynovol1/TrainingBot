from __future__ import annotations

from fastapi import Request


def push_flash(request: Request, message: str, category: str):
    flashes = request.session.get("_flash", [])
    flashes.append({"message": message, "category": category})
    request.session["_flash"] = flashes


def pop_flashes(request: Request) -> list[dict]:
    return request.session.pop("_flash", [])
