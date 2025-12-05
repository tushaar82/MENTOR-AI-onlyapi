#!/usr/bin/env python3
"""
Comprehensive Endpoint Testing Script for Mentor AI Backend API
Corrected with actual endpoint paths from router analysis

This script tests all API endpoints with the correct paths based on
actual router prefixes and endpoint definitions.

Author: Mentor AI Testing Suite
Version: 3.0.0
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EndpointTester:
    """Corrected endpoint tester with actual paths."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.student_id = "test_student_123"
        self.parent_id = "test_parent_123"
        self.child_id = "test_child_123"
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def get_auth_token(self) -> str:
        """Get authentication token for testing."""
        if self.auth_token:
            return self.auth_token
            
        # Try to get token from login endpoint
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/login/email",
                json=login_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("token", "mock_token_12345")
                    logger.info("Authentication successful")
                    return self.auth_token
                else:
                    logger.warning(f"Login failed: {response.status}")
                    # Use mock token for testing
                    self.auth_token = "mock_token_12345"
                    return self.auth_token
        except Exception as e:
            logger.warning(f"Auth error: {e}")
            # Use mock token for testing
            self.auth_token = "mock_token_12345"
            return self.auth_token
    
    async def get_headers(self, auth_required: bool = True) -> Dict[str, str]:
        """Get request headers with optional authentication."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if auth_required:
            token = await self.get_auth_token()
            headers["Authorization"] = f"Bearer {token}"
        
        return headers
    
    async def test_endpoint(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None, 
        headers: Optional[Dict] = None,
        expected_status: int = 200,
        timeout: int = 30
    ) -> Tuple[bool, Dict[str, Any]]:
        """Test an individual endpoint with proper error handling."""
        
        if headers is None:
            headers = await self.get_headers()
        
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                json=data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                response_time = time.time() - start_time
                
                try:
                    response_data = await response.json()
                except:
                    response_data = {"raw_response": await response.text()}
                
                success = response.status == expected_status
                
                result = {
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": response.status,
                    "expected_status": expected_status,
                    "success": success,
                    "response_time": response_time,
                    "response_data": response_data,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                if not success:
                    logger.warning(
                        f"FAILED: {method} {endpoint} - "
                        f"Status: {response.status}/{expected_status} - "
                        f"Time: {response_time:.2f}s"
                    )
                    
                    # Log specific error details
                    if response.status == 422:
                        logger.error(f"Validation Error: {response_data}")
                    elif response.status == 401:
                        logger.error(f"Authentication Error")
                    elif response.status == 404:
                        logger.error(f"Endpoint Not Found")
                    elif response.status == 500:
                        logger.error(f"Server Error: {response_data}")
                else:
                    logger.info(
                        f"SUCCESS: {method} {endpoint} - "
                        f"Status: {response.status} - "
                        f"Time: {response_time:.2f}s"
                    )
                
                return success, result
                
        except asyncio.TimeoutError:
            logger.error(f"TIMEOUT: {method} {endpoint} - Timeout after {timeout}s")
            return False, {
                "endpoint": endpoint,
                "method": method,
                "status_code": 0,
                "expected_status": expected_status,
                "success": False,
                "response_time": timeout,
                "error": "Request timeout",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"ERROR: {method} {endpoint} - {str(e)}")
            return False, {
                "endpoint": endpoint,
                "method": method,
                "status_code": 0,
                "expected_status": expected_status,
                "success": False,
                "response_time": time.time() - start_time,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_health_endpoints(self):
        """Test health check endpoints."""
        logger.info("Testing health endpoints...")
        
        health_endpoints = [
            ("/", "GET", None, 200),
            ("/api/health", "GET", None, 200),
            ("/api/diagnostic-test/health", "GET", None, 200),
            ("/api/rag/pipeline/status", "GET", None, 200),
            ("/api/analytics/health", "GET", None, 200),
            ("/api/guidance/health", "GET", None, 200),
            ("/api/auth/health", "GET", None, 200),
            ("/api/ai-features/health", "GET", None, 200),
            ("/api/token-usage/health", "GET", None, 200),
            ("/api/study-center/health", "GET", None, 200),
        ]
        
        for endpoint, method, data, expected in health_endpoints:
            success, result = await self.test_endpoint(method, endpoint, data, expected_status=expected)
            self.test_results.append(result)
    
    async def test_auth_endpoints(self):
        """Test authentication endpoints with correct paths."""
        logger.info("Testing authentication endpoints...")
        
        auth_endpoints = [
            # Registration endpoints (from auth_router.py - no prefix)
            ("/register/parent/email", "POST", {
                "email": "newuser@example.com",
                "password": "newpassword123",
                "full_name": "New User",
                "language": "en"
            }, 201),
            
            ("/register/parent/phone", "POST", {
                "phone": "+919876543210",
                "language": "en"
            }, 201),
            
            ("/register/parent/google", "POST", {
                "id_token": "mock_google_token_12345",
                "language": "en"
            }, 201),
            
            # Login endpoints (from login_router.py - no prefix)
            ("/login/email", "POST", {
                "email": "test@example.com",
                "password": "testpassword123"
            }, 200),
            
            ("/login/phone", "POST", {
                "phone": "+919876543210",
                "otp": "123456"
            }, 200),
            
            ("/login/google", "POST", {
                "id_token": "mock_google_token_12345"
            }, 200),
            
            # Token management
            ("/token/refresh", "POST", {
                "refresh_token": "mock_refresh_token"
            }, 200),
            
            # Logout
            ("/logout", "POST", {}, 200),
            
            # Profile endpoints
            ("/me", "GET", None, 200),
        ]
        
        for endpoint, method, data, expected in auth_endpoints:
            # Don't use auth headers for registration and login
            auth_required = not endpoint.startswith(("/register/", "/login/"))
            headers = await self.get_headers(auth_required=auth_required)
            
            success, result = await self.test_endpoint(method, endpoint, data, headers, expected)
            self.test_results.append(result)
    
    async def test_diagnostic_test_endpoints(self):
        """Test diagnostic test endpoints with proper validation."""
        logger.info("Testing diagnostic test endpoints...")
        
        # Test generation request
        test_gen_request = {
            "exam_type": "JEE_MAIN",
            "student_id": self.student_id,
            "async_generation": False
        }
        
        diagnostic_endpoints = [
            # Generate test
            ("/api/diagnostic-test/generate", "POST", test_gen_request, 201),
            
            # Generate async test
            ("/api/diagnostic-test/generate-async", "POST", test_gen_request, 202),
            
            # Get test metadata
            ("/api/diagnostic-test/test_mock_123/metadata", "GET", None, 200),
            
            # Get student tests
            (f"/api/diagnostic-test/student/{self.student_id}", "GET", None, 200),
            
            # Schedule test
            ("/api/diagnostic-test/schedule", "POST", {
                "child_id": self.child_id,
                "exam_type": "JEE_MAIN",
                "scheduled_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
                "test_id": "test_scheduled_123"
            }, 201),
        ]
        
        for endpoint, method, data, expected in diagnostic_endpoints:
            success, result = await self.test_endpoint(method, endpoint, data, expected_status=expected)
            self.test_results.append(result)
    
    async def test_rag_endpoints(self):
        """Test RAG endpoints with proper validation."""
        logger.info("Testing RAG endpoints...")
        
        # Valid RAG request
        rag_request = {
            "topic": "Limits and Continuity",
            "exam_type": "JEE_MAIN",
            "difficulty": "medium",
            "num_questions": 5,
            "include_explanations": True,
            "question_type": "single_correct",
            "use_cache": True
        }
        
        # Valid batch request
        batch_request = {
            "topics": ["Calculus", "Algebra", "Trigonometry"],
            "exam_type": "JEE_MAIN",
            "difficulty": "medium",
            "questions_per_topic": 3,
            "include_explanations": True,
            "question_type": "single_correct"
        }
        
        rag_endpoints = [
            # Generate questions
            ("/api/rag/generate-questions", "POST", rag_request, 200),
            
            # Generate batch
            ("/api/rag/generate-batch", "POST", batch_request, 200),
            
            # Build context
            ("/api/rag/context/build", "POST", {
                "topic": "Thermodynamics",
                "exam_type": "JEE_MAIN"
            }, 200),
            
            # Preview context
            ("/api/rag/context/preview", "POST", {
                "topic": "Mechanics",
                "exam_type": "JEE_ADVANCED"
            }, 200),
            
            # Get metrics
            ("/api/rag/metrics", "GET", None, 200),
        ]
        
        for endpoint, method, data, expected in rag_endpoints:
            success, result = await self.test_endpoint(method, endpoint, data, expected_status=expected)
            self.test_results.append(result)
    
    async def test_academic_guidance_endpoints(self):
        """Test academic guidance endpoints with proper validation."""
        logger.info("Testing academic guidance endpoints...")
        
        # Activity log request
        activity_request = {
            "student_id": self.student_id,
            "session_id": "session_123",
            "activities": [
                {
                    "activity_type": "topic_study",
                    "topic_id": "topic_calculus_001",
                    "subject": "Mathematics",
                    "chapter": "Calculus",
                    "sequence_number": 1,
                    "access_time": datetime.utcnow().isoformat(),
                    "time_spent_minutes": 45,
                    "completion_percentage": 80.0
                }
            ],
            "session_start": datetime.utcnow().isoformat(),
            "session_end": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            "total_duration_minutes": 60,
            "device_type": "desktop",
            "browser": "Chrome"
        }
        
        guidance_endpoints = [
            # Log activity
            ("/api/guidance/activity/log", "POST", activity_request, 201),
            
            # Trigger analysis
            (f"/api/guidance/analyze/{self.student_id}", "POST", None, 200),
        ]
        
        for endpoint, method, data, expected in guidance_endpoints:
            success, result = await self.test_endpoint(method, endpoint, data, expected_status=expected)
            self.test_results.append(result)
    
    async def test_analytics_endpoints(self):
        """Test analytics endpoints."""
        logger.info("Testing analytics endpoints...")
        
        analytics_endpoints = [
            # Get analytics
            (f"/api/analytics/student/{self.student_id}", "GET", None, 200),
            (f"/api/analytics/test/test_123", "GET", None, 200),
            (f"/api/analytics/analytics_123", "GET", None, 200),
            (f"/api/analytics/analytics_123/insights", "GET", None, 200),
            (f"/api/analytics/analytics_123/weak-topics", "GET", None, 200),
        ]
        
        for endpoint, method, data, expected in analytics_endpoints:
            success, result = await self.test_endpoint(method, endpoint, data, expected_status=expected)
            self.test_results.append(result)
    
    async def test_other_key_endpoints(self):
        """Test other key endpoints."""
        logger.info("Testing other key endpoints...")
        
        other_endpoints = [
            # Token usage
            ("/api/token-usage/limits/student/test_student_123", "GET", None, 200),
            ("/api/token-usage/parent", "GET", None, 200),
            ("/api/token-usage/student/test_student_123", "GET", None, 200),
            ("/api/token-usage/summary/parent", "GET", None, 200),
            
            # Study center
            ("/api/study-center/topics", "GET", None, 200),
            ("/api/study-center/progress/test_student_123", "GET", None, 200),
            ("/api/study-center/journey/test_student_123", "GET", None, 200),
            
            # AI features
            ("/api/ai-features/dashboard", "GET", None, 200),
            ("/api/ai-features/insights", "GET", None, 200),
            
            # Embeddings
            ("/api/vector-search/embeddings/status", "GET", None, 200),
            ("/api/vector-search/index/status", "GET", None, 200),
            
            # Vidhya AI
            ("/api/vidhya/health", "GET", None, 200),
            ("/api/vidhya/languages", "GET", None, 200),
        ]
        
        for endpoint, method, data, expected in other_endpoints:
            success, result = await self.test_endpoint(method, endpoint, data, expected_status=expected)
            self.test_results.append(result)
    
    async def run_all_tests(self):
        """Run all endpoint tests."""
        logger.info("Starting comprehensive endpoint testing with corrected paths...")
        
        test_methods = [
            self.test_health_endpoints,
            self.test_auth_endpoints,
            self.test_diagnostic_test_endpoints,
            self.test_rag_endpoints,
            self.test_academic_guidance_endpoints,
            self.test_analytics_endpoints,
            self.test_other_key_endpoints,
        ]
        
        for test_method in test_methods:
            try:
                await test_method()
                await asyncio.sleep(0.1)  # Small delay between tests
            except Exception as e:
                logger.error(f"Test method {test_method.__name__} failed: {e}")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - successful_tests
        
        # Group by status code
        status_counts = {}
        for result in self.test_results:
            status = result["status_code"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Group by endpoint type
        endpoint_groups = {}
        for result in self.test_results:
            endpoint = result["endpoint"]
            endpoint_type = endpoint.split("/")[1] if "/" in endpoint else "root"
            if endpoint_type not in endpoint_groups:
                endpoint_groups[endpoint_type] = {"total": 0, "success": 0}
            endpoint_groups[endpoint_type]["total"] += 1
            if result["success"]:
                endpoint_groups[endpoint_type]["success"] += 1
        
        # Calculate response time stats
        response_times = [r["response_time"] for r in self.test_results if r.get("response_time")]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
                "timestamp": datetime.utcnow().isoformat()
            },
            "status_distribution": status_counts,
            "endpoint_performance": endpoint_groups,
            "response_time_stats": {
                "average": avg_response_time,
                "minimum": min_response_time,
                "maximum": max_response_time
            },
            "failed_tests": [r for r in self.test_results if not r["success"]],
            "all_results": self.test_results
        }
        
        return report
    
    async def save_report(self, filename: str = "endpoint_test_results_corrected.json"):
        """Save test report to file."""
        report = self.generate_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Test report saved to {filename}")
        
        # Print summary
        summary = report["summary"]
        print(f"\n{'='*60}")
        print("CORRECTED ENDPOINT TESTING SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Successful: {summary['successful_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Average Response Time: {report['response_time_stats']['average']:.2f}s")
        print(f"{'='*60}")
        
        # Print status distribution
        print("\nStatus Code Distribution:")
        for status, count in report["status_distribution"].items():
            print(f"  {status}: {count}")
        
        # Print endpoint performance
        print("\nEndpoint Performance:")
        for endpoint_type, stats in report["endpoint_performance"].items():
            success_rate = (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
            print(f"  {endpoint_type}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")

async def main():
    """Main function to run all tests."""
    async with EndpointTester() as tester:
        await tester.run_all_tests()
        await tester.save_report()

if __name__ == "__main__":
    asyncio.run(main())