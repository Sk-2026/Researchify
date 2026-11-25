
import math
from datetime import date


class RecencyScorer:

    HALF_LIFE_DAYS = 730

    def score(self, publication_date: date | None) -> float:
        """
        Calculate a recency score between 0 and 1.

        Newer papers receive higher scores.
        Papers without publication dates receive 0.
        """

        if publication_date is None:
            return 0.0

        today = date.today()

        age_days = (today - publication_date).days

        # Future-dated papers should not receive a penalty.
        age_days = max(0, age_days)

        decay_rate = math.log(2) / self.HALF_LIFE_DAYS

        recency_score = math.exp(-decay_rate * age_days)

        return round(recency_score, 4)
