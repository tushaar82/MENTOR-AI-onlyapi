"""
Configuration for AI-Powered Academic Guidance System

This module provides configuration settings for the academic guidance system
including analysis parameters, recommendation settings, and feature flags.

Features:
- Analysis thresholds and parameters
- Recommendation engine settings
- Cache configuration
- Feature flags for A/B testing
- Performance monitoring settings

Author: Mentor AI Team
Version: 1.0.0
"""

import os
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AnalysisConfig(BaseModel):
    """Configuration for learning analysis."""
    
    min_data_points_for_pattern: int = Field(
        default=5,
        description="Minimum data points required for pattern detection"
    )
    error_pattern_threshold: float = Field(
        default=0.6,
        description="Threshold for error pattern detection (0.0-1.0)"
    )
    strength_confidence_threshold: float = Field(
        default=0.8,
        description="Confidence threshold for strength identification (0.0-1.0)"
    )
    gap_severity_thresholds: Dict[str, float] = Field(
        default={
            "minor": 0.3,
            "moderate": 0.5,
            "critical": 0.7
        },
        description="Performance thresholds for gap severity classification"
    )
    session_duration_max_minutes: int = Field(
        default=480,
        description="Maximum session duration in minutes (8 hours)"
    )
    sequence_max_topics: int = Field(
        default=20,
        description="Maximum topics per learning sequence"
    )


class RecommendationConfig(BaseModel):
    """Configuration for recommendation engine."""
    
    max_recommendations_per_type: int = Field(
        default=3,
        description="Maximum recommendations per type"
    )
    recommendation_validity_days: int = Field(
        default=14,
        description="Validity period for recommendations in days"
    )
    urgency_thresholds: Dict[str, int] = Field(
        default={
            "critical_gap": 3,
            "declining_performance": 7,
            "missed_prerequisites": 5
        },
        description="Days threshold for urgent recommendations"
    )
    max_estimated_hours_per_recommendation: float = Field(
        default=100.0,
        description="Maximum estimated hours per recommendation"
    )
    priority_weights: Dict[str, float] = Field(
        default={
            "urgent": 4.0,
            "high": 3.0,
            "medium": 2.0,
            "low": 1.0
        },
        description="Weights for recommendation prioritization"
    )


class CacheConfig(BaseModel):
    """Configuration for caching."""
    
    analysis_cache_hours: int = Field(
        default=24,
        description="Cache duration for analysis results in hours"
    )
    recommendations_cache_hours: int = Field(
        default=24,
        description="Cache duration for recommendations in hours"
    )
    max_cache_size: int = Field(
        default=1000,
        description="Maximum number of cached items"
    )
    enable_cache: bool = Field(
        default=True,
        description="Enable caching for performance"
    )


class DatabaseConfig(BaseModel):
    """Configuration for database connections."""
    
    connection_timeout_seconds: int = Field(
        default=30,
        description="Database connection timeout in seconds"
    )
    max_connections: int = Field(
        default=10,
        description="Maximum database connections"
    )
    batch_size: int = Field(
        default=100,
        description="Batch size for database operations"
    )
    enable_connection_pooling: bool = Field(
        default=True,
        description="Enable connection pooling"
    )


class LoggingConfig(BaseModel):
    """Configuration for logging."""
    
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    log_file_path: Optional[str] = Field(
        default=None,
        description="Path to log file (None for console only)"
    )
    max_log_size_mb: int = Field(
        default=100,
        description="Maximum log file size in MB"
    )
    enable_rotation: bool = Field(
        default=True,
        description="Enable log file rotation"
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )


class MonitoringConfig(BaseModel):
    """Configuration for monitoring and metrics."""
    
    enable_performance_monitoring: bool = Field(
        default=True,
        description="Enable performance monitoring"
    )
    metrics_collection_interval_seconds: int = Field(
        default=300,
        description="Interval for metrics collection in seconds"
    )
    enable_alerts: bool = Field(
        default=True,
        description="Enable alerting for anomalies"
    )
    alert_thresholds: Dict[str, float] = Field(
        default={
            "analysis_failure_rate": 0.05,
            "recommendation_generation_failure_rate": 0.05,
            "database_connection_failure_rate": 0.1
        },
        description="Thresholds for generating alerts"
    )


