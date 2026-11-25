
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.core.database import get_db
from app.models.feedback import UserFeedback
from app.models.paper import Paper, PaperStatus, UserPaper
from app.models.research_profile import ResearchProfile, ResearchKeyword
from app.schemas.recommendation import (
    RecommendationListResponse,
    RecommendedPaperResponse,
)
from app.services.feedback_service import FeedbackRecord
from app.services.recommendation_service import RecommendationService
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)

recommendation_service = RecommendationService()


@router.get(
    "",
    response_model=RecommendationListResponse,
)
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    user_id = current_user.id
    # 1. Load the researcher's profile.
    profile = await db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == user_id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Research profile not found.",
        )

    # 2. Load research keywords.
    keyword_result = await db.scalars(
        select(ResearchKeyword).where(
            ResearchKeyword.profile_id == profile.id
        )
    )

    researcher_keywords = list(keyword_result.all())

    included_keywords = [
        keyword for keyword in researcher_keywords
        if not keyword.is_excluded
    ]

    if not included_keywords:
        raise HTTPException(
            status_code=400,
            detail="Add at least one research interest first.",
        )

    # 3. Load candidate papers.
    # Include papers that are new or not yet associated
    # with this user. Exclude saved, read, and dismissed papers.
    paper_result = await db.scalars(
        select(Paper)
        .outerjoin(
            UserPaper,
            and_(
                UserPaper.paper_id == Paper.id,
                UserPaper.user_id == user_id,
            ),
        )
        .where(
            or_(
                UserPaper.id.is_(None),
                UserPaper.status == PaperStatus.NEW,
            )
        )
        .limit(500)
    )

    papers = list(paper_result.all())

    if not papers:
        return RecommendationListResponse(
            total=0,
            recommendations=[],
        )

    # 4. Load feedback history.
    feedback_result = await db.scalars(
        select(UserFeedback).where(
            UserFeedback.user_id == user_id
        )
    )

    feedback_history = [
        FeedbackRecord(
            matched_interest=feedback.matched_interest,
            feedback_type=(
                feedback.feedback_type.value
                if hasattr(feedback.feedback_type, "value")
                else str(feedback.feedback_type)
            ),
        )
        for feedback in feedback_result.all()
        if feedback.matched_interest
    ]

    # 5. Run ranking outside the async event loop.
    ranked = await run_in_threadpool(
        recommendation_service.rank,
        papers,
        researcher_keywords,
        feedback_history,
    )

    # 6. Convert ranked results into API responses.
    recommendations = [
        RecommendedPaperResponse(
            id=item.paper.id,
            title=item.paper.title,
            abstract=item.paper.abstract,
            doi=item.paper.doi,
            publication_date=item.paper.publication_date,
            authors=item.paper.authors or [],
            venue=item.paper.venue,
            citation_count=item.paper.citation_count,
            final_score=item.final_score,
            semantic_score=item.semantic_score,
            keyword_score=item.keyword_score,
            recency_score=item.recency_score,
            feedback_score=item.feedback_score,
            matched_keywords=item.matched_keywords,
            matched_interest=item.matched_interest,
        )
        for item in ranked[:limit]
    ]

    return RecommendationListResponse(
        total=len(recommendations),
        recommendations=recommendations,
    )
