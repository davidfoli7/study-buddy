from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
from pydantic import BaseModel

from ..core.database import get_db
from ..models.user import User
from ..models.learning_session import LearningSession
from ..models.content import Content, ContentInteraction
from .auth import get_current_user

router = APIRouter()


class LearningSessionCreate(BaseModel):
    subject: str
    topic: Optional[str] = None
    session_type: str  # study, assessment, review, practice
    difficulty_level: str = "medium"
    planned_duration_minutes: int = 60


class LearningSessionResponse(BaseModel):
    id: int
    subject: str
    topic: Optional[str]
    session_type: str
    difficulty_level: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_minutes: Optional[int]
    planned_duration_minutes: int
    completion_percentage: float
    focus_score: Optional[float]
    comprehension_score: Optional[float]
    activities_completed: int
    total_activities: int
    is_completed: bool
    notes: Optional[str]
    ai_insights: Optional[str]
    
    class Config:
        from_attributes = True


class LearningSessionUpdate(BaseModel):
    end_time: Optional[datetime] = None
    completion_percentage: Optional[float] = None
    focus_score: Optional[float] = None
    comprehension_score: Optional[float] = None
    activities_completed: Optional[int] = None
    total_activities: Optional[int] = None
    notes: Optional[str] = None
    is_completed: Optional[bool] = None


class StudyPlanResponse(BaseModel):
    recommended_sessions: List[dict]
    daily_goal_progress: float
    weekly_schedule: List[dict]
    next_review_topics: List[str]


