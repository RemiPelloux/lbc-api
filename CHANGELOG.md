# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.1] - 2026-03-23

### Added

- **Docker**: `Dockerfile` (Python 3.12 slim Bookworm) and `compose.yaml` for `docker compose up --build`.
- **Docker test cycle**: `Dockerfile.test`, `lbc-test` service (compose profile `test`), healthcheck on `lbc-api`, script `scripts/docker_up_test_down.sh`.
- **Docker HTTP e2e**: `tests/test_api_e2e_http.py`, `lbc-e2e` (profile `e2e`), script `scripts/docker_api_e2e.sh` — pytest hits the live API in Docker (`httpx` → `/health`, OpenAPI, real searches).

### Changed

- **`Client.fork()`**: new sessions clone the parent’s headers, cookies, and TLS impersonation profile instead of performing another `www.leboncoin.fr` warmup GET—removes N+1 homepage requests when prefetching users or batch-fetching ads in parallel.
- **Performance / DTOs**: response models use `revalidate_instances="never"`; `description` is a `@computed_field` alias of `body` (no duplicate string field).
- **`AdPictureSet.all_distinct_urls`**: ordered dedupe via `dict.fromkeys` (single pass).
- **Brand**: root `brand` values like `leboncoin` are replaced by the `brand` / `u_car_brand` attribute when present.
- **Mapper**: leaner image list handling; `_coerce_options` branch folded.

### Added

- Test `test_brand_fallback_when_root_is_leboncoin`.
- Test `test_fork_skips_second_homepage_warmup`.
- Live integration test (PS5, iPhone, Mazda MX-5, maison ~60 m² near Saint-Laurent-du-Var) lives in `tests/test_real_leboncoin_optional.py`; default `pytest` ignores that file via `addopts` (run it explicitly for real HTTP).
- `app/services/leboncoin/live_search_scenarios.py` + `scripts/print_live_search_examples.py` share the same four live queries and print one real listing per scenario as JSON.
- Live scenario **job offers Nice** (`EMPLOI_OFFRES_DEMPLOI`, rayon ~12 km) + `scripts/write_nice_job_offers_json.py` → `tests/nice_job_offers.json`.

## [0.6.0] - 2026-03-23

### Added

- **Rich ad JSON** (`AdOut`): `media` (thumb/small/large/generic URLs, `nb_images`, main thumb/small, `all_urls` deduped), full **`location`**, **`attributes`** (dynamic facets + extra keys allowed), **`options`**, **`price_cents`**, **`price_calendar`**, publication/metadata fields; **`description`** (same as **`body`**).
- **SDK**: `AdPictureSet` and parsing of the full upstream `images` object in `Ad._build`.
- **Tests** (`tests/test_ad_pictures.py`): `AdPictureSet` merge order/dedupe; `Ad._build` image tiers from raw JSON; `map_ad_to_response` exposes `images`, `media`, `body`/`description`.
- **README**: “JSON output schemas” section (field tables + illustrative `SearchResponse` example).

### Changed

- **`tests/test_search_service.py`**: mock ads include `pictures`, `location`, and related fields required by the mapper.

## [0.5.0] - 2026-03-23

### Added

- **Endpoints**: `POST /v1/search/cars`, `POST /v1/search/real-estate`; `GET /v1/schemas/search-cars`, `GET /v1/schemas/search-real-estate` (JSON Schema for request bodies with `$defs` and examples).
- **Schemas**: `SearchCarsBody`, `SearchRealEstateBody`, `SearchDomainBase`, **`RealEstateFilters`**; **`extra_from_real_estate_filters`** mapper.
- **Vehicle filters**: `u_car_brands` / `u_car_models`, `doors`, `vehicle_seats`, `vehicle_types`, `first_owner`, `critair`, `vehicule_colors`.
- **OpenAPI**: `Schemas` tag; app version **0.5.0**.

### Changed

- **`search` → kwargs**: `cars_body_to_kwargs`, `real_estate_body_to_kwargs`; shared `_search_core_kwargs` in `app/api/v1/common.py`.

## [0.4.0] - 2026-03-23

### Added

- **OpenAPI / Swagger**: tag descriptions, per-route summaries, shared error response models, `generate_operation_id`, Swagger UI options (filter, request duration, try-it-out).
- **Concurrency**: **`LbcClientPool`** and **`LBC_API_CLIENT_POOL_SIZE`** (default 4, cap 32); replaces a single global lock on the SDK client.
- **Vehicle search**: structured **`vehicle_filters`** merged into finder `extra_filters` (`app/services/leboncoin/vehicle_filters.py`).
- **Config**: optional **`LBC_API_DOCS_CONTACT_URL`**.
- **Runtime**: `uvicorn` uses **`loop="uvloop"`** on non-Windows when started via **`lbc-api`** / `app.main:run`.
- **Tests**: `tests/test_openapi.py` (`/openapi.json`, `/docs`, `/redoc`, tags, operationIds).

### Changed

- App version **0.4.0**; **`LbcRuntime`** delegates to the client pool (`app/services/lbc_pool.py`).

## [0.1.0] - 2026-03-23

### Added

- Initial **FastAPI** service: `GET /health`, `POST /v1/search`, `POST /v1/search/with-users`, `GET /v1/ads/{ad_id}`, `POST /v1/ads/batch`, `GET /v1/users/{user_id}`.
- Embedded **Leboncoin HTTP client** under `app/sdk/` (finder search, classified fetch, user card).
- **Layers**: `app/api`, `app/schemas`, `app/services`, `app/core`, pydantic settings (`LBC_API_*`), **`pytest`** suite with mocked sessions.
