from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Subject and topic tracking
    subject = Column(String, nullable=False)
    topic = Column(String, nullable=True)
    subtopic = Column(String, nullable=True)
    
    # Skill and mastery levels
    skill_level = Column(Float, default=0.0)  # 0-100, current skill level
    mastery_score = Column(Float, default=0.0)  # 0-100, mastery of this topic
    confidence_level = Column(Float, default=0.0)  # 0-100, student's confidence
    
    # Time tracking
    time_spent_minutes = Column(Integer, default=0)
    effective_study_time = Column(Integer, default=0)  # Time spent actively engaged
    last_studied_at = Column(DateTime(timezone=True), nullable=True)
    
    # Streak and consistency
    streak_days = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    study_frequency_score = Column(Float, default=0.0)  # 0-1, consistency metric
    
    # Performance metrics
    total_sessions = Column(Integer, default=0)
    completed_sessions = Column(Integer, default=0)
    average_session_score = Column(Float, default=0.0)
    best_session_score = Column(Float, default=0.0)
    worst_session_score = Column(Float, nullable=True)
    
    # Improvement tracking
    improvement_rate = Column(Float, default=0.0)  # Rate of improvement over time
    learning_velocity = Column(Float, default=0.0)  # Speed of learning new concepts
    retention_score = Column(Float, default=0.0)  # 0-100, how well knowledge is retained
    
    # Difficulty progression
    current_difficulty = Column(String, default="easy")  # easy, medium, hard
    max_difficulty_reached = Column(String, default="easy")
    difficulty_progression_rate = Column(Float, default=0.0)
    
    # Assessment performance
    total_assessments = Column(Integer, default=0)
    passed_assessments = Column(Integer, default=0)
    average_assessment_score = Column(Float, default=0.0)
    assessment_improvement_trend = Column(Float, default=0.0)
    
    # Predictive analytics
    predicted_mastery_date = Column(DateTime(timezone=True), nullable=True)
    predicted_next_milestone = Column(String, nullable=True)
    predicted_time_to_milestone = Column(Integer, nullable=True)  # Days
    learning_curve_classification = Column(String, nullable=True)  # fast, normal, slow, plateau
    
    # Content interaction patterns
    preferred_content_types = Column(Text, nullable=True)  # JSON of content type preferences
    learning_style_alignment = Column(Float, default=0.0)  # How well content matches learning style
    
    # Goals and targets
    target_skill_level = Column(Float, nullable=True)
    target_completion_date = Column(DateTime(timezone=True), nullable=True)
    is_goal_set = Column(Boolean, default=False)
    goal_progress_percentage = Column(Float, default=0.0)
    
    # Status tracking
    is_completed = Column(Boolean, default=False)
    is_mastered = Column(Boolean, default=False)
    needs_review = Column(Boolean, default=False)
    is_struggling = Column(Boolean, default=False)  # AI-detected struggling pattern
    
    # AI insights
    ai_insights = Column(Text, nullable=True)  # JSON of AI-generated insights
    recommended_actions = Column(Text, nullable=True)  # JSON of recommended next steps
    risk_factors = Column(Text, nullable=True)  # JSON of identified risk factors
    strength_areas = Column(Text, nullable=True)  # JSON of identified strengths
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="progress_records")

    def __repr__(self):
        return f"<Progress(id={self.id}, user_id={self.user_id}, subject='{self.subject}', mastery={self.mastery_score}%)>"


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Achievement details
    achievement_type = Column(String, nullable=False)  # streak, mastery, assessment, time, consistency, improvement
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    badge_icon = Column(String, nullable=True)  # Icon identifier for the badge
    
    # Achievement criteria
    category = Column(String, nullable=False)  # study_time, assessment_score, streak, mastery, etc.
    threshold_value = Column(Float, nullable=True)  # Numeric threshold for achievement
    threshold_unit = Column(String, nullable=True)  # days, hours, points, percentage, etc.
    
    # Subject/topic specificity
    subject = Column(String, nullable=True)  # Null for global achievements
    topic = Column(String, nullable=True)
    
    # Achievement metadata
    difficulty_level = Column(String, default="medium")  # easy, medium, hard, legendary
    rarity = Column(String, default="common")  # common, uncommon, rare, epic, legendary
    points_awarded = Column(Integer, default=10)  # Gamification points
    
    # Progress tracking
    current_progress = Column(Float, default=0.0)  # Current progress towards achievement
    required_progress = Column(Float, nullable=False)  # Required progress to unlock
    progress_percentage = Column(Float, default=0.0)  # Percentage complete
    
    # Status and timing
    is_unlocked = Column(Boolean, default=False)
    is_hidden = Column(Boolean, default=False)  # Hidden until certain conditions are met
    unlocked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Context and evidence
    trigger_event = Column(String, nullable=True)  # What triggered this achievement
    evidence_data = Column(Text, nullable=True)  # JSON of supporting data
    related_session_id = Column(Integer, ForeignKey("learning_sessions.id"), nullable=True)
    related_assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=True)
    
    # Sharing and social features
    is_shared = Column(Boolean, default=False)
    shared_at = Column(DateTime(timezone=True), nullable=True)
    celebration_shown = Column(Boolean, default=False)
    
    # Achievement series (for progressive achievements)
    series_name = Column(String, nullable=True)  # e.g., "Study Streak Master"
    series_level = Column(Integer, nullable=True)  # Level within the series
    next_level_threshold = Column(Float, nullable=True)
    
    # Expiration (for time-limited achievements)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_expired = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="achievements")
    related_session = relationship("LearningSession", foreign_keys=[related_session_id])
    related_assessment = relationship("Assessment", foreign_keys=[related_assessment_id])

    def __repr__(self):
        return f"<Achievement(id={self.id}, user_id={self.user_id}, title='{self.title}', unlocked={self.is_unlocked})>"