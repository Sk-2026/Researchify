
import re

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.dependencies import get_current_user
from app.integrations.openalex import OpenAlexClient


router = APIRouter(
    prefix="/profile",
    tags=["Paper Import"],
)


class PaperLookupRequest(BaseModel):
    query: str = Field(min_length=3, max_length=500)


class PaperCandidate(BaseModel):
    title: str
    doi: str | None = None
    abstract: str | None = None
    authors: list[str] = []
    publication_date: str | None = None
    venue: str | None = None
    suggested_keywords: list[str] = []


def is_doi(value: str) -> bool:
    return bool(
        re.match(
            r"^(https?://(dx\.)?doi\.org/|doi:)?10\.\d{4,9}/\S+$",
            value.strip(),
            re.IGNORECASE,
        )
    )


def normalize_doi(value: str) -> str:
    value = value.strip()
    value = re.sub(
        r"^https?://(dx\.)?doi\.org/",
        "",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(r"^doi:", "", value, flags=re.IGNORECASE)
    return value.strip()


@router.post("/suggest-keyword")
async def suggest_keywords(
    request: PaperLookupRequest,
    current_user=Depends(get_current_user),
):
    query = request.query.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Please enter a paper title or DOI.",
        )

    client = OpenAlexClient()

    try:
        if is_doi(query):
            paper = await client.find_by_doi(normalize_doi(query))
            papers = [paper] if paper else []
        else:
            papers = await client.search(query=query, limit=5)

    except httpx.HTTPError:
        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve paper information from OpenAlex.",
        )

    if not papers:
        raise HTTPException(
            status_code=404,
            detail="No matching paper was found. Check the title or DOI.",
        )

    candidates = []

    for paper in papers:
        if not paper:
            continue

        candidates.append(
            PaperCandidate(
                title=paper.title,
                doi=paper.doi,
                abstract=paper.abstract,
                authors=paper.authors or [],
                publication_date=(
                    paper.publication_date.isoformat()
                    if paper.publication_date
                    else None
                ),
                venue=paper.venue,
                suggested_keywords=paper.keywords or [],
            )
        )

    return {
        "count": len(candidates),
        "candidates": candidates,
        "message": (
            "Review the matching paper and its suggested keywords. "
            "No keywords have been added to your profile."
        ),
    }
