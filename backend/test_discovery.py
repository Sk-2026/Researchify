
import asyncio

from app.integrations.openalex import OpenAlexClient
from app.integrations.semantic_scholar import SemanticScholarClient

from dotenv import load_dotenv
load_dotenv()
import os

print(
    "Semantic Scholar API key loaded:",
    bool(os.getenv("SEMANTIC_SCHOLAR_API_KEY"))
)
async def main():

    keyword = "object detection"

    openalex = OpenAlexClient()
    semantic = SemanticScholarClient()

    print("\n--- OpenAlex ---")

    try:
        papers = await openalex.search(keyword, limit=5)

        for paper in papers:
            print("Title:", paper.title)
            print("DOI:", paper.doi)
            print("Abstract:", (paper.abstract or "")[:150])
            print()

    except Exception as error:
        print("OpenAlex error:", error)

    print("\n--- Semantic Scholar ---")

    try:
        papers = await semantic.search(keyword, limit=5)

        for paper in papers:
            print("Title:", paper.title)
            print("DOI:", paper.doi)
            print("Abstract:", (paper.abstract or "")[:150])
            print()

    except Exception as error:
        print("Semantic Scholar error:", error)

if __name__ == "__main__":
    asyncio.run(main())
