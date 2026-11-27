
import os
import asyncio
import time
import httpx

from datetime import date, datetime, timezone
from email.utils import parsedate_to_datetime

from app.integrations.base import PaperRecord


class SemanticScholarClient:

    BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

    # Shared across all SemanticScholarClient instances in this process.
    _request_lock = asyncio.Lock()
    _last_request_time = 0.0
    _minimum_request_interval = 1.0

    def __init__(self):
        self.api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

    @classmethod
    async def _wait_for_rate_limit(cls):
        """
        Ensure requests from this process start at least one second apart.
        """
        async with cls._request_lock:
            now = time.monotonic()
            elapsed = now - cls._last_request_time

            if elapsed < cls._minimum_request_interval:
                await asyncio.sleep(
                    cls._minimum_request_interval - elapsed
                )

            cls._last_request_time = time.monotonic()

    @staticmethod
    def _get_retry_delay(retry_after: str | None, attempt: int) -> float:
        """
        Parse Retry-After as seconds or an HTTP date.
        Fall back to exponential backoff.
        """
        if retry_after:
            try:
                return min(max(float(retry_after), 1.0), 60.0)
            except ValueError:
                try:
                    retry_date = parsedate_to_datetime(retry_after)

                    if retry_date.tzinfo is None:
                        retry_date = retry_date.replace(
                            tzinfo=timezone.utc
                        )

                    delay = (
                        retry_date - datetime.now(timezone.utc)
                    ).total_seconds()

                    return min(max(delay, 1.0), 60.0)
                except (TypeError, ValueError, OverflowError):
                    pass

        return min(2 ** (attempt + 1), 60.0)

    async def search(
        self,
        query: str,
        limit: int = 25,
        max_retries: int = 3,
    ) -> list[PaperRecord]:

        params = {
            "query": query,
            "limit": min(limit, 1000),
            "fields": (
                "title,abstract,year,publicationDate,"
                "authors,venue,citationCount,externalIds,url"
            ),
        }

        headers = {}

        if self.api_key:
            headers["x-api-key"] = self.api_key

        async with httpx.AsyncClient(timeout=30.0) as client:

            response = None

            for attempt in range(max_retries + 1):

                # Enforce the one-request-per-second limit.
                await self._wait_for_rate_limit()

                response = await client.get(
                    self.BASE_URL,
                    params=params,
                    headers=headers,
                )

                if response.status_code == 429:

                    if attempt == max_retries:
                        raise RuntimeError(
                            "Semantic Scholar rate limit exceeded "
                            "after retries. Please try again later."
                        )

                    delay = self._get_retry_delay(
                        response.headers.get("Retry-After"),
                        attempt,
                    )

                    print(
                        "Semantic Scholar rate limited. "
                        f"Retrying in {delay:.1f} seconds..."
                    )

                    await asyncio.sleep(delay)
                    continue

                response.raise_for_status()
                break

            if response is None:
                raise RuntimeError(
                    "Semantic Scholar request failed without a response."
                )

            results = response.json().get("data", [])

        papers = []

        for item in results:

            external_ids = item.get("externalIds") or {}
            doi = external_ids.get("DOI")

            publication_date = None

            if item.get("publicationDate"):
                try:
                    publication_date = date.fromisoformat(
                        item["publicationDate"]
                    )
                except ValueError:
                    pass

            elif item.get("year"):
                publication_date = date(item["year"], 1, 1)

            authors = [
                author.get("name")
                for author in item.get("authors", [])
                if author.get("name")
            ]

            paper = PaperRecord(
                source="semantic_scholar",
                source_id=item["paperId"],
                title=item.get("title") or "",
                doi=doi,
                abstract=item.get("abstract"),
                publication_date=publication_date,
                authors=authors,
                venue=item.get("venue"),
                citation_count=item.get("citationCount"),
                source_url=item.get("url"),
            )

            if paper.title:
                papers.append(paper)

        return papers
