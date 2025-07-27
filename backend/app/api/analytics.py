from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func, text
from pydantic import BaseModel

from ..core.database import get_db
from ..models.user import User
from ..models.learning_session import LearningSession
from ..models.assessment import Assessment
from ..models.content import ContentInteraction
from ..models.progress import Progress
from .auth import get_current_user

router = APIRouter()


class LearningAnalytics(BaseModel):
    total_study_time_minutes: int
    total_sessions: int
    total_assessments: int
    average_score: float
    subjects_studied: int
    content_consumed: int
    streak_days: int
    improvement_rate: float


class SubjectAnalytics(BaseModel):
    subject: str
    study_time_minutes: int
    sessions_count: int
    assessments_count: int
    average_score: float
    mastery_level: float
    improvement_trend: float


@router.get("/overview")
async def get_analytics_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(default=30, ge=1, le=365)
):
    """Get comprehensive analytics overview"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Learning sessions analytics
    sessions = db.query(LearningSession).filter(
        and_(
            LearningSession.user_id == current_user.id,
            LearningSession.start_time >= start_date
        )
    ).all()
    
    total_study_time = sum([s.duration_minutes or 0 for s in sessions])
    total_sessions = len(sessions)
    subjects_studied = len(set([s.subject for s in sessions]))
    
    # Assessment analytics
    assessments = db.query(Assessment).filter(
        and_(
            Assessment.user_id == current_user.id,
            Assessment.created_at >= start_date,
            Assessment.is_completed == True
        )
    ).all()
    
    total_assessments = len(assessments)
    average_score = sum([a.score_percentage for a in assessments]) / len(assessments) if assessments else 0
    
    # Content interaction analytics
    content_interactions = db.query(ContentInteraction).filter(
        and_(
            ContentInteraction.user_id == current_user.id,
            ContentInteraction.start_time >= start_date
        )
    ).count()
    
    # Calculate improvement rate (simplified)
    if len(assessments) >= 2:
        first_half = assessments[:len(assessments)//2]
        second_half = assessments[len(assessments)//2:]
        
        first_avg = sum([a.score_percentage for a in first_half]) / len(first_half)
        second_avg = sum([a.score_percentage for a in second_half]) / len(second_half)
        
        improvement_rate = ((second_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0
    else:
        improvement_rate = 0
    
    return {
        "period_days": days,
        "overview": {
            "total_study_time_minutes": total_study_time,
            "total_sessions": total_sessions,
            "total_assessments": total_assessments,
            "average_score": round(average_score, 2),
            "subjects_studied": subjects_studied,
            "content_interactions": content_interactions,
            "streak_days": current_user.streak_days,
            "improvement_rate": round(improvement_rate, 2)
        },
        "daily_average": {
            "study_time_minutes": round(total_study_time / days, 2),
            "sessions": round(total_sessions / days, 2),
            "assessments": round(total_assessments / days, 2)
        }
    }


@router.get("/subjects")
async def get_subject_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(default=30, ge=1, le=365)
):
    """Get analytics breakdown by subject"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get sessions grouped by subject
    session_stats = db.query(
        LearningSession.subject,
        func.count(LearningSession.id).label('session_count'),
        func.sum(LearningSession.duration_minutes).label('total_minutes'),
        func.avg(LearningSession.completion_percentage).label('avg_completion')
    ).filter(
        and_(
            LearningSession.user_id == current_user.id,
            LearningSession.start_time >= start_date
        )
    ).group_by(LearningSession.subject).all()
    
    # Get assessment stats by subject
    assessment_stats = db.query(
        Assessment.subject,
        func.count(Assessment.id).label('assessment_count'),
        func.avg(Assessment.score_percentage).label('avg_score')
    ).filter(
        and_(
            Assessment.user_id == current_user.id,
            Assessment.created_at >= start_date,
            Assessment.is_completed == True
        )
    ).group_by(Assessment.subject).all()
    
    # Get progress data
    progress_stats = db.query(Progress).filter(
        Progress.user_id == current_user.id
    ).all()
    
    # Combine data
    subject_data = {}
    
    # Add session data
    for stat in session_stats:
        subject_data[stat.subject] = {
            "subject": stat.subject,
            "study_time_minutes": int(stat.total_minutes or 0),
            "sessions_count": stat.session_count,
            "average_completion": round(stat.avg_completion or 0, 2),
            "assessments_count": 0,
            "average_score": 0,
            "mastery_level": 0,
            "improvement_trend": 0
        }
    
    # Add assessment data
    for stat in assessment_stats:
        if stat.subject in subject_data:
            subject_data[stat.subject]["assessments_count"] = stat.assessment_count
            subject_data[stat.subject]["average_score"] = round(stat.avg_score or 0, 2)
        else:
            subject_data[stat.subject] = {
                "subject": stat.subject,
                "study_time_minutes": 0,
                "sessions_count": 0,
                "average_completion": 0,
                "assessments_count": stat.assessment_count,
                "average_score": round(stat.avg_score or 0, 2),
                "mastery_level": 0,
                "improvement_trend": 0
            }
    
    # Add progress data
    for progress in progress_stats:
        if progress.subject in subject_data:
            subject_data[progress.subject]["mastery_level"] = round(progress.mastery_score, 2)
            subject_data[progress.subject]["improvement_trend"] = round(progress.improvement_rate, 2)
    
    return {
        "period_days": days,
        "subjects": list(subject_data.values())
    }


