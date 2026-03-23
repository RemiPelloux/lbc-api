from __future__ import annotations

from typing import NoReturn

from fastapi import HTTPException

from app.sdk.exceptions import DatadomeError, LBCError, NotFoundError, RequestError


def raise_lbc_as_http(exc: LBCError) -> NoReturn:
    if isinstance(exc, NotFoundError):
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if isinstance(exc, DatadomeError):
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    if isinstance(exc, RequestError):
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    raise HTTPException(status_code=500, detail=str(exc)) from exc
