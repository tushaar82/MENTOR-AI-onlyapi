"""
Token Usage Tracking Service for Mentor AI Platform.

This module provides comprehensive token usage tracking and limiting
for students based on their subscription plans.

Features:
- Daily and monthly token usage tracking
- Subscription-based token limits
- Token usage validation
- Firestore persistence
- Comprehensive error handling

Author: Mentor AI Team
Version: 1.0.0
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from google.cloud import firestore
from services.subscription_service import SubscriptionService
from utils.firebase_config import get_firestore_client

# Configure logging
logger = logging.getLogger(__name__)

# Firestore collections
TOKEN_USAGE_COLLECTION = "token_usage"


class TokenUsageService:
    """
    Service for tracking and managing token usage for students.
    
    This service provides token usage tracking, limit validation,
    and usage statistics for students based on their subscription plans.
    
    Attributes:
        db: Firestore database client
        subscription_service: Subscription service instance
    
    Example:
        >>> service = TokenUsageService()
        >>> check = service.check_token_limit("student123", 500)
        >>> if check["allowed"]:
        ...     # Process request
    """
    
    def __init__(self):
        """
        Initialize Token Usage Service.
        
        This constructor initializes the Firestore client and
        subscription service for token management.
        """
        logger.info("Initializing TokenUsageService")
        
        # Initialize Firestore client
        self.db = get_firestore_client()
        
        # Initialize subscription service
        self.subscription_service = SubscriptionService()
        
        logger.info("TokenUsageService initialized successfully")
    
    async def check_token_limit(
        self,
        student_id: str,
        tokens_requested: int,
        parent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check if student has sufficient tokens for this request.
        
        This method validates token usage against daily and monthly limits
        based on the student's subscription plan.
        
        Args:
            student_id: Student ID to check
            tokens_requested: Number of tokens needed for this request
            parent_id: Optional parent ID for subscription lookup
        
        Returns:
            Dict containing:
            - allowed: Whether request is allowed
            - daily_remaining: Remaining daily tokens
            - monthly_remaining: Remaining monthly tokens
            - tokens_requested: Tokens requested for this request
        
        Example:
            >>> service = TokenUsageService()
            >>> result = service.check_token_limit("student123", 500)
            >>> print(f"Allowed: {result['allowed']}")
        """
        try:
            logger.info(f"Checking token limit for student: {student_id}, tokens: {tokens_requested}")
            
            # Get current usage
            daily_usage = await self._get_daily_usage(student_id)
            monthly_usage = await self._get_monthly_usage(student_id)
            
            # Get student's subscription limits
            limits = await self._get_student_token_limits(student_id, parent_id)
            
            # Calculate remaining tokens
            daily_remaining = max(0, limits["daily"] - daily_usage)
            monthly_remaining = max(0, limits["monthly"] - monthly_usage)
            
            # Check if request is allowed
            allowed = (
                tokens_requested <= daily_remaining and
                tokens_requested <= monthly_remaining
            )
            
            result = {
                "allowed": allowed,
                "daily_remaining": daily_remaining,
                "monthly_remaining": monthly_remaining,
                "tokens_requested": tokens_requested,
                "daily_limit": limits["daily"],
                "monthly_limit": limits["monthly"],
                "daily_used": daily_usage,
                "monthly_used": monthly_usage
            }
            
            logger.info(
                f"Token limit check for {student_id}: allowed={allowed}, "
                f"daily={daily_usage}/{limits['daily']}, "
                f"monthly={monthly_usage}/{limits['monthly']}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error checking token limit for student {student_id}: {e}")
            logger.exception("Full traceback:")
            # Return conservative result on error
            return {
                "allowed": False,
                "daily_remaining": 0,
                "monthly_remaining": 0,
                "tokens_requested": tokens_requested,
                "error": "Failed to check token limits"
            }
    
    async def track_token_usage(
        self,
        student_id: str,
        tokens_used: int,
        interaction_type: str,
        parent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Record token usage for a student.
        
        This method updates daily and monthly token usage counters
        for a student after processing an AI interaction.
        
        Args:
            student_id: Student ID
            tokens_used: Number of tokens consumed
            interaction_type: Type of interaction (vidhya_chat, question_generation, etc.)
            parent_id: Optional parent ID
            metadata: Additional metadata for tracking
        
        Returns:
            True if tracking successful, False otherwise
        
        Example:
            >>> service = TokenUsageService()
            >>> success = service.track_token_usage("student123", 250, "vidhya_chat")
            >>> print(f"Tracking successful: {success}")
        """
        try:
            logger.info(f"Tracking token usage for student: {student_id}, tokens: {tokens_used}")
            
            # Get current timestamp
            now = datetime.utcnow()
            date_key = now.strftime("%Y-%m-%d")
            month_key = now.strftime("%Y-%m")
            
            # Create usage record
            usage_record = {
                "student_id": student_id,
                "parent_id": parent_id,
                "tokens_used": tokens_used,
                "interaction_type": interaction_type,
                "metadata": metadata or {},
                "timestamp": now,
                "date_key": date_key,
                "month_key": month_key
            }
            
            # Update daily usage
            await self._update_daily_usage(student_id, date_key, tokens_used, interaction_type)
            
            # Update monthly usage
            await self._update_monthly_usage(student_id, month_key, tokens_used, interaction_type)
            
            # Log individual usage record
            await self._log_individual_usage(usage_record)
            
            logger.info(f"Token usage tracked successfully for student: {student_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking token usage for student {student_id}: {e}")
            logger.exception("Full traceback:")
            return False
    
    async def get_student_token_usage(
        self,
        student_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive token usage for a student.
        
        Args:
            student_id: Student ID
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
        
        Returns:
            Dict containing usage statistics
        
        Example:
            >>> service = TokenUsageService()
            >>> usage = service.get_student_token_usage("student123")
            >>> print(f"Daily usage: {usage['daily']['used']}")
        """
        try:
            logger.info(f"Getting token usage for student: {student_id}")
            
            # Get current usage
            daily_usage = await self._get_daily_usage(student_id)
            monthly_usage = await self._get_monthly_usage(student_id)
            
            # Get limits
            limits = await self._get_student_token_limits(student_id)
            
            # Calculate remaining
            daily_remaining = max(0, limits["daily"] - daily_usage)
            monthly_remaining = max(0, limits["monthly"] - monthly_usage)
            
            # Get usage history if date range provided
            history = []
            if start_date or end_date:
                history = await self._get_usage_history(student_id, start_date, end_date)
            
            result = {
                "student_id": student_id,
                "daily": {
                    "used": daily_usage,
                    "limit": limits["daily"],
                    "remaining": daily_remaining,
                    "percentage": (daily_usage / limits["daily"]) * 100 if limits["daily"] > 0 else 0
                },
                "monthly": {
                    "used": monthly_usage,
                    "limit": limits["monthly"],
                    "remaining": monthly_remaining,
                    "percentage": (monthly_usage / limits["monthly"]) * 100 if limits["monthly"] > 0 else 0
                },
                "history": history,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Retrieved token usage for student {student_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error getting token usage for student {student_id}: {e}")
            logger.exception("Full traceback:")
            raise
    
    async def reset_daily_usage(self, student_id: str):
        """
        Reset daily token usage for a student (typically called at midnight).
        
        Args:
            student_id: Student ID to reset
        """
        try:
            date_key = datetime.utcnow().strftime("%Y-%m-%d")
            
            # Reset daily usage
            doc_ref = (
                self.db.collection(TOKEN_USAGE_COLLECTION)
                .document(student_id)
                .collection("daily")
                .document(date_key)
            )
            doc_ref.set({
                "tokens_used": 0,
                "requests": 0,
                "last_reset": datetime.utcnow(),
                "date_key": date_key
            })
            
            logger.info(f"Reset daily usage for student: {student_id}")
            
        except Exception as e:
            logger.error(f"Error resetting daily usage for student {student_id}: {e}")
    
    async def reset_monthly_usage(self, student_id: str):
        """
        Reset monthly token usage for a student (typically called on 1st of month).
        
        Args:
            student_id: Student ID to reset
        """
        try:
            month_key = datetime.utcnow().strftime("%Y-%m")
            
            # Reset monthly usage
            doc_ref = (
                self.db.collection(TOKEN_USAGE_COLLECTION)
                .document(student_id)
                .collection("monthly")
                .document(month_key)
            )
            doc_ref.set({
                "tokens_used": 0,
                "requests": 0,
                "last_reset": datetime.utcnow(),
                "month_key": month_key
            })
            
            logger.info(f"Reset monthly usage for student: {student_id}")
            
        except Exception as e:
            logger.error(f"Error resetting monthly usage for student {student_id}: {e}")
    
    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================
    
    async def _get_daily_usage(self, student_id: str) -> int:
        """Get daily token usage for a student."""
        try:
            date_key = datetime.utcnow().strftime("%Y-%m-%d")
            
            doc_ref = (
                self.db.collection(TOKEN_USAGE_COLLECTION)
                .document(student_id)
                .collection("daily")
                .document(date_key)
            )
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                return data.get("tokens_used", 0)
            else:
                # Create daily record if it doesn't exist
                await self.reset_daily_usage(student_id)
                return 0
                
        except Exception as e:
            logger.error(f"Error getting daily usage for student {student_id}: {e}")
            return 0
    
    async def _get_monthly_usage(self, student_id: str) -> int:
        """Get monthly token usage for a student."""
        try:
            month_key = datetime.utcnow().strftime("%Y-%m")
            
            doc_ref = (
                self.db.collection(TOKEN_USAGE_COLLECTION)
                .document(student_id)
                .collection("monthly")
                .document(month_key)
            )
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                return data.get("tokens_used", 0)
            else:
                # Create monthly record if it doesn't exist
                await self.reset_monthly_usage(student_id)
                return 0
                
        except Exception as e:
            logger.error(f"Error getting monthly usage for student {student_id}: {e}")
            return 0
    
    async def _get_student_token_limits(
        self,
        student_id: str,
        parent_id: Optional[str] = None
    ) -> Dict[str, int]:
        """Get token limits for a student based on their subscription."""
        try:
            # Default limits (free plan)
            default_limits = {"daily": 1000, "monthly": 10000}
            
            if not parent_id:
                # Try to get parent_id from student record
                parent_id = await self._get_student_parent_id(student_id)
            
            if not parent_id:
                logger.warning(f"No parent_id found for student: {student_id}, using default limits")
                return default_limits
            
            # Get subscription status
            status = self.subscription_service.check_subscription_status(parent_id)
            
            if status and hasattr(status, 'plan_id'):
                plan = self.subscription_service.get_plan_by_id(status.plan_id)
                if hasattr(plan, 'token_limits'):
                    return plan.token_limits
            
            logger.info(f"Using default token limits for student: {student_id}")
            return default_limits
            
        except Exception as e:
            logger.error(f"Error getting token limits for student {student_id}: {e}")
            return {"daily": 1000, "monthly": 10000}
    
    async def _get_student_parent_id(self, student_id: str) -> Optional[str]:
        """Get parent ID for a student from child profile."""
        try:
            doc_ref = self.db.collection("children").document(student_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                return data.get("parent_id")
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting parent ID for student {student_id}: {e}")
            return None
    
    async def _update_daily_usage(
        self,
        student_id: str,
        date_key: str,
        tokens_used: int,
        interaction_type: str
    ):
        """Update daily token usage for a student."""
        try:
            doc_ref = (
                self.db.collection(TOKEN_USAGE_COLLECTION)
                .document(student_id)
                .collection("daily")
                .document(date_key)
            )
            
            # Use Firestore transaction for atomic update
            transaction = self.db.transaction()
            
            @firestore.transactional
            def update_daily(transaction):
                doc = doc_ref.get(transaction=transaction)
                
                if doc.exists:
                    data = doc.to_dict()
                    current_tokens = data.get("tokens_used", 0)
                    current_requests = data.get("requests", 0)
                    
                    new_data = {
                        "tokens_used": current_tokens + tokens_used,
                        "requests": current_requests + 1,
                        "last_updated": datetime.utcnow(),
                        "date_key": date_key
                    }
                else:
                    new_data = {
                        "tokens_used": tokens_used,
                        "requests": 1,
                        "created_at": datetime.utcnow(),
                        "last_updated": datetime.utcnow(),
                        "date_key": date_key
                    }
                
                transaction.set(doc_ref, new_data)
                return new_data
            
            update_daily(transaction)
            
        except Exception as e:
            logger.error(f"Error updating daily usage for student {student_id}: {e}")
    
    async def _update_monthly_usage(
        self,
        student_id: str,
        month_key: str,
        tokens_used: int,
        interaction_type: str
    ):
        """Update monthly token usage for a student."""
        try:
            doc_ref = (
                self.db.collection(TOKEN_USAGE_COLLECTION)
                .document(student_id)
                .collection("monthly")
                .document(month_key)
            )
            
            # Use Firestore transaction for atomic update
            transaction = self.db.transaction()
            
            @firestore.transactional
            def update_monthly(transaction):
                doc = doc_ref.get(transaction=transaction)
                
                if doc.exists:
                    data = doc.to_dict()
                    current_tokens = data.get("tokens_used", 0)
                    current_requests = data.get("requests", 0)
                    
                    new_data = {
                        "tokens_used": current_tokens + tokens_used,
                        "requests": current_requests + 1,
                        "last_updated": datetime.utcnow(),
                        "month_key": month_key
                    }
                else:
                    new_data = {
                        "tokens_used": tokens_used,
                        "requests": 1,
                        "created_at": datetime.utcnow(),
                        "last_updated": datetime.utcnow(),
                        "month_key": month_key
                    }
                
                transaction.set(doc_ref, new_data)
                return new_data
            
            update_monthly(transaction)
            
        except Exception as e:
            logger.error(f"Error updating monthly usage for student {student_id}: {e}")
    
    async def _log_individual_usage(self, usage_record: Dict[str, Any]):
        """Log individual usage record for audit trail."""
        try:
            # Add to individual usage subcollection
            doc_ref = (
                self.db.collection(TOKEN_USAGE_COLLECTION)
                .document(usage_record["student_id"])
                .collection("individual_usage")
                .document()
            )
            doc_ref.set(usage_record)
            
        except Exception as e:
            logger.error(f"Error logging individual usage: {e}")
    
    async def _get_usage_history(
        self,
        student_id: str,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> list:
        """Get usage history for a student within date range."""
        try:
            query = (
                self.db.collection(TOKEN_USAGE_COLLECTION)
                .document(student_id)
                .collection("individual_usage")
                .order_by("timestamp", direction="DESCENDING")
            )
            
            if start_date:
                query = query.where("timestamp", ">=", start_date)
            
            if end_date:
                query = query.where("timestamp", "<=", end_date)
            
            # Limit to last 100 records
            query = query.limit(100)
            
            history = []
            for doc in query.stream():
                data = doc.to_dict()
                history.append(data)
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting usage history for student {student_id}: {e}")
            return []


# Singleton instance
_token_usage_service: Optional[TokenUsageService] = None


def get_token_usage_service() -> TokenUsageService:
    """
    Get or create singleton TokenUsageService instance.
    
    Returns:
        TokenUsageService instance
    """
    global _token_usage_service
    
    if _token_usage_service is None:
        logger.info("Creating new TokenUsageService singleton instance")
        _token_usage_service = TokenUsageService()
    
    return _token_usage_service


# Module initialization
logger.info("Token Usage Service module loaded")