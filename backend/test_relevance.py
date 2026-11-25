
from app.integrations.base import PaperRecord
from app.services.relevance_service import KeywordRelevanceScorer


researcher_keywords = [
    "Object Detection",
    "Gesture Recognition",
    "Vision-Language Models",
]

papers = [
    PaperRecord(
        source="openalex",
        source_id="paper_1",
        title="Vision Transformer Based Object Detection",
        abstract=(
            "This paper proposes a transformer architecture "
            "for object detection in autonomous systems."
        ),
    ),
    PaperRecord(
        source="openalex",
        source_id="paper_2",
        title="Gesture Recognition Using Deep Learning",
        abstract=(
            "A deep learning approach for hand gesture recognition."
        ),
    ),
    PaperRecord(
        source="openalex",
        source_id="paper_3",
        title="A Survey of Medical Image Segmentation",
        abstract=(
            "A review of segmentation methods in medical imaging."
        ),
    ),
]

scorer = KeywordRelevanceScorer()

ranked_papers = scorer.rank(papers, researcher_keywords)

print("\nRESEARCHIFY - PAPER RECOMMENDATIONS")
print("=" * 60)

for paper, result in ranked_papers:
    print(f"\nTitle: {paper.title}")
    print(f"Relevance: {result.score * 100:.2f}%")
    print(f"Title score: {result.title_score:.2f}")
    print(f"Abstract score: {result.abstract_score:.2f}")
    print(f"Matched interests: {result.matched_keywords}")
