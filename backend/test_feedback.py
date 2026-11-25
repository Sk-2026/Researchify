
from app.services.feedback_service import (
    FeedbackLearningService,
    FeedbackRecord,
)


feedback_history = [

    # Researcher likes Gesture Recognition.
    FeedbackRecord("Gesture Recognition", "relevant"),
    FeedbackRecord("Gesture Recognition", "saved"),
    FeedbackRecord("Gesture Recognition", "interesting"),

    # Researcher dislikes Object Detection.
    FeedbackRecord("Object Detection", "not_relevant"),
    FeedbackRecord("Object Detection", "not_relevant"),

    # Researcher already knows some Vision-Language research.
    FeedbackRecord("Vision-Language Models", "already_known"),
]

service = FeedbackLearningService()

preferences = service.calculate_interest_preferences(
    feedback_history
)

print("\nRESEARCHIFY - LEARNED RESEARCH PREFERENCES")
print("=" * 60)

for interest, score in preferences.items():
    print(f"{interest:30} | Preference: {score:.4f}")

print("\nTESTING NEW PAPER PREFERENCES")
print("=" * 60)

for interest in [
    "Gesture Recognition",
    "Object Detection",
    "Vision-Language Models",
    "Flow Matching",
]:

    score = service.score_candidate(
        interest,
        preferences,
    )

    print(f"{interest:30} | Feedback score: {score:.4f}")
