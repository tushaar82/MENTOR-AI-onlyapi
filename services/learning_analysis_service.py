"""
Learning Analysis Service for AI-Powered Academic Guidance System

This service processes student learning data to identify patterns, strengths, weaknesses,
and knowledge gaps. It uses statistical analysis and machine learning techniques
to generate insights for personalized recommendations.

Features:
- Pattern recognition in learning sequences
- Error pattern analysis
- Performance trend analysis
- Knowledge gap identification
- Learning strength identification
- Study behavior analysis

Author: Mentor AI Team
Version: 1.0.0
"""

import logging
import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from collections import defaultdict, Counter
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

from models.learning_analytics_models import (
    TopicAccess, QuizAttempt, QuestionError, LearningSequence,
    LearningPattern, KnowledgeGap, LearningStrength, LearningProgress,
    ErrorType, DifficultyLevel, LearningActivityType
)

# Configure logging
logger = logging.getLogger(__name__)


class LearningAnalysisService:
    """
    Service for analyzing student learning data and generating insights.
    
    This service processes various types of learning data to identify patterns,
    strengths, weaknesses, and knowledge gaps that inform personalized
    recommendations.
    """
    
    def __init__(self):
        """Initialize the learning analysis service."""
        logger.info("Initializing LearningAnalysisService")
        
        # Analysis parameters
        self.min_data_points_for_pattern = 5
        self.error_pattern_threshold = 0.6  # 60% occurrence for pattern
        self.strength_confidence_threshold = 0.8
        self.gap_severity_thresholds = {
            "minor": 0.3,    # Below 30% performance
            "moderate": 0.5,  # Below 50% performance
            "critical": 0.7   # Below 30% performance
        }
    
    async def analyze_learning_patterns(
        self,
        student_id: str,
        topic_accesses: List[TopicAccess],
        quiz_attempts: List[QuizAttempt],
        learning_sequences: List[LearningSequence]
    ) -> List[LearningPattern]:
        """
        Analyze learning patterns from student activity data.
        
        Args:
            student_id: Student identifier
            topic_accesses: List of topic access records
            quiz_attempts: List of quiz attempts
            learning_sequences: List of learning sequences
            
        Returns:
            List of identified learning patterns
        """
        logger.info(f"Analyzing learning patterns for student: {student_id}")
        
        patterns = []
        
        # Analyze time management patterns
        time_patterns = self._analyze_time_patterns(topic_accesses, quiz_attempts)
        patterns.extend(time_patterns)
        
        # Analyze difficulty preference patterns
        difficulty_patterns = self._analyze_difficulty_patterns(quiz_attempts)
        patterns.extend(difficulty_patterns)
        
        # Analyze subject transition patterns
        transition_patterns = self._analyze_transition_patterns(learning_sequences)
        patterns.extend(transition_patterns)
        
        # Analyze error patterns
        error_patterns = await self._analyze_error_patterns(student_id, quiz_attempts)
        patterns.extend(error_patterns)
        
        # Analyze learning sequence patterns
        sequence_patterns = self._analyze_sequence_patterns(learning_sequences)
        patterns.extend(sequence_patterns)
        
        logger.info(f"Identified {len(patterns)} learning patterns for student: {student_id}")
        return patterns
    
    def _analyze_time_patterns(
        self,
        topic_accesses: List[TopicAccess],
        quiz_attempts: List[QuizAttempt]
    ) -> List[LearningPattern]:
        """Analyze time management patterns."""
        patterns = []
        
        if not topic_accesses:
            return patterns
        
        # Calculate average time spent per topic
        topic_times = [access.time_spent_minutes for access in topic_accesses]
        avg_time = statistics.mean(topic_times) if topic_times else 0
        
        # Check for rushed learning (significantly below average)
        rushed_threshold = avg_time * 0.5
        rushed_count = sum(1 for time in topic_times if time < rushed_threshold)
        
        if rushed_count > len(topic_times) * 0.3:  # 30% rushed
            patterns.append(LearningPattern(
                pattern_id=f"time_rushed_{datetime.utcnow().timestamp()}",
                student_id=topic_accesses[0].student_id,
                pattern_type="rushed_learning",
                description="Student frequently spends less time than average on topics",
                confidence_score=min(rushed_count / len(topic_times), 1.0),
                frequency=rushed_count / len(topic_times),
                impact_level="medium" if rushed_count / len(topic_times) < 0.5 else "high",
                detected_at=datetime.utcnow()
            ))
        
        # Check for excessive time (significantly above average)
        excessive_threshold = avg_time * 2.0
        excessive_count = sum(1 for time in topic_times if time > excessive_threshold)
        
        if excessive_count > len(topic_times) * 0.2:  # 20% excessive
            patterns.append(LearningPattern(
                pattern_id=f"time_excessive_{datetime.utcnow().timestamp()}",
                student_id=topic_accesses[0].student_id,
                pattern_type="excessive_time",
                description="Student frequently spends excessive time on topics",
                confidence_score=min(excessive_count / len(topic_times), 1.0),
                frequency=excessive_count / len(topic_times),
                impact_level="medium",
                detected_at=datetime.utcnow()
            ))
        
        return patterns
    
    def _analyze_difficulty_patterns(self, quiz_attempts: List[QuizAttempt]) -> List[LearningPattern]:
        """Analyze difficulty preference patterns."""
        patterns = []
        
        if not quiz_attempts:
            return patterns
        
        # Group by difficulty
        difficulty_scores = defaultdict(list)
        for attempt in quiz_attempts:
            difficulty_scores[attempt.difficulty].append(attempt.score_percentage)
        
        # Check for difficulty avoidance
        for difficulty, scores in difficulty_scores.items():
            if len(scores) >= 3:  # Need at least 3 attempts
                avg_score = statistics.mean(scores)
                
                # Low performance on easy questions suggests conceptual issues
                if difficulty == DifficultyLevel.EASY and avg_score < 70:
                    patterns.append(LearningPattern(
                        pattern_id=f"easy_struggle_{datetime.utcnow().timestamp()}",
                        student_id=quiz_attempts[0].student_id,
                        pattern_type="difficulty_with_basics",
                        description="Student struggles with easy questions, indicating conceptual gaps",
                        confidence_score=0.8,
                        frequency=1.0,
                        impact_level="high",
                        detected_at=datetime.utcnow()
                    ))
                
                # High performance on hard but low on medium suggests inconsistent effort
                elif difficulty == DifficultyLevel.HARD and avg_score > 80:
                    medium_scores = difficulty_scores.get(DifficultyLevel.MEDIUM, [])
                    if medium_scores and statistics.mean(medium_scores) < 60:
                        patterns.append(LearningPattern(
                            pattern_id=f"inconsistent_effort_{datetime.utcnow().timestamp()}",
                            student_id=quiz_attempts[0].student_id,
                            pattern_type="inconsistent_effort",
                            description="Student performs well on hard questions but struggles with medium ones",
                            confidence_score=0.7,
                            frequency=0.8,
                            impact_level="medium",
                            detected_at=datetime.utcnow()
                        ))
        
        return patterns
    
    def _analyze_transition_patterns(self, learning_sequences: List[LearningSequence]) -> List[LearningPattern]:
        """Analyze subject transition patterns."""
        patterns = []
        
        if not learning_sequences:
            return patterns
        
        # Analyze subject switching frequency
        transition_counts = []
        for sequence in learning_sequences:
            transitions = sequence.subject_transitions
            if transitions:
                transition_counts.append(len(transitions))
        
        if transition_counts:
            avg_transitions = statistics.mean(transition_counts)
            
            # High frequency of subject switching
            if avg_transitions > 3:
                patterns.append(LearningPattern(
                    pattern_id=f"frequent_switching_{datetime.utcnow().timestamp()}",
                    student_id=learning_sequences[0].student_id,
                    pattern_type="frequent_subject_switching",
                    description="Student frequently switches between subjects during study sessions",
                    confidence_score=0.8,
                    frequency=1.0,
                    impact_level="medium",
                    detected_at=datetime.utcnow()
                ))
        
        return patterns
    
    async def _analyze_error_patterns(
        self,
        student_id: str,
        quiz_attempts: List[QuizAttempt]
    ) -> List[LearningPattern]:
        """Analyze error patterns in quiz attempts."""
        patterns = []
        
        # This would typically query QuestionError records
        # For now, we'll simulate based on quiz performance
        
        if not quiz_attempts:
            return patterns
        
        # Check for consistent low performance
        recent_attempts = quiz_attempts[-5:]  # Last 5 attempts
        if len(recent_attempts) >= 3:
            avg_score = statistics.mean([attempt.score_percentage for attempt in recent_attempts])
            
            if avg_score < 50:
                patterns.append(LearningPattern(
                    pattern_id=f"consistent_low_performance_{datetime.utcnow().timestamp()}",
                    student_id=student_id,
                    pattern_type="consistent_low_performance",
                    description="Student consistently scores below 50% in recent attempts",
                    confidence_score=0.9,
                    frequency=1.0,
                    impact_level="high",
                    detected_at=datetime.utcnow()
                ))
        
        return patterns
    
    def _analyze_sequence_patterns(self, learning_sequences: List[LearningSequence]) -> List[LearningPattern]:
        """Analyze learning sequence patterns."""
        patterns = []
        
        if not learning_sequences:
            return patterns
        
        # Analyze completion rates across sessions
        completion_rates = []
        for sequence in learning_sequences:
            if sequence.completion_rates:
                avg_completion = statistics.mean(sequence.completion_rates.values())
                completion_rates.append(avg_completion)
        
        if completion_rates:
            avg_completion = statistics.mean(completion_rates)
            
            # Low completion rate pattern
            if avg_completion < 60:
                patterns.append(LearningPattern(
                    pattern_id=f"low_completion_{datetime.utcnow().timestamp()}",
                    student_id=learning_sequences[0].student_id,
                    pattern_type="low_completion_rate",
                    description="Student consistently leaves topics incomplete",
                    confidence_score=0.8,
                    frequency=1.0,
                    impact_level="medium",
                    detected_at=datetime.utcnow()
                ))
        
        return patterns
    
    async def identify_knowledge_gaps(
        self,
        student_id: str,
        quiz_attempts: List[QuizAttempt],
        topic_accesses: List[TopicAccess]
    ) -> List[KnowledgeGap]:
        """
        Identify knowledge gaps based on performance data.
        
        Args:
            student_id: Student identifier
            quiz_attempts: List of quiz attempts
            topic_accesses: List of topic access records
            
        Returns:
            List of identified knowledge gaps
        """
        logger.info(f"Identifying knowledge gaps for student: {student_id}")
        
        gaps = []
        
        # Group quiz attempts by topic
        topic_performance = defaultdict(list)
        for attempt in quiz_attempts:
            topic_performance[attempt.topic_id].append(attempt.score_percentage)
        
        # Identify gaps based on performance
        for topic_id, scores in topic_performance.items():
            if len(scores) >= 2:  # Need at least 2 attempts
                avg_score = statistics.mean(scores)
                
                # Determine gap severity
                if avg_score < 30:
                    severity = "critical"
                elif avg_score < 50:
                    severity = "moderate"
                elif avg_score < 70:
                    severity = "minor"
                else:
                    continue  # No gap
                
                # Find corresponding topic access for context
                topic_info = next(
                    (access for access in topic_accesses if access.topic_id == topic_id),
                    None
                )
                
                if topic_info:
                    gaps.append(KnowledgeGap(
                        gap_id=f"gap_{topic_id}_{datetime.utcnow().timestamp()}",
                        student_id=student_id,
                        topic_id=topic_id,
                        subject=topic_info.subject,
                        gap_type="conceptual" if avg_score < 50 else "procedural",
                        severity=severity,
                        evidence=[
                            f"Average quiz score: {avg_score:.1f}%",
                            f"Number of attempts: {len(scores)}",
                            f"Score range: {min(scores):.1f}% - {max(scores):.1f}%"
                        ],
                        estimated_hours_to_close=self._estimate_hours_to_close_gap(avg_score),
                        prerequisite_topics=self._identify_prerequisites(topic_id, topic_info.subject)
                    ))
        
        logger.info(f"Identified {len(gaps)} knowledge gaps for student: {student_id}")
        return gaps
    
    def _estimate_hours_to_close_gap(self, current_score: float) -> float:
        """Estimate hours needed to close a knowledge gap."""
        # Base hours on how far below mastery (80%)
        if current_score >= 80:
            return 0.0
        
        gap_percentage = 80 - current_score
        # Rough estimate: 1 hour per 10% gap
        return max(1.0, gap_percentage / 10)
    
    def _identify_prerequisites(self, topic_id: str, subject: str) -> List[str]:
        """Identify prerequisite topics for a given topic."""
        # This would typically query a knowledge graph or curriculum mapping
        # For now, return common prerequisites based on subject
        prerequisites_map = {
            "Physics": {
                "thermodynamics": ["heat_transfer_basics", "energy_concepts"],
                "electromagnetism": ["electricity_basics", "magnetism_fundamentals"],
                "mechanics": ["kinematics", "forces", "motion"]
            },
            "Chemistry": {
                "organic_chemistry": ["basic_chemistry", "bonding"],
                "physical_chemistry": ["thermodynamics_basics", "kinetics"],
                "inorganic_chemistry": ["periodic_table", "chemical_bonding"]
            },
            "Mathematics": {
                "calculus": ["algebra", "functions", "limits"],
                "trigonometry": ["angles", "triangles", "basic_geometry"],
                "probability": ["statistics_basics", "permutations"]
            }
        }
        
        # Extract topic category from topic_id (simplified)
        topic_category = topic_id.split("_")[-1] if "_" in topic_id else topic_id
        
        return prerequisites_map.get(subject, {}).get(topic_category, [])
    
    async def identify_learning_strengths(
        self,
        student_id: str,
        quiz_attempts: List[QuizAttempt],
        topic_accesses: List[TopicAccess]
    ) -> List[LearningStrength]:
        """
        Identify learning strengths based on performance data.
        
        Args:
            student_id: Student identifier
            quiz_attempts: List of quiz attempts
            topic_accesses: List of topic access records
            
        Returns:
            List of identified learning strengths
        """
        logger.info(f"Identifying learning strengths for student: {student_id}")
        
        strengths = []
        
        # Group quiz attempts by topic
        topic_performance = defaultdict(list)
        for attempt in quiz_attempts:
            topic_performance[attempt.topic_id].append(attempt.score_percentage)
        
        # Identify strengths based on consistent high performance
        for topic_id, scores in topic_performance.items():
            if len(scores) >= 3:  # Need at least 3 attempts
                avg_score = statistics.mean(scores)
                score_std = statistics.stdev(scores) if len(scores) > 1 else 0
                
                # High average score with low variance indicates strength
                if avg_score >= 80 and score_std < 15:
                    # Find corresponding topic access for context
                    topic_info = next(
                        (access for access in topic_accesses if access.topic_id == topic_id),
                        None
                    )
                    
                    if topic_info:
                        # Determine strength type based on performance characteristics
                        strength_type = "application" if avg_score >= 90 else "procedural"
                        mastery_level = "advanced" if avg_score >= 95 else "proficient"
                        
                        strengths.append(LearningStrength(
                            strength_id=f"strength_{topic_id}_{datetime.utcnow().timestamp()}",
                            student_id=student_id,
                            topic_id=topic_id,
                            subject=topic_info.subject,
                            strength_type=strength_type,
                            mastery_level=mastery_level,
                            evidence=[
                                f"Average quiz score: {avg_score:.1f}%",
                                f"Score consistency: ±{score_std:.1f}%",
                                f"Number of attempts: {len(scores)}",
                                f"Best score: {max(scores):.1f}%"
                            ],
                            consistency_score=1.0 - (score_std / 100)  # Normalize to 0-1
                        ))
        
        logger.info(f"Identified {len(strengths)} learning strengths for student: {student_id}")
        return strengths
    
    def analyze_learning_progress(
        self,
        student_id: str,
        topic_accesses: List[TopicAccess],
        quiz_attempts: List[QuizAttempt]
    ) -> Dict[str, Any]:
        """
        Analyze overall learning progress for a student.
        
        Args:
            student_id: Student identifier
            topic_accesses: List of topic access records
            quiz_attempts: List of quiz attempts
            
        Returns:
            Dictionary containing progress metrics
        """
        logger.info(f"Analyzing learning progress for student: {student_id}")
        
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
            "analyzed_at": datetime.utcnow()
        }
        
        logger.info(f"Progress analysis completed for student: {student_id}")
        return progress_data
    
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
            "average_session_minutes": statistics.mean(session_times) if session_times else 0,
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
        
        scores = [attempt.score_percentage for attempt in quiz_attempts]
        average_score = statistics.mean(scores)
        best_score = max(scores)
        
        # Calculate recent trend (last 5 attempts vs previous)
        if len(scores) >= 10:
            recent_scores = scores[-5:]
            previous_scores = scores[-10:-5]
            recent_avg = statistics.mean(recent_scores)
            previous_avg = statistics.mean(previous_scores)
            
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
        
        completion_rates = [access.completion_percentage for access in topic_accesses]
        completed_count = sum(1 for rate in completion_rates if rate >= 80)
        
        return {
            "total_topics": len(topic_accesses),
            "completed_topics": completed_count,
            "average_completion": statistics.mean(completion_rates),
            "completion_distribution": {
                "fully_completed": sum(1 for rate in completion_rates if rate >= 90),
                "mostly_completed": sum(1 for rate in completion_rates if 70 <= rate < 90),
                "partially_completed": sum(1 for rate in completion_rates if 40 <= rate < 70),
                "barely_started": sum(1 for rate in completion_rates if rate < 40)
            }
        }


# Global service instance
learning_analysis_service = LearningAnalysisService()