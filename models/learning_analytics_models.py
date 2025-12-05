"""
Learning Analytics Models for AI-Powered Academic Guidance System

This module defines Pydantic models for capturing and analyzing student learning data,
including topic completion times, quiz scores, error patterns, and learning sequences.

Author: Mentor AI Team
Version: 1.0.0
"""

from datetime import datetime, date
from typing import List, Dict, Optional, Literal, Any, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


class ErrorType(str, Enum):
    """Types of errors students can make."""
    MISINTERPRETING_QUESTION = "misinterpreting_question"
    FORMULA_ERROR = "formula_error"
    CALCULATION_ERROR = "calculation_error"
    CONCEPTUAL_ERROR = "conceptual_error"
    TIME_MANAGEMENT = "time_management"
    CARELESS_MISTAKE = "careless_mistake"
    UNKNOWN = "unknown"


class LearningActivityType(str, Enum):
    """Types of learning activities."""
    TOPIC_STUDY = "topic_study"
    QUIZ_ATTEMPT = "quiz_attempt"
    PRACTICE_PROBLEMS = "practice_problems"
    VIDEO_WATCH = "video_watch"
    REVISION = "revision"
    DOUBT_RESOLUTION = "doubt_resolution"


class DifficultyLevel(str, Enum):
    """Difficulty levels for topics and questions."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class RecommendationType(str, Enum):
    """Types of recommendations."""
    PREREQUISITE_REVIEW = "prerequisite_review"
    ALTERNATIVE_RESOURCE = "alternative_resource"
    PRACTICE_MORE = "practice_more"
    CONCEPT_REINFORCEMENT = "concept_reinforcement"
    STUDY_STRATEGY = "study_strategy"
    TIME_ALLOCATION = "time_allocation"


class TopicAccess(BaseModel):
    """Record of a student accessing a topic."""
    
    activity_id: str = Field(..., description="Unique activity identifier")
    student_id: str = Field(..., description="Student identifier")
    topic_id: str = Field(..., description="Topic identifier")
    subject: str = Field(..., description="Subject name")
    chapter: Optional[str] = Field(None, description="Chapter name")
    sequence_number: int = Field(..., description="Order in learning sequence")
    access_time: datetime = Field(..., description="When topic was accessed")
    time_spent_minutes: int = Field(..., ge=0, description="Time spent on topic")
    completion_percentage: float = Field(..., ge=0, le=100, description="Completion percentage")
    activity_type: LearningActivityType = Field(..., description="Type of learning activity")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "activity_id": "activity_123",
                "student_id": "student_456",
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
    )


class QuizAttempt(BaseModel):
    """Record of a quiz attempt with detailed error analysis."""
    
    attempt_id: str = Field(..., description="Unique attempt identifier")
    student_id: str = Field(..., description="Student identifier")
    quiz_id: str = Field(..., description="Quiz identifier")
    subject: str = Field(..., description="Subject name")
    topic_id: str = Field(..., description="Primary topic covered")
    difficulty: DifficultyLevel = Field(..., description="Quiz difficulty level")
    start_time: datetime = Field(..., description="Quiz start time")
    end_time: datetime = Field(..., description="Quiz end time")
    total_time_minutes: int = Field(..., ge=0, description="Total time taken")
    total_questions: int = Field(..., gt=0, description="Total questions in quiz")
    attempted_questions: int = Field(..., ge=0, description="Questions attempted")
    correct_answers: int = Field(..., ge=0, description="Correct answers")
    score_percentage: float = Field(..., ge=0, le=100, description="Score percentage")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "attempt_id": "attempt_789",
                "student_id": "student_456",
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
                "score_percentage": 66.7
            }
        }
    )


class QuestionError(BaseModel):
    """Detailed error analysis for a specific question."""
    
    error_id: str = Field(..., description="Unique error identifier")
    attempt_id: str = Field(..., description="Associated quiz attempt")
    question_number: int = Field(..., gt=0, description="Question number")
    error_type: ErrorType = Field(..., description="Type of error made")
    error_description: str = Field(..., description="Detailed error description")
    student_answer: str = Field(..., description="Student's incorrect answer")
    correct_answer: str = Field(..., description="Correct answer")
    time_spent_seconds: int = Field(..., ge=0, description="Time spent on this question")
    confidence_level: Optional[float] = Field(
        None, ge=0, le=10, description="Student's confidence (1-10)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error_id": "error_001",
                "attempt_id": "attempt_789",
                "question_number": 5,
                "error_type": "formula_error",
                "error_description": "Applied wrong formula for heat transfer calculation",
                "student_answer": "25 J",
                "correct_answer": "35 J",
                "time_spent_seconds": 180,
                "confidence_level": 7.0
            }
        }
    )


class LearningSequence(BaseModel):
    """Sequence of topics accessed by a student."""
    
    sequence_id: str = Field(..., description="Unique sequence identifier")
    student_id: str = Field(..., description="Student identifier")
    session_date: date = Field(..., description="Date of learning session")
    session_duration_minutes: int = Field(..., ge=0, description="Total session duration")
    topic_sequence: List[str] = Field(..., description="Ordered list of topic IDs")
    subject_transitions: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="Records of subject changes during session"
    )
    completion_rates: Dict[str, float] = Field(
        default_factory=dict,
        description="Completion rates for each topic"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sequence_id": "sequence_001",
                "student_id": "student_456",
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
    )


class LearningPattern(BaseModel):
    """Identified learning patterns for a student."""
    
    pattern_id: str = Field(..., description="Unique pattern identifier")
    student_id: str = Field(..., description="Student identifier")
    pattern_type: str = Field(..., description="Type of pattern identified")
    description: str = Field(..., description="Pattern description")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in pattern")
    frequency: float = Field(..., ge=0, description="How often pattern occurs")
    impact_level: Literal["low", "medium", "high"] = Field(..., description="Impact on learning")
    detected_at: datetime = Field(..., description="When pattern was detected")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "pattern_id": "pattern_001",
                "student_id": "student_456",
                "pattern_type": "difficulty_with_formulas",
                "description": "Student consistently makes formula errors in physics problems",
                "confidence_score": 0.85,
                "frequency": 0.7,
                "impact_level": "high",
                "detected_at": "2024-01-15T16:00:00Z"
            }
        }
    )


class KnowledgeGap(BaseModel):
    """Identified knowledge gaps for a student."""
    
    gap_id: str = Field(..., description="Unique gap identifier")
    student_id: str = Field(..., description="Student identifier")
    topic_id: str = Field(..., description="Topic with knowledge gap")
    subject: str = Field(..., description="Subject name")
    gap_type: Literal["conceptual", "procedural", "factual"] = Field(..., description="Type of gap")
    severity: Literal["minor", "moderate", "critical"] = Field(..., description="Gap severity")
    evidence: List[str] = Field(..., description="Evidence supporting gap identification")
    estimated_hours_to_close: float = Field(..., ge=0, description="Estimated hours to close gap")
    prerequisite_topics: List[str] = Field(
        default_factory=list, 
        description="Prerequisite topics that need review"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "gap_id": "gap_001",
                "student_id": "student_456",
                "topic_id": "topic_thermodynamics_001",
                "subject": "Physics",
                "gap_type": "conceptual",
                "severity": "moderate",
                "evidence": [
                    "Low scores in thermodynamics quizzes (45% average)",
                    "Formula errors in 70% of attempts",
                    "Slow completion time (2x average)"
                ],
                "estimated_hours_to_close": 8.0,
                "prerequisite_topics": ["topic_heat_transfer_basics", "topic_energy_concepts"]
            }
        }
    )


class LearningStrength(BaseModel):
    """Identified learning strengths for a student."""
    
    strength_id: str = Field(..., description="Unique strength identifier")
    student_id: str = Field(..., description="Student identifier")
    topic_id: str = Field(..., description="Topic of strength")
    subject: str = Field(..., description="Subject name")
    strength_type: Literal["conceptual", "procedural", "application"] = Field(..., description="Type of strength")
    mastery_level: Literal["developing", "proficient", "advanced"] = Field(..., description="Mastery level")
    evidence: List[str] = Field(..., description="Evidence supporting strength identification")
    consistency_score: float = Field(..., ge=0, le=1, description="Consistency of performance")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "strength_id": "strength_001",
                "student_id": "student_456",
                "topic_id": "topic_mechanics_001",
                "subject": "Physics",
                "strength_type": "procedural",
                "mastery_level": "proficient",
                "evidence": [
                    "High scores in mechanics quizzes (85% average)",
                    "Fast completion time (0.8x average)",
                    "No procedural errors in last 5 attempts"
                ],
                "consistency_score": 0.9
            }
        }
    )


class Recommendation(BaseModel):
    """Personalized recommendation for a student."""
    
    recommendation_id: str = Field(..., description="Unique recommendation identifier")
    student_id: str = Field(..., description="Student identifier")
    recommendation_type: RecommendationType = Field(..., description="Type of recommendation")
    priority: Literal["low", "medium", "high", "urgent"] = Field(..., description="Recommendation priority")
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Detailed recommendation description")
    target_topic_id: Optional[str] = Field(None, description="Target topic for recommendation")
    target_subject: Optional[str] = Field(None, description="Target subject")
    estimated_time_hours: Optional[float] = Field(None, ge=0, description="Estimated time to implement")
    resources: List[Dict[str, str]] = Field(
        default_factory=list, 
        description="Recommended resources"
    )
    action_steps: List[str] = Field(
        default_factory=list, 
        description="Specific action steps to take"
    )
    expected_outcome: str = Field(..., description="Expected learning outcome")
    valid_until: Optional[datetime] = Field(None, description="Recommendation expiry date")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "recommendation_id": "rec_001",
                "student_id": "student_456",
                "recommendation_type": "prerequisite_review",
                "priority": "high",
                "title": "Review Heat Transfer Basics",
                "description": "Review fundamental concepts of heat transfer before continuing with thermodynamics",
                "target_topic_id": "topic_heat_transfer_basics",
                "target_subject": "Physics",
                "estimated_time_hours": 3.0,
                "resources": [
                    {"type": "video", "url": "https://example.com/heat-transfer", "title": "Heat Transfer Fundamentals"},
                    {"type": "practice", "url": "https://example.com/problems", "title": "Practice Problems"}
                ],
                "action_steps": [
                    "Watch introductory video on heat transfer",
                    "Complete 10 practice problems",
                    "Review formula sheet"
                ],
                "expected_outcome": "Improved understanding of thermodynamics concepts and better quiz performance",
                "valid_until": "2024-01-22T00:00:00Z"
            }
        }
    )


class LearningProgress(BaseModel):
    """Overall learning progress for a student."""
    
    progress_id: str = Field(..., description="Unique progress identifier")
    student_id: str = Field(..., description="Student identifier")
    subject: str = Field(..., description="Subject name")
    total_topics: int = Field(..., gt=0, description="Total topics in subject")
    completed_topics: int = Field(..., ge=0, description="Completed topics")
    mastered_topics: int = Field(..., ge=0, description="Mastered topics")
    current_streak_days: int = Field(..., ge=0, description="Current learning streak")
    longest_streak_days: int = Field(..., ge=0, description="Longest learning streak")
    average_session_time: float = Field(..., ge=0, description="Average session time in minutes")
    total_study_hours: float = Field(..., ge=0, description="Total study hours")
    last_activity: datetime = Field(..., description="Last learning activity")
    progress_percentage: float = Field(..., ge=0, le=100, description="Overall progress percentage")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "progress_id": "progress_001",
                "student_id": "student_456",
                "subject": "Physics",
                "total_topics": 50,
                "completed_topics": 35,
                "mastered_topics": 20,
                "current_streak_days": 5,
                "longest_streak_days": 12,
                "average_session_time": 75.5,
                "total_study_hours": 45.0,
                "last_activity": "2024-01-15T16:30:00Z",
                "progress_percentage": 70.0
            }
        }
    )


class StudentActivityLog(BaseModel):
    """Comprehensive activity log for a student."""
    
    log_id: str = Field(..., description="Unique log identifier")
    student_id: str = Field(..., description="Student identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    activities: List[Union[TopicAccess, QuizAttempt, LearningSequence]] = Field(
        ..., description="List of activities in the session"
    )
    session_start: datetime = Field(..., description="Session start time")
    session_end: datetime = Field(..., description="Session end time")
    total_duration_minutes: int = Field(..., ge=0, description="Total session duration")
    device_type: Optional[str] = Field(None, description="Device used (mobile/desktop/tablet)")
    browser: Optional[str] = Field(None, description="Browser used")
    ip_address: Optional[str] = Field(None, description="IP address (for security)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "log_id": "log_001",
                "student_id": "student_456",
                "session_id": "session_001",
                "activities": [
                    {
                        "activity_id": "activity_123",
                        "topic_id": "topic_mechanics_001",
                        "time_spent_minutes": 30,
                        "completion_percentage": 100.0
                    }
                ],
                "session_start": "2024-01-15T14:00:00Z",
                "session_end": "2024-01-15T16:30:00Z",
                "total_duration_minutes": 150,
                "device_type": "desktop",
                "browser": "Chrome"
            }
        }
    )