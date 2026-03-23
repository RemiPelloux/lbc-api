from dataclasses import dataclass
from typing import Any

from .user import User


@dataclass
class Location:
    country_id: str
    region_id: str
    region_name: str
    department_id: str
    department_name: str
    city_label: str
    city: str
    zipcode: str
    lat: float
    lng: float
    source: str
    provider: str
    is_shape: bool


@dataclass
class Attribute:
    key: str
    key_label: str | None
    value: str
    value_label: str
    values: list[str]
    values_label: list[str] | None
    value_label_reader: str | None
    generic: bool


def _str_list(v: Any) -> list[str]:
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x) for x in v if x is not None and str(x) != ""]
    return [str(v)]


_GARBAGE_ROOT_BRANDS = frozenset({"", "leboncoin"})


def _normalize_brand(raw_brand: Any, attributes: list[Attribute]) -> str:
    """Finder sometimes puts ``leboncoin`` at root; prefer human ``brand`` / ``u_car_brand`` attrs."""
    b = raw_brand.strip() if isinstance(raw_brand, str) else ""
    if b and b.lower() not in _GARBAGE_ROOT_BRANDS:
        return b
    for attr in attributes:
        if attr.key == "brand" and attr.value_label:
            label = str(attr.value_label).strip()
            if label:
                return label
    for attr in attributes:
        if attr.key == "u_car_brand" and attr.value_label:
            label = str(attr.value_label).strip()
            if label:
                return label
    return b


@dataclass
class AdPictureSet:
    """All image URL collections returned by finder / classified APIs."""

    urls_thumb: list[str]
    urls_small: list[str]
    urls_large: list[str]
    urls: list[str]
    nb_images: int | None
    thumb_url: str | None
    small_url: str | None

    def all_distinct_urls(self) -> list[str]:
        chunks: list[str] = []
        for seq in (self.urls_thumb, self.urls_small, self.urls_large, self.urls):
            chunks.extend(seq)
        for single in (self.thumb_url, self.small_url):
            if single:
                chunks.append(single)
        return list(dict.fromkeys(chunks))


@dataclass
class Ad:
    id: int
    first_publication_date: str
    expiration_date: str
    index_date: str
    status: str
    category_id: str
    category_name: str
    subject: str
    body: str
    brand: str
    ad_type: str
    url: str
    price: float
    #: Large gallery URLs (same as ``pictures.urls_large``)
    images: list[str]
    pictures: AdPictureSet
    attributes: list[Attribute]
    location: Location
    has_phone: bool
    favorites: int  # Unvailaible on Ad from Search
    options: dict[str, Any] | None
    price_cents: int | None
    price_calendar: Any

    _client: Any
    _user_id: str
    _user: User

    @staticmethod
    def _build(raw: dict, client: Any) -> "Ad":
        attributes: list[Attribute] = []
        for raw_attribute in raw.get("attributes", []):
            attributes.append(
                Attribute(
                    key=raw_attribute.get("key"),
                    key_label=raw_attribute.get("key_label"),
                    value=raw_attribute.get("value"),
                    value_label=raw_attribute.get("value_label"),
                    values=raw_attribute.get("values") or [],
                    values_label=raw_attribute.get("values_label"),
                    value_label_reader=raw_attribute.get("value_label_reader"),
                    generic=raw_attribute.get("generic"),
                )
            )

        raw_location: dict = raw.get("location", {})
        location = Location(
            country_id=raw_location.get("country_id"),
            region_id=raw_location.get("region_id"),
            region_name=raw_location.get("region_name"),
            department_id=raw_location.get("department_id"),
            department_name=raw_location.get("department_name"),
            city_label=raw_location.get("city_label"),
            city=raw_location.get("city"),
            zipcode=raw_location.get("zipcode"),
            lat=raw_location.get("lat"),
            lng=raw_location.get("lng"),
            source=raw_location.get("source"),
            provider=raw_location.get("provider"),
            is_shape=raw_location.get("is_shape"),
        )

        raw_img = raw.get("images") or {}
        tu = raw_img.get("thumb_url")
        su = raw_img.get("small_url")
        pictures = AdPictureSet(
            urls_thumb=_str_list(raw_img.get("urls_thumb")),
            urls_small=_str_list(raw_img.get("urls_small")),
            urls_large=_str_list(raw_img.get("urls_large")),
            urls=_str_list(raw_img.get("urls")),
            nb_images=raw_img.get("nb_images"),
            thumb_url=tu if isinstance(tu, str) else None,
            small_url=su if isinstance(su, str) else None,
        )
        large_only = pictures.urls_large

        raw_owner: dict = raw.get("owner", {})
        brand = _normalize_brand(raw.get("brand"), attributes)
        return Ad(
            id=raw.get("list_id"),
            first_publication_date=raw.get("first_publication_date"),
            expiration_date=raw.get("expiration_date"),
            index_date=raw.get("index_date"),
            status=raw.get("status"),
            category_id=raw.get("category_id"),
            category_name=raw.get("category_name"),
            subject=raw.get("subject"),
            body=raw.get("body"),
            brand=brand,
            ad_type=raw.get("ad_type"),
            url=raw.get("url"),
            price=raw.get("price_cents") / 100 if raw.get("price_cents") else None,
            images=large_only,
            pictures=pictures,
            attributes=attributes,
            location=location,
            has_phone=raw.get("has_phone"),
            favorites=raw.get("counters", {}).get("favorites"),
            options=raw.get("options"),
            price_cents=raw.get("price_cents"),
            price_calendar=raw.get("price_calendar"),
            _client=client,
            _user_id=raw_owner.get("user_id"),
            _user=None,
        )

    @property
    def title(self) -> str:
        return self.subject

    @property
    def user(self) -> User:
        if self._user is None:
            self._user = self._client.get_user(user_id=self._user_id)
        return self._user
