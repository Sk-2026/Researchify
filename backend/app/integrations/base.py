
from dataclasses import dataclass
from datetime import date


@dataclass
class PaperRecord:
    source: str
    source_id: str

    title: str
    doi: str | None = None
    abstract: str | None = None
    publication_date: date | None = None

    authors: list[str] | None = None
    venue: str | None = None
    citation_count: int | None = None
    source_url: str | None = None
