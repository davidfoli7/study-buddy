from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Session details
    subject = Column(String, nullable=False)
    topic = Column(String, nullable=True)
    session_type = Column(String, nullable=False)  # study, assessment, review, practice
    difficulty_level = Column(String, default="medium")  # easy, medium, hard
    
    # Time tracking
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    planned_duration_minutes = Column(Integer, default=60)
    
    # Performance metrics
    completion_percentage = Column(Float, default=0.0)
    focus_score = Column(Float, nullable=True)  # 0-100, based on engagement metrics
    comprehension_score = Column(Float, nullable=True)  # 0-100, based on assessments
    
    # Session data
    activities_completed = Column(Integer, default=0)
    total_activities = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    ai_insights = Column(Text, nullable=True)  # AI-generated insights about the session
    
    # Adaptive learning data
    initial_difficulty = Column(String, nullable=True)
    final_difficulty = Column(String, nullable=True)
    adaptations_made = Column(Integer, default=0)
    
    # Status
    is_completed = Column(Boolean, default=False)
    is_interrupted = Column(Boolean, default=False)
    interruption_reason = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="learning_sessions")
    content_interactions = relationship("ContentInteraction", back_populates="learning_session")

    def __repr__(self):
        return f"<LearningSession(id={self.id}, user_id={self.user_id}, subject='{self.subject}', type='{self.session_type}')>"