@router.post("/sessions", response_model=LearningSessionResponse)
async def create_learning_session(
    session_data: LearningSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new learning session"""
    session = LearningSession(
        user_id=current_user.id,
        subject=session_data.subject,
        topic=session_data.topic,
        session_type=session_data.session_type,
        difficulty_level=session_data.difficulty_level,
        planned_duration_minutes=session_data.planned_duration_minutes
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session


@router.get("/sessions", response_model=List[LearningSessionResponse])
async def get_learning_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=20, le=100),
    skip: int = Query(default=0, ge=0),
    subject: Optional[str] = Query(default=None),
    session_type: Optional[str] = Query(default=None)
):
    """Get user's learning sessions with optional filtering"""
    query = db.query(LearningSession).filter(LearningSession.user_id == current_user.id)
    
    if subject:
        query = query.filter(LearningSession.subject == subject)
    if session_type:
        query = query.filter(LearningSession.session_type == session_type)
    
    sessions = query.order_by(desc(LearningSession.start_time)).offset(skip).limit(limit).all()
    return sessions


@router.get("/sessions/{session_id}", response_model=LearningSessionResponse)
async def get_learning_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific learning session"""
    session = db.query(LearningSession).filter(
        and_(
            LearningSession.id == session_id,
            LearningSession.user_id == current_user.id
        )
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning session not found"
        )
    
    return session


@router.put("/sessions/{session_id}", response_model=LearningSessionResponse)
async def update_learning_session(
    session_id: int,
    session_update: LearningSessionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a learning session"""
    session = db.query(LearningSession).filter(
        and_(
            LearningSession.id == session_id,
            LearningSession.user_id == current_user.id
        )
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning session not found"
        )
    
    # Update fields if provided
    update_data = session_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(session, field, value)
    
    # Calculate duration if end_time is provided
    if session_update.end_time and session.start_time:
        duration = session_update.end_time - session.start_time
        session.duration_minutes = int(duration.total_seconds() / 60)
    
    db.commit()
    db.refresh(session)
    
    return session


@router.post("/sessions/{session_id}/complete")
async def complete_learning_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a learning session as completed"""
    session = db.query(LearningSession).filter(
        and_(
            LearningSession.id == session_id,
            LearningSession.user_id == current_user.id
        )
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning session not found"
        )
    
    session.is_completed = True
    session.end_time = datetime.utcnow()
    session.completion_percentage = 100.0
    
    if session.start_time:
        duration = session.end_time - session.start_time
        session.duration_minutes = int(duration.total_seconds() / 60)
    
    # Update user's total study time
    if session.duration_minutes:
        current_user.total_study_time_minutes += session.duration_minutes
    
    db.commit()
    db.refresh(session)
    
    return {"message": "Learning session completed successfully", "session": session}


@router.get("/study-plan", response_model=StudyPlanResponse)
async def get_study_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-generated personalized study plan"""
    # Get recent learning patterns
    recent_sessions = db.query(LearningSession).filter(
        and_(
            LearningSession.user_id == current_user.id,
            LearningSession.start_time >= datetime.utcnow() - timedelta(days=30)
        )
    ).order_by(desc(LearningSession.start_time)).limit(50).all()
    
    # Calculate daily goal progress
    today = datetime.utcnow().date()
    today_sessions = [s for s in recent_sessions if s.start_time.date() == today]
    today_minutes = sum([s.duration_minutes or 0 for s in today_sessions])
    daily_goal_progress = min(today_minutes / current_user.daily_study_goal_minutes * 100, 100)
    
    # Generate recommended sessions based on user's subjects of interest
    subjects = []
    if current_user.subjects_of_interest:
        subjects = current_user.subjects_of_interest.split(",")
    
    recommended_sessions = []
    for subject in subjects[:3]:  # Limit to top 3 subjects
        recommended_sessions.append({
            "subject": subject.strip(),
            "recommended_duration": 30,
            "difficulty": current_user.preferred_difficulty,
            "session_type": "study",
            "priority": "medium"
        })
    
    # Generate weekly schedule (simplified)
    weekly_schedule = []
    for i in range(7):
        day_date = datetime.utcnow() + timedelta(days=i)
        weekly_schedule.append({
            "date": day_date.strftime("%Y-%m-%d"),
            "day": day_date.strftime("%A"),
            "recommended_sessions": 2,
            "estimated_duration": current_user.daily_study_goal_minutes
        })
    
    # Get topics that need review (simplified)
    review_topics = []
    if recent_sessions:
        completed_topics = [s.topic for s in recent_sessions if s.topic and s.is_completed]
        review_topics = list(set(completed_topics))[:5]
    
    return StudyPlanResponse(
        recommended_sessions=recommended_sessions,
        daily_goal_progress=daily_goal_progress,
        weekly_schedule=weekly_schedule,
        next_review_topics=review_topics
    )


@router.get("/dashboard")
async def get_learning_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get learning dashboard data"""
    # Get recent activity
    recent_sessions = db.query(LearningSession).filter(
        and_(
            LearningSession.user_id == current_user.id,
            LearningSession.start_time >= datetime.utcnow() - timedelta(days=7)
        )
    ).order_by(desc(LearningSession.start_time)).limit(10).all()
    
    # Calculate weekly stats
    week_minutes = sum([s.duration_minutes or 0 for s in recent_sessions])
    week_sessions = len(recent_sessions)
    
    # Get subject distribution
    subject_stats = db.query(
        LearningSession.subject,
        func.count(LearningSession.id).label('session_count'),
        func.sum(LearningSession.duration_minutes).label('total_minutes')
    ).filter(
        and_(
            LearningSession.user_id == current_user.id,
            LearningSession.start_time >= datetime.utcnow() - timedelta(days=30)
        )
    ).group_by(LearningSession.subject).all()
    
    return {
        "recent_sessions": [
            {
                "id": s.id,
                "subject": s.subject,
                "topic": s.topic,
                "duration_minutes": s.duration_minutes,
                "completion_percentage": s.completion_percentage,
                "start_time": s.start_time
            } for s in recent_sessions
        ],
        "weekly_stats": {
            "total_minutes": week_minutes,
            "total_sessions": week_sessions,
            "daily_average": week_minutes / 7,
            "goal_progress": min(week_minutes / (current_user.daily_study_goal_minutes * 7) * 100, 100)
        },
        "subject_distribution": [
            {
                "subject": stat.subject,
                "session_count": stat.session_count,
                "total_minutes": stat.total_minutes or 0
            } for stat in subject_stats
        ]
    }