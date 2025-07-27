from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func, or_
from pydantic import BaseModel

from ..core.database import get_db
from ..models.user import User
from ..models.content import Content, ContentInteraction
from .auth import get_current_user

router = APIRouter()


class ContentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    content_type: str  # video, article, interactive, quiz, document, audio
    format: Optional[str] = None
    subject: str
    topic: Optional[str] = None
    subtopic: Optional[str] = None
    difficulty_level: str = "medium"
    grade_level: Optional[str] = None
    learning_objectives: Optional[List[str]] = None
    url: Optional[str] = None
    estimated_duration_minutes: Optional[int] = None
    author: Optional[str] = None


class ContentResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    content_type: str
    format: Optional[str]
    subject: str
    topic: Optional[str]
    subtopic: Optional[str]
    difficulty_level: str
    grade_level: Optional[str]
    learning_objectives: Optional[str]
    url: Optional[str]
    file_path: Optional[str]
    estimated_duration_minutes: Optional[int]
    complexity_score: Optional[float]
    readability_score: Optional[float]
    visual_score: float
    auditory_score: float
    kinesthetic_score: float
    reading_score: float
    average_rating: Optional[float]
    total_ratings: int
    view_count: int
    completion_count: int
    is_active: bool
    author: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ContentInteractionCreate(BaseModel):
    content_id: int
    interaction_type: str  # view, complete, bookmark, rate, comment, share
    progress_percentage: float = 0.0
    last_position: Optional[str] = None
    rating: Optional[int] = None
    difficulty_rating: Optional[str] = None
    usefulness_rating: Optional[int] = None
    notes: Optional[str] = None


class ContentInteractionResponse(BaseModel):
    id: int
    content_id: int
    interaction_type: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: Optional[float]
    progress_percentage: float
    last_position: Optional[str]
    is_completed: bool
    rating: Optional[int]
    difficulty_rating: Optional[str]
    usefulness_rating: Optional[int]
    notes: Optional[str]
    
    class Config:
        from_attributes = True


