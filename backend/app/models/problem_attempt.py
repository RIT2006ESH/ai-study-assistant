"""
Problem attempt model for tracking solved problems
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class ProblemType(str, enum.Enum):
    """Problem type enumeration"""
    MATH = "math"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"
    PROGRAMMING = "programming"
    OTHER = "other"


class ProblemAttempt(Base):
    """Problem attempt model for tracking solved problems"""

    __tablename__ = "problem_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Problem details
    problem_type = Column(Enum(ProblemType), nullable=False)
    problem_text = Column(Text, nullable=False)
    solution = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=True)
    
    # Metadata
    difficulty = Column(String(50), nullable=True)
    time_taken = Column(Integer, nullable=True)  # in seconds
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="problem_attempts")

    def __repr__(self):
        return f"<ProblemAttempt(id={self.id}, type={self.problem_type})>"