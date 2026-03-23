# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