@router.post("/", response_model=ContentResponse)
async def create_content(
    content_data: ContentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new learning content"""
    content = Content(
        title=content_data.title,
        description=content_data.description,
        content_type=content_data.content_type,
        format=content_data.format,
        subject=content_data.subject,
        topic=content_data.topic,
        subtopic=content_data.subtopic,
        difficulty_level=content_data.difficulty_level,
        grade_level=content_data.grade_level,
        learning_objectives=",".join(content_data.learning_objectives) if content_data.learning_objectives else None,
        url=content_data.url,
        estimated_duration_minutes=content_data.estimated_duration_minutes,
        author=content_data.author or current_user.full_name
    )
    
    db.add(content)
    db.commit()
    db.refresh(content)
    
    return content


@router.get("/", response_model=List[ContentResponse])
async def get_content(
    db: Session = Depends(get_db),
    limit: int = Query(default=20, le=100),
    skip: int = Query(default=0, ge=0),
    subject: Optional[str] = Query(default=None),
    content_type: Optional[str] = Query(default=None),
    difficulty_level: Optional[str] = Query(default=None),
    grade_level: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None)
):
    """Get learning content with filtering and search"""
    query = db.query(Content).filter(Content.is_active == True)
    
    if subject:
        query = query.filter(Content.subject == subject)
    if content_type:
        query = query.filter(Content.content_type == content_type)
    if difficulty_level:
        query = query.filter(Content.difficulty_level == difficulty_level)
    if grade_level:
        query = query.filter(Content.grade_level == grade_level)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Content.title.ilike(search_term),
                Content.description.ilike(search_term),
                Content.topic.ilike(search_term)
            )
        )
    
    content = query.order_by(desc(Content.average_rating), desc(Content.view_count)).offset(skip).limit(limit).all()
    return content


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content_by_id(
    content_id: int,
    db: Session = Depends(get_db)
):
    """Get specific content by ID"""
    content = db.query(Content).filter(
        and_(Content.id == content_id, Content.is_active == True)
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Increment view count
    content.view_count += 1
    db.commit()
    
    return content


@router.get("/recommendations/{subject}")
async def get_content_recommendations(
    subject: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=10, le=20)
):
    """Get personalized content recommendations for a subject"""
    # Get user's learning style preferences (simplified)
    user_difficulty = current_user.preferred_difficulty
    
    # Get content user hasn't interacted with much
    interacted_content_ids = db.query(ContentInteraction.content_id).filter(
        and_(
            ContentInteraction.user_id == current_user.id,
            ContentInteraction.progress_percentage > 50
        )
    ).subquery()
    
    # Base recommendation query
    query = db.query(Content).filter(
        and_(
            Content.is_active == True,
            Content.subject == subject,
            Content.difficulty_level == user_difficulty,
            ~Content.id.in_(interacted_content_ids)
        )
    )
    
    # Order by quality metrics
    recommendations = query.order_by(
        desc(Content.average_rating),
        desc(Content.engagement_score),
        desc(Content.view_count)
    ).limit(limit).all()
    
    return {
        "subject": subject,
        "recommendations": [
            {
                "id": content.id,
                "title": content.title,
                "content_type": content.content_type,
                "difficulty_level": content.difficulty_level,
                "estimated_duration_minutes": content.estimated_duration_minutes,
                "average_rating": content.average_rating,
                "description": content.description,
                "recommendation_reason": "Matches your learning style and difficulty preference"
            }
            for content in recommendations
        ]
    }


@router.post("/interactions", response_model=ContentInteractionResponse)
async def create_content_interaction(
    interaction_data: ContentInteractionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record content interaction"""
    # Check if content exists
    content = db.query(Content).filter(Content.id == interaction_data.content_id).first()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Check if there's an existing interaction to update
    existing_interaction = db.query(ContentInteraction).filter(
        and_(
            ContentInteraction.user_id == current_user.id,
            ContentInteraction.content_id == interaction_data.content_id,
            ContentInteraction.interaction_type == interaction_data.interaction_type
        )
    ).first()
    
    if existing_interaction:
        # Update existing interaction
        existing_interaction.progress_percentage = interaction_data.progress_percentage
        existing_interaction.last_position = interaction_data.last_position
        existing_interaction.end_time = datetime.utcnow()
        
        if interaction_data.rating:
            existing_interaction.rating = interaction_data.rating
        if interaction_data.difficulty_rating:
            existing_interaction.difficulty_rating = interaction_data.difficulty_rating
        if interaction_data.usefulness_rating:
            existing_interaction.usefulness_rating = interaction_data.usefulness_rating
        if interaction_data.notes:
            existing_interaction.notes = interaction_data.notes
        
        # Mark as completed if progress is 100%
        if interaction_data.progress_percentage >= 100:
            existing_interaction.is_completed = True
            existing_interaction.completion_time = datetime.utcnow()
        
        db.commit()
        db.refresh(existing_interaction)
        return existing_interaction
    
    else:
        # Create new interaction
        interaction = ContentInteraction(
            user_id=current_user.id,
            content_id=interaction_data.content_id,
            interaction_type=interaction_data.interaction_type,
            progress_percentage=interaction_data.progress_percentage,
            last_position=interaction_data.last_position,
            rating=interaction_data.rating,
            difficulty_rating=interaction_data.difficulty_rating,
            usefulness_rating=interaction_data.usefulness_rating,
            notes=interaction_data.notes
        )
        
        # Mark as completed if progress is 100%
        if interaction_data.progress_percentage >= 100:
            interaction.is_completed = True
            interaction.completion_time = datetime.utcnow()
            
            # Update content completion count
            content.completion_count += 1
        
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        
        return interaction


@router.get("/interactions/my", response_model=List[ContentInteractionResponse])
async def get_my_content_interactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=20, le=100),
    skip: int = Query(default=0, ge=0),
    interaction_type: Optional[str] = Query(default=None)
):
    """Get user's content interactions"""
    query = db.query(ContentInteraction).filter(ContentInteraction.user_id == current_user.id)
    
    if interaction_type:
        query = query.filter(ContentInteraction.interaction_type == interaction_type)
    
    interactions = query.order_by(desc(ContentInteraction.start_time)).offset(skip).limit(limit).all()
    return interactions


