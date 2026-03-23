"""OpenAPI / Swagger UI metadata and shared response schemas."""

from __future__ import annotations

from enum import Enum
from typing import Any

from fastapi.routing import APIRoute
from pydantic import BaseModel, Field

OPENAPI_TAGS: list[dict[str, str]] = [
    {
        "name": "Health",
        "description": "Process liveness for orchestrators and load balancers.",
    },
    {
        "name": "Search",
        "description": (
            "Classified search against Leboncoin finder. "
            "Use `vehicle_filters` for cars; `extra_filters` for any other supported key."
        ),
    },
    {
        "name": "Ads",
        "description": (
            "Fetch one or many ads by id. Batch uses parallel workers with isolated sessions."
        ),
    },
    {
        "name": "Users",
        "description": "Public user-card data for a seller id.",
    },
]


class ErrorResponse(BaseModel):
    """RFC7800-style payload used by FastAPI `HTTPException`."""

    detail: str | list[dict[str, Any]] = Field(
        ...,
        description="Human-readable error or validation detail list",
    )


COMMON_ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    400: {
        "description": "Invalid request (bad enum, malformed filter, etc.)",
        "model": ErrorResponse,
    },
    403: {
        "description": "Remote anti-bot block (Datadome) — slow down or use a clean FR proxy",
        "model": ErrorResponse,
    },
    404: {
        "description": "Ad or user not found",
        "model": ErrorResponse,
    },
    502: {
        "description": "Upstream HTTP error from classifieds API",
        "model": ErrorResponse,
    },
    500: {
        "description": "Unexpected server error",
        "model": ErrorResponse,
    },
}

SWAGGER_UI_PARAMETERS: dict[str, bool | str] = {
    "displayRequestDuration": True,
    "filter": True,
    "tryItOutEnabled": True,
    "persistAuthorization": False,
}


def generate_operation_id(route: APIRoute) -> str:
    """Stable, readable operationIds in OpenAPI (e.g. ``Search-post_search``)."""
    tags = route.tags or []
    raw = tags[0] if tags else None
    if raw is None:
        tag = "api"
    elif isinstance(raw, Enum):
        tag = str(raw.value)
    else:
        tag = str(raw)
    name = route.name or "op"
    safe_tag = "".join(c if c.isalnum() else "_" for c in tag).strip("_") or "api"
    return f"{safe_tag}-{name}"
