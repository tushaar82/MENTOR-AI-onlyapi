"""
Subscription Management Service for Mentor AI Platform.

This module handles the complete subscription lifecycle including activation,
status checking, cancellation, and subscription history management.

Features:
- Load and cache subscription plans
- Activate new subscriptions
- Check subscription status
- Cancel subscriptions
- Subscription history management
- Firestore integration
- Comprehensive error handling

Author: Mentor AI Team
Version: 1.0.0

Example Usage:
    >>> from services.subscription_service import SubscriptionService
    >>> 
    >>> # Initialize service
    >>> service = SubscriptionService()
    >>> 
    >>> # Activate subscription
    >>> subscription = service.activate_subscription(
    ...     parent_id="parent_abc123",
    ...     plan_id="premium_monthly",
    ...     payment_id="pay_xyz789",
    ...     order_id="order_xyz789"
    ... )
    >>> 
    >>> # Check status
    >>> status = service.check_subscription_status("parent_abc123")
    >>> print(f"Active: {status.is_active}, Days: {status.days_remaining}")
    >>> 
    >>> # Check if premium
    >>> is_premium = service.is_premium_active("parent_abc123")
"""

import json
import logging
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

from google.cloud import firestore

from models.payment_models import (
    SubscriptionPlan,
    SubscriptionDetails,
    SubscriptionStatusResponse,
    SubscriptionStatus,
    Currency
)
from utils.firebase_config import get_firestore_client

# Configure logging
logger = logging.getLogger(__name__)

# Firestore collection
SUBSCRIPTIONS_COLLECTION = "subscriptions"
SUBSCRIPTION_HISTORY_SUBCOLLECTION = "history"


class SubscriptionServiceError(Exception):
    """Base exception for subscription service errors."""
    pass


class PlanNotFoundError(SubscriptionServiceError):
    """Exception raised when subscription plan is not found."""
    pass


class SubscriptionNotFoundError(SubscriptionServiceError):
    """Exception raised when subscription is not found."""
    pass


