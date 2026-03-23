from __future__ import annotations

from app.schemas.responses import AdOut, SearchMeta, SearchResponse, UserOut
from app.sdk.model.ad import Ad
from app.sdk.model.search import Search
from app.sdk.model.user import User


def map_user_to_response(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        name=user.name,
        account_type=user.account_type,
        location=user.location,
    )


def map_ad_to_response(ad: Ad, *, include_user: bool) -> AdOut:
    user_out: UserOut | None = None
    if include_user and ad._user is not None:
        user_out = map_user_to_response(ad._user)
    return AdOut(
        id=ad.id,
        subject=ad.subject,
        url=ad.url,
        price=ad.price,
        category_name=ad.category_name,
        body=ad.body,
        first_publication_date=ad.first_publication_date,
        owner_user_id=ad._user_id,
        user=user_out,
    )


def map_search_to_response(result: Search, *, include_users: bool) -> SearchResponse:
    meta = SearchMeta(total=result.total, max_pages=result.max_pages)
    ads = [map_ad_to_response(ad, include_user=include_users) for ad in result.ads]
    return SearchResponse(meta=meta, ads=ads)
