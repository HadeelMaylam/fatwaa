"""
Configuration management for Fatwa RAG system.
Uses Pydantic Settings for environment variable handling.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Supabase Configuration
    supabase_url: str
    supabase_key: str

    # Qdrant Configuration
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection_name: str = "fatwas"

    # Groq API Configuration
    groq_api_key: str

    # Application Settings
    debug: bool = False
    log_level: str = "INFO"

    # Model Configuration
    embedding_model: str = "intfloat/multilingual-e5-small"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # Confidence Thresholds
    high_confidence_threshold: float = 0.80
    medium_confidence_threshold: float = 0.60
    low_confidence_threshold: float = 0.60

    # Search Settings
    initial_search_limit: int = 20
    max_results_return: int = 5

    # Embedding Dimension (multilingual-e5-small)
    embedding_dimension: int = 384

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
