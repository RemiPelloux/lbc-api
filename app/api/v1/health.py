from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Liveness", include_in_schema=True)
async def health() -> dict[str, str]:
    return {"status": "ok"}
