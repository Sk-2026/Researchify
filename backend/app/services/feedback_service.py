
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class FeedbackRecord:
    matched_interest: str
    feedback_type: str


class FeedbackLearningService:

    FEEDBACK_VALUES = {
        "relevant": 1.0,
        "saved": 1.0,
        "interesting": 0.8,
        "already_known": 0.3,
        "not_relevant": 0.0,
    }

    NEUTRAL_SCORE = 0.5

    # Prevent one or two feedback events from changing preferences
    # too aggressively.
    SMOOTHING_STRENGTH = 2

    def calculate_interest_preferences(
        self,
        feedback_history: list[FeedbackRecord],
    ) -> dict[str, float]:

        interest_scores = defaultdict(list)

        for record in feedback_history:

            interest = record.matched_interest
            feedback_type = record.feedback_type.lower()

            if not interest:
                continue

            if feedback_type not in self.FEEDBACK_VALUES:
                continue

            score = self.FEEDBACK_VALUES[feedback_type]

            interest_scores[interest].append(score)

        preferences = {}

        for interest, scores in interest_scores.items():

            total = sum(scores)
            count = len(scores)

            # Smooth the average toward a neutral score.
            preference = (
                total + self.SMOOTHING_STRENGTH * self.NEUTRAL_SCORE
            ) / (
                count + self.SMOOTHING_STRENGTH
            )

            preferences[interest] = round(preference, 4)

        return preferences

    def score_candidate(
        self,
        matched_interest: str | None,
        preferences: dict[str, float],
    ) -> float:

        if not matched_interest:
            return self.NEUTRAL_SCORE

        return preferences.get(
            matched_interest,
            self.NEUTRAL_SCORE,
        )
