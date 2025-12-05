"""
Comprehensive Endpoint Testing Script for Mentor AI Backend

This script tests all API endpoints systematically, starting with basic health checks
and progressing through different functional areas. It's designed to work without
relying on the problematic Gemini API by using fallback mechanisms where available.

Author: Mentor AI Team
Version: 1.0.0
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional
import httpx
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

class EndpointTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []
        self.auth_token = None
        self.parent_id = None
        self.child_id = None
        self.test_id = None
        
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def log_result(self, endpoint: str, method: str, status_code: int, 
                   response_time: float, success: bool, error: Optional[str] = None):
        """Log test result for an endpoint"""
        result = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "response_time_ms": round(response_time * 1000, 2),
            "success": success,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {method} {endpoint} - {status_code} ({response_time:.2f}s)")
        if error:
            logger.error(f"    Error: {error}")
    
    async def test_endpoint(self, method: str, endpoint: str, 
                           data: Optional[Dict] = None, 
                           headers: Optional[Dict] = None,
                           expected_status: int = 200) -> bool:
        """Test a single endpoint"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if headers is None:
                headers = {}
            
            if method.upper() == "GET":
                response = await self.client.get(url, headers=headers)
            elif method.upper() == "POST":
                response = await self.client.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = await self.client.put(url, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = await self.client.delete(url, headers=headers)
            elif method.upper() == "PATCH":
                response = await self.client.patch(url, json=data, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time = time.time() - start_time
            success = response.status_code == expected_status
            
            # Log response content for debugging
            if not success:
                try:
                    error_content = response.json()
                    error_msg = str(error_content.get("detail", error_content))
                except:
                    error_msg = response.text
                self.log_result(endpoint, method, response.status_code, response_time, False, error_msg)
            else:
                self.log_result(endpoint, method, response.status_code, response_time, True)
            
            return success
            
        except Exception as e:
            response_time = time.time() - start_time
            self.log_result(endpoint, method, 0, response_time, False, str(e))
            return False
    
    async def test_health_endpoints(self):
        """Test basic health and system endpoints"""
        logger.info("🔍 Testing Health Endpoints...")
        
        # Main health endpoint
        await self.test_endpoint("GET", "/health")
        
        # Root endpoint
        await self.test_endpoint("GET", "/")
        
        # API docs endpoints (should always be available)
        await self.test_endpoint("GET", "/api/docs")
        await self.test_endpoint("GET", "/api/redoc")
        await self.test_endpoint("GET", "/api/openapi.json")
    
    async def test_authentication_endpoints(self):
        """Test authentication and user management endpoints"""
        logger.info("🔐 Testing Authentication Endpoints...")
        
        # Simple registration (for testing without email verification)
        test_user = {
            "email": "testuser@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        
        await self.test_endpoint("POST", "/api/auth/register-simple", test_user, expected_status=201)
        
        # Try to login with the created user
        login_data = {
            "email": "testuser@example.com",
            "password": "testpassword123"
        }
        
        # Note: This might fail due to auth implementation, but we test it anyway
        await self.test_endpoint("POST", "/api/auth/login/email", login_data)
        
        # Test other auth endpoints (they should return appropriate error codes)
        await self.test_endpoint("GET", "/api/auth/current-parent", expected_status=401)
        await self.test_endpoint("POST", "/api/auth/refresh", {}, expected_status=401)
        await self.test_endpoint("POST", "/api/auth/logout", {}, expected_status=401)
    
    async def test_verification_endpoints(self):
        """Test email and phone verification endpoints"""
        logger.info("📧 Testing Verification Endpoints...")
        
        # Email verification endpoints
        await self.test_endpoint("POST", "/verify/email/send", {
            "email": "test@example.com"
        })
        
        await self.test_endpoint("POST", "/verify/email/confirm", {
            "email": "test@example.com",
            "code": "123456"
        })
        
        # Phone verification endpoints
        await self.test_endpoint("POST", "/verify/phone/send", {
            "phone": "+1234567890"
        })
        
        await self.test_endpoint("POST", "/verify/phone/confirm", {
            "phone": "+1234567890",
            "code": "123456"
        })
    
    async def test_child_management_endpoints(self):
        """Test child profile management endpoints"""
        logger.info("👶 Testing Child Management Endpoints...")
        
        # These endpoints require authentication, so they should return 401 without auth
        await self.test_endpoint("POST", "/api/child", {
            "name": "Test Child",
            "age": 15,
            "grade": "10"
        }, expected_status=401)
        
        await self.test_endpoint("GET", "/api/child", expected_status=401)
        await self.test_endpoint("PUT", "/api/child", {}, expected_status=401)
        await self.test_endpoint("DELETE", "/api/child", expected_status=401)
    
    async def test_exam_and_preferences_endpoints(self):
        """Test exam selection and preferences endpoints"""
        logger.info("📚 Testing Exam and Preferences Endpoints...")
        
        # Available exams (should work without auth)
        await self.test_endpoint("GET", "/api/exam/available")
        
        # Preferences endpoints (require auth)
        await self.test_endpoint("POST", "/api/preferences", {}, expected_status=401)
        await self.test_endpoint("GET", "/api/preferences", expected_status=401)
        await self.test_endpoint("PUT", "/api/preferences", {}, expected_status=401)
        
        # Exam selection endpoints (require auth)
        await self.test_endpoint("POST", "/api/exam/select", {
            "exam_type": "JEE",
            "subjects": ["Physics", "Chemistry", "Mathematics"]
        }, expected_status=401)
        
        await self.test_endpoint("GET", "/api/exam/selection", expected_status=401)
        await self.test_endpoint("PUT", "/api/exam/preferences", {}, expected_status=401)
        await self.test_endpoint("GET", "/api/exam/onboarding-status", expected_status=401)
    
    async def test_vector_and_embedding_endpoints(self):
        """Test vector search and embedding endpoints"""
        logger.info("🔍 Testing Vector Search and Embedding Endpoints...")
        
        # Vector search endpoints
        await self.test_endpoint("POST", "/api/vector-search/search", {
            "query": "Newton's laws of motion",
            "subject": "Physics",
            "limit": 10
        })
        
        await self.test_endpoint("GET", "/api/vector-search/index-status")
        await self.test_endpoint("GET", "/api/vector-search/syllabus")
        await self.test_endpoint("GET", "/api/vector-search/statistics")
        
        # Embedding endpoints
        await self.test_endpoint("POST", "/api/vector-search/embeddings", {
            "text": "Newton's first law of motion states that an object at rest stays at rest"
        })
        
        await self.test_endpoint("POST", "/api/vector-search/embeddings/batch", {
            "texts": [
                "Newton's first law",
                "Newton's second law",
                "Newton's third law"
            ]
        })
    
    async def test_diagnostic_test_endpoints(self):
        """Test diagnostic test endpoints"""
        logger.info("📝 Testing Diagnostic Test Endpoints...")
        
        # Test generation (might fail due to AI dependencies, but test anyway)
        await self.test_endpoint("POST", "/api/diagnostic-test/generate", {
            "subject": "Physics",
            "topics": ["Newton's Laws"],
            "difficulty": "medium",
            "question_count": 10
        })
        
        # Test retrieval endpoints
        await self.test_endpoint("GET", "/api/diagnostic-test/test123", expected_status=404)
        await self.test_endpoint("GET", "/api/diagnostic-test/test123/metadata", expected_status=404)
        
        # Test student tests (requires auth)
        await self.test_endpoint("GET", "/api/diagnostic-test/student", expected_status=401)
        
        # Test schedule endpoint
        await self.test_endpoint("POST", "/api/diagnostic-test/schedule", {
            "test_id": "test123",
            "scheduled_time": "2024-01-01T10:00:00Z"
        }, expected_status=401)
    
    async def test_rag_and_question_endpoints(self):
        """Test RAG and question generation endpoints"""
        logger.info("🤖 Testing RAG and Question Generation Endpoints...")
        
        # RAG endpoints
        await self.test_endpoint("POST", "/api/rag/generate-questions", {
            "topic": "Newton's Laws",
            "subject": "Physics",
            "difficulty": "medium",
            "question_count": 5
        })
        
        await self.test_endpoint("POST", "/api/rag/generate-batch", {
            "topics": ["Newton's Laws", "Kinematics"],
            "subject": "Physics",
            "questions_per_topic": 3
        })
        
        await self.test_endpoint("POST", "/api/rag/build-context", {
            "topic": "Newton's Laws",
            "subject": "Physics"
        })
        
        await self.test_endpoint("GET", "/api/rag/pipeline-status")
        await self.test_endpoint("GET", "/api/rag/metrics")
        
        # Question endpoints
        await self.test_endpoint("GET", "/api/questions/question123", expected_status=404)
        await self.test_endpoint("GET", "/api/questions/topic/Physics", expected_status=422)  # Missing required params
        await self.test_endpoint("POST", "/api/questions/validate", {
            "question": "What is Newton's first law?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option A",
            "subject": "Physics",
            "topic": "Newton's Laws"
        })
    
    async def test_study_center_endpoints(self):
        """Test study center and learning material endpoints"""
        logger.info("📖 Testing Study Center Endpoints...")
        
        # Study center endpoints
        await self.test_endpoint("GET", "/api/study-center/topics")
        await self.test_endpoint("GET", "/api/study-center/topic/Physics", expected_status=404)
        await self.test_endpoint("GET", "/api/study-center/materials/Physics", expected_status=404)
        
        # These might fail due to AI dependencies
        await self.test_endpoint("POST", "/api/study-center/generate-materials", {
            "topic": "Newton's Laws",
            "subject": "Physics",
            "material_type": "notes"
        })
        
        await self.test_endpoint("GET", "/api/study-center/mind-map/Physics", expected_status=404)
        await self.test_endpoint("GET", "/api/study-center/teaching/Physics", expected_status=404)
        await self.test_endpoint("GET", "/api/study-center/progress/student123", expected_status=401)
    
    async def test_schedule_endpoints(self):
        """Test schedule generation and management endpoints"""
        logger.info("📅 Testing Schedule Endpoints...")
        
        # Schedule endpoints (most require auth)
        await self.test_endpoint("POST", "/api/schedule/generate", {
            "student_id": "student123",
            "exam_type": "JEE",
            "subjects": ["Physics", "Chemistry", "Mathematics"],
            "study_hours_per_day": 4,
            "weeks_available": 12
        }, expected_status=401)
        
        await self.test_endpoint("GET", "/api/schedule/schedule123", expected_status=404)
        await self.test_endpoint("GET", "/api/schedule/student/student123", expected_status=401)
        await self.test_endpoint("GET", "/api/schedule/history/student123", expected_status=401)
        
        # Progress tracking
        await self.test_endpoint("POST", "/api/schedule/progress/update", {
            "schedule_id": "schedule123",
            "day": 1,
            "completed_topics": ["Newton's Laws"],
            "time_spent": 120
        }, expected_status=401)
        
        await self.test_endpoint("GET", "/api/schedule/progress/summary/student123", expected_status=401)
        await self.test_endpoint("GET", "/api/schedule/today/student123", expected_status=401)
    
    async def test_payment_endpoints(self):
        """Test payment and subscription endpoints"""
        logger.info("💳 Testing Payment Endpoints...")
        
        # Public endpoints
        await self.test_endpoint("GET", "/api/payment/plans")
        
        # Protected endpoints (require auth)
        await self.test_endpoint("POST", "/api/payment/create-order", {
            "plan_id": "basic",
            "amount": 999
        }, expected_status=401)
        
        await self.test_endpoint("POST", "/api/payment/verify", {
            "order_id": "order123",
            "payment_id": "payment123",
            "signature": "signature123"
        }, expected_status=401)
        
        await self.test_endpoint("GET", "/api/payment/subscription/status", expected_status=401)
        await self.test_endpoint("GET", "/api/payment/transactions", expected_status=401)
        await self.test_endpoint("POST", "/api/payment/subscription/cancel", expected_status=401)
    
    async def test_dashboard_endpoints(self):
        """Test dashboard endpoints for parents and students"""
        logger.info("📊 Testing Dashboard Endpoints...")
        
        # Parent dashboard endpoints (require auth)
        await self.test_endpoint("GET", "/api/parent/dashboard", expected_status=401)
        await self.test_endpoint("GET", "/api/parent/reports/weekly", expected_status=401)
        await self.test_endpoint("GET", "/api/parent/goals", expected_status=401)
        await self.test_endpoint("POST", "/api/parent/goals", {
            "title": "Complete Physics Chapter",
            "target_date": "2024-02-01"
        }, expected_status=401)
        
        # Student dashboard endpoints (require auth)
        await self.test_endpoint("GET", "/api/student/today", expected_status=401)
        await self.test_endpoint("GET", "/api/student/topic-resources/Physics", expected_status=401)
        await self.test_endpoint("POST", "/api/student/practice/quick", {
            "subject": "Physics",
            "duration": 15
        }, expected_status=401)
        
        await self.test_endpoint("POST", "/api/student/doubts", {
            "question": "What is Newton's first law?",
            "subject": "Physics"
        }, expected_status=401)
        
        await self.test_endpoint("GET", "/api/student/doubts/doubt123", expected_status=401)
        await self.test_endpoint("GET", "/api/student/revision-due", expected_status=401)
        await self.test_endpoint("GET", "/api/student/bookmarks", expected_status=401)
    
    async def test_gamification_endpoints(self):
        """Test gamification endpoints"""
        logger.info("🎮 Testing Gamification Endpoints...")
        
        # Gamification endpoints (require auth)
        await self.test_endpoint("GET", "/api/gamification/achievements", expected_status=401)
        await self.test_endpoint("POST", "/api/gamification/achievements/achievement123/claim", expected_status=401)
        await self.test_endpoint("GET", "/api/gamification/challenge/daily", expected_status=401)
        await self.test_endpoint("POST", "/api/gamification/challenge/daily/submit", {
            "answer": "Option A"
        }, expected_status=401)
        
        await self.test_endpoint("GET", "/api/gamification/leaderboard", expected_status=401)
        await self.test_endpoint("GET", "/api/gamification/streak", expected_status=401)
        await self.test_endpoint("GET", "/api/gamification/points", expected_status=401)
    
    async def test_analytics_endpoints(self):
        """Test analytics and performance endpoints"""
        logger.info("📈 Testing Analytics Endpoints...")
        
        # Analytics endpoints (require auth)
        await self.test_endpoint("POST", "/api/analytics/generate", {
            "student_id": "student123",
            "test_id": "test123",
            "analysis_type": "performance"
        }, expected_status=401)
        
        await self.test_endpoint("GET", "/api/analytics/analytics123", expected_status=404)
        await self.test_endpoint("GET", "/api/analytics/student/student123", expected_status=401)
        await self.test_endpoint("GET", "/api/analytics/test/test123", expected_status=401)
        await self.test_endpoint("GET", "/api/analytics/insights/analytics123", expected_status=404)
        await self.test_endpoint("GET", "/api/analytics/weak-topics/analytics123", expected_status=404)
    
    async def test_ai_features_endpoints(self):
        """Test AI-powered features endpoints"""
        logger.info("🤖 Testing AI Features Endpoints...")
        
        # AI features endpoints (require auth)
        await self.test_endpoint("GET", "/api/ai/interactions", expected_status=401)
        await self.test_endpoint("GET", "/api/ai/interactions/summary", expected_status=401)
        await self.test_endpoint("GET", "/api/ai/insights", expected_status=401)
        await self.test_endpoint("GET", "/api/ai/engagement-metrics", expected_status=401)
        
        # These might fail due to AI dependencies
        await self.test_endpoint("POST", "/api/ai/tutor/ask", {
            "question": "What is Newton's first law?",
            "subject": "Physics"
        }, expected_status=401)
        
        await self.test_endpoint("POST", "/api/ai/recommend/topics", {
            "student_id": "student123",
            "subject": "Physics"
        }, expected_status=401)
        
        await self.test_endpoint("POST", "/api/ai/readiness", {
            "student_id": "student123",
            "exam_type": "JEE"
        }, expected_status=401)
    
    async def test_language_endpoints(self):
        """Test language management endpoints"""
        logger.info("🌍 Testing Language Endpoints...")
        
        # Language endpoints
        await self.test_endpoint("GET", "/api/language/supported")
        await self.test_endpoint("GET", "/api/language/info/en")
        await self.test_endpoint("GET", "/api/language/translations/en")
        await self.test_endpoint("GET", "/api/language/rtl")
        await self.test_endpoint("GET", "/api/language/validate/en")
        await self.test_endpoint("GET", "/api/language/health")
        
        # Protected language endpoints
        await self.test_endpoint("POST", "/api/language/preference", {
            "language": "en"
        }, expected_status=401)
        
        await self.test_endpoint("GET", "/api/language/preference", expected_status=401)
        await self.test_endpoint("GET", "/api/language/translate?text=Hello&target=hi")
    
    async def test_token_usage_endpoints(self):
        """Test token usage tracking endpoints"""
        logger.info("🪙 Testing Token Usage Endpoints...")
        
        # Token usage endpoints (require auth)
        await self.test_endpoint("GET", "/api/token-usage/student/student123", expected_status=401)
        await self.test_endpoint("GET", "/api/token-usage/limits/student/student123", expected_status=401)
        await self.test_endpoint("GET", "/api/token-usage/parent", expected_status=401)
        await self.test_endpoint("POST", "/api/token-usage/reset/daily/student123", expected_status=401)
        await self.test_endpoint("GET", "/api/token-usage/summary/parent", expected_status=401)
    
    async def test_academic_guidance_endpoints(self):
        """Test academic guidance system endpoints"""
        logger.info("🎓 Testing Academic Guidance Endpoints...")
        
        # Academic guidance endpoints (require auth)
        await self.test_endpoint("POST", "/api/guidance/activity/log", {
            "student_id": "student123",
            "activity_type": "study",
            "subject": "Physics",
            "topic": "Newton's Laws",
            "duration": 30
        }, expected_status=401)
        
        await self.test_endpoint("POST", "/api/guidance/activity/topic-access", {
            "student_id": "student123",
            "subject": "Physics",
            "topic": "Newton's Laws"
        }, expected_status=401)
        
        await self.test_endpoint("POST", "/api/guidance/activity/quiz-attempt", {
            "student_id": "student123",
            "subject": "Physics",
            "topic": "Newton's Laws",
            "score": 8,
            "total_questions": 10
        }, expected_status=401)
        
        await self.test_endpoint("POST", "/api/guidance/activity/learning-sequence", {
            "student_id": "student123",
            "sequence": ["Newton's Laws", "Kinematics", "Work and Energy"]
        }, expected_status=401)
        
        await self.test_endpoint("POST", "/api/guidance/analysis/trigger", {
            "student_id": "student123",
            "analysis_types": ["knowledge_gaps", "learning_strengths"]
        }, expected_status=401)
        
        # Progress insights endpoints
        await self.test_endpoint("GET", "/api/progress/student123", expected_status=401)
        await self.test_endpoint("GET", "/api/progress/summary/student123", expected_status=401)
        await self.test_endpoint("GET", "/api/insights/student123", expected_status=401)
        await self.test_endpoint("GET", "/api/insights/patterns/student123", expected_status=401)
        await self.test_endpoint("GET", "/api/insights/gaps/student123", expected_status=401)
        await self.test_endpoint("GET", "/api/insights/strengths/student123", expected_status=401)
        await self.test_endpoint("GET", "/api/recommendations/student123", expected_status=401)
    
    async def test_vidhya_ai_endpoints(self):
        """Test Vidhya AI chat endpoints"""
        logger.info("💬 Testing Vidhya AI Endpoints...")
        
        # Vidhya AI endpoints (require auth)
        await self.test_endpoint("POST", "/api/vidhya/chat/start", {
            "language": "en"
        }, expected_status=401)
        
        await self.test_endpoint("POST", "/api/vidhya/chat/send", {
            "session_id": "session123",
            "message": "What is Newton's first law?"
        }, expected_status=401)
        
        await self.test_endpoint("GET", "/api/vidhya/chat/history/session123", expected_status=401)
        await self.test_endpoint("GET", "/api/vidhya/chat/sessions", expected_status=401)
        await self.test_endpoint("DELETE", "/api/vidhya/chat/session/session123", expected_status=401)
        
        # Public endpoints
        await self.test_endpoint("GET", "/api/vidhya/languages")
        await self.test_endpoint("GET", "/api/vidhya/health")
    
    async def test_parent_features_endpoints(self):
        """Test parent features endpoints"""
        logger.info("👨‍👩‍👧‍👦 Testing Parent Features Endpoints...")
        
        # Parent features endpoints (require auth)
        await self.test_endpoint("POST", "/api/parent/insights/generate", {
            "student_id": "student123",
            "insight_type": "performance"
        }, expected_status=401)
        
        await self.test_endpoint("GET", "/api/parent/insights", expected_status=401)
        await self.test_endpoint("POST", "/api/parent/insights/conversation-starters", {
            "student_id": "student123",
            "topic": "physics_performance"
        }, expected_status=401)
        
        await self.test_endpoint("POST", "/api/parent/analytics/predict", {
            "student_id": "student123",
            "prediction_type": "exam_performance"
        }, expected_status=401)
        
        await self.test_endpoint("POST", "/api/parent/communication/generate", {
            "student_id": "student123",
            "message_type": "progress_update"
        }, expected_status=401)
        
        await self.test_endpoint("POST", "/api/parent/engagement/track", {
            "student_id": "student123",
            "activity": "dashboard_login"
        }, expected_status=401)
        
        await self.test_endpoint("POST", "/api/parent/resources/generate", {
            "topic": "helping_child_with_physics",
            "resource_type": "tips"
        }, expected_status=401)
        
        # Metrics endpoints
        await self.test_endpoint("GET", "/api/parent/metrics/insights", expected_status=401)
        await self.test_endpoint("GET", "/api/parent/metrics/analytics", expected_status=401)
        await self.test_endpoint("GET", "/api/parent/metrics/communication", expected_status=401)
        await self.test_endpoint("GET", "/api/parent/metrics/engagement", expected_status=401)
        await self.test_endpoint("GET", "/api/parent/metrics/resource-library", expected_status=401)
        await self.test_endpoint("GET", "/api/parent/health")
    
    async def test_syllabus_coverage_endpoints(self):
        """Test syllabus coverage endpoints"""
        logger.info("📚 Testing Syllabus Coverage Endpoints...")
        
        # Syllabus coverage endpoints (require auth)
        await self.test_endpoint("GET", "/api/syllabus/coverage/student123", expected_status=401)
        await self.test_endpoint("GET", "/api/syllabus/untested/student123", expected_status=401)
        await self.test_endpoint("GET", "/api/syllabus/weak/student123", expected_status=401)
        await self.test_endpoint("GET", "/api/syllabus/recommendations/student123", expected_status=401)
        await self.test_endpoint("GET", "/api/syllabus/progress/student123", expected_status=401)
        await self.test_endpoint("GET", "/api/syllabus/topic/Physics/Newton's Laws", expected_status=401)
        await self.test_endpoint("GET", "/api/syllabus/health")
    
    async def run_all_tests(self):
        """Run all endpoint tests"""
        logger.info("🚀 Starting Comprehensive Endpoint Testing...")
        logger.info(f"Testing against: {self.base_url}")
        
        start_time = time.time()
        
        # Test endpoints in logical order
        await self.test_health_endpoints()
        await self.test_authentication_endpoints()
        await self.test_verification_endpoints()
        await self.test_child_management_endpoints()
        await self.test_exam_and_preferences_endpoints()
        await self.test_vector_and_embedding_endpoints()
        await self.test_diagnostic_test_endpoints()
        await self.test_rag_and_question_endpoints()
        await self.test_study_center_endpoints()
        await self.test_schedule_endpoints()
        await self.test_payment_endpoints()
        await self.test_dashboard_endpoints()
        await self.test_gamification_endpoints()
        await self.test_analytics_endpoints()
        await self.test_ai_features_endpoints()
        await self.test_language_endpoints()
        await self.test_token_usage_endpoints()
        await self.test_academic_guidance_endpoints()
        await self.test_vidhya_ai_endpoints()
        await self.test_parent_features_endpoints()
        await self.test_syllabus_coverage_endpoints()
        
        total_time = time.time() - start_time
        
        # Generate summary report
        self.generate_summary_report(total_time)
    
    def generate_summary_report(self, total_time: float):
        """Generate a summary report of all test results"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        # Group results by status code
        status_codes = {}
        for result in self.test_results:
            code = result["status_code"]
            status_codes[code] = status_codes.get(code, 0) + 1
        
        # Group results by endpoint category
        categories = {}
        for result in self.test_results:
            endpoint = result["endpoint"]
            category = endpoint.split("/")[1] if "/" in endpoint else "root"
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0}
            
            if result["success"]:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
        
        # Calculate average response time
        avg_response_time = sum(r["response_time_ms"] for r in self.test_results) / total_tests
        
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE ENDPOINT TEST REPORT")
        print("="*80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Average Response Time: {avg_response_time:.2f}ms")
        
        print("\n📈 Status Code Distribution:")
        for code, count in sorted(status_codes.items()):
            status = "✅" if code == 200 else "⚠️" if 400 <= code < 500 else "❌"
            print(f"  {status} {code}: {count} tests")
        
        print("\n📂 Results by Category:")
        for category, results in sorted(categories.items()):
            total = results["passed"] + results["failed"]
            success_rate = (results["passed"] / total) * 100 if total > 0 else 0
            print(f"  {category}: {results["passed"]}/{total} passed ({success_rate:.1f}%)")
        
        # Show failed tests
        failed_results = [r for r in self.test_results if not r["success"]]
        if failed_results:
            print("\n❌ Failed Tests:")
            for result in failed_results[:10]:  # Show first 10 failed tests
                print(f"  {result['method']} {result['endpoint']} - {result['status_code']}: {result['error']}")
            
            if len(failed_results) > 10:
                print(f"  ... and {len(failed_results) - 10} more failed tests")
        
        print("\n" + "="*80)
        
        # Save detailed results to file
        with open("endpoint_test_results.json", "w") as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "success_rate": (passed_tests/total_tests)*100,
                    "total_time": total_time,
                    "avg_response_time": avg_response_time
                },
                "status_codes": status_codes,
                "categories": categories,
                "detailed_results": self.test_results
            }, f, indent=2)
        
        print(f"📄 Detailed results saved to: endpoint_test_results.json")

async def main():
    """Main function to run the endpoint tests"""
    async with EndpointTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())