from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.api.deps import LbcRuntimeDep
from app.api.v1.common import run_sync_lbc
from app.sdk.client import Client
from app.services.leboncoin.mappers import map_user_to_response

router = APIRouter()


@router.get("/users/{user_id}")
async def get_user(user_id: str, runtime: LbcRuntimeDep) -> dict[str, Any]:
    user = await run_sync_lbc(runtime, Client.get_user, user_id)
    return map_user_to_response(user).model_dump()
