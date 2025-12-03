#!/usr/bin/env python3
"""
Comprehensive Firestore Database Initialization Script

This script initializes all required Firestore collections for the Mentor AI Platform
based on the models defined in the codebase. It creates collections with proper
structure and sample data for testing.

Usage:
    python scripts/database_manager.py --init          # Initialize all collections
    python scripts/database_manager.py --clear         # Delete all data
    python scripts/database_manager.py --stats         # Show collection stats
    python scripts/database_manager.py --reset         # Clear and reinitialize
    python scripts/database_manager.py --clear --dry-run  # Preview deletion

Author: Mentor AI Team
Version: 2.0.0
"""

import os
import sys
import asyncio
import argparse
import logging
import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Firebase imports
from firebase_admin import firestore
from google.cloud import firestore_v1
from google.api_core.exceptions import GoogleAPICallError

# Project imports
from utils.firebase_config import initialize_firebase, get_firestore_client
from models.database_models import DATABASE_SCHEMAS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Collection definitions based on models
ALL_COLLECTIONS = {
    # Authentication and User Management
    "parents": {
        "description": "Parent user profiles and authentication data",
        "indexes": [
            {"fields": ["email"], "name": "parents_by_email"},
            {"fields": ["phone"], "name": "parents_by_phone"},
            {"fields": ["created_at"], "name": "parents_by_created_at"}
        ]
    },
    "children": {
        "description": "Child/student profiles linked to parents",
        "indexes": [
            {"fields": ["parent_id"], "name": "children_by_parent"},
            {"fields": ["parent_id", "created_at"], "name": "children_by_parent_time"},
            {"fields": ["student_id"], "name": "children_by_student_id"}
        ]
    },
    "sessions": {
        "description": "User authentication sessions and tokens",
        "indexes": [
            {"fields": ["token_hash"], "name": "sessions_by_token"},
            {"fields": ["refresh_token_hash"], "name": "sessions_by_refresh_token"},
            {"fields": ["user_id", "created_at"], "name": "sessions_by_user_time"}
        ]
    },
    "verification_codes": {
        "description": "Email and phone verification codes",
        "indexes": [
            {"fields": ["email", "code", "type"], "name": "verification_by_email_code"},
            {"fields": ["phone", "otp", "type"], "name": "verification_by_phone_otp"}
        ]
    },
    
    # Exam and Test Management
    "exam_selections": {
        "description": "Student exam type selections (JEE/NEET)",
        "indexes": [
            {"fields": ["student_id"], "name": "exam_selections_by_student"},
            {"fields": ["student_id", "created_at"], "name": "exam_selections_by_student_time"}
        ]
    },
    "diagnostic_tests": {
        "description": "Generated diagnostic tests",
        "indexes": [
            {"fields": ["student_id"], "name": "diagnostic_tests_by_student"},
            {"fields": ["student_id", "created_at"], "name": "diagnostic_tests_by_student_time"},
            {"fields": ["exam_type", "created_at"], "name": "diagnostic_tests_by_exam_time"}
        ]
    },
    "test_submissions": {
        "description": "Student test submissions and answers",
        "indexes": [
            {"fields": ["test_id"], "name": "submissions_by_test"},
            {"fields": ["student_id"], "name": "submissions_by_student"},
            {"fields": ["student_id", "submission_time"], "name": "submissions_by_student_time"}
        ]
    },
    "questions": {
        "description": "Generated questions for tests and practice",
        "indexes": [
            {"fields": ["exam_type", "subject"], "name": "questions_by_exam_subject"},
            {"fields": ["topic"], "name": "questions_by_topic"},
            {"fields": ["difficulty"], "name": "questions_by_difficulty"},
            {"fields": ["question_type"], "name": "questions_by_type"},
            {"fields": ["metadata.validation_score"], "name": "questions_by_quality"},
            {"fields": ["created_at"], "name": "questions_by_created_at"}
        ]
    },
    
    # Analytics and Performance
    "analytics": {
        "description": "Test analytics and performance data",
        "indexes": [
            {"fields": ["overview.student_id", "created_at"], "name": "analytics_by_student_time"},
            {"fields": ["test_id"], "name": "analytics_by_test"}
        ]
    },
    "syllabus_coverage": {
        "description": "Student syllabus coverage tracking",
        "indexes": [
            {"fields": ["student_id", "exam_type"], "name": "coverage_by_student_exam"},
            {"fields": ["updated_at"], "name": "coverage_by_updated_at"}
        ]
    },
    
    # Scheduling and Progress
    "schedules": {
        "description": "AI-generated study schedules",
        "indexes": [
            {"fields": ["student_id"], "name": "schedules_by_student"},
            {"fields": ["student_id", "created_at"], "name": "schedules_by_student_time"},
            {"fields": ["status", "created_at"], "name": "schedules_by_status_time"}
        ]
    },
    
    # Subscriptions and Payments
    "subscriptions": {
        "description": "Active subscription plans",
        "indexes": [
            {"fields": ["parent_id"], "name": "subscriptions_by_parent"},
            {"fields": ["parent_id", "created_at"], "name": "subscriptions_by_parent_time"},
            {"fields": ["status"], "name": "subscriptions_by_status"}
        ]
    },
    "transactions": {
        "description": "Payment transactions and history",
        "indexes": [
            {"fields": ["parent_id", "created_at"], "name": "transactions_by_parent_time"},
            {"fields": ["order_id"], "name": "transactions_by_order"},
            {"fields": ["status"], "name": "transactions_by_status"}
        ]
    },
    
    # Preferences and Settings
    "preferences": {
        "description": "Parent preferences and settings",
        "indexes": [
            {"fields": ["parent_id"], "name": "preferences_by_parent"},
            {"fields": ["parent_id", "updated_at"], "name": "preferences_by_parent_time"}
        ]
    },
    
    # Caching and Performance
    "rag_cache": {
        "description": "RAG question generation cache",
        "indexes": [
            {"fields": ["cache_key"], "name": "rag_cache_by_key"},
            {"fields": ["created_at"], "name": "rag_cache_by_time"}
        ]
    },
    "search_cache": {
        "description": "Vector search results cache",
        "indexes": [
            {"fields": ["query_hash"], "name": "search_cache_by_query"},
            {"fields": ["created_at"], "name": "search_cache_by_time"}
        ]
    },
    "query_cache": {
        "description": "Persistent user query cache",
        "indexes": [
            {"fields": ["user_id", "query_hash"], "name": "query_cache_by_user_query"},
            {"fields": ["last_accessed"], "name": "query_cache_by_accessed"}
        ]
    },
    "rate_limits": {
        "description": "Rate limit tracking and violations",
        "indexes": [
            {"fields": ["user_id", "endpoint"], "name": "rate_limits_by_user_endpoint"},
            {"fields": ["timestamp"], "name": "rate_limits_by_timestamp"}
        ]
    },
    
    # AI Features and Interactions
    "ai_interactions": DATABASE_SCHEMAS["ai_interactions"].collection_name,
    "parent_insights": DATABASE_SCHEMAS["parent_insights"].collection_name,
    "engagement_metrics": DATABASE_SCHEMAS["engagement_metrics"].collection_name,
    "communication_history": DATABASE_SCHEMAS["communication_history"].collection_name,
    "intervention_alerts": DATABASE_SCHEMAS["intervention_alerts"].collection_name,
    "prediction_results": DATABASE_SCHEMAS["prediction_results"].collection_name,
    "communication_suggestions": DATABASE_SCHEMAS["communication_suggestions"].collection_name,
    "engagement_challenges": DATABASE_SCHEMAS["engagement_challenges"].collection_name,
    "achievements": DATABASE_SCHEMAS["achievements"].collection_name,
    "parent_resources": DATABASE_SCHEMAS["parent_resources"].collection_name,
    "resource_usage": DATABASE_SCHEMAS["resource_usage"].collection_name,
    
    # Embeddings and Vector Data
    "embeddings": {
        "description": "Text embeddings for semantic search",
        "indexes": [
            {"fields": ["text_hash"], "name": "embeddings_by_text_hash"},
            {"fields": ["model"], "name": "embeddings_by_model"},
            {"fields": ["created_at"], "name": "embeddings_by_created_at"}
        ]
    },
    
    # Learning Materials and Resources
    "learning_materials": {
        "description": "AI-generated learning materials",
        "indexes": [
            {"fields": ["student_id"], "name": "materials_by_student"},
            {"fields": ["topic"], "name": "materials_by_topic"},
            {"fields": ["subject"], "name": "materials_by_subject"},
            {"fields": ["created_at"], "name": "materials_by_created_at"}
        ]
    }
}

