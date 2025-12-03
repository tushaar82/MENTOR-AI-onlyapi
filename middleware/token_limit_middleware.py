"""
Token Limiting Middleware for Mentor AI Platform.

This module provides comprehensive token limiting middleware
that enforces token usage limits for students based on their subscription plans.

Features:
- Token usage validation before processing requests
- Automatic token usage tracking after responses
- Support for different AI endpoints
- Integration with subscription service
- Comprehensive error handling

Author: Mentor AI Team
Version: 1.0.0
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from services.token_usage_service import get_token_usage_service
from middleware.auth_middleware import get_current_user
from services.child_service import ChildService

# Configure logging
logger = logging.getLogger(__name__)

# AI endpoints that require token limiting
AI_ENDPOINTS = [
    "/api/vidhya/chat/send",
    "/api/rag/generate-questions",
    "/api/rag/generate-batch",
    "/api/vector-search/embeddings/generate",
    "/api/vector-search/embeddings/batch",
    "/api/diagnostic-test/generate",
    "/api/schedule/generate",
    "/api/ai/tutor/ask",
    "/api/ai/recommend/topics",
    "/api/ai/readiness",
    "/api/ai/mistake-analysis"
]

# Token estimation factors (rough estimates)
TOKEN_ESTIMATION_FACTORS = {
    "/api/vidhya/chat/send": {
        "input_factor": 0.25,  # 1 token per 4 characters
        "output_base": 150,     # Base tokens for response
        "output_factor": 0.25   # Additional tokens based on input
    },
    "/api/rag/generate-questions": {
        "input_factor": 0.25,
        "output_base": 500,
        "output_factor": 0.5
    },
    "/api/rag/generate-batch": {
        "input_factor": 0.25,
        "output_base": 2000,
        "output_factor": 2.0
    },
    "/api/vector-search/embeddings/generate": {
        "input_factor": 0.25,
        "output_base": 50,
        "output_factor": 0.1
    },
    "/api/diagnostic-test/generate": {
        "input_factor": 0.25,
        "output_base": 1000,
        "output_factor": 1.0
    },
    "/api/schedule/generate": {
        "input_factor": 0.25,
        "output_base": 800,
        "output_factor": 0.8
    }
}


class TokenLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for enforcing token usage limits.
    
    This middleware intercepts requests to AI endpoints,
    validates token usage before processing, and tracks
    actual token usage after responses.
    
    Attributes:
        token_service: TokenUsageService instance
        child_service: ChildService instance
    
    Example:
        >>> middleware = TokenLimitMiddleware()
        >>> response = await middleware.dispatch(request, call_next)
    """
    
    def __init__(self, app):
        """
        Initialize Token Limit Middleware.
        
        Args:
            app: FastAPI application instance
        """
        super().__init__(app)
        self.token_service = get_token_usage_service()
        self.child_service = ChildService()
        
        logger.info("TokenLimitMiddleware initialized")
        logger.info(f"Monitoring {len(AI_ENDPOINTS)} AI endpoints for token limiting")
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request with token limiting.
        
        This method checks token limits before processing requests
        and tracks actual token usage after responses.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware in chain
        
        Returns:
            HTTP response or token limit error
        """
        try:
            # Skip token limiting for non-AI endpoints
            if not self._is_ai_endpoint(request.url.path):
                return await call_next(request)
            
            # Skip for health checks and docs
            if request.url.path in ["/health", "/", "/api/docs", "/api/redoc", "/api/openapi.json"]:
                return await call_next(request)
            
            # Extract user and student information
            auth_info = await self._extract_auth_info(request)
            if not auth_info:
                # No auth info, proceed without token limiting (will be handled by auth middleware)
                return await call_next(request)
            
            user_id = auth_info.get("user_id")
            student_id = auth_info.get("student_id")
            parent_id = auth_info.get("parent_id")
            
            # If no student_id, try to extract from request
            if not student_id:
                student_id = await self._extract_student_id_from_request(request, user_id)
            
            # If still no student_id, proceed without token limiting
            if not student_id:
                logger.warning(f"No student_id found for request: {request.url.path}")
                return await call_next(request)
            
            # Estimate tokens needed for this request
            estimated_tokens = self._estimate_tokens(request)
            
            # Check token limits
            limit_check = await self.token_service.check_token_limit(
                student_id=student_id,
                tokens_requested=estimated_tokens,
                parent_id=parent_id
            )
            
            if not limit_check["allowed"]:
                logger.warning(
                    f"Token limit exceeded for student {student_id}: "
                    f"requested={estimated_tokens}, "
                    f"daily_remaining={limit_check['daily_remaining']}, "
                    f"monthly_remaining={limit_check['monthly_remaining']}"
                )
                
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "success": False,
                        "error": "Token limit exceeded",
                        "message": "You have exceeded your token limit. Please upgrade your plan or try again tomorrow.",
                        "tokens_requested": estimated_tokens,
                        "daily_remaining": limit_check["daily_remaining"],
                        "monthly_remaining": limit_check["monthly_remaining"],
                        "daily_limit": limit_check["daily_limit"],
                        "monthly_limit": limit_check["monthly_limit"],
                        "reset_time": self._get_reset_time()
                    }
                )
            
            # Process request
            response = await call_next(request)
            
            # Track actual token usage if available
            if hasattr(response, 'headers') and 'x-tokens-used' in response.headers:
                actual_tokens = int(response.headers['x-tokens-used'])
                
                # Track usage
                success = await self.token_service.track_token_usage(
                    student_id=student_id,
                    tokens_used=actual_tokens,
                    interaction_type=self._get_interaction_type(request),
                    parent_id=parent_id,
                    metadata={
                        "endpoint": request.url.path,
                        "method": request.method,
                        "user_agent": request.headers.get("user-agent"),
                        "estimated_tokens": estimated_tokens,
                        "actual_tokens": actual_tokens
                    }
                )
                
                if success:
                    # Add token usage info to response headers
                    response.headers["x-token-daily-remaining"] = str(limit_check["daily_remaining"] - actual_tokens)
                    response.headers["x-token-monthly-remaining"] = str(limit_check["monthly_remaining"] - actual_tokens)
                    response.headers["x-token-daily-used"] = str(limit_check["daily_used"] + actual_tokens)
                    response.headers["x-token-monthly-used"] = str(limit_check["monthly_used"] + actual_tokens)
                    
                    logger.info(
                        f"Token usage tracked for student {student_id}: "
                        f"tokens={actual_tokens}, "
                        f"daily_remaining={limit_check['daily_remaining'] - actual_tokens}"
                    )
                else:
                    logger.error(f"Failed to track token usage for student {student_id}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error in token limit middleware: {e}")
            logger.exception("Full traceback:")
            # Continue with request on error
            return await call_next(request)
    
    def _is_ai_endpoint(self, path: str) -> bool:
        """
        Check if endpoint requires token limiting.
        
        Args:
            path: Request path
        
        Returns:
            True if endpoint requires token limiting
        """
        # Check exact matches first
        if path in AI_ENDPOINTS:
            return True
        
        # Check pattern matches
        for endpoint in AI_ENDPOINTS:
            if "{" in endpoint:
                # Convert to regex pattern
                pattern = endpoint.replace("{", "[^/]+").replace("}", "[^/]*")
                import re
                if re.match(f"^{pattern}$", path):
                    return True
        
        return False
    
    async def _extract_auth_info(self, request: Request) -> Optional[Dict[str, str]]:
        """
        Extract authentication information from request.
        
        Args:
            request: HTTP request
        
        Returns:
            Dict with user_id, student_id, parent_id or None
        """
        try:
            # Try to get from request state (set by auth middleware)
            if hasattr(request.state, 'user_id'):
                user_id = request.state.user_id
                student_id = getattr(request.state, 'student_id', None)
                parent_id = getattr(request.state, 'parent_id', None)
                
                return {
                    "user_id": user_id,
                    "student_id": student_id,
                    "parent_id": parent_id
                }
            
            # Try to extract from Authorization header
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                # This would require JWT decoding - for now, return None
                # and let the auth middleware handle it
                pass
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting auth info: {e}")
            return None
    
    async def _extract_student_id_from_request(
        self,
        request: Request,
        user_id: str
    ) -> Optional[str]:
        """
        Extract student ID from request body or parameters.
        
        Args:
            request: HTTP request
            user_id: Authenticated user ID
        
        Returns:
            Student ID if found, None otherwise
        """
        try:
            # For POST requests, try to extract from body
            if request.method in ["POST", "PUT", "PATCH"]:
                try:
                    body = await request.json()
                    
                    # Common student_id field names
                    for field in ["student_id", "child_id", "student", "child"]:
                        if field in body:
                            return body[field]
                    
                    # For chat endpoints, try to get from session_id
                    if "session_id" in body:
                        # This would require looking up the session
                        # For now, return None
                        pass
                        
                except Exception:
                    # Invalid JSON body
                    pass
            
            # For GET requests, try to extract from query parameters
            elif request.method == "GET":
                query_params = request.query_params
                for field in ["student_id", "child_id", "student", "child"]:
                    if field in query_params:
                        return query_params[field]
            
            # Try to get child profile for this user
            try:
                child_profile = self.child_service.get_child_profile(user_id)
                return child_profile.child_id if child_profile else None
            except Exception:
                pass
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting student ID from request: {e}")
            return None
    
    def _estimate_tokens(self, request: Request) -> int:
        """
        Estimate tokens needed for this request.
        
        Args:
            request: HTTP request
        
        Returns:
            Estimated token count
        """
        try:
            path = request.url.path
            
            # Get estimation factor for this endpoint
            estimation = TOKEN_ESTIMATION_FACTORS.get(path, {
                "input_factor": 0.25,
                "output_base": 100,
                "output_factor": 0.25
            })
            
            # Estimate input tokens (rough calculation)
            input_tokens = 0
            if request.method in ["POST", "PUT", "PATCH"]:
                # Try to get content length
                content_length = request.headers.get("content-length")
                if content_length:
                    input_tokens = int(content_length) * estimation["input_factor"]
                else:
                    # Default estimate
                    input_tokens = 1000 * estimation["input_factor"]
            
            # Calculate total estimated tokens
            estimated_tokens = int(
                estimation["output_base"] +
                input_tokens +
                (input_tokens * estimation["output_factor"])
            )
            
            # Add safety margin (20%)
            estimated_tokens = int(estimated_tokens * 1.2)
            
            logger.debug(f"Estimated tokens for {path}: {estimated_tokens}")
            return estimated_tokens
            
        except Exception as e:
            logger.error(f"Error estimating tokens: {e}")
            # Return conservative estimate
            return 1000
    
    def _get_interaction_type(self, request: Request) -> str:
        """
        Get interaction type for tracking.
        
        Args:
            request: HTTP request
        
        Returns:
            Interaction type string
        """
        path = request.url.path
        
        # Map endpoints to interaction types
        endpoint_mapping = {
            "/api/vidhya/chat/send": "vidhya_chat",
            "/api/rag/generate-questions": "question_generation",
            "/api/rag/generate-batch": "batch_question_generation",
            "/api/vector-search/embeddings/generate": "embedding_generation",
            "/api/vector-search/embeddings/batch": "batch_embedding_generation",
            "/api/diagnostic-test/generate": "test_generation",
            "/api/schedule/generate": "schedule_generation",
            "/api/ai/tutor/ask": "ai_tutor",
            "/api/ai/recommend/topics": "topic_recommendation",
            "/api/ai/readiness": "readiness_assessment",
            "/api/ai/mistake-analysis": "mistake_analysis"
        }
        
        return endpoint_mapping.get(path, "unknown")
    
    def _get_reset_time(self) -> str:
        """
        Get next reset time for daily limits.
        
        Returns:
            ISO string of next reset time
        """
        now = datetime.utcnow()
        # Next midnight UTC
        tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        return tomorrow.isoformat()


# Factory function for creating middleware
def create_token_limit_middleware(app):
    """
    Create token limit middleware instance.
    
    Args:
        app: FastAPI application
    
    Returns:
        TokenLimitMiddleware instance
    """
    return TokenLimitMiddleware(app)


# Module initialization
logger.info("Token Limit Middleware module loaded")
logger.info(f"Configured for {len(AI_ENDPOINTS)} AI endpoints")