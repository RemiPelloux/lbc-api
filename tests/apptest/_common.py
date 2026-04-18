"""
Shared library for ``tests/apptest`` SaaS-compare prototype scripts.

Public surface (single, well-defined responsibility per function):

- ``OfferRow`` / ``CompareStats`` — output DTOs (immutable).
- ``FilterStage`` — declarative, ordered post-filter step (predicate + relevance note).
- ``extract_mileage_km`` / ``hot_vs_average_pct`` — pure helpers.
- ``select_via_stages`` — ordered fallback over a list of ``FilterStage``.
- ``compute_offers`` — single pass: priced rows + stats + sort by ``hot_vs_avg_pct``.
- ``build_rows`` / ``compute_stats`` — backwards-compat wrappers around ``compute_offers``.
- ``render_html`` / ``write_report`` — presentation + IO (no internal re-sort).
- ``CompareSpec`` / ``run_compare`` — orchestrator (settings → paginated search → filter →
  stats → report).
"""

from __future__ import annotations

import html as html_lib
import json
import re
import statistics
import sys
from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from string import Template
from typing import Any

# --- Boot: make ``app`` importable when this module is first loaded ------------------------------

_HERE = Path(__file__).resolve().parent
_LBC_API_ROOT = _HERE.parent.parent
for _p in (_HERE, _LBC_API_ROOT):
    _sp = str(_p)
    if _sp not in sys.path:
        sys.path.insert(0, _sp)

from app.core.config import get_settings  # noqa: E402
from app.schemas.requests import CityLocation, VehicleFilters  # noqa: E402
from app.sdk.exceptions import LBCError  # noqa: E402
from app.services.leboncoin.client_factory import build_lbc_client  # noqa: E402
from app.services.leboncoin.mappers import map_search_to_response  # noqa: E402
from app.services.leboncoin.search_service import execute_search  # noqa: E402
from app.services.leboncoin.vehicle_filters import extra_from_vehicle_filters  # noqa: E402

OUT_DIR = _HERE / "output"

# --- Module-level regex / constants (compiled once) ----------------------------------------------

_DIGITS_RE = re.compile(r"\D")
_MILEAGE_KEY_TOKENS = ("mileage", "kilometrage", "kilom")
_MILEAGE_RE = re.compile(r"(\d[\d\s]{2,8})\s*km\b")
_MAX_REASONABLE_KM = 1_000_000

PACK_SPORT_RE = re.compile(r"pack\s+sport(?!if)|sport\s+pack", re.IGNORECASE)


# --- DTOs ---------------------------------------------------------------------------------------


@dataclass(frozen=True)
class OfferRow:
    id: int | None
    subject: str
    url: str
    price_eur: float
    city_label: str | None
    mileage_km: int | None
    hot_vs_avg_pct: float
    thumb_url: str | None


@dataclass(frozen=True)
class CompareStats:
    avg_price_eur: float | None
    median_price_eur: float | None
    best_price_eur: float | None
    hottest: OfferRow | None


@dataclass(frozen=True)
class FilterStage:
    """One ordered post-filter step. The first stage that yields ≥1 ad wins."""

    name: str
    predicate: Callable[[Any], bool]
    relevance_note: str | None = None


@dataclass(frozen=True)
class CompareSpec:
    """Inputs of one comparison run (immutable & serializable)."""

    text: str | None
    category: str
    locations: list[CityLocation] | None
    vehicle_filters: VehicleFilters | None
    output_basename: str
    page_title: str
    page_h1: str
    page_intro_html: str
    filter_ok_hint: str
    sort: str = "CHEAPEST"
    limit: int = 35
    max_pages: int = 1
    placeholder_label: str = "Photo"
    accent_hex: str = "#ff6b35"
    accent_dim_hex: str = "#c84b28"
    extra_query_metadata: dict[str, Any] = field(default_factory=dict)


# --- Pure helpers --------------------------------------------------------------------------------


def _digits_to_int(s: str) -> int | None:
    digits = _DIGITS_RE.sub("", s)
    if not digits:
        return None
    try:
        return int(digits)
    except ValueError:
        return None


