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

Interactive docs: `http://localhost:8000/docs` · machine-readable **request/response** schemas: `http://localhost:8000/openapi.json`

### Docker

Yes — the API runs in a container like any FastAPI app. The image uses **Debian Bookworm (glibc)** so **`curl_cffi`** binary wheels install cleanly; **Alpine (musl)** is not recommended for this project.

```bash
docker compose up --build
# → http://localhost:8000/docs
```

Pass the same `LBC_API_*` variables via `compose.yaml` or an env file. Outbound calls to Leboncoin use the **container’s public IP**; Datadome may block some datacenter ranges — use `LBC_API_PROXY_URL` (residential / clean French IP) if you see HTTP 403.

---

## JSON output schemas

All search endpoints return the same **`SearchResponse`** envelope. **`GET /v1/ads/{ad_id}`** returns one **`Ad`** object. **`POST /v1/ads/batch`** returns a **JSON array** of **`Ad`** objects (same shape as one element of `ads`, no `meta` wrapper).

### `SearchResponse` (search endpoints)

| Field | Type | Description |
|-------|------|-------------|
| `meta` | object | Result metadata |
| `meta.total` | int \| null | Total hits (when provided by upstream) |
| `meta.max_pages` | int \| null | Max paginated pages |
| `ads` | array | List of ads |

### `Ad` (each element of `ads`, or single-ad routes)

| Field | Type | Description |
|-------|------|-------------|
| `id` | int \| null | Listing id (`list_id`) |
| `subject` | string | Title |
| `url` | string | Leboncoin listing page URL |
| `images` | string[] | Large image URLs (same as `media.urls_large`) |
| `media` | object | All image tiers from upstream |
| `media.urls_thumb` | string[] | Thumbnail URLs |
| `media.urls_small` | string[] | Small URLs |
| `media.urls_large` | string[] | Large URLs |
| `media.urls` | string[] | Generic gallery URLs when present |
| `media.nb_images` | int \| null | Count when provided |
| `media.thumb_url` | string \| null | Single main thumb |
| `media.small_url` | string \| null | Single main small |
| `media.all_urls` | string[] | All distinct photo URLs (merged, deduped) |
| `price` | number \| null | Price in major units (from `price_cents` / 100) |
| `price_cents` | int \| null | Raw cents when present |
| `price_calendar` | any \| null | Upstream pricing calendar when present |
| `category_id` | string \| null | Category id |
| `category_name` | string \| null | Category label |
| `brand` | string \| null | Vehicle/product brand; if upstream sends a placeholder (e.g. `leboncoin`), we substitute the `brand` / `u_car_brand` attribute when available |
| `ad_type` | string \| null | e.g. offer / demand |
| `body` | string | Full description text (upstream `body`) |
| `description` | string | Same as `body` |
| `first_publication_date` | string \| null | |
| `expiration_date` | string \| null | |
| `index_date` | string \| null | |
| `status` | string \| null | |
| `has_phone` | boolean \| null | |
| `favorites` | int \| null | Favorites count when present |
| `location` | object | See below |
| `attributes` | array | Dynamic facets (surface, DPE, etc.); see below |
| `options` | object \| null | Listing options (urgent, gallery, …) when present |
| `owner_user_id` | string \| null | Seller user id |
| `user` | object \| null | Present only when seller was prefetched (`/search/with-users`) |

### `location` (inside each ad)

| Field | Type |
|-------|------|
| `country_id`, `region_id`, `region_name`, `department_id`, `department_name` | string \| null |
| `city_label`, `city`, `zipcode` | string \| null |
| `lat`, `lng` | number \| null |
| `source`, `provider` | string \| null |
| `is_shape` | boolean \| null |

### `attributes[]` (inside each ad)

| Field | Type |
|-------|------|
| `key`, `key_label`, `value`, `value_label` | string \| null |
| `values` | string[] |
| `values_label` | string[] \| null |
| `value_label_reader` | string \| null |
| `generic` | boolean \| null |

Extra keys may appear on an attribute object if Leboncoin adds fields (`AdAttributeOut` allows unknown keys).

### `user` (when present on an ad)

| Field | Type |
|-------|------|
| `id` | string |
| `name` | string |
| `account_type` | string |
| `location` | string \| null |

