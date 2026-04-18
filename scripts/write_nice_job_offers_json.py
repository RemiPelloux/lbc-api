#!/usr/bin/env python3
"""Fetch job offers in Nice and write ``tests/nice_job_offers.json`` (run from repo root)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.core.config import get_settings  # noqa: E402
from app.sdk.exceptions import LBCError  # noqa: E402
from app.services.leboncoin.client_factory import build_lbc_client  # noqa: E402
from app.services.leboncoin.live_search_scenarios import (  # noqa: E402
    NICE_JOB_SEARCH_AREA,
    nice_job_offers_execute_kwargs,
)
from app.services.leboncoin.mappers import map_search_to_response  # noqa: E402
from app.services.leboncoin.search_service import execute_search  # noqa: E402

OUTPUT = _ROOT / "tests" / "nice_job_offers.json"


def main() -> int:
    get_settings.cache_clear()
    client = build_lbc_client(get_settings().proxy_url)
    kwargs = nice_job_offers_execute_kwargs()
    try:
        search = execute_search(client, **kwargs)
    except LBCError as exc:
        print(f"Leboncoin error: {exc!r}", file=sys.stderr)
        return 1

    response = map_search_to_response(search, include_users=False)
    payload = {
        "scenario_id": "job_offers_nice",
        "description": (
            "Offres d'emploi (cat. Leboncoin offres d'emploi), zone Nice, "
            f"lat={NICE_JOB_SEARCH_AREA.lat}, lng={NICE_JOB_SEARCH_AREA.lng}, "
            f"radius_m={NICE_JOB_SEARCH_AREA.radius}. "
            "Première page uniquement (voir limit / meta.max_pages pour la suite)."
        ),
        "search": {
            "category": kwargs.get("category"),
            "limit": kwargs.get("limit"),
            "page": kwargs.get("page"),
            "sort": kwargs.get("sort"),
            "location": {
                "city": NICE_JOB_SEARCH_AREA.city,
                "lat": NICE_JOB_SEARCH_AREA.lat,
                "lng": NICE_JOB_SEARCH_AREA.lng,
                "radius_m": NICE_JOB_SEARCH_AREA.radius,
            },
        },
        "meta": response.meta.model_dump(mode="json"),
        "ads": [ad.model_dump(mode="json") for ad in response.ads],
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(response.ads)} ads to {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
