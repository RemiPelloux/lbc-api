from __future__ import annotations

import uvicorn

from app.core.config import get_settings
from app.core.factory import create_app

app = create_app()


def run() -> None:
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        factory=False,
    )


if __name__ == "__main__":
    run()
