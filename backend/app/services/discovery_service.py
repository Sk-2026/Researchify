
from app.integrations.openalex import OpenAlexClient
from app.integrations.semantic_scholar import SemanticScholarClient


class DiscoveryService:

    def __init__(self):
        self.openalex = OpenAlexClient()
        self.semantic_scholar = SemanticScholarClient()

    async def discover(
        self,
        keywords: list[str],
        limit_per_source: int = 25,
        from_date: str | None = None,
        to_date: str | None = None,
    ):

        discovered_papers = []

        for keyword in keywords:

            openalex_results = await self.openalex.search(
                query=keyword,
                from_date=from_date,
                to_date=to_date,
                limit=limit_per_source,
            )

            semantic_results = await self.semantic_scholar.search(
                query=keyword,
                limit=limit_per_source,
            )

            discovered_papers.extend(openalex_results)
            discovered_papers.extend(semantic_results)

        return discovered_papers
