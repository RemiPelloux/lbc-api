from __future__ import annotations

from unittest.mock import MagicMock

from app.sdk.model.ad import Ad, AdPictureSet
from app.services.leboncoin.mappers import map_ad_to_response


def _minimal_ad_raw() -> dict:
    return {
        "list_id": 4242,
        "first_publication_date": "2024-06-01 10:00:00",
        "expiration_date": "",
        "index_date": "",
        "status": "active",
        "category_id": "9",
        "category_name": "Ventes immobilières",
        "subject": "Studio test",
        "body": "Description",
        "brand": "",
        "ad_type": "offer",
        "url": "https://www.leboncoin.fr/ad/4242.htm",
        "price_cents": 15000000,
        "has_phone": False,
        "owner": {"user_id": "00000000-0000-0000-0000-000000000001"},
        "location": {
            "country_id": "FR",
            "region_id": "12",
            "region_name": "Île-de-France",
            "department_id": "75",
            "department_name": "Paris",
            "city_label": "Paris",
            "city": "Paris",
            "zipcode": "75001",
            "lat": 48.86,
            "lng": 2.35,
            "source": "city",
            "provider": "here",
            "is_shape": True,
        },
        "attributes": [],
        "images": {
            "urls_thumb": ["https://img.example/thumb.jpg"],
            "urls_small": ["https://img.example/small.jpg"],
            "urls_large": ["https://img.example/large.jpg"],
            "urls": ["https://img.example/full.jpg"],
            "nb_images": 2,
            "thumb_url": "https://img.example/main_thumb.jpg",
            "small_url": "https://img.example/main_small.jpg",
        },
        "options": {"urgent": False, "gallery": True},
        "price_calendar": None,
    }


def test_ad_build_extracts_all_image_tiers_from_raw() -> None:
    client = MagicMock()
    ad = Ad._build(raw=_minimal_ad_raw(), client=client)
    assert ad.images == ["https://img.example/large.jpg"]
    assert ad.pictures.urls_large == ["https://img.example/large.jpg"]
    assert ad.pictures.urls_thumb == ["https://img.example/thumb.jpg"]
    assert ad.pictures.urls_small == ["https://img.example/small.jpg"]
    assert ad.pictures.urls == ["https://img.example/full.jpg"]
    assert ad.pictures.nb_images == 2
    assert ad.pictures.thumb_url == "https://img.example/main_thumb.jpg"
    assert ad.pictures.small_url == "https://img.example/main_small.jpg"


def test_map_ad_to_response_includes_images_and_media() -> None:
    ad = Ad._build(raw=_minimal_ad_raw(), client=MagicMock())
    out = map_ad_to_response(ad, include_user=False)
    assert out.body == "Description"
    assert out.description == out.body
    assert out.images == ["https://img.example/large.jpg"]
    assert out.media.urls_large == ["https://img.example/large.jpg"]
    assert out.media.urls_thumb == ["https://img.example/thumb.jpg"]
    assert out.media.all_urls == [
        "https://img.example/thumb.jpg",
        "https://img.example/small.jpg",
        "https://img.example/large.jpg",
        "https://img.example/full.jpg",
        "https://img.example/main_thumb.jpg",
        "https://img.example/main_small.jpg",
    ]
    assert out.media.nb_images == 2


def test_ad_picture_set_distinct_urls_preserve_order_dedupe() -> None:
    p = AdPictureSet(
        urls_thumb=["https://t1"],
        urls_small=["https://t1", "https://s1"],
        urls_large=["https://s1", "https://L1"],
        urls=["https://L1", "https://u1"],
        nb_images=4,
        thumb_url=None,
        small_url="https://single-small",
    )
    assert p.all_distinct_urls() == [
        "https://t1",
        "https://s1",
        "https://L1",
        "https://u1",
        "https://single-small",
    ]
