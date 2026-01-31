"""
Indexing script for fatwas.
Fetches all fatwas from Supabase, generates embeddings, and indexes into Qdrant.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from loguru import logger
from typing import List
import time

from app.services.supabase_service import supabase_service
from app.services.qdrant_service import qdrant_service
from app.layers.embedder import embedder
from app.layers.query_processor import query_processor


def prepare_text_for_embedding(question: str, answer: str) -> str:
    """
    Prepare fatwa text for embedding.
    Combines question and answer for better semantic coverage.

    Args:
        question: Fatwa question
        answer: Fatwa answer

    Returns:
        Combined and cleaned text
    """
    # Combine question and answer
    combined = f"{question} {answer}"

    # Clean the text
    cleaned = query_processor.clean_text(combined)

    return cleaned


def index_all_fatwas(recreate_collection: bool = False):
    """
    Main indexing function.

    Args:
        recreate_collection: If True, delete and recreate Qdrant collection
    """
    logger.info("="*60)
    logger.info("Starting Fatwa Indexing Process")
    logger.info("="*60)

    start_time = time.time()

    try:
        # Step 1: Fetch all fatwas from Supabase
        logger.info("Step 1: Fetching fatwas from Supabase...")
        fatwas = supabase_service.get_all_fatwas()

        if not fatwas:
            logger.error("No fatwas found in database!")
            return

        logger.info(f"✓ Fetched {len(fatwas)} fatwas")

        # Step 2: Prepare Qdrant collection
        logger.info("Step 2: Preparing Qdrant collection...")

        if recreate_collection:
            logger.warning("Deleting existing collection...")
            qdrant_service.delete_collection()
            time.sleep(2)  # Wait for deletion

        # Create collection (will skip if exists and not recreating)
        success = qdrant_service.create_collection()
        if not success:
            logger.error("Failed to create Qdrant collection")
            return

        logger.info("✓ Qdrant collection ready")

        # Step 3: Prepare fatwa texts
        logger.info("Step 3: Preparing texts for embedding...")
        texts = []
        fatwa_metadata = []

        for fatwa in fatwas:
            # Prepare text (question + answer)
            text = prepare_text_for_embedding(fatwa.question, fatwa.answer)
            texts.append(text)

            # Store metadata
            metadata = {
                "id": fatwa.id,
                "shaykh_name": fatwa.shaykh_name,
                "series_name": fatwa.series_name,
                "question": fatwa.question,
                "answer": fatwa.answer
            }
            fatwa_metadata.append(metadata)

        logger.info(f"✓ Prepared {len(texts)} texts")

        # Step 4: Generate embeddings
        logger.info("Step 4: Generating embeddings (this may take a while)...")
        embeddings = embedder.embed_documents_batch(texts, batch_size=32)
        logger.info(f"✓ Generated {len(embeddings)} embeddings")

        # Step 5: Index into Qdrant
        logger.info("Step 5: Indexing into Qdrant...")
        success = qdrant_service.index_fatwas(fatwa_metadata, embeddings)

        if not success:
            logger.error("Failed to index fatwas into Qdrant")
            return

        logger.info("✓ Indexing complete")

        # Step 6: Verify
        logger.info("Step 6: Verifying indexing...")
        collection_info = qdrant_service.get_collection_info()

        if collection_info:
            logger.info(f"✓ Collection info: {collection_info}")

        elapsed_time = time.time() - start_time
        logger.info("="*60)
        logger.info(f"✓ Indexing completed successfully!")
        logger.info(f"Total fatwas indexed: {len(fatwas)}")
        logger.info(f"Time taken: {elapsed_time:.2f} seconds")
        logger.info("="*60)

    except Exception as e:
        logger.error(f"Error during indexing: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Index fatwas into Qdrant")
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Delete and recreate Qdrant collection"
    )

    args = parser.parse_args()

    # Run indexing
    index_all_fatwas(recreate_collection=args.recreate)