def print_success(message):
    """Print success message with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] ✓ {message}")

def print_error(message):
    """Print error message with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] ✗ {message}")

def print_info(message):
    """Print info message with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] ℹ {message}")

def create_sample_data():
    """Create sample documents for testing."""
    return {
        "parents": {
            "_sample": {
                "uid": "sample_parent_id",
                "email": "parent@example.com",
                "phone": "+1234567890",
                "name": "Sample Parent",
                "email_verified": True,
                "phone_verified": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        },
        "children": {
            "_sample": {
                "student_id": "sample_student_id",
                "parent_id": "sample_parent_id",
                "name": "Sample Student",
                "age": 17,
                "grade": 12,
                "target_exam": "JEE_MAIN",
                "exam_date": "2025-04-15",
                "current_level": "intermediate",
                "username": "sample_student",
                "password": "sample_pass123",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        },
        "exam_selections": {
            "_sample": {
                "selection_id": "sample_selection_id",
                "student_id": "sample_student_id",
                "exam_type": "JEE_MAIN",
                "selected_date": datetime.now(timezone.utc).isoformat(),
                "preparation_start": datetime.now(timezone.utc).isoformat(),
                "target_exam_date": "2025-04-15",
                "is_sample": True,
            }
        },
        "diagnostic_tests": {
            "_sample": {
                "test_id": "sample_test_id",
                "student_id": "sample_student_id",
                "exam_type": "JEE_MAIN",
                "status": "completed",
                "total_questions": 30,
                "total_marks": 120,
                "generated_date": datetime.now(timezone.utc).isoformat(),
                "start_date": datetime.now(timezone.utc).isoformat(),
                "submission_date": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        },
        "schedules": {
            "_sample": {
                "schedule_id": "sample_schedule_id",
                "student_id": "sample_student_id",
                "parent_id": "sample_parent_id",
                "exam_type": "JEE_MAIN",
                "start_date": "2024-12-01",
                "exam_date": "2025-04-15",
                "total_days": 135,
                "daily_hours": 6,
                "status": "active",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        },
        "subscriptions": {
            "_sample": {
                "subscription_id": "sample_subscription_id",
                "parent_id": "sample_parent_id",
                "plan_id": "premium_monthly",
                "status": "active",
                "start_date": datetime.now(timezone.utc).isoformat(),
                "end_date": None,
                "auto_renew": True,
                "is_sample": True,
            }
        },
        "preferences": {
            "_sample": {
                "parent_id": "sample_parent_id",
                "language": "en",
                "email_notifications": True,
                "sms_notifications": True,
                "push_notifications": True,
                "teaching_involvement": "medium",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        },
        # Additional collections with sample data
        "test_submissions": {
            "_sample": {
                "submission_id": "sample_submission_id",
                "test_id": "sample_test_id",
                "student_id": "sample_student_id",
                "answers": {"1": "A", "2": "B", "3": "C", "4": "D"},
                "time_taken": 3600,
                "submission_time": datetime.now(timezone.utc).isoformat(),
                "score": 85,
                "total_marks": 120,
                "is_sample": True,
            }
        },
        "questions": {
            "_sample": {
                "question_id": "sample_question_id",
                "question": "What is the derivative of sin(x)?",
                "options": {"A": "cos(x)", "B": "-cos(x)", "C": "sin(x)", "D": "-sin(x)"},
                "correct_answer": "A",
                "explanation": "The derivative of sin(x) is cos(x) by standard differentiation rules.",
                "difficulty": "easy",
                "topic": "Calculus - Differentiation",
                "subject": "Mathematics",
                "question_type": "single_correct",
                "marks": 4,
                "estimated_time_minutes": 2,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        },
        "analytics": {
            "_sample": {
                "analytics_id": "sample_analytics_id",
                "test_id": "sample_test_id",
                "student_id": "sample_student_id",
                "total_score": 85,
                "max_score": 120,
                "percentage": 70.83,
                "accuracy": 70.83,
                "time_taken": 3600,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        },
        "syllabus_coverage": {
            "_sample": {
                "coverage_id": "sample_coverage_id",
                "student_id": "sample_student_id",
                "exam_type": "JEE_MAIN",
                "total_topics": 50,
                "covered_topics": 35,
                "coverage_percentage": 70.0,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        },
        "transactions": {
            "_sample": {
                "transaction_id": "sample_transaction_id",
                "parent_id": "sample_parent_id",
                "order_id": "order_12345",
                "amount": 999.00,
                "currency": "INR",
                "status": "completed",
                "payment_method": "credit_card",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        },
        "sessions": {
            "_sample": {
                "session_id": "sample_session_id",
                "user_id": "sample_parent_id",
                "token_hash": "hash123",
                "refresh_token_hash": "refresh_hash123",
                "expires_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        },
        "verification_codes": {
            "_sample": {
                "code_id": "sample_code_id",
                "email": "parent@example.com",
                "code": "123456",
                "type": "email",
                "expires_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        },
        # AI Features sample data
        "ai_interactions": {
            "_sample": {
                "interaction_id": "sample_interaction_id",
                "user_id": "sample_parent_id",
                "student_id": "sample_student_id",
                "interaction_type": "question_answer",
                "request_data": {"question": "What is calculus?"},
                "response_data": {"answer": "Calculus is the study of change..."},
                "status": "completed",
                "tokens_used": {"prompt": 50, "completion": 100},
                "cost": 0.005,
                "response_time_ms": 1500,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        },
        "parent_insights": {
            "_sample": {
                "insight_id": "sample_insight_id",
                "parent_id": "sample_parent_id",
                "student_id": "sample_student_id",
                "insight_type": "performance",
                "title": "Strong in Mathematics",
                "description": "Student shows excellent performance in calculus topics",
                "severity": "low",
                "data": {"score": 85, "topics": ["calculus", "derivatives"]},
                "action_required": False,
                "status": "new",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        },
        "engagement_metrics": {
            "_sample": {
                "metric_id": "sample_metric_id",
                "user_id": "sample_parent_id",
                "student_id": "sample_student_id",
                "metric_type": "study_time",
                "metric_name": "Daily Study Hours",
                "value": 4.5,
                "unit": "hours",
                "period": "daily",
                "date": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        },
        "communication_history": {
            "_sample": {
                "communication_id": "sample_comm_id",
                "parent_id": "sample_parent_id",
                "student_id": "sample_student_id",
                "communication_type": "notification",
                "channel": "email",
                "subject": "Study Progress Update",
                "content": "Student has completed calculus chapter",
                "status": "sent",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        },
        "intervention_alerts": {
            "_sample": {
                "alert_id": "sample_alert_id",
                "parent_id": "sample_parent_id",
                "student_id": "sample_student_id",
                "alert_type": "performance_drop",
                "severity": "medium",
                "title": "Math Score Decline",
                "description": "Student's math scores have dropped by 15% this week",
                "data": {"previous_score": 85, "current_score": 70, "drop_percentage": 15},
                "status": "new",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        },
        "prediction_results": {
            "_sample": {
                "prediction_id": "sample_prediction_id",
                "parent_id": "sample_parent_id",
                "student_id": "sample_student_id",
                "prediction_type": "performance_trend",
                "confidence_score": 0.85,
                "prediction_data": {"trend": "declining", "subject": "mathematics"},
                "risk_factors": ["practice_gap", "concept_gaps"],
                "time_horizon_days": 30,
                "model_version": "v1.0",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        },
        "communication_suggestions": {
            "_sample": {
                "suggestion_id": "sample_suggestion_id",
                "parent_id": "sample_parent_id",
                "student_id": "sample_student_id",
                "communication_type": "encouragement",
                "suggested_content": "Praise student for their calculus progress and suggest additional practice problems",
                "tone": "supportive",
                "context": {"recent_performance": "improving", "subject": "mathematics"},
                "used": False,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        },
        "engagement_challenges": {
            "_sample": {
                "challenge_id": "sample_challenge_id",
                "parent_id": "sample_parent_id",
                "student_id": "sample_student_id",
                "challenge_type": "weekly_goal",
                "title": "Complete 5 Calculus Problems",
                "description": "Complete 5 calculus problems this week with 80% accuracy",
                "difficulty_level": "medium",
                "target_metrics": {"problems_completed": 5, "accuracy": 80},
                "current_progress": {"problems_completed": 2, "accuracy": 75},
                "points_awarded": 50,
                "start_date": datetime.now(timezone.utc).isoformat(),
                "end_date": datetime.now(timezone.utc).isoformat(),
                "status": "active",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        },
        "achievements": {
            "_sample": {
                "achievement_id": "sample_achievement_id",
                "parent_id": "sample_parent_id",
                "student_id": "sample_student_id",
                "achievement_type": "milestone",
                "title": "Calculus Master",
                "description": "Completed all calculus topics with 85% accuracy",
                "badge_icon": "calculus_master",
                "points_awarded": 100,
                "rarity": "rare",
                "earned_at": datetime.now(timezone.utc).isoformat(),
                "shared": False,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        },
        "parent_resources": {
            "_sample": {
                "resource_id": "sample_resource_id",
                "title": "Calculus Study Guide",
                "description": "Comprehensive guide for calculus preparation",
                "resource_type": "guide",
                "category": "academic_support",
                "content": "https://example.com/calculus-guide",
                "age_appropriate": ["16-18"],
                "difficulty_level": "intermediate",
                "language": "en",
                "tags": ["calculus", "mathematics", "exam_prep"],
                "quality_score": 0.92,
                "usage_count": 15,
                "download_count": 8,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        },
        "resource_usage": {
            "_sample": {
                "usage_id": "sample_usage_id",
                "parent_id": "sample_parent_id",
                "student_id": "sample_student_id",
                "resource_id": "sample_resource_id",
                "usage_type": "viewed",
                "effectiveness_rating": 4.5,
                "feedback": "Very helpful for understanding calculus concepts",
                "time_spent_minutes": 30,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        },
        # Caching and Performance sample data
        "rag_cache": {
            "_sample": {
                "cache_key": "calculus_differentiation_rules",
                "cached_result": {"rules": ["chain rule", "product rule"], "examples": 3},
                "hit_count": 5,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "expires_at": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        },
        "search_cache": {
            "_sample": {
                "query_hash": "hash123",
                "cached_results": ["result1", "result2", "result3"],
                "hit_count": 10,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "expires_at": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        },
        "query_cache": {
            "_sample": {
                "cache_id": "cache123",
                "user_id": "sample_parent_id",
                "query": "What is the derivative of sin(x)?",
                "response": {"answer": "cos(x)", "explanation": "By chain rule..."},
                "hit_count": 3,
                "last_accessed": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        },
        "rate_limits": {
            "_sample": {
                "limit_id": "sample_limit_id",
                "user_id": "sample_parent_id",
                "endpoint": "/api/generate-question",
                "request_count": 50,
                "window_minutes": 60,
                "blocked": False,
                "violation_count": 0,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        },
        # Embeddings and Learning Materials sample data
        "embeddings": {
            "_sample": {
                "embedding_id": "sample_embedding_id",
                "text": "What is the derivative of sin(x)?",
                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
                "model": "textembedding-gecko@003",
                "dimension": 768,
                "text_length": 35,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        },
        "learning_materials": {
            "_sample": {
                "material_id": "sample_material_id",
                "student_id": "sample_student_id",
                "title": "Introduction to Calculus",
                "content": "Calculus is the mathematical study of continuous change...",
                "type": "video",
                "subject": "Mathematics",
                "topic": "Calculus",
                "difficulty": "beginner",
                "duration_minutes": 45,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "is_sample": True,
            }
        }
    }

class DatabaseManager:
    """Manager for Firestore database operations."""
    
    def __init__(self):
        """Initialize database manager."""
        self.db = None
        self.connected = False
        
    async def connect(self) -> bool:
        """Connect to Firestore."""
        try:
            logger.info("Connecting to Firestore...")
            initialize_firebase()
            self.db = get_firestore_client()
            self.connected = True
            logger.info("Successfully connected to Firestore")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Firestore: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from Firestore."""
        if self.connected:
            logger.info("Disconnecting from Firestore...")
            self.connected = False
            logger.info("Disconnected from Firestore")
    
    async def initialize_collections(self) -> Dict[str, bool]:
        """Initialize all collections defined in ALL_COLLECTIONS."""
        if not self.connected:
            logger.error("Not connected to Firestore")
            return {}
        
        results = {}
        
        logger.info("Initializing collections...")
        
        # Get sample data once
        sample_data = create_sample_data()
        
        # First, initialize collections from DATABASE_SCHEMAS
        for collection_name, schema in DATABASE_SCHEMAS.items():
            try:
                collection = self.db.collection(collection_name)
                
                # Create a dummy document to ensure collection exists
                dummy_doc = collection.document("_init_marker")
                dummy_doc.set({
                    "collection_initialized": True,
                    "schema": schema.collection_name,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "description": schema.description
                })
                
                # Delete dummy document immediately
                dummy_doc.delete()
                
                # Create sample data if available
                if collection_name in sample_data:
                    sample_doc = collection.document("_sample")
                    sample_doc.set(sample_data[collection_name]["_sample"])
                
                results[collection_name] = True
                logger.info(f"Initialized collection: {collection_name}")
                
            except Exception as e:
                results[collection_name] = False
                logger.error(f"Failed to initialize collection {collection_name}: {e}")
        
        # Then initialize additional collections
        for collection_name, config in ALL_COLLECTIONS.items():
            if collection_name in DATABASE_SCHEMAS:
                continue  # Already initialized above
                
            try:
                collection = self.db.collection(collection_name)
                
                # Create a dummy document to ensure collection exists
                dummy_doc = collection.document("_init_marker")
                dummy_doc.set({
                    "collection_initialized": True,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "description": config["description"]
                })
                
                # Delete dummy document immediately
                dummy_doc.delete()
                
                # Create sample data if available
                if collection_name in sample_data:
                    sample_doc = collection.document("_sample")
                    sample_doc.set(sample_data[collection_name]["_sample"])
                
                results[collection_name] = True
                logger.info(f"Initialized collection: {collection_name}")
                
            except Exception as e:
                results[collection_name] = False
                logger.error(f"Failed to initialize collection {collection_name}: {e}")
        
        # Create subcollections
        await self._create_subcollections()
        
        return results
    
    async def _create_subcollections(self):
        """Create important subcollections with sample data."""
        try:
            # Progress subcollection under schedules
            if "_sample" in create_sample_data().get("schedules", {}):
                schedule_id = "sample_schedule_id"
                progress_ref = (
                    self.db.collection("schedules")
                    .document(schedule_id)
                    .collection("progress")
                    .document("day_1")
                )
                
                progress_ref.set({
                    "day_number": 1,
                    "date": "2024-12-01",
                    "status": "pending",
                    "topics_completed": [],
                    "hours_studied": 0,
                    "completion_percentage": 0,
                    "is_sample": True,
                })
                logger.info("Created schedules/progress subcollection")
            
            # Subscription history subcollection
            if "_sample" in create_sample_data().get("subscriptions", {}):
                parent_id = "sample_parent_id"
                history_ref = (
                    self.db.collection("subscriptions")
                    .document(parent_id)
                    .collection("history")
                    .document("sample_history_id")
                )
                
                history_ref.set({
                    "subscription_id": "sample_subscription_id",
                    "action": "created",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "is_sample": True,
                })
                logger.info("Created subscriptions/history subcollection")
                
        except Exception as e:
            logger.error(f"Failed to create subcollections: {e}")
    
    async def delete_all_data(self, dry_run: bool = False) -> Dict[str, int]:
        """Delete all data from all collections while preserving structure."""
        if not self.connected:
            logger.error("Not connected to Firestore")
            return {}
        
        deleted_counts = {}
        
        logger.info("Deleting all data from collections...")
        
        # Get all collection names
        all_collection_names = set(ALL_COLLECTIONS.keys()) | set(DATABASE_SCHEMAS.keys())
        
        for collection_name in all_collection_names:
            try:
                collection = self.db.collection(collection_name)
                
                # Get all documents
                docs = list(collection.stream())
                doc_count = len(docs)
                
                if doc_count == 0:
                    deleted_counts[collection_name] = 0
                    logger.info(f"Collection {collection_name} is already empty")
                    continue
                
                if dry_run:
                    deleted_counts[collection_name] = doc_count
                    logger.info(f"[DRY RUN] Would delete {doc_count} documents from {collection_name}")
                    continue
                
                # Delete documents in batches (max 500 per batch)
                batch = self.db.batch()
                batch_count = 0
                
                for doc in docs:
                    batch.delete(doc.reference)
                    batch_count += 1
                    
                    # Execute batch when it reaches 500 operations
                    if batch_count >= 500:
                        batch.commit()
                        logger.info(f"Deleted batch of {batch_count} documents from {collection_name}")
                        batch = self.db.batch()
                        batch_count = 0
                    
                # Delete remaining documents in last batch
                if batch_count > 0:
                    batch.commit()
                    logger.info(f"Deleted final batch of {batch_count} documents from {collection_name}")
                
                deleted_counts[collection_name] = doc_count
                logger.info(f"Deleted {doc_count} documents from {collection_name}")
                
            except Exception as e:
                deleted_counts[collection_name] = 0
                logger.error(f"Failed to delete data from {collection_name}: {e}")
        
        return deleted_counts
    
    async def get_collection_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all collections."""
        if not self.connected:
            logger.error("Not connected to Firestore")
            return {}
        
        stats = {}
        
        logger.info("Getting collection statistics...")
        
        # Get all collection names
        all_collection_names = set(ALL_COLLECTIONS.keys()) | set(DATABASE_SCHEMAS.keys())
        
        for collection_name in all_collection_names:
            try:
                collection = self.db.collection(collection_name)
                docs = list(collection.stream())
                doc_count = len(docs)
                
                # Get size information (approximate)
                total_size = 0
                for doc in docs:
                    # Rough estimation of document size
                    doc_dict = doc.to_dict()
                    total_size += len(json.dumps(doc_dict, default=str))
                
                stats[collection_name] = {
                    "document_count": doc_count,
                    "estimated_size_bytes": total_size,
                    "estimated_size_kb": round(total_size / 1024, 2)
                }
                
                logger.info(f"Collection {collection_name}: {doc_count} documents, ~{stats[collection_name]['estimated_size_kb']} KB")
                
            except Exception as e:
                stats[collection_name] = {
                    "error": str(e)
                }
                logger.error(f"Failed to get stats for {collection_name}: {e}")
        
        return stats
    
    async def backup_collection(self, collection_name: str, backup_path: str) -> bool:
        """Backup a collection to a JSON file."""
        if not self.connected:
            logger.error("Not connected to Firestore")
            return False
        
        try:
            collection = self.db.collection(collection_name)
            docs = list(collection.stream())
            
            backup_data = []
            for doc in docs:
                doc_data = doc.to_dict()
                doc_data["_document_id"] = doc.id
                backup_data.append(doc_data)
            
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            logger.info(f"Backed up {len(backup_data)} documents from {collection_name} to {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to backup {collection_name}: {e}")
            return False

def confirm_deletion(stats: Dict[str, Dict[str, Any]]) -> bool:
    """Ask for confirmation before deleting data."""
    total_docs = sum(stat.get("document_count", 0) for stat in stats.values())
    
    print("\n" + "="*80)
    print("WARNING: This will delete ALL data from your Firestore collections!")
    print("="*80)
    print(f"Total documents to be deleted: {total_docs}")
    print("\nCollection breakdown:")
    
    for collection_name, stat in stats.items():
        if "error" not in stat:
            print(f"  - {collection_name}: {stat.get('document_count', 0)} documents")
    
    print("="*80)
    print("This action cannot be undone!")
    print("\nType 'DELETE' to confirm deletion:")
    
    confirmation = input("> ").strip()
    return confirmation == "DELETE"

async def main():
    """Main function to handle command-line arguments and execute operations."""
    parser = argparse.ArgumentParser(
        description="Database Manager for Mentor AI Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/database_manager.py --init
  python scripts/database_manager.py --clear
  python scripts/database_manager.py --stats
  python scripts/database_manager.py --reset
  python scripts/database_manager.py --clear --dry-run
        """
    )
    
    parser.add_argument("--init", action="store_true", help="Initialize all collections")
    parser.add_argument("--clear", action="store_true", help="Delete all data from collections")
    parser.add_argument("--stats", action="store_true", help="Show collection statistics")
    parser.add_argument("--reset", action="store_true", help="Clear and reinitialize all collections")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without executing")
    parser.add_argument("--backup", action="store_true", help="Backup data before clearing")
    parser.add_argument("--backup-dir", default="backups", help="Directory for backups (default: backups)")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.init, args.clear, args.stats, args.reset]):
        parser.print_help()
        return
    
    # Create database manager instance
    db_manager = DatabaseManager()
    
    # Connect to Firestore
    if not await db_manager.connect():
        logger.error("Failed to connect to Firestore. Exiting.")
        return
    
    try:
        # Handle stats command
        if args.stats:
            stats = await db_manager.get_collection_stats()
            print("\nCollection Statistics:")
            print("="*80)
            for collection_name, stat in stats.items():
                if "error" not in stat:
                    print(f"{collection_name}:")
                    print(f"  Documents: {stat.get('document_count', 0)}")
                    print(f"  Size: ~{stat.get('estimated_size_kb', 0)} KB")
                else:
                    print(f"{collection_name}: ERROR - {stat['error']}")
            print("="*80)
            return
        
        # Handle clear command
        if args.clear:
            stats = await db_manager.get_collection_stats()
            
            if not args.dry_run and not confirm_deletion(stats):
                print("Deletion cancelled by user.")
                return
            
            # Create backup if requested
            if args.backup and not args.dry_run:
                backup_dir = args.backup_dir
                os.makedirs(backup_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                all_collection_names = set(ALL_COLLECTIONS.keys()) | set(DATABASE_SCHEMAS.keys())
                for collection_name in all_collection_names:
                    backup_path = os.path.join(backup_dir, f"{collection_name}_{timestamp}.json")
                    await db_manager.backup_collection(collection_name, backup_path)
            
            # Delete data
            deleted_counts = await db_manager.delete_all_data(dry_run=args.dry_run)
            
            if args.dry_run:
                print("\n[DRY RUN] Would delete the following:")
                for collection_name, count in deleted_counts.items():
                    print(f"  - {collection_name}: {count} documents")
            else:
                print("\nDeletion completed:")
                total_deleted = sum(deleted_counts.values())
                print(f"Total documents deleted: {total_deleted}")
                for collection_name, count in deleted_counts.items():
                    print(f"  - {collection_name}: {count} documents")
            return
        
        # Handle init command
        if args.init:
            results = await db_manager.initialize_collections()
            print("\nInitialization results:")
            for collection_name, success in results.items():
                status = "SUCCESS" if success else "FAILED"
                print(f"  - {collection_name}: {status}")
            
            # Display required indexes
            print("\nRequired Indexes (create in Firebase Console):")
            print("-" * 80)
            for collection_name, config in ALL_COLLECTIONS.items():
                if "indexes" in config:
                    print(f"\n{collection_name}:")
                    for index in config["indexes"]:
                        fields_str = ", ".join(index["fields"])
                        print(f"  - {fields_str} ({index['name']})")
            
            # Add indexes from DATABASE_SCHEMAS
            for collection_name, schema in DATABASE_SCHEMAS.items():
                print(f"\n{collection_name}:")
                for index in schema.indexes:
                    fields_str = ", ".join(index["fields"])
                    print(f"  - {fields_str} ({index['name']})")
            
            print("\n" + "-" * 80)
            print("\nNext steps:")
            print("1. Go to Firebase Console: https://console.firebase.google.com/")
            print("2. Select your project")
            print("3. Go to Firestore Database")
            print("4. Verify collections are created")
            print("5. Create required indexes (see list above)")
            print("\nNote: Sample documents are marked with 'is_sample: true'")
            print("      You can delete them after testing")
            return
        
        # Handle reset command
        if args.reset:
            stats = await db_manager.get_collection_stats()
            
            if not confirm_deletion(stats):
                print("Reset cancelled by user.")
                return
            
            # Create backup if requested
            if args.backup:
                backup_dir = args.backup_dir
                os.makedirs(backup_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                all_collection_names = set(ALL_COLLECTIONS.keys()) | set(DATABASE_SCHEMAS.keys())
                for collection_name in all_collection_names:
                    backup_path = os.path.join(backup_dir, f"{collection_name}_{timestamp}.json")
                    await db_manager.backup_collection(collection_name, backup_path)
            
            # Clear data
            print("\nClearing collections...")
            deleted_counts = await db_manager.delete_all_data()
            total_deleted = sum(deleted_counts.values())
            print(f"Deleted {total_deleted} documents")
            
            # Reinitialize collections
            print("\nReinitializing collections...")
            init_results = await db_manager.initialize_collections()
            
            print("\nReset completed:")
            print(f"  Documents deleted: {total_deleted}")
            success_count = sum(1 for success in init_results.values() if success)
            print(f"  Collections initialized: {success_count}/{len(init_results)}")
            return
    
    finally:
        # Always disconnect
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())