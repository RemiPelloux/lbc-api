# LBC API

**Repository:** [github.com/RemiPelloux/lbc-api](https://github.com/RemiPelloux/lbc-api)

REST API for Leboncoin classified search and listings. The **HTTP client lives inside this repo** as `app/sdk/` (no separate vendor tree). The service exposes search, ad, and user endpoints with stable JSON.

**Disclaimer:** Not affiliated with, endorsed by, or supported by Leboncoin. Use responsibly, respect terms of use and rate limits. Remote HTTP 403 (anti-bot) is outside this project’s control.

---

## Features

- **Single installable project** — one `pip install -e ".[dev]"`, no extra package path.
- **Layers** — `app/api` (HTTP), `app/schemas` (DTOs), `app/services` (orchestration), `app/sdk` (low-level client), `app/core` (config + factory).
- **Concurrency** — serialized calls on a shared session; batch helpers use `Client.fork()`.

---

## Requirements

- Python **3.11+**

---

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Environment (prefix `LBC_API_`):

| Variable | Purpose |
|----------|---------|
| `LBC_API_HOST` | Bind address (default `0.0.0.0`) |
| `LBC_API_PORT` | Port (default `8000`) |
| `LBC_API_PROXY_URL` | HTTP(S) proxy, e.g. `http://user:pass@host:3128` |

Run:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
# or
lbc-api
```

Docs: `http://localhost:8000/docs`

---

## HTTP API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness |
| POST | `/v1/search` | Search |
| POST | `/v1/search/with-users` | Search + seller prefetch |
| GET | `/v1/ads/{ad_id}` | Single ad |
| POST | `/v1/ads/batch` | Multiple ads (parallel, stable order) |
| GET | `/v1/users/{user_id}` | User card |

---

## Layout

```
app/
  api/        # Routers, deps, HTTP errors
  core/       # Settings, create_app()
  schemas/    # Pydantic models
  services/   # Runtime + Leboncoin integration
  sdk/        # Embedded HTTP client (see NOTICE)
  main.py
tests/
```

---

## Quality

```bash
ruff check app tests && ruff format app tests
mypy app
pytest
```

---

## Clone

```bash
git clone https://github.com/RemiPelloux/lbc-api.git
cd lbc-api
```

---

## License

This project is released under the **MIT License** (`LICENSE`, Copyright Remi Pelloux). The embedded client under `app/sdk/` includes MIT-licensed third-party portions; see `NOTICE`.
