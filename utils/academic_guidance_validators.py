"""
Validators for AI-Powered Academic Guidance System

This module provides validation utilities for academic guidance data
including activity logging, analysis requests, and API parameters.

Features:
- Pydantic validators for complex data types
- Business logic validation
- Data consistency checks
- Error message formatting

Author: Mentor AI Team
Version: 1.0.0
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pydantic import ValidationError, field_validator

from models.learning_analytics_models import (
    LearningActivityType, DifficultyLevel, ErrorType,
    RecommendationType, Recommendation
)

# Configure logging
logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom validation error for academic guidance data."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


def validate_activity_sequence(topic_sequence: List[str]) -> List[str]:
    """
    Validate learning sequence data.
    
    Args:
        topic_sequence: List of topic IDs in sequence
        
    Returns:
        Validated topic sequence
        
    Raises:
        ValidationError: If sequence is invalid
    """
    if not topic_sequence:
        raise ValidationError("Topic sequence cannot be empty", "topic_sequence")
    
    if len(topic_sequence) > 20:
        raise ValidationError("Topic sequence cannot exceed 20 topics", "topic_sequence")
    
    # Check for duplicates
    if len(topic_sequence) != len(set(topic_sequence)):
        raise ValidationError("Topic sequence cannot contain duplicates", "topic_sequence")
    
    return topic_sequence


def validate_completion_percentage(completion_percentage: float) -> float:
    """
    Validate completion percentage.
    
    Args:
        completion_percentage: Completion percentage value
        
    Returns:
        Validated completion percentage
        
    Raises:
        ValidationError: If percentage is invalid
    """
    if not isinstance(completion_percentage, (int, float)):
        raise ValidationError("Completion percentage must be a number", "completion_percentage")
    
    if completion_percentage < 0 or completion_percentage > 100:
        raise ValidationError("Completion percentage must be between 0 and 100", "completion_percentage")
    
    # Round to 1 decimal place
    return round(completion_percentage, 1)


def validate_time_spent(time_spent_minutes: int) -> int:
    """
    Validate time spent on activity.
    
    Args:
        time_spent_minutes: Time spent in minutes
        
    Returns:
        Validated time spent
        
    Raises:
        ValidationError: If time is invalid
    """
    if not isinstance(time_spent_minutes, int):
        raise ValidationError("Time spent must be an integer", "time_spent_minutes")
    
    if time_spent_minutes < 0:
        raise ValidationError("Time spent cannot be negative", "time_spent_minutes")
    
    if time_spent_minutes > 480:  # 8 hours max per session
        raise ValidationError("Time spent cannot exceed 480 minutes (8 hours)", "time_spent_minutes")
    
    return time_spent_minutes


def validate_quiz_score(score_percentage: float) -> float:
    """
    Validate quiz score percentage.
    
    Args:
        score_percentage: Quiz score percentage
        
    Returns:
        Validated score percentage
        
    Raises:
        ValidationError: If score is invalid
    """
    if not isinstance(score_percentage, (int, float)):
        raise ValidationError("Score percentage must be a number", "score_percentage")
    
    if score_percentage < 0 or score_percentage > 100:
        raise ValidationError("Score percentage must be between 0 and 100", "score_percentage")
    
    return round(score_percentage, 1)


def validate_session_duration(start_time: datetime, end_time: datetime) -> int:
    """
    Validate session duration and calculate minutes.
    
    Args:
        start_time: Session start time
        end_time: Session end time
        
    Returns:
        Duration in minutes
        
    Raises:
        ValidationError: If session times are invalid
    """
    if not isinstance(start_time, datetime) or not isinstance(end_time, datetime):
        raise ValidationError("Session times must be datetime objects")
    
    if end_time <= start_time:
        raise ValidationError("End time must be after start time")
    
    duration = (end_time - start_time).total_seconds() / 60
    
    if duration > 480:  # 8 hours max
        raise ValidationError("Session duration cannot exceed 480 minutes (8 hours)")
    
    return int(duration)


def validate_error_type(error_type: str) -> ErrorType:
    """
    Validate error type.
    
    Args:
        error_type: Error type string
        
    Returns:
        Validated error type
        
    Raises:
        ValidationError: If error type is invalid
    """
    valid_types = [e.value for e in ErrorType]
    
    if error_type not in valid_types:
        raise ValidationError(
            f"Invalid error type. Must be one of: {', '.join(valid_types)}",
            "error_type"
        )
    
    return ErrorType(error_type)


def validate_difficulty_level(difficulty: str) -> DifficultyLevel:
    """
    Validate difficulty level.
    
    Args:
        difficulty: Difficulty level string
        
    Returns:
        Validated difficulty level
        
    Raises:
        ValidationError: If difficulty is invalid
    """
    valid_levels = [level.value for level in DifficultyLevel]
    
    if difficulty not in valid_levels:
        raise ValidationError(
            f"Invalid difficulty level. Must be one of: {', '.join(valid_levels)}",
            "difficulty"
        )
    
    return DifficultyLevel(difficulty)


def validate_recommendation_priority(priority: str) -> str:
    """
    Validate recommendation priority.
    
    Args:
        priority: Priority string
        
    Returns:
        Validated priority
        
    Raises:
        ValidationError: If priority is invalid
    """
    valid_priorities = ["low", "medium", "high", "urgent"]
    
    if priority not in valid_priorities:
        raise ValidationError(
            f"Invalid priority. Must be one of: {', '.join(valid_priorities)}",
            "priority"
        )
    
    return priority


def validate_recommendation_type(rec_type: str) -> RecommendationType:
    """
    Validate recommendation type.
    
    Args:
        rec_type: Recommendation type string
        
    Returns:
        Validated recommendation type
        
    Raises:
        ValidationError: If recommendation type is invalid
    """
    valid_types = [t.value for t in RecommendationType]
    
    if rec_type not in valid_types:
        raise ValidationError(
            f"Invalid recommendation type. Must be one of: {', '.join(valid_types)}",
            "recommendation_type"
        )
    
    return RecommendationType(rec_type)


def validate_estimated_time(hours: float) -> float:
    """
    Validate estimated time for recommendations.
    
    Args:
        hours: Estimated time in hours
        
    Returns:
        Validated time in hours
        
    Raises:
        ValidationError: If time is invalid
    """
    if not isinstance(hours, (int, float)):
        raise ValidationError("Estimated time must be a number", "estimated_time_hours")
    
    if hours < 0:
        raise ValidationError("Estimated time cannot be negative", "estimated_time_hours")
    
    if hours > 100:  # 100 hours max per recommendation
        raise ValidationError("Estimated time cannot exceed 100 hours", "estimated_time_hours")
    
    return round(hours, 1)


def validate_student_id(student_id: str) -> str:
    """
    Validate student ID format.
    
    Args:
        student_id: Student identifier
        
    Returns:
        Validated student ID
        
    Raises:
        ValidationError: If student ID is invalid
    """
    if not isinstance(student_id, str):
        raise ValidationError("Student ID must be a string", "student_id")
    
    if not student_id.strip():
        raise ValidationError("Student ID cannot be empty", "student_id")
    
    if len(student_id) < 3 or len(student_id) > 50:
        raise ValidationError("Student ID must be between 3 and 50 characters", "student_id")
    
    # Check for valid characters (alphanumeric, underscore, hyphen)
    import re
    if not re.match(r'^[a-zA-Z0-9_-]+$', student_id):
        raise ValidationError("Student ID can only contain letters, numbers, underscore, and hyphen", "student_id")
    
    return student_id.strip()


def validate_topic_id(topic_id: str) -> str:
    """
    Validate topic ID format.
    
    Args:
        topic_id: Topic identifier
        
    Returns:
        Validated topic ID
        
    Raises:
        ValidationError: If topic ID is invalid
    """
    if not isinstance(topic_id, str):
        raise ValidationError("Topic ID must be a string", "topic_id")
    
    if not topic_id.strip():
        raise ValidationError("Topic ID cannot be empty", "topic_id")
    
    if len(topic_id) < 5 or len(topic_id) > 100:
        raise ValidationError("Topic ID must be between 5 and 100 characters", "topic_id")
    
    # Check for valid format (subject_topic_identifier)
    import re
    if not re.match(r'^[a-zA-Z0-9_]+$', topic_id):
        raise ValidationError("Topic ID can only contain letters, numbers, and underscore", "topic_id")
    
    return topic_id.strip()


def validate_activity_data_consistency(
    activities: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Validate consistency of activity data.
    
    Args:
        activities: List of activity dictionaries
        
    Returns:
        Validated activities
        
    Raises:
        ValidationError: If data is inconsistent
    """
    if not activities:
        raise ValidationError("Activities list cannot be empty")
    
    validated_activities = []
    
    for i, activity in enumerate(activities):
        try:
            # Check required fields based on activity type
            activity_type = activity.get("activity_type")
            
            if activity_type == "topic_study":
                required_fields = ["topic_id", "subject", "time_spent_minutes", "completion_percentage"]
            elif activity_type == "quiz_attempt":
                required_fields = ["quiz_id", "subject", "topic_id", "score_percentage"]
            elif activity_type == "learning_sequence":
                required_fields = ["topic_sequence", "session_duration_minutes"]
            else:
                # Skip validation for unknown activity types
                validated_activities.append(activity)
                continue
            
            # Check required fields
            missing_fields = [field for field in required_fields if field not in activity]
            if missing_fields:
                raise ValidationError(
                    f"Activity {i+1} missing required fields: {', '.join(missing_fields)}",
                    f"activities[{i}]"
                )
            
            # Validate specific fields
            if "time_spent_minutes" in activity:
                activity["time_spent_minutes"] = validate_time_spent(activity["time_spent_minutes"])
            
            if "completion_percentage" in activity:
                activity["completion_percentage"] = validate_completion_percentage(activity["completion_percentage"])
            
            if "score_percentage" in activity:
                activity["score_percentage"] = validate_quiz_score(activity["score_percentage"])
            
            validated_activities.append(activity)
            
        except ValidationError as e:
            # Add context to validation error
            if not e.field:
                e.field = f"activities[{i}]"
            raise e
    
    return validated_activities


