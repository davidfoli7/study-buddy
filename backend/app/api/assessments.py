from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
from pydantic import BaseModel

from ..core.database import get_db
from ..models.user import User
from ..models.assessment import Assessment, Question, Answer
from .auth import get_current_user

router = APIRouter()


class QuestionCreate(BaseModel):
    question_text: str
    question_type: str
    difficulty_level: str = "medium"
    subject: str
    topic: Optional[str] = None
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: Optional[str] = None
    points_possible: float = 1.0


class QuestionResponse(BaseModel):
    id: int
    question_text: str
    question_type: str
    difficulty_level: str
    subject: str
    topic: Optional[str]
    options: Optional[List[str]]
    explanation: Optional[str]
    points_possible: float
    
    class Config:
        from_attributes = True


class AssessmentCreate(BaseModel):
    title: str
    subject: str
    topic: Optional[str] = None
    assessment_type: str = "formative"
    difficulty_level: str = "medium"
    time_limit_minutes: Optional[int] = None
    questions: List[QuestionCreate] = []


class AssessmentResponse(BaseModel):
    id: int
    title: str
    subject: str
    topic: Optional[str]
    assessment_type: str
    difficulty_level: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    time_limit_minutes: Optional[int]
    time_taken_minutes: Optional[float]
    total_questions: int
    questions_answered: int
    correct_answers: int
    score_percentage: Optional[float]
    status: str
    is_completed: bool
    strengths: Optional[str]
    weaknesses: Optional[str]
    recommendations: Optional[str]
    
    class Config:
        from_attributes = True


class AnswerSubmission(BaseModel):
    question_id: int
    answer_text: Optional[str] = None
    selected_option: Optional[str] = None


class AssessmentSubmission(BaseModel):
    answers: List[AnswerSubmission]


