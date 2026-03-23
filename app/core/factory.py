from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1 import build_v1_router
from app.core.config import get_settings
from app.core.openapi_config import (
    OPENAPI_TAGS,
    SWAGGER_UI_PARAMETERS,
    generate_operation_id,
)
from app.services.lbc_pool import LbcClientPool
from app.services.leboncoin.client_factory import build_lbc_client


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    n = max(1, min(settings.client_pool_size, 32))
    clients = [build_lbc_client(settings.proxy_url) for _ in range(n)]
    app.state.lbc_pool = LbcClientPool(clients)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    contact = None
    if settings.docs_contact_url:
        contact = {"name": "API support", "url": str(settings.docs_contact_url)}

    application = FastAPI(
        title="LBC API",
        description=(
            "**Leboncoin classifieds** as JSON: search, ads, sellers.\n\n"
            "- **Not** affiliated with Leboncoin.\n"
            "- Remote **403** = anti-bot; reduce concurrency or use a clean FR proxy.\n"
            "- `client_pool_size` (env `LBC_API_CLIENT_POOL_SIZE`) "
            "controls parallel upstream sessions.\n"
        ),
        version="0.4.0",
        lifespan=_lifespan,
        openapi_tags=OPENAPI_TAGS,
        swagger_ui_parameters=SWAGGER_UI_PARAMETERS,
        generate_unique_id_function=generate_operation_id,
        contact=contact,
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        responses={
            "4XX": {"description": "Client or upstream policy error"},
            "5XX": {"description": "Server error"},
        },
    )
    application.include_router(build_v1_router())
    return application
