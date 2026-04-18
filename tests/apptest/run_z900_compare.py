#!/usr/bin/env python3
"""
Live Leboncoin search: Kawasaki Z900 A2 · ≤ 7 000 € · ≤ 17 500 km — 20 km Saint-Laurent-du-Var.

Run from ``lbc-api/``::

    python3 tests/apptest/run_z900_compare.py
"""

from __future__ import annotations

import re

import _common as cm
from app.schemas.requests import CityLocation, IntRange, VehicleFilters

# Centre St-Laurent-du-Var (~mairie), 20 km radius — covers Nice, Cagnes, Antibes, Vence, Carros.
SEARCH_RADIUS_KM = 20
SAINT_LAURENT_DU_VAR = CityLocation(
    lat=43.6732,
    lng=7.1906,
    radius=SEARCH_RADIUS_KM * 1_000,
    city="Saint-Laurent-du-Var",
)

VEHICLE_FILTERS = VehicleFilters(
    price_eur=IntRange(min=1, max=7_000),
    mileage_km=IntRange(min=0, max=17_500),
)

SPEC = cm.CompareSpec(
    text="z900 a2",
    category="VEHICULES_MOTOS",
    locations=[SAINT_LAURENT_DU_VAR],
    vehicle_filters=VEHICLE_FILTERS,
    output_basename="z900_compare",
    page_title="Kawasaki Z900 A2 — compare (preview)",
    page_h1=f"Kawasaki Z900 A2 · St-Laurent-du-Var {SEARCH_RADIUS_KM} km",
    page_intro_html=(
        f"Filtres : <strong>&lt; 7 000 €</strong>, <strong>≤ 17 500 km</strong>, "
        f"{SEARCH_RADIUS_KM} km autour de Saint-Laurent-du-Var. Le « % chaud » = "
        "écart au prix moyen du lot affiché (positif = sous la moyenne)."
    ),
    filter_ok_hint=(
        "Annonces retenues : titre ou description contient « Z900 » / « Z 900 »."
    ),
    accent_hex="#ff6b35",
    accent_dim_hex="#c84b28",
    placeholder_label="Moto",
    max_pages=2,
)

# --- Predicates ---------------------------------------------------------------------------------

_Z900_RE = re.compile(r"z\s*[- ]?900", re.IGNORECASE)
# Titles that look like another bike (Z900 mentioned only as a body comparison).
_OTHER_BIKE_TITLE_RE = re.compile(
    r"royal\s*enfield|continental\s*gt|qjmotor|qj\s*motor|srk|cb\s*\d{3}|mt\s*\d{2}",
    re.IGNORECASE,
)


def _is_z900_in_title(ad: object) -> bool:
    """Strict: Z900 must appear in the title (avoids body-only comparisons leaking in)."""

    subject = getattr(ad, "subject", "") or ""
    return bool(_Z900_RE.search(subject))


def _is_z900_anywhere(ad: object) -> bool:
    """Relaxed fallback: Z900 in title or body, but never on a known other-bike title."""

    subject = getattr(ad, "subject", "") or ""
    body = getattr(ad, "body", "") or ""
    if _OTHER_BIKE_TITLE_RE.search(subject) and not _Z900_RE.search(subject):
        return False
    return bool(_Z900_RE.search(subject) or _Z900_RE.search(body))


def _accept_anything(_ad: object) -> bool:
    return True


STAGES = (
    cm.FilterStage(name="z900_in_title", predicate=_is_z900_in_title),
    cm.FilterStage(
        name="z900_anywhere",
        predicate=_is_z900_anywhere,
        relevance_note=(
            "Aucune annonce avec « Z900 » dans le titre — affichage des annonces qui "
            "mentionnent Z900 dans la description (à vérifier manuellement)."
        ),
    ),
    cm.FilterStage(
        name="raw_finder_results",
        predicate=_accept_anything,
        relevance_note=(
            "Aucune Kawasaki Z900 ne correspond à la zone et aux filtres. "
            "Ci-dessous : annonces brutes renvoyées par le moteur (à vérifier)."
        ),
    ),
)


# Public alias used by the unit tests.
_is_z900 = _is_z900_anywhere


def main() -> int:
    return cm.run_compare(SPEC, STAGES)


if __name__ == "__main__":
    raise SystemExit(main())
