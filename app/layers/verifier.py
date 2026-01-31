"""
Layer 5: Verifier
Filters and verifies search results based on confidence thresholds.
"""

from typing import List, Tuple, Optional
from enum import Enum
from loguru import logger

from app.config import settings
from app.models import FatwaDetail


class ConfidenceLevel(Enum):
    """Confidence level enum."""
    HIGH = "high"          # >= 0.80
    MEDIUM = "medium"      # >= 0.60, < 0.80
    LOW = "low"            # < 0.60


class Verifier:
    """Verifies and filters search results based on confidence."""

    def __init__(self):
        """Initialize verifier with thresholds from config."""
        self.high_threshold = settings.high_confidence_threshold
        self.medium_threshold = settings.medium_confidence_threshold
        self.low_threshold = settings.low_confidence_threshold
        logger.info(f"Verifier initialized with thresholds: "
                   f"high={self.high_threshold}, "
                   f"medium={self.medium_threshold}, "
                   f"low={self.low_threshold}")

    def get_confidence_level(self, score: float) -> ConfidenceLevel:
        """
        Determine confidence level based on score.

        Args:
            score: Reranker score

        Returns:
            ConfidenceLevel enum
        """
        if score >= self.high_threshold:
            return ConfidenceLevel.HIGH
        elif score >= self.medium_threshold:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    def filter_results(
        self,
        ranked_fatwas: List[Tuple[FatwaDetail, float]],
        min_confidence: Optional[ConfidenceLevel] = None
    ) -> List[Tuple[FatwaDetail, float]]:
        """
        Filter results by minimum confidence level.

        Args:
            ranked_fatwas: List of (FatwaDetail, score) tuples
            min_confidence: Minimum confidence level (default: MEDIUM)

        Returns:
            Filtered list of (FatwaDetail, score) tuples
        """
        if not ranked_fatwas:
            return []

        # Default to MEDIUM confidence
        min_conf = min_confidence or ConfidenceLevel.MEDIUM

        # Determine threshold based on confidence level
        if min_conf == ConfidenceLevel.HIGH:
            threshold = self.high_threshold
        elif min_conf == ConfidenceLevel.MEDIUM:
            threshold = self.medium_threshold
        else:
            threshold = self.low_threshold

        # Filter by threshold
        filtered = [
            (fatwa, score)
            for fatwa, score in ranked_fatwas
            if score >= threshold
        ]

        logger.info(f"Filtered {len(ranked_fatwas)} results to {len(filtered)} "
                   f"with min confidence={min_conf.value}, threshold={threshold}")

        return filtered

    def should_return_results(self, top_score: float) -> bool:
        """
        Determine if results should be returned to user.

        Args:
            top_score: Best reranker score

        Returns:
            True if results are reliable enough to show
        """
        # Only return if top score meets minimum threshold
        should_return = top_score >= self.low_threshold

        if not should_return:
            logger.warning(f"Top score {top_score:.4f} below minimum threshold "
                          f"{self.low_threshold}. Will not return results.")

        return should_return

    def needs_warning(self, score: float) -> bool:
        """
        Check if result needs a confidence warning.

        Args:
            score: Reranker score

        Returns:
            True if warning should be shown to user
        """
        # Show warning for medium confidence results
        confidence = self.get_confidence_level(score)
        return confidence == ConfidenceLevel.MEDIUM

    def get_warning_message(self) -> str:
        """Get warning message for medium confidence results."""
        return (
            "تنبيه: الفتوى التالية قد تكون ذات صلة بسؤالك، "
            "لكن يُنصح بإعادة صياغة السؤال للحصول على نتيجة أفضل."
        )


# Global instance
verifier = Verifier()
