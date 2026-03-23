"""Domain-specific search bodies (cars, immobilier) and structured immobilier filters."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.requests import CityLocation, IntRange, VehicleFilters


class RealEstateFilters(BaseModel):
    """
    Structured immobilier filters. Finder keys match Leboncoin URL/API tokens.

    Enum-style fields are **lists of string ids** as used on the site (copy from a refined
    search URL if unsure). Ranges are inclusive min/max integers.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "price_eur": {"min": 250_000, "max": 450_000},
                    "square_m2": {"min": 45, "max": 85},
                    "rooms": {"min": 3, "max": 5},
                    "bedrooms": {"min": 2, "max": 4},
                    "real_estate_types": ["2"],
                    "energy_rates": ["a", "b", "c"],
                    "ges_ratings": ["a", "b"],
                    "land_plot_surface_m2": {"min": 0, "max": 500},
                    "floor_numbers": ["1", "2"],
                    "furnished": ["0"],
                    "elevator": ["1"],
                    "specificities": ["1", "2"],
                    "immo_sell_types": ["old"],
                    "lease_types": ["sell"],
                    "nb_parkings": {"min": 1, "max": 2},
                },
                {
                    "building_year": {"min": 1990, "max": 2024},
                    "nb_shower_rooms": {"min": 1, "max": 2},
                    "charges_eur": {"min": 100, "max": 400},
                    "rent_eur": {"min": 700, "max": 1500},
                    "fees_at_buyer_expense_eur": {"min": 0, "max": 15000},
                    "mandate_types": ["1"],
                    "heating_types": ["individuel"],
                    "outside_access_types": ["1"],
                    "global_conditions": ["bon_etat"],
                    "activity_sectors": ["bureaux"],
                    "orientation": ["sud"],
                    "seller_types": ["private"],
                    "custom_refunds": ["0"],
                    "proximities": ["1"],
                    "land_types": ["constructible"],
                    "fees_charged_to": ["buyer"],
                    "is_import": ["false"],
                },
            ]
        }
    )

    price_eur: IntRange | None = Field(default=None, description="Euros → finder `price`")
    square_m2: IntRange | None = Field(default=None, description="Habitable m² → `square`")
    land_plot_surface_m2: IntRange | None = Field(
        default=None,
        description="Terrain / parcelle m² → `land_plot_surface`",
    )
    rooms: IntRange | None = Field(default=None, description="Pièces (min/max) → `rooms`")
    bedrooms: IntRange | None = Field(default=None, description="Chambres → `bedrooms`")
    building_year: IntRange | None = Field(
        default=None,
        description="Année de construction → `building_year`",
    )
    nb_parkings: IntRange | None = Field(default=None, description="Places parking → `nb_parkings`")
    nb_shower_rooms: IntRange | None = Field(
        default=None,
        description="Salles d'eau → `nb_shower_room`",
    )
    charges_eur: IntRange | None = Field(
        default=None,
        description="Charges mensuelles (locations) → `charges`",
    )
    rent_eur: IntRange | None = Field(default=None, description="Loyer mensuel → `rent`")
    fees_at_buyer_expense_eur: IntRange | None = Field(
        default=None,
        description="Honoraires à la charge de l'acquéreur → `fees_at_buyer_expense`",
    )

    real_estate_types: list[str] | None = Field(
        default=None,
        description="Types de bien → `real_estate_type` (ex. 1 maison, 2 appartement — ids site)",
    )
    energy_rates: list[str] | None = Field(
        default=None,
        description="Classe DPE → `energy_rate` (ex. a, b, c, d, e, f, g, v)",
    )
    ges_ratings: list[str] | None = Field(default=None, description="GES → `ges`")
    floor_numbers: list[str] | None = Field(default=None, description="Étage → `floor_number`")
    furnished: list[str] | None = Field(default=None, description="Meublé → `furnished`")
    elevator: list[str] | None = Field(default=None, description="Ascenseur → `elevator`")
    specificities: list[str] | None = Field(
        default=None,
        description="Équipements (balcon, cave, …) → `specificities`",
    )
    immo_sell_types: list[str] | None = Field(
        default=None,
        description="Neuf / ancien → `immo_sell_type` (ex. old, new)",
    )
    lease_types: list[str] | None = Field(
        default=None,
        description="Vente / location → `lease_type` (ex. sell, rent)",
    )
    mandate_types: list[str] | None = Field(
        default=None,
        description="Type de mandat → `mandate_type`",
    )
    heating_types: list[str] | None = Field(default=None, description="Chauffage → `heating_type`")
    outside_access_types: list[str] | None = Field(default=None, description="→ `outside_access`")
    global_conditions: list[str] | None = Field(
        default=None,
        description="État du bien → `global_condition`",
    )
    activity_sectors: list[str] | None = Field(
        default=None,
        description="Secteur d'activité (bureaux / commerces) → `activity_sector`",
    )
    orientation: list[str] | None = Field(default=None, description="Exposition → `orientation`")
    seller_types: list[str] | None = Field(default=None, description="→ `seller_type`")
    custom_refunds: list[str] | None = Field(
        default=None,
        description="→ `custom_refund`",
    )
    proximities: list[str] | None = Field(default=None, description="Proximités → `proximity`")
    land_types: list[str] | None = Field(
        default=None,
        description="Nature du terrain → `land_type`",
    )
    fees_charged_to: list[str] | None = Field(
        default=None,
        description="Honoraires → `fees_charged_to`",
    )
    is_import: list[str] | None = Field(
        default=None,
        description="Import → `is_import` (ex. true/false)",
    )


