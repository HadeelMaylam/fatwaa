"""
Pydantic models for request/response schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID


class SearchRequest(BaseModel):
    """Request model for fatwa search."""
    query: str = Field(..., min_length=1, description="User's question in Arabic")
    limit: int = Field(default=5, ge=1, le=10, description="Maximum number of results")
    shaykh_filter: Optional[str] = Field(None, description="Filter by shaykh name")


class FatwaResponse(BaseModel):
    """Single fatwa response with metadata."""
    question: str = Field(..., description="Original question from database")
    answer: str = Field(..., description="Original fatwa answer")
    shaykh: str = Field(..., description="Shaykh name")
    series: str = Field(..., description="Series name")
    link: str = Field(..., description="Source URL")
    confidence_score: Optional[float] = Field(None, description="Relevance score")


class SearchResponse(BaseModel):
    """Response model for fatwa search."""
    found: bool = Field(..., description="Whether matching fatwas were found")
    confidence: Optional[float] = Field(None, description="Top result confidence score")
    fatwa: Optional[FatwaResponse] = Field(None, description="Main fatwa result")
    other_results: List[FatwaResponse] = Field(default=[], description="Additional relevant fatwas")
    message: Optional[str] = Field(None, description="Message when no results found")
    suggestions: List[str] = Field(default=[], description="Suggestions for user")


class FatwaDetail(BaseModel):
    """Fatwa detail from database."""
    id: UUID
    category: str
    question: str
    answer: str
    link: str
    shaykh_id: UUID
    series_id: UUID
    shaykh_name: Optional[str] = None
    series_name: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    qdrant_connected: bool
    supabase_connected: bool
    embedding_model_loaded: bool
