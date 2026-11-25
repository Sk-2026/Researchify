
from datetime import date, timedelta

from app.services.recency_service import RecencyScorer


scorer = RecencyScorer()

today = date.today()

publication_dates = {
    "Today": today,
    "1 year ago": today - timedelta(days=365),
    "2 years ago": today - timedelta(days=730),
    "3 years ago": today - timedelta(days=1095),
    "4 years ago": today - timedelta(days=1460),
    "6 years ago": today - timedelta(days=2190),
    "Unknown publication date": None,
}

print("\nRESEARCHIFY - RECENCY SCORING")
print("=" * 55)

for label, publication_date in publication_dates.items():

    score = scorer.score(publication_date)

    print(f"{label:30} | Score: {score:.4f}")
