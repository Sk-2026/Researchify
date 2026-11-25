
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.research_profile import ResearchProfile
from app.schemas.profile import (
    ResearchProfileCreateRequest,
    ResearchProfileResponse,
)
from uuid import UUID

from app.models.research_profile import ResearchKeyword
from app.schemas.profile import (
    ResearchKeywordCreateRequest,
    ResearchKeywordCreateResponse,
)

from app.schemas.profile import ResearchProfileUpdateRequest
router = APIRouter(
    prefix="/profile",
    tags=["Research Profile"],
)


@router.post(
    "",
    response_model=ResearchProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_profile(
    payload: ResearchProfileCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Check whether the researcher already has a profile.
    existing_profile = await db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == current_user.id
        )
    )

    if existing_profile:
        raise HTTPException(
            status_code=409,
            detail="Research profile already exists.",
        )

    profile = ResearchProfile(
        user_id=current_user.id,
        domain=payload.domain,
        description=payload.description,
        timezone=payload.timezone,
        digest_time=payload.digest_time,
    )

    db.add(profile)
    await db.commit()

    # Fetch the profile with its keywords loaded.
    result = await db.scalar(
        select(ResearchProfile)
        .options(selectinload(ResearchProfile.keywords))
        .where(ResearchProfile.id == profile.id)
    )

    return result


@router.get(
    "",
    response_model=ResearchProfileResponse,
)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await db.scalar(
        select(ResearchProfile)
        .options(selectinload(ResearchProfile.keywords))
        .where(ResearchProfile.user_id == current_user.id)
    )

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Research profile not found.",
        )

    return profile


@router.post(
    "/keywords",
    response_model=ResearchKeywordCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_keyword(
    payload: ResearchKeywordCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
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

    normalized_keyword = payload.keyword.strip()

    if not normalized_keyword:
        raise HTTPException(
            status_code=422,
            detail="Keyword cannot be empty.",
        )

    existing_keyword = await db.scalar(
        select(ResearchKeyword).where(
            ResearchKeyword.profile_id == profile.id,
            ResearchKeyword.keyword.ilike(normalized_keyword),
            ResearchKeyword.is_excluded == payload.is_excluded,
        )
    )

    if existing_keyword:
        raise HTTPException(
            status_code=409,
            detail="This keyword already exists.",
        )

    keyword = ResearchKeyword(
        profile_id=profile.id,
        keyword=normalized_keyword,
        category=payload.category,
        is_excluded=payload.is_excluded,
    )

    db.add(keyword)
    await db.commit()
    await db.refresh(keyword)

    return keyword


@router.delete(
    "/keywords/{keyword_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_keyword(
    keyword_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
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

    keyword = await db.scalar(
        select(ResearchKeyword).where(
            ResearchKeyword.id == keyword_id,
            ResearchKeyword.profile_id == profile.id,
        )
    )

    if keyword is None:
        raise HTTPException(
            status_code=404,
            detail="Keyword not found.",
        )

    await db.delete(keyword)
    await db.commit()


@router.put(
    "",
    response_model=ResearchProfileResponse,
)
async def update_profile(
    payload: ResearchProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await db.scalar(
        select(ResearchProfile)
        .options(selectinload(ResearchProfile.keywords))
        .where(ResearchProfile.user_id == current_user.id)
    )

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Research profile not found.",
        )

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.commit()

    await db.refresh(profile)

    return profile
