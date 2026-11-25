
import asyncio

from app.integrations.openalex import OpenAlexClient
from app.services.recency_service import RecencyScorer


async def main():

    client = OpenAlexClient()
    scorer = RecencyScorer()

    papers = await client.search(
        query="Object Detection",
        limit=10,
    )

    ranked = []

    for paper in papers:
        recency = scorer.score(paper.publication_date)

        ranked.append((paper, recency))

    ranked.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    print("\nRESEARCHIFY - RECENT RESEARCH PAPERS")
    print("=" * 65)

    for paper, score in ranked:

        print(f"\nTitle: {paper.title}")
        print(f"Publication date: {paper.publication_date}")
        print(f"Recency score: {score:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
