"""
Academic Guidance Router for AI-Powered Academic Guidance System

This module defines FastAPI endpoints for student activity logging,
progress tracking, and personalized guidance insights.

Endpoints:
- POST /api/guidance/activity/log: Log student learning activity
- GET /api/guidance/progress/{student_id}: Get comprehensive progress report
- GET /api/guidance/insights/{student_id}: Get specific guidance insights
- POST /api/guidance/analyze/{student_id}: Trigger learning analysis
- GET /api/guidance/recommendations/{student_id}: Get current recommendations

Author: Mentor AI Team
Version: 1.0.0
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Depends, Query, status, Body
from pydantic import BaseModel, Field

from models.learning_analytics_models import (
    TopicAccess, QuizAttempt, QuestionError, LearningSequence,
    StudentActivityLog, LearningActivityType, DifficultyLevel
)
from services.academic_guidance_service import (
    academic_guidance_service,
    AcademicGuidanceServiceError,
    StudentNotFoundError,
    InvalidActivityError
)
from middleware.testing_auth import get_current_user_testing as get_current_user

# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@router.get(
    "/health",
    summary="Health Check",
    description=f"Check if the guidance service is operational",
    tags=["Health"]
)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Service health status
    """
    from datetime import datetime
    return {
        "status": "healthy",
        "service": "guidance",
        "timestamp": datetime.utcnow().isoformat()
    }


# Configure logging
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(
    prefix="/api/guidance",
    tags=["Academic Guidance"]
)


class ActivityLogRequest(BaseModel):
    """Request model for activity logging."""
    
    student_id: str = Field(..., description="Student identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    activities: List[Dict[str, Any]] = Field(..., description="List of activities")
    session_start: Optional[datetime] = Field(None, description="Session start time")
    session_end: Optional[datetime] = Field(None, description="Session end time")
    total_duration_minutes: Optional[int] = Field(None, ge=0, description="Total session duration")
    device_type: Optional[str] = Field(None, description="Device type")
    browser: Optional[str] = Field(None, description="Browser used")
    ip_address: Optional[str] = Field(None, description="IP address")
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "student_123",
                "session_id": "session_456",
                "activities": [
                    {
                        "activity_type": "topic_study",
                        "topic_id": "topic_thermodynamics_001",
                        "subject": "Physics",
                        "chapter": "Thermodynamics",
                        "sequence_number": 1,
                        "access_time": "2024-01-15T10:30:00Z",
                        "time_spent_minutes": 45,
                        "completion_percentage": 80.0
                    }
                ],
                "session_start": "2024-01-15T10:00:00Z",
                "session_end": "2024-01-15T12:00:00Z",
                "total_duration_minutes": 120,
                "device_type": "desktop",
                "browser": "Chrome"
            }
        }


class TopicAccessRequest(BaseModel):
    """Request model for topic access logging."""
    
    student_id: str = Field(..., description="Student identifier")
    topic_id: str = Field(..., description="Topic identifier")
    subject: str = Field(..., description="Subject name")
    chapter: Optional[str] = Field(None, description="Chapter name")
    sequence_number: Optional[int] = Field(0, description="Sequence in learning path")
    access_time: Optional[datetime] = Field(None, description="Access time")
    time_spent_minutes: int = Field(..., ge=0, description="Time spent in minutes")
    completion_percentage: float = Field(..., ge=0, le=100, description="Completion percentage")
    activity_type: LearningActivityType = Field(..., description="Activity type")
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "student_123",
                "topic_id": "topic_thermodynamics_001",
                "subject": "Physics",
                "chapter": "Thermodynamics",
                "sequence_number": 3,
                "access_time": "2024-01-15T10:30:00Z",
                "time_spent_minutes": 45,
                "completion_percentage": 80.0,
                "activity_type": "topic_study"
            }
        }


