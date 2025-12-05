"""
Progress and Insights Router for AI-Powered Academic Guidance System

This module defines FastAPI endpoints for accessing student progress reports,
personalized guidance insights, and recommendations.

Endpoints:
- GET /api/progress/{student_id}: Get comprehensive progress report
- GET /api/insights/{student_id}: Get specific guidance insights
- GET /api/recommendations/{student_id}: Get current recommendations
- GET /api/progress/{student_id}/summary: Get progress summary
- GET /api/insights/{student_id}/patterns: Get learning patterns
- GET /api/insights/{student_id}/gaps: Get knowledge gaps
- GET /api/insights/{student_id}/strengths: Get learning strengths

Author: Mentor AI Team
Version: 1.0.0
"""

import logging
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel

from services.academic_guidance_service import (
    academic_guidance_service,
    AcademicGuidanceServiceError,
    StudentNotFoundError
)
from middleware.testing_auth import get_current_user_testing as get_current_user

# Configure logging
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(
    prefix="/api/progress",
    tags=["Progress & Insights"]
)


class ProgressResponse(BaseModel):
    """Response model for progress data."""
    
    success: bool
    student_id: str
    report_generated_at: datetime
    analysis_summary: Dict[str, Any]
    progress_data: Dict[str, Any]
    performance_trends: Dict[str, Any]
    next_steps: List[Dict[str, str]]
    recent_activities: List[Dict[str, Any]]
    current_recommendations: List[Dict[str, Any]]
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "student_id": "student_123",
                "report_generated_at": "2024-01-15T16:30:00Z",
                "analysis_summary": {
                    "status": "completed",
                    "learning_patterns_count": 5,
                    "knowledge_gaps_count": 3,
                    "learning_strengths_count": 2,
                    "recommendations_count": 8
                },
                "progress_data": {
                    "study_streak": {"current_streak": 5, "longest_streak": 12},
                    "time_metrics": {"total_hours": 45.0, "average_session_minutes": 75.5},
                    "performance_metrics": {"average_score": 72.5, "recent_trend": "improving"}
                },
                "performance_trends": {
                    "trend": "improving",
                    "average_score": 72.5,
                    "best_score": 85.0
                },
                "next_steps": [
                    {
                        "priority": "urgent",
                        "action": "Address critical knowledge gaps",
                        "description": "Focus on 2 critical knowledge gaps immediately"
                    }
                ]
            }
        }


class InsightsResponse(BaseModel):
    """Response model for guidance insights."""
    
    success: bool
    student_id: str
    insight_type: str
    data: Union[List[Dict[str, Any]], Dict[str, Any]]
    summary: str
    metadata: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "student_id": "student_123",
                "insight_type": "comprehensive",
                "data": {
                    "learning_patterns": [],
                    "knowledge_gaps": [],
                    "learning_strengths": [],
                    "recommendations": []
                },
                "summary": "Comprehensive insights with 5 patterns, 3 gaps, 2 strengths, and 8 recommendations",
                "metadata": {
                    "generated_at": "2024-01-15T16:30:00Z",
                    "total_activities": 25
                }
            }
        }


class RecommendationsResponse(BaseModel):
    """Response model for recommendations."""
    
    success: bool
    student_id: str
    recommendations: List[Dict[str, Any]]
    summary: Dict[str, Any]
    generated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "student_id": "student_123",
                "recommendations": [
                    {
                        "recommendation_id": "rec_001",
                        "recommendation_type": "prerequisite_review",
                        "priority": "high",
                        "title": "Review Heat Transfer Basics",
                        "description": "Master foundational concepts before tackling thermodynamics",
                        "estimated_time_hours": 3.0,
                        "resources": [],
                        "action_steps": []
                    }
                ],
                "summary": {
                    "total_recommendations": 8,
                    "urgent_count": 2,
                    "high_count": 3,
                    "medium_count": 2,
                    "low_count": 1
                },
                "generated_at": "2024-01-15T16:30:00Z"
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


