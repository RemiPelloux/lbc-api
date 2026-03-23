from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.api.deps import LbcRuntimeDep
from app.api.v1.common import run_sync_lbc
from app.schemas.requests import BatchAdsBody
from app.sdk.client import Client
from app.services.leboncoin.mappers import map_ad_to_response

router = APIRouter()


@router.get("/ads/{ad_id}")
async def get_ad(ad_id: str, runtime: LbcRuntimeDep) -> dict[str, Any]:
    ad = await run_sync_lbc(runtime, Client.get_ad, ad_id)
    return map_ad_to_response(ad, include_user=False).model_dump()


@router.post("/ads/batch")
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