class QuizAttemptRequest(BaseModel):
    """Request model for quiz attempt logging."""
    
    student_id: str = Field(..., description="Student identifier")
    quiz_id: str = Field(..., description="Quiz identifier")
    subject: str = Field(..., description="Subject name")
    topic_id: str = Field(..., description="Primary topic")
    difficulty: DifficultyLevel = Field(..., description="Quiz difficulty")
    start_time: datetime = Field(..., description="Quiz start time")
    end_time: datetime = Field(..., description="Quiz end time")
    total_time_minutes: int = Field(..., ge=0, description="Total time taken")
    total_questions: int = Field(..., gt=0, description="Total questions")
    attempted_questions: int = Field(..., ge=0, description="Questions attempted")
    correct_answers: int = Field(..., ge=0, description="Correct answers")
    score_percentage: float = Field(..., ge=0, le=100, description="Score percentage")
    question_errors: Optional[List[Dict[str, Any]]] = Field(None, description="List of question errors")
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "student_123",
                "quiz_id": "quiz_thermo_001",
                "subject": "Physics",
                "topic_id": "topic_thermodynamics_001",
                "difficulty": "medium",
                "start_time": "2024-01-15T14:00:00Z",
                "end_time": "2024-01-15T15:30:00Z",
                "total_time_minutes": 90,
                "total_questions": 20,
                "attempted_questions": 18,
                "correct_answers": 12,
                "score_percentage": 66.7,
                "question_errors": [
                    {
                        "question_number": 5,
                        "error_type": "formula_error",
                        "error_description": "Applied wrong formula for heat transfer",
                        "student_answer": "25 J",
                        "correct_answer": "35 J",
                        "time_spent_seconds": 180,
                        "confidence_level": 7.0
                    }
                ]
            }
        }


class LearningSequenceRequest(BaseModel):
    """Request model for learning sequence logging."""
    
    student_id: str = Field(..., description="Student identifier")
    session_date: datetime = Field(..., description="Session date")
    session_duration_minutes: int = Field(..., ge=0, description="Session duration")
    topic_sequence: List[str] = Field(..., description="Ordered topic sequence")
    subject_transitions: Optional[List[Dict[str, Any]]] = Field(None, description="Subject transitions")
    completion_rates: Optional[Dict[str, float]] = Field(None, description="Completion rates")
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "student_123",
                "session_date": "2024-01-15",
                "session_duration_minutes": 120,
                "topic_sequence": [
                    "topic_mechanics_001",
                    "topic_thermodynamics_001",
                    "topic_optics_001"
                ],
                "subject_transitions": [
                    {"from": "Physics", "to": "Physics", "at_topic": "topic_thermodynamics_001"}
                ],
                "completion_rates": {
                    "topic_mechanics_001": 100.0,
                    "topic_thermodynamics_001": 80.0,
                    "topic_optics_001": 60.0
                }
            }
        }


def verify_student_or_parent_access(student_id: str, current_user: str) -> bool:
    """
    Verify that the current user has access to student data.
    
    In a real implementation, this would check:
    - If current user is the student themselves
    - If current user is a parent of the student
    - Firebase auth integration
    
    For now, this is a placeholder that always returns True.
    """
    # TODO: Implement actual access verification
    # This would typically check:
    # 1. JWT token validation
    # 2. Firebase user ID verification
    # 3. Parent-child relationship validation
    return True


