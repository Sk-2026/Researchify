
import re
from dataclasses import dataclass
from typing import Iterable, Any


@dataclass
class RelevanceResult:
    score: float
    title_score: float
    abstract_score: float
    matched_keywords: list[str]
    excluded_matches: list[str]
    is_excluded: bool


class KeywordRelevanceScorer:
    """
    Calculates keyword relevance using weighted title and abstract
    matching.

    Exact phrase matches are retained as a reliable signal.
    Title matches receive more weight than abstract matches.
    """

    TITLE_WEIGHT = 0.75
    ABSTRACT_WEIGHT = 0.25

    @staticmethod
    def normalize(text: str) -> str:
        words = re.findall(r"\w+", text.casefold())
        return " ".join(words)

    @classmethod
    def matches(cls, text: str, keyword: str) -> bool:
        normalized_text = f" {cls.normalize(text)} "
        normalized_keyword = f" {cls.normalize(keyword)} "

        if normalized_keyword == "  ":
            return False

        return normalized_keyword in normalized_text

    @staticmethod
    def extract_keywords(
        researcher_keywords: Iterable[Any],
    ) -> tuple[list[str], list[str]]:

        included = []
        excluded = []

        seen_included = set()
        seen_excluded = set()

        for item in researcher_keywords:
            keyword = (
                item if isinstance(item, str)
                else getattr(item, "keyword", "")
            )

            if not keyword:
                continue

            is_excluded = (
                False if isinstance(item, str)
                else bool(getattr(item, "is_excluded", False))
            )

            normalized = KeywordRelevanceScorer.normalize(keyword)

            if not normalized:
                continue

            if is_excluded:
                if normalized not in seen_excluded:
                    excluded.append(keyword)
                    seen_excluded.add(normalized)
            else:
                if normalized not in seen_included:
                    included.append(keyword)
                    seen_included.add(normalized)

        return included, excluded

    def score(self, paper, researcher_keywords) -> RelevanceResult:

        title = paper.title or ""
        abstract = paper.abstract or ""

        included, excluded = self.extract_keywords(
            researcher_keywords
        )

        # Excluded topics remain hard filters.
        excluded_matches = [
            keyword
            for keyword in excluded
            if self.matches(title, keyword)
            or self.matches(abstract, keyword)
        ]

        if excluded_matches:
            return RelevanceResult(
                score=0.0,
                title_score=0.0,
                abstract_score=0.0,
                matched_keywords=[],
                excluded_matches=excluded_matches,
                is_excluded=True,
            )

        if not included:
            return RelevanceResult(
                score=0.0,
                title_score=0.0,
                abstract_score=0.0,
                matched_keywords=[],
                excluded_matches=[],
                is_excluded=False,
            )

        title_matches = [
            keyword for keyword in included
            if self.matches(title, keyword)
        ]

        abstract_matches = [
            keyword for keyword in included
            if self.matches(abstract, keyword)
        ]

        total_keywords = len(included)

        title_score = len(title_matches) / total_keywords
        abstract_score = len(abstract_matches) / total_keywords

        # A paper without an abstract is scored using its title.
        if abstract.strip():
            final_score = (
                self.TITLE_WEIGHT * title_score
                + self.ABSTRACT_WEIGHT * abstract_score
            )
        else:
            final_score = title_score

        matched = list(
            dict.fromkeys(title_matches + abstract_matches)
        )

        return RelevanceResult(
            score=round(final_score, 4),
            title_score=round(title_score, 4),
            abstract_score=round(abstract_score, 4),
            matched_keywords=matched,
            excluded_matches=[],
            is_excluded=False,
        )

    def rank(self, papers, researcher_keywords):
        ranked = []

        for paper in papers:
            result = self.score(paper, researcher_keywords)

            if not result.is_excluded:
                ranked.append((paper, result))

        return sorted(
            ranked,
            key=lambda item: item[1].score,
            reverse=True,
        )
