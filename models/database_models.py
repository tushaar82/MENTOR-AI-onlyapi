"""
Database Models for AI Interactions and Parent Features

This module defines Pydantic models for database collections related to
AI interactions, parent insights, engagement metrics, communication history,
and intervention alerts.

Author: Mentor AI Team
Version: 1.0.0
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field


# ============================================================================
# AI INTERACTIONS MODELS
# ============================================================================

class AIInteraction(BaseModel):
    """Model for AI interaction records."""
    
    interaction_id: str = Field(..., description="Unique interaction identifier")
    user_id: str = Field(..., description="User who initiated interaction")
    student_id: Optional[str] = Field(None, description="Student ID if applicable")
    interaction_type: str = Field(..., description="Type of interaction")
    request_data: Dict[str, Any] = Field(..., description="Request parameters and context")
    response_data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    status: str = Field(..., description="Status (pending, completed, failed)")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    tokens_used: Dict[str, int] = Field(default_factory=dict, description="Token usage breakdown")
    cost: float = Field(0.0, description="Cost of this interaction")
    response_time_ms: int = Field(0, description="Response time in milliseconds")
    cached: bool = Field(False, description="Whether result was from cache")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class AIInteractionSummary(BaseModel):
    """Summary of AI interactions for analytics."""
    
    user_id: str = Field(..., description="User ID")
    period_start: datetime = Field(..., description="Period start date")
    period_end: datetime = Field(..., description="Period end date")
    total_interactions: int = Field(..., description="Total interactions")
    successful_interactions: int = Field(..., description="Successful interactions")
    failed_interactions: int = Field(..., description="Failed interactions")
    total_cost: float = Field(..., description="Total cost")
    total_tokens: int = Field(..., description="Total tokens used")
    average_response_time_ms: float = Field(..., description="Average response time")
    interaction_types: Dict[str, int] = Field(default_factory=dict, description="Count by interaction type")
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# PARENT INSIGHTS MODELS
# ============================================================================

class ParentInsight(BaseModel):
    """Model for parent insights."""
    
    insight_id: str = Field(..., description="Unique insight identifier")
    parent_id: str = Field(..., description="Parent ID")
    student_id: str = Field(..., description="Student ID")
    insight_type: Literal["performance", "engagement", "weak_areas", "progress", "recommendation"] = Field(..., description="Type of insight")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Detailed description")
    severity: Literal["low", "medium", "high", "critical"] = Field(..., description="Insight severity")
    data: Dict[str, Any] = Field(..., description="Insight data")
    action_required: bool = Field(False, description="Whether action is required")
    action_taken: Optional[str] = Field(None, description="Action taken if any")
    status: Literal["new", "acknowledged", "in_progress", "resolved"] = Field(..., description="Insight status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class ParentDashboardConfig(BaseModel):
    """Configuration for parent dashboard."""
    
    parent_id: str = Field(..., description="Parent ID")
    notification_preferences: Dict[str, bool] = Field(
        default_factory=lambda: {
            "email": True,
            "push": True,
            "weekly_reports": True,
            "critical_alerts": True,
            "progress_updates": True
        },
        description="Notification preferences"
    )
    insight_preferences: Dict[str, bool] = Field(
        default_factory=lambda: {
            "performance_trends": True,
            "engagement_metrics": True,
            "weak_areas": True,
            "recommendations": True,
            "progress_tracking": True
        },
        description="Insight preferences"
    )
    privacy_settings: Dict[str, bool] = Field(
        default_factory=lambda: {
            "share_performance": True,
            "share_engagement": True,
            "share_weak_areas": True,
            "allow_data_export": True
        },
        description="Privacy settings"
    )
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# ENGAGEMENT METRICS MODELS
# ============================================================================

class EngagementMetric(BaseModel):
    """Model for engagement metrics."""
    
    metric_id: str = Field(..., description="Unique metric identifier")
    user_id: str = Field(..., description="User ID")
    student_id: str = Field(..., description="Student ID")
    metric_type: Literal["study_time", "question_attempts", "test_performance", "content_interaction", "goal_completion"] = Field(..., description="Type of metric")
    metric_name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    unit: str = Field(..., description="Unit of measurement")
    period: Literal["daily", "weekly", "monthly"] = Field(..., description="Period type")
    date: datetime = Field(..., description="Metric date")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class EngagementSummary(BaseModel):
    """Summary of engagement metrics."""
    
    user_id: str = Field(..., description="User ID")
    student_id: str = Field(..., description="Student ID")
    period_start: datetime = Field(..., description="Period start date")
    period_end: datetime = Field(..., description="Period end date")
    metrics: Dict[str, List[EngagementMetric]] = Field(..., description="Metrics by type")
    trends: Dict[str, Any] = Field(..., description="Trend analysis")
    insights: List[str] = Field(..., description="Generated insights")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class StudySession(BaseModel):
    """Model for study sessions."""
    
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User ID")
    student_id: str = Field(..., description="Student ID")
    start_time: datetime = Field(..., description="Session start time")
    end_time: Optional[datetime] = Field(None, description="Session end time")
    duration_minutes: Optional[int] = Field(None, description="Duration in minutes")
    topics_studied: List[str] = Field(default_factory=list, description="Topics studied")
    questions_attempted: int = Field(0, description="Questions attempted")
    questions_correct: int = Field(0, description="Questions correct")
    content_interactions: int = Field(0, description="Content interactions")
    goals_completed: List[str] = Field(default_factory=list, description="Goals completed")
    quality_score: float = Field(0.0, description="Session quality score")
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# COMMUNICATION HISTORY MODELS
# ============================================================================

class CommunicationRecord(BaseModel):
    """Model for communication records."""
    
    communication_id: str = Field(..., description="Unique communication identifier")
    parent_id: str = Field(..., description="Parent ID")
    student_id: Optional[str] = Field(None, description="Student ID")
    communication_type: Literal["notification", "alert", "insight", "report", "message"] = Field(..., description="Type of communication")
    channel: Literal["email", "push", "in_app", "sms"] = Field(..., description="Communication channel")
    direction: Literal["sent", "received"] = Field(..., description="Communication direction")
    subject: str = Field(..., description="Communication subject")
    content: str = Field(..., description="Communication content")
    priority: Literal["low", "medium", "high", "critical"] = Field(..., description="Communication priority")
    status: Literal["pending", "sent", "delivered", "failed", "read"] = Field(..., description="Communication status")
    sent_at: Optional[datetime] = Field(None, description="Send timestamp")
    delivered_at: Optional[datetime] = Field(None, description="Delivery timestamp")
    read_at: Optional[datetime] = Field(None, description="Read timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CommunicationTemplate(BaseModel):
    """Model for communication templates."""
    
    template_id: str = Field(..., description="Unique template identifier")
    template_name: str = Field(..., description="Template name")
    template_type: Literal["notification", "alert", "report", "message"] = Field(..., description="Template type")
    subject: str = Field(..., description="Template subject")
    content_template: str = Field(..., description="Content template with placeholders")
    variables: List[str] = Field(default_factory=list, description="Template variables")
    default_channel: Literal["email", "push", "in_app"] = Field(..., description="Default channel")
    default_priority: Literal["low", "medium", "high"] = Field(..., description="Default priority")
    active: bool = Field(True, description="Whether template is active")
    created_by: str = Field(..., description="Creator user ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")


# ============================================================================
# INTERVENTION ALERTS MODELS
# ============================================================================

class InterventionAlert(BaseModel):
    """Model for intervention alerts."""
    
    alert_id: str = Field(..., description="Unique alert identifier")
    parent_id: str = Field(..., description="Parent ID")
    student_id: str = Field(..., description="Student ID")
    alert_type: Literal["performance_drop", "low_engagement", "missed_goals", "weak_performance", "critical_issue"] = Field(..., description="Type of alert")
    severity: Literal["low", "medium", "high", "critical"] = Field(..., description="Alert severity")
    title: str = Field(..., description="Alert title")
    description: str = Field(..., description="Alert description")
    data: Dict[str, Any] = Field(..., description="Alert data and metrics")
    threshold_triggered: bool = Field(False, description="Whether threshold was triggered")
    threshold_value: Optional[float] = Field(None, description="Threshold value that was triggered")
    current_value: Optional[float] = Field(None, description="Current value that triggered alert")
    recommended_actions: List[str] = Field(default_factory=list, description="Recommended actions")
    status: Literal["new", "acknowledged", "in_progress", "resolved"] = Field(..., description="Alert status")
    acknowledged_at: Optional[datetime] = Field(None, description="Acknowledgment timestamp")
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")
    resolved_by: Optional[str] = Field(None, description="Who resolved the alert")
    resolution_notes: Optional[str] = Field(None, description="Resolution notes")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class InterventionRule(BaseModel):
    """Model for intervention alert rules."""
    
    rule_id: str = Field(..., description="Unique rule identifier")
    parent_id: str = Field(..., description="Parent ID")
    student_id: Optional[str] = Field(None, description="Student ID if specific, None for global")
    rule_name: str = Field(..., description="Rule name")
    alert_type: Literal["performance_drop", "low_engagement", "missed_goals", "weak_performance", "critical_issue"] = Field(..., description="Alert type")
    metric_type: Literal["study_time", "question_attempts", "test_performance", "content_interaction", "goal_completion"] = Field(..., description="Metric type to monitor")
    condition: Literal["less_than", "greater_than", "equals", "not_equals", "trend_down", "no_activity"] = Field(..., description="Trigger condition")
    threshold_value: float = Field(..., description="Threshold value")
    time_window_hours: int = Field(24, description="Time window in hours")
    consecutive_occurrences: int = Field(1, description="Consecutive occurrences required")
    active: bool = Field(True, description="Whether rule is active")
    notification_channels: List[Literal["email", "push", "in_app", "sms"]] = Field(default_factory=lambda: ["email", "push"], description="Notification channels")
    cooldown_hours: int = Field(24, description="Cooldown period in hours")
    created_by: str = Field(..., description="Creator user ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")


# ============================================================================
# DATABASE SCHEMA MODELS
# ============================================================================

class DatabaseSchema(BaseModel):
    """Database schema definition for collections."""
    
    collection_name: str = Field(..., description="Collection name")
    description: str = Field(..., description="Collection description")
    fields: Dict[str, Dict[str, Any]] = Field(..., description="Field definitions")
    indexes: List[Dict[str, Any]] = Field(default_factory=list, description="Index definitions")
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Database schema definitions
AI_INTERACTIONS_SCHEMA = DatabaseSchema(
    collection_name="ai_interactions",
    description="All AI interactions with full tracking",
    fields={
        "interaction_id": {"type": "string", "required": True, "description": "Unique identifier"},
        "user_id": {"type": "string", "required": True, "description": "User who initiated"},
        "student_id": {"type": "string", "required": False, "description": "Student ID if applicable"},
        "interaction_type": {"type": "string", "required": True, "description": "Type of interaction"},
        "request_data": {"type": "map", "required": True, "description": "Request parameters"},
        "response_data": {"type": "map", "required": False, "description": "Response data"},
        "status": {"type": "string", "required": True, "description": "Processing status"},
        "error_message": {"type": "string", "required": False, "description": "Error if failed"},
        "tokens_used": {"type": "map", "required": True, "description": "Token usage"},
        "cost": {"type": "float", "required": True, "description": "Cost in USD"},
        "response_time_ms": {"type": "integer", "required": True, "description": "Response time"},
        "cached": {"type": "boolean", "required": True, "description": "From cache"},
        "created_at": {"type": "timestamp", "required": True, "description": "Creation time"},
        "completed_at": {"type": "timestamp", "required": False, "description": "Completion time"},
        "metadata": {"type": "map", "required": True, "description": "Additional metadata"}
    },
    indexes=[
        {"fields": ["user_id", "created_at"], "name": "user_interactions_by_time"},
        {"fields": ["student_id", "created_at"], "name": "student_interactions_by_time"},
        {"fields": ["interaction_type", "created_at"], "name": "interactions_by_type"},
        {"fields": ["status", "created_at"], "name": "interactions_by_status"}
    ]
)

PARENT_INSIGHTS_SCHEMA = DatabaseSchema(
    collection_name="parent_insights",
    description="Parent insights and recommendations",
    fields={
        "insight_id": {"type": "string", "required": True, "description": "Unique identifier"},
        "parent_id": {"type": "string", "required": True, "description": "Parent ID"},
        "student_id": {"type": "string", "required": True, "description": "Student ID"},
        "insight_type": {"type": "string", "required": True, "description": "Type of insight"},
        "title": {"type": "string", "required": True, "description": "Insight title"},
        "description": {"type": "string", "required": True, "description": "Detailed description"},
        "severity": {"type": "string", "required": True, "description": "Insight severity"},
        "data": {"type": "map", "required": True, "description": "Insight data"},
        "action_required": {"type": "boolean", "required": True, "description": "Action needed"},
        "action_taken": {"type": "string", "required": False, "description": "Action taken"},
        "status": {"type": "string", "required": True, "description": "Insight status"},
        "created_at": {"type": "timestamp", "required": True, "description": "Creation time"},
        "resolved_at": {"type": "timestamp", "required": False, "description": "Resolution time"},
        "metadata": {"type": "map", "required": True, "description": "Additional metadata"}
    },
    indexes=[
        {"fields": ["parent_id", "created_at"], "name": "parent_insights_by_time"},
        {"fields": ["student_id", "created_at"], "name": "student_insights_by_time"},
        {"fields": ["insight_type", "created_at"], "name": "insights_by_type"},
        {"fields": ["severity", "created_at"], "name": "insights_by_severity"},
        {"fields": ["status", "created_at"], "name": "insights_by_status"}
    ]
)

ENGAGEMENT_METRICS_SCHEMA = DatabaseSchema(
    collection_name="engagement_metrics",
    description="Student engagement and activity metrics",
    fields={
        "metric_id": {"type": "string", "required": True, "description": "Unique identifier"},
        "user_id": {"type": "string", "required": True, "description": "User ID"},
        "student_id": {"type": "string", "required": True, "description": "Student ID"},
        "metric_type": {"type": "string", "required": True, "description": "Type of metric"},
        "metric_name": {"type": "string", "required": True, "description": "Metric name"},
        "value": {"type": "float", "required": True, "description": "Metric value"},
        "unit": {"type": "string", "required": True, "description": "Unit of measurement"},
        "period": {"type": "string", "required": True, "description": "Period type"},
        "date": {"type": "timestamp", "required": True, "description": "Metric date"},
        "context": {"type": "map", "required": True, "description": "Additional context"},
        "created_at": {"type": "timestamp", "required": True, "description": "Creation time"}
    },
    indexes=[
        {"fields": ["student_id", "date"], "name": "student_metrics_by_date"},
        {"fields": ["metric_type", "date"], "name": "metrics_by_type_date"},
        {"fields": ["user_id", "date"], "name": "user_metrics_by_date"}
    ]
)

COMMUNICATION_HISTORY_SCHEMA = DatabaseSchema(
    collection_name="communication_history",
    description="All communications with parents and students",
    fields={
        "communication_id": {"type": "string", "required": True, "description": "Unique identifier"},
        "parent_id": {"type": "string", "required": True, "description": "Parent ID"},
        "student_id": {"type": "string", "required": False, "description": "Student ID"},
        "communication_type": {"type": "string", "required": True, "description": "Type of communication"},
        "channel": {"type": "string", "required": True, "description": "Communication channel"},
        "direction": {"type": "string", "required": True, "description": "Direction"},
        "subject": {"type": "string", "required": True, "description": "Subject"},
        "content": {"type": "string", "required": True, "description": "Content"},
        "priority": {"type": "string", "required": True, "description": "Priority"},
        "status": {"type": "string", "required": True, "description": "Status"},
        "sent_at": {"type": "timestamp", "required": False, "description": "Send time"},
        "delivered_at": {"type": "timestamp", "required": False, "description": "Delivery time"},
        "read_at": {"type": "timestamp", "required": False, "description": "Read time"},
        "metadata": {"type": "map", "required": True, "description": "Additional metadata"},
        "created_at": {"type": "timestamp", "required": True, "description": "Creation time"}
    },
    indexes=[
        {"fields": ["parent_id", "created_at"], "name": "parent_communications_by_time"},
        {"fields": ["student_id", "created_at"], "name": "student_communications_by_time"},
        {"fields": ["communication_type", "created_at"], "name": "communications_by_type"},
        {"fields": ["status", "created_at"], "name": "communications_by_status"}
    ]
)

INTERVENTION_ALERTS_SCHEMA = DatabaseSchema(
    collection_name="intervention_alerts",
    description="Alerts for parent intervention needs",
    fields={
        "alert_id": {"type": "string", "required": True, "description": "Unique identifier"},
        "parent_id": {"type": "string", "required": True, "description": "Parent ID"},
        "student_id": {"type": "string", "required": True, "description": "Student ID"},
        "alert_type": {"type": "string", "required": True, "description": "Type of alert"},
        "severity": {"type": "string", "required": True, "description": "Alert severity"},
        "title": {"type": "string", "required": True, "description": "Alert title"},
        "description": {"type": "string", "required": True, "description": "Alert description"},
        "data": {"type": "map", "required": True, "description": "Alert data"},
        "threshold_triggered": {"type": "boolean", "required": True, "description": "Threshold triggered"},
        "threshold_value": {"type": "float", "required": False, "description": "Threshold value"},
        "current_value": {"type": "float", "required": False, "description": "Current value"},
        "recommended_actions": {"type": "array", "required": True, "description": "Recommended actions"},
        "status": {"type": "string", "required": True, "description": "Alert status"},
        "acknowledged_at": {"type": "timestamp", "required": False, "description": "Acknowledgment time"},
        "resolved_at": {"type": "timestamp", "required": False, "description": "Resolution time"},
        "resolved_by": {"type": "string", "required": False, "description": "Resolver"},
        "resolution_notes": {"type": "string", "required": False, "description": "Resolution notes"},
        "created_at": {"type": "timestamp", "required": True, "description": "Creation time"},
        "metadata": {"type": "map", "required": True, "description": "Additional metadata"}
    },
    indexes=[
        {"fields": ["parent_id", "created_at"], "name": "parent_alerts_by_time"},
        {"fields": ["student_id", "created_at"], "name": "student_alerts_by_time"},
        {"fields": ["alert_type", "created_at"], "name": "alerts_by_type"},
        {"fields": ["severity", "created_at"], "name": "alerts_by_severity"},
        {"fields": ["status", "created_at"], "name": "alerts_by_status"}
    ]
)

# ============================================================================
# PHASE 2 PARENT AI FEATURES MODELS
# ============================================================================

class PredictionResult(BaseModel):
    """Model for predictive analytics results."""
    
    prediction_id: str = Field(..., description="Unique prediction identifier")
    parent_id: str = Field(..., description="Parent ID")
    student_id: str = Field(..., description="Student ID")
    prediction_type: Literal["performance_trend", "risk_assessment", "intervention_need", "engagement_forecast"] = Field(..., description="Type of prediction")
    confidence_score: float = Field(..., description="Confidence score (0-1)")
    prediction_data: Dict[str, Any] = Field(..., description="Prediction data and insights")
    risk_factors: List[str] = Field(default_factory=list, description="Identified risk factors")
    recommended_actions: List[str] = Field(default_factory=list, description="Recommended actions")
    time_horizon_days: int = Field(..., description="Prediction time horizon in days")
    model_version: str = Field(..., description="AI model version used")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Prediction expiry time")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class CommunicationSuggestion(BaseModel):
    """Model for AI-powered communication suggestions."""
    
    suggestion_id: str = Field(..., description="Unique suggestion identifier")
    parent_id: str = Field(..., description="Parent ID")
    student_id: str = Field(..., description="Student ID")
    communication_type: Literal["conversation_starter", "encouragement", "concern", "goal_discussion", "progress_review"] = Field(..., description="Type of communication")
    suggested_content: str = Field(..., description="Suggested communication content")
    tone: Literal["supportive", "encouraging", "concerned", "neutral", "celebratory"] = Field(..., description="Recommended tone")
    context: Dict[str, Any] = Field(..., description="Context for the suggestion")
    timing_suggestion: Optional[str] = Field(None, description="When to have this conversation")
    follow_up_suggestions: List[str] = Field(default_factory=list, description="Follow-up suggestions")
    effectiveness_score: Optional[float] = Field(None, description="Effectiveness score if used")
    used: bool = Field(False, description="Whether suggestion was used")
    feedback: Optional[str] = Field(None, description="User feedback on suggestion")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    used_at: Optional[datetime] = Field(None, description="When suggestion was used")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class EngagementChallenge(BaseModel):
    """Model for gamified engagement challenges."""
    
    challenge_id: str = Field(..., description="Unique challenge identifier")
    parent_id: str = Field(..., description="Parent ID")
    student_id: str = Field(..., description="Student ID")
    challenge_type: Literal["weekly_goal", "study_streak", "topic_mastery", "practice_consistency", "engagement_boost"] = Field(..., description="Type of challenge")
    title: str = Field(..., description="Challenge title")
    description: str = Field(..., description="Challenge description")
    difficulty_level: Literal["easy", "medium", "hard", "expert"] = Field(..., description="Difficulty level")
    target_metrics: Dict[str, Any] = Field(..., description="Target metrics to achieve")
    current_progress: Dict[str, Any] = Field(default_factory=dict, description="Current progress")
    points_awarded: int = Field(0, description="Points awarded for completion")
    bonus_points: int = Field(0, description="Bonus points available")
    start_date: datetime = Field(..., description="Challenge start date")
    end_date: datetime = Field(..., description="Challenge end date")
    status: Literal["active", "completed", "failed", "expired"] = Field(..., description="Challenge status")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class Achievement(BaseModel):
    """Model for parent and student achievements."""
    
    achievement_id: str = Field(..., description="Unique achievement identifier")
    parent_id: str = Field(..., description="Parent ID")
    student_id: str = Field(..., description="Student ID")
    achievement_type: Literal["milestone", "streak", "improvement", "engagement", "mastery"] = Field(..., description="Type of achievement")
    title: str = Field(..., description="Achievement title")
    description: str = Field(..., description="Achievement description")
    badge_icon: str = Field(..., description="Badge icon identifier")
    points_awarded: int = Field(..., description="Points awarded")
    rarity: Literal["common", "rare", "epic", "legendary"] = Field(..., description="Achievement rarity")
    criteria_met: Dict[str, Any] = Field(..., description="Criteria that were met")
    earned_at: datetime = Field(..., description="When achievement was earned")
    shared: bool = Field(False, description="Whether achievement was shared")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class ParentResource(BaseModel):
    """Model for parent resources with AI curation."""
    
    resource_id: str = Field(..., description="Unique resource identifier")
    title: str = Field(..., description="Resource title")
    description: str = Field(..., description="Resource description")
    resource_type: Literal["article", "video", "guide", "template", "tool", "course"] = Field(..., description="Type of resource")
    category: Literal["academic_support", "parenting_tips", "communication", "motivation", "exam_prep", "career_guidance"] = Field(..., description="Resource category")
    content: str = Field(..., description="Resource content or URL")
    age_appropriate: List[str] = Field(default_factory=list, description="Age groups this is appropriate for")
    difficulty_level: Literal["beginner", "intermediate", "advanced"] = Field(..., description="Difficulty level")
    language: str = Field(default="en", description="Resource language")
    tags: List[str] = Field(default_factory=list, description="Resource tags")
    quality_score: float = Field(..., description="AI-assessed quality score (0-1)")
    effectiveness_rating: Optional[float] = Field(None, description="User effectiveness rating")
    usage_count: int = Field(0, description="Number of times used")
    download_count: int = Field(0, description="Number of times downloaded")
    author: Optional[str] = Field(None, description="Resource author")
    source: Optional[str] = Field(None, description="Resource source")
    curated_by_ai: bool = Field(True, description="Whether curated by AI")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class ResourceUsage(BaseModel):
    """Model for tracking resource usage and effectiveness."""
    
    usage_id: str = Field(..., description="Unique usage identifier")
    parent_id: str = Field(..., description="Parent ID")
    student_id: Optional[str] = Field(None, description="Student ID if applicable")
    resource_id: str = Field(..., description="Resource ID")
    usage_type: Literal["viewed", "downloaded", "bookmarked", "shared", "rated"] = Field(..., description="Type of usage")
    effectiveness_rating: Optional[float] = Field(None, description="User effectiveness rating (1-5)")
    feedback: Optional[str] = Field(None, description="User feedback")
    outcome: Optional[str] = Field(None, description="Outcome after using resource")
    time_spent_minutes: Optional[int] = Field(None, description="Time spent with resource")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


# ============================================================================
# PHASE 2 DATABASE SCHEMA MODELS
# ============================================================================

PREDICTION_RESULTS_SCHEMA = DatabaseSchema(
    collection_name="prediction_results",
    description="Predictive analytics results for early warnings",
    fields={
        "prediction_id": {"type": "string", "required": True, "description": "Unique identifier"},
        "parent_id": {"type": "string", "required": True, "description": "Parent ID"},
        "student_id": {"type": "string", "required": True, "description": "Student ID"},
        "prediction_type": {"type": "string", "required": True, "description": "Type of prediction"},
        "confidence_score": {"type": "float", "required": True, "description": "Confidence score"},
        "prediction_data": {"type": "map", "required": True, "description": "Prediction data"},
        "risk_factors": {"type": "array", "required": True, "description": "Risk factors"},
        "recommended_actions": {"type": "array", "required": True, "description": "Recommended actions"},
        "time_horizon_days": {"type": "integer", "required": True, "description": "Time horizon"},
        "model_version": {"type": "string", "required": True, "description": "Model version"},
        "created_at": {"type": "timestamp", "required": True, "description": "Creation time"},
        "expires_at": {"type": "timestamp", "required": False, "description": "Expiry time"}
    },
    indexes=[
        {"fields": ["parent_id", "created_at"], "name": "parent_predictions_by_time"},
        {"fields": ["student_id", "created_at"], "name": "student_predictions_by_time"},
        {"fields": ["prediction_type", "created_at"], "name": "predictions_by_type"},
        {"fields": ["confidence_score", "created_at"], "name": "predictions_by_confidence"}
    ]
)

COMMUNICATION_SUGGESTIONS_SCHEMA = DatabaseSchema(
    collection_name="communication_suggestions",
    description="AI-powered communication suggestions",
    fields={
        "suggestion_id": {"type": "string", "required": True, "description": "Unique identifier"},
        "parent_id": {"type": "string", "required": True, "description": "Parent ID"},
        "student_id": {"type": "string", "required": True, "description": "Student ID"},
        "communication_type": {"type": "string", "required": True, "description": "Type of communication"},
        "suggested_content": {"type": "string", "required": True, "description": "Suggested content"},
        "tone": {"type": "string", "required": True, "description": "Recommended tone"},
        "context": {"type": "map", "required": True, "description": "Context"},
        "timing_suggestion": {"type": "string", "required": False, "description": "Timing suggestion"},
        "follow_up_suggestions": {"type": "array", "required": True, "description": "Follow-up suggestions"},
        "effectiveness_score": {"type": "float", "required": False, "description": "Effectiveness score"},
        "used": {"type": "boolean", "required": True, "description": "Whether used"},
        "feedback": {"type": "string", "required": False, "description": "User feedback"},
        "created_at": {"type": "timestamp", "required": True, "description": "Creation time"},
        "used_at": {"type": "timestamp", "required": False, "description": "When used"}
    },
    indexes=[
        {"fields": ["parent_id", "created_at"], "name": "parent_suggestions_by_time"},
        {"fields": ["student_id", "created_at"], "name": "student_suggestions_by_time"},
        {"fields": ["communication_type", "created_at"], "name": "suggestions_by_type"},
        {"fields": ["used", "created_at"], "name": "suggestions_by_usage"}
    ]
)

ENGAGEMENT_CHALLENGES_SCHEMA = DatabaseSchema(
    collection_name="engagement_challenges",
    description="Gamified engagement challenges",
    fields={
        "challenge_id": {"type": "string", "required": True, "description": "Unique identifier"},
        "parent_id": {"type": "string", "required": True, "description": "Parent ID"},
        "student_id": {"type": "string", "required": True, "description": "Student ID"},
        "challenge_type": {"type": "string", "required": True, "description": "Type of challenge"},
        "title": {"type": "string", "required": True, "description": "Challenge title"},
        "description": {"type": "string", "required": True, "description": "Challenge description"},
        "difficulty_level": {"type": "string", "required": True, "description": "Difficulty level"},
        "target_metrics": {"type": "map", "required": True, "description": "Target metrics"},
        "current_progress": {"type": "map", "required": True, "description": "Current progress"},
        "points_awarded": {"type": "integer", "required": True, "description": "Points awarded"},
        "bonus_points": {"type": "integer", "required": True, "description": "Bonus points"},
        "start_date": {"type": "timestamp", "required": True, "description": "Start date"},
        "end_date": {"type": "timestamp", "required": True, "description": "End date"},
        "status": {"type": "string", "required": True, "description": "Challenge status"},
        "completed_at": {"type": "timestamp", "required": False, "description": "Completion time"},
        "created_at": {"type": "timestamp", "required": True, "description": "Creation time"}
    },
    indexes=[
        {"fields": ["parent_id", "created_at"], "name": "parent_challenges_by_time"},
        {"fields": ["student_id", "created_at"], "name": "student_challenges_by_time"},
        {"fields": ["challenge_type", "created_at"], "name": "challenges_by_type"},
        {"fields": ["status", "created_at"], "name": "challenges_by_status"}
    ]
)

ACHIEVEMENTS_SCHEMA = DatabaseSchema(
    collection_name="achievements",
    description="Parent and student achievements",
    fields={
        "achievement_id": {"type": "string", "required": True, "description": "Unique identifier"},
        "parent_id": {"type": "string", "required": True, "description": "Parent ID"},
        "student_id": {"type": "string", "required": True, "description": "Student ID"},
        "achievement_type": {"type": "string", "required": True, "description": "Type of achievement"},
        "title": {"type": "string", "required": True, "description": "Achievement title"},
        "description": {"type": "string", "required": True, "description": "Achievement description"},
        "badge_icon": {"type": "string", "required": True, "description": "Badge icon"},
        "points_awarded": {"type": "integer", "required": True, "description": "Points awarded"},
        "rarity": {"type": "string", "required": True, "description": "Achievement rarity"},
        "criteria_met": {"type": "map", "required": True, "description": "Criteria met"},
        "earned_at": {"type": "timestamp", "required": True, "description": "When earned"},
        "shared": {"type": "boolean", "required": True, "description": "Whether shared"},
        "created_at": {"type": "timestamp", "required": True, "description": "Creation time"}
    },
    indexes=[
        {"fields": ["parent_id", "earned_at"], "name": "parent_achievements_by_time"},
        {"fields": ["student_id", "earned_at"], "name": "student_achievements_by_time"},
        {"fields": ["achievement_type", "earned_at"], "name": "achievements_by_type"},
        {"fields": ["rarity", "earned_at"], "name": "achievements_by_rarity"}
    ]
)

PARENT_RESOURCES_SCHEMA = DatabaseSchema(
    collection_name="parent_resources",
    description="AI-curated parent resources",
    fields={
        "resource_id": {"type": "string", "required": True, "description": "Unique identifier"},
        "title": {"type": "string", "required": True, "description": "Resource title"},
        "description": {"type": "string", "required": True, "description": "Resource description"},
        "resource_type": {"type": "string", "required": True, "description": "Resource type"},
        "category": {"type": "string", "required": True, "description": "Resource category"},
        "content": {"type": "string", "required": True, "description": "Resource content or URL"},
        "age_appropriate": {"type": "array", "required": True, "description": "Age groups"},
        "difficulty_level": {"type": "string", "required": True, "description": "Difficulty level"},
        "language": {"type": "string", "required": True, "description": "Resource language"},
        "tags": {"type": "array", "required": True, "description": "Resource tags"},
        "quality_score": {"type": "float", "required": True, "description": "Quality score"},
        "effectiveness_rating": {"type": "float", "required": False, "description": "Effectiveness rating"},
        "usage_count": {"type": "integer", "required": True, "description": "Usage count"},
        "download_count": {"type": "integer", "required": True, "description": "Download count"},
        "author": {"type": "string", "required": False, "description": "Resource author"},
        "source": {"type": "string", "required": False, "description": "Resource source"},
        "curated_by_ai": {"type": "boolean", "required": True, "description": "AI curated"},
        "last_updated": {"type": "timestamp", "required": True, "description": "Last updated"},
        "created_at": {"type": "timestamp", "required": True, "description": "Creation time"}
    },
    indexes=[
        {"fields": ["category", "created_at"], "name": "resources_by_category"},
        {"fields": ["resource_type", "created_at"], "name": "resources_by_type"},
        {"fields": ["quality_score", "created_at"], "name": "resources_by_quality"},
        {"fields": ["language", "created_at"], "name": "resources_by_language"}
    ]
)

RESOURCE_USAGE_SCHEMA = DatabaseSchema(
    collection_name="resource_usage",
    description="Resource usage tracking and effectiveness",
    fields={
        "usage_id": {"type": "string", "required": True, "description": "Unique identifier"},
        "parent_id": {"type": "string", "required": True, "description": "Parent ID"},
        "student_id": {"type": "string", "required": False, "description": "Student ID"},
        "resource_id": {"type": "string", "required": True, "description": "Resource ID"},
        "usage_type": {"type": "string", "required": True, "description": "Type of usage"},
        "effectiveness_rating": {"type": "float", "required": False, "description": "Effectiveness rating"},
        "feedback": {"type": "string", "required": False, "description": "User feedback"},
        "outcome": {"type": "string", "required": False, "description": "Outcome"},
        "time_spent_minutes": {"type": "integer", "required": False, "description": "Time spent"},
        "created_at": {"type": "timestamp", "required": True, "description": "Creation time"}
    },
    indexes=[
        {"fields": ["parent_id", "created_at"], "name": "parent_usage_by_time"},
        {"fields": ["student_id", "created_at"], "name": "student_usage_by_time"},
        {"fields": ["resource_id", "created_at"], "name": "usage_by_resource"},
        {"fields": ["usage_type", "created_at"], "name": "usage_by_type"}
    ]
)

# All schemas for easy access
DATABASE_SCHEMAS = {
    "ai_interactions": AI_INTERACTIONS_SCHEMA,
    "parent_insights": PARENT_INSIGHTS_SCHEMA,
    "engagement_metrics": ENGAGEMENT_METRICS_SCHEMA,
    "communication_history": COMMUNICATION_HISTORY_SCHEMA,
    "intervention_alerts": INTERVENTION_ALERTS_SCHEMA,
    "prediction_results": PREDICTION_RESULTS_SCHEMA,
    "communication_suggestions": COMMUNICATION_SUGGESTIONS_SCHEMA,
    "engagement_challenges": ENGAGEMENT_CHALLENGES_SCHEMA,
    "achievements": ACHIEVEMENTS_SCHEMA,
    "parent_resources": PARENT_RESOURCES_SCHEMA,
    "resource_usage": RESOURCE_USAGE_SCHEMA
}