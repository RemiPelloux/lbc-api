from __future__ import annotations

from app.api.v1.common import cars_body_to_kwargs, real_estate_body_to_kwargs
from app.schemas.domain_search import RealEstateFilters, SearchCarsBody, SearchRealEstateBody
from app.schemas.requests import IntRange
from app.services.leboncoin.real_estate_filters import extra_from_real_estate_filters


def test_extra_from_real_estate_filters_ranges_and_enums() -> None:
    rf = RealEstateFilters(
        price_eur=IntRange(min=200_000, max=400_000),
        square_m2=IntRange(min=40, max=90),
        rooms=IntRange(min=2, max=4),
        bedrooms=IntRange(min=1, max=3),
        real_estate_types=["1", "2"],
        energy_rates=["a", "b"],
        ges_ratings=["a"],
        nb_parkings=IntRange(min=0, max=2),
        nb_shower_rooms=IntRange(min=1, max=2),
        rent_eur=IntRange(min=500, max=1200),
        charges_eur=IntRange(min=50, max=250),
        building_year=IntRange(min=1990, max=2020),
        fees_at_buyer_expense_eur=IntRange(min=0, max=10_000),
        immo_sell_types=["old"],
        lease_types=["sell"],
        elevator=["1"],
        furnished=["0"],
    )
    extra = extra_from_real_estate_filters(rf)
    assert extra["price"] == [200_000, 400_000]
    assert extra["square"] == [40, 90]
    assert extra["rooms"] == [2, 4]
    assert extra["bedrooms"] == [1, 3]
    assert extra["real_estate_type"] == ["1", "2"]
    assert extra["energy_rate"] == ["a", "b"]
    assert extra["ges"] == ["a"]
    assert extra["nb_parkings"] == [0, 2]
    assert extra["nb_shower_room"] == [1, 2]
    assert extra["rent"] == [500, 1200]
    assert extra["charges"] == [50, 250]
    assert extra["building_year"] == [1990, 2020]
    assert extra["fees_at_buyer_expense"] == [0, 10_000]
    assert extra["immo_sell_type"] == ["old"]
    assert extra["lease_type"] == ["sell"]
    assert extra["elevator"] == ["1"]
    assert extra["furnished"] == ["0"]


def test_real_estate_body_default_category_and_merge() -> None:
    body = SearchRealEstateBody(
        text="studio",
        real_estate_filters=RealEstateFilters(square_m2=IntRange(min=20, max=35)),
        extra_filters={"price": [100_000, 200_000]},
    )
    kwargs = real_estate_body_to_kwargs(body)
    assert kwargs["category"] == "IMMOBILIER_VENTES_IMMOBILIERES"
    assert kwargs["extra_filters"]["square"] == [20, 35]
    assert kwargs["extra_filters"]["price"] == [100_000, 200_000]


def test_cars_body_default_category() -> None:
    body = SearchCarsBody(text="clio")
    assert cars_body_to_kwargs(body)["category"] == "VEHICULES_VOITURES"
