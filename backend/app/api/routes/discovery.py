
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.research_profile import ResearchProfile, ResearchKeyword
from app.services.research_pipeline_service import ResearchPipelineService
from app.schemas.discovery import DiscoveryRunResponse


router = APIRouter(
    prefix="/discovery",
    tags=["Paper Discovery"],
)

pipeline_service = ResearchPipelineService()


@router.post(
    "/run",
    response_model=DiscoveryRunResponse,
)
async def run_discovery(
    limit_per_source: int = Query(default=25, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 1. Load the authenticated researcher's profile.
    profile = await db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == current_user.id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Research profile not found.",
        )

    # 2. Load the researcher's keywords.
    keyword_result = await db.scalars(
        select(ResearchKeyword).where(
            ResearchKeyword.profile_id == profile.id
        )
    )

    researcher_keywords = list(keyword_result.all())

    included_keywords = [
        keyword.keyword.strip()
        for keyword in researcher_keywords
        if not keyword.is_excluded and keyword.keyword.strip()
    ]

    if not included_keywords:
        raise HTTPException(
            status_code=400,
            detail="Add at least one research interest first.",
        )

    # 3. Run discovery and store the papers.
    try:
        result = await pipeline_service.discover_and_store(
            keywords=included_keywords,
            db=db,
            user_id=current_user.id,
            limit_per_source=limit_per_source,
        )

        await db.commit()

    except Exception:
        await db.rollback()
        raise

    # 4. Return discovery statistics.
    return DiscoveryRunResponse(
        message="Research paper discovery completed successfully.",
        discovered_count=result.discovered_count,
        inserted_count=result.inserted_count,
        updated_count=result.updated_count,
        sources_added=result.sources_added,
    )
