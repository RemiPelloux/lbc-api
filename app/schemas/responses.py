from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, computed_field


class ApiModel(BaseModel):
    """Output DTOs: skip re-validation on ``model_validate`` for faster serialization paths."""

    model_config = ConfigDict(revalidate_instances="never")


class UserOut(ApiModel):
    id: str
    name: str
    account_type: str
    location: str | None = None


class AdLocationOut(ApiModel):
    country_id: str | None = None
    region_id: str | None = None
    region_name: str | None = None
    department_id: str | None = None
    department_name: str | None = None
    city_label: str | None = None
    city: str | None = None
    zipcode: str | None = None
    lat: float | None = None
    lng: float | None = None
    source: str | None = None
    provider: str | None = None
    is_shape: bool | None = None


class AdAttributeOut(ApiModel):
    model_config = ConfigDict(extra="allow", revalidate_instances="never")

    key: str | None = None
    key_label: str | None = None
    value: str | None = None
    value_label: str | None = None
    values: list[str] = Field(default_factory=list)
    values_label: list[str] | None = None
    value_label_reader: str | None = None
    generic: bool | None = None


class AdMediaOut(ApiModel):
    """Every image URL tier from Leboncoin, plus a single deduped list."""

    urls_thumb: list[str] = Field(default_factory=list)
    urls_small: list[str] = Field(default_factory=list)
    urls_large: list[str] = Field(default_factory=list)
    urls: list[str] = Field(
        default_factory=list,
        description="Generic `images.urls` gallery when present",
    )
    nb_images: int | None = None
    thumb_url: str | None = Field(default=None, description="Single main thumb when present")
    small_url: str | None = Field(default=None, description="Single main small when present")
    all_urls: list[str] = Field(
        default_factory=list,
        description="All distinct image URLs (thumb/small/large/gallery/singletons merged)",
    )


class AdOut(ApiModel):
    model_config = ConfigDict(extra="allow", revalidate_instances="never")

    id: int | None
    subject: str
    url: str
    #: Same as ``media.urls_large`` (large photos)
    images: list[str] = Field(default_factory=list)
    media: AdMediaOut
    price: float | None
    price_cents: int | None = None
    price_calendar: Any = None
    category_id: str | None = None
    category_name: str | None = None
    brand: str | None = None
    ad_type: str | None = None
    #: Full listing text from upstream ``body`` (Leboncoin description)
    body: str

    first_publication_date: str | None = None
    expiration_date: str | None = None
    index_date: str | None = None
    status: str | None = None
    has_phone: bool | None = None
    favorites: int | None = None
    location: AdLocationOut
    attributes: list[AdAttributeOut] = Field(default_factory=list)
    options: dict[str, Any] | None = None
    owner_user_id: str | None = None
    user: UserOut | None = None

    @computed_field
    def description(self) -> str:
        """Alias of ``body`` (no duplicate storage)."""
        return self.body


class SearchMeta(ApiModel):
    total: int | None
    max_pages: int | None


class SearchResponse(ApiModel):
    meta: SearchMeta
    ads: list[AdOut]
