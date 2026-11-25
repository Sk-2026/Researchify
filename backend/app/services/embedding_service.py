
from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_model():
    """
    Load the model only once per Python process.
    """
    return SentenceTransformer(MODEL_NAME)


class EmbeddingService:

    def __init__(self):
        self.model = get_model()

    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Convert text into a normalized 384-dimensional vector.
        """
        if not text or not text.strip():
            raise ValueError("Cannot generate embedding for empty text.")

        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embedding.astype(np.float32)

    def generate_paper_embedding(self, paper) -> np.ndarray:
        """
        Generate one embedding from a paper's title and abstract.
        """
        text = f"Title: {paper.title or ''}"

        if paper.abstract:
            text += f"\nAbstract: {paper.abstract}"

        return self.generate_embedding(text)

    def generate_interest_embeddings(
        self,
        researcher_keywords: list[str],
    ) -> dict[str, np.ndarray]:
        """
        Generate one embedding for each research interest.
        """
        if not researcher_keywords:
            return {}

        vectors = self.model.encode(
            researcher_keywords,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return {
            keyword: vector.astype(np.float32)
            for keyword, vector in zip(researcher_keywords, vectors)
        }

    @staticmethod
    def cosine_similarity(
        vector_a: np.ndarray,
        vector_b: np.ndarray,
    ) -> float:
        """
        Both vectors are normalized, so their dot product
        is their cosine similarity.
        """
        return float(np.dot(vector_a, vector_b))
