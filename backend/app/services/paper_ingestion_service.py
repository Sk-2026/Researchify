
import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.base import PaperRecord
from app.models.paper import Paper, PaperSource, UserPaper, PaperStatus


@dataclass
class IngestionResult:
    inserted: int = 0
    updated: int = 0
    sources_added: int = 0


class PaperIngestionService:

    @staticmethod
    def normalize_doi(doi: str | None) -> str | None:
        if not doi:
            return None

        doi = doi.strip()

        for prefix in (
            "https://doi.org/",
            "http://doi.org/",
            "https://dx.doi.org/",
            "http://dx.doi.org/",
            "doi:",
        ):
            if doi.lower().startswith(prefix):
                doi = doi[len(prefix):]
                break

        return doi.strip().lower() or None

    async def ingest(
        self,
        records: list[PaperRecord],
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> IngestionResult:

        result = IngestionResult()

        for record in records:

            normalized_doi = self.normalize_doi(record.doi)
            paper = None

            # 1. Identify an existing paper by DOI.
            if normalized_doi:
                paper = await db.scalar(
                    select(Paper).where(Paper.doi == normalized_doi)
                )

            # 2. If DOI lookup fails, use source identity.
            if paper is None:
                paper = await db.scalar(
                    select(Paper)
                    .join(PaperSource, PaperSource.paper_id == Paper.id)
                    .where(
                        PaperSource.source == record.source,
                        PaperSource.source_id == record.source_id,
                    )
                )

            # 3. Insert a new paper or enrich an existing one.
            if paper is None:
                paper = Paper(
                    doi=normalized_doi,
                    title=record.title,
                    abstract=record.abstract,
                    publication_date=record.publication_date,
                    authors=record.authors or [],
                    venue=record.venue,
                    citation_count=record.citation_count,
                )

                db.add(paper)
                await db.flush()

                result.inserted += 1

            else:
                if not paper.doi and normalized_doi:
                    paper.doi = normalized_doi

                if not paper.abstract and record.abstract:
                    paper.abstract = record.abstract

                if not paper.publication_date and record.publication_date:
                    paper.publication_date = record.publication_date

                if not paper.authors and record.authors:
                    paper.authors = record.authors

                if not paper.venue and record.venue:
                    paper.venue = record.venue

                if (
                    paper.citation_count is None
                    and record.citation_count is not None
                ):
                    paper.citation_count = record.citation_count

                result.updated += 1

            # 4. Store the academic source independently.
            existing_source = await db.scalar(
                select(PaperSource).where(
                    PaperSource.source == record.source,
                    PaperSource.source_id == record.source_id,
                )
            )

            if existing_source is None:
                db.add(
                    PaperSource(
                        paper_id=paper.id,
                        source=record.source,
                        source_id=record.source_id,
                        source_url=record.source_url,
                    )
                )

                result.sources_added += 1

            # 5. Associate the paper with the researcher.
            existing_user_paper = await db.scalar(
                select(UserPaper).where(
                    UserPaper.user_id == user_id,
                    UserPaper.paper_id == paper.id,
                )
            )

            if existing_user_paper is None:
                db.add(
                    UserPaper(
                        user_id=user_id,
                        paper_id=paper.id,
                        status=PaperStatus.NEW,
                    )
                )

        await db.flush()

        return result
