from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import ads, health, search, users


def build_v1_router() -> APIRouter:
    root = APIRouter()
    root.include_router(health.router)
    v1 = APIRouter(prefix="/v1")
    v1.include_router(search.router)
    v1.include_router(ads.router)
    v1.include_router(users.router)
    root.include_router(v1)
    return root
