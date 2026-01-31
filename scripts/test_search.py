"""
Testing script for fatwa search system.
Tests the full pipeline with sample queries.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from loguru import logger
import json

from app.layers.query_processor import query_processor
from app.layers.embedder import embedder
from app.layers.searcher import searcher
from app.layers.reranker import reranker
from app.layers.verifier import verifier
from app.layers.formatter import formatter
from app.services.supabase_service import supabase_service
from app.config import settings


def test_query(query: str, show_full_answer: bool = False):
    """
    Test a single query through the full pipeline.

    Args:
        query: Arabic query text
        show_full_answer: Whether to print full fatwa answer
    """
    logger.info("="*80)
    logger.info(f"Testing query: '{query}'")
    logger.info("="*80)

    try:
        # Layer 1: Process query
        logger.info("[Layer 1] Processing query...")
        processed = query_processor.process(query)
        logger.info(f"Processed: '{processed}'")

        # Layer 2: Embed query
        logger.info("[Layer 2] Generating embedding...")
        embedding = embedder.embed_query(processed)
        logger.info(f"Embedding dimension: {len(embedding)}")

        # Layer 3: Search
        logger.info("[Layer 3] Searching Qdrant...")
        results = searcher.search(embedding, limit=settings.initial_search_limit)
        logger.info(f"Found {len(results)} candidates")

        if not results:
            logger.warning("No results found!")
            return

        # Get full fatwas
        fatwa_ids = searcher.get_fatwa_ids(results)
        fatwas = supabase_service.get_fatwas_by_ids(fatwa_ids)
        logger.info(f"Retrieved {len(fatwas)} fatwas from database")

        # Layer 4: Rerank
        logger.info("[Layer 4] Reranking results...")
        ranked = reranker.rerank(processed, fatwas, top_k=10)
        logger.info(f"Reranked {len(ranked)} results")

        if ranked:
            logger.info(f"Top 5 scores: {[f'{score:.4f}' for _, score in ranked[:5]]}")

        # Layer 5: Verify
        logger.info("[Layer 5] Verifying confidence...")
        top_score = ranked[0][1] if ranked else 0.0
        should_return = verifier.should_return_results(top_score)
        logger.info(f"Top score: {top_score:.4f}, Should return: {should_return}")

        if not should_return:
            logger.warning("Confidence too low - would not return results")
            print("\nResult: لم أجد فتوى مطابقة لسؤالك\n")
            return

        # Filter results
        filtered = verifier.filter_results(ranked)
        logger.info(f"Filtered to {len(filtered)} results")

        # Layer 6: Format
        logger.info("[Layer 6] Formatting response...")
        response = formatter.format_success_response(filtered, max_results=3)

        # Display results
        print("\n" + "="*80)
        print("RESULTS")
        print("="*80)
        print(f"Found: {response.found}")
        print(f"Confidence: {response.confidence:.4f}")

        if response.message:
            print(f"Message: {response.message}")

        if response.fatwa:
            print("\n--- Main Result ---")
            print(f"Shaykh: {response.fatwa.shaykh}")
            print(f"Series: {response.fatwa.series}")
            print(f"Score: {response.fatwa.confidence_score:.4f}")
            print(f"\nQuestion: {response.fatwa.question}")

            if show_full_answer:
                print(f"\nAnswer: {response.fatwa.answer}")
            else:
                print(f"\nAnswer: {response.fatwa.answer[:300]}...")

            print(f"\nLink: {response.fatwa.link}")

        if response.other_results:
            print(f"\n--- Other Results ({len(response.other_results)}) ---")
            for i, fatwa in enumerate(response.other_results, 1):
                print(f"\n{i}. Score: {fatwa.confidence_score:.4f}")
                print(f"   Question: {fatwa.question[:100]}...")
                print(f"   Shaykh: {fatwa.shaykh}")

        print("\n" + "="*80)

    except Exception as e:
        logger.error(f"Error during test: {e}", exc_info=True)


def run_test_suite():
    """Run a suite of test queries."""

    test_queries = [
        # Formal Arabic
        "ما حكم الصلاة في البيت؟",
        "هل يجوز الجمع بين الصلاتين للمسافر؟",

        # Gulf Dialect
        "وش حكم الصلاة بالشورت؟",
        "ايش حكم قراءة القرآن بدون وضوء؟",
        "ليش الزكاة واجبة؟",

        # Complex questions
        "ابي اعرف حكم صلاة الجمعة للمسافر",
        "هل يجوز الصيام بدون سحور؟",
    ]

    logger.info(f"Running test suite with {len(test_queries)} queries...")

    for i, query in enumerate(test_queries, 1):
        logger.info(f"\n\n>>> Test {i}/{len(test_queries)}")
        test_query(query, show_full_answer=False)
        input("\nPress Enter to continue to next test...")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test fatwa search system")
    parser.add_argument(
        "--query",
        type=str,
        help="Single query to test"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Show full fatwa answers"
    )
    parser.add_argument(
        "--suite",
        action="store_true",
        help="Run full test suite"
    )

    args = parser.parse_args()

    if args.suite:
        run_test_suite()
    elif args.query:
        test_query(args.query, show_full_answer=args.full)
    else:
        # Default: run one example
        test_query("وش حكم الصلاة بالشورت؟", show_full_answer=True)
