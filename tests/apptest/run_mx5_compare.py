#!/usr/bin/env python3
"""
Live Leboncoin search: Mazda MX-5 184 ch · 2020+ · ≤ 50 000 km · Pack Sport — France entière.

Run from ``lbc-api/``::

    python3 tests/apptest/run_mx5_compare.py
"""

from __future__ import annotations

import re
from datetime import datetime

import _common as cm
from app.schemas.requests import IntRange, VehicleFilters

# --- Search spec --------------------------------------------------------------------------------

_THIS_YEAR = datetime.now().year

VEHICLE_FILTERS = VehicleFilters(
    registration_year=IntRange(min=2020, max=_THIS_YEAR + 1),
    mileage_km=IntRange(min=0, max=50_000),
    # Horsepower 184 ch is enforced in-app: LBC finder with min=max=184 returns ~0 ad.
)

SPEC = cm.CompareSpec(
    text="mazda mx5",
    category="VEHICULES_VOITURES",
    locations=None,
    vehicle_filters=VEHICLE_FILTERS,
    output_basename="mx5_compare",
    page_title="Mazda MX-5 — compare (preview)",
    page_h1="Mazda MX-5 · 184 ch · 2020+ · Pack Sport",
    page_intro_html=(
        "Filtres finder : année <strong>≥ 2020</strong>, <strong>≤ 50 000 km</strong>, "
        "France entière. Filtre app : <strong>184 ch</strong> + <strong>MX-5</strong> "
        "+ <strong>Pack Sport</strong> quand mentionné. Le « % chaud » = écart au prix "
        "moyen du lot affiché (positif = sous la moyenne)."
    ),
    filter_ok_hint=(
        "Annonces retenues : MX-5 / MX5, 184 ch, et « Pack Sport » (ou « Sport Pack »)."
    ),
    accent_hex="#e85d4c",
    accent_dim_hex="#b84538",
    extra_query_metadata={
        "horsepower_cv_target": 184,
        "horsepower_filter_strategy": "title+body+attributes (finder hp range often empty)",
    },
)

# --- Predicates (pure, easy to unit-test) ---------------------------------------------------------

_MX5_RE = re.compile(r"mx\s*[- ]?5", re.IGNORECASE)
_184_TEXT_RE = re.compile(r"\b184\s*(ch|cv|hp|ps|din)\b", re.IGNORECASE)
_184_BARE_RE = re.compile(r"\b184\b")
_184_ATTR_UNITS = ("ch", "cv", "din", "kw")


def _is_mx5(ad: object) -> bool:
    blob = f"{getattr(ad, 'subject', '') or ''} {getattr(ad, 'body', '') or ''}"
    return bool(_MX5_RE.search(blob))


def _is_184_cv(ad: object) -> bool:
    subject = getattr(ad, "subject", "") or ""
    body = getattr(ad, "body", "") or ""
    blob = f"{subject} {body}"
    if _184_TEXT_RE.search(blob):
        return True
    if _184_BARE_RE.search(blob) and _MX5_RE.search(blob):
        return True
    for attr in getattr(ad, "attributes", []) or []:
        raw = f"{attr.value_label or ''} {attr.value or ''}".lower()
        if "184" in raw and any(unit in raw for unit in _184_ATTR_UNITS):
            return True
    return False


def _is_pack_sport(ad: object) -> bool:
    blob = f"{getattr(ad, 'subject', '') or ''} {getattr(ad, 'body', '') or ''}"
    return bool(cm.PACK_SPORT_RE.search(blob))


def _all_strict(ad: object) -> bool:
    return _is_mx5(ad) and _is_184_cv(ad) and _is_pack_sport(ad)


def _mx5_184(ad: object) -> bool:
    return _is_mx5(ad) and _is_184_cv(ad)


STAGES = (
    cm.FilterStage(name="mx5+184ch+pack_sport", predicate=_all_strict),
    cm.FilterStage(
        name="mx5+184ch",
        predicate=_mx5_184,
        relevance_note=(
            "Aucune annonce ne mentionne « Pack Sport » ou « Sport Pack » — "
            "affichage des MX-5 184 ch (2020+, ≤ 50 000 km) sans ce critère."
        ),
    ),
    cm.FilterStage(
        name="mx5_only",
        predicate=_is_mx5,
        relevance_note=(
            "184 ch non retrouvé dans le titre, la description ni les attributs — "
            "affichage des MX-5 correspondant aux filtres année / kilométrage uniquement."
        ),
    ),
)


def main() -> int:
    return cm.run_compare(SPEC, STAGES)


if __name__ == "__main__":
    raise SystemExit(main())
