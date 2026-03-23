from __future__ import annotations

from pydantic import BaseModel


class UserOut(BaseModel):
    id: str
    name: str
    account_type: str
    location: str | None = None


class AdOut(BaseModel):
    id: int | None
    subject: str
    url: str
    price: float | None
    category_name: str | None
    body: str
    first_publication_date: str | None
    owner_user_id: str | None = None
    user: UserOut | None = None


class SearchMeta(BaseModel):
    total: int | None
    max_pages: int | None


class SearchResponse(BaseModel):
    meta: SearchMeta
    ads: list[AdOut]