@router.get(
    "/{student_id}",
    response_model=ProgressResponse,
    summary="Get comprehensive progress report",
    description="""
    Get a comprehensive progress report for a student including:
    - Learning patterns and analysis
    - Knowledge gaps and their severity
    - Learning strengths and mastery levels
    - Personalized recommendations
    - Performance trends and metrics
    - Recent activities and next steps
    
    **Access Control:**
    - Students can access their own progress
    - Parents can access their children's progress
    - Requires valid authentication token
    """,
    responses={
        200: {"description": "Progress report retrieved successfully"},
        401: {"description": "Unauthorized access"},
        404: {"description": "Student not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_progress_report(
    student_id: str,
    include_recent: bool = Query(True, description="Include recent activities"),
    include_recommendations: bool = Query(True, description="Include current recommendations"),
    parent_id: Optional[str] = Query(None, description="Parent ID for access control"),
    current_user: str = Depends(get_current_user)
) -> ProgressResponse:
    """
    Get comprehensive progress report for a student.
    
    Args:
        student_id: Student identifier
        include_recent: Whether to include recent activities
        include_recommendations: Whether to include recommendations
        parent_id: Parent ID for access control
        current_user: Authenticated user ID
        
    Returns:
        Comprehensive progress report
        
    Raises:
        HTTPException: 401 for unauthorized access
        HTTPException: 404 if student not found
        HTTPException: 500 for processing errors
    """
    try:
        logger.info(f"Getting progress report for student: {student_id}")
        
        # Verify access
        if not verify_student_or_parent_access(student_id, current_user):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access denied: insufficient permissions"
            )
        
        # Get progress report
        progress_report = await academic_guidance_service.get_student_progress_report(
            student_id=student_id,
            parent_id=parent_id
        )
        
        logger.info(f"Progress report retrieved for student: {student_id}")
        
        return ProgressResponse(**progress_report)
        
    except StudentNotFoundError as e:
        logger.warning(f"Student not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    except AcademicGuidanceServiceError as e:
        logger.error(f"Failed to get progress report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve progress report. Please try again later."
        )
    
    except Exception as e:
        logger.error(f"Unexpected error getting progress report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )


@router.get(
    "/{student_id}/summary",
    summary="Get progress summary",
    description="""
    Get a concise summary of student progress including:
    - Overall completion percentage
    - Current study streak
    - Average performance metrics
    - Subject-wise progress
    - Recent activity count
    
    This endpoint provides a quick overview suitable for dashboards.
    """,
    responses={
        200: {"description": "Progress summary retrieved successfully"},
        401: {"description": "Unauthorized access"},
        404: {"description": "Student not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_progress_summary(
    student_id: str,
    parent_id: Optional[str] = Query(None, description="Parent ID for access control"),
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get concise progress summary for a student.
    
    Args:
        student_id: Student identifier
        parent_id: Parent ID for access control
        current_user: Authenticated user ID
        
    Returns:
        Progress summary data
    """
    try:
        logger.info(f"Getting progress summary for student: {student_id}")
        
        # Verify access
        if not verify_student_or_parent_access(student_id, current_user):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access denied: insufficient permissions"
            )
        
        # Get full progress report
        progress_report = await academic_guidance_service.get_student_progress_report(
            student_id=student_id,
            parent_id=parent_id
        )
        
        # Extract summary data
        progress_data = progress_report.get("progress_data", {})
        analysis_summary = progress_report.get("analysis_summary", {})
        
        # Create summary
        summary = {
            "student_id": student_id,
            "overall_progress": progress_data.get("completion_metrics", {}).get("overall_progress", 0),
            "current_streak": progress_data.get("study_streak", {}).get("current_streak", 0),
            "longest_streak": progress_data.get("study_streak", {}).get("longest_streak", 0),
            "total_study_hours": progress_data.get("time_metrics", {}).get("total_hours", 0),
            "average_session_time": progress_data.get("time_metrics", {}).get("average_session_minutes", 0),
            "average_score": progress_data.get("performance_metrics", {}).get("average_score", 0),
            "performance_trend": progress_data.get("performance_metrics", {}).get("recent_trend", "stable"),
            "subjects_mastered": len(progress_report.get("learning_strengths", [])),
            "critical_gaps": len([gap for gap in progress_report.get("knowledge_gaps", []) 
                               if gap.get("severity") == "critical"]),
            "active_recommendations": analysis_summary.get("recommendations_count", 0),
            "last_activity": progress_report.get("recent_activities", [{}])[0].get("session_start") if progress_report.get("recent_activities") else None,
            "summary_generated_at": progress_report.get("report_generated_at")
        }
        
        logger.info(f"Progress summary retrieved for student: {student_id}")
        return summary
        
    except Exception as e:
        logger.error(f"Failed to get progress summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve progress summary. Please try again later."
        )


@router.get(
    "/insights/{student_id}",
    response_model=InsightsResponse,
    summary="Get guidance insights",
    description="""
    Get specific guidance insights for a student. Available insight types:
    - comprehensive: All insights (patterns, gaps, strengths, recommendations)
    - patterns: Learning patterns only
    - gaps: Knowledge gaps only
    - strengths: Learning strengths only
    - recommendations: Recommendations only
    
    **Access Control:**
    - Students can access their own insights
    - Parents can access their children's insights
    - Requires valid authentication token
    """,
    responses={
        200: {"description": "Insights retrieved successfully"},
        401: {"description": "Unauthorized access"},
        404: {"description": "Student not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_guidance_insights(
    student_id: str,
    insight_type: Optional[str] = Query("comprehensive", description="Type of insight"),
    parent_id: Optional[str] = Query(None, description="Parent ID for access control"),
    current_user: str = Depends(get_current_user)
) -> InsightsResponse:
    """
    Get specific guidance insights for a student.
    
    Args:
        student_id: Student identifier
        insight_type: Type of insight to retrieve
        parent_id: Parent ID for access control
        current_user: Authenticated user ID
        
    Returns:
        Guidance insights data
    """
    try:
        logger.info(f"Getting guidance insights for student: {student_id}, type: {insight_type}")
        
        # Verify access
        if not verify_student_or_parent_access(student_id, current_user):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access denied: insufficient permissions"
            )
        
        # Get insights
        insights = await academic_guidance_service.get_guidance_insights(
            student_id=student_id,
            insight_type=insight_type,
            parent_id=parent_id
        )
        
        logger.info(f"Guidance insights retrieved for student: {student_id}")
        
        return InsightsResponse(**insights)
        
    except AcademicGuidanceServiceError as e:
        logger.error(f"Failed to get guidance insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve guidance insights. Please try again later."
        )
    
    except Exception as e:
        logger.error(f"Unexpected error getting guidance insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )


@router.get(
    "/insights/{student_id}/patterns",
    summary="Get learning patterns",
    description="""
    Get detailed learning patterns identified for a student including:
    - Time management patterns
    - Difficulty preference patterns
    - Subject transition patterns
    - Error patterns
    - Sequence patterns
    
    Each pattern includes confidence scores and impact levels.
    """,
    responses={
        200: {"description": "Learning patterns retrieved successfully"},
        401: {"description": "Unauthorized access"},
        404: {"description": "Student not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_learning_patterns(
    student_id: str,
    parent_id: Optional[str] = Query(None, description="Parent ID for access control"),
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get learning patterns for a student.
    
    Args:
        student_id: Student identifier
        parent_id: Parent ID for access control
        current_user: Authenticated user ID
        
    Returns:
        Learning patterns data
    """
    try:
        logger.info(f"Getting learning patterns for student: {student_id}")
        
        # Verify access
        if not verify_student_or_parent_access(student_id, current_user):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access denied: insufficient permissions"
            )
        
        # Get patterns insights
        insights = await academic_guidance_service.get_guidance_insights(
            student_id=student_id,
            insight_type="patterns",
            parent_id=parent_id
        )
        
        return {
            "success": True,
            "student_id": student_id,
            "patterns": insights.get("data", []),
            "summary": insights.get("summary", ""),
            "metadata": insights.get("metadata", {}),
            "generated_at": insights.get("metadata", {}).get("generated_at")
        }
        
    except Exception as e:
        logger.error(f"Failed to get learning patterns: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve learning patterns. Please try again later."
        )


@router.get(
    "/insights/{student_id}/gaps",
    summary="Get knowledge gaps",
    description="""
    Get detailed knowledge gaps identified for a student including:
    - Gap type (conceptual, procedural, factual)
    - Severity level (minor, moderate, critical)
    - Evidence supporting gap identification
    - Estimated time to close gaps
    - Prerequisite topics needed
    
    Gaps are prioritized by severity and impact on learning.
    """,
    responses={
        200: {"description": "Knowledge gaps retrieved successfully"},
        401: {"description": "Unauthorized access"},
        404: {"description": "Student not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_knowledge_gaps(
    student_id: str,
    severity_filter: Optional[str] = Query(None, description="Filter by severity"),
    parent_id: Optional[str] = Query(None, description="Parent ID for access control"),
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get knowledge gaps for a student.
    
    Args:
        student_id: Student identifier
        severity_filter: Filter gaps by severity (critical, moderate, minor)
        parent_id: Parent ID for access control
        current_user: Authenticated user ID
        
    Returns:
        Knowledge gaps data
    """
    try:
        logger.info(f"Getting knowledge gaps for student: {student_id}")
        
        # Verify access
        if not verify_student_or_parent_access(student_id, current_user):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access denied: insufficient permissions"
            )
        
        # Get gaps insights
        insights = await academic_guidance_service.get_guidance_insights(
            student_id=student_id,
            insight_type="gaps",
            parent_id=parent_id
        )
        
        gaps = insights.get("data", [])
        
        # Apply severity filter if provided
        if severity_filter:
            gaps = [gap for gap in gaps if gap.get("severity") == severity_filter]
        
        # Calculate summary
        summary = {
            "total_gaps": len(gaps),
            "critical_gaps": len([gap for gap in gaps if gap.get("severity") == "critical"]),
            "moderate_gaps": len([gap for gap in gaps if gap.get("severity") == "moderate"]),
            "minor_gaps": len([gap for gap in gaps if gap.get("severity") == "minor"]),
            "total_estimated_hours": sum(gap.get("estimated_hours_to_close", 0) for gap in gaps)
        }
        
        return {
            "success": True,
            "student_id": student_id,
            "gaps": gaps,
            "summary": summary,
            "metadata": insights.get("metadata", {}),
            "generated_at": insights.get("metadata", {}).get("generated_at")
        }
        
    except Exception as e:
        logger.error(f"Failed to get knowledge gaps: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve knowledge gaps. Please try again later."
        )


@router.get(
    "/insights/{student_id}/strengths",
    summary="Get learning strengths",
    description="""
    Get detailed learning strengths identified for a student including:
    - Strength type (conceptual, procedural, application)
    - Mastery level (developing, proficient, advanced)
    - Evidence supporting strength identification
    - Consistency scores
    - Subject-wise strengths
    
    Strengths help identify areas where the student excels.
    """,
    responses={
        200: {"description": "Learning strengths retrieved successfully"},
        401: {"description": "Unauthorized access"},
        404: {"description": "Student not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_learning_strengths(
    student_id: str,
    strength_type: Optional[str] = Query(None, description="Filter by strength type"),
    parent_id: Optional[str] = Query(None, description="Parent ID for access control"),
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get learning strengths for a student.
    
    Args:
        student_id: Student identifier
        strength_type: Filter strengths by type (conceptual, procedural, application)
        parent_id: Parent ID for access control
        current_user: Authenticated user ID
        
    Returns:
        Learning strengths data
    """
    try:
        logger.info(f"Getting learning strengths for student: {student_id}")
        
        # Verify access
        if not verify_student_or_parent_access(student_id, current_user):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access denied: insufficient permissions"
            )
        
        # Get strengths insights
        insights = await academic_guidance_service.get_guidance_insights(
            student_id=student_id,
            insight_type="strengths",
            parent_id=parent_id
        )
        
        strengths = insights.get("data", [])
        
        # Apply type filter if provided
        if strength_type:
            strengths = [strength for strength in strengths if strength.get("strength_type") == strength_type]
        
        # Calculate summary
        summary = {
            "total_strengths": len(strengths),
            "conceptual_strengths": len([s for s in strengths if s.get("strength_type") == "conceptual"]),
            "procedural_strengths": len([s for s in strengths if s.get("strength_type") == "procedural"]),
            "application_strengths": len([s for s in strengths if s.get("strength_type") == "application"]),
            "advanced_strengths": len([s for s in strengths if s.get("mastery_level") == "advanced"]),
            "proficient_strengths": len([s for s in strengths if s.get("mastery_level") == "proficient"])
        }
        
        return {
            "success": True,
            "student_id": student_id,
            "strengths": strengths,
            "summary": summary,
            "metadata": insights.get("metadata", {}),
            "generated_at": insights.get("metadata", {}).get("generated_at")
        }
        
    except Exception as e:
        logger.error(f"Failed to get learning strengths: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve learning strengths. Please try again later."
        )


@router.get(
    "/recommendations/{student_id}",
    response_model=RecommendationsResponse,
    summary="Get current recommendations",
    description="""
    Get current personalized recommendations for a student including:
    - Prerequisite review recommendations
    - Alternative resource suggestions
    - Practice more recommendations
    - Study strategy recommendations
    - Time allocation suggestions
    
    Recommendations are prioritized by urgency and impact.
    """,
    responses={
        200: {"description": "Recommendations retrieved successfully"},
        401: {"description": "Unauthorized access"},
        404: {"description": "Student not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_recommendations(
    student_id: str,
    priority_filter: Optional[str] = Query(None, description="Filter by priority"),
    type_filter: Optional[str] = Query(None, description="Filter by recommendation type"),
    parent_id: Optional[str] = Query(None, description="Parent ID for access control"),
    current_user: str = Depends(get_current_user)
) -> RecommendationsResponse:
    """
    Get current recommendations for a student.
    
    Args:
        student_id: Student identifier
        priority_filter: Filter recommendations by priority (urgent, high, medium, low)
        type_filter: Filter recommendations by type
        parent_id: Parent ID for access control
        current_user: Authenticated user ID
        
    Returns:
        Current recommendations
    """
    try:
        logger.info(f"Getting recommendations for student: {student_id}")
        
        # Verify access
        if not verify_student_or_parent_access(student_id, current_user):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access denied: insufficient permissions"
            )
        
        # Get recommendations insights
        insights = await academic_guidance_service.get_guidance_insights(
            student_id=student_id,
            insight_type="recommendations",
            parent_id=parent_id
        )
        
        recommendations = insights.get("data", [])
        
        # Apply filters if provided
        if priority_filter:
            recommendations = [rec for rec in recommendations if rec.get("priority") == priority_filter]
        
        if type_filter:
            recommendations = [rec for rec in recommendations if rec.get("recommendation_type") == type_filter]
        
        # Calculate summary
        summary = {
            "total_recommendations": len(recommendations),
            "urgent_count": len([rec for rec in recommendations if rec.get("priority") == "urgent"]),
            "high_count": len([rec for rec in recommendations if rec.get("priority") == "high"]),
            "medium_count": len([rec for rec in recommendations if rec.get("priority") == "medium"]),
            "low_count": len([rec for rec in recommendations if rec.get("priority") == "low"]),
            "total_estimated_hours": sum(rec.get("estimated_time_hours", 0) for rec in recommendations)
        }
        
        response = {
            "success": True,
            "student_id": student_id,
            "recommendations": recommendations,
            "summary": summary,
            "generated_at": insights.get("metadata", {}).get("generated_at", datetime.utcnow())
        }
        
        logger.info(f"Recommendations retrieved for student: {student_id}")
        return RecommendationsResponse(**response)
        
    except Exception as e:
        logger.error(f"Failed to get recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recommendations. Please try again later."
        )