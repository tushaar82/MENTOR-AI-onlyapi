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
                student_id, learning_patterns, knowledge_gaps, learning_strengths, progress_data
            )
            
            # Compile analysis results
            analysis_results = {
                "student_id": student_id,
                "analysis_timestamp": datetime.utcnow(),
                "status": "completed",
                "learning_patterns": [pattern.model_dump() for pattern in learning_patterns],
                "knowledge_gaps": [gap.model_dump() for gap in knowledge_gaps],
                "learning_strengths": [strength.model_dump() for strength in learning_strengths],
                "progress_data": progress_data,
                "recommendations": [rec.model_dump() for rec in recommendations],
                "data_summary": {
                    "topic_accesses": len(topic_accesses),
                    "quiz_attempts": len(quiz_attempts),
                    "learning_sequences": len(learning_sequences),
                    "total_activities": len(topic_accesses) + len(quiz_attempts) + len(learning_sequences)
                }
            }
            
            # Store analysis results
            await self._store_analysis_results(student_id, analysis_results)
            
            # Store individual components
            await self._store_learning_patterns(student_id, learning_patterns)
            await self._store_knowledge_gaps(student_id, knowledge_gaps)
            await self._store_learning_strengths(student_id, learning_strengths)
            await self._store_recommendations(student_id, recommendations)
            await self._store_learning_progress(student_id, progress_data)
            
            logger.info(f"Analysis completed for student: {student_id}")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Failed to analyze learning for student {student_id}: {e}")
            raise AcademicGuidanceServiceError(f"Analysis failed: {str(e)}")
    
    async def _get_cached_analysis(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis if available."""
        try:
            # Check for recent analysis
            cache_cutoff = datetime.utcnow() - timedelta(hours=self.recommendation_cache_hours)
            
            analysis_ref = self.db.collection("student_analysis_cache").document(student_id)
            doc = await analysis_ref.get()
            
            if doc.exists:
                analysis_data = doc.to_dict()
                cached_at = analysis_data.get("cached_at")
                
                if cached_at and cached_at > cache_cutoff:
                    return analysis_data.get("analysis_results")
            
            return None
        except Exception as e:
            logger.error(f"Error getting cached analysis: {e}")
            return None
    
    async def _store_analysis_results(self, student_id: str, analysis_results: Dict[str, Any]) -> None:
        """Store analysis results in cache."""
        cache_data = {
            "student_id": student_id,
            "cached_at": datetime.utcnow(),
            "analysis_results": analysis_results
        }
        
        cache_ref = self.db.collection("student_analysis_cache").document(student_id)
        await cache_ref.set(cache_data)
    
    async def _store_learning_patterns(
        self,
        student_id: str,
        learning_patterns: List[LearningPattern]
    ) -> None:
        """Store learning patterns in Firestore."""
        collection = self.db.collection(self.collections["learning_patterns"])
        
        for pattern in learning_patterns:
            await collection.document(pattern.pattern_id).set(pattern.model_dump())
    
    async def _store_knowledge_gaps(
        self,
        student_id: str,
        knowledge_gaps: List[KnowledgeGap]
    ) -> None:
        """Store knowledge gaps in Firestore."""
        collection = self.db.collection(self.collections["knowledge_gaps"])
        
        for gap in knowledge_gaps:
            await collection.document(gap.gap_id).set(gap.model_dump())
    
    async def _store_learning_strengths(
        self,
        student_id: str,
        learning_strengths: List[LearningStrength]
    ) -> None:
        """Store learning strengths in Firestore."""
        collection = self.db.collection(self.collections["learning_strengths"])
        
        for strength in learning_strengths:
            await collection.document(strength.strength_id).set(strength.model_dump())
    
    async def _store_recommendations(
        self,
        student_id: str,
        recommendations: List[Recommendation]
    ) -> None:
        """Store recommendations in Firestore."""
        collection = self.db.collection(self.collections["recommendations"])
        
        # Clear old recommendations first
        old_recs = collection.where(
            filter=FieldFilter("student_id", "==", student_id)
        ).stream()
        
        for doc in old_recs:
            await doc.reference.delete()
        
        # Store new recommendations
        for rec in recommendations:
            await collection.document(rec.recommendation_id).set(rec.model_dump())
    
    async def _store_learning_progress(
        self,
        student_id: str,
        progress_data: Dict[str, Any]
    ) -> None:
        """Store learning progress in Firestore."""
        # Create progress record for each subject
        for subject in progress_data.get("completion_metrics", {}).get("subjects", {}):
            progress = LearningProgress(
                progress_id=f"progress_{student_id}_{subject}_{int(datetime.utcnow().timestamp())}",
                student_id=student_id,
                subject=subject,
                total_topics=progress_data["completion_metrics"]["subjects"][subject]["total"],
                completed_topics=progress_data["completion_metrics"]["subjects"][subject]["completed"],
                mastered_topics=progress_data["completion_metrics"]["subjects"][subject]["mastered"],
                current_streak_days=progress_data["study_streak"]["current_streak"],
                longest_streak_days=progress_data["study_streak"]["longest_streak"],
                average_session_time=progress_data["time_metrics"]["average_session_minutes"],
                total_study_hours=progress_data["time_metrics"]["total_hours"],
                last_activity=progress_data.get("analyzed_at", datetime.utcnow()),
                progress_percentage=progress_data["completion_metrics"]["subjects"][subject]["progress"]
            )
            
            collection = self.db.collection(self.collections["learning_progress"])
            await collection.document(progress.progress_id).set(progress.model_dump())
    
    async def _get_student_topic_accesses(self, student_id: str, limit: int = 100) -> List[TopicAccess]:
        """Get student's topic access records."""
        try:
            collection = self.db.collection(self.collections["topic_accesses"])
            query = collection.where(
                filter=FieldFilter("student_id", "==", student_id)
            ).order_by("access_time", direction=firestore.Query.DESCENDING).limit(limit)
            
            docs = list(query.stream())
            return [TopicAccess(**doc.to_dict()) for doc in docs]
        except Exception as e:
            logger.error(f"Error getting topic accesses: {e}")
            return []
    
    async def _get_student_quiz_attempts(self, student_id: str, limit: int = 50) -> List[QuizAttempt]:
        """Get student's quiz attempt records."""
        try:
            collection = self.db.collection(self.collections["quiz_attempts"])
            query = collection.where(
                filter=FieldFilter("student_id", "==", student_id)
            ).order_by("start_time", direction=firestore.Query.DESCENDING).limit(limit)
            
            docs = list(query.stream())
            return [QuizAttempt(**doc.to_dict()) for doc in docs]
        except Exception as e:
            logger.error(f"Error getting quiz attempts: {e}")
            return []
    
    async def _get_student_learning_sequences(self, student_id: str, limit: int = 50) -> List[LearningSequence]:
        """Get student's learning sequence records."""
        try:
            collection = self.db.collection(self.collections["learning_sequences"])
            query = collection.where(
                filter=FieldFilter("student_id", "==", student_id)
            ).order_by("session_date", direction=firestore.Query.DESCENDING).limit(limit)
            
            docs = list(query.stream())
            return [LearningSequence(**doc.to_dict()) for doc in docs]
        except Exception as e:
            logger.error(f"Error getting learning sequences: {e}")
            return []
    
    async def get_student_progress_report(
        self,
        student_id: str,
        parent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive progress report for a student.
        
        Args:
            student_id: Student identifier
            parent_id: Parent ID for access control
            
        Returns:
            Comprehensive progress report
            
        Raises:
            StudentNotFoundError: If student doesn't exist
        """
        logger.info(f"Getting progress report for student: {student_id}")
        
        try:
            # Verify access if parent_id provided
            if parent_id and not await self._verify_parent_access(parent_id, student_id):
                raise AcademicGuidanceServiceError("Access denied: Parent-child relationship not verified")
            
            # Check if student exists
            if not await self._student_exists(student_id):
                raise StudentNotFoundError(f"Student not found: {student_id}")
            
            # Get latest analysis
            analysis_data = await self._get_cached_analysis(student_id)
            
            if not analysis_data:
                # Generate new analysis if no cache
                analysis_data = await self.analyze_student_learning(student_id)
            
            # Get recent activities
            recent_activities = await self._get_recent_activities(student_id, limit=10)
            
            # Get current recommendations
            current_recommendations = await self._get_current_recommendations(student_id)
            
            # Compile progress report
            progress_report = {
                "student_id": student_id,
                "report_generated_at": datetime.utcnow(),
                "analysis_summary": {
                    "status": analysis_data.get("status", "unknown"),
                    "learning_patterns_count": len(analysis_data.get("learning_patterns", [])),
                    "knowledge_gaps_count": len(analysis_data.get("knowledge_gaps", [])),
                    "learning_strengths_count": len(analysis_data.get("learning_strengths", [])),
                    "recommendations_count": len(analysis_data.get("recommendations", []))
                },
                "progress_data": analysis_data.get("progress_data", {}),
                "learning_patterns": analysis_data.get("learning_patterns", []),
                "knowledge_gaps": analysis_data.get("knowledge_gaps", []),
                "learning_strengths": analysis_data.get("learning_strengths", []),
                "recommendations": analysis_data.get("recommendations", []),
                "recent_activities": [activity.model_dump() for activity in recent_activities],
                "current_recommendations": [rec.model_dump() for rec in current_recommendations],
                "performance_trends": self._calculate_performance_trends(analysis_data),
                "next_steps": self._generate_next_steps(analysis_data)
            }
            
            logger.info(f"Progress report generated for student: {student_id}")
            return progress_report
            
        except Exception as e:
            logger.error(f"Failed to generate progress report for student {student_id}: {e}")
            raise AcademicGuidanceServiceError(f"Progress report generation failed: {str(e)}")
    
    async def _verify_parent_access(self, parent_id: str, student_id: str) -> bool:
        """Verify parent has access to student data."""
        try:
            # Check parent-child relationship
            parent_ref = self.db.collection("parents").document(parent_id)
            parent_doc = await parent_ref.get()
            
            if not parent_doc.exists:
                return False
            
            parent_data = parent_doc.to_dict()
            children = parent_data.get("children", [])
            
            return student_id in children
        except Exception as e:
            logger.error(f"Error verifying parent access: {e}")
            return False
    
    async def _get_recent_activities(self, student_id: str, limit: int = 10) -> List[StudentActivityLog]:
        """Get recent student activities."""
        try:
            collection = self.db.collection(self.collections["student_activities"])
            query = collection.where(
                filter=FieldFilter("student_id", "==", student_id)
            ).order_by("session_start", direction=firestore.Query.DESCENDING).limit(limit)
            
            docs = list(query.stream())
            return [StudentActivityLog(**doc.to_dict()) for doc in docs]
        except Exception as e:
            logger.error(f"Error getting recent activities: {e}")
            return []
    
    async def _get_current_recommendations(self, student_id: str) -> List[Recommendation]:
        """Get current valid recommendations for student."""
        try:
            collection = self.db.collection(self.collections["recommendations"])
            query = collection.where(
                filter=FieldFilter("student_id", "==", student_id)
            ).where(
                filter=FieldFilter("valid_until", ">", datetime.utcnow())
            ).order_by("priority", direction=firestore.Query.DESCENDING)
            
            docs = list(query.stream())
            return [Recommendation(**doc.to_dict()) for doc in docs]
        except Exception as e:
            logger.error(f"Error getting current recommendations: {e}")
            return []
    
    def _calculate_performance_trends(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance trends from analysis data."""
        progress_data = analysis_data.get("progress_data", {})
        performance_metrics = progress_data.get("performance_metrics", {})
        
        return {
            "trend": performance_metrics.get("recent_trend", "stable"),
            "average_score": performance_metrics.get("average_score", 0),
            "best_score": performance_metrics.get("best_score", 0),
            "total_attempts": performance_metrics.get("total_attempts", 0),
            "score_distribution": performance_metrics.get("score_distribution", {})
        }
    
    def _generate_next_steps(self, analysis_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate next steps based on analysis."""
        next_steps = []
        
        # Priority based on knowledge gaps
        gaps = analysis_data.get("knowledge_gaps", [])
        critical_gaps = [gap for gap in gaps if gap.get("severity") == "critical"]
        
        if critical_gaps:
            next_steps.append({
                "priority": "urgent",
                "action": "Address critical knowledge gaps",
                "description": f"Focus on {len(critical_gaps)} critical knowledge gaps immediately"
            })
        
        # Add recommendation-based next steps
        recommendations = analysis_data.get("recommendations", [])
        high_priority_recs = [rec for rec in recommendations if rec.get("priority") in ["urgent", "high"]]
        
        if high_priority_recs:
            next_steps.append({
                "priority": "high",
                "action": "Follow high-priority recommendations",
                "description": f"Implement {len(high_priority_recs)} high-priority recommendations"
            })
        
        # Add strength-based next steps
        strengths = analysis_data.get("learning_strengths", [])
        if strengths:
            next_steps.append({
                "priority": "medium",
                "action": "Leverage learning strengths",
                "description": f"Use your {len(strengths)} identified strengths to tackle advanced topics"
            })
        
        return next_steps
    
    async def get_guidance_insights(
        self,
        student_id: str,
        insight_type: Optional[str] = None,
        parent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get specific guidance insights for a student.
        
        Args:
            student_id: Student identifier
            insight_type: Type of insight (patterns, gaps, strengths, recommendations)
            parent_id: Parent ID for access control
            
        Returns:
            Specific guidance insights
        """
        logger.info(f"Getting guidance insights for student: {student_id}, type: {insight_type}")
        
        try:
            # Verify access if parent_id provided
            if parent_id and not await self._verify_parent_access(parent_id, student_id):
                raise AcademicGuidanceServiceError("Access denied: Parent-child relationship not verified")
            
            # Get latest analysis
            analysis_data = await self._get_cached_analysis(student_id)
            
            if not analysis_data:
                # Generate new analysis if no cache
                analysis_data = await self.analyze_student_learning(student_id)
            
            # Filter insights based on type
            if insight_type == "patterns":
                insights = {
                    "insight_type": "learning_patterns",
                    "data": analysis_data.get("learning_patterns", []),
                    "summary": f"Identified {len(analysis_data.get('learning_patterns', []))} learning patterns"
                }
            elif insight_type == "gaps":
                insights = {
                    "insight_type": "knowledge_gaps",
                    "data": analysis_data.get("knowledge_gaps", []),
                    "summary": f"Identified {len(analysis_data.get('knowledge_gaps', []))} knowledge gaps"
                }
            elif insight_type == "strengths":
                insights = {
                    "insight_type": "learning_strengths",
                    "data": analysis_data.get("learning_strengths", []),
                    "summary": f"Identified {len(analysis_data.get('learning_strengths', []))} learning strengths"
                }
            elif insight_type == "recommendations":
                insights = {
                    "insight_type": "recommendations",
                    "data": analysis_data.get("recommendations", []),
                    "summary": f"Generated {len(analysis_data.get('recommendations', []))} personalized recommendations"
                }
            else:
                # Return all insights
                insights = {
                    "insight_type": "comprehensive",
                    "learning_patterns": analysis_data.get("learning_patterns", []),
                    "knowledge_gaps": analysis_data.get("knowledge_gaps", []),
                    "learning_strengths": analysis_data.get("learning_strengths", []),
                    "recommendations": analysis_data.get("recommendations", []),
                    "summary": f"Comprehensive insights with {len(analysis_data.get('learning_patterns', []))} patterns, "
                              f"{len(analysis_data.get('knowledge_gaps', []))} gaps, "
                              f"{len(analysis_data.get('learning_strengths', []))} strengths, "
                              f"and {len(analysis_data.get('recommendations', []))} recommendations"
                }
            
            # Add metadata
            insights["metadata"] = {
                "student_id": student_id,
                "generated_at": datetime.utcnow(),
                "data_freshness": analysis_data.get("analysis_timestamp"),
                "total_activities": analysis_data.get("data_summary", {}).get("total_activities", 0)
            }
            
            logger.info(f"Guidance insights generated for student: {student_id}")
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get guidance insights for student {student_id}: {e}")
            raise AcademicGuidanceServiceError(f"Guidance insights retrieval failed: {str(e)}")


# Global service instance
academic_guidance_service = AcademicGuidanceService()