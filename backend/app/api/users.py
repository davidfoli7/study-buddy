from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..core.database import get_db
from ..core.security import get_password_hash
from ..models.user import User
from .auth import get_current_user, UserResponse

router = APIRouter()


class UserUpdate(BaseModel):
    full_name: str = None
    bio: str = None
    grade_level: str = None
    subjects_of_interest: List[str] = None
    preferred_difficulty: str = None
    daily_study_goal_minutes: int = None
    preferred_study_time: str = None


class UserStats(BaseModel):
    total_study_time_minutes: int
    total_assessments_completed: int
    average_score: float
    streak_days: int
    achievements_count: int
    learning_sessions_count: int


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile"""
    # Convert subjects to list for response
    if current_user.subjects_of_interest:
        current_user.subjects_of_interest = current_user.subjects_of_interest.split(",")
    else:
        current_user.subjects_of_interest = []
    
    return current_user


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    # Update fields if provided
    if user_data.full_name is not None:
        current_user.full_name = user_data.full_name
    if user_data.bio is not None:
        current_user.bio = user_data.bio
    if user_data.grade_level is not None:
        current_user.grade_level = user_data.grade_level
    if user_data.subjects_of_interest is not None:
        current_user.subjects_of_interest = ",".join(user_data.subjects_of_interest)
    if user_data.preferred_difficulty is not None:
        current_user.preferred_difficulty = user_data.preferred_difficulty
    if user_data.daily_study_goal_minutes is not None:
        current_user.daily_study_goal_minutes = user_data.daily_study_goal_minutes
    if user_data.preferred_study_time is not None:
        current_user.preferred_study_time = user_data.preferred_study_time

    db.commit()
    db.refresh(current_user)
    
    # Convert subjects to list for response
    if current_user.subjects_of_interest:
        current_user.subjects_of_interest = current_user.subjects_of_interest.split(",")
    else:
        current_user.subjects_of_interest = []
    
    return current_user


@router.get("/stats", response_model=UserStats)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's learning statistics"""
    from ..models.achievement import Achievement
    from ..models.learning_session import LearningSession
    
    achievements_count = db.query(Achievement).filter(
        Achievement.user_id == current_user.id,
        Achievement.is_unlocked == True
    ).count()
    
    learning_sessions_count = db.query(LearningSession).filter(
        LearningSession.user_id == current_user.id
    ).count()
    
    return UserStats(
        total_study_time_minutes=current_user.total_study_time_minutes,
        total_assessments_completed=current_user.total_assessments_completed,
        average_score=current_user.average_score,
        streak_days=current_user.streak_days,
        achievements_count=achievements_count,
        learning_sessions_count=learning_sessions_count
    )


@router.delete("/account")
async def delete_user_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete current user's account (soft delete)"""
    current_user.is_active = False
    db.commit()
    
    return {"message": "Account successfully deactivated"}


@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user's password"""
    from ..core.security import verify_password
    
    # Verify current password
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    return {"message": "Password successfully changed"}