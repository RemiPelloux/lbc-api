from __future__ import annotations

import asyncio
from typing import Annotated, cast

from fastapi import Depends, Request

from app.sdk.client import Client
from app.services.sync_runtime import LbcRuntime


def get_lbc_runtime(request: Request) -> LbcRuntime:
    client = cast(Client, request.app.state.lbc_client)
    lock = cast(asyncio.Lock, request.app.state.lbc_lock)
    return LbcRuntime(client, lock)


LbcRuntimeDep = Annotated[LbcRuntime, Depends(get_lbc_runtime)]
