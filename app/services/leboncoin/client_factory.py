from __future__ import annotations

from urllib.parse import urlparse

from app.sdk.client import Client
from app.sdk.model.proxy import Proxy


def build_lbc_client(proxy_url: str | None) -> Client:
    if not proxy_url:
        return Client()
    parsed = urlparse(proxy_url)
    if not parsed.hostname:
        raise ValueError("Proxy URL must include a host")
    port = parsed.port
    if port is None:
        port = 443 if parsed.scheme in ("https", "") else 80
    scheme = parsed.scheme or "http"
    proxy = Proxy(
        host=parsed.hostname,
        port=port,
        username=parsed.username,
        password=parsed.password,
        scheme=scheme,
    )
    return Client(proxy=proxy)
