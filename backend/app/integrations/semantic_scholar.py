
import os
import asyncio
import httpx

from datetime import date
from app.integrations.base import PaperRecord


class SemanticScholarClient:

    BASE_URL = (
        "https://api.semanticscholar.org/graph/v1/paper/search"
    )

    def __init__(self):
        self.api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

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

            for attempt in range(max_retries + 1):

                response = await client.get(
                    self.BASE_URL,
                    params=params,
                    headers=headers,
                )

                if response.status_code == 429:

                    if attempt == max_retries:
                        raise RuntimeError(
                            "Semantic Scholar rate limit exceeded. "
                            "Try again later or configure an API key."
                        )

                    retry_after = response.headers.get("Retry-After")

                    try:
                        delay = float(retry_after) if retry_after else 2 ** (attempt + 1)
                    except ValueError:
                        delay = 2 ** (attempt + 1)

                    delay = min(delay, 60)

                    print(
                        f"Semantic Scholar rate limited. "
                        f"Retrying in {delay} seconds..."
                    )

                    await asyncio.sleep(delay)
                    continue

                response.raise_for_status()
                break

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
