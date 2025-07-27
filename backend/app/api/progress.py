from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
from pydantic import BaseModel

from ..core.database import get_db
from ..models.user import User
from ..models.progress import Progress, Achievement
from .auth import get_current_user

router = APIRouter()


class ProgressResponse(BaseModel):
    id: int
    subject: str
    topic: Optional[str]
    subtopic: Optional[str]
    skill_level: float
    mastery_score: float
    confidence_level: float
    time_spent_minutes: int
    effective_study_time: int
    last_studied_at: Optional[datetime]
    streak_days: int
    longest_streak: int
    study_frequency_score: float
    total_sessions: int
    completed_sessions: int
    average_session_score: float
    improvement_rate: float
    learning_velocity: float
    retention_score: float
    current_difficulty: str
    is_completed: bool
    is_mastered: bool
    needs_review: bool
    is_struggling: bool
    
    class Config:
        from_attributes = True


class AchievementResponse(BaseModel):
    id: int
    achievement_type: str
    title: str
    description: str
    badge_icon: Optional[str]
    category: str
    difficulty_level: str
    rarity: str
    points_awarded: int
    current_progress: float
    required_progress: float
    progress_percentage: float
    is_unlocked: bool
    unlocked_at: Optional[datetime]
    subject: Optional[str]
    topic: Optional[str]
    
    class Config:
        from_attributes = True


@router.get("/subjects", response_model=List[ProgressResponse])
async def get_progress_by_subjects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get learning progress for all subjects"""
    progress_records = db.query(Progress).filter(
        Progress.user_id == current_user.id
    ).order_by(desc(Progress.mastery_score)).all()
    
    return progress_records


@router.get("/subject/{subject}", response_model=List[ProgressResponse])
async def get_progress_by_subject(
    subject: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed progress for a specific subject"""
    progress_records = db.query(Progress).filter(
        and_(
            Progress.user_id == current_user.id,
            Progress.subject == subject
        )
    ).order_by(desc(Progress.mastery_score)).all()
    
    return progress_records


@router.get("/dashboard")
async def get_progress_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive progress dashboard data"""
    
    # Get overall progress stats
    all_progress = db.query(Progress).filter(Progress.user_id == current_user.id).all()
    
    if not all_progress:
        return {
            "overall_stats": {
                "total_subjects": 0,
                "mastered_subjects": 0,
                "average_mastery": 0,
                "total_study_time": 0,
                "current_streak": 0
            },
            "subject_progress": [],
            "recent_achievements": [],
            "struggling_areas": [],
            "mastery_timeline": []
        }
    
    # Calculate overall stats
    total_subjects = len(set([p.subject for p in all_progress]))
    mastered_subjects = len([p for p in all_progress if p.is_mastered])
    average_mastery = sum([p.mastery_score for p in all_progress]) / len(all_progress)
    total_study_time = sum([p.time_spent_minutes for p in all_progress])
    current_streak = max([p.streak_days for p in all_progress]) if all_progress else 0
    
    # Subject-level progress
    subject_stats = {}
    for progress in all_progress:
        subject = progress.subject
        if subject not in subject_stats:
            subject_stats[subject] = {
                "subject": subject,
                "topics": [],
                "overall_mastery": 0,
                "time_spent": 0,
                "is_struggling": False
            }
        
        subject_stats[subject]["topics"].append({
            "topic": progress.topic or "General",
            "mastery_score": progress.mastery_score,
            "confidence_level": progress.confidence_level,
            "needs_review": progress.needs_review
        })
        subject_stats[subject]["time_spent"] += progress.time_spent_minutes
        if progress.is_struggling:
            subject_stats[subject]["is_struggling"] = True
    
    # Calculate average mastery per subject
    for subject_data in subject_stats.values():
        if subject_data["topics"]:
            subject_data["overall_mastery"] = sum([t["mastery_score"] for t in subject_data["topics"]]) / len(subject_data["topics"])
    
    subject_progress = list(subject_stats.values())
    
    # Recent achievements
    recent_achievements = db.query(Achievement).filter(
        and_(
            Achievement.user_id == current_user.id,
            Achievement.is_unlocked == True,
            Achievement.unlocked_at >= datetime.utcnow() - timedelta(days=30)
        )
    ).order_by(desc(Achievement.unlocked_at)).limit(5).all()
    
    # Struggling areas
    struggling_areas = [
        {
            "subject": p.subject,
            "topic": p.topic,
            "mastery_score": p.mastery_score,
            "confidence_level": p.confidence_level,
            "recommended_action": "Review fundamentals" if p.mastery_score < 50 else "Additional practice needed"
        }
        for p in all_progress if p.is_struggling or p.mastery_score < 60
    ]
    
    return {
        "overall_stats": {
            "total_subjects": total_subjects,
            "mastered_subjects": mastered_subjects,
            "average_mastery": round(average_mastery, 2),
            "total_study_time": total_study_time,
            "current_streak": current_streak
        },
        "subject_progress": subject_progress,
        "recent_achievements": [
            {
                "title": a.title,
                "description": a.description,
                "badge_icon": a.badge_icon,
                "points_awarded": a.points_awarded,
                "unlocked_at": a.unlocked_at
            } for a in recent_achievements
        ],
        "struggling_areas": struggling_areas[:5],  # Limit to top 5
        "improvement_recommendations": [
            "Focus on struggling areas in " + area["subject"] for area in struggling_areas[:3]
        ]
    }


@router.get("/achievements", response_model=List[AchievementResponse])
async def get_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    unlocked_only: bool = Query(default=False)
):
    """Get user's achievements"""
    query = db.query(Achievement).filter(Achievement.user_id == current_user.id)
    
    if unlocked_only:
        query = query.filter(Achievement.is_unlocked == True)
    
    achievements = query.order_by(
        desc(Achievement.is_unlocked),
        desc(Achievement.unlocked_at),
        desc(Achievement.points_awarded)
    ).all()
    
    return achievements


