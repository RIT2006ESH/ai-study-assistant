"""
Document model for storing uploaded study materials
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class DocumentType(str, enum.Enum):
    """Document type enumeration"""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


class ProcessingStatus(str, enum.Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base):
    """Document model for user-uploaded study materials"""
    
    __tablename__ = "documents"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to user
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Document metadata
    title = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)  # S3 path or local path
    file_size = Column(Integer, nullable=False)  # Size in bytes
    document_type = Column(Enum(DocumentType), nullable=False)
    mime_type = Column(String(100), nullable=False)
    
    # Processing status
    processing_status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING, nullable=False)
    processing_error = Column(Text, nullable=True)
    
    # Extracted content
    extracted_text = Column(Text, nullable=True)
    text_length = Column(Integer, default=0)
    page_count = Column(Integer, nullable=True)
    
    # Vector embeddings metadata
    is_indexed = Column(Boolean, default=False, nullable=False)
    vector_store_id = Column(String(255), nullable=True)  # ID in Pinecone/Chroma
    chunk_count = Column(Integer, default=0)
    
    # Subject classification
    subject = Column(String(100), nullable=True)  # e.g., "Mathematics", "Physics"
    topic = Column(String(255), nullable=True)
    difficulty_level = Column(String(50), nullable=True)  # "beginner", "intermediate", "advanced"
    
    # Usage statistics
    view_count = Column(Integer, default=0)
    question_count = Column(Integer, default=0)
    summary_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="documents")
    conversations = relationship("Conversation", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title}, type={self.document_type})>"
    
    def to_dict(self) -> dict:
        """Convert document to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "document_type": self.document_type.value,
            "processing_status": self.processing_status.value,
            "is_indexed": self.is_indexed,
            "page_count": self.page_count,
            "text_length": self.text_length,
            "subject": self.subject,
            "topic": self.topic,
            "difficulty_level": self.difficulty_level,
            "view_count": self.view_count,
            "question_count": self.question_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
        }