"""
Layer 2: Embedder
Converts text to vector embeddings using multilingual-e5-small model.
"""

from sentence_transformers import SentenceTransformer
from typing import List, Union
from loguru import logger
import numpy as np

from app.config import settings


class Embedder:
    """Converts text to embeddings using multilingual-e5-small."""

    def __init__(self):
        """Initialize the embedding model."""
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        self.model = SentenceTransformer(settings.embedding_model)
        logger.info("Embedding model loaded successfully")

    def embed_query(self, query: str) -> List[float]:
        """
        Embed a query text.
        For e5 models, queries must be prefixed with "query: "

        Args:
            query: Processed query text

        Returns:
            Embedding vector as list of floats
        """
        try:
            # Add "query: " prefix for e5 model
            prefixed_query = f"query: {query}"

            # Generate embedding
            embedding = self.model.encode(
                prefixed_query,
                normalize_embeddings=True  # Normalize for cosine similarity
            )

            # Convert to list
            embedding_list = embedding.tolist()

            logger.debug(f"Generated query embedding with dimension: {len(embedding_list)}")
            return embedding_list

        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise

    def embed_document(self, text: str) -> List[float]:
        """
        Embed a document text (fatwa).
        For e5 models, documents must be prefixed with "passage: "

        Args:
            text: Document text (question + answer)

        Returns:
            Embedding vector as list of floats
        """
        try:
            # Add "passage: " prefix for e5 model
            prefixed_text = f"passage: {text}"

            # Generate embedding
            embedding = self.model.encode(
                prefixed_text,
                normalize_embeddings=True
            )

            # Convert to list
            embedding_list = embedding.tolist()

            return embedding_list

        except Exception as e:
            logger.error(f"Error generating document embedding: {e}")
            raise

    def embed_documents_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Embed multiple documents in batches (for indexing).

        Args:
            texts: List of document texts
            batch_size: Number of documents to process at once

        Returns:
            List of embedding vectors
        """
        try:
            # Add "passage: " prefix to all texts
            prefixed_texts = [f"passage: {text}" for text in texts]

            logger.info(f"Embedding {len(texts)} documents in batches of {batch_size}")

            # Generate embeddings in batches
            embeddings = self.model.encode(
                prefixed_texts,
                batch_size=batch_size,
                normalize_embeddings=True,
                show_progress_bar=True
            )

            # Convert to list of lists
            embeddings_list = embeddings.tolist()

            logger.info(f"Successfully embedded {len(embeddings_list)} documents")
            return embeddings_list

        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise

    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.model is not None


# Global instance (will be initialized when first imported)
embedder = Embedder()
