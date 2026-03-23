from __future__ import annotations

from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TYPE_CHECKING

from ..exceptions import NotFoundError
from ..model import User

if TYPE_CHECKING:
    from ..model import Ad


class UserMixin:
    def prefetch_users_for_ads(
        self,
        ads: Iterable[Ad],
        *,
        parallel: bool = False,
        max_workers: int = 4,
    ) -> None:
        """
        Resolve seller profiles for the given ads without N+1 duplicate fetches.

        Collects unique owner IDs from ads, fetches each user once, then attaches ``User``
        instances so ``ad.user`` does not trigger additional HTTP calls.

        Args:
            ads: Ads typically returned from ``search``; only entries with ``_user_id`` are
                considered.
            parallel: When True, fetches distinct users concurrently (each worker uses
                ``fork()`` so sessions stay isolated). When False, fetches sequentially.
            max_workers: Upper bound on concurrent user fetches when ``parallel`` is True.

        Note:
            Parallel mode creates one new client per distinct user (via ``fork()``) and may
            increase burst traffic; respect Leboncoin rate limits and Datadome guidance.
        """
        unique_ids: list[str] = []
        seen: set[str] = set()
        for ad in ads:
            uid = ad._user_id
            if not uid or uid in seen:
                continue
            seen.add(uid)
            unique_ids.append(uid)
        if not unique_ids:
            return

        users_by_id: dict[str, User]
        if parallel:

            def _load(uid: str) -> tuple[str, User]:
                worker = self.fork()
                return uid, worker.get_user(uid)

            users_by_id = {}
            with ThreadPoolExecutor(max_workers=max(1, max_workers)) as executor:
                futures = [executor.submit(_load, uid) for uid in unique_ids]
                for future in as_completed(futures):
                    uid, user = future.result()
                    users_by_id[uid] = user
        else:
            users_by_id = {uid: self.get_user(uid) for uid in unique_ids}

        for ad in ads:
            uid = ad._user_id
            if uid and uid in users_by_id:
                ad._user = users_by_id[uid]

    def get_user(self, user_id: str) -> User:
        """
        Retrieve information about a user based on their user ID.

        This method fetches detailed user data such as their profile, professional status,
        and other relevant metadata available through the public user API.

        Args:
            user_id (str): The unique identifier of the user on Leboncoin. Usually found in the url (e.g 57f99bb6-0446-4b82-b05d-a44ea7bcd2cc).

        Returns:
            User: A `User` object containing the parsed user information.
        """
        user_data = self._fetch(
            method="GET", url=f"https://api.leboncoin.fr/api/user-card/v2/{user_id}/infos"
        )

        pro_data = None
        if user_data.get("account_type") == "pro":
            try:
                pro_data = self._fetch(
                    method="GET",
                    url=f"https://api.leboncoin.fr/api/onlinestores/v2/users/{user_id}?fields=all",
                )
            except NotFoundError:
                pass  # Some professional users may not have a Leboncoin page.
        return User._build(user_data=user_data, pro_data=pro_data)
