from __future__ import annotations

from typing import Any

from app.schemas.domain_search import RealEstateFilters


def extra_from_real_estate_filters(filters: RealEstateFilters | None) -> dict[str, Any]:
    """
    Map structured immobilier filters to ``client.search`` kwargs.

    Finder rules (see ``app.sdk.utils.build_search_payload_with_args``): each kwarg is a
    ``list``/``tuple`` of two ints (range) or of strings (enum tokens copied from Leboncoin).
    """
    if filters is None:
        return {}

    extra: dict[str, Any] = {}

    def add_range(key: str, r: Any) -> None:
        extra[key] = [r.min, r.max]

    if filters.price_eur is not None:
        add_range("price", filters.price_eur)
    if filters.square_m2 is not None:
        add_range("square", filters.square_m2)
    if filters.land_plot_surface_m2 is not None:
        add_range("land_plot_surface", filters.land_plot_surface_m2)
    if filters.rooms is not None:
        add_range("rooms", filters.rooms)
    if filters.bedrooms is not None:
        add_range("bedrooms", filters.bedrooms)
    if filters.nb_parkings is not None:
        add_range("nb_parkings", filters.nb_parkings)
    if filters.nb_shower_rooms is not None:
        add_range("nb_shower_room", filters.nb_shower_rooms)
    if filters.charges_eur is not None:
        add_range("charges", filters.charges_eur)
    if filters.rent_eur is not None:
        add_range("rent", filters.rent_eur)
    if filters.building_year is not None:
        add_range("building_year", filters.building_year)
    if filters.fees_at_buyer_expense_eur is not None:
        add_range("fees_at_buyer_expense", filters.fees_at_buyer_expense_eur)

    if filters.real_estate_types:
        extra["real_estate_type"] = list(filters.real_estate_types)
    if filters.energy_rates:
        extra["energy_rate"] = list(filters.energy_rates)
    if filters.ges_ratings:
        extra["ges"] = list(filters.ges_ratings)
    if filters.floor_numbers:
        extra["floor_number"] = list(filters.floor_numbers)
    if filters.furnished:
        extra["furnished"] = list(filters.furnished)
    if filters.elevator:
        extra["elevator"] = list(filters.elevator)
    if filters.specificities:
        extra["specificities"] = list(filters.specificities)
    if filters.immo_sell_types:
        extra["immo_sell_type"] = list(filters.immo_sell_types)
    if filters.lease_types:
        extra["lease_type"] = list(filters.lease_types)
    if filters.mandate_types:
        extra["mandate_type"] = list(filters.mandate_types)
    if filters.heating_types:
        extra["heating_type"] = list(filters.heating_types)
    if filters.outside_access_types:
        extra["outside_access"] = list(filters.outside_access_types)
    if filters.global_conditions:
        extra["global_condition"] = list(filters.global_conditions)
    if filters.activity_sectors:
        extra["activity_sector"] = list(filters.activity_sectors)
    if filters.orientation:
        extra["orientation"] = list(filters.orientation)
    if filters.seller_types:
        extra["seller_type"] = list(filters.seller_types)
    if filters.custom_refunds:
        extra["custom_refund"] = list(filters.custom_refunds)
    if filters.proximities:
        extra["proximity"] = list(filters.proximities)
    if filters.land_types:
        extra["land_type"] = list(filters.land_types)
    if filters.fees_charged_to:
        extra["fees_charged_to"] = list(filters.fees_charged_to)
    if filters.is_import:
        extra["is_import"] = list(filters.is_import)

    return extra
