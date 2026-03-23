from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1 import build_v1_router
from app.core.config import get_settings
from app.services.leboncoin.client_factory import build_lbc_client


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    app.state.lbc_client = build_lbc_client(settings.proxy_url)
    app.state.lbc_lock = asyncio.Lock()
    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title="LBC API",
        description=(
            "HTTP API for Leboncoin classifieds using an embedded client SDK (`app.sdk`). "
            "Not affiliated with or endorsed by Leboncoin."
        ),
        version="0.3.0",
        lifespan=_lifespan,
    )
    application.include_router(build_v1_router())
    return application
