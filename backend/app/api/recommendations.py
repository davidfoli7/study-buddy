from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func, or_
from pydantic import BaseModel

from ..core.database import get_db
from ..models.user import User
from ..models.recommendation import Recommendation
from ..models.content import Content, ContentInteraction
from ..models.learning_session import LearningSession
from ..models.assessment import Assessment
from .auth import get_current_user

router = APIRouter()


class RecommendationResponse(BaseModel):
    id: int
    recommendation_type: str
    title: str
    description: str
    priority: str
    category: str
    estimated_time_minutes: Optional[int]
    difficulty_level: Optional[str]
    optimal_time_of_day: Optional[str]
    reasoning: str
    confidence_score: float
    is_viewed: bool
    is_accepted: Optional[bool]
    is_completed: bool
    created_at: datetime
    expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class RecommendationAcceptance(BaseModel):
    is_accepted: bool
    feedback: Optional[str] = None


@router.get("/", response_model=List[RecommendationResponse])
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=10, le=50),
    skip: int = Query(default=0, ge=0),
    recommendation_type: Optional[str] = Query(default=None),
    priority: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None)
):
    """Get user's personalized recommendations"""
    query = db.query(Recommendation).filter(Recommendation.user_id == current_user.id)
    
    if recommendation_type:
        query = query.filter(Recommendation.recommendation_type == recommendation_type)
    if priority:
        query = query.filter(Recommendation.priority == priority)
    if status:
        query = query.filter(Recommendation.status == status)
    
    # Filter out expired recommendations
    query = query.filter(
        or_(
            Recommendation.expires_at.is_(None),
            Recommendation.expires_at > datetime.utcnow()
        )
    )
    
    recommendations = query.order_by(
        desc(Recommendation.priority),
        desc(Recommendation.confidence_score),
        desc(Recommendation.created_at)
    ).offset(skip).limit(limit).all()
    
    return recommendations


