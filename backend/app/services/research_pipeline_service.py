
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.discovery_service import DiscoveryService
from app.services.paper_ingestion_service import PaperIngestionService

import uuid

@dataclass
class ResearchPipelineResult:
    discovered_count: int
    inserted_count: int
    updated_count: int
    sources_added: int


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
    )-> ResearchPipelineResult:

        # Step 1: Discover papers from academic providers.
        records = await self.discovery_service.discover(
            keywords=keywords,
            limit_per_source=limit_per_source,
            from_date=from_date,
            to_date=to_date,
        )

        # Step 2: Remove duplicate records from the same
        # provider before ingestion.
        unique_records = {}
        for record in records:
            key = (record.source, record.source_id)
            unique_records[key] = record

        records = list(unique_records.values())

        # Step 3: Persist papers and their provider records.
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
        )