def extract_mileage_km(attributes: Sequence[Any], body: str) -> int | None:
    """Best-effort mileage extraction (attributes first, body regex fallback)."""

    for attr in attributes:
        key = (attr.key or "").lower()
        if not any(tok in key for tok in _MILEAGE_KEY_TOKENS):
            continue
        candidates: tuple[Any, ...] = (attr.value_label, attr.value, *(attr.values or []))
        for raw in candidates:
            if not raw:
                continue
            n = _digits_to_int(str(raw))
            if n is not None and 0 <= n < _MAX_REASONABLE_KM:
                return n

    m = _MILEAGE_RE.search(body.lower())
    if m:
        n = _digits_to_int(m.group(1))
        if n is not None and 0 <= n < _MAX_REASONABLE_KM:
            return n
    return None


def hot_vs_average_pct(price: float, avg: float) -> float:
    """Positive % means the ad is *cheaper* than ``avg`` by that fraction."""

    if avg <= 0:
        return 0.0
    return round((avg - price) / avg * 100, 1)


def select_via_stages(
    ads: Sequence[Any],
    stages: Iterable[FilterStage],
) -> tuple[list[Any], FilterStage | None]:
    """Try ``stages`` in order; return the first non-empty match (and which stage matched)."""

    for stage in stages:
        kept = [a for a in ads if stage.predicate(a)]
        if kept:
            return kept, stage
    return [], None


# --- Build rows + stats (single pass, single sort) -----------------------------------------------


def _ad_thumb(ad: Any) -> str | None:
    media = ad.media
    if media and media.thumb_url:
        return media.thumb_url
    images = ad.images
    if images:
        return images[0]
    return None


