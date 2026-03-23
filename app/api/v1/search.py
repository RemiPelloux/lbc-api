from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import LbcRuntimeDep
from app.api.v1.common import run_sync_lbc, search_body_to_kwargs
from app.core.openapi_config import COMMON_ERROR_RESPONSES
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
