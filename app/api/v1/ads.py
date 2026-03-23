from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.api.deps import LbcRuntimeDep
from app.api.v1.common import run_sync_lbc
from app.core.openapi_config import COMMON_ERROR_RESPONSES
from app.schemas.requests import BatchAdsBody
from app.sdk.client import Client
from app.services.leboncoin.mappers import map_ad_to_response

router = APIRouter(tags=["Ads"], responses=COMMON_ERROR_RESPONSES)


@router.get(
    "/ads/{ad_id}",
    summary="Get one ad",
    description="Single ad payload mapped to a stable JSON shape (no embedded user).",
)
async def get_ad(ad_id: str, runtime: LbcRuntimeDep) -> dict[str, Any]:
    ad = await run_sync_lbc(runtime, Client.get_ad, ad_id)
    return map_ad_to_response(ad, include_user=False).model_dump()


@router.post(
    "/ads/batch",
    summary="Batch ads by id",
    description="Parallel fetch inside the SDK; respects `max_workers` per request.",
)
async def post_ads_batch(body: BatchAdsBody, runtime: LbcRuntimeDep) -> list[dict[str, Any]]:
    if not body.ids:
        return []
    ads = await run_sync_lbc(
        runtime,
        Client.get_ads_parallel,
        body.ids,
        max_workers=body.max_workers,
    )
    return [map_ad_to_response(a, include_user=False).model_dump() for a in ads]