@router.post("/", response_model=AssessmentResponse)
async def create_assessment(
    assessment_data: AssessmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new assessment"""
    assessment = Assessment(
        user_id=current_user.id,
        title=assessment_data.title,
        subject=assessment_data.subject,
        topic=assessment_data.topic,
        assessment_type=assessment_data.assessment_type,
        difficulty_level=assessment_data.difficulty_level,
        time_limit_minutes=assessment_data.time_limit_minutes,
        total_questions=len(assessment_data.questions)
    )
    
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    
    # Add questions
    for q_data in assessment_data.questions:
        question = Question(
            assessment_id=assessment.id,
            question_text=q_data.question_text,
            question_type=q_data.question_type,
            difficulty_level=q_data.difficulty_level,
            subject=q_data.subject,
            topic=q_data.topic,
            options=",".join(q_data.options) if q_data.options else None,
            correct_answer=q_data.correct_answer,
            explanation=q_data.explanation,
            points_possible=q_data.points_possible
        )
        db.add(question)
    
    db.commit()
    db.refresh(assessment)
    
    return assessment


@router.get("/", response_model=List[AssessmentResponse])
async def get_assessments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=20, le=100),
    skip: int = Query(default=0, ge=0),
    subject: Optional[str] = Query(default=None),
    assessment_type: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None)
):
    """Get user's assessments with optional filtering"""
    query = db.query(Assessment).filter(Assessment.user_id == current_user.id)
    
    if subject:
        query = query.filter(Assessment.subject == subject)
    if assessment_type:
        query = query.filter(Assessment.assessment_type == assessment_type)
    if status:
        query = query.filter(Assessment.status == status)
    
    assessments = query.order_by(desc(Assessment.created_at)).offset(skip).limit(limit).all()
    return assessments


@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific assessment"""
    assessment = db.query(Assessment).filter(
        and_(
            Assessment.id == assessment_id,
            Assessment.user_id == current_user.id
        )
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    return assessment


@router.get("/{assessment_id}/questions", response_model=List[QuestionResponse])
async def get_assessment_questions(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get questions for an assessment"""
    assessment = db.query(Assessment).filter(
        and_(
            Assessment.id == assessment_id,
            Assessment.user_id == current_user.id
        )
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    questions = db.query(Question).filter(Question.assessment_id == assessment_id).all()
    
    # Parse options for response
    for question in questions:
        if question.options:
            question.options = question.options.split(",")
        else:
            question.options = []
    
    return questions


@router.post("/{assessment_id}/start")
async def start_assessment(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start an assessment"""
    assessment = db.query(Assessment).filter(
        and_(
            Assessment.id == assessment_id,
            Assessment.user_id == current_user.id
        )
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    if assessment.status != "not_started":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assessment has already been started"
        )
    
    assessment.status = "in_progress"
    assessment.start_time = datetime.utcnow()
    
    db.commit()
    db.refresh(assessment)
    
    return {"message": "Assessment started successfully", "assessment": assessment}


@router.post("/{assessment_id}/submit")
async def submit_assessment(
    assessment_id: int,
    submission: AssessmentSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit answers for an assessment"""
    assessment = db.query(Assessment).filter(
        and_(
            Assessment.id == assessment_id,
            Assessment.user_id == current_user.id
        )
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    if assessment.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assessment is not in progress"
        )
    
    # Get all questions for this assessment
    questions = db.query(Question).filter(Question.assessment_id == assessment_id).all()
    question_dict = {q.id: q for q in questions}
    
    correct_answers = 0
    total_points = 0
    earned_points = 0
    
    # Process each answer
    for answer_data in submission.answers:
        question = question_dict.get(answer_data.question_id)
        if not question:
            continue
        
        # Create answer record
        answer = Answer(
            assessment_id=assessment_id,
            question_id=answer_data.question_id,
            user_id=current_user.id,
            answer_text=answer_data.answer_text,
            selected_option=answer_data.selected_option,
            points_possible=question.points_possible
        )
        
        # Check if answer is correct
        user_answer = answer_data.answer_text or answer_data.selected_option
        if user_answer and user_answer.strip().lower() == question.correct_answer.strip().lower():
            answer.is_correct = True
            answer.points_earned = question.points_possible
            correct_answers += 1
            earned_points += question.points_possible
        else:
            answer.is_correct = False
            answer.points_earned = 0
        
        total_points += question.points_possible
        db.add(answer)
    
    # Update assessment
    assessment.end_time = datetime.utcnow()
    assessment.is_completed = True
    assessment.status = "completed"
    assessment.questions_answered = len(submission.answers)
    assessment.correct_answers = correct_answers
    assessment.score_percentage = (earned_points / total_points * 100) if total_points > 0 else 0
    
    if assessment.start_time:
        duration = assessment.end_time - assessment.start_time
        assessment.time_taken_minutes = duration.total_seconds() / 60
    
    # Update user stats
    current_user.total_assessments_completed += 1
    if current_user.total_assessments_completed > 0:
        current_user.average_score = (
            (current_user.average_score * (current_user.total_assessments_completed - 1) + assessment.score_percentage) 
            / current_user.total_assessments_completed
        )
    
    db.commit()
    db.refresh(assessment)
    
    return {
        "message": "Assessment submitted successfully",
        "assessment": assessment,
        "score": assessment.score_percentage,
        "correct_answers": correct_answers,
        "total_questions": len(questions)
    }


@router.get("/{assessment_id}/results")
async def get_assessment_results(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed results for a completed assessment"""
    assessment = db.query(Assessment).filter(
        and_(
            Assessment.id == assessment_id,
            Assessment.user_id == current_user.id
        )
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    if not assessment.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assessment is not completed yet"
        )
    
    # Get questions and answers
    questions = db.query(Question).filter(Question.assessment_id == assessment_id).all()
    answers = db.query(Answer).filter(Answer.assessment_id == assessment_id).all()
    
    # Create answer lookup
    answer_dict = {a.question_id: a for a in answers}
    
    # Build detailed results
    question_results = []
    for question in questions:
        answer = answer_dict.get(question.id)
        question_results.append({
            "question_id": question.id,
            "question_text": question.question_text,
            "question_type": question.question_type,
            "correct_answer": question.correct_answer,
            "user_answer": answer.answer_text or answer.selected_option if answer else None,
            "is_correct": answer.is_correct if answer else False,
            "points_earned": answer.points_earned if answer else 0,
            "points_possible": question.points_possible,
            "explanation": question.explanation
        })
    
    return {
        "assessment": assessment,
        "summary": {
            "total_questions": assessment.total_questions,
            "questions_answered": assessment.questions_answered,
            "correct_answers": assessment.correct_answers,
            "score_percentage": assessment.score_percentage,
            "time_taken_minutes": assessment.time_taken_minutes
        },
        "question_results": question_results
    }


@router.get("/analytics/performance")
async def get_assessment_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    subject: Optional[str] = Query(default=None),
    days: int = Query(default=30, ge=1, le=365)
):
    """Get assessment performance analytics"""
    from datetime import timedelta
    
    # Base query
    query = db.query(Assessment).filter(
        and_(
            Assessment.user_id == current_user.id,
            Assessment.is_completed == True,
            Assessment.created_at >= datetime.utcnow() - timedelta(days=days)
        )
    )
    
    if subject:
        query = query.filter(Assessment.subject == subject)
    
    assessments = query.order_by(Assessment.created_at).all()
    
    if not assessments:
        return {
            "total_assessments": 0,
            "average_score": 0,
            "improvement_trend": 0,
            "subject_performance": [],
            "difficulty_performance": [],
            "recent_scores": []
        }
    
    # Calculate metrics
    total_assessments = len(assessments)
    average_score = sum([a.score_percentage for a in assessments]) / total_assessments
    
    # Calculate improvement trend (simple linear trend)
    scores = [a.score_percentage for a in assessments]
    if len(scores) > 1:
        n = len(scores)
        x_sum = sum(range(n))
        y_sum = sum(scores)
        xy_sum = sum(i * score for i, score in enumerate(scores))
        x_squared_sum = sum(i * i for i in range(n))
        
        improvement_trend = (n * xy_sum - x_sum * y_sum) / (n * x_squared_sum - x_sum * x_sum)
    else:
        improvement_trend = 0
    
    # Subject performance
    subject_stats = {}
    for assessment in assessments:
        subject = assessment.subject
        if subject not in subject_stats:
            subject_stats[subject] = {"total": 0, "score_sum": 0, "count": 0}
        subject_stats[subject]["score_sum"] += assessment.score_percentage
        subject_stats[subject]["count"] += 1
    
    subject_performance = [
        {
            "subject": subject,
            "average_score": stats["score_sum"] / stats["count"],
            "assessment_count": stats["count"]
        }
        for subject, stats in subject_stats.items()
    ]
    
    # Difficulty performance
    difficulty_stats = {}
    for assessment in assessments:
        difficulty = assessment.difficulty_level
        if difficulty not in difficulty_stats:
            difficulty_stats[difficulty] = {"score_sum": 0, "count": 0}
        difficulty_stats[difficulty]["score_sum"] += assessment.score_percentage
        difficulty_stats[difficulty]["count"] += 1
    
    difficulty_performance = [
        {
            "difficulty": difficulty,
            "average_score": stats["score_sum"] / stats["count"],
            "assessment_count": stats["count"]
        }
        for difficulty, stats in difficulty_stats.items()
    ]
    
    # Recent scores for trend visualization
    recent_scores = [
        {
            "date": assessment.created_at.strftime("%Y-%m-%d"),
            "score": assessment.score_percentage,
            "subject": assessment.subject
        }
        for assessment in assessments[-10:]  # Last 10 assessments
    ]
    
    return {
        "total_assessments": total_assessments,
        "average_score": round(average_score, 2),
        "improvement_trend": round(improvement_trend, 4),
        "subject_performance": subject_performance,
        "difficulty_performance": difficulty_performance,
        "recent_scores": recent_scores
    }