from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _no_real_session(
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Prevent outbound HTTP unless the test is marked ``@pytest.mark.real_lbc``."""

    if request.node.get_closest_marker("real_lbc"):
        return

    def _fake_init_session(self, proxy=None, impersonate=None, request_verify=True):
        class _Resp:
            ok = True

            def json(self):
                return {}

        class _Sess:
            def __init__(self) -> None:
                self.proxies: dict[str, str] = {}
                # Minimal shape expected by ``Client.fork()`` / ``_fork_session_from_parent``
                self.headers: dict[str, str] = {"User-Agent": "LBC;mock"}
                self.cookies: dict[str, str] = {}
                self._lbc_impersonate = "firefox"

            def get(self, *_a, **_k):
                return _Resp()

            def request(self, *_a, **_k):
                return _Resp()

        return _Sess()

    monkeypatch.setattr(
        "app.sdk.mixin.session.SessionMixin._init_session",
        _fake_init_session,
    )
