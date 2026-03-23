from __future__ import annotations

import pytest
from app.api.v1.common import search_body_to_kwargs
from app.schemas.requests import IntRange, SearchByArgsBody, VehicleFilters
from app.services.leboncoin.vehicle_filters import extra_from_vehicle_filters


def test_extra_from_vehicle_filters_maps_ranges_and_enums() -> None:
    vf = VehicleFilters(
        registration_year=IntRange(min=2015, max=2020),
        mileage_km=IntRange(min=0, max=120_000),
        horsepower=IntRange(min=130, max=200),
        price_eur=IntRange(min=10_000, max=35_000),
        fuels=["diesel"],
        gearboxes=["manuelle"],
        u_car_brands=["renault"],
        u_car_models=["clio"],
        doors=IntRange(min=5, max=5),
        vehicle_seats=IntRange(min=5, max=5),
        vehicle_types=["citadine"],
        first_owner=["1"],
        critair=["1"],
        vehicule_colors=["bleu"],
    )
    extra = extra_from_vehicle_filters(vf)
    assert extra["regdate"] == [2015, 2020]
    assert extra["mileage"] == [0, 120_000]
    assert extra["horsepower"] == [130, 200]
    assert extra["price"] == [10_000, 35_000]
    assert extra["fuel"] == ["diesel"]
    assert extra["gearbox"] == ["manuelle"]
    assert extra["u_car_brand"] == ["renault"]
    assert extra["u_car_model"] == ["clio"]
    assert extra["doors"] == [5, 5]
    assert extra["vehicle_seats"] == [5, 5]
    assert extra["vehicle_type"] == ["citadine"]
    assert extra["first_owner"] == ["1"]
    assert extra["critair"] == ["1"]
    assert extra["vehicule_color"] == ["bleu"]


def test_int_range_rejects_inverted_bounds() -> None:
    with pytest.raises(ValueError):
        IntRange(min=2020, max=2015)


def test_search_body_merges_vehicle_then_extra_filters() -> None:
    body = SearchByArgsBody(
        text="mx5",
        category="VEHICULES_VOITURES",
        vehicle_filters=VehicleFilters(
            registration_year=IntRange(min=2016, max=2022),
        ),
        extra_filters={"horsepower": [150, 200]},
    )
    kwargs = search_body_to_kwargs(body)
    assert kwargs["extra_filters"]["regdate"] == [2016, 2022]
    assert kwargs["extra_filters"]["horsepower"] == [150, 200]


def test_extra_filters_overrides_vehicle_same_key() -> None:
    body = SearchByArgsBody(
        vehicle_filters=VehicleFilters(
            price_eur=IntRange(min=1, max=9),
        ),
        extra_filters={"price": [5000, 50_000]},
    )
    merged = search_body_to_kwargs(body)["extra_filters"]
    assert merged["price"] == [5000, 50_000]
