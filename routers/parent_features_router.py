"""
Parent Features Router

This router provides API endpoints for all parent-focused features
including AI insights, predictive analytics, communication hub,
gamified engagement, and resource library.

Author: Mentor AI Team
Version: 1.0.0
"""

import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from fastapi.responses import JSONResponse

from services.parent_ai_insights_service import (
    get_parent_ai_insights_service, 
    InsightType, 
    InsightRequest, 
    InsightSeverity
)
from services.predictive_analytics_service import (
    get_predictive_analytics_service,
    PredictionType,
    PredictionRequest,
    RiskLevel
)
from services.communication_hub_service import (
    get_communication_hub_service,
    CommunicationType,
    CommunicationRequest,
    Channel,
    Priority,
    Mood,
    Tone
)
from services.gamified_engagement_service import (
    get_gamified_engagement_service,
    EngagementType,
    EngagementEvent,
    ChallengeType,
    DifficultyLevel
)
from services.parent_resource_library_service import (
    get_parent_resource_library_service,
    ResourceType,
    ResourceCategory,
    ResourceRequest,
    DifficultyLevel as ResourceDifficultyLevel
)
from middleware.auth_middleware import get_current_user
from models.parent_models import (
    ChildDashboard,
    WeeklyReport,
    EmailScheduleRequest,
    NotificationSettings,
    Goal,
    GoalRequest,
    GoalUpdateRequest
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/parent",
    tags=["parent-features"],
    responses={404: {"description": "Resource not found"}}
)

# ============================================================================
# PARENT AI INSIGHTS ENDPOINTS
# ============================================================================

