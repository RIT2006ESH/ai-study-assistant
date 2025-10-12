from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class SummaryLevel(str, Enum):
    """Summary detail level"""
    BRIEF = "brief"
    MODERATE = "moderate"
    DETAILED = "detailed"


class SummaryRequest(BaseModel):
    """Schema for summary request"""
    level: SummaryLevel = Field(
        default=SummaryLevel.MODERATE,
        description="Level of detail for the summary"
    )
    focus_areas: Optional[List[str]] = Field(
        default=None,
        description="Optional list of topics to focus on in the summary"
    )


class SummaryResponse(BaseModel):
    """Schema for summary response"""
    document_id: int
    summary: str
    level: SummaryLevel
    word_count: int
    original_length: int
    
    class Config:
        from_attributes = True


class KeyPointsResponse(BaseModel):
    """Schema for key points extraction response"""
    document_id: int
    key_points: str
