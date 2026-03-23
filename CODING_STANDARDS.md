# Coding standards

## Tooling

- Python 3.11+
- Ruff (lint + format), mypy strict on `app/` (embedded `app.sdk` modules are excluded from strict checks via `pyproject.toml` overrides)

## Layering

| Layer | Role |
|--------|------|
| `app/api/` | Routes, FastAPI dependencies, HTTP ↔ exception mapping |
| `app/schemas/` | Request/response DTOs |
| `app/services/` | Orchestration using `app.sdk` |
| `app/sdk/` | Low-level Leboncoin HTTP client (no FastAPI imports) |
| `app/core/` | Settings, `create_app()` |

## Concurrency

- Shared `Client` session is not thread-safe: the app uses a lock + `asyncio.to_thread`.
- Parallel batch paths in the SDK use `Client.fork()`.

## Tests

No network in default unit tests; stub session init in `tests/conftest.py`.

## Legal

State clearly that the service is not affiliated with Leboncoin. See `NOTICE` for SDK attribution.