def _to_price(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def compute_offers(ads: Sequence[Any]) -> tuple[list[OfferRow], CompareStats]:
    """Single pass over ``ads``: extract priced rows, compute stats, sort once.

    Performance notes (vs. the old ``build_rows`` + ``compute_stats`` + ``render_html.sort``
    pipeline):
      - ads are scanned once (instead of twice for avg + per-row build).
      - ``hottest`` reuses the sort instead of an extra ``max()`` pass.
      - rows are sorted once (descending hot %); ``render_html`` consumes that order as-is.
    """

    priced: list[tuple[Any, float]] = []
    total = 0.0
    for ad in ads:
        price = _to_price(ad.price)
        if price is None:
            continue
        priced.append((ad, price))
        total += price

    if not priced:
        return [], CompareStats(None, None, None, None)

    avg = total / len(priced)
    rows = [
        OfferRow(
            id=ad.id,
            subject=ad.subject or "",
            url=ad.url or "",
            price_eur=price,
            city_label=(ad.location.city_label or ad.location.city),
            mileage_km=extract_mileage_km(ad.attributes, ad.body or ""),
            hot_vs_avg_pct=hot_vs_average_pct(price, avg),
            thumb_url=_ad_thumb(ad),
        )
        for ad, price in priced
    ]
    rows.sort(key=lambda r: r.hot_vs_avg_pct, reverse=True)

    prices = [p for _, p in priced]
    stats = CompareStats(
        avg_price_eur=avg,
        median_price_eur=statistics.median(prices),
        best_price_eur=min(prices),
        hottest=rows[0],
    )
    return rows, stats


# --- Backwards-compat thin wrappers (kept so existing call sites & tests stay valid) -------------


def build_rows(ads: Sequence[Any]) -> list[OfferRow]:
    """Compat shim: returns rows sorted by ``hot_vs_avg_pct`` desc (was unsorted before)."""

    rows, _ = compute_offers(ads)
    return rows


def compute_stats(rows: Sequence[OfferRow]) -> CompareStats:
    """Compat shim: derive stats from a row list without re-sorting."""

    if not rows:
        return CompareStats(None, None, None, None)
    prices = [r.price_eur for r in rows]
    return CompareStats(
        avg_price_eur=statistics.fmean(prices),
        median_price_eur=statistics.median(prices),
        best_price_eur=min(prices),
        hottest=max(rows, key=lambda r: r.hot_vs_avg_pct),
    )


# --- Presentation --------------------------------------------------------------------------------


_TEMPLATE_PATH = _HERE / "_template.html"


@lru_cache(maxsize=1)
def _load_template() -> Template:
    return Template(_TEMPLATE_PATH.read_text(encoding="utf-8"))


def _esc(s: str | None) -> str:
    return html_lib.escape(s or "", quote=True)


def _format_price(value: float) -> str:
    return f"{value:,.0f} €".replace(",", " ")


def _format_km(value: int | None) -> str:
    if value is None:
        return "—"
    return f"{value:,} km".replace(",", " ")


def _render_card(row: OfferRow, placeholder_label: str) -> str:
    hot = row.hot_vs_avg_pct
    hot_cls = "pill hot" if hot > 0 else "pill cool"
    hot_txt = f"{hot:+.1f} %"
    if row.thumb_url:
        img = f'<img src="{_esc(row.thumb_url)}" alt="" loading="lazy" />'
    else:
        img = f'<div class="ph">{_esc(placeholder_label)}</div>'
    title = _esc(row.subject[:120])
    href = _esc(row.url)
    return (
        '<article class="card">'
        f'<div class="thumb">{img}</div>'
        '<div class="body">'
        f'<h3><a href="{href}" target="_blank" rel="noopener">{title}</a></h3>'
        f'<p class="meta">{_esc(row.city_label)} · {_format_km(row.mileage_km)}</p>'
        '<div class="row">'
        f'<span class="price">{_format_price(row.price_eur)}</span>'
        f'<span class="{hot_cls}">vs moy. {hot_txt}</span>'
        "</div></div></article>"
    )


def render_html(
    *,
    spec: CompareSpec,
    rows: Sequence[OfferRow],
    stats: CompareStats,
    meta_total: int | None,
    relevance_note: str | None,
    strict_filter_ok: bool,
    generated_at: datetime | None = None,
) -> str:
    """Render the HTML report. ``rows`` MUST be pre-sorted (see ``compute_offers``)."""

    cards = "".join(_render_card(r, spec.placeholder_label) for r in rows)

    hero_hot = ""
    if stats.hottest is not None:
        h = stats.hottest
        hero_hot = (
            '<p class="hero-sub">Offre la plus <strong>« chaude »</strong> : '
            f'<a href="{_esc(h.url)}">{_esc(h.subject[:80])}</a> — '
            f"{_format_price(h.price_eur)} soit <em>{h.hot_vs_avg_pct:+.1f} %</em> "
            "vs la moyenne du lot.</p>"
        )

    if stats.avg_price_eur is None:
        stats_block = ""
    else:
        med = _format_price(stats.median_price_eur) if stats.median_price_eur is not None else "—"
        best = _format_price(stats.best_price_eur) if stats.best_price_eur is not None else "—"
        avg_fmt = _format_price(stats.avg_price_eur)
        stats_block = (
            '<div class="stats">'
            f'<div class="stat"><span>Prix moyen</span><strong>{avg_fmt}</strong></div>'
            f'<div class="stat"><span>Médiane</span><strong>{med}</strong></div>'
            f'<div class="stat"><span>Meilleur prix</span><strong>{best}</strong></div>'
            f'<div class="stat"><span>Annonces</span><strong>{len(rows)}</strong></div>'
            "</div>"
        )

    empty = "" if rows else (
        '<p class="empty">Aucune annonce avec prix sur cette sélection. '
        "Élargissez les critères ou vérifiez le proxy.</p>"
    )
    total_hint = ""
    if meta_total is not None:
        total_hint = (
            f'<p class="hint">Total estimé côté moteur : ~{meta_total} annonces '
            "(filtres finder).</p>"
        )
    filter_hint = (
        f'<p class="hint ok">{_esc(spec.filter_ok_hint)}</p>' if strict_filter_ok else ""
    )
    rel = f'<p class="warn">{_esc(relevance_note)}</p>' if relevance_note else ""

    when = (generated_at or datetime.now(UTC)).strftime("%Y-%m-%d %H:%M UTC")

    return _load_template().substitute(
        title=_esc(spec.page_title),
        accent=spec.accent_hex,
        accent_dim=spec.accent_dim_hex,
        h1=_esc(spec.page_h1),
        intro=spec.page_intro_html,
        hero_hot=hero_hot,
        filter_hint=filter_hint,
        rel=rel,
        stats_block=stats_block,
        empty=empty,
        total_hint=total_hint,
        cards=cards,
        generated_at=when,
    )


# --- IO + orchestrator ---------------------------------------------------------------------------


def write_report(
    *,
    spec: CompareSpec,
    rows: Sequence[OfferRow],
    stats: CompareStats,
    meta_total: int | None,
    matched_stage: FilterStage | None,
    relevance_note: str | None,
    strict_filter_ok: bool,
) -> tuple[Path, Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUT_DIR / f"{spec.output_basename}.json"
    html_path = OUT_DIR / f"{spec.output_basename}.html"

    payload: dict[str, Any] = {
        "generated_at": datetime.now(UTC).isoformat(),
        "query": {
            "text": spec.text,
            "category": spec.category,
            "sort": spec.sort,
            "limit": spec.limit,
            "locations": (
                [loc.model_dump() for loc in spec.locations] if spec.locations else None
            ),
            "vehicle_filters": (
                spec.vehicle_filters.model_dump(exclude_none=True)
                if spec.vehicle_filters is not None
                else None
            ),
            **spec.extra_query_metadata,
        },
        "meta": {"total": meta_total},
        "filtering": {
            "matched_stage": matched_stage.name if matched_stage else None,
            "strict_filter_ok": strict_filter_ok,
            "relevance_note": relevance_note,
        },
        "stats": {
            "avg_price_eur": stats.avg_price_eur,
            "median_price_eur": stats.median_price_eur,
            "best_price_eur": stats.best_price_eur,
            "hottest_ad_id": stats.hottest.id if stats.hottest else None,
        },
        "offers": [
            {
                "id": r.id,
                "subject": r.subject,
                "url": r.url,
                "price_eur": r.price_eur,
                "city_label": r.city_label,
                "mileage_km": r.mileage_km,
                "hot_vs_avg_pct": r.hot_vs_avg_pct,
                "thumb_url": r.thumb_url,
            }
            for r in rows
        ],
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    html_path.write_text(
        render_html(
            spec=spec,
            rows=rows,
            stats=stats,
            meta_total=meta_total,
            relevance_note=relevance_note,
            strict_filter_ok=strict_filter_ok,
        ),
        encoding="utf-8",
    )
    return json_path, html_path


def _iter_pages(client: Any, spec: CompareSpec, extra: dict[str, Any]) -> Iterator[Any]:
    """Yield successive ``Search`` results, stopping early on short pages or upstream errors."""

    for page in range(1, spec.max_pages + 1):
        search = execute_search(
            client,
            text=spec.text,
            url=None,
            page=page,
            limit=spec.limit,
            limit_alu=3,
            search_in_title_only=False,
            category=spec.category,
            sort=spec.sort,
            ad_type=None,
            owner_type=None,
            shippable=None,
            locations=spec.locations,
            extra_filters=extra,
        )
        yield search
        # Short page = no more results; bail out instead of paying for an empty round-trip.
        if not search.ads or len(search.ads) < spec.limit:
            return


def _fetch_all_ads(
    client: Any, spec: CompareSpec, extra: dict[str, Any]
) -> tuple[list[Any], int | None]:
    """Paginate, dedupe by ``ad.id`` (stable, by first-seen page order)."""

    seen: set[int] = set()
    collected: list[Any] = []
    meta_total: int | None = None
    for search in _iter_pages(client, spec, extra):
        resp = map_search_to_response(search, include_users=False)
        if meta_total is None:
            meta_total = resp.meta.total
        for ad in resp.ads:
            ad_id = ad.id
            if ad_id is None or ad_id in seen:
                continue
            seen.add(ad_id)
            collected.append(ad)
    return collected, meta_total


def run_compare(spec: CompareSpec, stages: Sequence[FilterStage]) -> int:
    """End-to-end run: paginated live search → tiered filters → stats → JSON+HTML report.

    Returns a process exit code (0 = ok, 1 = upstream error).
    """

    stages_seq = tuple(stages)
    if not stages_seq:
        print("No filter stages provided.", file=sys.stderr)
        return 1

    get_settings.cache_clear()
    settings = get_settings()
    client = build_lbc_client(settings.proxy_url)

    extra = extra_from_vehicle_filters(spec.vehicle_filters)

    try:
        raw_ads, meta_total = _fetch_all_ads(client, spec, extra)
    except LBCError as exc:
        print(f"Upstream error: {exc!r}", file=sys.stderr)
        return 1

    ads, matched = select_via_stages(raw_ads, stages_seq)
    relevance_note = matched.relevance_note if matched else None
    strict_filter_ok = matched is not None and matched is stages_seq[0]

    rows, stats = compute_offers(ads)

    json_path, html_path = write_report(
        spec=spec,
        rows=rows,
        stats=stats,
        meta_total=meta_total,
        matched_stage=matched,
        relevance_note=relevance_note,
        strict_filter_ok=strict_filter_ok,
    )

    print(f"Wrote {json_path}")
    print(f"Wrote {html_path}")
    if stats.hottest is not None:
        h = stats.hottest
        print(
            f"Hottest: {h.hot_vs_avg_pct:+.1f}% vs avg — "
            f"{_format_price(h.price_eur)} — {h.subject[:70]}"
        )
    return 0
