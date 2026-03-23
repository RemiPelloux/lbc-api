from __future__ import annotations

from typing import Any, cast

from app.schemas.requests import CityLocation
from app.schemas.responses import SearchResponse
from app.sdk.client import Client
from app.sdk.model.city import City
from app.sdk.model.enums import AdType, Category, Department, OwnerType, Region, Sort
from app.sdk.model.search import Search
from app.services.leboncoin.enum_resolution import parse_enum_member
from app.services.leboncoin.locations import cities_from_request
from app.services.leboncoin.mappers import map_search_to_response

LocationsArg = list[Region | Department | City] | Region | Department | City | None


def execute_search(
    client: Client,
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
) -> Search:
    kwargs: dict[str, Any] = dict(extra_filters)
    loc = cities_from_request(locations)

    if url:
        return client.search(
            url=url,
            page=page,
            limit=limit,
            limit_alu=limit_alu,
        )

    resolved_owner: OwnerType | None = None
    if owner_type:
        resolved_owner = parse_enum_member(OwnerType, owner_type, None)

    return client.search(
        text=text,
        page=page,
        limit=limit,
        limit_alu=limit_alu,
        search_in_title_only=search_in_title_only,
        category=parse_enum_member(Category, category, Category.TOUTES_CATEGORIES),
        sort=parse_enum_member(Sort, sort, Sort.RELEVANCE),
        ad_type=parse_enum_member(AdType, ad_type, AdType.OFFER),
        owner_type=resolved_owner,
        shippable=shippable,
        locations=cast(LocationsArg, loc),
        **kwargs,
    )


def run_search(client: Client, **kwargs: Any) -> SearchResponse:
    result = execute_search(client, **kwargs)
    return map_search_to_response(result, include_users=False)


def run_search_with_users(
    client: Client,
    *,
    prefetch_users_parallel: bool,
    prefetch_max_workers: int,
    **search_kwargs: Any,
) -> SearchResponse:
    result = execute_search(client, **search_kwargs)
    if not result.ads:
        return map_search_to_response(result, include_users=False)

    client.prefetch_users_for_ads(
        result.ads,
        parallel=prefetch_users_parallel,
        max_workers=prefetch_max_workers,
    )
    return map_search_to_response(result, include_users=True)
