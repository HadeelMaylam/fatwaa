"""
Layer 3: Searcher
Performs hybrid search using Qdrant vector database.
"""

from typing import List, Dict, Any, Optional
from loguru import logger

from app.config import settings
from app.services.qdrant_service import qdrant_service


class Searcher:
    """Performs semantic search in Qdrant."""

    def __init__(self):
        """Initialize searcher."""
        self.qdrant = qdrant_service
        logger.info("Searcher initialized")

    def search(
        self,
        query_vector: List[float],
        limit: Optional[int] = None,
        shaykh_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar fatwas using vector similarity.

        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results (defaults to config)
            shaykh_filter: Optional shaykh name to filter by

        Returns:
            List of candidate fatwas with scores and metadata
        """
        try:
            # Use config default if limit not specified
            search_limit = limit or settings.initial_search_limit

            logger.info(f"Searching Qdrant for top {search_limit} results")

            # Perform vector search
            results = self.qdrant.search(
                query_vector=query_vector,
                limit=search_limit,
                shaykh_filter=shaykh_filter
            )

            logger.info(f"Qdrant returned {len(results)} candidates")

            # Add metadata
            for result in results:
                result['search_score'] = result.get('score', 0.0)

            return results

        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []

    def get_fatwa_ids(self, search_results: List[Dict[str, Any]]) -> List[str]:
        """
        Extract fatwa IDs from search results.

        Args:
            search_results: Results from Qdrant search

        Returns:
            List of fatwa UUID strings
        """
        return [result['fatwa_id'] for result in search_results if 'fatwa_id' in result]


# Global instance
searcher = Searcher()
