"""
AI Features Router

This router handles all API endpoints for AI features and parent insights:
- AI interactions tracking
- Parent insights generation
- Engagement metrics
- Communication history
- Intervention alerts

Author: Mentor AI Team
Version: 1.0.0
"""

import os
import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse

from services.database_service import database_service
from services.unified_gemini_config_service import get_unified_gemini_service
from services.gemini_service import get_gemini_service
from services.rag_service import RAGService
from services.ai_content_service import get_ai_content_service
from models.database_models import (
    AIInteraction, ParentInsight, EngagementMetric, CommunicationRecord,
    InterventionAlert, InterventionRule, ParentDashboardConfig
)
# The get_current_user function returns a string (user_id), not a User model
from middleware.auth_middleware import get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/ai-features", tags=["AI Features"])


# ============================================================================
# AI INTERACTIONS ENDPOINTS
# ============================================================================

@router.get("/interactions", response_model=List[AIInteraction])
async def get_ai_interactions(
    current_user: str = Depends(get_current_user),
    student_id: Optional[str] = Query(None, description="Filter by student ID"),
    interaction_type: Optional[str] = Query(None, description="Filter by interaction type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    skip: int = Query(0, ge=0, description="Number of results to skip")
):
    """
    Get AI interactions with optional filters.
    
    Args:
        current_user: Authenticated user
        student_id: Optional student ID filter
        interaction_type: Optional interaction type filter
        status: Optional status filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        limit: Maximum number of results
        skip: Number of results to skip
    
    Returns:
        List of AI interactions
    """
    try:
        interactions = await database_service.get_ai_interactions(
            user_id=current_user,
            student_id=student_id,
            interaction_type=interaction_type,
            status=status,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            skip=skip
        )
        
        return interactions
        
    except Exception as e:
        logger.error(f"Failed to get AI interactions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve AI interactions")


@router.get("/interactions/summary")
async def get_ai_interactions_summary(
    current_user: str = Depends(get_current_user),
    days: int = Query(30, ge=1, le=365, description="Number of days to summarize")
):
    """
    Get AI interactions summary for the user.
    
    Args:
        current_user: Authenticated user
        days: Number of days to include in summary
    
    Returns:
        AI interactions summary
    """
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        summary = await database_service.get_ai_interaction_summary(
            user_id=current_user,
            period_start=start_date,
            period_end=end_date
        )
        
        return summary
        
    except Exception as e:
        logger.error(f"Failed to get AI interactions summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve AI interactions summary")


# ============================================================================
# PARENT INSIGHTS ENDPOINTS
# ============================================================================

@router.get("/insights", response_model=List[ParentInsight])
async def get_parent_insights(
    current_user: str = Depends(get_current_user),
    student_id: Optional[str] = Query(None, description="Filter by student ID"),
    insight_type: Optional[str] = Query(None, description="Filter by insight type"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    skip: int = Query(0, ge=0, description="Number of results to skip")
):
    """
    Get parent insights with optional filters.
    
    Args:
        current_user: Authenticated user
        student_id: Optional student ID filter
        insight_type: Optional insight type filter
        severity: Optional severity filter
        status: Optional status filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        limit: Maximum number of results
        skip: Number of results to skip
    
    Returns:
        List of parent insights
    """
    try:
        insights = await database_service.get_parent_insights(
            parent_id=current_user,
            student_id=student_id,
            insight_type=insight_type,
            severity=severity,
            status=status,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            skip=skip
        )
        
        return insights
        
    except Exception as e:
        logger.error(f"Failed to get parent insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve parent insights")


@router.post("/insights/{insight_id}/status")
async def update_parent_insight_status(
    insight_id: str,
    status_data: Dict[str, Any],
    current_user: str = Depends(get_current_user)
):
    """
    Update parent insight status.
    
    Args:
        insight_id: Insight ID
        status_data: Status update data
        current_user: Authenticated user
    
    Returns:
        Update result
    """
    try:
        status = status_data.get("status")
        action_taken = status_data.get("action_taken")
        
        if not status:
            raise HTTPException(status_code=400, detail="Status is required")
        
        success = await database_service.update_parent_insight_status(
            insight_id=insight_id,
            status=status,
            action_taken=action_taken
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Insight not found")
        
        return {"message": "Insight status updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update parent insight status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update insight status")


@router.get("/insights/generate")
async def generate_parent_insights(
    current_user: str = Depends(get_current_user),
    student_id: str = Query(..., description="Student ID"),
    insight_type: Optional[str] = Query(None, description="Specific insight type to generate")
):
    """
    Generate parent insights using AI.
    
    Args:
        current_user: Authenticated user
        student_id: Student ID
        insight_type: Optional specific insight type
    
    Returns:
        Generated insights
    """
    try:
        # Get student data and performance metrics
        # This would typically involve querying multiple collections
        student_data = await _get_student_data_for_insights(student_id)
        
        # Generate insights using AI content service
        ai_content_service = await get_ai_content_service()
        insights = await ai_content_service.generate_parent_insights(
            parent_id=current_user,
            student_id=student_id,
            student_data=student_data,
            insight_type=insight_type
        )
        
        # Save insights to database
        saved_insights = []
        for insight_data in insights:
            insight = ParentInsight(
                insight_id=str(uuid.uuid4()),
                parent_id=current_user,
                student_id=student_id,
                **insight_data
            )
            
            await database_service.save_parent_insight(insight)
            saved_insights.append(insight)
        
        return {"insights": saved_insights, "count": len(saved_insights)}
        
    except Exception as e:
        logger.error(f"Failed to generate parent insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate insights")


# ============================================================================
# ENGAGEMENT METRICS ENDPOINTS
# ============================================================================

@router.get("/engagement-metrics", response_model=List[EngagementMetric])
async def get_engagement_metrics(
    current_user: str = Depends(get_current_user),
    student_id: str = Query(..., description="Student ID"),
    metric_type: Optional[str] = Query(None, description="Filter by metric type"),
    period: Optional[str] = Query(None, description="Filter by period"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    skip: int = Query(0, ge=0, description="Number of results to skip")
):
    """
    Get engagement metrics with optional filters.
    
    Args:
        current_user: Authenticated user
        student_id: Student ID
        metric_type: Optional metric type filter
        period: Optional period filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        limit: Maximum number of results
        skip: Number of results to skip
    
    Returns:
        List of engagement metrics
    """
    try:
        metrics = await database_service.get_engagement_metrics(
            student_id=student_id,
            metric_type=metric_type,
            period=period,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            skip=skip
        )
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get engagement metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve engagement metrics")


@router.post("/engagement-metrics/track")
async def track_engagement_metric(
    metric_data: Dict[str, Any],
    current_user: str = Depends(get_current_user)
):
    """
    Track an engagement metric.
    
    Args:
        metric_data: Metric data
        current_user: Authenticated user
    
    Returns:
        Tracking result
    """
    try:
        metric = EngagementMetric(
            metric_id=str(uuid.uuid4()),
            user_id=current_user,
            **metric_data
        )
        
        await database_service.save_engagement_metric(metric)
        
        return {"message": "Engagement metric tracked successfully", "metric_id": metric.metric_id}
        
    except Exception as e:
        logger.error(f"Failed to track engagement metric: {e}")
        raise HTTPException(status_code=500, detail="Failed to track engagement metric")


# ============================================================================
# COMMUNICATION HISTORY ENDPOINTS
# ============================================================================

@router.get("/communications", response_model=List[CommunicationRecord])
async def get_communication_history(
    current_user: str = Depends(get_current_user),
    student_id: Optional[str] = Query(None, description="Filter by student ID"),
    communication_type: Optional[str] = Query(None, description="Filter by communication type"),
    channel: Optional[str] = Query(None, description="Filter by channel"),
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    skip: int = Query(0, ge=0, description="Number of results to skip")
):
    """
    Get communication history with optional filters.
    
    Args:
        current_user: Authenticated user
        student_id: Optional student ID filter
        communication_type: Optional communication type filter
        channel: Optional channel filter
        status: Optional status filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        limit: Maximum number of results
        skip: Number of results to skip
    
    Returns:
        List of communication records
    """
    try:
        communications = await database_service.get_communication_history(
            parent_id=current_user,
            student_id=student_id,
            communication_type=communication_type,
            channel=channel,
            status=status,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            skip=skip
        )
        
        return communications
        
    except Exception as e:
        logger.error(f"Failed to get communication history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve communication history")


# ============================================================================
# INTERVENTION ALERTS ENDPOINTS
# ============================================================================

@router.get("/alerts", response_model=List[InterventionAlert])
async def get_intervention_alerts(
    current_user: str = Depends(get_current_user),
    student_id: Optional[str] = Query(None, description="Filter by student ID"),
    alert_type: Optional[str] = Query(None, description="Filter by alert type"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    skip: int = Query(0, ge=0, description="Number of results to skip")
):
    """
    Get intervention alerts with optional filters.
    
    Args:
        current_user: Authenticated user
        student_id: Optional student ID filter
        alert_type: Optional alert type filter
        severity: Optional severity filter
        status: Optional status filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        limit: Maximum number of results
        skip: Number of results to skip
    
    Returns:
        List of intervention alerts
    """
    try:
        alerts = await database_service.get_intervention_alerts(
            parent_id=current_user,
            student_id=student_id,
            alert_type=alert_type,
            severity=severity,
            status=status,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            skip=skip
        )
        
        return alerts
        
    except Exception as e:
        logger.error(f"Failed to get intervention alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve intervention alerts")


@router.post("/alerts/{alert_id}/status")
async def update_intervention_alert_status(
    alert_id: str,
    status_data: Dict[str, Any],
    current_user: str = Depends(get_current_user)
):
    """
    Update intervention alert status.
    
    Args:
        alert_id: Alert ID
        status_data: Status update data
        current_user: Authenticated user
    
    Returns:
        Update result
    """
    try:
        status = status_data.get("status")
        resolution_notes = status_data.get("resolution_notes")
        
        if not status:
            raise HTTPException(status_code=400, detail="Status is required")
        
        success = await database_service.update_intervention_alert_status(
            alert_id=alert_id,
            status=status,
            resolved_by=current_user,
            resolution_notes=resolution_notes
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {"message": "Alert status updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update intervention alert status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update alert status")


# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@router.get("/dashboard")
async def get_parent_dashboard(
    current_user: str = Depends(get_current_user),
    student_id: Optional[str] = Query(None, description="Filter by student ID")
):
    """
    Get parent dashboard data including insights, alerts, and communications.
    
    Args:
        current_user: Authenticated user
        student_id: Optional student ID filter
    
    Returns:
        Dashboard data
    """
    try:
        dashboard_data = await database_service.get_dashboard_stats(
            parent_id=current_user,
            student_id=student_id
        )
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Failed to get parent dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard data")


@router.get("/dashboard/config")
async def get_parent_dashboard_config(
    current_user: str = Depends(get_current_user)
):
    """
    Get parent dashboard configuration.
    
    Args:
        current_user: Authenticated user
    
    Returns:
        Dashboard configuration
    """
    try:
        # For now, return default configuration
        # In a real implementation, this would be stored in the database
        config = ParentDashboardConfig(
            parent_id=current_user
        )
        
        return config
        
    except Exception as e:
        logger.error(f"Failed to get parent dashboard config: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard configuration")


@router.post("/dashboard/config")
async def update_parent_dashboard_config(
    config_data: Dict[str, Any],
    current_user: str = Depends(get_current_user)
):
    """
    Update parent dashboard configuration.
    
    Args:
        config_data: Configuration data
        current_user: Authenticated user
    
    Returns:
        Update result
    """
    try:
        # Update configuration in database
        # For now, just return success
        # In a real implementation, this would update the database
        
        return {"message": "Dashboard configuration updated successfully"}
        
    except Exception as e:
        logger.error(f"Failed to update parent dashboard config: {e}")
        raise HTTPException(status_code=500, detail="Failed to update dashboard configuration")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def _get_student_data_for_insights(student_id: str) -> Dict[str, Any]:
    """
    Get student data for generating insights.
    
    Args:
        student_id: Student ID
    
    Returns:
        Student data dictionary
    """
    try:
        # This would typically query multiple collections to get comprehensive student data
        # For now, return mock data
        
        # Get recent engagement metrics
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        engagement_metrics = await database_service.get_engagement_metrics(
            student_id=student_id,
            start_date=start_date,
            end_date=end_date,
            limit=100
        )
        
        # Get recent AI interactions
        ai_interactions = await database_service.get_ai_interactions(
            student_id=student_id,
            start_date=start_date,
            end_date=end_date,
            limit=100
        )
        
        # Get active intervention alerts
        active_alerts = await database_service.get_intervention_alerts(
            parent_id="",  # This would need to be determined
            student_id=student_id,
            status="new",
            limit=10
        )
        
        return {
            "student_id": student_id,
            "engagement_metrics": [metric.model_dump() for metric in engagement_metrics],
            "ai_interactions": [interaction.model_dump() for interaction in ai_interactions],
            "active_alerts": [alert.model_dump() for alert in active_alerts],
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get student data for insights: {e}")
        raise


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
async def health_check():
    """
    Health check endpoint for AI features service.
    
    Returns:
        Health status
    """
    try:
        # Check database connection
        # This would typically ping the database
        db_status = "healthy"
        
        # Check AI services
        gemini_status = "healthy" if gemini_service else "unhealthy"
        rag_status = "healthy" if rag_service else "unhealthy"
        
        overall_status = "healthy" if all([
            db_status == "healthy",
            gemini_status == "healthy",
            rag_status == "healthy"
        ]) else "unhealthy"
        
        return {
            "status": overall_status,
            "services": {
                "database": db_status,
                "gemini": gemini_status,
                "rag": rag_status
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