class FeatureFlags(BaseModel):
    """Feature flags for A/B testing and gradual rollout."""
    
    enable_advanced_analysis: bool = Field(
        default=True,
        description="Enable advanced learning pattern analysis"
    )
    enable_ml_recommendations: bool = Field(
        default=False,
        description="Enable machine learning based recommendations"
    )
    enable_real_time_analysis: bool = Field(
        default=True,
        description="Enable real-time analysis triggers"
    )
    enable_predictive_insights: bool = Field(
        default=False,
        description="Enable predictive learning insights"
    )
    enable_parent_notifications: bool = Field(
        default=True,
        description="Enable parent notifications for critical insights"
    )
    rollout_percentage: float = Field(
        default=100.0,
        description="Percentage of users to roll out features to (0-100)"
    )


class AcademicGuidanceConfig(BaseModel):
    """Main configuration for academic guidance system."""
    
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)
    recommendations: RecommendationConfig = Field(default_factory=RecommendationConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    features: FeatureFlags = Field(default_factory=FeatureFlags)
    
    class Config:
        env_prefix = "ACADEMIC_GUIDANCE_"
        env_file = ".env"
        case_sensitive = False


def get_config() -> AcademicGuidanceConfig:
    """
    Get academic guidance configuration from environment variables.
    
    Returns:
        AcademicGuidanceConfig: Configuration object
        
    Raises:
        ValueError: If required environment variables are missing
    """
    try:
        config = AcademicGuidanceConfig()
        
        # Log configuration loading
        print(f"Academic Guidance Configuration loaded:")
        print(f"  Analysis: min_data_points={config.analysis.min_data_points_for_pattern}")
        print(f"  Recommendations: max_per_type={config.recommendations.max_recommendations_per_type}")
        print(f"  Cache: enabled={config.cache.enable_cache}, duration={config.cache.analysis_cache_hours}h")
        print(f"  Features: advanced_analysis={config.features.enable_advanced_analysis}")
        print(f"  Monitoring: enabled={config.monitoring.enable_performance_monitoring}")
        
        return config
        
    except Exception as e:
        print(f"Error loading configuration: {e}")
        # Return default configuration on error
        return AcademicGuidanceConfig()


def get_firestore_config() -> Dict[str, Any]:
    """
    Get Firestore configuration from environment.
    
    Returns:
        Dictionary with Firestore configuration
    """
    return {
        "credentials_path": os.getenv("FIREBASE_CREDENTIALS_PATH", "config/firebase-credentials.json"),
        "project_id": os.getenv("FIREBASE_PROJECT_ID", "mentor-ai-dev"),
        "storage_bucket": os.getenv("FIREBASE_STORAGE_BUCKET", "mentor-ai-dev.appspot.com"),
        "database_url": os.getenv("FIREBASE_DATABASE_URL"),
        "collection_prefix": os.getenv("FIREBASE_COLLECTION_PREFIX", "mentor_ai")
    }


def get_gemini_config() -> Dict[str, Any]:
    """
    Get Gemini API configuration from environment.
    
    Returns:
        Dictionary with Gemini API configuration
    """
    return {
        "api_key": os.getenv("GOOGLE_API_KEY", ""),
        "model": os.getenv("GEMINI_MODEL", "gemini-pro"),
        "temperature": float(os.getenv("GEMINI_TEMPERATURE", "0.7")),
        "max_tokens": int(os.getenv("GEMINI_MAX_TOKENS", "2048")),
        "timeout_seconds": int(os.getenv("GEMINI_TIMEOUT_SECONDS", "30")),
        "retry_attempts": int(os.getenv("GEMINI_RETRY_ATTEMPTS", "3")),
        "enable_caching": os.getenv("GEMINI_ENABLE_CACHING", "true").lower() == "true"
    }


def get_analysis_thresholds() -> Dict[str, float]:
    """
    Get analysis thresholds for different metrics.
    
    Returns:
        Dictionary with analysis thresholds
    """
    config = get_config()
    return {
        "pattern_detection": config.analysis.min_data_points_for_pattern,
        "error_pattern": config.analysis.error_pattern_threshold,
        "strength_confidence": config.analysis.strength_confidence_threshold,
        "gap_critical": config.analysis.gap_severity_thresholds["critical"],
        "gap_moderate": config.analysis.gap_severity_thresholds["moderate"],
        "gap_minor": config.analysis.gap_severity_thresholds["minor"],
        "completion_low": 40.0,
        "completion_high": 90.0,
        "score_poor": 50.0,
        "score_excellent": 85.0,
        "session_short_minutes": 30,
        "session_long_minutes": 240
    }


def get_recommendation_settings() -> Dict[str, Any]:
    """
    Get recommendation engine settings.
    
    Returns:
        Dictionary with recommendation settings
    """
    config = get_config()
    return {
        "max_per_type": config.recommendations.max_recommendations_per_type,
        "validity_days": config.recommendations.recommendation_validity_days,
        "urgency_thresholds": config.recommendations.urgency_thresholds,
        "priority_weights": config.recommendations.priority_weights,
        "max_estimated_hours": config.recommendations.max_estimated_hours_per_recommendation
    }


def get_cache_settings() -> Dict[str, Any]:
    """
    Get cache configuration.
    
    Returns:
        Dictionary with cache settings
    """
    config = get_config()
    return {
        "enabled": config.cache.enable_cache,
        "analysis_cache_hours": config.cache.analysis_cache_hours,
        "recommendations_cache_hours": config.cache.recommendations_cache_hours,
        "max_size": config.cache.max_cache_size
    }


def get_feature_flags() -> Dict[str, bool]:
    """
    Get feature flags.
    
    Returns:
        Dictionary with feature flags
    """
    config = get_config()
    return {
        "advanced_analysis": config.features.enable_advanced_analysis,
        "ml_recommendations": config.features.enable_ml_recommendations,
        "real_time_analysis": config.features.enable_real_time_analysis,
        "predictive_insights": config.features.enable_predictive_insights,
        "parent_notifications": config.features.enable_parent_notifications,
        "rollout_enabled": config.features.rollout_percentage > 0
    }


def is_development() -> bool:
    """
    Check if running in development environment.
    
    Returns:
        bool: True if development environment
    """
    return os.getenv("ENVIRONMENT", "development").lower() == "development"


def is_production() -> bool:
    """
    Check if running in production environment.
    
    Returns:
        bool: True if production environment
    """
    return os.getenv("ENVIRONMENT", "development").lower() == "production"


def is_testing() -> bool:
    """
    Check if running in testing environment.
    
    Returns:
        bool: True if testing environment
    """
    return os.getenv("ENVIRONMENT", "development").lower() == "testing"


def get_log_level() -> str:
    """
    Get configured log level.
    
    Returns:
        str: Log level string
    """
    config = get_config()
    return config.logging.log_level


def get_database_config() -> Dict[str, Any]:
    """
    Get database configuration.
    
    Returns:
        Dictionary with database configuration
    """
    config = get_config()
    return {
        "connection_timeout": config.database.connection_timeout_seconds,
        "max_connections": config.database.max_connections,
        "batch_size": config.database.batch_size,
        "enable_connection_pooling": config.database.enable_connection_pooling
    }


def get_monitoring_config() -> Dict[str, Any]:
    """
    Get monitoring configuration.
    
    Returns:
        Dictionary with monitoring configuration
    """
    config = get_config()
    return {
        "enabled": config.monitoring.enable_performance_monitoring,
        "metrics_interval": config.monitoring.metrics_collection_interval_seconds,
        "enable_alerts": config.monitoring.enable_alerts,
        "alert_thresholds": config.monitoring.alert_thresholds
    }


# Global configuration instance
config = get_config()