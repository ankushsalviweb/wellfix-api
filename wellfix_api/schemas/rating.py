"""
Rating schema definitions.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# Base Rating schema for common attributes
class RatingBase(BaseModel):
    """Base schema for rating attributes."""
    score: int = Field(..., description="Rating score (1-5)", ge=1, le=5)
    comment: Optional[str] = Field(None, description="Optional comment on the rating")


# Schema for creating a new rating
class RatingCreate(RatingBase):
    """Schema for creating a new rating."""
    pass


# Schema for reading a rating
class RatingResponse(RatingBase):
    """Schema for reading a rating."""
    id: int
    job_id: int
    customer_id: str
    engineer_id: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Schema for listing ratings
class RatingListResponse(BaseModel):
    """Schema for listing ratings with pagination."""
    ratings: list[RatingResponse]
    count: int
    page: int
    size: int
    
    model_config = ConfigDict(from_attributes=True) 