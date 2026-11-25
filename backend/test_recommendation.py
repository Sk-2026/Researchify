
from datetime import date, timedelta

from app.integrations.base import PaperRecord
from app.services.recommendation_service import RecommendationService


researcher_keywords = [
    "Object Detection",
    "Gesture Recognition",
    "Vision-Language Models",
    "Flow Matching",
]

papers = [
    PaperRecord(
        source="openalex",
        source_id="paper_1",
        title="Deep Learning Based Object Detection",
        abstract=(
            "A neural network architecture for detecting and "
            "localizing objects in images."
        ),
        publication_date=date.today() - timedelta(days=100),
    ),

    PaperRecord(
        source="openalex",
        source_id="paper_2",
        title="Recognizing and Localizing Objects in Images",
        abstract=(
            "A visual recognition method to identify objects "
            "and their locations in a scene."
        ),
        publication_date=date.today() - timedelta(days=300),
    ),

    PaperRecord(
        source="openalex",
        source_id="paper_3",
        title="Hand Gesture Recognition Using Neural Networks",
        abstract=(
            "A computer vision system for recognizing hand "
            "movements and classifying human gestures."
        ),
        publication_date=date.today() - timedelta(days=200),
    ),

    PaperRecord(
        source="openalex",
        source_id="paper_4",
        title="Medical Image Segmentation",
        abstract=(
            "A study of segmentation techniques for medical images."
        ),
        publication_date=date.today() - timedelta(days=50),
    ),
]

service = RecommendationService()

recommendations = service.rank(
    papers=papers,
    researcher_keywords=researcher_keywords,
)

print("\nRESEARCHIFY - PERSONALIZED RECOMMENDATIONS")
print("=" * 75)

for rank, result in enumerate(recommendations, start=1):

    print(f"\nRank: {rank}")
    print(f"Title: {result.paper.title}")
    print(f"Final score: {result.final_score:.4f}")

    print(f"Semantic: {result.semantic_score:.4f}")
    print(f"Keyword: {result.keyword_score:.4f}")
    print(f"Recency: {result.recency_score:.4f}")
    print(f"Feedback: {result.feedback_score:.4f}")

    print(f"Matched interest: {result.matched_interest}")
    print(f"Matched keywords: {result.matched_keywords}")
