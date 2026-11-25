
from dataclasses import dataclass

from app.services.relevance_service import KeywordRelevanceScorer
from app.services.semantic_relevance_service import SemanticRelevanceScorer
from app.services.recency_service import RecencyScorer

from app.services.feedback_service import (
    FeedbackLearningService,
    FeedbackRecord,
)
@dataclass
class RecommendationResult:
    paper: object
    final_score: float
    semantic_score: float
    keyword_score: float
    recency_score: float
    feedback_score: float
    matched_keywords: list[str]
    matched_interest: str | None


class RecommendationService:

    SEMANTIC_WEIGHT = 0.50
    KEYWORD_WEIGHT = 0.25
    RECENCY_WEIGHT = 0.15
    FEEDBACK_WEIGHT = 0.10

    NEUTRAL_FEEDBACK = 0.50

    def __init__(self):
        self.keyword_scorer = KeywordRelevanceScorer()
        self.semantic_scorer = SemanticRelevanceScorer()
        self.recency_scorer = RecencyScorer()
        self.feedback_service = FeedbackLearningService()

    def rank(
        self,
        papers,
        researcher_keywords,
        feedback_history=None,
    ):

        included_keywords, _ = (
            self.keyword_scorer.extract_keywords(researcher_keywords)
        )

        interest_embeddings = (
            self.semantic_scorer.embedding_service
            .generate_interest_embeddings(included_keywords)
        )

        # Learn the researcher's topic preferences.
        preferences = (
            self.feedback_service.calculate_interest_preferences(
                feedback_history or []
            )
        )

        recommendations = []

        for paper in papers:

            keyword_result = self.keyword_scorer.score(
                paper,
                researcher_keywords,
            )

            if keyword_result.is_excluded:
                continue

            # Semantic relevance.
            if interest_embeddings:

                paper_embedding = (
                    self.semantic_scorer.embedding_service
                    .generate_paper_embedding(paper)
                )

                interest_scores = {
                    keyword: max(
                        0.0,
                        self.semantic_scorer.embedding_service
                        .cosine_similarity(
                            paper_embedding,
                            interest_embedding,
                        ),
                    )
                    for keyword, interest_embedding
                    in interest_embeddings.items()
                }

                matched_interest = max(
                    interest_scores,
                    key=interest_scores.get,
                )

                semantic_score = interest_scores[matched_interest]

            else:
                semantic_score = 0.0
                matched_interest = None

            # Recency.
            recency_score = self.recency_scorer.score(
                paper.publication_date
            )

            # Personalized feedback score.
            feedback_score = (
                self.feedback_service.score_candidate(
                    matched_interest,
                    preferences,
                )
            )

            # Unified ranking.
            final_score = (
                self.SEMANTIC_WEIGHT * semantic_score
                + self.KEYWORD_WEIGHT * keyword_result.score
                + self.RECENCY_WEIGHT * recency_score
                + self.FEEDBACK_WEIGHT * feedback_score
            )

            recommendations.append(
                RecommendationResult(
                    paper=paper,
                    final_score=round(final_score, 4),
                    semantic_score=round(semantic_score, 4),
                    keyword_score=keyword_result.score,
                    recency_score=recency_score,
                    feedback_score=round(feedback_score, 4),
                    matched_keywords=keyword_result.matched_keywords,
                    matched_interest=matched_interest,
                )
            )

        recommendations.sort(
            key=lambda result: result.final_score,
            reverse=True,
        )

        return recommendations
