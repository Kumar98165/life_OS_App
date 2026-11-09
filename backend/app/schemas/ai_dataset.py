"""LifeOS - AI Dataset Management Schemas (Step 7).

Pydantic v2 validation models for dataset record filtering, curation reviews,
snapshot version creation, and JSONL dataset exports.
"""
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


class DatasetSampleFilterQuery(BaseModel):
    """Query parameters for listing and filtering dataset samples."""
    category: Optional[str] = Field(None, max_length=50)
    validation_status: Optional[Literal["pending", "valid", "invalid"]] = None
    sanitization_status: Optional[Literal["pending", "sanitized", "rejected"]] = None
    review_status: Optional[Literal["pending", "approved", "rejected"]] = None
    consent_status: Optional[Literal["pending", "granted", "revoked"]] = None
    dataset_version_id: Optional[str] = Field(None, min_length=36, max_length=36)
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)


class ReviewSampleRequest(BaseModel):
    """Payload for approving or rejecting a candidate training sample."""
    review_status: Literal["approved", "rejected"]
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    validation_notes: Optional[str] = Field(None, max_length=1000)


class CreateDatasetVersionRequest(BaseModel):
    """Payload for creating an immutable versioned snapshot of approved samples."""
    version_name: str = Field(..., min_length=2, max_length=50, pattern=r'^[a-zA-Z0-9_\-\.]+$')
    description: Optional[str] = Field(None, max_length=255)
    dataset_type: Literal["sft", "dpo", "mixed"] = "sft"
    categories: Optional[List[str]] = None


class DatasetVersionResponse(BaseModel):
    """Response schema for a dataset version snapshot."""
    id: str
    version_name: str
    description: Optional[str] = None
    sample_count: int
    dataset_type: str
    manifest_hash: str
    included_categories: List[str] = []
    validation_summary: Dict[str, Any] = {}
    is_exported: bool
    exported_at: Optional[str] = None
    created_at: Optional[str] = None
