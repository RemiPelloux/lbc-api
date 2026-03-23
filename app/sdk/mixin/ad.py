from __future__ import annotations

from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor

from ..model import Ad


class AdMixin:
    def get_ads_parallel(
        self,
        ad_ids: Sequence[str | int],
        *,
        max_workers: int = 4,
    ) -> list[Ad]:
        """
        Fetch multiple classified ads concurrently while keeping sessions isolated.

        Order of the returned list matches ``ad_ids``. Each fetch uses ``fork()`` to avoid
        sharing a non-thread-safe session across workers.
        """
        ids = list(ad_ids)
        if not ids:
            return []

        workers = max(1, min(max_workers, len(ids)))

        def _fetch_one(index: int, raw_id: str | int) -> tuple[int, Ad]:
            return index, self.fork().get_ad(raw_id)

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(_fetch_one, i, aid) for i, aid in enumerate(ids)]
            indexed: list[tuple[int, Ad]] = [future.result() for future in futures]

        indexed.sort(key=lambda item: item[0])
        return [ad for _, ad in indexed]

    def get_ad(self, ad_id: str | int) -> Ad:
        """
        Retrieve detailed information about a classified ad using its ID.

        This method fetches the full content of an ad, including its description,
        pricing, location, and other relevant metadata made
        available through the public Leboncoin ad API.

        Args:
            ad_id (Union[str, int]): The unique identifier of the ad on Leboncoin. Can be found in the ad URL.

        Returns:
            Ad: An `Ad` object containing the parsed ad information.
        """
        body = self._fetch(
            method="GET", url=f"https://api.leboncoin.fr/api/adfinder/v1/classified/{ad_id}"
        )
        return Ad._build(raw=body, client=self)
