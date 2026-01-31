"""
Main FastAPI application for Fatwa RAG system.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from app.config import settings
from app.api.routes import router


# Configure logger
logger.remove()  # Remove default handler
logger.add(
    sys.stdout,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
)


# Create FastAPI app
app = FastAPI(
    title="Fatwa RAG System",
    description="Semantic search system for Islamic fatwas from Sheikh Ibn Baz and Sheikh Ibn Uthaymeen",
    version="1.0.0",
    debug=settings.debug
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routes
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("="*50)
    logger.info("Starting Fatwa RAG System")
    logger.info("="*50)
    logger.info(f"Embedding Model: {settings.embedding_model}")
    logger.info(f"Reranker Model: {settings.reranker_model}")
    logger.info(f"Qdrant Collection: {settings.qdrant_collection_name}")
    logger.info(f"Debug Mode: {settings.debug}")
    logger.info("="*50)

    # Models are lazy-loaded on first use
    logger.info("Services ready. Models will be loaded on first request.")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Fatwa RAG System")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Fatwa RAG System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
