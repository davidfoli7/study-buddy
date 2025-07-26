from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Recommendation details
    recommendation_type = Column(String, nullable=False)  # content, study_plan, assessment, break, review
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String, default="medium")  # low, medium, high, urgent
    category = Column(String, nullable=False)  # subject, skill, habit, wellness, etc.
    
    # Target references
    target_content_id = Column(Integer, ForeignKey("content.id"), nullable=True)
    target_assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=True)
    target_learning_session_id = Column(Integer, ForeignKey("learning_sessions.id"), nullable=True)
    
    # Recommendation parameters
    estimated_time_minutes = Column(Integer, nullable=True)
    difficulty_level = Column(String, nullable=True)  # easy, medium, hard
    optimal_time_of_day = Column(String, nullable=True)  # morning, afternoon, evening
    
    # AI reasoning and confidence
    reasoning = Column(Text, nullable=False)  # Why this recommendation was made
    confidence_score = Column(Float, nullable=False)  # 0-1, AI confidence in recommendation
    model_version = Column(String, nullable=True)  # Version of the recommendation model used
    
    # User interaction tracking
    is_viewed = Column(Boolean, default=False)
    is_accepted = Column(Boolean, nullable=True)  # True=accepted, False=declined, None=not responded
    is_completed = Column(Boolean, default=False)
    
    # Timestamps for interaction
    viewed_at = Column(DateTime(timezone=True), nullable=True)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Performance tracking
    effectiveness_score = Column(Float, nullable=True)  # Post-completion assessment of usefulness
    user_rating = Column(Integer, nullable=True)  # 1-5 user rating of recommendation
    actual_time_taken = Column(Integer, nullable=True)  # Minutes actually spent
    
    # Context data
    context_data = Column(Text, nullable=True)  # JSON string of contextual factors
    trigger_event = Column(String, nullable=True)  # What triggered this recommendation
    personalization_factors = Column(Text, nullable=True)  # JSON of personalization data used
    
    # A/B testing and experimentation
    experiment_group = Column(String, nullable=True)  # For A/B testing different recommendation strategies
    variant_id = Column(String, nullable=True)  # Specific variant within experiment
    
    # Status and lifecycle
    status = Column(String, default="pending")  # pending, active, completed, expired, declined
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="recommendations")
    target_content = relationship("Content", foreign_keys=[target_content_id])
    target_assessment = relationship("Assessment", foreign_keys=[target_assessment_id])
    target_learning_session = relationship("LearningSession", foreign_keys=[target_learning_session_id])

    def __repr__(self):
        return f"<Recommendation(id={self.id}, user_id={self.user_id}, type='{self.recommendation_type}', title='{self.title}')>"