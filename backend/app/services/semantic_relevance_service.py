
from dataclasses import dataclass

from app.services.embedding_service import EmbeddingService


@dataclass
class SemanticResult:
    score: float
    matched_interest: str | None
    interest_scores: dict[str, float]


class SemanticRelevanceScorer:

    def __init__(self):
        self.embedding_service = EmbeddingService()

    def score(self, paper, researcher_keywords: list[str]) -> SemanticResult:

        if not researcher_keywords:
            return SemanticResult(
                score=0.0,
                matched_interest=None,
                interest_scores={},
            )

        paper_embedding = (
            self.embedding_service.generate_paper_embedding(paper)
        )

        interest_embeddings = (
            self.embedding_service.generate_interest_embeddings(
                researcher_keywords
            )
        )

        interest_scores = {}

        for keyword, interest_embedding in interest_embeddings.items():
            similarity = (
                self.embedding_service.cosine_similarity(
                    paper_embedding,
                    interest_embedding,
                )
            )

            interest_scores[keyword] = round(similarity, 4)

        best_interest = max(
            interest_scores,
            key=interest_scores.get,
        )

        best_score = interest_scores[best_interest]

        return SemanticResult(
            score=round(best_score, 4),
            matched_interest=best_interest,
            interest_scores=interest_scores,
        )
