from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from app.sdk.model.enums import Sort
from app.sdk.model.search import Search
from app.services.leboncoin.enum_resolution import parse_enum_member
from app.services.leboncoin.search_service import execute_search, run_search_with_users


def test_parse_enum_member_resolves_name() -> None:
    assert parse_enum_member(Sort, "NEWEST", Sort.RELEVANCE) == Sort.NEWEST


def test_parse_enum_member_unknown_raises() -> None:
    with pytest.raises(ValueError):
        parse_enum_member(Sort, "NOT_A_REAL_SORT", Sort.RELEVANCE)


def test_execute_search_uses_url_mode() -> None:
    client = MagicMock()
    fake = MagicMock(spec=Search)
    client.search.return_value = fake

    result = execute_search(
        client,
        text="ignored",
        url="https://www.leboncoin.fr/recherche?category=9",
        page=2,
        limit=10,
        limit_alu=0,
        search_in_title_only=False,
        category=None,
        sort=None,
        ad_type=None,
        owner_type=None,
        shippable=None,
        locations=None,
        extra_filters={},
    )

    assert result is fake
    client.search.assert_called_once()
    kwargs = client.search.call_args.kwargs
    assert kwargs["url"].startswith("https://")
    assert kwargs["page"] == 2
    assert kwargs["limit"] == 10


def test_run_search_with_users_calls_prefetch(monkeypatch: pytest.MonkeyPatch) -> None:
    client = MagicMock()
    ad = MagicMock()
    ad._user_id = "u1"
    ad._user = None
    ad.id = 1
    ad.subject = "item"
    ad.url = "https://example.test/ad"
    ad.price = None
    ad.category_name = "cat"
    ad.body = ""
    ad.first_publication_date = None
    search = MagicMock(spec=Search)
    search.ads = [ad]
    search.total = 1
    search.max_pages = 1

    monkeypatch.setattr(
        "app.services.leboncoin.search_service.execute_search",
        lambda *_a, **_k: search,
    )

    prefetch = MagicMock()
    client.prefetch_users_for_ads = prefetch

    run_search_with_users(
        client,
        prefetch_users_parallel=True,
        prefetch_max_workers=3,
        text="bike",
        url=None,
        page=1,
        limit=5,
        limit_alu=0,
        search_in_title_only=False,
        category=None,
        sort=None,
        ad_type=None,
        owner_type=None,
        shippable=None,
        locations=None,
        extra_filters={},
    )

    prefetch.assert_called_once()
    assert prefetch.call_args.kwargs["parallel"] is True
    assert prefetch.call_args.kwargs["max_workers"] == 3
