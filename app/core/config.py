from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LBC_API_", env_file=".env", extra="ignore")

    host: str = "0.0.0.0"
    port: int = 8000
    proxy_url: str | None = None
    #: Concurrent isolated Leboncoin sessions (1 = serial; 3-6 typical)
    client_pool_size: int = 4
    #: Optional URL shown in OpenAPI Contact (e.g. repo or support page)
    docs_contact_url: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
