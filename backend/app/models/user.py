from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Profile information
    bio = Column(Text, nullable=True)
    avatar_url = Column(String, nullable=True)
    grade_level = Column(String, nullable=True)  # e.g., "High School", "College", "Graduate"
    subjects_of_interest = Column(Text, nullable=True)  # JSON string of subjects
    
    # Learning preferences
    preferred_difficulty = Column(String, default="medium")  # easy, medium, hard
    daily_study_goal_minutes = Column(Integer, default=60)
    preferred_study_time = Column(String, nullable=True)  # morning, afternoon, evening
    
    # Analytics
    total_study_time_minutes = Column(Integer, default=0)
    total_assessments_completed = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    streak_days = Column(Integer, default=0)
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships will be defined in other models to avoid circular imports

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"