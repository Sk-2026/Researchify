
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

from app.services.notification_monitoring_service import (
    NotificationMonitoringService,
)

from app.schemas.discovery import DiscoveryRunResponse


router = APIRouter(
    prefix="/discovery",
    tags=["Paper Discovery"],
)

monitoring_service = NotificationMonitoringService()


@router.post(
    "/run",
    response_model=DiscoveryRunResponse,
)
async def run_discovery(
    limit_per_source: int = Query(default=25, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await monitoring_service.monitor_user(
            db=db,
            user=current_user,
            limit_per_source=limit_per_source,
        )

        if result.message == "Research profile not found.":
            raise HTTPException(
                status_code=404,
                detail=result.message,
            )

        if result.message == "No active research interests.":
            raise HTTPException(
                status_code=400,
                detail="Add at least one research interest first.",
            )

        return DiscoveryRunResponse(
            message=(
                f"{result.message} "
                f"{result.new_papers_count} new researcher-paper "
                f"associations found; "
                f"{result.notifications_created} qualifying notifications "
                f"created; "
                f"email {'sent' if result.email_sent else 'not sent'}."
            ),
            discovered_count=result.discovered_count,
            inserted_count=result.inserted_count,
            updated_count=result.updated_count,
            sources_added=0,
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Paper discovery failed. Check backend logs.",
        )