@router.get("/interactions/{content_id}/progress")
async def get_content_progress(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's progress on specific content"""
    interaction = db.query(ContentInteraction).filter(
        and_(
            ContentInteraction.user_id == current_user.id,
            ContentInteraction.content_id == content_id,
            ContentInteraction.interaction_type == "view"
        )
    ).order_by(desc(ContentInteraction.start_time)).first()
    
    if not interaction:
        return {
            "content_id": content_id,
            "progress_percentage": 0,
            "is_completed": False,
            "last_position": None,
            "time_spent_seconds": 0
        }
    
    return {
        "content_id": content_id,
        "progress_percentage": interaction.progress_percentage,
        "is_completed": interaction.is_completed,
        "last_position": interaction.last_position,
        "time_spent_seconds": interaction.duration_seconds or 0,
        "last_accessed": interaction.start_time
    }


@router.post("/{content_id}/rate")
async def rate_content(
    content_id: int,
    rating: int = Query(..., ge=1, le=5),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rate content (1-5 stars)"""
    # Check if content exists
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Check if user already rated this content
    existing_rating = db.query(ContentInteraction).filter(
        and_(
            ContentInteraction.user_id == current_user.id,
            ContentInteraction.content_id == content_id,
            ContentInteraction.interaction_type == "rate"
        )
    ).first()
    
    if existing_rating:
        # Update existing rating
        old_rating = existing_rating.rating
        existing_rating.rating = rating
        
        # Update content average rating
        if content.total_ratings > 0:
            total_rating_points = content.average_rating * content.total_ratings
            total_rating_points = total_rating_points - old_rating + rating
            content.average_rating = total_rating_points / content.total_ratings
        
    else:
        # Create new rating interaction
        rating_interaction = ContentInteraction(
            user_id=current_user.id,
            content_id=content_id,
            interaction_type="rate",
            rating=rating
        )
        db.add(rating_interaction)
        
        # Update content average rating
        if content.total_ratings > 0:
            total_rating_points = content.average_rating * content.total_ratings
            content.average_rating = (total_rating_points + rating) / (content.total_ratings + 1)
        else:
            content.average_rating = rating
        
        content.total_ratings += 1
    
    db.commit()
    
    return {
        "message": "Content rated successfully",
        "rating": rating,
        "new_average_rating": round(content.average_rating, 2)
    }


@router.get("/subjects/list")
async def get_available_subjects(db: Session = Depends(get_db)):
    """Get list of available subjects"""
    subjects = db.query(Content.subject).filter(Content.is_active == True).distinct().all()
    return {"subjects": [subject[0] for subject in subjects]}


@router.get("/analytics/engagement")
async def get_content_engagement_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(default=30, ge=1, le=365)
):
    """Get user's content engagement analytics"""
    from datetime import timedelta
    
    # Get interactions from the specified period
    interactions = db.query(ContentInteraction).filter(
        and_(
            ContentInteraction.user_id == current_user.id,
            ContentInteraction.start_time >= datetime.utcnow() - timedelta(days=days)
        )
    ).all()
    
    if not interactions:
        return {
            "total_interactions": 0,
            "content_types_engaged": [],
            "subjects_studied": [],
            "completion_rate": 0,
            "average_session_duration": 0
        }
    
    # Analyze engagement patterns
    content_types = {}
    subjects = {}
    total_duration = 0
    completed_interactions = 0
    
    for interaction in interactions:
        # Content types
        if interaction.content:
            content_type = interaction.content.content_type
            subject = interaction.content.subject
            
            content_types[content_type] = content_types.get(content_type, 0) + 1
            subjects[subject] = subjects.get(subject, 0) + 1
        
        # Duration
        if interaction.duration_seconds:
            total_duration += interaction.duration_seconds
        
        # Completion
        if interaction.is_completed:
            completed_interactions += 1
    
    return {
        "total_interactions": len(interactions),
        "content_types_engaged": [
            {"type": ct, "count": count} for ct, count in content_types.items()
        ],
        "subjects_studied": [
            {"subject": subj, "count": count} for subj, count in subjects.items()
        ],
        "completion_rate": round(completed_interactions / len(interactions) * 100, 2),
        "average_session_duration": round(total_duration / len(interactions) / 60, 2) if interactions else 0,  # minutes
        "total_study_time_hours": round(total_duration / 3600, 2)
    }