@router.get("/performance-trends")
async def get_performance_trends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(default=30, ge=7, le=365),
    metric: str = Query(default="score", regex="^(score|study_time|completion)$")
):
    """Get performance trends over time"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    if metric == "score":
        # Assessment score trends
        assessments = db.query(Assessment).filter(
            and_(
                Assessment.user_id == current_user.id,
                Assessment.created_at >= start_date,
                Assessment.is_completed == True
            )
        ).order_by(Assessment.created_at).all()
        
        trend_data = []
        for assessment in assessments:
            trend_data.append({
                "date": assessment.created_at.strftime("%Y-%m-%d"),
                "value": assessment.score_percentage,
                "subject": assessment.subject,
                "type": "assessment"
            })
    
    elif metric == "study_time":
        # Daily study time trends
        sessions = db.query(LearningSession).filter(
            and_(
                LearningSession.user_id == current_user.id,
                LearningSession.start_time >= start_date
            )
        ).order_by(LearningSession.start_time).all()
        
        daily_time = {}
        for session in sessions:
            date_key = session.start_time.strftime("%Y-%m-%d")
            if date_key not in daily_time:
                daily_time[date_key] = 0
            daily_time[date_key] += session.duration_minutes or 0
        
        trend_data = [
            {
                "date": date,
                "value": minutes,
                "subject": "All",
                "type": "study_time"
            }
            for date, minutes in sorted(daily_time.items())
        ]
    
    else:  # completion
        # Session completion trends
        sessions = db.query(LearningSession).filter(
            and_(
                LearningSession.user_id == current_user.id,
                LearningSession.start_time >= start_date,
                LearningSession.completion_percentage.isnot(None)
            )
        ).order_by(LearningSession.start_time).all()
        
        trend_data = []
        for session in sessions:
            trend_data.append({
                "date": session.start_time.strftime("%Y-%m-%d"),
                "value": session.completion_percentage,
                "subject": session.subject,
                "type": "completion"
            })
    
    # Calculate trend statistics
    if len(trend_data) >= 2:
        values = [d["value"] for d in trend_data]
        first_half_avg = sum(values[:len(values)//2]) / (len(values)//2)
        second_half_avg = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        trend_direction = "improving" if second_half_avg > first_half_avg else "declining"
        trend_percentage = ((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg > 0 else 0
    else:
        trend_direction = "stable"
        trend_percentage = 0
    
    return {
        "period_days": days,
        "metric": metric,
        "trend_data": trend_data,
        "trend_summary": {
            "direction": trend_direction,
            "percentage_change": round(trend_percentage, 2),
            "total_data_points": len(trend_data)
        }
    }


@router.get("/learning-patterns")
async def get_learning_patterns(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(default=30, ge=7, le=90)
):
    """Analyze learning patterns and habits"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    sessions = db.query(LearningSession).filter(
        and_(
            LearningSession.user_id == current_user.id,
            LearningSession.start_time >= start_date
        )
    ).all()
    
    if not sessions:
        return {
            "period_days": days,
            "patterns": {
                "most_productive_time": "No data",
                "average_session_length": 0,
                "preferred_subjects": [],
                "study_consistency": 0,
                "weekly_pattern": []
            }
        }
    
    # Time of day analysis
    hour_stats = {}
    for session in sessions:
        hour = session.start_time.hour
        if hour not in hour_stats:
            hour_stats[hour] = {"count": 0, "total_minutes": 0}
        hour_stats[hour]["count"] += 1
        hour_stats[hour]["total_minutes"] += session.duration_minutes or 0
    
    # Find most productive time
    most_productive_hour = max(hour_stats.items(), key=lambda x: x[1]["total_minutes"])[0] if hour_stats else 12
    time_periods = {
        range(6, 12): "Morning",
        range(12, 17): "Afternoon", 
        range(17, 22): "Evening",
        range(22, 24): "Night",
        range(0, 6): "Night"
    }
    
    most_productive_time = "Morning"
    for time_range, period in time_periods.items():
        if most_productive_hour in time_range:
            most_productive_time = period
            break
    
    # Average session length
    session_lengths = [s.duration_minutes for s in sessions if s.duration_minutes]
    average_session_length = sum(session_lengths) / len(session_lengths) if session_lengths else 0
    
    # Subject preferences
    subject_stats = {}
    for session in sessions:
        subject = session.subject
        if subject not in subject_stats:
            subject_stats[subject] = {"count": 0, "total_minutes": 0}
        subject_stats[subject]["count"] += 1
        subject_stats[subject]["total_minutes"] += session.duration_minutes or 0
    
    preferred_subjects = sorted(
        subject_stats.items(), 
        key=lambda x: x[1]["total_minutes"], 
        reverse=True
    )[:3]
    
    # Study consistency (days with sessions / total days)
    session_dates = set([s.start_time.date() for s in sessions])
    study_consistency = len(session_dates) / days * 100
    
    # Weekly pattern
    day_stats = {}
    for session in sessions:
        day_name = session.start_time.strftime("%A")
        if day_name not in day_stats:
            day_stats[day_name] = {"count": 0, "total_minutes": 0}
        day_stats[day_name]["count"] += 1
        day_stats[day_name]["total_minutes"] += session.duration_minutes or 0
    
    weekly_pattern = [
        {
            "day": day,
            "sessions": stats["count"],
            "minutes": stats["total_minutes"]
        }
        for day, stats in day_stats.items()
    ]
    
    return {
        "period_days": days,
        "patterns": {
            "most_productive_time": most_productive_time,
            "average_session_length": round(average_session_length, 2),
            "preferred_subjects": [
                {
                    "subject": subject,
                    "sessions": stats["count"],
                    "total_minutes": stats["total_minutes"]
                }
                for subject, stats in preferred_subjects
            ],
            "study_consistency": round(study_consistency, 2),
            "weekly_pattern": weekly_pattern,
            "total_sessions": len(sessions),
            "total_study_days": len(session_dates)
        }
    }


