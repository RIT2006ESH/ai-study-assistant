"""
Learning profile model for tracking user progress
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class LearningProfile(Base):
    """Learning profile model for user study analytics"""

    __tablename__ = "learning_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Study statistics
    total_study_time = Column(Integer, default=0)  # in minutes
    documents_studied = Column(Integer, default=0)
    questions_asked = Column(Integer, default=0)
    problems_solved = Column(Integer, default=0)
    
    # Preferences
    preferred_subjects = Column(JSON, nullable=True)  # List of subjects
    learning_style = Column(String(50), nullable=True)  # visual, auditory, kinesthetic
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="learning_profile")

    def __repr__(self):
        return f"<LearningProfile(id={self.id}, user_id={self.user_id})>"