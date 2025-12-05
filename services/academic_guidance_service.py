
"""
Academic Guidance Service for AI-Powered Academic Guidance System

This service orchestrates the complete academic guidance pipeline, coordinating:
- Student activity logging and tracking
- Learning data analysis
- Personalized recommendation generation
- Progress monitoring and reporting
- Firestore integration for data persistence

Features:
- Complete pipeline orchestration
- Real-time activity processing
- Comprehensive progress tracking
- Personalized guidance generation
- Parent-child access control

Author: Mentor AI Team
Version: 1.0.0
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from google.cloud import firestore
from google.cloud.firestore_v1 import FieldFilter

from models.learning_analytics_models import (
    TopicAccess, QuizAttempt, QuestionError, LearningSequence,
    StudentActivityLog, LearningProgress, Recommendation,
    LearningPattern, KnowledgeGap, LearningStrength
)
from services.learning_analysis_service import learning_analysis_service
from services.recommendation_engine import recommendation_engine
from utils.firebase_config import get_firestore_client

# Configure logging
logger = logging.getLogger(__name__)


class AcademicGuidanceServiceError(Exception):
    """Base exception for academic guidance service errors."""
    pass


class StudentNotFoundError(AcademicGuidanceServiceError):
    """Exception raised when student is not found."""
    pass


class InvalidActivityError(AcademicGuidanceServiceError):
    """Exception raised when activity data is invalid."""
    pass


class AcademicGuidanceService:
    """
    Main service for AI-powered academic guidance.
    
    This service coordinates all aspects of student learning tracking,
    analysis, and personalized recommendation generation.
    """
    
    def __init__(self):
        """Initialize academic guidance service."""
        logger.info("Initializing AcademicGuidanceService")
        
        # Initialize Firestore client
        self.db = get_firestore_client()
        
        # Collection names
        self.collections = {
            "student_activities": "student_activities",
            "topic_accesses": "topic_accesses",
            "quiz_attempts": "quiz_attempts",
            "question_errors": "question_errors",
            "learning_sequences": "learning_sequences",
            "learning_patterns": "learning_patterns",
            "knowledge_gaps": "knowledge_gaps",
            "learning_strengths": "learning_strengths",
            "learning_progress": "learning_progress",
            "recommendations": "recommendations"
        }
        
        # Analysis parameters
        self.analysis_threshold = 5  # Minimum activities for analysis
        self.recommendation_cache_hours = 24  # Cache recommendations for 24 hours
    
    async def log_student_activity(
        self,
        student_id: str,
        activity_data: Dict[str, Any]
    ) -> str:
        """
        Log a student learning activity.
        
        Args:
            student_id: Student identifier
            activity_data: Activity data including type, duration, etc.
            
        Returns:
            Activity log ID
            
        Raises:
            StudentNotFoundError: If student doesn't exist
            InvalidActivityError: If activity data is invalid
        """
        logger.info(f"Logging activity for student: {student_id}")
        
        try:
            # Validate student exists (would check users collection)
            if not await self._student_exists(student_id):
                raise StudentNotFoundError(f"Student not found: {student_id}")
            
            # Generate activity log
            activity_log = StudentActivityLog(
                log_id=f"log_{uuid.uuid4().hex[:8]}",
                student_id=student_id,
                session_id=activity_data.get("session_id"),
                activities=activity_data.get("activities", []),
                session_start=activity_data.get("session_start", datetime.utcnow()),
                session_end=activity_data.get("session_end", datetime.utcnow()),
                total_duration_minutes=activity_data.get("total_duration_minutes", 0),
                device_type=activity_data.get("device_type"),
                browser=activity_data.get("browser"),
                ip_address=activity_data.get("ip_address")
            )
            
            # Store in Firestore
            await self._store_activity_log(activity_log)
            
            # Process individual activities
            await self._process_individual_activities(student_id, activity_log.activities)
            
            logger.info(f"Activity logged successfully: {activity_log.log_id}")
            return activity_log.log_id
            
        except Exception as e:
            logger.error(f"Failed to log activity for student {student_id}: {e}")
            raise AcademicGuidanceServiceError(f"Activity logging failed: {str(e)}")
    
    async def _student_exists(self, student_id: str) -> bool:
        """Check if student exists in the system."""
        try:
            # This would typically check the users/children collection
            students_ref = self.db.collection("children")
            doc = students_ref.document(student_id).get()
            return doc.exists
        except Exception as e:
            logger.error(f"Error checking student existence: {e}")
            return False
    
    async def _store_activity_log(self, activity_log: StudentActivityLog) -> None:
        """Store activity log in Firestore."""
        collection = self.db.collection(self.collections["student_activities"])
        await collection.document(activity_log.log_id).set(activity_log.model_dump())
    
    async def _process_individual_activities(
        self,
        student_id: str,
        activities: List[Dict[str, Any]]
    ) -> None:
        """Process and store individual activities."""
        for activity in activities:
            activity_type = activity.get("activity_type")
            
            if activity_type == "topic_study":
                await self._store_topic_access(student_id, activity)
            elif activity_type == "quiz_attempt":
                await self._store_quiz_attempt(student_id, activity)
            elif activity_type == "learning_sequence":
                await self._store_learning_sequence(student_id, activity)
    
    async def _store_topic_access(self, student_id: str, activity_data: Dict[str, Any]) -> None:
        """Store topic access record."""
        topic_access = TopicAccess(
            activity_id=f"topic_{uuid.uuid4().hex[:8]}",
            student_id=student_id,
            topic_id=activity_data["topic_id"],
            subject=activity_data["subject"],
            chapter=activity_data.get("chapter"),
            sequence_number=activity_data.get("sequence_number", 0),
            access_time=activity_data.get("access_time", datetime.utcnow()),
            time_spent_minutes=activity_data["time_spent_minutes"],
            completion_percentage=activity_data["completion_percentage"],
            activity_type=activity_data["activity_type"]
        )
        
        collection = self.db.collection(self.collections["topic_accesses"])
        await collection.document(topic_access.activity_id).set(topic_access.model_dump())
    
    async def _store_quiz_attempt(self, student_id: str, activity_data: Dict[str, Any]) -> None:
        """Store quiz attempt record."""
        quiz_attempt = QuizAttempt(
            attempt_id=f"quiz_{uuid.uuid4().hex[:8]}",
            student_id=student_id,
            quiz_id=activity_data["quiz_id"],
            subject=activity_data["subject"],
            topic_id=activity_data["topic_id"],
            difficulty=activity_data["difficulty"],
            start_time=activity_data["start_time"],
            end_time=activity_data["end_time"],
            total_time_minutes=activity_data["total_time_minutes"],
            total_questions=activity_data["total_questions"],
            attempted_questions=activity_data["attempted_questions"],
            correct_answers=activity_data["correct_answers"],
            score_percentage=activity_data["score_percentage"]
        )
        
        collection = self.db.collection(self.collections["quiz_attempts"])
        await collection.document(quiz_attempt.attempt_id).set(quiz_attempt.model_dump())
        
        # Store question errors if provided
        for error_data in activity_data.get("question_errors", []):
            await self._store_question_error(quiz_attempt.attempt_id, error_data)
    
    async def _store_question_error(self, attempt_id: str, error_data: Dict[str, Any]) -> None:
        """Store question error record."""
        question_error = QuestionError(
            error_id=f"error_{uuid.uuid4().hex[:8]}",
            attempt_id=attempt_id,
            question_number=error_data["question_number"],
            error_type=error_data["error_type"],
            error_description=error_data["error_description"],
            student_answer=error_data["student_answer"],
            correct_answer=error_data["correct_answer"],
            time_spent_seconds=error_data["time_spent_seconds"],
            confidence_level=error_data.get("confidence_level")
        )
        
        collection = self.db.collection(self.collections["question_errors"])
        await collection.document(question_error.error_id).set(question_error.model_dump())
    
    async def _store_learning_sequence(self, student_id: str, activity_data: Dict[str, Any]) -> None:
        """Store learning sequence record."""
        learning_sequence = LearningSequence(
            sequence_id=f"seq_{uuid.uuid4().hex[:8]}",
            student_id=student_id,
            session_date=activity_data["session_date"],
            session_duration_minutes=activity_data["session_duration_minutes"],
            topic_sequence=activity_data["topic_sequence"],
            subject_transitions=activity_data.get("subject_transitions", []),
            completion_rates=activity_data.get("completion_rates", {})
        )
        
        collection = self.db.collection(self.collections["learning_sequences"])
        await collection.document(learning_sequence.sequence_id).set(learning_sequence.model_dump())
    
    async def analyze_student_learning(
        self,
        student_id: str,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze student learning data and generate insights.
        
        Args:
            student_id: Student identifier
            force_refresh: Force new analysis even if cached
            
        Returns:
            Dictionary containing analysis results
            
        Raises:
            StudentNotFoundError: If student doesn't exist
        """
        logger.info(f"Analyzing learning for student: {student_id}")
        
        try:
            # Check if student exists
            if not await self._student_exists(student_id):
                raise StudentNotFoundError(f"Student not found: {student_id}")
            
            # Check for cached analysis
            if not force_refresh:
                cached_analysis = await self._get_cached_analysis(student_id)
                if cached_analysis:
                    logger.info(f"Returning cached analysis for student: {student_id}")
                    return cached_analysis
            
            # Retrieve student data
            topic_accesses = await self._get_student_topic_accesses(student_id)
            quiz_attempts = await self._get_student_quiz_attempts(student_id)
            learning_sequences = await self._get_student_learning_sequences(student_id)
            
            # Perform analysis if enough data
            if len(topic_accesses) + len(quiz_attempts) < self.analysis_threshold:
                logger.warning(f"Insufficient data for analysis: {student_id}")
                return {
                    "status": "insufficient_data",
                    "message": "Need more learning activities for analysis",
                    "min_activities": self.analysis_threshold,
                    "current_activities": len(topic_accesses) + len(quiz_attempts)
                }
            
            # Generate learning patterns
            learning_patterns = await learning_analysis_service.analyze_learning_patterns(
                student_id, topic_accesses, quiz_attempts, learning_sequences
            )
            
            # Identify knowledge gaps
            knowledge_gaps = await learning_analysis_service.identify_knowledge_gaps(
                student_id, quiz_attempts, topic_accesses
            )
            
            # Identify learning strengths
            learning_strengths = await learning_analysis_service.identify_learning_strengths(
                student_id, quiz_attempts, topic_accesses
            )
            
            # Analyze overall progress
            progress_data = learning_analysis_service.analyze_learning_progress(
                student_id, topic_accesses, quiz_attempts
            )
            
            # Generate recommendations
            recommendations = await recommendation_engine.generate_recommendations(
