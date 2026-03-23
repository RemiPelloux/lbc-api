from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.schemas.domain_search import SearchCarsBody, SearchRealEstateBody

router = APIRouter(tags=["Schemas"])


@router.get(
    "/schemas/search-cars",
    summary="JSON Schema: POST /v1/search/cars",
    description=(
        "Schéma JSON complet du corps de requête (propriétés, `$defs`, `examples`). "
        "Référence `VehicleFilters` pour les filtres voiture."
    ),
    response_model=None,
)
def get_search_cars_json_schema() -> dict[str, Any]:
    return SearchCarsBody.model_json_schema(mode="serialization")


@router.get(
    "/schemas/search-real-estate",
    summary="JSON Schema: POST /v1/search/real-estate",
    description="Schéma JSON du corps immobilier (`RealEstateFilters`) avec exemples.",
    response_model=None,
)
def get_search_real_estate_json_schema() -> dict[str, Any]:
    return SearchRealEstateBody.model_json_schema(mode="serialization")
