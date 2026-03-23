from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _no_real_session(monkeypatch: pytest.MonkeyPatch) -> None:
    """Prevent outbound HTTP when tests construct a real ``Client``."""

    def _fake_init_session(self, proxy=None, impersonate=None, request_verify=True):
        class _Resp:
            ok = True

            def json(self):
                return {}

        class _Sess:
            def __init__(self) -> None:
                self.proxies: dict[str, str] = {}

            def get(self, *_a, **_k):
                return _Resp()

            def request(self, *_a, **_k):
                return _Resp()

        return _Sess()

    monkeypatch.setattr(
        "app.sdk.mixin.session.SessionMixin._init_session",
        _fake_init_session,
    )
