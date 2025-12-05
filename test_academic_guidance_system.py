#!/usr/bin/env python3
"""
Test Script for AI-Powered Academic Guidance System

This script tests the complete academic guidance system including:
- Data model validation
- Service functionality
- API endpoint structure
- Integration between components

Usage:
    python3 test_academic_guidance_system.py

Author: Mentor AI Team
Version: 1.0.0
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add project root to path
sys.path.append('.')

from models.learning_analytics_models import (
    TopicAccess, QuizAttempt, QuestionError, LearningSequence,
    StudentActivityLog, LearningPattern, KnowledgeGap,
    LearningStrength, Recommendation, ErrorType, DifficultyLevel,
    LearningActivityType, RecommendationType
)
from services.learning_analysis_service import learning_analysis_service
from services.recommendation_engine import recommendation_engine
from services.academic_guidance_service import academic_guidance_service


class AcademicGuidanceSystemTester:
    """Test class for the academic guidance system."""
    
    def __init__(self):
        """Initialize the test class."""
        self.test_student_id = "test_student_123"
        self.test_parent_id = "test_parent_456"
        self.test_results = []
    
    def log_test_result(self, test_name: str, passed: bool, message: str = ""):
        """Log a test result."""
        status = "PASS" if passed else "FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.utcnow()
        })
        print(f"[{status}] {test_name}: {message}")
    
    def test_data_models(self):
        """Test data model validation."""
        print("\n=== Testing Data Models ===")
        
        try:
            # Test TopicAccess model
            topic_access = TopicAccess(
                activity_id="topic_001",
                student_id=self.test_student_id,
                topic_id="physics_mechanics",
                subject="Physics",
                chapter="Mechanics",
                sequence_number=1,
                access_time=datetime.utcnow(),
                time_spent_minutes=45,
                completion_percentage=80,
                activity_type=LearningActivityType.TOPIC_STUDY
            )
            self.log_test_result("TopicAccess Model", True, "Model validation successful")
            
            # Test QuizAttempt model
            quiz_attempt = QuizAttempt(
                attempt_id="quiz_001",
                student_id=self.test_student_id,
                quiz_id="physics_quiz_001",
                subject="Physics",
                topic_id="physics_mechanics",
                difficulty=DifficultyLevel.MEDIUM,
                start_time=datetime.utcnow() - timedelta(minutes=30),
                end_time=datetime.utcnow(),
                total_time_minutes=30,
                total_questions=10,
                attempted_questions=8,
                correct_answers=6,
                score_percentage=75.0
            )
            self.log_test_result("QuizAttempt Model", True, "Model validation successful")
            
            # Test QuestionError model
            question_error = QuestionError(
                error_id="error_001",
                attempt_id="quiz_001",
                question_number=3,
                error_type=ErrorType.FORMULA_ERROR,
                error_description="Incorrect formula application",
                student_answer="F=ma^2",
                correct_answer="F=ma",
                time_spent_seconds=120,
                confidence_level=0.7
            )
            self.log_test_result("QuestionError Model", True, "Model validation successful")
            
            # Test LearningSequence model
            learning_sequence = LearningSequence(
                sequence_id="seq_001",
                student_id=self.test_student_id,
                session_date=datetime.utcnow().date(),
                session_duration_minutes=60,
                topic_sequence=["physics_kinematics", "physics_mechanics", "chemistry_basics"],
                subject_transitions=[
                    {"from": "Physics", "to": "Physics", "at_topic": "physics_mechanics"},
                    {"from": "Physics", "to": "Physics", "at_topic": "physics_thermodynamics"},
                    {"from": "Physics", "to": "Chemistry", "at_topic": "chemistry_basics"}
                ],
                completion_rates={"physics_kinematics": 90, "physics_mechanics": 70, "chemistry_basics": 50}
            )
            self.log_test_result("LearningSequence Model", True, "Model validation successful")
            
            # Test LearningPattern model
            learning_pattern = LearningPattern(
                pattern_id="pattern_001",
                student_id=self.test_student_id,
                pattern_type="rushed_learning",
                description="Student rushes through topics",
                confidence_score=0.8,
                frequency=0.6,
                impact_level="medium",
                detected_at=datetime.utcnow()
            )
            self.log_test_result("LearningPattern Model", True, "Model validation successful")
            
            # Test KnowledgeGap model
            knowledge_gap = KnowledgeGap(
                gap_id="gap_001",
                student_id=self.test_student_id,
                topic_id="physics_thermodynamics",
                subject="Physics",
                gap_type="conceptual",
                severity="moderate",
                evidence=["Low quiz scores", "Conceptual mistakes"],
                estimated_hours_to_close=5.0,
                prerequisite_topics=["physics_basics", "heat_concepts"]
            )
            self.log_test_result("KnowledgeGap Model", True, "Model validation successful")
            
            # Test LearningStrength model
            learning_strength = LearningStrength(
                strength_id="strength_001",
                student_id=self.test_student_id,
                topic_id="mathematics_algebra",
                subject="Mathematics",
                strength_type="procedural",
                mastery_level="proficient",
                evidence=["High quiz scores", "Consistent performance"],
                consistency_score=0.9
            )
            self.log_test_result("LearningStrength Model", True, "Model validation successful")
            
            # Test Recommendation model
            recommendation = Recommendation(
                recommendation_id="rec_001",
                student_id=self.test_student_id,
                recommendation_type=RecommendationType.PREREQUISITE_REVIEW,
                priority="high",
                title="Review Physics Basics",
                description="Review fundamental physics concepts",
                target_topic_id="physics_basics",
                target_subject="Physics",
                estimated_time_hours=3.0,
                resources=[{"type": "video", "url": "https://example.com", "title": "Physics Basics"}],
                action_steps=["Watch videos", "Practice problems"],
                expected_outcome="Better understanding of physics concepts",
                valid_until=datetime.utcnow() + timedelta(days=14)
            )
            self.log_test_result("Recommendation Model", True, "Model validation successful")
            
        except Exception as e:
            self.log_test_result("Data Models", False, f"Model validation failed: {str(e)}")
    
    def test_learning_analysis_service(self):
        """Test the learning analysis service."""
        print("\n=== Testing Learning Analysis Service ===")
        
        try:
            # Create test data
            topic_accesses = [
                TopicAccess(
                    activity_id="topic_001",
                    student_id=self.test_student_id,
                    topic_id="physics_mechanics",
                    subject="Physics",
                    sequence_number=1,
                    access_time=datetime.utcnow() - timedelta(days=1),
                    time_spent_minutes=30,
                    completion_percentage=80,
                    activity_type=LearningActivityType.TOPIC_STUDY
                ),
                TopicAccess(
                    activity_id="topic_002",
                    student_id=self.test_student_id,
                    topic_id="physics_thermodynamics",
                    subject="Physics",
                    sequence_number=2,
                    access_time=datetime.utcnow() - timedelta(days=2),
                    time_spent_minutes=15,  # Rushed
                    completion_percentage=40,
                    activity_type=LearningActivityType.TOPIC_STUDY
                )
            ]
            
            quiz_attempts = [
                QuizAttempt(
                    attempt_id="quiz_001",
                    student_id=self.test_student_id,
                    quiz_id="physics_quiz_001",
                    subject="Physics",
                    topic_id="physics_mechanics",
                    difficulty=DifficultyLevel.MEDIUM,
                    start_time=datetime.utcnow() - timedelta(days=1, hours=1),
                    end_time=datetime.utcnow() - timedelta(days=1),
                    total_time_minutes=60,
                    total_questions=10,
                    attempted_questions=10,
                    correct_answers=8,
                    score_percentage=80.0
                ),
                QuizAttempt(
                    attempt_id="quiz_002",
                    student_id=self.test_student_id,
                    quiz_id="physics_quiz_002",
                    subject="Physics",
                    topic_id="physics_thermodynamics",
                    difficulty=DifficultyLevel.EASY,
                    start_time=datetime.utcnow() - timedelta(days=2, hours=1),
                    end_time=datetime.utcnow() - timedelta(days=2),
                    total_time_minutes=45,
                    total_questions=10,
                    attempted_questions=10,
                    correct_answers=4,
                    score_percentage=40.0
                )
            ]
            
            learning_sequences = [
                LearningSequence(
                    sequence_id="seq_001",
                    student_id=self.test_student_id,
                    session_date=datetime.utcnow().date(),
                    session_duration_minutes=60,
                    topic_sequence=["physics_mechanics", "physics_thermodynamics"],
                    subject_transitions=[
                        {"from": "Physics", "to": "Physics", "at_topic": "physics_mechanics"},
                        {"from": "Physics", "to": "Physics", "at_topic": "physics_thermodynamics"}
                    ],
                    completion_rates={"physics_mechanics": 80, "physics_thermodynamics": 40}
                )
            ]
            
            # Test learning patterns analysis
            patterns = asyncio.run(learning_analysis_service.analyze_learning_patterns(
                self.test_student_id, topic_accesses, quiz_attempts, learning_sequences
            ))
            self.log_test_result("Learning Patterns Analysis", True, f"Found {len(patterns)} patterns")
            
            # Test knowledge gaps identification
            gaps = asyncio.run(learning_analysis_service.identify_knowledge_gaps(
                self.test_student_id, quiz_attempts, topic_accesses
            ))
            self.log_test_result("Knowledge Gaps Identification", True, f"Found {len(gaps)} gaps")
            
            # Test learning strengths identification
            strengths = asyncio.run(learning_analysis_service.identify_learning_strengths(
                self.test_student_id, quiz_attempts, topic_accesses
            ))
            self.log_test_result("Learning Strengths Identification", True, f"Found {len(strengths)} strengths")
            
            # Test progress analysis
            progress = learning_analysis_service.analyze_learning_progress(
                self.test_student_id, topic_accesses, quiz_attempts
            )
            self.log_test_result("Progress Analysis", True, f"Progress metrics calculated")
            
        except Exception as e:
            self.log_test_result("Learning Analysis Service", False, f"Service test failed: {str(e)}")
    
    def test_recommendation_engine(self):
        """Test the recommendation engine."""
        print("\n=== Testing Recommendation Engine ===")
        
        try:
            # Create test data
            learning_patterns = [
                LearningPattern(
                    pattern_id="pattern_001",
                    student_id=self.test_student_id,
                    pattern_type="rushed_learning",
                    description="Student rushes through topics",
                    confidence_score=0.8,
                    frequency=0.6,
                    impact_level="medium",
                    detected_at=datetime.utcnow()
                )
            ]
            
            knowledge_gaps = [
                KnowledgeGap(
                    gap_id="gap_001",
                    student_id=self.test_student_id,
                    topic_id="physics_thermodynamics",
                    subject="Physics",
                    gap_type="conceptual",
                    severity="moderate",
                    evidence=["Low quiz scores"],
                    estimated_hours_to_close=5.0,
                    prerequisite_topics=["physics_basics"]
                )
            ]
            
            learning_strengths = [
                LearningStrength(
                    strength_id="strength_001",
                    student_id=self.test_student_id,
                    topic_id="mathematics_algebra",
                    subject="Mathematics",
                    strength_type="procedural",
                    mastery_level="proficient",
                    evidence=["High quiz scores"],
                    consistency_score=0.9
                )
            ]
            
            progress_data = {
                "study_streak": {"current_streak": 3, "longest_streak": 7},
                "time_metrics": {"average_session_minutes": 45, "total_hours": 10},
                "performance_metrics": {"average_score": 70, "recent_trend": "stable"},
                "completion_metrics": {"total_topics": 5, "completed_topics": 3}
            }
            
            # Test recommendation generation
            recommendations = asyncio.run(recommendation_engine.generate_recommendations(
                self.test_student_id, learning_patterns, knowledge_gaps, learning_strengths, progress_data
            ))
            self.log_test_result("Recommendation Generation", True, f"Generated {len(recommendations)} recommendations")
            
            # Verify recommendation types
            rec_types = [rec.recommendation_type for rec in recommendations]
            self.log_test_result("Recommendation Types", True, f"Types: {rec_types}")
            
        except Exception as e:
            self.log_test_result("Recommendation Engine", False, f"Engine test failed: {str(e)}")
    
    def test_service_integration(self):
        """Test service integration."""
        print("\n=== Testing Service Integration ===")
        
        try:
            # Test that services can be imported and instantiated
            from services.academic_guidance_service import academic_guidance_service
            self.log_test_result("Service Import", True, "Services imported successfully")
            
            # Test service initialization
            service = academic_guidance_service
            self.log_test_result("Service Initialization", True, "Service initialized successfully")
            
            # Test collection names
            collections = service.collections
            expected_collections = [
                "student_activities", "topic_accesses", "quiz_attempts", 
                "question_errors", "learning_sequences", "learning_patterns",
                "knowledge_gaps", "learning_strengths", "learning_progress", "recommendations"
            ]
            
            missing_collections = [col for col in expected_collections if col not in collections]
            if not missing_collections:
                self.log_test_result("Collection Configuration", True, "All collections configured")
            else:
                self.log_test_result("Collection Configuration", False, f"Missing collections: {missing_collections}")
                
        except Exception as e:
            self.log_test_result("Service Integration", False, f"Integration test failed: {str(e)}")
    
    def test_api_structure(self):
        """Test API endpoint structure."""
        print("\n=== Testing API Structure ===")
        
        try:
            # Test router imports
            from routers.academic_guidance_router import router as guidance_router
            from routers.progress_insights_router import router as insights_router
            self.log_test_result("Router Import", True, "Routers imported successfully")
            
            # Test router configuration
            guidance_routes = [route.path for route in guidance_router.routes]
            insights_routes = [route.path for route in insights_router.routes]
            
            expected_guidance_routes = [
                "/api/guidance/activity/log", "/api/guidance/activity/topic-access", "/api/guidance/activity/quiz-attempt",
                "/api/guidance/activity/learning-sequence", "/api/guidance/analyze/{student_id}"
            ]
            
            expected_insights_routes = [
                "/api/progress/{student_id}", "/api/progress/{student_id}/summary", "/api/progress/insights/{student_id}",
                "/api/progress/insights/{student_id}/patterns", "/api/progress/insights/{student_id}/gaps",
                "/api/progress/insights/{student_id}/strengths", "/api/progress/recommendations/{student_id}"
            ]
            
            missing_guidance = [route for route in expected_guidance_routes if route not in guidance_routes]
            missing_insights = [route for route in expected_insights_routes if route not in insights_routes]
            
            if not missing_guidance:
                self.log_test_result("Guidance Router Routes", True, "All guidance routes configured")
            else:
                self.log_test_result("Guidance Router Routes", False, f"Missing routes: {missing_guidance}")
            
            if not missing_insights:
                self.log_test_result("Insights Router Routes", True, "All insights routes configured")
            else:
                self.log_test_result("Insights Router Routes", False, f"Missing routes: {missing_insights}")
                
        except Exception as e:
            self.log_test_result("API Structure", False, f"API structure test failed: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests."""
        print("Starting AI-Powered Academic Guidance System Tests")
        print("=" * 60)
        
        self.test_data_models()
        self.test_learning_analysis_service()
        self.test_recommendation_engine()
        self.test_service_integration()
        self.test_api_structure()
        
        # Print summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["status"] == "PASS")
        failed = sum(1 for result in self.test_results if result["status"] == "FAIL")
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if failed > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  - {result['test']}: {result['message']}")
        
        return failed == 0


if __name__ == "__main__":
    tester = AcademicGuidanceSystemTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)