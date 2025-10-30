# app/models/question.py
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Question(Base):
    """Model for storing uploaded questions and their solutions"""
    
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Image and text data
    image_path = Column(String(500), nullable=False)
    question_text = Column(Text, nullable=False)
    
    # Classification
    subject = Column(String(100), nullable=True, index=True)
    difficulty_level = Column(String(20), default="medium")  # easy, medium, hard
    
    # Solution data
    solution = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    steps = Column(JSON, default=list)  # List of solution steps
    
    # Metadata
    confidence_score = Column(Float, default=0.0)  # AI confidence in solution
    is_bookmarked = Column(Integer, default=0)  # User bookmark
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="questions")
    
    def __repr__(self):
        return f"<Question(id={self.id}, subject={self.subject}, user_id={self.user_id})>"
