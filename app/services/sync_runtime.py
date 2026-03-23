from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from app.services.lbc_pool import LbcClientPool

T = TypeVar("T")


class LbcRuntime:
    """Thin facade over ``LbcClientPool`` for dependency injection."""

    def __init__(self, pool: LbcClientPool) -> None:
        self._pool = pool

    async def run(self, func: Callable[..., T], /, *args: Any, **kwargs: Any) -> T:
        return await self._pool.run(func, *args, **kwargs)
