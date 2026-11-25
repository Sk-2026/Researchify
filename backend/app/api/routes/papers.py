
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.paper import Paper, UserPaper, PaperStatus
from app.models.user import User
from app.schemas.paper import (
    PaperStatusUpdateRequest,
    PaperStatusResponse,
)

router = APIRouter(prefix="/papers", tags=["Papers"])


@router.put("/{paper_id}/status", response_model=PaperStatusResponse)
async def update_paper_status(
    paper_id: UUID,
    payload: PaperStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify that the paper exists.
    paper = await db.scalar(
        select(Paper).where(Paper.id == paper_id)
    )

    if paper is None:
        raise HTTPException(
            status_code=404,
            detail="Paper not found.",
        )

    # Find this paper's association with the authenticated user.
    user_paper = await db.scalar(
        select(UserPaper).where(
            UserPaper.user_id == current_user.id,
            UserPaper.paper_id == paper_id,
        )
    )

    if user_paper is None:
        user_paper = UserPaper(
            user_id=current_user.id,
            paper_id=paper_id,
            status=payload.status,
        )
        db.add(user_paper)
    else:
        user_paper.status = payload.status

    await db.commit()

    return PaperStatusResponse(
        paper_id=str(paper_id),
        status=user_paper.status,
    )
