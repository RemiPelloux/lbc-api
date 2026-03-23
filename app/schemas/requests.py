from __future__ import annotations

from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class IntRange(BaseModel):
    """Inclusive integer range for Leboncoin ``ranges`` filters (min/max)."""

    min: int = Field(..., description="Lower bound (inclusive)")
    max: int = Field(..., description="Upper bound (inclusive)")

    @model_validator(mode="after")
    def min_not_above_max(self) -> Self:
        if self.min > self.max:
            raise ValueError("min must be less than or equal to max")
        return self


class VehicleFilters(BaseModel):
    """
    Common car (voitures) filters. Keys match Leboncoin finder payload names.

    For ``fuels`` / ``gearboxes``, pass the same string ids as in a Leboncoin URL
    (e.g. copy from the site when refining a search). ``extra_filters`` can still
    add any other supported key.
    """

    registration_year: IntRange | None = Field(
        default=None,
        description="First registration year → `regdate`",
    )
    mileage_km: IntRange | None = Field(
        default=None,
        description="Mileage in km → `mileage`",
    )
    horsepower: IntRange | None = Field(
        default=None,
        description="DIN horsepower → finder key `horsepower` (not horse_power)",
    )
    price_eur: IntRange | None = Field(
        default=None,
        description="Price in euros → `price`",
    )
    fuels: list[str] | None = Field(
        default=None,
        description="Fuel enum values (e.g. `diesel`, `essence` — use Leboncoin URL tokens)",
    )
    gearboxes: list[str] | None = Field(
        default=None,
        description="Gearbox enum values (e.g. `manuelle`, `automatique`)",
    )


class CityLocation(BaseModel):
    lat: float
    lng: float
    radius: int = Field(..., description="Radius in meters")
    city: str


class SearchByArgsBody(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "text": "mazda mx5",
                    "category": "VEHICULES_VOITURES",
                    "sort": "NEWEST",
                    "limit": 10,
                    "vehicle_filters": {
                        "price_eur": {"min": 5000, "max": 15000},
                        "mileage_km": {"min": 0, "max": 120000},
                    },
                },
                {
                    "url": "https://www.leboncoin.fr/voitures/offres/",
                    "page": 1,
                    "limit": 35,
                },
            ]
        }
    )

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
    vehicle_filters: VehicleFilters | None = Field(
        default=None,
        description="Car-oriented filters (voitures); merged into the finder payload",
    )
    extra_filters: dict[str, Any] = Field(
        default_factory=dict,
        description="Extra SDK kwargs: int ranges [min,max], enum lists of strings",
    )


class SearchWithUsersBody(SearchByArgsBody):
    prefetch_users_parallel: bool = False
    prefetch_max_workers: int = 4


class BatchAdsBody(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"ids": ["1234567890", "9876543210"], "max_workers": 4}]}
    )

    ids: list[str | int]
    max_workers: int = 4