@router.post("/generate")
async def generate_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate new AI-powered recommendations for the user"""
    
    # Get user's recent activity
    recent_sessions = db.query(LearningSession).filter(
        and_(
            LearningSession.user_id == current_user.id,
            LearningSession.start_time >= datetime.utcnow() - timedelta(days=30)
        )
    ).order_by(desc(LearningSession.start_time)).limit(20).all()
    
    recent_assessments = db.query(Assessment).filter(
        and_(
            Assessment.user_id == current_user.id,
            Assessment.created_at >= datetime.utcnow() - timedelta(days=30),
            Assessment.is_completed == True
        )
    ).order_by(desc(Assessment.created_at)).limit(10).all()
    
    recent_content_interactions = db.query(ContentInteraction).filter(
        and_(
            ContentInteraction.user_id == current_user.id,
            ContentInteraction.start_time >= datetime.utcnow() - timedelta(days=30)
        )
    ).order_by(desc(ContentInteraction.start_time)).limit(20).all()
    
    recommendations_created = 0
    
    # 1. Study consistency recommendations
    if len(recent_sessions) < 10:  # Low activity
        study_recommendation = Recommendation(
            user_id=current_user.id,
            recommendation_type="study_plan",
            title="Build a Consistent Study Habit",
            description="Based on your recent activity, establishing a regular study routine could significantly improve your learning outcomes. Start with just 20 minutes per day.",
            priority="high",
            category="habit",
            estimated_time_minutes=20,
            difficulty_level="easy",
            optimal_time_of_day=current_user.preferred_study_time or "morning",
            reasoning="User has low study frequency in the past 30 days. Consistency is key for effective learning.",
            confidence_score=0.85,
            status="active",
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.add(study_recommendation)
        recommendations_created += 1
    
    # 2. Subject-specific recommendations based on poor performance
    struggling_subjects = []
    for assessment in recent_assessments:
        if assessment.score_percentage < 70:  # Below 70% considered struggling
            struggling_subjects.append(assessment.subject)
    
    if struggling_subjects:
        # Get most common struggling subject
        most_struggling = max(set(struggling_subjects), key=struggling_subjects.count)
        
        # Find helpful content for this subject
        helpful_content = db.query(Content).filter(
            and_(
                Content.subject == most_struggling,
                Content.difficulty_level == "easy",
                Content.is_active == True,
                Content.average_rating >= 4.0
            )
        ).order_by(desc(Content.average_rating)).first()
        
        if helpful_content:
            content_recommendation = Recommendation(
                user_id=current_user.id,
                recommendation_type="content",
                title=f"Review Fundamentals in {most_struggling}",
                description=f"Your recent assessments show you might benefit from reviewing basic concepts in {most_struggling}. Try this highly-rated content: '{helpful_content.title}'",
                priority="high",
                category="subject",
                target_content_id=helpful_content.id,
                estimated_time_minutes=helpful_content.estimated_duration_minutes,
                difficulty_level="easy",
                reasoning=f"User scored below 70% in recent {most_struggling} assessments. Recommending foundational content.",
                confidence_score=0.80,
                status="active",
                expires_at=datetime.utcnow() + timedelta(days=14)
            )
            db.add(content_recommendation)
            recommendations_created += 1
    
    # 3. Progress celebration and next steps
    if recent_assessments and max([a.score_percentage for a in recent_assessments]) >= 90:
        best_subject = max(recent_assessments, key=lambda x: x.score_percentage).subject
        
        # Find more challenging content in their best subject
        advanced_content = db.query(Content).filter(
            and_(
                Content.subject == best_subject,
                Content.difficulty_level == "hard",
                Content.is_active == True
            )
        ).order_by(desc(Content.average_rating)).first()
        
        if advanced_content:
            challenge_recommendation = Recommendation(
                user_id=current_user.id,
                recommendation_type="content",
                title=f"Challenge Yourself in {best_subject}",
                description=f"Great job scoring {max([a.score_percentage for a in recent_assessments]):.0f}% in {best_subject}! Ready for a bigger challenge? Try this advanced content.",
                priority="medium",
                category="skill",
                target_content_id=advanced_content.id,
                estimated_time_minutes=advanced_content.estimated_duration_minutes,
                difficulty_level="hard",
                reasoning=f"User performing excellently in {best_subject}. Ready for advanced material.",
                confidence_score=0.75,
                status="active",
                expires_at=datetime.utcnow() + timedelta(days=21)
            )
            db.add(challenge_recommendation)
            recommendations_created += 1
    
    # 4. Break and wellness recommendations
    total_recent_study_time = sum([s.duration_minutes or 0 for s in recent_sessions])
    if total_recent_study_time > 600:  # More than 10 hours in 30 days
        avg_daily_time = total_recent_study_time / 30
        if avg_daily_time > current_user.daily_study_goal_minutes * 1.5:
            wellness_recommendation = Recommendation(
                user_id=current_user.id,
                recommendation_type="break",
                title="Take a Well-Deserved Break",
                description="You've been studying hard lately! Consider taking a short break to avoid burnout. A 15-minute walk or meditation can help consolidate learning.",
                priority="medium",
                category="wellness",
                estimated_time_minutes=15,
                reasoning="User has been studying intensively. Break recommended to prevent burnout.",
                confidence_score=0.70,
                status="active",
                expires_at=datetime.utcnow() + timedelta(days=3)
            )
            db.add(wellness_recommendation)
            recommendations_created += 1
    
    # 5. Content type diversification
    interaction_types = {}
    for interaction in recent_content_interactions:
        if interaction.content:
            content_type = interaction.content.content_type
            interaction_types[content_type] = interaction_types.get(content_type, 0) + 1
    
    if len(interaction_types) == 1 and list(interaction_types.keys())[0] in ["article", "document"]:
        # User only engages with text-based content
        video_content = db.query(Content).filter(
            and_(
                Content.content_type == "video",
                Content.is_active == True,
                Content.average_rating >= 4.0
            )
        ).order_by(desc(Content.average_rating)).first()
        
        if video_content:
            variety_recommendation = Recommendation(
                user_id=current_user.id,
                recommendation_type="content",
                title="Try Video-Based Learning",
                description="You've been engaging mostly with text content. Visual learners often benefit from video content. Try this popular video!",
                priority="low",
                category="learning_style",
                target_content_id=video_content.id,
                estimated_time_minutes=video_content.estimated_duration_minutes,
                reasoning="User shows preference for text content. Recommending content type diversification.",
                confidence_score=0.65,
                status="active",
                expires_at=datetime.utcnow() + timedelta(days=30)
            )
            db.add(variety_recommendation)
            recommendations_created += 1
    
    db.commit()
    
    return {
        "message": f"Generated {recommendations_created} new recommendations",
        "recommendations_created": recommendations_created
    }


@router.get("/{recommendation_id}", response_model=RecommendationResponse)
async def get_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific recommendation"""
    recommendation = db.query(Recommendation).filter(
        and_(
            Recommendation.id == recommendation_id,
            Recommendation.user_id == current_user.id
        )
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    # Mark as viewed
    if not recommendation.is_viewed:
        recommendation.is_viewed = True
        recommendation.viewed_at = datetime.utcnow()
        db.commit()
    
    return recommendation


@router.post("/{recommendation_id}/respond")
async def respond_to_recommendation(
    recommendation_id: int,
    response: RecommendationAcceptance,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Accept or decline a recommendation"""
    recommendation = db.query(Recommendation).filter(
        and_(
            Recommendation.id == recommendation_id,
            Recommendation.user_id == current_user.id
        )
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    recommendation.is_accepted = response.is_accepted
    recommendation.responded_at = datetime.utcnow()
    
    if response.is_accepted:
        recommendation.status = "accepted"
    else:
        recommendation.status = "declined"
    
    db.commit()
    db.refresh(recommendation)
    
    return {
        "message": "Response recorded successfully",
        "recommendation": recommendation
    }


@router.post("/{recommendation_id}/complete")
async def complete_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a recommendation as completed"""
    recommendation = db.query(Recommendation).filter(
        and_(
            Recommendation.id == recommendation_id,
            Recommendation.user_id == current_user.id
        )
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    if not recommendation.is_accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot complete a recommendation that wasn't accepted"
        )
    
    recommendation.is_completed = True
    recommendation.completed_at = datetime.utcnow()
    recommendation.status = "completed"
    
    db.commit()
    db.refresh(recommendation)
    
    return {
        "message": "Recommendation marked as completed",
        "recommendation": recommendation
    }


@router.get("/analytics/effectiveness")
async def get_recommendation_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(default=30, ge=1, le=365)
):
    """Get analytics on recommendation effectiveness"""
    
    # Get recommendations from the specified period
    recommendations = db.query(Recommendation).filter(
        and_(
            Recommendation.user_id == current_user.id,
            Recommendation.created_at >= datetime.utcnow() - timedelta(days=days)
        )
    ).all()
    
    if not recommendations:
        return {
            "total_recommendations": 0,
            "acceptance_rate": 0,
            "completion_rate": 0,
            "type_breakdown": [],
            "priority_breakdown": []
        }
    
    # Calculate metrics
    total_recommendations = len(recommendations)
    viewed_count = sum(1 for r in recommendations if r.is_viewed)
    accepted_count = sum(1 for r in recommendations if r.is_accepted == True)
    completed_count = sum(1 for r in recommendations if r.is_completed)
    
    acceptance_rate = (accepted_count / viewed_count * 100) if viewed_count > 0 else 0
    completion_rate = (completed_count / accepted_count * 100) if accepted_count > 0 else 0
    
    # Type breakdown
    type_stats = {}
    for rec in recommendations:
        rec_type = rec.recommendation_type
        if rec_type not in type_stats:
            type_stats[rec_type] = {"total": 0, "accepted": 0, "completed": 0}
        type_stats[rec_type]["total"] += 1
        if rec.is_accepted:
            type_stats[rec_type]["accepted"] += 1
        if rec.is_completed:
            type_stats[rec_type]["completed"] += 1
    
    type_breakdown = [
        {
            "type": rec_type,
            "total": stats["total"],
            "acceptance_rate": (stats["accepted"] / stats["total"] * 100) if stats["total"] > 0 else 0,
            "completion_rate": (stats["completed"] / stats["accepted"] * 100) if stats["accepted"] > 0 else 0
        }
        for rec_type, stats in type_stats.items()
    ]
    
    # Priority breakdown
    priority_stats = {}
    for rec in recommendations:
        priority = rec.priority
        if priority not in priority_stats:
            priority_stats[priority] = {"total": 0, "accepted": 0}
        priority_stats[priority]["total"] += 1
        if rec.is_accepted:
            priority_stats[priority]["accepted"] += 1
    
    priority_breakdown = [
        {
            "priority": priority,
            "total": stats["total"],
            "acceptance_rate": (stats["accepted"] / stats["total"] * 100) if stats["total"] > 0 else 0
        }
        for priority, stats in priority_stats.items()
    ]
    
    return {
        "total_recommendations": total_recommendations,
        "viewed_count": viewed_count,
        "acceptance_rate": round(acceptance_rate, 2),
        "completion_rate": round(completion_rate, 2),
        "type_breakdown": type_breakdown,
        "priority_breakdown": priority_breakdown
    }


@router.delete("/{recommendation_id}")
async def dismiss_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dismiss a recommendation (soft delete)"""
    recommendation = db.query(Recommendation).filter(
        and_(
            Recommendation.id == recommendation_id,
            Recommendation.user_id == current_user.id
        )
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    recommendation.status = "dismissed"
    db.commit()
    
    return {"message": "Recommendation dismissed successfully"}