"""
Gemini-based Learning Analysis Service for AI-Powered Academic Guidance System

This service uses Google's Gemini AI to analyze student learning data and identify
patterns, strengths, weaknesses, and knowledge gaps. It replaces sklearn-based
machine learning with AI-powered analysis for more nuanced insights.

Features:
- AI-powered pattern recognition in learning sequences
- Intelligent error pattern analysis
- Advanced performance trend analysis
- AI-driven knowledge gap identification
- Smart learning strength identification
- Context-aware study behavior analysis

Author: Mentor AI Team
Version: 1.0.0
"""

import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from collections import defaultdict, Counter

from models.learning_analytics_models import (
    TopicAccess, QuizAttempt, QuestionError, LearningSequence,
    LearningPattern, KnowledgeGap, LearningStrength, LearningProgress,
    ErrorType, DifficultyLevel, LearningActivityType
)
from services.unified_gemini_config_service import get_unified_gemini_service, GeminiConfig

# Configure logging
logger = logging.getLogger(__name__)


class GeminiLearningAnalysisService:
    """
    Service for analyzing student learning data using Gemini AI.
    
    This service processes various types of learning data to identify patterns,
    strengths, weaknesses, and knowledge gaps using AI-powered analysis
    instead of traditional machine learning algorithms.
    """
    
    def __init__(self, unified_config: Optional[GeminiConfig] = None):
        """Initialize the Gemini-based learning analysis service."""
        logger.info("Initializing GeminiLearningAnalysisService")
        
        # Initialize Gemini service
        self.unified_service = get_unified_gemini_service(config=unified_config)
        
        # Analysis parameters
        self.min_data_points_for_pattern = 5
        self.error_pattern_threshold = 0.6  # 60% occurrence for pattern
        self.strength_confidence_threshold = 0.8
        self.gap_severity_thresholds = {
            "minor": 0.3,    # Below 30% performance
            "moderate": 0.5,  # Below 50% performance
            "critical": 0.7   # Below 30% performance
        }
        
        # AI analysis prompts
        self.pattern_analysis_prompt = """
        You are an expert educational psychologist and learning analyst. Analyze the following student learning data
        to identify meaningful learning patterns. Focus on:
        1. Time management patterns (rushed learning, excessive time, optimal pacing)
        2. Difficulty preference patterns (avoiding certain difficulty levels)
        3. Subject transition patterns (frequent switching, focused study)
        4. Error patterns (consistent mistakes, conceptual issues)
        5. Learning sequence patterns (completion rates, topic ordering)

        Student Data:
        {student_data}

        Provide analysis in JSON format with:
        {{
            "patterns": [
                {{
                    "pattern_type": "pattern_name",
                    "description": "Clear description of the pattern",
                    "confidence_score": 0.0-1.0,
                    "frequency": 0.0-1.0,
                    "impact_level": "low|medium|high",
                    "evidence": ["supporting evidence 1", "supporting evidence 2"]
                }}
            ]
        }}
        """
        
        self.knowledge_gap_prompt = """
        You are an expert educational assessor. Analyze the student's quiz performance and topic access data
        to identify knowledge gaps. Focus on:
        1. Topics with consistently low performance
        2. Conceptual vs procedural gaps
        3. Prerequisite gaps that affect current learning
        4. Severity assessment of each gap

        Student Performance Data:
        {performance_data}

        Provide analysis in JSON format with:
        {{
            "knowledge_gaps": [
                {{
                    "topic_id": "topic_identifier",
                    "gap_type": "conceptual|procedural|prerequisite",
                    "severity": "minor|moderate|critical",
                    "evidence": ["evidence 1", "evidence 2"],
                    "estimated_hours_to_close": 0.0,
                    "prerequisite_topics": ["prereq1", "prereq2"]
                }}
            ]
        }}
        """
        
        self.learning_strengths_prompt = """
        You are an expert educational psychologist. Analyze the student's performance data to identify
        learning strengths. Focus on:
        1. Topics with consistent high performance
        2. Types of strengths (conceptual, procedural, application)
        3. Consistency and reliability of strengths
        4. Mastery level assessment

        Student Performance Data:
        {performance_data}

        Provide analysis in JSON format with:
        {{
            "learning_strengths": [
                {{
                    "topic_id": "topic_identifier",
                    "strength_type": "conceptual|procedural|application",
                    "mastery_level": "developing|proficient|advanced",
                    "evidence": ["evidence 1", "evidence 2"],
                    "consistency_score": 0.0-1.0
                }}
            ]
        }}
        """
    
    async def analyze_learning_patterns(
        self,
        student_id: str,
        topic_accesses: List[TopicAccess],
        quiz_attempts: List[QuizAttempt],
        learning_sequences: List[LearningSequence]
    ) -> List[LearningPattern]:
        """
        Analyze learning patterns using Gemini AI.
        
        Args:
            student_id: Student identifier
            topic_accesses: List of topic access records
            quiz_attempts: List of quiz attempts
            learning_sequences: List of learning sequences
            
        Returns:
            List of identified learning patterns
        """
        logger.info(f"Analyzing learning patterns using Gemini for student: {student_id}")
        
        # Prepare data for Gemini analysis
        student_data = self._prepare_pattern_analysis_data(
            topic_accesses, quiz_attempts, learning_sequences
        )
        
        # Use Gemini for pattern analysis
        try:
            prompt = self.pattern_analysis_prompt.format(student_data=json.dumps(student_data, indent=2))
            
            response = await self.unified_service.generate_content(
                prompt=prompt,
                interaction_type="learning_pattern_analysis",
                user_id=student_id,
                use_cache=True
            )
            
            # Parse Gemini response
            patterns_data = json.loads(response) if isinstance(response, str) else response
            patterns = []
            
            for pattern_data in patterns_data.get("patterns", []):
                pattern = LearningPattern(
                    pattern_id=f"pattern_{datetime.utcnow().timestamp()}_{len(patterns)}",
                    student_id=student_id,
                    pattern_type=pattern_data["pattern_type"],
                    description=pattern_data["description"],
                    confidence_score=pattern_data["confidence_score"],
                    frequency=pattern_data["frequency"],
                    impact_level=pattern_data["impact_level"],
                    detected_at=datetime.utcnow()
                )
                patterns.append(pattern)
            
            logger.info(f"Gemini identified {len(patterns)} learning patterns for student: {student_id}")
            return patterns
            
        except Exception as e:
            logger.error(f"Gemini pattern analysis failed for student {student_id}: {e}")
            # Fallback to rule-based analysis
            return await self._fallback_pattern_analysis(
                student_id, topic_accesses, quiz_attempts, learning_sequences
            )
    
    async def identify_knowledge_gaps(
        self,
        student_id: str,
        quiz_attempts: List[QuizAttempt],
        topic_accesses: List[TopicAccess]
    ) -> List[KnowledgeGap]:
        """
        Identify knowledge gaps using Gemini AI.
        
        Args:
            student_id: Student identifier
            quiz_attempts: List of quiz attempts
            topic_accesses: List of topic access records
            
        Returns:
            List of identified knowledge gaps
        """
        logger.info(f"Identifying knowledge gaps using Gemini for student: {student_id}")
        
        # Prepare performance data for Gemini analysis
        performance_data = self._prepare_performance_data(quiz_attempts, topic_accesses)
        
        try:
            prompt = self.knowledge_gap_prompt.format(performance_data=json.dumps(performance_data, indent=2))
            
            response = await self.unified_service.generate_content(
                prompt=prompt,
                interaction_type="knowledge_gap_analysis",
                user_id=student_id,
                use_cache=True
            )
            
            # Parse Gemini response
            gaps_data = json.loads(response) if isinstance(response, str) else response
            gaps = []
            
            for gap_data in gaps_data.get("knowledge_gaps", []):
                # Find corresponding topic access for subject info
                topic_info = next(
                    (access for access in topic_accesses if access.topic_id == gap_data["topic_id"]),
                    None
                )
                
                if topic_info:
                    gap = KnowledgeGap(
                        gap_id=f"gap_{gap_data['topic_id']}_{datetime.utcnow().timestamp()}",
                        student_id=student_id,
                        topic_id=gap_data["topic_id"],
                        subject=topic_info.subject,
                        gap_type=gap_data["gap_type"],
                        severity=gap_data["severity"],
                        evidence=gap_data["evidence"],
                        estimated_hours_to_close=gap_data["estimated_hours_to_close"],
                        prerequisite_topics=gap_data["prerequisite_topics"]
                    )
                    gaps.append(gap)
            
            logger.info(f"Gemini identified {len(gaps)} knowledge gaps for student: {student_id}")
            return gaps
            
        except Exception as e:
            logger.error(f"Gemini knowledge gap analysis failed for student {student_id}: {e}")
            # Fallback to rule-based analysis
            return await self._fallback_knowledge_gap_analysis(student_id, quiz_attempts, topic_accesses)
    
    async def identify_learning_strengths(
        self,
        student_id: str,
        quiz_attempts: List[QuizAttempt],
        topic_accesses: List[TopicAccess]
    ) -> List[LearningStrength]:
        """
        Identify learning strengths using Gemini AI.
        
        Args:
            student_id: Student identifier
            quiz_attempts: List of quiz attempts
            topic_accesses: List of topic access records
            
        Returns:
            List of identified learning strengths
        """
        logger.info(f"Identifying learning strengths using Gemini for student: {student_id}")
        
        # Prepare performance data for Gemini analysis
        performance_data = self._prepare_performance_data(quiz_attempts, topic_accesses)
        
        try:
            prompt = self.learning_strengths_prompt.format(performance_data=json.dumps(performance_data, indent=2))
            
            response = await self.unified_service.generate_content(
                prompt=prompt,
                interaction_type="learning_strength_analysis",
                user_id=student_id,
                use_cache=True
            )
            
            # Parse Gemini response
            strengths_data = json.loads(response) if isinstance(response, str) else response
            strengths = []
            
            for strength_data in strengths_data.get("learning_strengths", []):
                # Find corresponding topic access for subject info
                topic_info = next(
                    (access for access in topic_accesses if access.topic_id == strength_data["topic_id"]),
                    None
                )
                
                if topic_info:
                    strength = LearningStrength(
                        strength_id=f"strength_{strength_data['topic_id']}_{datetime.utcnow().timestamp()}",
                        student_id=student_id,
                        topic_id=strength_data["topic_id"],
                        subject=topic_info.subject,
                        strength_type=strength_data["strength_type"],
                        mastery_level=strength_data["mastery_level"],
                        evidence=strength_data["evidence"],
                        consistency_score=strength_data["consistency_score"]
                    )
                    strengths.append(strength)
            
            logger.info(f"Gemini identified {len(strengths)} learning strengths for student: {student_id}")
            return strengths
            
        except Exception as e:
            logger.error(f"Gemini learning strength analysis failed for student {student_id}: {e}")
            # Fallback to rule-based analysis
            return await self._fallback_learning_strength_analysis(student_id, quiz_attempts, topic_accesses)
    
    def analyze_learning_progress(
        self,
        student_id: str,
        topic_accesses: List[TopicAccess],
        quiz_attempts: List[QuizAttempt]
    ) -> Dict[str, Any]:
        """
        Analyze overall learning progress using traditional methods (enhanced with AI insights).
        
        Args:
            student_id: Student identifier
            topic_accesses: List of topic access records
            quiz_attempts: List of quiz attempts
            
        Returns:
            Dictionary containing progress metrics
        """
        logger.info(f"Analyzing learning progress for student: {student_id}")
        
        # Use traditional statistical methods for progress metrics
        # (These are more reliable for quantitative metrics)
        
        # Calculate study streak
        streak_data = self._calculate_study_streak(topic_accesses)
        
        # Calculate time metrics
        time_metrics = self._calculate_time_metrics(topic_accesses)
        
        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(quiz_attempts)
        
        # Calculate completion metrics
        completion_metrics = self._calculate_completion_metrics(topic_accesses)
        
        progress_data = {
            "student_id": student_id,
            "study_streak": streak_data,
            "time_metrics": time_metrics,
            "performance_metrics": performance_metrics,
            "completion_metrics": completion_metrics,
            "analyzed_at": datetime.utcnow(),
            "analysis_method": "gemini_enhanced"
        }
        
        logger.info(f"Progress analysis completed for student: {student_id}")
        return progress_data
    
    def _prepare_pattern_analysis_data(
        self,
        topic_accesses: List[TopicAccess],
        quiz_attempts: List[QuizAttempt],
        learning_sequences: List[LearningSequence]
    ) -> Dict[str, Any]:
        """Prepare student data for Gemini pattern analysis."""
        return {
            "topic_accesses": [
                {
                    "topic_id": access.topic_id,
                    "subject": access.subject,
                    "time_spent_minutes": access.time_spent_minutes,
                    "completion_percentage": access.completion_percentage,
                    "access_time": access.access_time.isoformat(),
                    "sequence_number": access.sequence_number
                }
                for access in topic_accesses
            ],
            "quiz_attempts": [
                {
                    "topic_id": attempt.topic_id,
                    "subject": attempt.subject,
                    "difficulty": attempt.difficulty,
                    "score_percentage": attempt.score_percentage,
                    "total_time_minutes": attempt.total_time_minutes,
                    "attempted_questions": attempt.attempted_questions,
                    "correct_answers": attempt.correct_answers
                }
                for attempt in quiz_attempts
            ],
            "learning_sequences": [
                {
                    "session_date": sequence.session_date.isoformat(),
                    "session_duration_minutes": sequence.session_duration_minutes,
                    "topic_sequence": sequence.topic_sequence,
                    "subject_transitions": sequence.subject_transitions,
                    "completion_rates": sequence.completion_rates
                }
                for sequence in learning_sequences
            ]
        }
    
    def _prepare_performance_data(
        self,
        quiz_attempts: List[QuizAttempt],
        topic_accesses: List[TopicAccess]
    ) -> Dict[str, Any]:
        """Prepare performance data for Gemini analysis."""
        # Group quiz attempts by topic
        topic_performance = defaultdict(list)
        for attempt in quiz_attempts:
            topic_performance[attempt.topic_id].append({
                "score_percentage": attempt.score_percentage,
                "difficulty": attempt.difficulty,
                "subject": attempt.subject,
                "total_time_minutes": attempt.total_time_minutes,
                "attempted_questions": attempt.attempted_questions,
                "correct_answers": attempt.correct_answers
            })
        
        # Add topic access information
        topic_access_info = {}
        for access in topic_accesses:
            topic_access_info[access.topic_id] = {
                "subject": access.subject,
                "time_spent_minutes": access.time_spent_minutes,
                "completion_percentage": access.completion_percentage
            }
        
        return {
            "topic_performance": dict(topic_performance),
            "topic_access_info": topic_access_info,
            "analysis_date": datetime.utcnow().isoformat()
        }
    
    def _calculate_study_streak(self, topic_accesses: List[TopicAccess]) -> Dict[str, Any]:
        """Calculate study streak metrics."""
        if not topic_accesses:
            return {"current_streak": 0, "longest_streak": 0}
        
        # Group accesses by date
        dates = set(access.access_time.date() for access in topic_accesses)
        sorted_dates = sorted(dates)
        
        current_streak = 0
        longest_streak = 0
        temp_streak = 0
        
        # Calculate streaks
        for i, date in enumerate(sorted_dates):
            if i == 0:
                temp_streak = 1
            else:
                # Check if consecutive day
                prev_date = sorted_dates[i-1]
                if (date - prev_date).days == 1:
                    temp_streak += 1
                else:
                    temp_streak = 1
            
            longest_streak = max(longest_streak, temp_streak)
            
            # Check if this is part of current streak (last 7 days)
            if (datetime.utcnow().date() - date).days <= 7:
                current_streak = max(current_streak, temp_streak)
        
        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak
        }
    
    def _calculate_time_metrics(self, topic_accesses: List[TopicAccess]) -> Dict[str, Any]:
        """Calculate time-based metrics."""
        if not topic_accesses:
            return {
                "total_study_minutes": 0,
                "average_session_minutes": 0,
                "total_sessions": 0
            }
        
        from statistics import mean
        
        total_minutes = sum(access.time_spent_minutes for access in topic_accesses)
        
        # Group by session (same day)
        sessions = defaultdict(list)
        for access in topic_accesses:
            sessions[access.access_time.date()].append(access)
        
        session_times = []
        for date, accesses in sessions.items():
            session_time = sum(access.time_spent_minutes for access in accesses)
            session_times.append(session_time)
        
        return {
            "total_study_minutes": total_minutes,
            "total_hours": total_minutes / 60,
            "average_session_minutes": mean(session_times) if session_times else 0,
            "total_sessions": len(sessions)
        }
    
    def _calculate_performance_metrics(self, quiz_attempts: List[QuizAttempt]) -> Dict[str, Any]:
        """Calculate performance-based metrics."""
        if not quiz_attempts:
            return {
                "average_score": 0,
                "best_score": 0,
                "recent_trend": "stable",
                "total_attempts": 0
            }
        
        from statistics import mean
        
        scores = [attempt.score_percentage for attempt in quiz_attempts]
        average_score = mean(scores)
        best_score = max(scores)
        
        # Calculate recent trend (last 5 attempts vs previous)
        if len(scores) >= 10:
            recent_scores = scores[-5:]
            previous_scores = scores[-10:-5]
            recent_avg = mean(recent_scores)
            previous_avg = mean(previous_scores)
            
            if recent_avg > previous_avg + 5:
                trend = "improving"
            elif recent_avg < previous_avg - 5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "average_score": average_score,
            "best_score": best_score,
            "recent_trend": trend,
            "total_attempts": len(quiz_attempts),
            "score_distribution": {
                "excellent": sum(1 for score in scores if score >= 90),
                "good": sum(1 for score in scores if 70 <= score < 90),
                "average": sum(1 for score in scores if 50 <= score < 70),
                "poor": sum(1 for score in scores if score < 50)
            }
        }
    
    def _calculate_completion_metrics(self, topic_accesses: List[TopicAccess]) -> Dict[str, Any]:
        """Calculate completion-based metrics."""
        if not topic_accesses:
            return {
                "total_topics": 0,
                "completed_topics": 0,
                "average_completion": 0
            }
        
        from statistics import mean
        
        completion_rates = [access.completion_percentage for access in topic_accesses]
        completed_count = sum(1 for rate in completion_rates if rate >= 80)
        
        return {
            "total_topics": len(topic_accesses),
            "completed_topics": completed_count,
            "average_completion": mean(completion_rates),
            "completion_distribution": {
                "fully_completed": sum(1 for rate in completion_rates if rate >= 90),
                "mostly_completed": sum(1 for rate in completion_rates if 70 <= rate < 90),
                "partially_completed": sum(1 for rate in completion_rates if 40 <= rate < 70),
                "barely_started": sum(1 for rate in completion_rates if rate < 40)
            }
        }
    
    async def _fallback_pattern_analysis(
        self,
        student_id: str,
        topic_accesses: List[TopicAccess],
        quiz_attempts: List[QuizAttempt],
        learning_sequences: List[LearningSequence]
    ) -> List[LearningPattern]:
        """Fallback pattern analysis using rule-based logic."""
        # Import the original service for fallback
        from services.learning_analysis_service import learning_analysis_service
        
        logger.warning(f"Using fallback pattern analysis for student: {student_id}")
        return await learning_analysis_service.analyze_learning_patterns(
            student_id, topic_accesses, quiz_attempts, learning_sequences
        )
    
    async def _fallback_knowledge_gap_analysis(
        self,
        student_id: str,
        quiz_attempts: List[QuizAttempt],
        topic_accesses: List[TopicAccess]
    ) -> List[KnowledgeGap]:
        """Fallback knowledge gap analysis using rule-based logic."""
        from services.learning_analysis_service import learning_analysis_service
        
        logger.warning(f"Using fallback knowledge gap analysis for student: {student_id}")
        return await learning_analysis_service.identify_knowledge_gaps(
            student_id, quiz_attempts, topic_accesses
        )
    
    async def _fallback_learning_strength_analysis(
        self,
        student_id: str,
        quiz_attempts: List[QuizAttempt],
        topic_accesses: List[TopicAccess]
    ) -> List[LearningStrength]:
        """Fallback learning strength analysis using rule-based logic."""
        from services.learning_analysis_service import learning_analysis_service
        
        logger.warning(f"Using fallback learning strength analysis for student: {student_id}")
        return await learning_analysis_service.identify_learning_strengths(
            student_id, quiz_attempts, topic_accesses
        )


# Global service instance
gemini_learning_analysis_service = GeminiLearningAnalysisService()