@router.get("/content-engagement")
async def get_content_engagement_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(default=30, ge=1, le=365)
):
    """Analyze content engagement patterns"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    interactions = db.query(ContentInteraction).filter(
        and_(
            ContentInteraction.user_id == current_user.id,
            ContentInteraction.start_time >= start_date
        )
    ).all()
    
    if not interactions:
        return {
            "period_days": days,
            "engagement": {
                "total_interactions": 0,
                "content_types": [],
                "completion_rates": [],
                "engagement_time": 0,
                "favorite_content_types": []
            }
        }
    
    # Content type analysis
    content_type_stats = {}
    total_engagement_time = 0
    completed_content = 0
    
    for interaction in interactions:
        if interaction.content:
            content_type = interaction.content.content_type
            if content_type not in content_type_stats:
                content_type_stats[content_type] = {
                    "count": 0,
                    "completed": 0,
                    "total_time": 0,
                    "average_rating": 0,
                    "rating_count": 0
                }
            
            content_type_stats[content_type]["count"] += 1
            
            if interaction.is_completed:
                content_type_stats[content_type]["completed"] += 1
                completed_content += 1
            
            if interaction.duration_seconds:
                content_type_stats[content_type]["total_time"] += interaction.duration_seconds
                total_engagement_time += interaction.duration_seconds
            
            if interaction.rating:
                content_type_stats[content_type]["average_rating"] += interaction.rating
                content_type_stats[content_type]["rating_count"] += 1
    
    # Calculate averages and completion rates
    content_types = []
    for content_type, stats in content_type_stats.items():
        completion_rate = (stats["completed"] / stats["count"] * 100) if stats["count"] > 0 else 0
        average_rating = (stats["average_rating"] / stats["rating_count"]) if stats["rating_count"] > 0 else 0
        
        content_types.append({
            "type": content_type,
            "interactions": stats["count"],
            "completion_rate": round(completion_rate, 2),
            "total_time_minutes": round(stats["total_time"] / 60, 2),
            "average_rating": round(average_rating, 2)
        })
    
    # Sort by engagement time to find favorites
    content_types.sort(key=lambda x: x["total_time_minutes"], reverse=True)
    
    return {
        "period_days": days,
        "engagement": {
            "total_interactions": len(interactions),
            "completed_content": completed_content,
            "overall_completion_rate": round(completed_content / len(interactions) * 100, 2),
            "total_engagement_time_hours": round(total_engagement_time / 3600, 2),
            "content_types": content_types,
            "favorite_content_types": content_types[:3]
        }
    }


@router.get("/recommendations-effectiveness")
async def get_recommendations_effectiveness(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(default=30, ge=1, le=365)
):
    """Analyze the effectiveness of AI recommendations"""
    
    from ..models.recommendation import Recommendation
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    recommendations = db.query(Recommendation).filter(
        and_(
            Recommendation.user_id == current_user.id,
            Recommendation.created_at >= start_date
        )
    ).all()
    
    if not recommendations:
        return {
            "period_days": days,
            "effectiveness": {
                "total_recommendations": 0,
                "acceptance_rate": 0,
                "completion_rate": 0,
                "type_performance": [],
                "impact_score": 0
            }
        }
    
    total_recommendations = len(recommendations)
    viewed_count = sum(1 for r in recommendations if r.is_viewed)
    accepted_count = sum(1 for r in recommendations if r.is_accepted == True)
    completed_count = sum(1 for r in recommendations if r.is_completed)
    
    acceptance_rate = (accepted_count / viewed_count * 100) if viewed_count > 0 else 0
    completion_rate = (completed_count / accepted_count * 100) if accepted_count > 0 else 0
    
    # Type performance analysis
    type_stats = {}
    for rec in recommendations:
        rec_type = rec.recommendation_type
        if rec_type not in type_stats:
            type_stats[rec_type] = {
                "total": 0,
                "viewed": 0,
                "accepted": 0,
                "completed": 0,
                "avg_confidence": 0
            }
        
        type_stats[rec_type]["total"] += 1
        type_stats[rec_type]["avg_confidence"] += rec.confidence_score
        
        if rec.is_viewed:
            type_stats[rec_type]["viewed"] += 1
        if rec.is_accepted:
            type_stats[rec_type]["accepted"] += 1
        if rec.is_completed:
            type_stats[rec_type]["completed"] += 1
    
    type_performance = []
    for rec_type, stats in type_stats.items():
        stats["avg_confidence"] = stats["avg_confidence"] / stats["total"]
        acceptance_rate_type = (stats["accepted"] / stats["viewed"] * 100) if stats["viewed"] > 0 else 0
        completion_rate_type = (stats["completed"] / stats["accepted"] * 100) if stats["accepted"] > 0 else 0
        
        type_performance.append({
            "type": rec_type,
            "total": stats["total"],
            "acceptance_rate": round(acceptance_rate_type, 2),
            "completion_rate": round(completion_rate_type, 2),
            "average_confidence": round(stats["avg_confidence"], 2)
        })
    
    # Calculate impact score (simplified)
    impact_score = (acceptance_rate * 0.4 + completion_rate * 0.6) if accepted_count > 0 else 0
    
    return {
        "period_days": days,
        "effectiveness": {
            "total_recommendations": total_recommendations,
            "viewed_count": viewed_count,
            "acceptance_rate": round(acceptance_rate, 2),
            "completion_rate": round(completion_rate, 2),
            "type_performance": type_performance,
            "impact_score": round(impact_score, 2)
        }
    }