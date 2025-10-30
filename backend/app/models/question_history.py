from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class QuestionHistory(Base):
    """Model to store user's question analysis history"""
    __tablename__ = "question_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    subject = Column(String(50), default="general", index=True)
    solution = Column(Text, nullable=True)
    image_filename = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to User
    user = relationship("User", back_populates="question_history")
    
    def __repr__(self):
        return f"<QuestionHistory(id={self.id}, user_id={self.user_id}, subject={self.subject})>"
