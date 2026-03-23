from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CityLocation(BaseModel):
    lat: float
    lng: float
    radius: int = Field(..., description="Radius in meters")
    city: str


class SearchByArgsBody(BaseModel):
    text: str | None = None
    url: str | None = None
    page: int = 1
    limit: int = 35
    limit_alu: int = 3
    search_in_title_only: bool = False
    category: str | None = None
    sort: str | None = None
    ad_type: str | None = None
    owner_type: str | None = None
    shippable: bool | None = None
    locations: list[CityLocation] | None = None
    extra_filters: dict[str, Any] = Field(default_factory=dict)


class SearchWithUsersBody(SearchByArgsBody):
    prefetch_users_parallel: bool = False
    prefetch_max_workers: int = 4


class BatchAdsBody(BaseModel):
    ids: list[str | int]
    max_workers: int = 4
