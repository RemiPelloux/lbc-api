from __future__ import annotations

import asyncio
import functools
from collections.abc import Callable
from typing import Any, TypeVar

from app.sdk.client import Client

T = TypeVar("T")


class LbcClientPool:
    """
    Bounded pool of isolated ``Client`` instances (each with its own HTTP session).

    Replaces a single global lock: up to ``pool_size`` finder calls can run concurrently
    on distinct sessions. Still respect remote rate limits (Datadome).
    """

    def __init__(self, clients: list[Client]) -> None:
        if not clients:
            raise ValueError("client pool requires at least one Client")
        self._pool_size = len(clients)
        self._queue: asyncio.Queue[Client] = asyncio.Queue()
        for client in clients:
            self._queue.put_nowait(client)

    @property
    def pool_size(self) -> int:
        return self._pool_size

    async def run(self, func: Callable[..., T], /, *args: Any, **kwargs: Any) -> T:
        client = await self._queue.get()
        try:
            bound = functools.partial(func, client, *args, **kwargs)
            return await asyncio.to_thread(bound)
        finally:
            self._queue.put_nowait(client)
