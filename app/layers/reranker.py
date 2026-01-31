"""
Layer 4: Reranker
Reorders search results using cross-encoder for higher precision.
"""

from sentence_transformers import CrossEncoder
from typing import List, Dict, Any, Tuple, Optional
from loguru import logger

from app.config import settings
from app.models import FatwaDetail


class Reranker:
    """Reranks search results using cross-encoder model."""

    def __init__(self):
        """Initialize cross-encoder model."""
        logger.info(f"Loading reranker model: {settings.reranker_model}")
        self.model = CrossEncoder(settings.reranker_model)
        logger.info("Reranker model loaded successfully")

    def rerank(
        self,
        query: str,
        fatwas: List[FatwaDetail],
        top_k: Optional[int] = None
    ) -> List[Tuple[FatwaDetail, float]]:
        """
        Rerank fatwas using cross-encoder.

        Args:
            query: Original user query
            fatwas: List of FatwaDetail objects to rerank
            top_k: Number of top results to return (None = all)

        Returns:
            List of (FatwaDetail, score) tuples sorted by relevance
        """
        try:
            if not fatwas:
                return []

            logger.info(f"Reranking {len(fatwas)} candidates")

            # Create query-document pairs
            pairs = []
            for fatwa in fatwas:
                # Combine question and answer for better matching
                document = f"{fatwa.question} {fatwa.answer}"
                pairs.append([query, document])

            # Get cross-encoder scores
            scores = self.model.predict(pairs)

            # Combine fatwas with scores
            fatwa_score_pairs = list(zip(fatwas, scores))

            # Sort by score (descending)
            ranked = sorted(fatwa_score_pairs, key=lambda x: x[1], reverse=True)

            # Return top_k if specified
            if top_k:
                ranked = ranked[:top_k]

            logger.info(f"Reranking complete. Top score: {ranked[0][1]:.4f}" if ranked else "No results")

            return ranked

        except Exception as e:
            logger.error(f"Error during reranking: {e}")
            # Return original order with zero scores on error
            return [(fatwa, 0.0) for fatwa in fatwas]

    def is_loaded(self) -> bool:
        """Check if reranker model is loaded."""
        return self.model is not None


# Global instance
reranker = Reranker()
