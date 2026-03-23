from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from fastapi import HTTPException

from app.api.errors import raise_lbc_as_http
from app.schemas.requests import SearchByArgsBody
from app.sdk.exceptions import LBCError
from app.services.leboncoin.vehicle_filters import extra_from_vehicle_filters
from app.services.sync_runtime import LbcRuntime

T = TypeVar("T")


def search_body_to_kwargs(body: SearchByArgsBody) -> dict[str, Any]:
    merged_extra: dict[str, Any] = {
        **extra_from_vehicle_filters(body.vehicle_filters),
        **body.extra_filters,
    }
    return {
        "text": body.text,
        "url": body.url,
        "page": body.page,
        "limit": body.limit,
        "limit_alu": body.limit_alu,
        "search_in_title_only": body.search_in_title_only,
        "category": body.category,
        "sort": body.sort,
        "ad_type": body.ad_type,
        "owner_type": body.owner_type,
        "shippable": body.shippable,
        "locations": body.locations,
        "extra_filters": merged_extra,
    }


async def run_sync_lbc(
    runtime: LbcRuntime,
    func: Callable[..., T],
    /,
    *args: Any,
    **kwargs: Any,
) -> T:
    try:
        return await runtime.run(func, *args, **kwargs)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except LBCError as exc:
        raise_lbc_as_http(exc)
