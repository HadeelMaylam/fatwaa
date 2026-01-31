"""
Layer 6: Formatter
Formats final response with original fatwa text and metadata.
"""

from typing import List, Tuple, Optional
from loguru import logger

from app.models import FatwaDetail, FatwaResponse, SearchResponse
from app.layers.verifier import verifier


class Formatter:
    """Formats search results into final response."""

    def __init__(self):
        """Initialize formatter."""
        logger.info("Formatter initialized")

    def format_fatwa(self, fatwa: FatwaDetail, score: Optional[float] = None) -> FatwaResponse:
        """
        Format a single fatwa for response.

        Args:
            fatwa: FatwaDetail object
            score: Optional confidence score

        Returns:
            FatwaResponse object
        """
        return FatwaResponse(
            question=fatwa.question,
            answer=fatwa.answer,
            shaykh=fatwa.shaykh_name or "غير محدد",
            series=fatwa.series_name or "غير محدد",
            link=fatwa.link,
            confidence_score=score
        )

    def format_success_response(
        self,
        ranked_fatwas: List[Tuple[FatwaDetail, float]],
        max_results: int = 5
    ) -> SearchResponse:
        """
        Format successful search response.

        Args:
            ranked_fatwas: List of (FatwaDetail, score) tuples (sorted)
            max_results: Maximum results to include

        Returns:
            SearchResponse object
        """
        if not ranked_fatwas:
            return self.format_no_results_response()

        # Get top result
        top_fatwa, top_score = ranked_fatwas[0]

        # Format main result
        main_fatwa = self.format_fatwa(top_fatwa, top_score)

        # Format other results (up to max_results - 1)
        other_results = [
            self.format_fatwa(fatwa, score)
            for fatwa, score in ranked_fatwas[1:max_results]
        ]

        # Check if warning is needed
        warning_message = None
        if verifier.needs_warning(top_score):
            warning_message = verifier.get_warning_message()

        response = SearchResponse(
            found=True,
            confidence=top_score,
            fatwa=main_fatwa,
            other_results=other_results,
            message=warning_message
        )

        logger.info(f"Formatted success response with {len(other_results) + 1} results")
        return response

    def format_no_results_response(
        self,
        reason: Optional[str] = None
    ) -> SearchResponse:
        """
        Format response when no matching fatwas found.

        Args:
            reason: Optional reason why no results found

        Returns:
            SearchResponse object
        """
        message = reason or "لم أجد فتوى مطابقة لسؤالك"

        suggestions = [
            "حاول إعادة صياغة السؤال بطريقة مختلفة",
            "استخدم كلمات أكثر وضوحاً",
            "تأكد من أن السؤال يتعلق بأحكام شرعية"
        ]

        response = SearchResponse(
            found=False,
            confidence=None,
            fatwa=None,
            other_results=[],
            message=message,
            suggestions=suggestions
        )

        logger.info("Formatted no results response")
        return response

    def format_error_response(self, error_message: str) -> SearchResponse:
        """
        Format error response.

        Args:
            error_message: Error description

        Returns:
            SearchResponse object
        """
        response = SearchResponse(
            found=False,
            confidence=None,
            fatwa=None,
            other_results=[],
            message=f"حدث خطأ أثناء البحث: {error_message}",
            suggestions=["الرجاء المحاولة مرة أخرى"]
        )

        logger.error(f"Formatted error response: {error_message}")
        return response


# Global instance
formatter = Formatter()
