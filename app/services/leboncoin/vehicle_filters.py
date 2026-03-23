from __future__ import annotations

from typing import Any

from app.schemas.requests import VehicleFilters


def extra_from_vehicle_filters(filters: VehicleFilters | None) -> dict[str, Any]:
    """
    Convert structured vehicle filters into ``client.search`` keyword arguments.

    The underlying SDK expects:
    - numeric ranges as length-2 ``list``/``tuple`` of ints (min, max);
    - discrete filters as ``list`` of string enum ids (same as Leboncoin search URLs).
    """
    if filters is None:
        return {}

    extra: dict[str, Any] = {}

    if filters.registration_year is not None:
        y = filters.registration_year
        extra["regdate"] = [y.min, y.max]

    if filters.mileage_km is not None:
        m = filters.mileage_km
        extra["mileage"] = [m.min, m.max]

    if filters.horsepower is not None:
        h = filters.horsepower
        extra["horsepower"] = [h.min, h.max]

    if filters.price_eur is not None:
        p = filters.price_eur
        extra["price"] = [p.min, p.max]

    if filters.fuels:
        extra["fuel"] = list(filters.fuels)

    if filters.gearboxes:
        extra["gearbox"] = list(filters.gearboxes)

    if filters.u_car_brands:
        extra["u_car_brand"] = list(filters.u_car_brands)
    if filters.u_car_models:
        extra["u_car_model"] = list(filters.u_car_models)
    if filters.doors is not None:
        d = filters.doors
        extra["doors"] = [d.min, d.max]
    if filters.vehicle_seats is not None:
        s = filters.vehicle_seats
        extra["vehicle_seats"] = [s.min, s.max]
    if filters.vehicle_types:
        extra["vehicle_type"] = list(filters.vehicle_types)
    if filters.first_owner:
        extra["first_owner"] = list(filters.first_owner)
    if filters.critair:
        extra["critair"] = list(filters.critair)
    if filters.vehicule_colors:
        extra["vehicule_color"] = list(filters.vehicule_colors)

    return extra
