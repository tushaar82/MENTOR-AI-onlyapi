"""
Recommendation Engine for AI-Powered Academic Guidance System

This service generates personalized recommendations for students based on their
learning patterns, knowledge gaps, strengths, and progress analysis.
It uses rule-based logic and AI to suggest optimal learning paths.

Features:
- Personalized learning path recommendations
- Resource suggestions based on learning style
- Prerequisite topic recommendations
- Study strategy recommendations
- Time allocation suggestions
- Adaptive difficulty progression

Author: Mentor AI Team
Version: 1.0.0
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from collections import defaultdict
import json

from models.learning_analytics_models import (
    LearningPattern, KnowledgeGap, LearningStrength, Recommendation,
    RecommendationType, DifficultyLevel
)
# from services.learning_analysis_service import LearningAnalysisService
# Removed circular dependency - not needed in this module

# Configure logging
logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Engine for generating personalized learning recommendations.
    
    This service analyzes student data to generate actionable recommendations
    that help students improve their learning outcomes.
    """
    
    def __init__(self):
        """Initialize the recommendation engine."""
        logger.info("Initializing RecommendationEngine")
        
        # Recommendation parameters
        self.max_recommendations_per_type = 3
        self.recommendation_validity_days = 14
        self.urgency_thresholds = {
            "critical_gap": 3,  # days
            "declining_performance": 7,
            "missed_prerequisites": 5
        }
        
        # Resource mapping (would typically come from a database)
        self.resource_library = {
            "video": {
                "khan_academy": "https://khanacademy.org",
                "youtube_education": "https://youtube.com/education",
                "coursera": "https://coursera.org"
            },
            "practice": {
                "khan_practice": "https://khanacademy.org/math",
                "brilliant": "https://brilliant.org",
                "ixl": "https://ixl.com"
            },
            "reading": {
                "ncert": "https://ncert.nic.in",
                "mit_opencourseware": "https://ocw.mit.edu",
                "textbook_solutions": "https://chegg.com"
            },
            "interactive": {
                "phet_simulations": "https://phet.colorado.edu",
                "geogebra": "https://geogebra.org",
                "desmos": "https://desmos.com"
            }
        }
    
    async def generate_recommendations(
        self,
        student_id: str,
        learning_patterns: List[LearningPattern],
        knowledge_gaps: List[KnowledgeGap],
        learning_strengths: List[LearningStrength],
        progress_data: Dict[str, Any]
    ) -> List[Recommendation]:
        """
        Generate comprehensive recommendations for a student.
        
        Args:
            student_id: Student identifier
            learning_patterns: Identified learning patterns
            knowledge_gaps: Knowledge gaps to address
            learning_strengths: Student's learning strengths
            progress_data: Overall progress analysis
            
        Returns:
            List of personalized recommendations
        """
        logger.info(f"Generating recommendations for student: {student_id}")
        
        recommendations = []
        
        # Priority 1: Address critical knowledge gaps
        gap_recommendations = self._generate_gap_recommendations(
            student_id, knowledge_gaps
        )
        recommendations.extend(gap_recommendations)
        
        # Priority 2: Address learning patterns
        pattern_recommendations = self._generate_pattern_recommendations(
            student_id, learning_patterns
        )
        recommendations.extend(pattern_recommendations)
        
        # Priority 3: Leverage learning strengths
        strength_recommendations = self._generate_strength_recommendations(
            student_id, learning_strengths
        )
        recommendations.extend(strength_recommendations)
        
        # Priority 4: Study strategy recommendations
        strategy_recommendations = self._generate_strategy_recommendations(
            student_id, learning_patterns, progress_data
        )
        recommendations.extend(strategy_recommendations)
        
        # Priority 5: Time allocation recommendations
        time_recommendations = self._generate_time_recommendations(
            student_id, progress_data
        )
        recommendations.extend(time_recommendations)
        
        # Sort by priority and limit recommendations
        recommendations = self._prioritize_recommendations(recommendations)
        
        logger.info(f"Generated {len(recommendations)} recommendations for student: {student_id}")
        return recommendations
    
    def _generate_gap_recommendations(
        self,
        student_id: str,
        knowledge_gaps: List[KnowledgeGap]
    ) -> List[Recommendation]:
        """Generate recommendations to address knowledge gaps."""
        recommendations = []
        
        # Sort gaps by severity
        sorted_gaps = sorted(
            knowledge_gaps,
            key=lambda gap: {"critical": 3, "moderate": 2, "minor": 1}[gap.severity],
            reverse=True
        )
        
        for gap in sorted_gaps[:self.max_recommendations_per_type]:
            # Determine priority based on severity
            priority_map = {"critical": "urgent", "moderate": "high", "minor": "medium"}
            priority = priority_map.get(gap.severity, "medium")
            
            # Generate prerequisite review recommendations
            if gap.prerequisite_topics:
                rec = Recommendation(
                    recommendation_id=f"prereq_{gap.gap_id}_{datetime.utcnow().timestamp()}",
                    student_id=student_id,
                    recommendation_type=RecommendationType.PREREQUISITE_REVIEW,
                    priority=priority,
                    title=f"Review Prerequisites for {gap.topic_id}",
                    description=f"Master the foundational concepts before tackling {gap.topic_id}. "
                              f"These prerequisites are essential for understanding the current topic.",
                    target_topic_id=gap.prerequisite_topics[0] if gap.prerequisite_topics else None,
                    target_subject=gap.subject,
                    estimated_time_hours=gap.estimated_hours_to_close * 0.4,  # 40% for prerequisites
                    resources=self._get_prerequisite_resources(gap.subject, gap.prerequisite_topics),
                    action_steps=[
                        f"Review {prereq} fundamentals" for prereq in gap.prerequisite_topics[:3]
                    ] + [
                        "Complete practice problems on prerequisites",
                        "Take a quick assessment to verify understanding"
                    ],
                    expected_outcome="Strong foundation for tackling current topic gaps",
                    valid_until=datetime.utcnow() + timedelta(days=self.recommendation_validity_days)
                )
                recommendations.append(rec)
            
            # Generate alternative resource recommendations
            rec = Recommendation(
                recommendation_id=f"resource_{gap.gap_id}_{datetime.utcnow().timestamp()}",
                student_id=student_id,
                recommendation_type=RecommendationType.ALTERNATIVE_RESOURCE,
                priority=priority,
                title=f"Alternative Learning Resources for {gap.topic_id}",
                description=f"Try different learning approaches to understand {gap.topic_id}. "
                          f"Since traditional methods aren't working, these resources might help.",
                target_topic_id=gap.topic_id,
                target_subject=gap.subject,
                estimated_time_hours=gap.estimated_hours_to_close * 0.6,  # 60% for alternative resources
                resources=self._get_alternative_resources(gap.subject, gap.topic_id, gap.gap_type),
                action_steps=[
                    "Watch video explanations from different perspectives",
                    "Try interactive simulations",
                    "Work through guided examples",
                    "Practice with immediate feedback"
                ],
                expected_outcome="Improved understanding through diverse learning approaches",
                valid_until=datetime.utcnow() + timedelta(days=self.recommendation_validity_days)
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _generate_pattern_recommendations(
        self,
        student_id: str,
        learning_patterns: List[LearningPattern]
    ) -> List[Recommendation]:
        """Generate recommendations based on learning patterns."""
        recommendations = []
        
        for pattern in learning_patterns:
            if pattern.pattern_type == "rushed_learning":
                rec = Recommendation(
                    recommendation_id=f"pattern_{pattern.pattern_id}_{datetime.utcnow().timestamp()}",
                    student_id=student_id,
                    recommendation_type=RecommendationType.STUDY_STRATEGY,
                    priority="medium" if pattern.impact_level == "medium" else "high",
                    title="Improve Time Management",
                    description="You're rushing through topics. Allocate more time for deep learning.",
                    target_subject=None,
                    estimated_time_hours=2.0,
                    resources=[
                        {
                            "type": "article",
                            "url": "https://example.com/time-management",
                            "title": "Effective Study Time Management"
                        }
                    ],
                    action_steps=[
                        "Use Pomodoro technique (25 min study, 5 min break)",
                        "Set minimum time goals per topic",
                        "Take short breaks to maintain focus",
                        "Review understanding before moving on"
                    ],
                    expected_outcome="Better comprehension and retention through adequate study time",
                    valid_until=datetime.utcnow() + timedelta(days=self.recommendation_validity_days)
                )
                recommendations.append(rec)
            
            elif pattern.pattern_type == "difficulty_with_basics":
                rec = Recommendation(
                    recommendation_id=f"pattern_{pattern.pattern_id}_{datetime.utcnow().timestamp()}",
                    student_id=student_id,
                    recommendation_type=RecommendationType.PREREQUISITE_REVIEW,
                    priority="high",
                    title="Strengthen Foundation",
                    description="Focus on basic concepts before attempting advanced problems.",
                    target_subject=None,
                    estimated_time_hours=5.0,
                    resources=self._get_foundation_resources(),
                    action_steps=[
                        "Review fundamental concepts",
                        "Practice basic problems first",
                        "Build confidence gradually",
                        "Move to advanced topics only after mastery"
                    ],
                    expected_outcome="Strong foundation enabling better performance on all difficulty levels",
                    valid_until=datetime.utcnow() + timedelta(days=self.recommendation_validity_days)
                )
                recommendations.append(rec)
            
            elif pattern.pattern_type == "inconsistent_effort":
                rec = Recommendation(
                    recommendation_id=f"pattern_{pattern.pattern_id}_{datetime.utcnow().timestamp()}",
                    student_id=student_id,
                    recommendation_type=RecommendationType.STUDY_STRATEGY,
                    priority="medium",
                    title="Maintain Consistent Effort",
                    description="Apply the same focus to medium-difficulty topics as you do to hard ones.",
                    target_subject=None,
                    estimated_time_hours=3.0,
                    resources=[
                        {
                            "type": "article",
                            "url": "https://example.com/consistent-effort",
                            "title": "Building Consistent Study Habits"
                        }
                    ],
                    action_steps=[
                        "Set specific goals for each study session",
                        "Track effort level across different topics",
                        "Apply problem-solving strategies consistently",
                        "Review and adjust approach regularly"
                    ],
                    expected_outcome="Consistent performance across all difficulty levels",
                    valid_until=datetime.utcnow() + timedelta(days=self.recommendation_validity_days)
                )
                recommendations.append(rec)
            
            elif pattern.pattern_type == "frequent_subject_switching":
                rec = Recommendation(
                    recommendation_id=f"pattern_{pattern.pattern_id}_{datetime.utcnow().timestamp()}",
                    student_id=student_id,
                    recommendation_type=RecommendationType.STUDY_STRATEGY,
                    priority="medium",
                    title="Focus on Single Subject Sessions",
                    description="Dedicate study sessions to one subject for deeper learning.",
                    target_subject=None,
                    estimated_time_hours=2.0,
                    resources=[
                        {
                            "type": "article",
                            "url": "https://example.com/focused-study",
                            "title": "Power of Focused Study Sessions"
                        }
                    ],
                    action_steps=[
                        "Plan subject-specific study days",
                        "Minimize distractions during study",
                        "Use subject blocks of 2-3 hours",
                        "Take subject-focused breaks"
                    ],
                    expected_outcome="Deeper understanding and better knowledge retention",
                    valid_until=datetime.utcnow() + timedelta(days=self.recommendation_validity_days)
                )
                recommendations.append(rec)
        
        return recommendations
    
    def _generate_strength_recommendations(
        self,
        student_id: str,
        learning_strengths: List[LearningStrength]
    ) -> List[Recommendation]:
        """Generate recommendations to leverage learning strengths."""
        recommendations = []
        
        # Sort strengths by consistency score
        sorted_strengths = sorted(
            learning_strengths,
            key=lambda strength: strength.consistency_score,
            reverse=True
        )
        
        for strength in sorted_strengths[:2]:  # Top 2 strengths
            if strength.strength_type == "application":
                rec = Recommendation(
                    recommendation_id=f"strength_{strength.strength_id}_{datetime.utcnow().timestamp()}",
                    student_id=student_id,
                    recommendation_type=RecommendationType.PRACTICE_MORE,
                    priority="low",
                    title=f"Apply Advanced {strength.subject} Problems",
                    description="Use your strong application skills to tackle challenging problems.",
                    target_topic_id=strength.topic_id,
                    target_subject=strength.subject,
                    estimated_time_hours=4.0,
                    resources=self._get_advanced_practice_resources(strength.subject),
                    action_steps=[
                        "Attempt competition-level problems",
                        "Try real-world applications",
                        "Teach concepts to others",
                        "Explore advanced topics"
                    ],
                    expected_outcome="Excellence in advanced applications and competitive exams",
                    valid_until=datetime.utcnow() + timedelta(days=self.recommendation_validity_days)
                )
                recommendations.append(rec)
            
            elif strength.strength_type == "procedural":
                rec = Recommendation(
                    recommendation_id=f"strength_{strength.strength_id}_{datetime.utcnow().timestamp()}",
                    student_id=student_id,
                    recommendation_type=RecommendationType.PRACTICE_MORE,
                    priority="low",
                    title=f"Master Complex Procedures in {strength.subject}",
                    description="Your procedural skills are excellent - tackle complex multi-step problems.",
                    target_topic_id=strength.topic_id,
                    target_subject=strength.subject,
                    estimated_time_hours=3.0,
                    resources=self._get_procedural_resources(strength.subject),
                    action_steps=[
                        "Practice multi-step problems",
                        "Create procedure checklists",
                        "Time yourself for efficiency",
                        "Document problem-solving approaches"
                    ],
                    expected_outcome="Mastery of complex procedures and problem-solving techniques",
                    valid_until=datetime.utcnow() + timedelta(days=self.recommendation_validity_days)
                )
                recommendations.append(rec)
        
        return recommendations
    
    def _generate_strategy_recommendations(
        self,
        student_id: str,
        learning_patterns: List[LearningPattern],
        progress_data: Dict[str, Any]
    ) -> List[Recommendation]:
        """Generate study strategy recommendations."""
        recommendations = []
        
        # Analyze study streak
        streak_data = progress_data.get("study_streak", {})
        current_streak = streak_data.get("current_streak", 0)
        
        if current_streak < 3:
            rec = Recommendation(
                recommendation_id=f"streak_{student_id}_{datetime.utcnow().timestamp()}",
                student_id=student_id,
                recommendation_type=RecommendationType.STUDY_STRATEGY,
                priority="medium",
                title="Build Consistent Study Habits",
                description="Establish a daily study routine to build momentum and retention.",
                target_subject=None,
                estimated_time_hours=1.0,
                resources=[
                    {
                        "type": "article",
                        "url": "https://example.com/study-habits",
                        "title": "Building Effective Study Habits"
                    }
                ],
                action_steps=[
                    "Set fixed study times daily",
                    "Start with 30-minute sessions",
                    "Gradually increase study duration",
                    "Track daily progress"
                ],
                expected_outcome="Consistent learning habits and improved knowledge retention",
                valid_until=datetime.utcnow() + timedelta(days=self.recommendation_validity_days)
            )
            recommendations.append(rec)
        
        # Analyze performance trend
        performance_metrics = progress_data.get("performance_metrics", {})
        trend = performance_metrics.get("recent_trend", "stable")
        
        if trend == "declining":
            rec = Recommendation(
                recommendation_id=f"trend_{student_id}_{datetime.utcnow().timestamp()}",
                student_id=student_id,
                recommendation_type=RecommendationType.STUDY_STRATEGY,
                priority="high",
                title="Address Performance Decline",
                description="Your recent performance shows a declining trend. Let's address this quickly.",
                target_subject=None,
                estimated_time_hours=3.0,
                resources=[
                    {
                        "type": "article",
                        "url": "https://example.com/performance-recovery",
                        "title": "Recovering from Performance Decline"
                    }
                ],
                action_steps=[
                    "Review recent mistakes",
                    "Identify knowledge gaps",
                    "Seek help on difficult topics",
                    "Adjust study strategies"
                ],
                expected_outcome="Reversed performance decline and renewed improvement",
                valid_until=datetime.utcnow() + timedelta(days=self.recommendation_validity_days)
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _generate_time_recommendations(
        self,
        student_id: str,
        progress_data: Dict[str, Any]
    ) -> List[Recommendation]:
        """Generate time allocation recommendations."""
        recommendations = []
        
        time_metrics = progress_data.get("time_metrics", {})
        avg_session_time = time_metrics.get("average_session_minutes", 0)
        
        if avg_session_time < 30:
            rec = Recommendation(
                recommendation_id=f"time_{student_id}_{datetime.utcnow().timestamp()}",
                student_id=student_id,
                recommendation_type=RecommendationType.TIME_ALLOCATION,
                priority="medium",
                title="Increase Study Session Duration",
                description="Your study sessions are quite short. Try longer sessions for deeper learning.",
                target_subject=None,
                estimated_time_hours=2.0,
                resources=[
                    {
                        "type": "article",
                        "url": "https://example.com/study-duration",
                        "title": "Optimizing Study Session Length"
                    }
                ],
                action_steps=[
                    "Gradually increase session length",
                    "Use 45-60 minute sessions",
                    "Include short breaks",
                    "Focus on one topic per session"
                ],
                expected_outcome="Deeper understanding and better knowledge retention",
                valid_until=datetime.utcnow() + timedelta(days=self.recommendation_validity_days)
            )
            recommendations.append(rec)
        
        elif avg_session_time > 120:
            rec = Recommendation(
                recommendation_id=f"time_{student_id}_{datetime.utcnow().timestamp()}",
                student_id=student_id,
                recommendation_type=RecommendationType.TIME_ALLOCATION,
                priority="medium",
                title="Optimize Study Session Length",
                description="Very long sessions may lead to fatigue. Try shorter, focused sessions.",
                target_subject=None,
                estimated_time_hours=1.0,
                resources=[
                    {
                        "type": "article",
                        "url": "https://example.com/study-breaks",
                        "title": "Power of Strategic Study Breaks"
                    }
                ],
                action_steps=[
                    "Break long sessions into 45-minute blocks",
                    "Take 10-15 minute breaks",
                    "Switch topics between blocks",
                    "Maintain focus during blocks"
                ],
                expected_outcome="Improved focus and better knowledge retention",
                valid_until=datetime.utcnow() + timedelta(days=self.recommendation_validity_days)
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _get_prerequisite_resources(
        self,
        subject: str,
        prerequisite_topics: List[str]
    ) -> List[Dict[str, str]]:
        """Get resources for prerequisite topics."""
        resources = []
        
        base_resources = self.resource_library.get("video", {})
        for resource_name, resource_url in base_resources.items():
            resources.append({
                "type": "video",
                "url": resource_url,
                "title": f"{resource_name.replace('_', ' ').title()} - {subject} Prerequisites"
            })
        
        return resources[:3]  # Limit to 3 resources
    
    def _get_alternative_resources(
        self,
        subject: str,
        topic_id: str,
        gap_type: str
    ) -> List[Dict[str, str]]:
        """Get alternative learning resources based on gap type."""
        resources = []
        
        if gap_type == "conceptual":
            # Focus on visual and interactive resources
            resources.extend([
                {
                    "type": "interactive",
                    "url": self.resource_library["interactive"]["phet_simulations"],
                    "title": f"Interactive Simulations for {topic_id}"
                },
                {
                    "type": "video",
                    "url": self.resource_library["video"]["khan_academy"],
                    "title": f"Visual Learning for {topic_id}"
                }
            ])
        elif gap_type == "procedural":
            # Focus on step-by-step resources
            resources.extend([
                {
                    "type": "practice",
                    "url": self.resource_library["practice"]["khan_practice"],
                    "title": f"Step-by-Step Practice for {topic_id}"
                },
                {
                    "type": "reading",
                    "url": self.resource_library["reading"]["ncert"],
                    "title": f"Textbook Examples for {topic_id}"
                }
            ])
        
        return resources[:3]  # Limit to 3 resources
    
    def _get_foundation_resources(self) -> List[Dict[str, str]]:
        """Get resources for strengthening foundations."""
        return [
            {
                "type": "video",
                "url": self.resource_library["video"]["khan_academy"],
                "title": "Foundation Building Videos"
            },
            {
                "type": "practice",
                "url": self.resource_library["practice"]["brilliant"],
                "title": "Foundational Practice Problems"
            },
            {
                "type": "reading",
                "url": self.resource_library["reading"]["ncert"],
                "title": "Basic Concept Reading"
            }
        ]
    
    def _get_advanced_practice_resources(self, subject: str) -> List[Dict[str, str]]:
        """Get advanced practice resources for a subject."""
        return [
            {
                "type": "practice",
                "url": self.resource_library["practice"]["brilliant"],
                "title": f"Advanced {subject} Problems"
            },
            {
                "type": "interactive",
                "url": self.resource_library["interactive"]["geogebra"],
                "title": f"Advanced {subject} Simulations"
            }
        ]
    
    def _get_procedural_resources(self, subject: str) -> List[Dict[str, str]]:
        """Get procedural learning resources for a subject."""
        return [
            {
                "type": "practice",
                "url": self.resource_library["practice"]["ixl"],
                "title": f"Procedural {subject} Practice"
            },
            {
                "type": "video",
                "url": self.resource_library["video"]["youtube_education"],
                "title": f"Step-by-Step {subject} Solutions"
            }
        ]
    
    def _prioritize_recommendations(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """Prioritize recommendations by urgency and impact."""
        # Define priority order
        priority_order = {"urgent": 4, "high": 3, "medium": 2, "low": 1}
        
        # Sort by priority
        sorted_recommendations = sorted(
            recommendations,
            key=lambda rec: priority_order.get(rec.priority, 0),
            reverse=True
        )
        
        # Limit total recommendations
        max_total = 8
        return sorted_recommendations[:max_total]


# Global service instance
recommendation_engine = RecommendationEngine()