
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.notification import Notification


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get("/")
async def get_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.scalars(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
    )

    notifications = list(result.all())

    return {
        "total": len(notifications),
        "unread_count": sum(
            1 for notification in notifications
            if not notification.is_read
        ),
        "notifications": [
            {
                "id": str(notification.id),
                "paper_id": str(notification.paper_id),
                "title": notification.title,
                "message": notification.message,
                "relevance_score": notification.relevance_score,
                "is_read": notification.is_read,
                "email_sent": notification.email_sent,
                "created_at": notification.created_at.isoformat(),
            }
            for notification in notifications
        ],
    }


@router.patch("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    notification = await db.scalar(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )

    if notification is None:
        raise HTTPException(
            status_code=404,
            detail="Notification not found.",
        )

    notification.is_read = True

    await db.commit()

    return {
        "message": "Notification marked as read.",
        "notification_id": str(notification.id),
    }
