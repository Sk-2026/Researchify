
import asyncio
import logging

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.research_profile import ResearchProfile
from app.services.notification_monitoring_service import (
    NotificationMonitoringService,
)


# Run monitoring every 30 minutes.
MONITORING_INTERVAL_SECONDS = 30 * 60

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)

monitoring_service = NotificationMonitoringService()


async def get_active_researcher_ids():
    """Return IDs of active users who have research profiles."""

    async with AsyncSessionLocal() as db:
        result = await db.scalars(
            select(User.id)
            .join(
                ResearchProfile,
                ResearchProfile.user_id == User.id,
            )
            .where(User.is_active.is_(True))
        )

        return list(result.all())


async def monitor_all_researchers():
    """Run discovery and notification monitoring for every researcher."""

    researcher_ids = await get_active_researcher_ids()

    logger.info(
        "Starting monitoring cycle for %s researcher(s).",
        len(researcher_ids),
    )

    for user_id in researcher_ids:
        try:
            async with AsyncSessionLocal() as db:

                user = await db.get(User, user_id)

                if user is None or not user.is_active:
                    continue

                result = await monitoring_service.monitor_user(
                    db=db,
                    user=user,
                    limit_per_source=25,
                )

                logger.info(
                    "Monitoring completed for user %s: "
                    "discovered=%s, new_papers=%s, notifications=%s, "
                    "email_sent=%s, message=%s",
                    user_id,
                    result.discovered_count,
                    result.new_papers_count,
                    result.notifications_created,
                    result.email_sent,
                    result.message,
                )

        except Exception:
            logger.exception(
                "Monitoring failed for user %s. Continuing with next user.",
                user_id,
            )

    logger.info("Monitoring cycle finished.")


async def main():
    logger.info("ZealWithin automatic monitoring worker started.")

    while True:
        try:
            await monitor_all_researchers()

        except Exception:
            logger.exception("Monitoring cycle failed.")

        logger.info(
            "Next monitoring cycle will start in %s minutes.",
            MONITORING_INTERVAL_SECONDS // 60,
        )

        await asyncio.sleep(MONITORING_INTERVAL_SECONDS)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("ZealWithin monitoring worker stopped.")