def validate_recommendation_data(recommendation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate recommendation data structure.
    
    Args:
        recommendation: Recommendation dictionary
        
    Returns:
        Validated recommendation
        
    Raises:
        ValidationError: If recommendation is invalid
    """
    required_fields = ["recommendation_type", "priority", "title", "description", "expected_outcome"]
    
    # Check required fields
    missing_fields = [field for field in required_fields if field not in recommendation]
    if missing_fields:
        raise ValidationError(
            f"Recommendation missing required fields: {', '.join(missing_fields)}"
        )
    
    # Validate specific fields
    if "priority" in recommendation:
        recommendation["priority"] = validate_recommendation_priority(recommendation["priority"])
    
    if "recommendation_type" in recommendation:
        recommendation["recommendation_type"] = validate_recommendation_type(recommendation["recommendation_type"])
    
    if "estimated_time_hours" in recommendation:
        recommendation["estimated_time_hours"] = validate_estimated_time(recommendation["estimated_time_hours"])
    
    return recommendation


def format_validation_errors(errors: List[ValidationError]) -> Dict[str, Any]:
    """
    Format validation errors for API responses.
    
    Args:
        errors: List of validation errors
        
    Returns:
        Formatted error dictionary
    """
    formatted_errors = []
    
    for error in errors:
        error_dict = {
            "message": error.message,
            "field": error.field
        }
        formatted_errors.append(error_dict)
    
    return {
        "success": False,
        "error_type": "validation_error",
        "errors": formatted_errors,
        "total_errors": len(errors)
    }


class ActivityDataValidator:
    """Comprehensive validator for activity data."""
    
    @staticmethod
    def validate_topic_access(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate topic access activity data.
        
        Args:
            data: Topic access data dictionary
            
        Returns:
            Validated data
            
        Raises:
            ValidationError: If data is invalid
        """
        required_fields = ["student_id", "topic_id", "subject", "time_spent_minutes", "completion_percentage"]
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}", field)
        
        # Validate specific fields
        data["student_id"] = validate_student_id(data["student_id"])
        data["topic_id"] = validate_topic_id(data["topic_id"])
        data["time_spent_minutes"] = validate_time_spent(data["time_spent_minutes"])
        data["completion_percentage"] = validate_completion_percentage(data["completion_percentage"])
        
        return data
    
    @staticmethod
    def validate_quiz_attempt(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate quiz attempt activity data.
        
        Args:
            data: Quiz attempt data dictionary
            
        Returns:
            Validated data
            
        Raises:
            ValidationError: If data is invalid
        """
        required_fields = ["student_id", "quiz_id", "subject", "topic_id", "score_percentage"]
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}", field)
        
        # Validate specific fields
        data["student_id"] = validate_student_id(data["student_id"])
        data["topic_id"] = validate_topic_id(data["topic_id"])
        data["score_percentage"] = validate_quiz_score(data["score_percentage"])
        
        # Validate optional fields
        if "difficulty" in data:
            data["difficulty"] = validate_difficulty_level(data["difficulty"])
        
        if "question_errors" in data and data["question_errors"]:
            for i, error in enumerate(data["question_errors"]):
                if "error_type" in error:
                    error["error_type"] = validate_error_type(error["error_type"])
        
        return data
    
    @staticmethod
    def validate_learning_sequence(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate learning sequence activity data.
        
        Args:
            data: Learning sequence data dictionary
            
        Returns:
            Validated data
            
        Raises:
            ValidationError: If data is invalid
        """
        required_fields = ["student_id", "topic_sequence", "session_duration_minutes"]
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}", field)
        
        # Validate specific fields
        data["student_id"] = validate_student_id(data["student_id"])
        data["topic_sequence"] = validate_activity_sequence(data["topic_sequence"])
        data["session_duration_minutes"] = validate_time_spent(data["session_duration_minutes"])
        
        return data