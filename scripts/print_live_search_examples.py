#!/usr/bin/env python3
"""Print one real listing per scenario (PS5, iPhone, Mazda MX-5, maison St-Laurent-du-Var)."""

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
from app.services.leboncoin.live_search_scenarios import live_scenario_execute_kwargs  # noqa: E402
from app.services.leboncoin.mappers import map_search_to_response  # noqa: E402
from app.services.leboncoin.search_service import execute_search  # noqa: E402


def main() -> int:
    get_settings.cache_clear()
    settings = get_settings()
    client = build_lbc_client(settings.proxy_url)
    examples: dict[str, dict[str, object | None]] = {}

    for scenario_id, kwargs in live_scenario_execute_kwargs():
        try:
            search = execute_search(client, **kwargs)
        except LBCError as exc:
            print(f"{scenario_id}: upstream error: {exc!r}", file=sys.stderr)
            return 1
        if not search.ads:
            print(f"{scenario_id}: no ads returned", file=sys.stderr)
            return 1
        resp = map_search_to_response(search, include_users=False)
        ad = resp.ads[0]
        loc = ad.location
        examples[scenario_id] = {
            "id": ad.id,
            "subject": ad.subject,
            "url": ad.url,
            "price_eur": ad.price,
            "price_cents": ad.price_cents,
            "city_label": loc.city_label,
            "city": loc.city,
            "zipcode": loc.zipcode,
            "department": loc.department_name,
            "first_image_url": ad.images[0] if ad.images else None,
        }

    print(json.dumps(examples, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