### `GET /v1/users/{user_id}`

Returns a **`User`** object with the same fields as `user` above (top-level JSON, not wrapped).

### Example: `SearchResponse` (shape only — **not** real data)

The JSON below shows **field names and nesting** only. **URLs and ids are invented** and will **not** load in a browser. For **real** listings and **real** `img.leboncoin.fr` links, run `pytest tests/test_real_leboncoin_optional.py -v` (see **Quality**).

```json
{
  "meta": {
    "total": 8830,
    "max_pages": 100
  },
  "ads": [
    {
      "id": 2179560719,
      "subject": "Example listing title",
      "url": "https://www.example.invalid/classified/0000000000.htm",
      "images": ["https://example.invalid/illustration-large.jpg"],
      "media": {
        "urls_thumb": ["https://example.invalid/illustration-thumb.jpg"],
        "urls_small": ["https://example.invalid/illustration-small.jpg"],
        "urls_large": ["https://example.invalid/illustration-large.jpg"],
        "urls": ["https://example.invalid/illustration.jpg"],
        "nb_images": 3,
        "thumb_url": null,
        "small_url": null,
        "all_urls": ["https://example.invalid/illustration.jpg"]
      },
      "price": 30500.0,
      "price_cents": 3050000,
      "price_calendar": null,
      "category_id": "9",
      "category_name": "Ventes immobilières",
      "brand": "",
      "ad_type": "offer",
      "body": "Full description text from the listing.",
      "description": "Full description text from the listing.",
      "first_publication_date": "2023-04-20 21:48:31",
      "expiration_date": "",
      "index_date": "",
      "status": "active",
      "has_phone": false,
      "favorites": null,
      "location": {
        "country_id": "FR",
        "region_id": "12",
        "region_name": "Ile-de-France",
        "department_id": "75",
        "department_name": "Paris",
        "city_label": "Paris 75009",
        "city": "Paris",
        "zipcode": "75009",
        "lat": 48.87115,
        "lng": 2.33207,
        "source": "city",
        "provider": "here",
        "is_shape": true
      },
      "attributes": [
        {
          "key": "real_estate_type",
          "key_label": "Type de bien",
          "value": "4",
          "value_label": "Parking",
          "values": ["4"],
          "values_label": null,
          "value_label_reader": null,
          "generic": true
        }
      ],
      "options": {
        "has_option": false,
        "booster": false,
        "photosup": false,
        "urgent": false,
        "gallery": false,
        "sub_toplist": false
      },
      "owner_user_id": "1988e0d2-9857-4270-80a3-16bee1703849",
      "user": null
    }
  ]
}
```

`user` is populated only on **`POST /v1/search/with-users`** when prefetch succeeds; otherwise it is `null`.

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

Default `pytest` does **not** collect `tests/test_real_leboncoin_optional.py` (see `addopts` in `pyproject.toml`), so the offline suite stays fast—**no skipped row** for a test you never meant to run.

### Live Leboncoin HTTP (no fake URLs)

Run that file **explicitly**. It performs **four** real finder searches and asserts **real** `leboncoin.fr` / `img.leboncoin.fr` URLs:

1. **PS5** (cat. consoles)  
2. **iPhone** (cat. téléphones)  
3. **Mazda MX-5** (cat. voitures)  
4. **Maison ~60 m²** (ventes immo), **5 km** autour de **Saint-Laurent-du-Var** (surface 55–65 m², type maison)

```bash
# If you get HTTP 403 / Datadome, try a French residential IP or:
# export LBC_API_PROXY_URL=http://user:pass@host:port
pytest tests/test_real_leboncoin_optional.py -v
```

To print **one real listing per scenario** as JSON (same searches as the test)::

    python3 scripts/print_live_search_examples.py

If the run fails, the message explains anti-bot / proxy; the suite does not invent listing or image URLs.

---

## Clone

```bash
git clone https://github.com/RemiPelloux/lbc-api.git
cd lbc-api
```

---

## License

This project is released under the **MIT License** (`LICENSE`, Copyright Remi Pelloux). The embedded client under `app/sdk/` includes MIT-licensed third-party portions; see `NOTICE`.
