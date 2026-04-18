"""
Pure unit tests for the SaaS-compare prototype helpers (no HTTP, fast).

Covers ``hot_vs_average_pct``, mileage extraction, stage selection,
``build_rows`` / ``compute_stats`` invariants, and the per-script predicates
(MX-5 184 ch + Pack Sport, Z900).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

# Re-use the same sys.path bootstrap as the run scripts.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import _common as cm  # noqa: E402, I001
import run_mx5_compare as mx5_runner  # noqa: E402
import run_z900_compare as z900_runner  # noqa: E402


# --- Lightweight ad fakes (avoid importing pydantic AdOut for speed) -----------------------------


@dataclass
class _Attr:
    key: str | None = None
    value: str | None = None
    value_label: str | None = None
    values: list[str] = field(default_factory=list)


@dataclass
class _Loc:
    city_label: str | None = None
    city: str | None = None


@dataclass
class _Media:
    thumb_url: str | None = None


@dataclass
class _Ad:
    id: int = 1
    subject: str = ""
    body: str = ""
    url: str = "https://example.com/ad/1"
    price: float | None = 1000.0
    attributes: list[_Attr] = field(default_factory=list)
    location: _Loc = field(default_factory=_Loc)
    media: _Media | None = None
    images: list[str] = field(default_factory=list)


# --- hot_vs_average_pct ---------------------------------------------------------------------------


class TestHotVsAveragePct:
    def test_below_average_is_positive(self) -> None:
        assert cm.hot_vs_average_pct(price=900.0, avg=1000.0) == 10.0

    def test_above_average_is_negative(self) -> None:
        assert cm.hot_vs_average_pct(price=1100.0, avg=1000.0) == -10.0

    def test_equal_to_average_is_zero(self) -> None:
        assert cm.hot_vs_average_pct(price=1000.0, avg=1000.0) == 0.0

    def test_zero_avg_is_safe(self) -> None:
        assert cm.hot_vs_average_pct(price=500.0, avg=0.0) == 0.0

    def test_rounded_to_one_decimal(self) -> None:
        assert cm.hot_vs_average_pct(price=993.0, avg=1000.0) == 0.7


# --- extract_mileage_km ---------------------------------------------------------------------------


class TestExtractMileageKm:
    def test_from_mileage_attribute(self) -> None:
        attrs = [_Attr(key="mileage", value_label="42 500 km")]
        assert cm.extract_mileage_km(attrs, body="") == 42500

    def test_from_kilometrage_attribute_with_value(self) -> None:
        attrs = [_Attr(key="kilometrage", value="17500")]
        assert cm.extract_mileage_km(attrs, body="") == 17500

    def test_from_body_when_no_attribute(self) -> None:
        body = "Très bel état, 89 000 km au compteur, ct ok."
        assert cm.extract_mileage_km([], body) == 89000

    def test_returns_none_when_unknown(self) -> None:
        assert cm.extract_mileage_km([], body="aucune info utile ici") is None

    def test_ignores_unreasonable_values(self) -> None:
        attrs = [_Attr(key="mileage", value_label="9 999 999 999 km")]
        assert cm.extract_mileage_km(attrs, body="") is None


# --- select_via_stages ----------------------------------------------------------------------------


class TestSelectViaStages:
    def test_first_matching_stage_wins(self) -> None:
        ads = [_Ad(subject="A"), _Ad(subject="B")]
        stages = (
            cm.FilterStage(name="empty", predicate=lambda a: False),
            cm.FilterStage(name="all", predicate=lambda a: True, relevance_note="loose"),
        )
        kept, matched = cm.select_via_stages(ads, stages)
        assert [a.subject for a in kept] == ["A", "B"]
        assert matched is not None and matched.name == "all"
        assert matched.relevance_note == "loose"

    def test_returns_empty_when_no_stage_matches(self) -> None:
        ads = [_Ad()]
        stages = (cm.FilterStage(name="never", predicate=lambda a: False),)
        kept, matched = cm.select_via_stages(ads, stages)
        assert kept == []
        assert matched is None


# --- build_rows + compute_stats ------------------------------------------------------------------


class TestBuildRowsAndStats:
    def _ads(self) -> list[_Ad]:
        return [
            _Ad(id=1, subject="cheap", price=800.0, location=_Loc(city_label="Nice")),
            _Ad(id=2, subject="mid", price=1000.0, location=_Loc(city_label="Antibes")),
            _Ad(id=3, subject="dear", price=1200.0, location=_Loc(city_label="Cannes")),
        ]

    def test_drops_ads_with_no_price(self) -> None:
        ads = [_Ad(price=None), _Ad(price=900.0)]
        rows = cm.build_rows(ads)
        assert len(rows) == 1
        assert rows[0].price_eur == 900.0

    def test_hot_pct_relative_to_average(self) -> None:
        rows = cm.build_rows(self._ads())
        # avg = 1000 → 800 = +20%, 1000 = 0%, 1200 = -20%
        by_id = {r.id: r for r in rows}
        assert by_id[1].hot_vs_avg_pct == 20.0
        assert by_id[2].hot_vs_avg_pct == 0.0
        assert by_id[3].hot_vs_avg_pct == -20.0

    def test_compute_stats_picks_correct_hottest_and_best(self) -> None:
        rows = cm.build_rows(self._ads())
        stats = cm.compute_stats(rows)
        assert stats.avg_price_eur == 1000.0
        assert stats.median_price_eur == 1000.0
        assert stats.best_price_eur == 800.0
        assert stats.hottest is not None and stats.hottest.id == 1

    def test_empty_input_yields_empty_stats(self) -> None:
        stats = cm.compute_stats([])
        assert stats == cm.CompareStats(None, None, None, None)

    def test_thumb_falls_back_to_images_when_media_missing(self) -> None:
        ad = _Ad(price=1000.0, media=None, images=["https://img/a.jpg"])
        rows = cm.build_rows([ad])
        assert rows[0].thumb_url == "https://img/a.jpg"


# --- MX-5 predicates ------------------------------------------------------------------------------


class TestMx5Predicates:
    def test_pack_sport_matches_canonical_phrasing(self) -> None:
        ad = _Ad(subject="Mazda MX-5 Pack Sport 2.0 184ch")
        assert mx5_runner._all_strict(ad)

    def test_pack_sport_does_not_match_pack_sportif(self) -> None:
        # The bug we fixed: "Pack Sportif" was matching the old regex.
        ad = _Ad(subject="MX-5 Pack Sportif 184 ch")
        assert not cm.PACK_SPORT_RE.search(ad.subject)

    def test_184_cv_via_attribute_value(self) -> None:
        ad = _Ad(
            subject="Mazda MX-5",
            attributes=[_Attr(key="horsepower", value_label="184 ch")],
        )
        assert mx5_runner._is_184_cv(ad)

    def test_184_cv_via_body_with_unit(self) -> None:
        ad = _Ad(subject="Mazda MX-5", body="Moteur 2.0 de 184 cv, état neuf.")
        assert mx5_runner._is_184_cv(ad)

    def test_184_bare_requires_mx5_context(self) -> None:
        unrelated = _Ad(subject="Vélo 184 spokes", body="rien à voir")
        assert not mx5_runner._is_184_cv(unrelated)

    def test_falls_back_when_no_pack_sport(self) -> None:
        # _all_strict should fail, _mx5_184 should pass.
        ad = _Ad(subject="Mazda MX-5 184 ch Selection")
        assert not mx5_runner._all_strict(ad)
        assert mx5_runner._mx5_184(ad)


# --- Z900 predicates ------------------------------------------------------------------------------


class TestZ900Predicate:
    def test_matches_title(self) -> None:
        assert z900_runner._is_z900(_Ad(subject="Kawasaki Z900 70kw"))

    def test_matches_with_space_or_dash(self) -> None:
        assert z900_runner._is_z900(_Ad(subject="Kawa Z 900"))
        assert z900_runner._is_z900(_Ad(subject="kawa z-900 a2"))

    def test_drops_other_bike_titles_even_if_body_mentions_z900(self) -> None:
        ad = _Ad(
            subject="Royal Enfield Continental GT",
            body="Comparable à une Z900 mais beaucoup plus légère.",
        )
        assert not z900_runner._is_z900(ad)

    def test_matches_when_body_mentions_z900_and_title_is_neutral(self) -> None:
        ad = _Ad(subject="Moto sportive", body="Vends ma Z900 abs.")
        assert z900_runner._is_z900(ad)


# --- render_html smoke ----------------------------------------------------------------------------


class TestRenderHtmlSmoke:
    def test_renders_well_formed_html_with_stats_and_card(self) -> None:
        rows = cm.build_rows(
            [
                _Ad(
                    id=42,
                    subject="Z900 70kw",
                    price=6500.0,
                    location=_Loc(city_label="Nice"),
                )
            ]
        )
        stats = cm.compute_stats(rows)
        html = cm.render_html(
            spec=z900_runner.SPEC,
            rows=rows,
            stats=stats,
            meta_total=1,
            relevance_note=None,
            strict_filter_ok=True,
        )
        assert "<!DOCTYPE html>" in html
        assert "Kawasaki Z900 A2" in html
        assert "Z900 70kw" in html
        assert "6 500 €" in html
