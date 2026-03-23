from __future__ import annotations

from typing import Any

from app.schemas.responses import (
    AdAttributeOut,
    AdLocationOut,
    AdMediaOut,
    AdOut,
    SearchMeta,
    SearchResponse,
    UserOut,
)
from app.sdk.model.ad import Ad, Attribute, Location
from app.sdk.model.search import Search
from app.sdk.model.user import User


def map_user_to_response(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        name=user.name,
        account_type=user.account_type,
        location=user.location,
    )


def _map_location(loc: Location) -> AdLocationOut:
    return AdLocationOut(
        country_id=loc.country_id,
        region_id=loc.region_id,
        region_name=loc.region_name,
        department_id=loc.department_id,
        department_name=loc.department_name,
        city_label=loc.city_label,
        city=loc.city,
        zipcode=loc.zipcode,
        lat=loc.lat,
        lng=loc.lng,
        source=loc.source,
        provider=loc.provider,
        is_shape=loc.is_shape,
    )


def _map_attribute(attr: Attribute) -> AdAttributeOut:
    vals = attr.values if isinstance(attr.values, list) else []
    str_vals = [v for v in vals if isinstance(v, str)]
    return AdAttributeOut(
        key=attr.key,
        key_label=attr.key_label,
        value=attr.value,
        value_label=attr.value_label,
        values=str_vals,
        values_label=attr.values_label,
        value_label_reader=attr.value_label_reader,
        generic=attr.generic,
    )


def _map_media(ad: Ad) -> AdMediaOut:
    p = ad.pictures
    all_urls = p.all_distinct_urls()
    return AdMediaOut(
        urls_thumb=p.urls_thumb,
        urls_small=p.urls_small,
        urls_large=p.urls_large,
        urls=p.urls,
        nb_images=p.nb_images,
        thumb_url=p.thumb_url,
        small_url=p.small_url,
        all_urls=all_urls,
    )


def _coerce_options(raw: dict[str, Any] | None) -> dict[str, Any] | None:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        return None
    return dict(raw)


def map_ad_to_response(ad: Ad, *, include_user: bool) -> AdOut:
    user_out: UserOut | None = None
    if include_user and ad._user is not None:
        user_out = map_user_to_response(ad._user)

    raw_images = ad.images or []
    imgs = raw_images if isinstance(raw_images, list) else []
    images_large = [u for u in imgs if isinstance(u, str)]

    text_body = ad.body or ""
    return AdOut(
        id=ad.id,
        subject=ad.subject or "",
        url=ad.url or "",
        images=images_large,
        media=_map_media(ad),
        price=ad.price,
        price_cents=ad.price_cents,
        price_calendar=ad.price_calendar,
        category_id=ad.category_id,
        category_name=ad.category_name,
        brand=ad.brand,
        ad_type=ad.ad_type,
        body=text_body,
        description=text_body,
        first_publication_date=ad.first_publication_date,
        expiration_date=ad.expiration_date,
        index_date=ad.index_date,
        status=ad.status,
        has_phone=ad.has_phone,
        favorites=ad.favorites,
        location=_map_location(ad.location),
        attributes=[_map_attribute(a) for a in ad.attributes],
        options=_coerce_options(ad.options),
        owner_user_id=ad._user_id,
        user=user_out,
    )


def map_search_to_response(result: Search, *, include_users: bool) -> SearchResponse:
    meta = SearchMeta(total=result.total, max_pages=result.max_pages)
    ads = [map_ad_to_response(ad, include_user=include_users) for ad in result.ads]
    return SearchResponse(meta=meta, ads=ads)