@router.post(
    "/activity/log",
    status_code=status.HTTP_201_CREATED,
    summary="Log student activity",
    description="""
    Log a student learning activity including topic access, quiz attempts,
    and learning sequences. This endpoint processes the activity data
    and triggers analysis when sufficient data is available.
    
    **Activity Types:**
    - topic_study: Student studied a specific topic
    - quiz_attempt: Student attempted a quiz
    - practice_problems: Student practiced problems
    - video_watch: Student watched educational video
    - revision: Student revised previously studied topics
    - doubt_resolution: Student resolved doubts
    
    **Processing:**
    - Activities are stored individually for detailed tracking
    - Session data is aggregated for analysis
    - Automatic analysis triggered when threshold met
    """,
    responses={
        201: {
            "description": "Activity logged successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "log_id": "log_abc123",
                        "message": "Activity logged successfully",
                        "analysis_triggered": False
                    }
                }
            }
        },
        400: {"description": "Invalid activity data"},
        401: {"description": "Unauthorized access"},
        404: {"description": "Student not found"},
        500: {"description": "Internal server error"}
    }
)
async def log_student_activity(
    request: ActivityLogRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Log a student learning activity.
    
    Args:
        request: ActivityLogRequest with activity details
        current_user: Authenticated user ID
        
    Returns:
        Success response with log ID
        
    Raises:
        HTTPException: 400 for validation errors
        HTTPException: 401 for unauthorized access
        HTTPException: 404 if student not found
        HTTPException: 500 for processing errors
    """
    try:
        logger.info(f"Logging activity for student: {request.student_id}")
        
        # Verify access
        if not verify_student_or_parent_access(request.student_id, current_user):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access denied: insufficient permissions"
            )
        
        # Log activity
        log_id = await academic_guidance_service.log_student_activity(
            student_id=request.student_id,
            activity_data=request.model_dump()
        )
        
        # Check if analysis should be triggered
        # This would typically check if enough data has accumulated
        analysis_triggered = False  # Placeholder logic
        
        logger.info(f"Activity logged successfully: {log_id}")
        
        return {
            "success": True,
            "log_id": log_id,
            "message": "Activity logged successfully",
            "analysis_triggered": analysis_triggered,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except StudentNotFoundError as e:
        logger.warning(f"Student not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    except InvalidActivityError as e:
        logger.warning(f"Invalid activity data: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except AcademicGuidanceServiceError as e:
        logger.error(f"Failed to log activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log activity. Please try again later."
        )
    
    except Exception as e:
        logger.error(f"Unexpected error logging activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )


@router.post(
    "/activity/topic-access",
    status_code=status.HTTP_201_CREATED,
    summary="Log topic access",
    description="""
    Log a student's topic access activity. This is a specialized endpoint
    for logging when a student accesses and studies a specific topic.
    """,
    responses={
        201: {"description": "Topic access logged successfully"},
        400: {"description": "Invalid topic access data"},
        401: {"description": "Unauthorized access"},
        404: {"description": "Student not found"},
        500: {"description": "Internal server error"}
    }
)
async def log_topic_access(
    request: TopicAccessRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Log a student's topic access activity.
    
    Args:
        request: TopicAccessRequest with topic details
        current_user: Authenticated user ID
        
    Returns:
        Success response with activity ID
    """
    try:
        logger.info(f"Logging topic access for student: {request.student_id}")
        
        # Verify access
        if not verify_student_or_parent_access(request.student_id, current_user):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access denied: insufficient permissions"
            )
        
        # Convert to activity log format
        activity_data = {
            "activities": [{
                "activity_type": request.activity_type,
                "topic_id": request.topic_id,
                "subject": request.subject,
                "chapter": request.chapter,
                "sequence_number": request.sequence_number,
                "access_time": request.access_time,
                "time_spent_minutes": request.time_spent_minutes,
                "completion_percentage": request.completion_percentage
            }],
            "session_start": request.access_time,
            "total_duration_minutes": request.time_spent_minutes
        }
        
        # Log activity
        log_id = await academic_guidance_service.log_student_activity(
            student_id=request.student_id,
            activity_data=activity_data
        )
        
        logger.info(f"Topic access logged successfully: {log_id}")
        
        return {
            "success": True,
            "log_id": log_id,
            "message": "Topic access logged successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to log topic access: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log topic access. Please try again later."
        )