@router.post("/achievements/check")
async def check_for_new_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check and unlock new achievements based on current progress"""
    
    achievements_unlocked = 0
    
    # Study streak achievements
    max_streak = db.query(func.max(Progress.streak_days)).filter(Progress.user_id == current_user.id).scalar() or 0
    
    streak_milestones = [7, 14, 30, 60, 100]
    for milestone in streak_milestones:
        if max_streak >= milestone:
            existing = db.query(Achievement).filter(
                and_(
                    Achievement.user_id == current_user.id,
                    Achievement.achievement_type == "streak",
                    Achievement.threshold_value == milestone
                )
            ).first()
            
            if not existing:
                streak_achievement = Achievement(
                    user_id=current_user.id,
                    achievement_type="streak",
                    title=f"{milestone}-Day Study Streak",
                    description=f"Studied consistently for {milestone} days in a row!",
                    badge_icon="streak_badge",
                    category="consistency",
                    difficulty_level="medium" if milestone <= 30 else "hard",
                    rarity="uncommon" if milestone <= 30 else "rare",
                    points_awarded=milestone * 2,
                    threshold_value=milestone,
                    required_progress=milestone,
                    current_progress=max_streak,
                    progress_percentage=100.0,
                    is_unlocked=True,
                    unlocked_at=datetime.utcnow()
                )
                db.add(streak_achievement)
                achievements_unlocked += 1
    
    # Study time achievements
    total_study_time = current_user.total_study_time_minutes
    time_milestones = [600, 1200, 3000, 6000, 12000]  # 10h, 20h, 50h, 100h, 200h
    
    for milestone in time_milestones:
        if total_study_time >= milestone:
            existing = db.query(Achievement).filter(
                and_(
                    Achievement.user_id == current_user.id,
                    Achievement.achievement_type == "time",
                    Achievement.threshold_value == milestone
                )
            ).first()
            
            if not existing:
                hours = milestone // 60
                time_achievement = Achievement(
                    user_id=current_user.id,
                    achievement_type="time",
                    title=f"{hours}-Hour Scholar",
                    description=f"Dedicated {hours} hours to learning!",
                    badge_icon="time_badge",
                    category="dedication",
                    difficulty_level="easy" if hours <= 20 else "medium" if hours <= 100 else "hard",
                    rarity="common" if hours <= 20 else "uncommon" if hours <= 100 else "rare",
                    points_awarded=hours * 5,
                    threshold_value=milestone,
                    required_progress=milestone,
                    current_progress=total_study_time,
                    progress_percentage=100.0,
                    is_unlocked=True,
                    unlocked_at=datetime.utcnow()
                )
                db.add(time_achievement)
                achievements_unlocked += 1
    
    # Assessment performance achievements
    if current_user.average_score >= 95:
        existing = db.query(Achievement).filter(
            and_(
                Achievement.user_id == current_user.id,
                Achievement.achievement_type == "assessment",
                Achievement.title == "Perfectionist"
            )
        ).first()
        
        if not existing:
            perfect_achievement = Achievement(
                user_id=current_user.id,
                achievement_type="assessment",
                title="Perfectionist",
                description="Maintained an average score of 95% or higher!",
                badge_icon="perfect_badge",
                category="excellence",
                difficulty_level="hard",
                rarity="epic",
                points_awarded=100,
                threshold_value=95,
                required_progress=95,
                current_progress=current_user.average_score,
                progress_percentage=100.0,
                is_unlocked=True,
                unlocked_at=datetime.utcnow()
            )
            db.add(perfect_achievement)
            achievements_unlocked += 1
    
    # Mastery achievements
    mastered_subjects = db.query(Progress).filter(
        and_(
            Progress.user_id == current_user.id,
            Progress.is_mastered == True
        )
    ).count()
    
    mastery_milestones = [1, 3, 5, 10]
    for milestone in mastery_milestones:
        if mastered_subjects >= milestone:
            existing = db.query(Achievement).filter(
                and_(
                    Achievement.user_id == current_user.id,
                    Achievement.achievement_type == "mastery",
                    Achievement.threshold_value == milestone
                )
            ).first()
            
            if not existing:
                mastery_achievement = Achievement(
                    user_id=current_user.id,
                    achievement_type="mastery",
                    title=f"Master of {milestone} Subject{'s' if milestone > 1 else ''}",
                    description=f"Achieved mastery in {milestone} subject{'s' if milestone > 1 else ''}!",
                    badge_icon="mastery_badge",
                    category="expertise",
                    difficulty_level="medium" if milestone <= 3 else "hard",
                    rarity="rare" if milestone <= 3 else "epic",
                    points_awarded=milestone * 50,
                    threshold_value=milestone,
                    required_progress=milestone,
                    current_progress=mastered_subjects,
                    progress_percentage=100.0,
                    is_unlocked=True,
                    unlocked_at=datetime.utcnow()
                )
                db.add(mastery_achievement)
                achievements_unlocked += 1
    
    db.commit()
    
    return {
        "message": f"Checked achievements. {achievements_unlocked} new achievements unlocked!",
        "achievements_unlocked": achievements_unlocked
    }


@router.get("/analytics/trends")
async def get_progress_trends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(default=30, ge=7, le=365),
    subject: Optional[str] = Query(default=None)
):
    """Get progress trends and analytics"""
    
    # Get learning sessions for trend analysis
    from ..models.learning_session import LearningSession
    
    sessions_query = db.query(LearningSession).filter(
        and_(
            LearningSession.user_id == current_user.id,
            LearningSession.start_time >= datetime.utcnow() - timedelta(days=days)
        )
    )
    
    if subject:
        sessions_query = sessions_query.filter(LearningSession.subject == subject)
    
    sessions = sessions_query.order_by(LearningSession.start_time).all()
    
    # Group sessions by date
    daily_stats = {}
    for session in sessions:
        date_key = session.start_time.date().strftime("%Y-%m-%d")
        if date_key not in daily_stats:
            daily_stats[date_key] = {
                "date": date_key,
                "study_time_minutes": 0,
                "sessions_count": 0,
                "average_completion": 0,
                "subjects_studied": set()
            }
        
        daily_stats[date_key]["study_time_minutes"] += session.duration_minutes or 0
        daily_stats[date_key]["sessions_count"] += 1
        daily_stats[date_key]["subjects_studied"].add(session.subject)
        
        if session.completion_percentage:
            daily_stats[date_key]["average_completion"] += session.completion_percentage
    
    # Calculate averages and convert sets to counts
    for stats in daily_stats.values():
        if stats["sessions_count"] > 0:
            stats["average_completion"] = stats["average_completion"] / stats["sessions_count"]
        stats["subjects_studied"] = len(stats["subjects_studied"])
    
    trend_data = list(daily_stats.values())
    trend_data.sort(key=lambda x: x["date"])
    
    # Calculate overall trends
    if len(trend_data) >= 7:
        recent_week = trend_data[-7:]
        previous_week = trend_data[-14:-7] if len(trend_data) >= 14 else []
        
        recent_avg_time = sum([d["study_time_minutes"] for d in recent_week]) / 7
        previous_avg_time = sum([d["study_time_minutes"] for d in previous_week]) / len(previous_week) if previous_week else recent_avg_time
        
        time_trend = ((recent_avg_time - previous_avg_time) / previous_avg_time * 100) if previous_avg_time > 0 else 0
    else:
        time_trend = 0
    
    return {
        "period_days": days,
        "subject_filter": subject,
        "daily_trends": trend_data,
        "summary": {
            "total_study_time": sum([d["study_time_minutes"] for d in trend_data]),
            "total_sessions": sum([d["sessions_count"] for d in trend_data]),
            "average_daily_time": sum([d["study_time_minutes"] for d in trend_data]) / len(trend_data) if trend_data else 0,
            "time_trend_percentage": round(time_trend, 2),
            "most_active_day": max(trend_data, key=lambda x: x["study_time_minutes"])["date"] if trend_data else None
        }
    }