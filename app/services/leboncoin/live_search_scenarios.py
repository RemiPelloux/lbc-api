"""Shared live-search scenarios (integration test + ``scripts/print_live_search_examples.py``)."""

from __future__ import annotations

from typing import Any

from app.schemas.domain_search import RealEstateFilters
from app.schemas.requests import CityLocation, IntRange

from .real_estate_filters import extra_from_real_estate_filters

# Centre-ville Saint-Laurent-du-Var (~mairie) ; rayon 5 km = 5000 m
SAINT_LAURENT_DU_VAR = CityLocation(
    lat=43.6732,
    lng=7.1906,
    radius=5000,
    city="Saint-Laurent-du-Var",
)

# Nice (centre-ville) ; rayon 12 km — agglomeration courante pour l'emploi local
NICE_JOB_SEARCH_AREA = CityLocation(
    lat=43.7031,
    lng=7.2661,
    radius=12_000,
    city="Nice",
)


def base_execute_search_kwargs() -> dict[str, Any]:
    return {
        "url": None,
        "page": 1,
        "limit": 10,
        "limit_alu": 3,
        "search_in_title_only": False,
        "sort": "NEWEST",
        "ad_type": None,
        "owner_type": None,
        "shippable": None,
    }


def nice_job_offers_execute_kwargs() -> dict[str, Any]:
    """Offres d'emploi sur Nice (sans mot-cle) — premiere page finder (``limit`` annonces)."""
    return {
        **base_execute_search_kwargs(),
        "limit": 35,
        "text": None,
        "category": "EMPLOI_OFFRES_DEMPLOI",
        "locations": [NICE_JOB_SEARCH_AREA],
        "extra_filters": {},
    }


def live_scenario_execute_kwargs() -> list[tuple[str, dict[str, Any]]]:
    """(scenario_id, kwargs for ``execute_search``)."""
    bk = base_execute_search_kwargs()
    immo_extra = extra_from_real_estate_filters(
        RealEstateFilters(
            square_m2=IntRange(min=55, max=65),
            real_estate_types=["1"],
        )
    )
    return [
        (
            "ps5",
            {
                **bk,
                "text": "playstation 5",
                "category": "ELECTRONIQUE_CONSOLES",
                "locations": None,
                "extra_filters": {},
            },
        ),
        (
            "iphone",
            {
                **bk,
                "text": "iphone",
                "category": "ELECTRONIQUE_TELEPHONES_ET_OBJETS_CONNECTES",
                "locations": None,
                "extra_filters": {},
            },
        ),
        (
            "mazda_mx5",
            {
                **bk,
                "text": "mazda mx5",
                "category": "VEHICULES_VOITURES",
                "locations": None,
                "extra_filters": {},
            },
        ),
        (
            "maison_60m2_saint_laurent_du_var_5km",
            {
                **bk,
                "text": "maison",
                "category": "IMMOBILIER_VENTES_IMMOBILIERES",
                "locations": [SAINT_LAURENT_DU_VAR],
                "extra_filters": immo_extra,
            },
        ),
        ("job_offers_nice", nice_job_offers_execute_kwargs()),
    ]
