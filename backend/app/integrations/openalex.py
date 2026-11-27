
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

    def _build_params(self, extra_params=None):
        params = {}

        if self.api_key:
            params["api_key"] = self.api_key

        if self.mailto:
            params["mailto"] = self.mailto

        if extra_params:
            params.update(extra_params)

        return params

    def _to_paper_record(self, item: dict) -> PaperRecord | None:
        if not item or not item.get("id"):
            return None

        authors = [
            authorship.get("author", {}).get("display_name")
            for authorship in item.get("authorships", [])
            if authorship.get("author", {}).get("display_name")
        ]

        location = item.get("primary_location") or {}
        venue = (location.get("source") or {}).get("display_name")

        publication_date = None

        if item.get("publication_date"):
            try:
                publication_date = date.fromisoformat(
                    item["publication_date"]
                )
            except ValueError:
                publication_date = None

        keywords = [
            keyword.get("display_name")
            for keyword in item.get("keywords", [])
            if keyword.get("display_name")
        ]

        return PaperRecord(
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
            keywords=keywords,
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
                "cited_by_count,abstract_inverted_index,keywords"
            ),
        }

        filters = []

        if from_date:
            filters.append(f"from_publication_date:{from_date}")

        if to_date:
            filters.append(f"to_publication_date:{to_date}")

        if filters:
            params["filter"] = ",".join(filters)

        params = self._build_params(params)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                self.BASE_URL,
                params=params,
            )
            response.raise_for_status()

        results = response.json().get("results", [])

        papers = []

        for item in results:
            paper = self._to_paper_record(item)

            if paper and paper.title:
                papers.append(paper)

        return papers

    async def find_by_doi(self, doi: str) -> PaperRecord | None:
        normalized_doi = doi.strip()

        normalized_doi = normalized_doi.removeprefix(
            "https://doi.org/"
        )
        normalized_doi = normalized_doi.removeprefix(
            "http://doi.org/"
        )
        normalized_doi = normalized_doi.removeprefix(
            "doi:"
        )
        normalized_doi = normalized_doi.strip()

        if not normalized_doi:
            return None

        params = {
            "filter": f"doi:https://doi.org/{normalized_doi}",
            "per_page": 1,
            "select": (
                "id,doi,title,publication_date,"
                "authorships,primary_location,"
                "cited_by_count,abstract_inverted_index,keywords"
            ),
        }

        params = self._build_params(params)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                self.BASE_URL,
                params=params,
            )
            response.raise_for_status()

        results = response.json().get("results", [])

        if not results:
            return None

        return self._to_paper_record(results[0])
