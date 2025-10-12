from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Document type enumeration"""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


class ProcessingStatus(str, Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentCreate(BaseModel):
    title: str
    content: str
    file_path: Optional[str] = None


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    subject: Optional[str] = None
    topic: Optional[str] = None
    difficulty_level: Optional[str] = None


class DocumentResponse(BaseModel):
    id: int
    user_id: int
    title: str
    original_filename: str
    file_path: str
    file_size: int
    document_type: DocumentType
    mime_type: str
    processing_status: ProcessingStatus
    processing_error: Optional[str] = None
    extracted_text: Optional[str] = None
    text_length: int
    page_count: Optional[int] = None
    is_indexed: bool
    vector_store_id: Optional[str] = None
    chunk_count: int
    subject: Optional[str] = None
    topic: Optional[str] = None
    difficulty_level: Optional[str] = None
    view_count: int
    question_count: int
    summary_count: int
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    id: int
    user_id: int
    title: str
    original_filename: str
    file_size: int
    document_type: DocumentType
    processing_status: ProcessingStatus
    subject: Optional[str] = None
    topic: Optional[str] = None
    view_count: int
    created_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True