
from app.integrations.base import PaperRecord
from app.services.semantic_relevance_service import (
    SemanticRelevanceScorer,
)


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
            "This paper proposes a neural network architecture "
            "for detecting and localizing objects in images."
        ),
    ),
    PaperRecord(
        source="openalex",
        source_id="paper_2",
        title="Recognizing and Localizing Objects in Images",
        abstract=(
            "We introduce a visual recognition approach to identify "
            "different objects and their locations in a scene."
        ),
    ),
    PaperRecord(
        source="openalex",
        source_id="paper_3",
        title="Hand Gesture Recognition Using Neural Networks",
        abstract=(
            "A computer vision system for recognizing hand movements "
            "and classifying human gestures."
        ),
    ),
    PaperRecord(
        source="openalex",
        source_id="paper_4",
        title="Medical Image Segmentation",
        abstract=(
            "A study of segmentation techniques for medical images."
        ),
    ),
]

scorer = SemanticRelevanceScorer()

ranked = []

for paper in papers:
    result = scorer.score(paper, researcher_keywords)
    ranked.append((paper, result))

ranked.sort(
    key=lambda item: item[1].score,
    reverse=True,
)

print("\nRESEARCHIFY - SEMANTIC RECOMMENDATIONS")
print("=" * 65)

for paper, result in ranked:
    print(f"\nTitle: {paper.title}")
    print(f"Semantic similarity: {result.score:.4f}")
    print(f"Closest interest: {result.matched_interest}")
    print(f"All interest scores: {result.interest_scores}")