@router.post(
    "/activity/quiz-attempt",
    status_code=status.HTTP_201_CREATED,
    summary="Log quiz attempt",
    description="""
    Log a student's quiz attempt with detailed error analysis.
    This endpoint captures comprehensive quiz performance data.
    """,
    responses={
        201: {"description": "Quiz attempt logged successfully"},
        400: {"description": "Invalid quiz attempt data"},
        401: {"description": "Unauthorized access"},
        404: {"description": "Student not found"},
        500: {"description": "Internal server error"}
    }
)
async def log_quiz_attempt(
    request: QuizAttemptRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Log a student's quiz attempt.
    
    Args:
        request: QuizAttemptRequest with quiz details
        current_user: Authenticated user ID
        
    Returns:
        Success response with attempt ID
    """
    try:
        logger.info(f"Logging quiz attempt for student: {request.student_id}")
        
        # Verify access
        if not verify_student_or_parent_access(request.student_id, current_user):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access denied: insufficient permissions"
            )
        
        # Convert to activity log format
        activity_data = {
            "activities": [{
                "activity_type": "quiz_attempt",
                "quiz_id": request.quiz_id,
                "subject": request.subject,
                "topic_id": request.topic_id,
                "difficulty": request.difficulty,
                "start_time": request.start_time,
                "end_time": request.end_time,
                "total_time_minutes": request.total_time_minutes,
                "total_questions": request.total_questions,
                "attempted_questions": request.attempted_questions,
                "correct_answers": request.correct_answers,
                "score_percentage": request.score_percentage,
                "question_errors": request.question_errors
            }],
            "session_start": request.start_time,
            "session_end": request.end_time,
            "total_duration_minutes": request.total_time_minutes
        }
        
        # Log activity
        log_id = await academic_guidance_service.log_student_activity(
            student_id=request.student_id,
            activity_data=activity_data
        )
        
        logger.info(f"Quiz attempt logged successfully: {log_id}")
        
        return {
            "success": True,
            "log_id": log_id,
            "message": "Quiz attempt logged successfully",
            "score_percentage": request.score_percentage,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to log quiz attempt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log quiz attempt. Please try again later."
        )


@router.post(
    "/activity/learning-sequence",
    status_code=status.HTTP_201_CREATED,
    summary="Log learning sequence",
    description="""
    Log a student's learning sequence during a study session.
    This captures the order and context of topic exploration.
    """,
    responses={
        201: {"description": "Learning sequence logged successfully"},
        400: {"description": "Invalid learning sequence data"},
        401: {"description": "Unauthorized access"},
        404: {"description": "Student not found"},
        500: {"description": "Internal server error"}
    }
)
async def log_learning_sequence(
    request: LearningSequenceRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Log a student's learning sequence.
    
    Args:
        request: LearningSequenceRequest with sequence details
        current_user: Authenticated user ID
        
    Returns:
        Success response with sequence ID
    """
    try:
        logger.info(f"Logging learning sequence for student: {request.student_id}")
        
        # Verify access
        if not verify_student_or_parent_access(request.student_id, current_user):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access denied: insufficient permissions"
            )
        
        # Convert to activity log format
        activity_data = {
            "activities": [{
                "activity_type": "learning_sequence",
                "session_date": request.session_date,
                "session_duration_minutes": request.session_duration_minutes,
                "topic_sequence": request.topic_sequence,
                "subject_transitions": request.subject_transitions,
                "completion_rates": request.completion_rates
            }],
            "session_start": request.session_date,
            "total_duration_minutes": request.session_duration_minutes
        }
        
        # Log activity
        log_id = await academic_guidance_service.log_student_activity(
            student_id=request.student_id,
            activity_data=activity_data
        )
        
        logger.info(f"Learning sequence logged successfully: {log_id}")
        
        return {
            "success": True,
            "log_id": log_id,
            "message": "Learning sequence logged successfully",
            "topics_count": len(request.topic_sequence),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to log learning sequence: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log learning sequence. Please try again later."
        )


@router.post(
    "/analyze/{student_id}",
    summary="Trigger learning analysis",
    description="""
    Trigger comprehensive learning analysis for a student.
    This endpoint forces a fresh analysis of all available data
    and generates new patterns, gaps, strengths, and recommendations.
    """,
    responses={
        200: {
            "description": "Analysis completed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Analysis completed",
                        "analysis_id": "analysis_123",
                        "patterns_identified": 5,
                        "gaps_identified": 3,
                        "strengths_identified": 2,
                        "recommendations_generated": 8
                    }
                }
            }
        },
        401: {"description": "Unauthorized access"},
        404: {"description": "Student not found"},
        500: {"description": "Internal server error"}
    }
)
async def trigger_learning_analysis(
    student_id: str,
    force_refresh: bool = Query(False, description="Force fresh analysis"),
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Trigger learning analysis for a student.
    
    Args:
        student_id: Student identifier
        force_refresh: Force new analysis even if cached
        current_user: Authenticated user ID
        
    Returns:
        Analysis results summary
    """
    try:
        logger.info(f"Triggering analysis for student: {student_id}")
        
        # Verify access
        if not verify_student_or_parent_access(student_id, current_user):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access denied: insufficient permissions"
            )
        
        # Perform analysis
        analysis_results = await academic_guidance_service.analyze_student_learning(
            student_id=student_id,
            force_refresh=force_refresh
        )
        
        # Return summary
        return {
            "success": True,
            "message": "Analysis completed successfully",
            "analysis_id": f"analysis_{student_id}_{int(datetime.utcnow().timestamp())}",
            "analysis_timestamp": analysis_results.get("analysis_timestamp"),
            "status": analysis_results.get("status"),
            "patterns_identified": len(analysis_results.get("learning_patterns", [])),
            "gaps_identified": len(analysis_results.get("knowledge_gaps", [])),
            "strengths_identified": len(analysis_results.get("learning_strengths", [])),
            "recommendations_generated": len(analysis_results.get("recommendations", [])),
            "data_summary": analysis_results.get("data_summary", {})
        }
        
    except StudentNotFoundError as e:
        logger.warning(f"Student not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    except AcademicGuidanceServiceError as e:
        logger.error(f"Failed to trigger analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete analysis. Please try again later."
        )
    
    except Exception as e:
        logger.error(f"Unexpected error in analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )