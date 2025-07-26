from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class LearningStyle(Base):
    __tablename__ = "learning_styles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # VARK Model Scores (0-1 scale)
    visual_score = Column(Float, default=0.25)  # Visual learner preference
    auditory_score = Column(Float, default=0.25)  # Auditory learner preference
    reading_score = Column(Float, default=0.25)  # Reading/writing learner preference
    kinesthetic_score = Column(Float, default=0.25)  # Kinesthetic learner preference
    
    # Additional Learning Preferences
    social_vs_solitary = Column(Float, default=0.5)  # 0 = solitary, 1 = social
    sequential_vs_global = Column(Float, default=0.5)  # 0 = sequential, 1 = global
    active_vs_reflective = Column(Float, default=0.5)  # 0 = reflective, 1 = active
    sensing_vs_intuitive = Column(Float, default=0.5)  # 0 = intuitive, 1 = sensing
    
    # Dominant Learning Style
    dominant_style = Column(String, nullable=True)  # visual, auditory, reading, kinesthetic, multimodal
    
    # Learning Environment Preferences
    preferred_pace = Column(String, default="medium")  # slow, medium, fast, self_paced
    preferred_complexity = Column(String, default="gradual")  # immediate, gradual, complex
    preferred_feedback_frequency = Column(String, default="moderate")  # immediate, moderate, delayed
    
    # Engagement Patterns
    attention_span_minutes = Column(Integer, default=30)
    break_frequency_minutes = Column(Integer, default=25)  # Pomodoro-style preferences
    optimal_session_length = Column(Integer, default=60)
    
    # Confidence Levels (0-1 scale)
    confidence_score = Column(Float, default=0.5)
    accuracy_confidence = Column(Float, default=0.8)  # How accurate this assessment is
    
    # Assessment metadata
    assessment_method = Column(String, default="behavioral")  # survey, behavioral, hybrid
    data_points_count = Column(Integer, default=0)  # Number of interactions used for assessment
    last_updated_method = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="learning_style_assessments")
    assessments = relationship("LearningStyleAssessment", back_populates="learning_style")

    def __repr__(self):
        return f"<LearningStyle(id={self.id}, user_id={self.user_id}, dominant='{self.dominant_style}')>"


class LearningStyleAssessment(Base):
    __tablename__ = "learning_style_assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    learning_style_id = Column(Integer, ForeignKey("learning_styles.id"), nullable=True)
    
    # Assessment details
    assessment_type = Column(String, nullable=False)  # initial_survey, behavioral_analysis, periodic_update
    assessment_name = Column(String, nullable=True)  # VARK, Kolb, Honey-Mumford, custom
    
    # Survey responses (if applicable)
    survey_responses = Column(Text, nullable=True)  # JSON string of question-answer pairs
    
    # Behavioral data analysis
    content_interaction_period_days = Column(Integer, nullable=True)
    interactions_analyzed = Column(Integer, default=0)
    assessment_period_start = Column(DateTime(timezone=True), nullable=True)
    assessment_period_end = Column(DateTime(timezone=True), nullable=True)
    
    # Results
    visual_indicators = Column(Text, nullable=True)  # JSON of specific behaviors indicating visual preference
    auditory_indicators = Column(Text, nullable=True)  # JSON of specific behaviors indicating auditory preference
    reading_indicators = Column(Text, nullable=True)  # JSON of specific behaviors indicating reading preference
    kinesthetic_indicators = Column(Text, nullable=True)  # JSON of specific behaviors indicating kinesthetic preference
    
    # Confidence and reliability
    confidence_score = Column(Float, nullable=True)  # 0-1, how confident we are in this assessment
    reliability_score = Column(Float, nullable=True)  # 0-1, based on consistency of data
    
    # Machine learning model info
    model_version = Column(String, nullable=True)
    model_accuracy = Column(Float, nullable=True)
    feature_importance = Column(Text, nullable=True)  # JSON of which features were most important
    
    # Insights and recommendations
    key_insights = Column(Text, nullable=True)  # JSON of key findings
    learning_recommendations = Column(Text, nullable=True)  # JSON of specific recommendations
    content_type_preferences = Column(Text, nullable=True)  # JSON mapping content types to preference scores
    
    # Status
    status = Column(String, default="in_progress")  # in_progress, completed, needs_review
    is_baseline = Column(Boolean, default=False)  # Is this the initial baseline assessment?
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="learning_style_assessments")
    learning_style = relationship("LearningStyle", back_populates="assessments")

    def __repr__(self):
        return f"<LearningStyleAssessment(id={self.id}, user_id={self.user_id}, type='{self.assessment_type}', status='{self.status}')>"