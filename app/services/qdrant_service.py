"""
Qdrant service for vector search operations.
Handles collection management and semantic search.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
    SearchRequest as QdrantSearchRequest,
    Filter,
    FieldCondition,
    MatchValue
)
from typing import List, Dict, Any, Optional
from loguru import logger
from uuid import UUID

from app.config import settings


class QdrantService:
    """Service for interacting with Qdrant vector database."""

    def __init__(self):
        """Initialize Qdrant client."""
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key
        )
        self.collection_name = settings.qdrant_collection_name
        logger.info("Qdrant client initialized")

    async def test_connection(self) -> bool:
        """Test Qdrant connection."""
        try:
            collections = self.client.get_collections()
            logger.info("Qdrant connection successful")
            return True
        except Exception as e:
            logger.error(f"Qdrant connection failed: {e}")
            return False

    def create_collection(self) -> bool:
        """
        Create Qdrant collection for fatwas if it doesn't exist.

        Returns:
            True if created or already exists, False on error
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name in collection_names:
                logger.info(f"Collection '{self.collection_name}' already exists")
                return True

            # Create new collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=settings.embedding_dimension,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection '{self.collection_name}'")
            return True

        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            return False

    def delete_collection(self) -> bool:
        """Delete the collection (useful for reindexing)."""
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Deleted collection '{self.collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            return False

    def index_fatwas(self, fatwas: List[Dict[str, Any]], embeddings: List[List[float]]) -> bool:
        """
        Index fatwas into Qdrant collection.

        Args:
            fatwas: List of fatwa dictionaries with id and metadata
            embeddings: List of embedding vectors (same order as fatwas)

        Returns:
            True if successful, False otherwise
        """
        try:
            if len(fatwas) != len(embeddings):
                raise ValueError("Number of fatwas must match number of embeddings")

            # Create points
            points = []
            for i, (fatwa, embedding) in enumerate(zip(fatwas, embeddings)):
                point = PointStruct(
                    id=i,  # Use index as point ID
                    vector=embedding,
                    payload={
                        "fatwa_id": str(fatwa["id"]),
                        "shaykh_name": fatwa.get("shaykh_name", ""),
                        "series_name": fatwa.get("series_name", ""),
                        "question": fatwa.get("question", ""),
                        "answer": fatwa.get("answer", "")[:500]  # First 500 chars for preview
                    }
                )
                points.append(point)

            # Upload in batches of 100
            batch_size = 100
            total_batches = (len(points) + batch_size - 1) // batch_size

            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
                current_batch = (i // batch_size) + 1
                logger.info(f"Indexed batch {current_batch}/{total_batches}")

            logger.info(f"Successfully indexed {len(points)} fatwas")
            return True

        except Exception as e:
            logger.error(f"Error indexing fatwas: {e}")
            return False

    def search(
        self,
        query_vector: List[float],
        limit: int = 20,
        shaykh_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar fatwas using vector similarity.

        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results
            shaykh_filter: Optional filter by shaykh name

        Returns:
            List of search results with fatwa_id and score
        """
        try:
            # Build filter if needed
            search_filter = None
            if shaykh_filter:
                search_filter = Filter(
                    must=[
                        FieldCondition(
                            key="shaykh_name",
                            match=MatchValue(value=shaykh_filter)
                        )
                    ]
                )

            # Perform search
            results = self.client.search_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit,
                query_filter=search_filter,
                with_payload=True
            )

            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "fatwa_id": result.payload["fatwa_id"],
                    "score": result.score,
                    "shaykh_name": result.payload.get("shaykh_name", ""),
                    "series_name": result.payload.get("series_name", ""),
                    "question_preview": result.payload.get("question", "")[:200],
                    "answer_preview": result.payload.get("answer", "")[:200]
                })

            logger.info(f"Found {len(formatted_results)} results")
            return formatted_results

        except Exception as e:
            logger.error(f"Error searching Qdrant: {e}")
            return []

    def get_collection_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the collection."""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": info.config.params.vectors.size,
                "points_count": info.points_count,
                "vectors_count": info.vectors_count
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return None


# Global instance
qdrant_service = QdrantService()
