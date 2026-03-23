from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from fastapi import HTTPException

from app.api.errors import raise_lbc_as_http
from app.schemas.domain_search import SearchCarsBody, SearchRealEstateBody
from app.schemas.requests import CityLocation, SearchByArgsBody
from app.sdk.exceptions import LBCError
from app.services.leboncoin.real_estate_filters import extra_from_real_estate_filters
from app.services.leboncoin.vehicle_filters import extra_from_vehicle_filters
from app.services.sync_runtime import LbcRuntime

T = TypeVar("T")


def _search_core_kwargs(
    *,
    text: str | None,
    url: str | None,
    page: int,
    limit: int,
    limit_alu: int,
    search_in_title_only: bool,
    category: str | None,
    sort: str | None,
    ad_type: str | None,
    owner_type: str | None,
    shippable: bool | None,
    locations: list[CityLocation] | None,
    extra_filters: dict[str, Any],
) -> dict[str, Any]:
    return {
        "text": text,
        "url": url,
        "page": page,
        "limit": limit,
        "limit_alu": limit_alu,
        "search_in_title_only": search_in_title_only,
        "category": category,
        "sort": sort,
        "ad_type": ad_type,
        "owner_type": owner_type,
        "shippable": shippable,
        "locations": locations,
        "extra_filters": extra_filters,
    }


def search_body_to_kwargs(body: SearchByArgsBody) -> dict[str, Any]:
    merged_extra: dict[str, Any] = {
        **extra_from_vehicle_filters(body.vehicle_filters),
        **body.extra_filters,
    }
    return _search_core_kwargs(
        text=body.text,
        url=body.url,
        page=body.page,
        limit=body.limit,
        limit_alu=body.limit_alu,
        search_in_title_only=body.search_in_title_only,
        category=body.category,
        sort=body.sort,
        ad_type=body.ad_type,
        owner_type=body.owner_type,
        shippable=body.shippable,
        locations=body.locations,
        extra_filters=merged_extra,
    )


def cars_body_to_kwargs(body: SearchCarsBody) -> dict[str, Any]:
    category = body.category or "VEHICULES_VOITURES"
    merged_extra = {
        **extra_from_vehicle_filters(body.vehicle_filters),
        **body.extra_filters,
    }
    return _search_core_kwargs(
        text=body.text,
        url=body.url,
        page=body.page,
        limit=body.limit,
        limit_alu=body.limit_alu,
        search_in_title_only=body.search_in_title_only,
        category=category,
        sort=body.sort,
        ad_type=body.ad_type,
        owner_type=body.owner_type,
        shippable=body.shippable,
        locations=body.locations,
        extra_filters=merged_extra,
    )


def real_estate_body_to_kwargs(body: SearchRealEstateBody) -> dict[str, Any]:
    category = body.category or "IMMOBILIER_VENTES_IMMOBILIERES"
    merged_extra = {
        **extra_from_real_estate_filters(body.real_estate_filters),
        **body.extra_filters,
    }
    return _search_core_kwargs(
        text=body.text,
        url=body.url,
        page=body.page,
        limit=body.limit,
        limit_alu=body.limit_alu,
        search_in_title_only=body.search_in_title_only,
        category=category,
        sort=body.sort,
        ad_type=body.ad_type,
        owner_type=body.owner_type,
        shippable=body.shippable,
        locations=body.locations,
        extra_filters=merged_extra,
    )


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
