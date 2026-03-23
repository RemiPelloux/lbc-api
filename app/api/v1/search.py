from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import LbcRuntimeDep
from app.api.v1.common import (
    cars_body_to_kwargs,
    real_estate_body_to_kwargs,
    run_sync_lbc,
    search_body_to_kwargs,
)
from app.core.openapi_config import COMMON_ERROR_RESPONSES
from app.schemas.domain_search import SearchCarsBody, SearchRealEstateBody
from app.schemas.requests import SearchByArgsBody, SearchWithUsersBody
from app.schemas.responses import SearchResponse
from app.services.leboncoin.search_service import run_search, run_search_with_users

router = APIRouter(tags=["Search"], responses=COMMON_ERROR_RESPONSES)


@router.post(
    "/search",
    response_model=SearchResponse,
    summary="Search classifieds",
    description="Finder search by text, URL, category, sort, geo, and optional car filters.",
)
async def post_search(body: SearchByArgsBody, runtime: LbcRuntimeDep) -> SearchResponse:
    return await run_sync_lbc(runtime, run_search, **search_body_to_kwargs(body))


@router.post(
    "/search/with-users",
    response_model=SearchResponse,
    summary="Search with seller prefetch",
    description=(
        "Same as `/search` but can prefetch user cards for listed ads (extra upstream calls)."
    ),
)
async def post_search_with_users(
    body: SearchWithUsersBody,
    runtime: LbcRuntimeDep,
) -> SearchResponse:
    kwargs = search_body_to_kwargs(body)
    return await run_sync_lbc(
        runtime,
        run_search_with_users,
        prefetch_users_parallel=body.prefetch_users_parallel,
        prefetch_max_workers=body.prefetch_max_workers,
        **kwargs,
    )


@router.post(
    "/search/cars",
    response_model=SearchResponse,
    summary="Search cars & vehicles",
    description=(
        "Même moteur que `POST /v1/search` avec catégorie par défaut **VEHICULES_VOITURES** "
        "et schéma `vehicle_filters` étendu (marque, modèle, places, Crit'Air, …). "
        "Schéma JSON: `GET /v1/schemas/search-cars`."
    ),
)
async def post_search_cars(body: SearchCarsBody, runtime: LbcRuntimeDep) -> SearchResponse:
    return await run_sync_lbc(runtime, run_search, **cars_body_to_kwargs(body))


@router.post(
    "/search/real-estate",
    response_model=SearchResponse,
    summary="Search real estate",
    description=(
        "Catégorie par défaut **IMMOBILIER_VENTES_IMMOBILIERES**; "
        "filtres surface, pièces, DPE, loyer, etc. via `real_estate_filters`. "
        "Schéma JSON: `GET /v1/schemas/search-real-estate`."
    ),
)
async def post_search_real_estate(
    body: SearchRealEstateBody,
    runtime: LbcRuntimeDep,
) -> SearchResponse:
    return await run_sync_lbc(runtime, run_search, **real_estate_body_to_kwargs(body))
