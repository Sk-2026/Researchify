
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.feedback import UserFeedback
from app.models.paper import Paper
from app.models.user import User
from app.schemas.feedback import (
    FeedbackCreateRequest,
    FeedbackResponse,
)

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post(
    "/{paper_id}",
    response_model=FeedbackResponse,
)
async def submit_feedback(
    paper_id: UUID,
    payload: FeedbackCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Get the authenticated user's ID from the JWT.
    user_id = current_user.id

    # Verify that the paper exists.
    paper = await db.scalar(
        select(Paper).where(Paper.id == paper_id)
    )

    if paper is None:
        raise HTTPException(
            status_code=404,
            detail="Paper not found.",
        )

    # Check whether feedback already exists.
    feedback = await db.scalar(
        select(UserFeedback).where(
            UserFeedback.user_id == user_id,
            UserFeedback.paper_id == paper_id,
        )
    )

    if feedback is None:
        feedback = UserFeedback(
            user_id=user_id,
            paper_id=paper_id,
            feedback_type=payload.feedback_type,
            matched_interest=payload.matched_interest,
        )
        db.add(feedback)
    else:
        feedback.feedback_type = payload.feedback_type
        feedback.matched_interest = payload.matched_interest

    await db.commit()
    await db.refresh(feedback)

    return feedback
