from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.api.deps import LbcRuntimeDep
from app.api.v1.common import run_sync_lbc
from app.core.openapi_config import COMMON_ERROR_RESPONSES
from app.sdk.client import Client
from app.services.leboncoin.mappers import map_user_to_response

router = APIRouter(tags=["Users"], responses=COMMON_ERROR_RESPONSES)


@router.get(
    "/users/{user_id}",
    summary="Get public user card",
    description="Seller profile fields exposed by the upstream API.",
)
async def get_user(user_id: str, runtime: LbcRuntimeDep) -> dict[str, Any]:
    user = await run_sync_lbc(runtime, Client.get_user, user_id)
    return map_user_to_response(user).model_dump()
