from __future__ import annotations

from typing import Annotated, cast

from fastapi import Depends, Request

from app.services.lbc_pool import LbcClientPool
from app.services.sync_runtime import LbcRuntime


def get_lbc_runtime(request: Request) -> LbcRuntime:
    pool = cast(LbcClientPool, request.app.state.lbc_pool)
    return LbcRuntime(pool)


LbcRuntimeDep = Annotated[LbcRuntime, Depends(get_lbc_runtime)]
