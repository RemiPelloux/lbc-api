"""
Live Leboncoin HTTP (real finder + real URLs).

**Not** part of the default ``pytest`` run (see ``addopts`` in ``pyproject.toml``) so the
offline suite stays fast and deterministic. Run this file **explicitly** when you want real
checks (PS5, iPhone, Mazda MX-5, maison ~60 m² près de Saint-Laurent-du-Var, 5 km)::

    pytest tests/test_real_leboncoin_optional.py -v

Use a clean French IP or ``LBC_API_PROXY_URL`` if you see HTTP 403 / Datadome.
"""

from __future__ import annotations

from typing import Any

import pytest
from app.core.config import get_settings
from app.sdk.exceptions import LBCError
from app.services.leboncoin.client_factory import build_lbc_client
from app.services.leboncoin.live_search_scenarios import live_scenario_execute_kwargs
from app.services.leboncoin.mappers import map_search_to_response
from app.services.leboncoin.search_service import execute_search

pytestmark = pytest.mark.real_lbc

_SCENARIO_LABELS: dict[str, str] = {
    "ps5": "PS5 (consoles)",
    "iphone": "iPhone (téléphones)",
    "mazda_mx5": "Mazda MX-5 (voitures)",
    "maison_60m2_saint_laurent_du_var_5km": (
        "Maison ~60 m² ventes, Saint-Laurent-du-Var 5 km"
    ),
}


def _assert_real_listing(label: str, *, min_ads: int = 1):
    def _check(search: Any) -> None:
        assert len(search.ads) >= min_ads, (
            f"{label}: finder returned fewer than {min_ads} ad(s) "
            "(query too narrow, empty region, or upstream change)."
        )
        out = map_search_to_response(search, include_users=False)
        first = out.ads[0]
        assert first.url.startswith("https://www.leboncoin.fr/"), (
            f"{label}: expected real listing URL on leboncoin.fr, got: {first.url!r}"
        )
        assert first.id is not None and first.id > 0, (
            f"{label}: expected real list_id from upstream."
        )
        if first.images:
            assert all(
                u.startswith("https://img.leboncoin.fr/") for u in first.images
            ), f"{label}: image URLs should be on Leboncoin CDN, got: {first.images!r}"
        if first.media.all_urls:
            assert all(
                u.startswith("https://img.leboncoin.fr/") for u in first.media.all_urls
            ), f"{label}: media.all_urls should only contain Leboncoin CDN URLs."

    return _check


def _scenario_specs():
    return [
        (sid, kw, _assert_real_listing(_SCENARIO_LABELS[sid]))
        for sid, kw in live_scenario_execute_kwargs()
    ]


def test_live_searches_ps5_iphone_mazda_and_realestate_near_saint_laurent_du_var() -> None:
    """Four real finder calls: run via ``pytest tests/test_real_leboncoin_optional.py``."""
    get_settings.cache_clear()
    settings = get_settings()
    client = build_lbc_client(settings.proxy_url)

    failures: list[str] = []

    for scenario_id, kwargs, assert_ok in _scenario_specs():
        try:
            search = execute_search(client, **kwargs)
        except LBCError as exc:
            failures.append(
                f"{scenario_id}: Leboncoin rejected the request (often 403 / Datadome). "
                f"Try FR residential IP or LBC_API_PROXY_URL. Detail: {exc!r}"
            )
            continue
        try:
            assert_ok(search)
        except AssertionError as exc:
            failures.append(f"{scenario_id}: {exc}")

    assert not failures, ";\n".join(failures)