@router.post("/insights/generate", response_model=Dict[str, Any])
async def generate_insight(
    insight_type: str = Query(..., description="Type of insight to generate"),
    student_id: str = Query(..., description="Student ID"),
    time_period_days: int = Query(30, description="Time period in days"),
    include_recommendations: bool = Query(True, description="Include recommendations"),
    severity_threshold: str = Query("medium", description="Severity threshold"),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate AI-powered insight for parent.
    
    Args:
        insight_type: Type of insight (performance, engagement, weak_areas, etc.)
        student_id: Student ID
        time_period_days: Time period for analysis
        include_recommendations: Whether to include recommendations
        severity_threshold: Minimum severity level
        current_user: Authenticated user
    
    Returns:
        Generated insight with recommendations and metadata
    """
    try:
        # Validate insight type
        try:
            insight_enum = InsightType(insight_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid insight type: {insight_type}")
        
        # Validate severity threshold
        try:
            severity_enum = InsightSeverity(severity_threshold)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid severity threshold: {severity_threshold}")
        
        # Get service
        service = get_parent_ai_insights_service()
        
        # Create request
        request = InsightRequest(
            parent_id=current_user["user_id"],
            student_id=student_id,
            insight_type=insight_enum,
            time_period_days=time_period_days,
            include_recommendations=include_recommendations,
            severity_threshold=severity_enum,
            context={"request_source": "api"}
        )
        
        # Generate insight
        result = await service.generate_insight(request)
        
        return {
            "success": True,
            "insight": {
                "insight_id": result.insight_id,
                "insight_type": result.insight_type.value,
                "title": result.title,
                "description": result.description,
                "severity": result.severity.value,
                "data": result.data,
                "recommendations": result.recommendations,
                "action_required": result.action_required,
                "confidence_score": result.confidence_score,
                "generation_time_ms": result.generation_time_ms,
                "created_at": result.created_at.isoformat()
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Insight generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights", response_model=Dict[str, Any])
async def get_insights(
    student_id: Optional[str] = Query(None, description="Filter by student ID"),
    insight_type: Optional[str] = Query(None, description="Filter by insight type"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: int = Query(50, description="Maximum number of insights"),
    start_after: Optional[str] = Query(None, description="Pagination cursor"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get parent insights with filtering and pagination.
    
    Args:
        student_id: Optional student ID filter
        insight_type: Optional insight type filter
        severity: Optional severity filter
        limit: Maximum number of insights to return
        start_after: Pagination cursor
        current_user: Authenticated user
    
    Returns:
        List of insights with pagination support
    """
    try:
        # Parse filters
        insight_type_enum = InsightType(insight_type) if insight_type else None
        severity_enum = InsightSeverity(severity) if severity else None
        
        # Get service
        service = get_parent_ai_insights_service()
        
        # Get insights
        insights = await service.get_insights(
            parent_id=current_user["user_id"],
            student_id=student_id,
            insight_type=insight_type_enum,
            severity=severity_enum,
            limit=limit,
            start_after=start_after
        )
        
        return {
            "success": True,
            "insights": [insight.model_dump() for insight in insights],
            "total_count": len(insights),
            "has_more": len(insights) == limit,
            "next_cursor": insights[-1].insight_id if insights else None
        }
        
    except Exception as e:
        logger.error(f"Get insights failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/insights/conversation-starters", response_model=Dict[str, Any])
async def generate_conversation_starters(
    student_id: str = Query(..., description="Student ID"),
    mood_context: Optional[str] = Query(None, description="Child's mood context"),
    language: str = Query("english", description="Language for starters"),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate AI-powered conversation starters.
    
    Args:
        student_id: Student ID
        mood_context: Optional mood context (stressed, happy, etc.)
        language: Language for conversation starters
        current_user: Authenticated user
    
    Returns:
        List of conversation starter suggestions
    """
    try:
        # Parse mood
        mood_enum = Mood(mood_context) if mood_context else None
        
        # Get service
        service = get_parent_ai_insights_service()
        
        # Generate conversation starters
        starters = await service.generate_conversation_starters(
            parent_id=current_user["user_id"],
            student_id=student_id,
            mood_context=mood_enum,
            language=language
        )
        
        return {
            "success": True,
            "conversation_starters": starters,
            "generated_at": datetime.utcnow().isoformat(),
            "mood_context": mood_context,
            "language": language
        }
        
    except Exception as e:
        logger.error(f"Conversation starters generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/insights/activity-suggestions", response_model=Dict[str, Any])
async def generate_activity_suggestions(
    student_id: str = Query(..., description="Student ID"),
    activity_type: str = Query("educational", description="Type of activity"),
    time_available_minutes: int = Query(30, description="Time available in minutes"),
    subject_focus: Optional[str] = Query(None, description="Subject to focus on"),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate parent-child activity suggestions.
    
    Args:
        student_id: Student ID
        activity_type: Type of activity (educational, recreational, bonding)
        time_available_minutes: Time available in minutes
        subject_focus: Optional subject to focus on
        current_user: Authenticated user
    
    Returns:
        List of activity suggestions with details
    """
    try:
        # Get service
        service = get_parent_ai_insights_service()
        
        # Generate activity suggestions
        suggestions = await service.generate_activity_suggestions(
            parent_id=current_user["user_id"],
            student_id=student_id,
            activity_type=activity_type,
            time_available_minutes=time_available_minutes,
            subject_focus=subject_focus
        )
        
        return {
            "success": True,
            "activity_suggestions": suggestions,
            "generated_at": datetime.utcnow().isoformat(),
            "activity_type": activity_type,
            "time_available_minutes": time_available_minutes,
            "subject_focus": subject_focus
        }
        
    except Exception as e:
        logger.error(f"Activity suggestions generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PREDICTIVE ANALYTICS ENDPOINTS
# ============================================================================

@router.post("/analytics/predict", response_model=Dict[str, Any])
async def generate_prediction(
    prediction_type: str = Query(..., description="Type of prediction"),
    student_id: str = Query(..., description="Student ID"),
    time_period_days: int = Query(30, description="Time period in days"),
    threshold_sensitivity: float = Query(0.7, description="Threshold sensitivity (0-1)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate predictive analytics for early warnings.
    
    Args:
        prediction_type: Type of prediction (performance_trend, engagement_pattern, etc.)
        student_id: Student ID
        time_period_days: Time period for analysis
        threshold_sensitivity: Sensitivity threshold (0-1)
        current_user: Authenticated user
    
    Returns:
        Prediction with risk assessment and recommendations
    """
    try:
        # Validate prediction type
        try:
            prediction_enum = PredictionType(prediction_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid prediction type: {prediction_type}")
        
        # Get service
        service = get_predictive_analytics_service()
        
        # Create request
        request = PredictionRequest(
            student_id=student_id,
            parent_id=current_user["user_id"],
            prediction_type=prediction_enum,
            time_period_days=time_period_days,
            threshold_sensitivity=threshold_sensitivity,
            context={"request_source": "api"}
        )
        
        # Generate prediction
        result = await service.generate_prediction(request)
        
        return {
            "success": True,
            "prediction": {
                "prediction_id": result.prediction_id,
                "prediction_type": result.prediction_type.value,
                "risk_level": result.risk_level.value,
                "confidence_score": result.confidence_score,
                "predictions": result.predictions,
                "risk_factors": result.risk_factors,
                "recommendations": result.recommendations,
                "alerts_triggered": result.alerts_triggered,
                "time_horizon_days": result.time_horizon_days,
                "generation_time_ms": result.generation_time_ms,
                "created_at": result.created_at.isoformat()
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Prediction generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analytics/what-if", response_model=Dict[str, Any])
async def analyze_what_if_scenario(
    student_id: str = Query(..., description="Student ID"),
    scenario: Dict[str, Any] = Body(..., description="What-if scenario parameters"),
    time_horizon_days: int = Query(30, description="Time horizon in days"),
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze what-if scenarios for planning.
    
    Args:
        student_id: Student ID
        scenario: Scenario parameters (increased study time, new subjects, etc.)
        time_horizon_days: Time horizon for prediction
        current_user: Authenticated user
    
    Returns:
        Scenario analysis with predicted outcomes
    """
    try:
        # Get service
        service = get_predictive_analytics_service()
        
        # Analyze scenario
        analysis = await service.analyze_what_if_scenario(
            student_id=student_id,
            parent_id=current_user["user_id"],
            scenario=scenario,
            time_horizon_days=time_horizon_days
        )
        
        return {
            "success": True,
            "scenario_analysis": analysis,
            "analyzed_at": datetime.utcnow().isoformat(),
            "scenario": scenario,
            "time_horizon_days": time_horizon_days
        }
        
    except Exception as e:
        logger.error(f"What-if analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analytics/intervention-recommendations", response_model=Dict[str, Any])
async def get_intervention_recommendations(
    student_id: str = Query(..., description="Student ID"),
    risk_factors: List[str] = Body(..., description="Identified risk factors"),
    current_performance: Dict[str, Any] = Body(..., description="Current performance data"),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate intervention recommendations based on risk factors.
    
    Args:
        student_id: Student ID
        risk_factors: List of identified risk factors
        current_performance: Current performance data
        current_user: Authenticated user
    
    Returns:
        List of intervention recommendations with details
    """
    try:
        # Get service
        service = get_predictive_analytics_service()
        
        # Generate recommendations
        recommendations = await service.get_intervention_recommendations(
            student_id=student_id,
            parent_id=current_user["user_id"],
            risk_factors=risk_factors,
            current_performance=current_performance
        )
        
        return {
            "success": True,
            "intervention_recommendations": recommendations,
            "generated_at": datetime.utcnow().isoformat(),
            "risk_factors": risk_factors
        }
        
    except Exception as e:
        logger.error(f"Intervention recommendations failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# COMMUNICATION HUB ENDPOINTS
# ============================================================================

@router.post("/communication/generate", response_model=Dict[str, Any])
async def generate_communication(
    communication_type: str = Query(..., description="Type of communication"),
    student_id: str = Query(..., description="Student ID"),
    child_mood: Optional[str] = Query(None, description="Child's mood"),
    channel: Optional[str] = Query(None, description="Communication channel"),
    priority: str = Query("medium", description="Message priority"),
    language: str = Query("english", description="Language for communication"),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate AI-powered communication.
    
    Args:
        communication_type: Type of communication (notification, alert, message, etc.)
        student_id: Student ID
        child_mood: Optional child mood (stressed, happy, etc.)
        channel: Optional communication channel
        priority: Message priority (low, medium, high, critical)
        language: Language for communication
        current_user: Authenticated user
    
    Returns:
        Generated communication with optimal tone and timing
    """
    try:
        # Parse enums
        comm_type_enum = CommunicationType(communication_type)
        mood_enum = Mood(child_mood) if child_mood else None
        channel_enum = Channel(channel) if channel else None
        priority_enum = Priority(priority)
        
        # Get service
        service = get_communication_hub_service()
        
        # Create request
        request = CommunicationRequest(
            parent_id=current_user["user_id"],
            student_id=student_id,
            communication_type=comm_type_enum,
            child_mood=mood_enum,
            channel=channel_enum,
            priority=priority_enum,
            language=language,
            context={"request_source": "api"}
        )
        
        # Generate communication
        result = await service.generate_communication(request)
        
        return {
            "success": True,
            "communication": {
                "communication_id": result.communication_id,
                "communication_type": result.communication_type.value,
                "channel": result.channel.value,
                "subject": result.subject,
                "content": result.content,
                "tone": result.tone.value,
                "priority": result.priority.value,
                "suggested_timing": result.suggested_timing.isoformat() if result.suggested_timing else None,
                "follow_up_actions": result.follow_up_actions,
                "effectiveness_score": result.effectiveness_score,
                "generation_time_ms": result.generation_time_ms,
                "created_at": result.created_at.isoformat()
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Communication generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/communication/conversation-starters", response_model=Dict[str, Any])
async def generate_conversation_starters_communication(
    student_id: str = Query(..., description="Student ID"),
    mood_context: Optional[str] = Query(None, description="Child's mood"),
    conversation_goal: Optional[str] = Query(None, description="Goal for conversation"),
    language: str = Query("english", description="Language for starters"),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate AI-powered conversation starters.
    
    Args:
        student_id: Student ID
        mood_context: Optional child mood
        conversation_goal: Optional goal for conversation
        language: Language for conversation starters
        current_user: Authenticated user
    
    Returns:
        List of conversation starter suggestions
    """
    try:
        # Parse mood
        mood_enum = Mood(mood_context) if mood_context else None
        
        # Get service
        service = get_communication_hub_service()
        
        # Generate conversation starters
        starters = await service.generate_conversation_starters(
            parent_id=current_user["user_id"],
            student_id=student_id,
            mood_context=mood_enum,
            conversation_goal=conversation_goal,
            language=language
        )
        
        return {
            "success": True,
            "conversation_starters": starters,
            "generated_at": datetime.utcnow().isoformat(),
            "mood_context": mood_context,
            "conversation_goal": conversation_goal,
            "language": language
        }
        
    except Exception as e:
        logger.error(f"Conversation starters generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/communication/effectiveness", response_model=Dict[str, Any])
async def analyze_communication_effectiveness(
    student_id: str = Query(..., description="Student ID"),
    time_period_days: int = Query(30, description="Period to analyze in days"),
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze communication effectiveness over time.
    
    Args:
        student_id: Student ID
        time_period_days: Period to analyze in days
        current_user: Authenticated user
    
    Returns:
        Communication effectiveness analysis and insights
    """
    try:
        # Get service
        service = get_communication_hub_service()
        
        # Analyze effectiveness
        analysis = await service.analyze_communication_effectiveness(
            parent_id=current_user["user_id"],
            student_id=student_id,
            time_period_days=time_period_days
        )
        
        return {
            "success": True,
            "effectiveness_analysis": analysis,
            "analyzed_at": datetime.utcnow().isoformat(),
            "time_period_days": time_period_days
        }
        
    except Exception as e:
        logger.error(f"Communication effectiveness analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/communication/follow-up-reminders", response_model=Dict[str, Any])
async def schedule_follow_up_reminders(
    communication_id: str = Query(..., description="Communication ID"),
    follow_up_actions: List[str] = Body(..., description="Follow-up actions to schedule"),
    current_user: dict = Depends(get_current_user)
):
    """
    Schedule follow-up reminders for communications.
    
    Args:
        communication_id: Original communication ID
        follow_up_actions: List of follow-up actions
        current_user: Authenticated user
    
    Returns:
        List of scheduled reminders
    """
    try:
        # Extract student ID from communication (would need to look up)
        # For now, we'll use a placeholder
        student_id = "student_from_communication"
        
        # Get service
        service = get_communication_hub_service()
        
        # Schedule reminders
        reminders = await service.schedule_follow_up_reminders(
            communication_id=communication_id,
            follow_up_actions=follow_up_actions,
            parent_id=current_user["user_id"],
            student_id=student_id
        )
        
        return {
            "success": True,
            "follow_up_reminders": reminders,
            "scheduled_at": datetime.utcnow().isoformat(),
            "communication_id": communication_id
        }
        
    except Exception as e:
        logger.error(f"Follow-up reminders scheduling failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# GAMIFIED ENGAGEMENT ENDPOINTS
# ============================================================================

@router.post("/engagement/track", response_model=Dict[str, Any])
async def track_engagement(
    engagement_type: str = Query(..., description="Type of engagement"),
    student_id: str = Query(..., description="Student ID"),
    event_data: Dict[str, Any] = Body(..., description="Event data"),
    current_user: dict = Depends(get_current_user)
):
    """
    Track parent engagement event and award points.
    
    Args:
        engagement_type: Type of engagement (daily_check_in, weekly_challenge, etc.)
        student_id: Student ID
        event_data: Event-specific data
        current_user: Authenticated user
    
    Returns:
        Tracking results with points earned and achievements
    """
    try:
        # Parse engagement type
        engagement_enum = EngagementType(engagement_type)
        
        # Get service
        service = get_gamified_engagement_service()
        
        # Create engagement event
        event = EngagementEvent(
            parent_id=current_user["user_id"],
            student_id=student_id,
            engagement_type=engagement_enum,
            event_data=event_data,
            timestamp=datetime.utcnow(),
            points_earned=0  # Will be calculated by service
        )
        
        # Track engagement
        result = await service.track_engagement(event)
        
        return {
            "success": True,
            "tracking_result": result,
            "tracked_at": datetime.utcnow().isoformat(),
            "engagement_type": engagement_type
        }
        
    except Exception as e:
        logger.error(f"Engagement tracking failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/engagement/weekly-challenge", response_model=Dict[str, Any])
async def generate_weekly_challenge(
    challenge_type: Optional[str] = Query(None, description="Type of weekly challenge"),
    difficulty: str = Query("medium", description="Challenge difficulty"),
    personalized: bool = Query(True, description="Whether to personalize challenge"),
    student_id: str = Query(..., description="Student ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate AI-powered weekly challenge.
    
    Args:
        challenge_type: Optional type of weekly challenge
        difficulty: Challenge difficulty (easy, medium, hard)
        personalized: Whether to personalize based on history
        student_id: Student ID
        current_user: Authenticated user
    
    Returns:
        Generated weekly challenge with requirements and rewards
    """
    try:
        # Parse enums
        challenge_enum = ChallengeType(challenge_type) if challenge_type else None
        difficulty_enum = DifficultyLevel(difficulty)
        
        # Get service
        service = get_gamified_engagement_service()
        
        # Generate challenge
        result = await service.generate_weekly_challenge(
            parent_id=current_user["user_id"],
            student_id=student_id,
            challenge_type=challenge_enum,
            difficulty=difficulty,
            personalized=personalized
        )
        
        return {
            "success": True,
            "weekly_challenge": result["challenge"],
            "generated_at": datetime.utcnow().isoformat(),
            "challenge_type": challenge_type,
            "difficulty": difficulty,
            "personalized": personalized
        }
        
    except Exception as e:
        logger.error(f"Weekly challenge generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/engagement/complete-challenge", response_model=Dict[str, Any])
async def complete_challenge(
    challenge_id: str = Query(..., description="Challenge ID"),
    completion_data: Dict[str, Any] = Body(..., description="Completion details"),
    current_user: dict = Depends(get_current_user)
):
    """
    Mark weekly challenge as completed and award rewards.
    
    Args:
        challenge_id: Challenge ID
        completion_data: Completion details and evidence
        current_user: Authenticated user
    
    Returns:
        Completion results with rewards awarded
    """
    try:
        # Get service
        service = get_gamified_engagement_service()
        
        # Complete challenge
        result = await service.complete_challenge(
            challenge_id=challenge_id,
            parent_id=current_user["user_id"],
            completion_data=completion_data
        )
        
        return {
            "success": True,
            "completion_result": result,
            "completed_at": datetime.utcnow().isoformat(),
            "challenge_id": challenge_id
        }
        
    except Exception as e:
        logger.error(f"Challenge completion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/engagement/leaderboard", response_model=Dict[str, Any])
async def get_leaderboard(
    leaderboard_type: str = Query("weekly", description="Type of leaderboard"),
    limit: int = Query(50, description="Maximum number of results"),
    include_self: bool = Query(True, description="Include requesting parent"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get engagement leaderboard rankings.
    
    Args:
        leaderboard_type: Type of leaderboard (weekly, monthly, all_time)
        limit: Maximum number of results
        include_self: Include requesting parent in results
        current_user: Authenticated user
    
    Returns:
        Leaderboard data with rankings and statistics
    """
    try:
        # Get service
        service = get_gamified_engagement_service()
        
        # Get leaderboard
        result = await service.get_leaderboard(
            leaderboard_type=leaderboard_type,
            limit=limit,
            include_self=include_self,
            parent_id=current_user["user_id"]
        )
        
        return {
            "success": True,
            "leaderboard": result,
            "generated_at": datetime.utcnow().isoformat(),
            "leaderboard_type": leaderboard_type,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Leaderboard generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/engagement/analytics", response_model=Dict[str, Any])
async def get_engagement_analytics(
    student_id: str = Query(None, description="Filter by student ID"),
    time_period_days: int = Query(30, description="Period to analyze in days"),
    include_benchmarks: bool = Query(True, description="Include benchmark comparisons"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get comprehensive engagement analytics for parent.
    
    Args:
        student_id: Optional student ID filter
        time_period_days: Period to analyze in days
        include_benchmarks: Include benchmark comparisons
        current_user: Authenticated user
    
    Returns:
        Engagement analytics with insights and benchmarks
    """
    try:
        # Get service
        service = get_gamified_engagement_service()
        
        # Get analytics
        result = await service.get_engagement_analytics(
            parent_id=current_user["user_id"],
            student_id=student_id or "all_students",
            time_period_days=time_period_days,
            include_benchmarks=include_benchmarks
        )
        
        return {
            "success": True,
            "engagement_analytics": result,
            "analyzed_at": datetime.utcnow().isoformat(),
            "time_period_days": time_period_days,
            "include_benchmarks": include_benchmarks
        }
        
    except Exception as e:
        logger.error(f"Engagement analytics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PARENT RESOURCE LIBRARY ENDPOINTS
# ============================================================================

@router.post("/resources/generate", response_model=Dict[str, Any])
async def generate_resource(
    resource_type: str = Query(..., description="Type of resource"),
    student_id: str = Query(..., description="Student ID"),
    category: Optional[str] = Query(None, description="Resource category"),
    subject: Optional[str] = Query(None, description="Subject focus"),
    difficulty_level: Optional[str] = Query(None, description="Difficulty level"),
    language: str = Query("english", description="Resource language"),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate AI-powered educational resource.
    
    Args:
        resource_type: Type of resource (article, video, exercise, etc.)
        student_id: Student ID
        category: Optional resource category
        subject: Optional subject focus
        difficulty_level: Optional difficulty level
        language: Resource language
        current_user: Authenticated user
    
    Returns:
        Generated resource with quality assessment
    """
    try:
        # Parse enums
        resource_enum = ResourceType(resource_type)
        category_enum = ResourceCategory(category) if category else None
        difficulty_enum = ResourceDifficultyLevel(difficulty_level) if difficulty_level else None
        
        # Get service
        service = get_parent_resource_library_service()
        
        # Create request
        request = ResourceRequest(
            parent_id=current_user["user_id"],
            student_id=student_id,
            request_type="generate",
            resource_type=resource_enum,
            category=category_enum,
            subject=subject,
            difficulty_level=difficulty_enum,
            language=language,
            context={"request_source": "api"}
        )
        
        # Generate resource
        result = await service.generate_resource(request)
        
        return {
            "success": True,
            "resource": result.resources[0].__dict__ if result.resources else {},
            "generated_at": datetime.utcnow().isoformat(),
            "resource_type": resource_type,
            "quality_score": result.resources[0].quality_score.value if result.resources else "average",
            "personalized": result.personalized
        }
        
    except Exception as e:
        logger.error(f"Resource generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resources/search", response_model=Dict[str, Any])
async def search_resources(
    query: str = Query(..., description="Search query"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    difficulty_level: Optional[str] = Query(None, description="Filter by difficulty"),
    language: str = Query("english", description="Resource language"),
    limit: int = Query(10, description="Maximum number of results"),
    current_user: dict = Depends(get_current_user)
):
    """
    Search for educational resources with AI-powered filtering.
    
    Args:
        query: Search query string
        resource_type: Optional resource type filter
        category: Optional resource category filter
        subject: Optional subject filter
        difficulty_level: Optional difficulty level filter
        language: Resource language
        limit: Maximum number of results
        current_user: Authenticated user
    
    Returns:
        Filtered and ranked search results
    """
    try:
        # Parse enums
        resource_enum = ResourceType(resource_type) if resource_type else None
        category_enum = ResourceCategory(category) if category else None
        difficulty_enum = ResourceDifficultyLevel(difficulty_level) if difficulty_level else None
        
        # Get service
        service = get_parent_resource_library_service()
        
        # Create request
        request = ResourceRequest(
            parent_id=current_user["user_id"],
            student_id="search_student",  # Would need actual student ID
            request_type="search",
            query=query,
            resource_type=resource_enum,
            category=category_enum,
            subject=subject,
            difficulty_level=difficulty_enum,
            language=language,
            limit=limit,
            context={"request_source": "api"}
        )
        
        # Search resources
        result = await service.search_resources(request)
        
        return {
            "success": True,
            "search_results": [resource.__dict__ for resource in result.resources],
            "total_found": result.total_found,
            "search_time_ms": result.search_time_ms,
            "quality_filtered": result.quality_filtered,
            "recommendations": result.recommendations,
            "next_steps": result.next_steps,
            "searched_at": datetime.utcnow().isoformat(),
            "query": query
        }
        
    except Exception as e:
        logger.error(f"Resource search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resources/recommend", response_model=Dict[str, Any])
async def recommend_resources(
    student_id: str = Query(..., description="Student ID"),
    context: Optional[Dict[str, Any]] = Body(None, description="Additional context for recommendations"),
    limit: int = Query(10, description="Maximum number of recommendations"),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate personalized resource recommendations.
    
    Args:
        student_id: Student ID
        context: Optional additional context for recommendations
        limit: Maximum number of recommendations
        current_user: Authenticated user
    
    Returns:
        Personalized resource recommendations with insights
    """
    try:
        # Get service
        service = get_parent_resource_library_service()
        
        # Generate recommendations
        result = await service.recommend_resources(
            parent_id=current_user["user_id"],
            student_id=student_id,
            context=context,
            limit=limit
        )
        
        return {
            "success": True,
            "recommendations": [resource.__dict__ for resource in result.resources],
            "total_found": result.total_found,
            "recommendations_insights": result.recommendations,
            "next_steps": result.next_steps,
            "recommended_at": datetime.utcnow().isoformat(),
            "context": context
        }
        
    except Exception as e:
        logger.error(f"Resource recommendations failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resources/rate", response_model=Dict[str, Any])
async def rate_resource(
    resource_id: str = Query(..., description="Resource ID"),
    rating: float = Query(..., description="Rating score (1-5)"),
    feedback: Optional[str] = Body(None, description="Optional feedback text"),
    current_user: dict = Depends(get_current_user)
):
    """
    Rate a resource and update its effectiveness.
    
    Args:
        resource_id: Resource ID to rate
        rating: Rating score (1-5)
        feedback: Optional feedback text
        current_user: Authenticated user
    
    Returns:
        Rating results with updated effectiveness
    """
    try:
        # Validate rating
        if not 1 <= rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Get service
        service = get_parent_resource_library_service()
        
        # Rate resource
        result = await service.rate_resource(
            resource_id=resource_id,
            parent_id=current_user["user_id"],
            rating=rating,
            feedback=feedback
        )
        
        return {
            "success": True,
            "rating_result": result,
            "rated_at": datetime.utcnow().isoformat(),
            "resource_id": resource_id,
            "rating": rating
        }
        
    except Exception as e:
        logger.error(f"Resource rating failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/resources/analytics/{resource_id}", response_model=Dict[str, Any])
async def get_resource_analytics(
    resource_id: str = Path(..., description="Resource ID"),
    time_period_days: int = Query(30, description="Period to analyze in days"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get analytics for a specific resource.
    
    Args:
        resource_id: Resource ID
        time_period_days: Period to analyze in days
        current_user: Authenticated user
    
    Returns:
        Resource analytics with usage patterns and insights
    """
    try:
        # Get service
        service = get_parent_resource_library_service()
        
        # Get analytics
        result = await service.get_resource_analytics(
            resource_id=resource_id,
            time_period_days=time_period_days
        )
        
        return {
            "success": True,
            "resource_analytics": result,
            "analyzed_at": datetime.utcnow().isoformat(),
            "resource_id": resource_id,
            "time_period_days": time_period_days
        }
        
    except Exception as e:
        logger.error(f"Resource analytics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SERVICE METRICS ENDPOINTS
# ============================================================================

@router.get("/metrics/insights", response_model=Dict[str, Any])
async def get_insights_service_metrics(
    current_user: dict = Depends(get_current_user)
):
    """
    Get metrics for Parent AI Insights Service.
    
    Args:
        current_user: Authenticated user
    
    Returns:
        Service metrics and performance data
    """
    try:
        service = get_parent_ai_insights_service()
        metrics = service.get_metrics()
        
        return {
            "success": True,
            "service": "parent_ai_insights",
            "metrics": metrics,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Get insights metrics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/analytics", response_model=Dict[str, Any])
async def get_analytics_service_metrics(
    current_user: dict = Depends(get_current_user)
):
    """
    Get metrics for Predictive Analytics Service.
    
    Args:
        current_user: Authenticated user
    
    Returns:
        Service metrics and performance data
    """
    try:
        service = get_predictive_analytics_service()
        metrics = service.get_metrics()
        
        return {
            "success": True,
            "service": "predictive_analytics",
            "metrics": metrics,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Get analytics metrics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/communication", response_model=Dict[str, Any])
async def get_communication_service_metrics(
    current_user: dict = Depends(get_current_user)
):
    """
    Get metrics for Communication Hub Service.
    
    Args:
        current_user: Authenticated user
    
    Returns:
        Service metrics and performance data
    """
    try:
        service = get_communication_hub_service()
        metrics = service.get_metrics()
        
        return {
            "success": True,
            "service": "communication_hub",
            "metrics": metrics,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Get communication metrics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/engagement", response_model=Dict[str, Any])
async def get_engagement_service_metrics(
    current_user: dict = Depends(get_current_user)
):
    """
    Get metrics for Gamified Engagement Service.
    
    Args:
        current_user: Authenticated user
    
    Returns:
        Service metrics and performance data
    """
    try:
        service = get_gamified_engagement_service()
        metrics = service.get_metrics()
        
        return {
            "success": True,
            "service": "gamified_engagement",
            "metrics": metrics,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Get engagement metrics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/resource-library", response_model=Dict[str, Any])
async def get_resource_library_service_metrics(
    current_user: dict = Depends(get_current_user)
):
    """
    Get metrics for Parent Resource Library Service.
    
    Args:
        current_user: Authenticated user
    
    Returns:
        Service metrics and performance data
    """
    try:
        service = get_parent_resource_library_service()
        metrics = service.get_metrics()
        
        return {
            "success": True,
            "service": "parent_resource_library",
            "metrics": metrics,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Get resource library metrics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    Health check endpoint for parent features service.
    
    Returns:
        Service health status and basic metrics
    """
    try:
        # Check all services
        insights_service = get_parent_ai_insights_service()
        analytics_service = get_predictive_analytics_service()
        communication_service = get_communication_hub_service()
        engagement_service = get_gamified_engagement_service()
        resource_service = get_parent_resource_library_service()
        
        # Get basic metrics from all services
        insights_metrics = insights_service.get_metrics()
        analytics_metrics = analytics_service.get_metrics()
        communication_metrics = communication_service.get_metrics()
        engagement_metrics = engagement_service.get_metrics()
        resource_metrics = resource_service.get_metrics()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "parent_ai_insights": {"status": "healthy", "metrics": insights_metrics},
                "predictive_analytics": {"status": "healthy", "metrics": analytics_metrics},
                "communication_hub": {"status": "healthy", "metrics": communication_metrics},
                "gamified_engagement": {"status": "healthy", "metrics": engagement_metrics},
                "parent_resource_library": {"status": "healthy", "metrics": resource_metrics}
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

# Module initialization
logger.info("Parent Features Router module loaded")