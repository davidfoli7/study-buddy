from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class Content(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    
    # Content details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    content_type = Column(String, nullable=False)  # video, article, interactive, quiz, document, audio
    format = Column(String, nullable=True)  # pdf, mp4, html, etc.
    
    # Educational metadata
    subject = Column(String, nullable=False)
    topic = Column(String, nullable=True)
    subtopic = Column(String, nullable=True)
    difficulty_level = Column(String, default="medium")  # easy, medium, hard, expert
    grade_level = Column(String, nullable=True)
    learning_objectives = Column(Text, nullable=True)  # JSON string of objectives
    
    # Content location
    url = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    external_source = Column(String, nullable=True)  # youtube, khan_academy, coursera, etc.
    
    # AI-generated metadata
    estimated_duration_minutes = Column(Integer, nullable=True)
    complexity_score = Column(Float, nullable=True)  # 0-1 AI-calculated complexity
    readability_score = Column(Float, nullable=True)  # Flesch-Kincaid or similar
    key_concepts = Column(Text, nullable=True)  # JSON string of key concepts
    prerequisites = Column(Text, nullable=True)  # JSON string of prerequisite topics
    
    # Learning style compatibility
    visual_score = Column(Float, default=0.0)  # 0-1 suitability for visual learners
    auditory_score = Column(Float, default=0.0)  # 0-1 suitability for auditory learners
    kinesthetic_score = Column(Float, default=0.0)  # 0-1 suitability for kinesthetic learners
    reading_score = Column(Float, default=0.0)  # 0-1 suitability for reading/writing learners
    
    # Quality metrics
    accuracy_score = Column(Float, nullable=True)  # AI-verified accuracy
    engagement_score = Column(Float, nullable=True)  # Based on user interactions
    average_rating = Column(Float, nullable=True)
    total_ratings = Column(Integer, default=0)
    
    # Usage statistics
    view_count = Column(Integer, default=0)
    completion_count = Column(Integer, default=0)
    average_completion_rate = Column(Float, nullable=True)
    average_time_spent = Column(Float, nullable=True)
    
    # Content management
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    author = Column(String, nullable=True)
    source_attribution = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    interactions = relationship("ContentInteraction", back_populates="content")

    def __repr__(self):
        return f"<Content(id={self.id}, title='{self.title}', type='{self.content_type}', subject='{self.subject}')>"


class ContentInteraction(Base):
    __tablename__ = "content_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    learning_session_id = Column(Integer, ForeignKey("learning_sessions.id"), nullable=True)
    
    # Interaction details
    interaction_type = Column(String, nullable=False)  # view, complete, bookmark, rate, comment, share
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Progress tracking
    progress_percentage = Column(Float, default=0.0)
    last_position = Column(String, nullable=True)  # For videos: timestamp, for documents: page/section
    is_completed = Column(Boolean, default=False)
    completion_time = Column(DateTime(timezone=True), nullable=True)
    
    # Engagement metrics
    interaction_count = Column(Integer, default=1)  # Number of clicks, pauses, etc.
    focus_time_seconds = Column(Float, nullable=True)  # Active engagement time
    idle_time_seconds = Column(Float, nullable=True)  # Time spent idle
    
    # User feedback
    rating = Column(Integer, nullable=True)  # 1-5 stars
    difficulty_rating = Column(String, nullable=True)  # too_easy, just_right, too_hard
    usefulness_rating = Column(Integer, nullable=True)  # 1-5 scale
    notes = Column(Text, nullable=True)
    
    # Learning outcomes
    comprehension_score = Column(Float, nullable=True)  # Post-content assessment score
    retention_score = Column(Float, nullable=True)  # Long-term retention assessment
    application_score = Column(Float, nullable=True)  # Ability to apply learned concepts
    
    # AI insights
    learning_style_match = Column(Float, nullable=True)  # How well content matched user's style
    predicted_effectiveness = Column(Float, nullable=True)  # AI prediction of learning effectiveness
    actual_effectiveness = Column(Float, nullable=True)  # Measured effectiveness post-learning
    
    # Behavioral data
    device_type = Column(String, nullable=True)  # desktop, tablet, mobile
    location = Column(String, nullable=True)  # general location if available
    time_of_day = Column(String, nullable=True)  # morning, afternoon, evening, night
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="content_interactions")
    content = relationship("Content", back_populates="interactions")
    learning_session = relationship("LearningSession", back_populates="content_interactions")

    def __repr__(self):
        return f"<ContentInteraction(id={self.id}, user_id={self.user_id}, content_id={self.content_id}, type='{self.interaction_type}')>"