class SubscriptionService:
    """
    Subscription management service for handling subscription lifecycle.
    
    This service manages all subscription operations including plan loading,
    subscription activation, status checking, and cancellation.
    
    Attributes:
        plans: Dictionary of cached subscription plans (plan_id -> SubscriptionPlan)
    
    Example:
        >>> service = SubscriptionService()
        >>> plans = service.get_all_plans()
        >>> print(f"Available plans: {len(plans)}")
    """
    
    def __init__(self):
        """
        Initialize subscription service and load plans from JSON.
        
        This constructor loads subscription plans from the configuration file
        and caches them in memory for fast access.
        
        Raises:
            FileNotFoundError: If subscription plans file is not found
            ValueError: If plans file is invalid
        """
        logger.info("Initializing SubscriptionService")
        
        # Load subscription plans
        self.plans: Dict[str, SubscriptionPlan] = {}
        self._load_plans()
        
        logger.info(f"SubscriptionService initialized with {len(self.plans)} plans")
    
    def _load_plans(self) -> None:
        """
        Load subscription plans from JSON file.
        
        This method reads the subscription_plans.json file and caches the plans
        in memory as SubscriptionPlan objects.
        
        Raises:
            FileNotFoundError: If plans file is not found
            ValueError: If JSON is invalid
        """
        try:
            # Get path to subscription plans file
            plans_file = Path(__file__).parent.parent / "data" / "subscription_plans.json"
            
            if not plans_file.exists():
                error_msg = f"Subscription plans file not found: {plans_file}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            logger.info(f"Loading subscription plans from: {plans_file}")
            
            # Read and parse JSON
            with open(plans_file, 'r', encoding='utf-8') as f:
                plans_data = json.load(f)
            
            # Convert to SubscriptionPlan objects and cache
            for plan_data in plans_data:
                plan = SubscriptionPlan(**plan_data)
                self.plans[plan.plan_id] = plan
                logger.debug(f"Loaded plan: {plan.plan_id} - {plan.name}")
            
            logger.info(f"Successfully loaded {len(self.plans)} subscription plans")
            
        except FileNotFoundError:
            raise
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in subscription plans file: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Error loading subscription plans: {e}"
            logger.error(error_msg)
            logger.exception("Full traceback:")
            raise SubscriptionServiceError(error_msg)
    
    def get_all_plans(self) -> List[SubscriptionPlan]:
        """
        Get all available subscription plans.
        
        Returns:
            List of all subscription plans
        
        Example:
            >>> plans = service.get_all_plans()
            >>> for plan in plans:
            ...     print(f"{plan.name}: ₹{plan.get_price_in_rupees()}")
        """
        logger.debug(f"Getting all plans: {len(self.plans)} available")
        return list(self.plans.values())
    
    def get_plan_by_id(self, plan_id: str) -> SubscriptionPlan:
        """
        Get subscription plan by ID.
        
        Args:
            plan_id: Plan identifier
        
        Returns:
            SubscriptionPlan object
        
        Raises:
            PlanNotFoundError: If plan is not found
        
        Example:
            >>> plan = service.get_plan_by_id("premium_monthly")
            >>> print(f"{plan.name}: {plan.duration_days} days")
        """
        logger.debug(f"Getting plan by ID: {plan_id}")
        
        if plan_id not in self.plans:
            error_msg = f"Plan not found: {plan_id}"
            logger.error(error_msg)
            raise PlanNotFoundError(error_msg)
        
        return self.plans[plan_id]
    
    def activate_subscription(
        self,
        parent_id: str,
        plan_id: str,
        payment_id: str,
        order_id: str
    ) -> SubscriptionDetails:
        """
        Activate a new subscription for a parent.
        
        This method creates a new active subscription with the specified plan,
        calculates start and end dates, and saves it to Firestore.
        
        Args:
            parent_id: Firebase user ID of the parent
            plan_id: Subscription plan identifier
            payment_id: Razorpay payment ID
            order_id: Razorpay order ID
        
        Returns:
            SubscriptionDetails object for the activated subscription
        
        Raises:
            PlanNotFoundError: If plan is not found
            SubscriptionServiceError: If activation fails
        
        Example:
            >>> subscription = service.activate_subscription(
            ...     parent_id="parent_abc123",
            ...     plan_id="premium_monthly",
            ...     payment_id="pay_xyz789",
            ...     order_id="order_xyz789"
            ... )
            >>> print(f"Activated: {subscription.plan_name}")
        """
        logger.info(
            f"Activating subscription: parent_id={parent_id}, plan_id={plan_id}"
        )
        
        try:
            # Get plan details
            plan = self.get_plan_by_id(plan_id)
            
            # Calculate dates
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=plan.duration_days)
            
            # Generate subscription ID
            subscription_id = f"sub_{parent_id}_{int(datetime.utcnow().timestamp())}"
            
            # Create subscription details
            subscription = SubscriptionDetails(
                subscription_id=subscription_id,
                parent_id=parent_id,
                plan_id=plan.plan_id,
                plan_name=plan.name,
                status=SubscriptionStatus.ACTIVE,
                start_date=start_date,
                end_date=end_date,
                auto_renew=False,  # Default to no auto-renew
                amount_paid=plan.price,
                currency=plan.currency,
                payment_id=payment_id,
                created_at=start_date,
                updated_at=start_date
            )
            
            # Save to Firestore
            db = get_firestore_client()
            
            # Save current subscription (document ID = parent_id)
            doc_ref = db.collection(SUBSCRIPTIONS_COLLECTION).document(parent_id)
            subscription_dict = subscription.model_dump(mode='json')
            doc_ref.set(subscription_dict)
            
            # Also save to history subcollection
            history_ref = (
                db.collection(SUBSCRIPTIONS_COLLECTION)
                .document(parent_id)
                .collection(SUBSCRIPTION_HISTORY_SUBCOLLECTION)
                .document(subscription_id)
            )
            history_ref.set(subscription_dict)
            
            logger.info(
                f"Subscription activated successfully: {subscription_id}, "
                f"expires: {end_date.isoformat()}"
            )
            
            return subscription
            
        except PlanNotFoundError:
            raise
        except Exception as e:
            error_msg = f"Failed to activate subscription: {e}"
            logger.error(error_msg)
            logger.exception("Full traceback:")
            raise SubscriptionServiceError(error_msg)
    
    def get_subscription(self, parent_id: str) -> Optional[SubscriptionDetails]:
        """
        Get current subscription for a parent.
        
        Args:
            parent_id: Firebase user ID of the parent
        
        Returns:
            SubscriptionDetails object or None if not found
        
        Example:
            >>> subscription = service.get_subscription("parent_abc123")
            >>> if subscription:
            ...     print(f"Plan: {subscription.plan_name}")
        """
        logger.debug(f"Getting subscription for parent: {parent_id}")
        
        try:
            db = get_firestore_client()
            doc_ref = db.collection(SUBSCRIPTIONS_COLLECTION).document(parent_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                logger.debug(f"No subscription found for parent: {parent_id}")
                return None
            
            subscription_data = doc.to_dict()
            subscription = SubscriptionDetails(**subscription_data)
            
            logger.debug(
                f"Subscription found: {subscription.plan_id}, "
                f"status: {subscription.status.value}"
            )
            
            return subscription
            
        except Exception as e:
            error_msg = f"Error fetching subscription: {e}"
            logger.error(error_msg)
            logger.exception("Full traceback:")
            raise SubscriptionServiceError(error_msg)
    
    def check_subscription_status(
        self,
        parent_id: str
    ) -> SubscriptionStatusResponse:
        """
        Check subscription status for a parent.
        
        This method retrieves the subscription and returns a user-friendly
        status response. If no subscription exists, returns free plan status.
        
        Args:
            parent_id: Firebase user ID of the parent
        
        Returns:
            SubscriptionStatusResponse with current status
        
        Example:
            >>> status = service.check_subscription_status("parent_abc123")
            >>> print(f"Active: {status.is_active}")
            >>> print(f"Days remaining: {status.days_remaining}")
        """
        logger.info(f"Checking subscription status for: {parent_id}")
        
        try:
            subscription = self.get_subscription(parent_id)
            
            # If no subscription, return free plan status
            if not subscription:
                logger.debug("No subscription found, returning free plan status")
                free_plan = self.get_plan_by_id("free")
                
                return SubscriptionStatusResponse(
                    is_active=True,  # Free plan is always active
                    plan_name=free_plan.name,
                    plan_id=free_plan.plan_id,
                    days_remaining=365,  # Free plan duration
                    expires_at=datetime.utcnow() + timedelta(days=365),
                    features=free_plan.features,
                    auto_renew=False,
                    amount_paid=None
                )
            
            # Check if subscription is expired
            is_expired = self._is_subscription_expired(subscription)
            
            # If expired, update status in Firestore
            if is_expired and subscription.status == SubscriptionStatus.ACTIVE:
                logger.info(f"Subscription expired, updating status: {subscription.subscription_id}")
                subscription.status = SubscriptionStatus.EXPIRED
                self._update_subscription_status(parent_id, SubscriptionStatus.EXPIRED)
            
            # Calculate if currently active
            is_active = (
                subscription.status == SubscriptionStatus.ACTIVE and
                not is_expired
            )
            
            # Calculate days remaining
            days_remaining = subscription.days_remaining() if is_active else 0
            
            # Get plan features
            try:
                plan = self.get_plan_by_id(subscription.plan_id)
                features = plan.features
            except PlanNotFoundError:
                logger.warning(f"Plan not found: {subscription.plan_id}, using empty features")
                features = []
            
            status_response = SubscriptionStatusResponse(
                is_active=is_active,
                plan_name=subscription.plan_name,
                plan_id=subscription.plan_id,
                days_remaining=days_remaining,
                expires_at=subscription.end_date,
                features=features,
                auto_renew=subscription.auto_renew,
                amount_paid=subscription.amount_paid
            )
            
            logger.info(
                f"Subscription status: is_active={is_active}, "
                f"days_remaining={days_remaining}"
            )
            
            return status_response
            
        except Exception as e:
            error_msg = f"Error checking subscription status: {e}"
            logger.error(error_msg)
            logger.exception("Full traceback:")
            raise SubscriptionServiceError(error_msg)
    
    def is_premium_active(self, parent_id: str) -> bool:
        """
        Quick check if parent has active premium subscription.
        
        This is a lightweight method used by middleware for access control.
        
        Args:
            parent_id: Firebase user ID of the parent
        
        Returns:
            True if premium subscription is active, False otherwise
        
        Example:
            >>> if service.is_premium_active("parent_abc123"):
            ...     print("Access granted to premium features")
        """
        logger.debug(f"Checking premium status for: {parent_id}")
        
        try:
            subscription = self.get_subscription(parent_id)
            
            if not subscription:
                logger.debug("No subscription found, premium not active")
                return False
            
            # Check if subscription is active and not expired
            is_active = subscription.is_active()
            
            # Check if it's a premium plan (not free)
            is_premium = subscription.plan_id != "free"
            
            result = is_active and is_premium
            
            logger.debug(
                f"Premium status: {result} (plan: {subscription.plan_id}, "
                f"status: {subscription.status.value})"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error checking premium status: {e}")
            # Return False on error (safer to deny access)
            return False
    
    def cancel_subscription(self, parent_id: str) -> SubscriptionDetails:
        """
        Cancel a subscription.
        
        This method marks the subscription as cancelled but keeps the end_date
        unchanged, allowing access until the current period expires.
        
        Args:
            parent_id: Firebase user ID of the parent
        
        Returns:
            Updated SubscriptionDetails
        
        Raises:
            SubscriptionNotFoundError: If subscription not found
        
        Example:
            >>> subscription = service.cancel_subscription("parent_abc123")
            >>> print(f"Cancelled, access until: {subscription.end_date}")
        """
        logger.info(f"Cancelling subscription for: {parent_id}")
        
        try:
            subscription = self.get_subscription(parent_id)
            
            if not subscription:
                error_msg = f"No subscription found for parent: {parent_id}"
                logger.error(error_msg)
                raise SubscriptionNotFoundError(error_msg)
            
            # Update subscription status
            subscription.status = SubscriptionStatus.CANCELLED
            subscription.auto_renew = False
            subscription.updated_at = datetime.utcnow()
            
            # Save to Firestore
            db = get_firestore_client()
            doc_ref = db.collection(SUBSCRIPTIONS_COLLECTION).document(parent_id)
            subscription_dict = subscription.model_dump(mode='json')
            doc_ref.update({
                'status': SubscriptionStatus.CANCELLED.value,
                'auto_renew': False,
                'updated_at': subscription.updated_at
            })
            
            logger.info(
                f"Subscription cancelled: {subscription.subscription_id}, "
                f"access until: {subscription.end_date.isoformat()}"
            )
            
            return subscription
            
        except SubscriptionNotFoundError:
            raise
        except Exception as e:
            error_msg = f"Failed to cancel subscription: {e}"
            logger.error(error_msg)
            logger.exception("Full traceback:")
            raise SubscriptionServiceError(error_msg)
    
    def get_subscription_history(
        self,
        parent_id: str,
        limit: Optional[int] = None
    ) -> List[SubscriptionDetails]:
        """
        Get subscription history for a parent.
        
        Args:
            parent_id: Firebase user ID of the parent
            limit: Maximum number of records to return (None for all)
        
        Returns:
            List of SubscriptionDetails ordered by created_at descending
        
        Example:
            >>> history = service.get_subscription_history("parent_abc123", limit=5)
            >>> for sub in history:
            ...     print(f"{sub.plan_name}: {sub.status.value}")
        """
        logger.info(f"Getting subscription history for: {parent_id}, limit: {limit}")
        
        try:
            db = get_firestore_client()
            
            # Query history subcollection
            history_ref = (
                db.collection(SUBSCRIPTIONS_COLLECTION)
                .document(parent_id)
                .collection(SUBSCRIPTION_HISTORY_SUBCOLLECTION)
                .order_by('created_at', direction=firestore.Query.DESCENDING)
            )
            
            if limit:
                history_ref = history_ref.limit(limit)
            
            docs = history_ref.stream()
            
            # Convert to SubscriptionDetails objects
            subscriptions = []
            for doc in docs:
                try:
                    sub_data = doc.to_dict()
                    subscription = SubscriptionDetails(**sub_data)
                    subscriptions.append(subscription)
                except Exception as e:
                    logger.warning(
                        f"Skipping invalid subscription record: {doc.id}, error: {e}"
                    )
            
            logger.info(f"Found {len(subscriptions)} subscription records")
            
            return subscriptions
            
        except Exception as e:
            error_msg = f"Error fetching subscription history: {e}"
            logger.error(error_msg)
            logger.exception("Full traceback:")
            raise SubscriptionServiceError(error_msg)
    
    def _is_subscription_expired(self, subscription: SubscriptionDetails) -> bool:
        """
        Check if a subscription is expired.
        
        Args:
            subscription: SubscriptionDetails object
        
        Returns:
            True if expired, False otherwise
        """
        now = datetime.utcnow()
        is_expired = subscription.end_date <= now
        
        logger.debug(
            f"Checking expiration: end_date={subscription.end_date.isoformat()}, "
            f"now={now.isoformat()}, expired={is_expired}"
        )
        
        return is_expired
    
    def _update_subscription_status(
        self,
        parent_id: str,
        status: SubscriptionStatus
    ) -> None:
        """
        Update subscription status in Firestore.
        
        Args:
            parent_id: Firebase user ID of the parent
            status: New subscription status
        """
        try:
            db = get_firestore_client()
            doc_ref = db.collection(SUBSCRIPTIONS_COLLECTION).document(parent_id)
            doc_ref.update({
                'status': status.value,
                'updated_at': datetime.utcnow()
            })
            
            logger.debug(f"Updated subscription status to: {status.value}")
            
        except Exception as e:
            logger.error(f"Failed to update subscription status: {e}")
            # Don't raise - this is a background update
    
    def has_feature_access(
        self,
        parent_id: str,
        feature: str
    ) -> bool:
        """
        Check if parent has access to a specific feature.
        
        Args:
            parent_id: Firebase user ID of parent
            feature: Feature name to check access for
        
        Returns:
            True if parent has access to the feature, False otherwise
        
        Example:
            >>> if service.has_feature_access("parent_abc123", "parent_training_academy"):
            ...     print("Access granted to parent training academy")
        """
        logger.debug(f"Checking feature access: parent_id={parent_id}, feature={feature}")
        
        try:
            # Get subscription status
            status = self.check_subscription_status(parent_id)
            
            # Check if feature is in the plan's features list
            return feature in status.features
            
        except Exception as e:
            logger.error(f"Error checking feature access: {e}")
            # Return False on error (safer to deny access)
            return False
    
    def get_subscription_tier(self, parent_id: str) -> str:
        """
        Get the subscription tier for a parent.
        
        Args:
            parent_id: Firebase user ID of parent
        
        Returns:
            Subscription tier name (basic, standard, premium_plus)
        
        Example:
            >>> tier = service.get_subscription_tier("parent_abc123")
            >>> print(f"Current tier: {tier}")
        """
        logger.debug(f"Getting subscription tier for: {parent_id}")
        
        try:
            status = self.check_subscription_status(parent_id)
            plan_id = status.plan_id
            
            # Map plan IDs to tiers
            if plan_id in ["basic", "free"]:
                return "basic"
            elif plan_id in ["standard_monthly", "standard_yearly"]:
                return "standard"
            elif plan_id in ["premium_plus_monthly", "premium_plus_yearly"]:
                return "premium_plus"
            else:
                return "unknown"
                
        except Exception as e:
            logger.error(f"Error getting subscription tier: {e}")
            return "unknown"
    
    def can_access_feature_tier(
        self,
        parent_id: str,
        required_tier: str
    ) -> bool:
        """
        Check if parent can access features of a specific tier.
        
        Args:
            parent_id: Firebase user ID of parent
            required_tier: Required tier (basic, standard, premium_plus)
        
        Returns:
            True if parent's tier is equal to or higher than required tier
        
        Example:
            >>> if service.can_access_feature_tier("parent_abc123", "standard"):
            ...     print("Can access standard tier features")
        """
        logger.debug(f"Checking tier access: parent_id={parent_id}, required_tier={required_tier}")
        
        try:
            current_tier = self.get_subscription_tier(parent_id)
            
            # Define tier hierarchy
            tier_hierarchy = {
                "basic": 0,
                "standard": 1,
                "premium_plus": 2
            }
            
            current_level = tier_hierarchy.get(current_tier, 0)
            required_level = tier_hierarchy.get(required_tier, 0)
            
            return current_level >= required_level
            
        except Exception as e:
            logger.error(f"Error checking tier access: {e}")
            return False
    
    def get_feature_limits(
        self,
        parent_id: str,
        feature: str
    ) -> Dict[str, Any]:
        """
        Get usage limits for a specific feature based on subscription.
        
        Args:
            parent_id: Firebase user ID of parent
            feature: Feature name to get limits for
        
        Returns:
            Dictionary containing feature limits
        
        Example:
            >>> limits = service.get_feature_limits("parent_abc123", "diagnostic_tests")
            >>> print(f"Monthly limit: {limits.get('monthly_limit', 0)}")
        """
        logger.debug(f"Getting feature limits: parent_id={parent_id}, feature={feature}")
        
        try:
            status = self.check_subscription_status(parent_id)
            plan_id = status.plan_id
            
            # Define feature limits for each plan
            feature_limits = {
                "basic": {
                    "diagnostic_tests": {"monthly_limit": 1, "daily_limit": 1},
                    "practice_questions": {"monthly_limit": 50, "daily_limit": 5},
                    "ai_tokens": {"daily_limit": 1000, "monthly_limit": 10000},
                    "parent_training_modules": {"total_limit": 0},
                    "community_resources": {"access_level": "read_only"},
                    "study_tools": {"access_level": "basic"},
                    "analytics": {"access_level": "basic"},
                    "whatsapp_notifications": {"enabled": False}
                },
                "standard": {
                    "diagnostic_tests": {"monthly_limit": 3, "daily_limit": 1},
                    "practice_questions": {"monthly_limit": -1, "daily_limit": 20},  # -1 = unlimited
                    "ai_tokens": {"daily_limit": 5000, "monthly_limit": 50000},
                    "parent_training_modules": {"total_limit": 5},
                    "community_resources": {"access_level": "full"},
                    "study_tools": {"access_level": "basic"},
                    "analytics": {"access_level": "enhanced"},
                    "whatsapp_notifications": {"enabled": True, "level": "basic"}
                },
                "premium_plus": {
                    "diagnostic_tests": {"monthly_limit": -1, "daily_limit": -1},  # unlimited
                    "practice_questions": {"monthly_limit": -1, "daily_limit": -1},  # unlimited
                    "ai_tokens": {"daily_limit": 15000, "monthly_limit": 150000},
                    "parent_training_modules": {"total_limit": -1},  # unlimited
                    "community_resources": {"access_level": "full_with_contribution"},
                    "study_tools": {"access_level": "advanced"},
                    "analytics": {"access_level": "advanced"},
                    "whatsapp_notifications": {"enabled": True, "level": "full"}
                }
            }
            
            # Get current tier
            tier = self.get_subscription_tier(parent_id)
            
            # Return limits for the tier, or empty dict if not found
            return feature_limits.get(tier, {})
            
        except Exception as e:
            logger.error(f"Error getting feature limits: {e}")
            return {}
    
    def upgrade_subscription(
        self,
        parent_id: str,
        new_plan_id: str,
        payment_id: str,
        order_id: str
    ) -> SubscriptionDetails:
        """
        Upgrade a subscription to a higher tier plan.
        
        Args:
            parent_id: Firebase user ID of parent
            new_plan_id: New plan ID to upgrade to
            payment_id: Razorpay payment ID
            order_id: Razorpay order ID
        
        Returns:
            Updated SubscriptionDetails
        
        Raises:
            PlanNotFoundError: If new plan is not found
            SubscriptionServiceError: If upgrade fails
        
        Example:
            >>> subscription = service.upgrade_subscription(
            ...     parent_id="parent_abc123",
            ...     plan_id="premium_plus_monthly",
            ...     payment_id="pay_xyz789",
            ...     order_id="order_xyz789"
            ... )
        """
        logger.info(f"Upgrading subscription: parent_id={parent_id}, new_plan_id={new_plan_id}")
        
        try:
            # Get current subscription
            current_subscription = self.get_subscription(parent_id)
            
            if not current_subscription:
                # No existing subscription, activate new one
                return self.activate_subscription(parent_id, new_plan_id, payment_id, order_id)
            
            # Get new plan details
            new_plan = self.get_plan_by_id(new_plan_id)
            
            # Check if this is actually an upgrade
            current_tier = self.get_subscription_tier(parent_id)
            new_tier = self.get_subscription_tier_from_plan_id(new_plan_id)
            
            tier_hierarchy = {"basic": 0, "standard": 1, "premium_plus": 2}
            
            if tier_hierarchy.get(new_tier, 0) <= tier_hierarchy.get(current_tier, 0):
                logger.warning(f"Not an upgrade: {current_tier} -> {new_tier}")
                # Still allow the change, but log it
            
            # Calculate new end date (extend from current end date)
            current_end = current_subscription.end_date
            if current_subscription.is_active():
                # Extend from current end date
                new_end_date = current_end + timedelta(days=new_plan.duration_days)
            else:
                # Start fresh from today
                start_date = datetime.utcnow()
                new_end_date = start_date + timedelta(days=new_plan.duration_days)
            
            # Create new subscription details
            new_subscription = SubscriptionDetails(
                subscription_id=f"sub_{parent_id}_{int(datetime.utcnow().timestamp())}",
                parent_id=parent_id,
                plan_id=new_plan.plan_id,
                plan_name=new_plan.name,
                status=SubscriptionStatus.ACTIVE,
                start_date=current_subscription.start_date if current_subscription.is_active() else datetime.utcnow(),
                end_date=new_end_date,
                auto_renew=False,
                amount_paid=new_plan.price,
                currency=new_plan.currency,
                payment_id=payment_id,
                created_at=current_subscription.created_at,
                updated_at=datetime.utcnow()
            )
            
            # Save to Firestore
            db = get_firestore_client()
            
            # Update current subscription
            doc_ref = db.collection(SUBSCRIPTIONS_COLLECTION).document(parent_id)
            subscription_dict = new_subscription.model_dump(mode='json')
            doc_ref.set(subscription_dict)
            
            # Save to history
            history_ref = (
                db.collection(SUBSCRIPTIONS_COLLECTION)
                .document(parent_id)
                .collection(SUBSCRIPTION_HISTORY_SUBCOLLECTION)
                .document(new_subscription.subscription_id)
            )
            history_ref.set(subscription_dict)
            
            logger.info(
                f"Subscription upgraded successfully: {new_subscription.subscription_id}, "
                f"new plan: {new_plan.name}, expires: {new_end_date.isoformat()}"
            )
            
            return new_subscription
            
        except PlanNotFoundError:
            raise
        except Exception as e:
            error_msg = f"Failed to upgrade subscription: {e}"
            logger.error(error_msg)
            logger.exception("Full traceback:")
            raise SubscriptionServiceError(error_msg)
    
    def get_subscription_tier_from_plan_id(self, plan_id: str) -> str:
        """
        Get subscription tier from plan ID.
        
        Args:
            plan_id: Plan identifier
        
        Returns:
            Subscription tier name (basic, standard, premium_plus)
        """
        if plan_id in ["basic", "free"]:
            return "basic"
        elif plan_id in ["standard_monthly", "standard_yearly"]:
            return "standard"
        elif plan_id in ["premium_plus_monthly", "premium_plus_yearly"]:
            return "premium_plus"
        else:
            return "unknown"
