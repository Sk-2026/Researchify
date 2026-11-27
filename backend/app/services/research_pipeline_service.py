
import uuid
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.paper import Paper
from app.services.discovery_service import DiscoveryService
from app.services.paper_ingestion_service import PaperIngestionService


@dataclass
class ResearchPipelineResult:
    discovered_count: int
    inserted_count: int
    updated_count: int
    sources_added: int
    newly_associated_papers: list[Paper] = field(default_factory=list)


class ResearchPipelineService:

    def __init__(self):
        self.discovery_service = DiscoveryService()
        self.ingestion_service = PaperIngestionService()

    async def discover_and_store(
        self,
        keywords: list[str],
        db: AsyncSession,
        user_id: uuid.UUID,
        limit_per_source: int = 25,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> ResearchPipelineResult:

        records = await self.discovery_service.discover(
            keywords=keywords,
            limit_per_source=limit_per_source,
            from_date=from_date,
            to_date=to_date,
        )

        # Remove duplicate records from discovery providers.
        unique_records = {}

        for record in records:
            key = (record.source, record.source_id)
            unique_records[key] = record

        records = list(unique_records.values())

        # Store papers and identify first-time user associations.
        ingestion = await self.ingestion_service.ingest(
            records=records,
            db=db,
            user_id=user_id,
        )

        return ResearchPipelineResult(
            discovered_count=len(records),
            inserted_count=ingestion.inserted,
            updated_count=ingestion.updated,
            sources_added=ingestion.sources_added,
            newly_associated_papers=ingestion.newly_associated_papers,
        )
