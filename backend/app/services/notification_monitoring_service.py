
import asyncio
import logging
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.research_profile import ResearchProfile, ResearchKeyword
from app.models.paper import UserPaper
from app.models.notification import Notification

from app.services.research_pipeline_service import ResearchPipelineService
from app.services.recommendation_service import RecommendationService
from app.services.email_service import EmailNotificationService


logger = logging.getLogger(__name__)

DEFAULT_NOTIFICATION_THRESHOLD = 0.55


@dataclass
class MonitoringResult:
    discovered_count: int = 0
    inserted_count: int = 0
    updated_count: int = 0
    new_papers_count: int = 0
    notifications_created: int = 0
    email_sent: bool = False
    message: str = ""


class NotificationMonitoringService:

    def __init__(self):
        self.pipeline_service = ResearchPipelineService()
        self.recommendation_service = RecommendationService()

    async def monitor_user(
        self,
        db: AsyncSession,
        user: User,
        limit_per_source: int = 25,
    ) -> MonitoringResult:

        result = MonitoringResult()

        try:
            # 1. Load the researcher's profile.
            profile = await db.scalar(
                select(ResearchProfile).where(
                    ResearchProfile.user_id == user.id
                )
            )

            if profile is None:
                result.message = "Research profile not found."
                return result

            # 2. Load research keywords.
            keyword_result = await db.scalars(
                select(ResearchKeyword).where(
                    ResearchKeyword.profile_id == profile.id
                )
            )

            researcher_keywords = list(keyword_result.all())

            included_keywords = [
                item.keyword.strip()
                for item in researcher_keywords
                if not item.is_excluded and item.keyword.strip()
            ]

            if not included_keywords:
                result.message = "No active research interests."
                return result

            # 3. Discover and store new papers.
            pipeline_result = (
                await self.pipeline_service.discover_and_store(
                    keywords=included_keywords,
                    db=db,
                    user_id=user.id,
                    limit_per_source=limit_per_source,
                )
            )

            new_papers = pipeline_result.newly_associated_papers

            result.discovered_count = pipeline_result.discovered_count
            result.inserted_count = pipeline_result.inserted_count
            result.updated_count = pipeline_result.updated_count
            result.new_papers_count = len(new_papers)

            # 4. Score new papers.
            recommendations = self.recommendation_service.rank(
                papers=new_papers,
                researcher_keywords=researcher_keywords,
                feedback_history=[],
            )

            notifications_to_email = []
            created_notifications = []

            # 5. Create notifications for qualifying papers.
            for recommendation in recommendations:

                paper = recommendation.paper
                relevance_score = recommendation.relevance_score

                # Save the research relevance score.
                user_paper = await db.scalar(
                    select(UserPaper).where(
                        UserPaper.user_id == user.id,
                        UserPaper.paper_id == paper.id,
                    )
                )

                if user_paper:
                    user_paper.relevance_score = relevance_score

                if relevance_score < DEFAULT_NOTIFICATION_THRESHOLD:
                    continue

                # Prevent duplicate notifications.
                existing_notification = await db.scalar(
                    select(Notification).where(
                        Notification.user_id == user.id,
                        Notification.paper_id == paper.id,
                    )
                )

                if existing_notification is not None:
                    continue

                notification = Notification(
                    user_id=user.id,
                    paper_id=paper.id,
                    title="New highly relevant research paper",
                    message=(
                        f'"{paper.title}" matches your research interests '
                        f"with a relevance score of {relevance_score:.1%}."
                    ),
                    relevance_score=relevance_score,
                )

                db.add(notification)
                created_notifications.append(notification)

                notifications_to_email.append({
                    "title": paper.title,
                    "relevance_score": relevance_score,
                    "doi": paper.doi,
                    "abstract": paper.abstract,
                })

            # 6. Commit papers and in-app notifications first.
            await db.commit()

            result.notifications_created = len(created_notifications)

            # 7. Send email without blocking the async event loop.
            if notifications_to_email:

                try:
                    email_sent = await asyncio.to_thread(
                        EmailNotificationService.send_paper_alert,
                        recipient_email=user.email,
                        recipient_name=user.full_name,
                        papers=notifications_to_email,
                    )

                    if email_sent:
                        for notification in created_notifications:
                            notification.email_sent = True

                        await db.commit()
                        result.email_sent = True

                except Exception:
                    logger.exception(
                        "Automatic email notification failed for user %s",
                        user.id,
                    )
                    await db.rollback()

            result.message = "Monitoring completed successfully."
            return result

        except Exception:
            await db.rollback()

            logger.exception(
                "Monitoring failed for user %s",
                user.id,
            )

            raise
