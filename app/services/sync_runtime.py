from __future__ import annotations

import asyncio
import functools
from collections.abc import Callable
from typing import Any, TypeVar

from app.sdk.client import Client

T = TypeVar("T")


class LbcRuntime:
    """Runs blocking Leboncoin SDK calls in a thread pool behind a single lock."""

    def __init__(self, client: Client, lock: asyncio.Lock) -> None:
        self._client = client
        self._lock = lock

    async def run(self, func: Callable[..., T], /, *args: Any, **kwargs: Any) -> T:
        async with self._lock:
            bound = functools.partial(func, self._client, *args, **kwargs)
            return await asyncio.to_thread(bound)
