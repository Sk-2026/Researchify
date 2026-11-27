
from dataclasses import dataclass

from app.services.relevance_service import KeywordRelevanceScorer
from app.services.semantic_relevance_service import SemanticRelevanceScorer
from app.services.recency_service import RecencyScorer

from app.services.feedback_service import (
    FeedbackLearningService,
)


@dataclass
class RecommendationResult:
    paper: object
    final_score: float
    relevance_score: float
    semantic_score: float
    keyword_score: float
    recency_score: float
    feedback_score: float
    matched_keywords: list[str]
    matched_interest: str | None


class RecommendationService:
    """
    Ranks papers by research relevance and personalization.

    Research relevance:
        55% semantic similarity
        45% keyword relevance

    Final ranking:
        70% research relevance
        25% recency
         5% researcher feedback

    relevance_score is a ranking component, NOT a calibrated
    probability that a paper is relevant.
    """

    SEMANTIC_WEIGHT = 0.55
    KEYWORD_WEIGHT = 0.45

    RELEVANCE_RANKING_WEIGHT = 0.70
    RECENCY_WEIGHT = 0.25
    FEEDBACK_WEIGHT = 0.05

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
            self.keyword_scorer.extract_keywords(
                researcher_keywords
            )
        )

        preferences = (
            self.feedback_service.calculate_interest_preferences(
                feedback_history or []
            )
        )

        recommendations = []

        for paper in papers:

            # 1. Exact keyword relevance and excluded-topic filtering.
            keyword_result = self.keyword_scorer.score(
                paper,
                researcher_keywords,
            )

            if keyword_result.is_excluded:
                continue

            # 2. Semantic relevance.
            semantic_result = self.semantic_scorer.score(
                paper,
                included_keywords,
            )

            semantic_score = semantic_result.score
            matched_interest = semantic_result.matched_interest

            # 3. Research relevance (used for notification threshold).
            relevance_score = (
                self.SEMANTIC_WEIGHT * semantic_score
                + self.KEYWORD_WEIGHT * keyword_result.score
            )

            # 4. Recency.
            recency_score = self.recency_scorer.score(
                paper.publication_date
            )

            # 5. Researcher feedback.
            feedback_score = (
                self.feedback_service.score_candidate(
                    matched_interest,
                    preferences,
                )
            )

            # 6. Final personalized ranking.
            final_score = (
                self.RELEVANCE_RANKING_WEIGHT * relevance_score
                + self.RECENCY_WEIGHT * recency_score
                + self.FEEDBACK_WEIGHT * feedback_score
            )

            recommendations.append(
                RecommendationResult(
                    paper=paper,
                    final_score=round(final_score, 4),
                    relevance_score=round(relevance_score, 4),
                    semantic_score=round(semantic_score, 4),
                    keyword_score=round(keyword_result.score, 4),
                    recency_score=round(recency_score, 4),
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
