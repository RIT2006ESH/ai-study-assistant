# app/schemas/question.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class QuestionBase(BaseModel):
    """Base question schema"""
    question_text: str
    subject: Optional[str] = None
    difficulty_level: Optional[str] = "medium"


class QuestionCreate(QuestionBase):
    """Schema for creating a new question"""
    image_path: str
    solution: str
    explanation: Optional[str] = None
    steps: Optional[List[str]] = []
    confidence_score: Optional[float] = 0.0


class QuestionResponse(BaseModel):
    """Schema for question response"""
    id: int
    user_id: int
    image_path: str
    question_text: str
    subject: Optional[str]
    difficulty_level: str
    solution: str
    explanation: Optional[str]
    steps: List[str]
    confidence_score: float
    is_bookmarked: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class QuestionListResponse(BaseModel):
    """Schema for paginated question list"""
    questions: List[QuestionResponse]
    total: int
    skip: int
    limit: int


class QuestionUpdate(BaseModel):
    """Schema for updating a question"""
    is_bookmarked: Optional[int] = None
    subject: Optional[str] = None


class SolutionResponse(BaseModel):
    """Schema for solution details"""
    answer: str
    explanation: str
    steps: List[str]
    confidence: float
    difficulty: str
    subject: str
