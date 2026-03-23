from __future__ import annotations

from app.schemas.requests import CityLocation
from app.sdk.model.city import City


def cities_from_request(locations: list[CityLocation] | None) -> list[City] | None:
    if not locations:
        return None
    return [
        City(lat=item.lat, lng=item.lng, radius=item.radius, city=item.city) for item in locations
    ]