class SearchDomainBase(BaseModel):
    """Shared search fields for domain endpoints (cars, immobilier)."""

    text: str | None = None
    url: str | None = None
    page: int = 1
    limit: int = 35
    limit_alu: int = 3
    search_in_title_only: bool = False
    sort: str | None = None
    ad_type: str | None = None
    owner_type: str | None = None
    shippable: bool | None = None
    locations: list[CityLocation] | None = None
    extra_filters: dict[str, Any] = Field(
        default_factory=dict,
        description="Any other finder key as range [min,max] or enum list of strings",
    )


class SearchCarsBody(SearchDomainBase):
    """Search pré-configurée **véhicules** (default catégorie voitures)."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "text": "peugeot 308",
                    "sort": "NEWEST",
                    "limit": 15,
                    "category": "VEHICULES_VOITURES",
                    "vehicle_filters": {
                        "registration_year": {"min": 2018, "max": 2023},
                        "mileage_km": {"min": 0, "max": 100000},
                        "horsepower": {"min": 100, "max": 160},
                        "price_eur": {"min": 8000, "max": 22000},
                        "fuels": ["diesel", "essence"],
                        "gearboxes": ["manuelle", "automatique"],
                        "u_car_brands": ["peugeot"],
                        "u_car_models": ["308"],
                        "doors": {"min": 4, "max": 5},
                        "vehicle_seats": {"min": 5, "max": 5},
                        "vehicle_types": ["citadine"],
                        "first_owner": ["1"],
                        "critair": ["1", "2"],
                        "vehicule_colors": ["gris", "noir"],
                    },
                },
                {
                    "category": "VEHICULES_MOTOS",
                    "vehicle_filters": {
                        "registration_year": {"min": 2015, "max": 2024},
                        "mileage_km": {"min": 0, "max": 50000},
                        "horsepower": {"min": 15, "max": 95},
                        "price_eur": {"min": 2000, "max": 12000},
                        "fuels": ["essence"],
                        "gearboxes": ["manuelle"],
                        "u_car_brands": ["yamaha"],
                        "u_car_models": ["mt-07"],
                        "doors": {"min": 0, "max": 0},
                        "vehicle_seats": {"min": 1, "max": 2},
                        "vehicle_types": ["roadster"],
                        "first_owner": ["0"],
                        "critair": ["0"],
                        "vehicule_colors": ["noir"],
                    },
                },
            ]
        }
    )

    category: str | None = Field(
        default=None,
        description=(
            "Sous-catégorie véhicules (enum name ou id). Défaut: `VEHICULES_VOITURES` "
            "(ex. `VEHICULES_MOTOS`, `VEHICULES_UTILITAIRES`)."
        ),
    )
    vehicle_filters: VehicleFilters | None = Field(
        default=None,
        description="Filtres voiture / 2-roues / utilitaires selon la catégorie choisie",
    )


class SearchRealEstateBody(SearchDomainBase):
    """Search pré-configurée **immobilier** (défaut: ventes)."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "text": "appartement lumineux",
                    "sort": "NEWEST",
                    "category": "IMMOBILIER_VENTES_IMMOBILIERES",
                    "real_estate_filters": {
                        "price_eur": {"min": 300000, "max": 550000},
                        "square_m2": {"min": 55, "max": 95},
                        "rooms": {"min": 3, "max": 4},
                        "real_estate_types": ["2"],
                        "energy_rates": ["a", "b", "c"],
                        "floor_numbers": ["2", "3", "4"],
                        "elevator": ["1"],
                        "immo_sell_types": ["old"],
                        "lease_types": ["sell"],
                    },
                },
                {
                    "category": "IMMOBILIER_LOCATIONS",
                    "real_estate_filters": {
                        "rent_eur": {"min": 800, "max": 1400},
                        "square_m2": {"min": 35, "max": 60},
                        "rooms": {"min": 2, "max": 3},
                        "furnished": ["1"],
                        "charges_eur": {"min": 50, "max": 200},
                    },
                },
            ]
        }
    )

    category: str | None = Field(
        default=None,
        description=(
            "Sous-catégorie immobilier. Défaut: `IMMOBILIER_VENTES_IMMOBILIERES`. "
            "Ex. `IMMOBILIER_LOCATIONS`, `IMMOBILIER_COLOCATIONS`, "
            "`IMMOBILIER_BUREAUX_ET_COMMERCES`."
        ),
    )
    real_estate_filters: RealEstateFilters | None = Field(
        default=None,
        description="Filtres spécifiques annonces immo (finder)",
    )
