
import os
import httpx

from datetime import date

from app.integrations.base import PaperRecord


class OpenAlexClient:

    BASE_URL = "https://api.openalex.org/works"

    def __init__(self):
        self.api_key = os.getenv("OPENALEX_API_KEY")
        self.mailto = os.getenv("OPENALEX_MAILTO")

    @staticmethod
    def reconstruct_abstract(inverted_index):
        if not inverted_index:
            return None

        words = {}

        for word, positions in inverted_index.items():
            for position in positions:
                words[position] = word

        return " ".join(
            words[position]
            for position in sorted(words)
        )

    async def search(
        self,
        query: str,
        from_date: str | None = None,
        to_date: str | None = None,
        limit: int = 25,
    ) -> list[PaperRecord]:

        params = {
            "search": query,
            "per_page": min(limit, 100),
            "select": (
                "id,doi,title,publication_date,"
                "authorships,primary_location,"
                "cited_by_count,abstract_inverted_index"
            ),
        }

        filters = []

        if from_date:
            filters.append(f"from_publication_date:{from_date}")

        if to_date:
            filters.append(f"to_publication_date:{to_date}")

        if filters:
            params["filter"] = ",".join(filters)

        if self.api_key:
            params["api_key"] = self.api_key

        if self.mailto:
            params["mailto"] = self.mailto

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                self.BASE_URL,
                params=params,
            )
            response.raise_for_status()

        results = response.json().get("results", [])

        papers = []

        for item in results:

            authors = [
                author.get("author", {}).get("display_name")
                for author in item.get("authorships", [])
                if author.get("author", {}).get("display_name")
            ]

            location = item.get("primary_location") or {}
            venue = (location.get("source") or {}).get(
                "display_name"
            )

            publication_date = None

            if item.get("publication_date"):
                publication_date = date.fromisoformat(
                    item["publication_date"]
                )

            paper = PaperRecord(
                source="openalex",
                source_id=item["id"].rsplit("/", 1)[-1],
                title=item.get("title") or "",
                doi=item.get("doi"),
                abstract=self.reconstruct_abstract(
                    item.get("abstract_inverted_index")
                ),
                publication_date=publication_date,
                authors=authors,
                venue=venue,
                citation_count=item.get("cited_by_count"),
                source_url=item.get("id"),
            )

            if paper.title:
                papers.append(paper)

        return papers
