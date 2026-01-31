"""
FastAPI routes for Fatwa RAG system.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Optional
from uuid import UUID
from loguru import logger

from app.models import SearchRequest, SearchResponse, HealthResponse, FatwaDetail
from app.services.supabase_service import supabase_service
from app.services.qdrant_service import qdrant_service
from app.layers.query_processor import query_processor
from app.layers.embedder import embedder
from app.layers.searcher import searcher
from app.layers.reranker import reranker
from app.layers.verifier import verifier
from app.layers.formatter import formatter
from app.config import settings


# Create router
router = APIRouter(prefix="/api", tags=["fatwa"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    Verifies all services are connected and ready.
    """
    try:
        # Test Supabase connection
        supabase_ok = await supabase_service.test_connection()

        # Test Qdrant connection
        qdrant_ok = await qdrant_service.test_connection()

        # Check if models are loaded
        embedder_ok = embedder.is_loaded()
        reranker_ok = reranker.is_loaded()

        all_ok = supabase_ok and qdrant_ok and embedder_ok and reranker_ok

        return HealthResponse(
            status="ok" if all_ok else "degraded",
            supabase_connected=supabase_ok,
            qdrant_connected=qdrant_ok,
            embedding_model_loaded=embedder_ok and reranker_ok
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service health check failed"
        )


@router.post("/search", response_model=SearchResponse)
async def search_fatwas(request: SearchRequest):
    """
    Search for fatwas based on user query.

    This endpoint orchestrates the full 6-layer pipeline:
    1. Query Processing
    2. Embedding
    3. Search
    4. Reranking
    5. Verification
    6. Formatting
    """
    try:
        logger.info(f"Search request received: '{request.query}'")

        # Layer 1: Process query
        processed_query = query_processor.process(request.query)
        logger.info(f"Processed query: '{processed_query}'")

        # Layer 2: Embed query
        query_embedding = embedder.embed_query(processed_query)

        # Layer 3: Search in Qdrant
        search_results = searcher.search(
            query_vector=query_embedding,
            limit=settings.initial_search_limit,
            shaykh_filter=request.shaykh_filter
        )

        if not search_results:
            logger.info("No results found in Qdrant")
            return formatter.format_no_results_response()

        # Get full fatwa details from Supabase
        fatwa_ids = searcher.get_fatwa_ids(search_results)
        fatwas = supabase_service.get_fatwas_by_ids(fatwa_ids)

        if not fatwas:
            logger.warning("Fatwas not found in Supabase for IDs from Qdrant")
            return formatter.format_no_results_response()

        # Layer 4: Rerank using cross-encoder
        ranked_fatwas = reranker.rerank(
            query=processed_query,
            fatwas=fatwas,
            top_k=request.limit * 2  # Get more for filtering
        )

        if not ranked_fatwas:
            return formatter.format_no_results_response()

        # Layer 5: Verify confidence
        top_score = ranked_fatwas[0][1]

        if not verifier.should_return_results(top_score):
            logger.info(f"Top score {top_score:.4f} too low, not returning results")
            return formatter.format_no_results_response(
                reason="لم أجد فتوى تطابق سؤالك بدرجة كافية"
            )

        # Filter by minimum confidence
        filtered_fatwas = verifier.filter_results(
            ranked_fatwas,
            min_confidence=None  # Uses MEDIUM as default
        )

        if not filtered_fatwas:
            return formatter.format_no_results_response(
                reason="النتائج الموجودة ذات صلة ضعيفة بسؤالك"
            )

        # Layer 6: Format response
        response = formatter.format_success_response(
            filtered_fatwas,
            max_results=request.limit
        )

        logger.info(f"Search completed successfully. Returned {len(response.other_results) + 1} results")
        return response

    except Exception as e:
        logger.error(f"Error during search: {e}", exc_info=True)
        return formatter.format_error_response(str(e))


@router.get("/fatwa/{fatwa_id}")
async def get_fatwa(fatwa_id: UUID):
    """
    Get a specific fatwa by ID.
    """
    try:
        fatwa = supabase_service.get_fatwa_by_id(fatwa_id)

        if not fatwa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fatwa with ID {fatwa_id} not found"
            )

        # Format as response
        fatwa_response = formatter.format_fatwa(fatwa)

        return {
            "found": True,
            "fatwa": fatwa_response
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching fatwa {fatwa_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving fatwa"
        )


@router.get("/stats")
async def get_stats():
    """Get system statistics."""
    try:
        collection_info = qdrant_service.get_collection_info()

        return {
            "qdrant_collection": collection_info,
            "config": {
                "embedding_model": settings.embedding_model,
                "reranker_model": settings.reranker_model,
                "high_confidence_threshold": settings.high_confidence_threshold,
                "medium_confidence_threshold": settings.medium_confidence_threshold,
            }
        }

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving statistics"
        )
