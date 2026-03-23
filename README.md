# LBC API

**Repository:** [github.com/RemiPelloux/lbc-api](https://github.com/RemiPelloux/lbc-api)

REST API for Leboncoin classified search and listings. The **HTTP client lives inside this repo** as `app/sdk/` (no separate vendor tree). The service exposes search, ad, and user endpoints with stable JSON.

**Disclaimer:** Not affiliated with, endorsed by, or supported by Leboncoin. Use responsibly, respect terms of use and rate limits. Remote HTTP 403 (anti-bot) is outside this project’s control.

---

## Features

- **Single installable project** — one `pip install -e ".[dev]"`, no extra package path.
- **Layers** — `app/api` (HTTP), `app/schemas` (DTOs), `app/services` (orchestration), `app/sdk` (low-level client), `app/core` (config + factory).
- **Concurrency** — pool of isolated `Client` sessions (`LBC_API_CLIENT_POOL_SIZE`, default 4); batch helpers still use `Client.fork()` inside the SDK.
- **OpenAPI** — `/docs` (Swagger UI), `/redoc`, `/openapi.json`; JSON is serialized via FastAPI + Pydantic (native bytes path).

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
| `LBC_API_CLIENT_POOL_SIZE` | Parallel upstream sessions (1–32, default `4`) |
| `LBC_API_DOCS_CONTACT_URL` | Optional URL in OpenAPI “Contact” block |

Run:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
# or
lbc-api
```

Interactive docs: `http://localhost:8000/docs` · machine-readable schema: `http://localhost:8000/openapi.json`

---

## HTTP API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness |
| POST | `/v1/search` | Search (any category) |
| POST | `/v1/search/cars` | Search véhicules (default `VEHICULES_VOITURES`, `vehicle_filters` étendu) |
| POST | `/v1/search/real-estate` | Search immobilier (default ventes, `real_estate_filters`) |
| POST | `/v1/search/with-users` | Search + seller prefetch |
| GET | `/v1/schemas/search-cars` | JSON Schema du corps `POST /v1/search/cars` (`$defs` + exemples) |
| GET | `/v1/schemas/search-real-estate` | JSON Schema du corps `POST /v1/search/real-estate` |
| GET | `/v1/ads/{ad_id}` | Single ad |
| POST | `/v1/ads/batch` | Multiple ads (parallel, stable order) |
| GET | `/v1/users/{user_id}` | User card |

### Car filters (`POST /v1/search` or `POST /v1/search/cars`)

Use `vehicle_filters` for common voiture ranges (merged into the Leboncoin payload). `extra_filters` can add any other supported key and **overrides** the same key from `vehicle_filters`.

Example:

```json
{
  "text": "mazda mx5 nd",
  "category": "VEHICULES_VOITURES",
  "sort": "NEWEST",
  "vehicle_filters": {
    "registration_year": { "min": 2015, "max": 2022 },
    "mileage_km": { "min": 0, "max": 120000 },
    "horsepower": { "min": 130, "max": 200 },
    "price_eur": { "min": 15000, "max": 35000 },
    "fuels": ["diesel"],
    "gearboxes": ["manuelle"]
  }
}
```

`fuels` / `gearboxes` values must match Leboncoin’s enum tokens (copy them from a refined search URL on the site if unsure).

Optional extras on `vehicle_filters`: `u_car_brands` / `u_car_models` (finder `u_car_brand`, `u_car_model`), `doors`, `vehicle_seats`, `vehicle_types`, `first_owner`, `critair`, `vehicule_colors`. See **`GET /v1/schemas/search-cars`** for the full JSON Schema and examples.

### Real estate filters (`POST /v1/search/real-estate`)

Use `real_estate_filters` for surface (`square_m2` → `square`), pièces (`rooms`), prix / loyer / charges, DPE (`energy_rates`, `ges_ratings`), type de bien (`real_estate_types` → `real_estate_type`), équipements (`specificities`, `elevator`, `furnished`), etc. `extra_filters` overrides the same finder key. Full field list and examples: **`GET /v1/schemas/search-real-estate`**.

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
