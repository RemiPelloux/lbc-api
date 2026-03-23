from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from app.sdk import Client
from app.sdk.mixin.user import UserMixin
from app.sdk.model.user import User


def _minimal_user(user_id: str) -> User:
    payload = {
        "user_id": user_id,
        "name": "seller",
        "registered_at": "",
        "location": "",
        "feedback": {},
        "profile_picture": {},
        "reply": {},
        "presence": {},
        "badges": [],
        "total_ads": 0,
        "store_id": 0,
        "account_type": "private",
        "description": "",
    }
    return User._build(user_data=payload, pro_data=None)


class _UserProbe(UserMixin):
    def __init__(self) -> None:
        self.calls: list[str] = []

    def fork(self) -> _UserProbe:
        return self

    def get_user(self, user_id: str) -> User:
        self.calls.append(user_id)
        return _minimal_user(user_id)


def test_prefetch_users_deduplicates_sequential_mode() -> None:
    probe = _UserProbe()

    class _Ad:
        def __init__(self, uid: str) -> None:
            self._user_id = uid
            self._user = None

    ads = [_Ad("a"), _Ad("b"), _Ad("a")]
    probe.prefetch_users_for_ads(ads, parallel=False)

    assert probe.calls == ["a", "b"]
    assert ads[0]._user is not None and ads[0]._user.id == "a"
    assert ads[1]._user is not None and ads[1]._user.id == "b"
    assert ads[2]._user is ads[0]._user


def test_prefetch_users_parallel_uses_forked_workers(monkeypatch: pytest.MonkeyPatch) -> None:
    base = Client()
    workers: list[int] = []
    calls: list[str] = []

    def _tracking_fork(self: Client) -> MagicMock:
        forked = MagicMock(spec=Client)

        def _gu(uid: str) -> User:
            calls.append(uid)
            return _minimal_user(uid)

        forked.get_user = _gu
        workers.append(id(forked))
        return forked

    monkeypatch.setattr(Client, "fork", _tracking_fork)

    class _Ad:
        def __init__(self, uid: str) -> None:
            self._user_id = uid
            self._user = None

    ads = [_Ad("x"), _Ad("y")]
    base.prefetch_users_for_ads(ads, parallel=True, max_workers=4)

    assert sorted(calls) == ["x", "y"]
    assert len(workers) == 2
    assert workers[0] != workers[1]


def test_get_ads_parallel_preserves_order(monkeypatch: pytest.MonkeyPatch) -> None:
    base = Client()

    def _fake_fork(self: Client) -> Client:
        return self

    def _fake_get_ad(self: Client, ad_id: int | str) -> MagicMock:
        ad = MagicMock()
        ad.id = int(ad_id)
        return ad

    monkeypatch.setattr(Client, "fork", _fake_fork)
    monkeypatch.setattr(Client, "get_ad", _fake_get_ad)

    ads = base.get_ads_parallel([3, 1, 2], max_workers=3)
    assert [ad.id for ad in ads] == [3, 1, 2]


def test_client_fork_returns_independent_instance() -> None:
    parent = Client()
    child = parent.fork()
    assert child is not parent
    assert child.session is not parent.session


def test_fork_skips_second_homepage_warmup(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.sdk.mixin.session import SessionMixin

    calls: list[str] = []

    real_init = SessionMixin._init_session

    def _track_init(self: SessionMixin, *a: object, **k: object) -> object:
        calls.append("init_session")
        return real_init(self, *a, **k)

    monkeypatch.setattr(SessionMixin, "_init_session", _track_init)
    parent = Client()
    assert calls == ["init_session"]
    child = parent.fork()
    assert calls == ["init_session"]
    assert child.session is not parent.session
