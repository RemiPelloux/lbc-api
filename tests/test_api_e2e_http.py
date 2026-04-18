"""
HTTP end-to-end tests against a **running** API (e.g. ``lbc-api`` in Docker).

Set ``LBC_API_E2E_BASE_URL`` (no trailing slash), e.g. ``http://127.0.0.1:8000`` on the host
or ``http://lbc-api:8000`` from another container on the same Compose network.

This module is **ignored** in the default ``pytest`` run (``addopts`` in ``pyproject.toml``);
run it explicitly via ``scripts/docker_api_e2e.sh`` or::

    LBC_API_E2E_BASE_URL=http://127.0.0.1:8000 pytest tests/test_api_e2e_http.py -v
"""

from __future__ import annotations

import json
import os

import httpx
import pytest

pytestmark = pytest.mark.e2e_http


@pytest.fixture(scope="module")
def base_url() -> str:
    raw = os.environ.get("LBC_API_E2E_BASE_URL", "").strip().rstrip("/")
    if not raw:
        pytest.fail(
            "LBC_API_E2E_BASE_URL must be set (e.g. http://lbc-api:8000 inside Compose)."
        )
    return raw


@pytest.fixture(scope="module")
def http_client(base_url: str) -> httpx.Client:
    with httpx.Client(base_url=base_url, timeout=60.0) as client:
        yield client


def test_e2e_health(http_client: httpx.Client) -> None:
    r = http_client.get("/health")
    assert r.status_code == 200, r.text
    assert r.json() == {"status": "ok"}


def test_e2e_openapi_lists_search(http_client: httpx.Client) -> None:
    r = http_client.get("/openapi.json")
    assert r.status_code == 200, r.text
    paths = r.json().get("paths", {})
    assert "/v1/search" in paths
    assert "/health" in paths or any("health" in p for p in paths)


def _assert_search_ok(r: httpx.Response, label: str) -> dict:
    if r.status_code in (403, 502, 503):
        pytest.fail(
            f"{label}: upstream/API error {r.status_code} (often Datadome from container IP). "
            f"Body (truncated): {r.text[:800]!r}"
        )
    assert r.status_code == 200, f"{label}: {r.status_code} {r.text[:800]!r}"
    data = r.json()
    assert "meta" in data and "ads" in data, f"{label}: unexpected JSON keys {data.keys()}"
    assert isinstance(data["ads"], list)
    return data


def _print_listing_samples(scenario: str, data: dict, *, max_ads: int = 2) -> None:
    """Echo real listing snippets to stdout (use ``pytest -s`` to see them)."""
    meta = data.get("meta", {})
    ads = data.get("ads", [])[:max_ads]
    print(f"\n--- E2E listing samples: {scenario} ---", flush=True)
    print(f"meta: {json.dumps(meta, ensure_ascii=False)}", flush=True)
    for i, ad in enumerate(ads, 1):
        loc = ad.get("location") or {}
        sample = {
            "id": ad.get("id"),
            "subject": ad.get("subject"),
            "url": ad.get("url"),
            "price_eur": ad.get("price"),
            "city": loc.get("city_label") or loc.get("city"),
        }
        print(f"ad[{i}]: {json.dumps(sample, ensure_ascii=False)}", flush=True)


def test_e2e_scenario_search_iphone(http_client: httpx.Client) -> None:
    body: dict = {
        "text": "iphone",
        "page": 1,
        "limit": 5,
        "limit_alu": 0,
        "search_in_title_only": False,
        "category": "ELECTRONIQUE_TELEPHONES_ET_OBJETS_CONNECTES",
        "sort": "NEWEST",
        "extra_filters": {},
    }
    r = http_client.post("/v1/search", json=body)
    data = _assert_search_ok(r, "iphone search")
    assert len(data["ads"]) >= 1, "expected at least one ad from live finder"
    first = data["ads"][0]
    assert first.get("url", "").startswith("https://www.leboncoin.fr/")
    _print_listing_samples("iPhone (telephones)", data)


def test_e2e_scenario_job_offers_nice(http_client: httpx.Client) -> None:
    body: dict = {
        "text": None,
        "page": 1,
        "limit": 5,
        "limit_alu": 0,
        "search_in_title_only": False,
        "category": "EMPLOI_OFFRES_DEMPLOI",
        "sort": "NEWEST",
        "locations": [
            {"lat": 43.7031, "lng": 7.2661, "radius": 12000, "city": "Nice"},
        ],
        "extra_filters": {},
    }
    r = http_client.post("/v1/search", json=body)
    data = _assert_search_ok(r, "Nice job offers")
    assert len(data["ads"]) >= 1, "expected at least one job ad near Nice"
    first = data["ads"][0]
    assert first.get("url", "").startswith("https://www.leboncoin.fr/")
    _print_listing_samples("Job offers near Nice", data)
