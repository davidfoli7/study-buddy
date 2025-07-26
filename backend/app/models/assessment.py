from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Assessment details
    title = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    topic = Column(String, nullable=True)
    assessment_type = Column(String, nullable=False)  # diagnostic, formative, summative, adaptive
    difficulty_level = Column(String, default="medium")
    
    # Timing
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    time_limit_minutes = Column(Integer, nullable=True)
    time_taken_minutes = Column(Float, nullable=True)
    
    # Scoring
    total_questions = Column(Integer, default=0)
    questions_answered = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    score_percentage = Column(Float, nullable=True)
    max_possible_score = Column(Float, default=100.0)
    
    # Adaptive features
    initial_difficulty = Column(String, nullable=True)
    final_difficulty = Column(String, nullable=True)
    difficulty_adjustments = Column(Integer, default=0)
    
    # AI Analysis
    strengths = Column(Text, nullable=True)  # JSON string of identified strengths
    weaknesses = Column(Text, nullable=True)  # JSON string of identified weaknesses
    recommendations = Column(Text, nullable=True)  # AI-generated study recommendations
    learning_style_indicators = Column(Text, nullable=True)  # JSON data about learning style
    
    # Status
    status = Column(String, default="not_started")  # not_started, in_progress, completed, abandoned
    is_completed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="assessments")
    questions = relationship("Question", back_populates="assessment", cascade="all, delete-orphan")
    answers = relationship("Answer", back_populates="assessment", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Assessment(id={self.id}, title='{self.title}', user_id={self.user_id}, score={self.score_percentage}%)>"


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    
    # Question content
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)  # multiple_choice, true_false, short_answer, essay, fill_blank
    difficulty_level = Column(String, default="medium")
    subject = Column(String, nullable=False)
    topic = Column(String, nullable=True)
    
    # Multiple choice specifics
    options = Column(Text, nullable=True)  # JSON string of options for multiple choice
    correct_answer = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    
    # Scoring
    points_possible = Column(Float, default=1.0)
    
    # Metadata
    bloom_taxonomy_level = Column(String, nullable=True)  # remember, understand, apply, analyze, evaluate, create
    learning_objective = Column(String, nullable=True)
    tags = Column(Text, nullable=True)  # JSON string of tags
    
    # AI-generated metadata
    estimated_time_seconds = Column(Integer, nullable=True)
    difficulty_score = Column(Float, nullable=True)  # 0-1 AI-calculated difficulty
    
    # Usage statistics
    times_asked = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    average_time_taken = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    assessment = relationship("Assessment", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Question(id={self.id}, type='{self.question_type}', difficulty='{self.difficulty_level}')>"


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Answer content
    answer_text = Column(Text, nullable=True)
    selected_option = Column(String, nullable=True)  # For multiple choice
    
    # Scoring
    is_correct = Column(Boolean, nullable=True)
    points_earned = Column(Float, default=0.0)
    points_possible = Column(Float, default=1.0)
    
    # Timing
    time_taken_seconds = Column(Float, nullable=True)
    answered_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # AI Analysis
    confidence_level = Column(Float, nullable=True)  # 0-1, AI-estimated student confidence
    reasoning_quality = Column(Float, nullable=True)  # For essay/short answer, AI assessment
    ai_feedback = Column(Text, nullable=True)
    
    # Behavioral data
    hesitation_time = Column(Float, nullable=True)  # Time before starting to answer
    revision_count = Column(Integer, default=0)  # Number of times answer was changed
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    assessment = relationship("Assessment", back_populates="answers")
    question = relationship("Question", back_populates="answers")

    def __repr__(self):
        return f"<Answer(id={self.id}, question_id={self.question_id}, is_correct={self.is_correct}, points={self.points_earned})>"