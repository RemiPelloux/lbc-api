from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import LbcRuntimeDep
from app.api.v1.common import run_sync_lbc, search_body_to_kwargs
from app.schemas.requests import SearchByArgsBody, SearchWithUsersBody
from app.schemas.responses import SearchResponse
from app.services.leboncoin.search_service import run_search, run_search_with_users

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def post_search(body: SearchByArgsBody, runtime: LbcRuntimeDep) -> SearchResponse:
    return await run_sync_lbc(runtime, run_search, **search_body_to_kwargs(body))


@router.post("/search/with-users", response_model=SearchResponse)
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
