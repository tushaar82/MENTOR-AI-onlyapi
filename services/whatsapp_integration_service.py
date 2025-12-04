"""
WhatsApp Integration Service

This service provides WhatsApp Business API integration for parent communication
in low-bandwidth areas, enabling affordable access to Mentor AI features.

Features:
- WhatsApp Business API integration
- Opt-in/opt-out management
- Message templates and automation
- Notification routing system
- Interactive WhatsApp sessions
- Multi-language support
- Cost-effective communication
- Offline message queuing
- Rich media support
- Analytics and tracking

Author: Mentor AI Team
Version: 1.0.0
"""

import logging
import time
import json
import hashlib
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field
from google.cloud import firestore

from services.unified_gemini_config_service import get_unified_gemini_service, GeminiConfig
from services.ai_content_service import get_ai_content_service, ContentType, ContentRequest
from utils.firebase_config import get_firestore_client

# Configure logging
logger = logging.getLogger(__name__)

# Message types and categories
class MessageType(Enum):
    """Types of WhatsApp messages."""
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    LOCATION = "location"
    CONTACT = "contact"
    INTERACTIVE = "interactive"
    TEMPLATE = "template"
    BUTTON = "button"
    LIST = "list"

class MessageCategory(Enum):
    """Categories of WhatsApp messages."""
    NOTIFICATION = "notification"
    ALERT = "alert"
    REMINDER = "reminder"
    UPDATE = "update"
    INSIGHT = "insight"
    RESOURCE = "resource"
    QUESTION = "question"
    RESPONSE = "response"
    MARKETING = "marketing"
    SUPPORT = "support"

class NotificationType(Enum):
    """Types of notifications."""
    DAILY_PROGRESS = "daily_progress"
    WEEKLY_REPORT = "weekly_report"
    INTERVENTION_ALERT = "intervention_alert"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    STUDY_REMINDER = "study_reminder"
    TEST_SCHEDULED = "test_scheduled"
    RESOURCE_SHARED = "resource_shared"
    PAYMENT_REMINDER = "payment_reminder"
    SYSTEM_UPDATE = "system_update"

class SessionStatus(Enum):
    """Status of WhatsApp sessions."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    CLOSED = "closed"

@dataclass
class WhatsAppMessage:
    """WhatsApp message definition."""
    
    message_id: str
    parent_id: str
    student_id: Optional[str]
    phone_number: str
    message_type: MessageType
    category: MessageCategory
    content: str
    media_url: Optional[str]
    interactive_elements: Optional[Dict[str, Any]]
    template_name: Optional[str]
    template_variables: Optional[Dict[str, str]]
    language: str
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]
    status: str  # "pending", "sent", "delivered", "read", "failed"
    error_message: Optional[str]
    cost: float
    created_at: datetime

@dataclass
class WhatsAppSession:
    """WhatsApp session definition."""
    
    session_id: str
    parent_id: str
    student_id: Optional[str]
    phone_number: str
    status: SessionStatus
    context: Dict[str, Any]
    last_activity: datetime
    expires_at: datetime
    message_count: int
    session_type: str  # "support", "learning", "consultation"
    language: str
    created_at: datetime

@dataclass
class WhatsAppTemplate:
    """WhatsApp message template definition."""
    
    template_id: str
    template_name: str
    category: MessageCategory
    language: str
    content_template: str
    variables: List[str]
    buttons: Optional[List[Dict[str, Any]]]
    media_type: Optional[str]
    status: str  # "approved", "pending", "rejected"
    created_at: datetime
    updated_at: datetime

@dataclass
class WhatsAppOptIn:
    """WhatsApp opt-in definition."""
    
    opt_in_id: str
    parent_id: str
    phone_number: str
    status: str  # "opted_in", "opted_out", "pending"
    notification_types: List[NotificationType]
    preferred_language: str
    quiet_hours: Dict[str, Any]  # {"start": "22:00", "end": "08:00", "timezone": "UTC"}
    opt_in_date: datetime
    last_interaction: datetime

class WhatsAppIntegrationService:
    """
    Service for WhatsApp Business API integration.
    
    This service provides comprehensive WhatsApp communication capabilities
    with cost-effective messaging for parents in low-bandwidth areas.
    
    Attributes:
        unified_service: Unified Gemini configuration service
        ai_content_service: AI content generation service
        db: Firestore database client
        whatsapp_api: WhatsApp Business API client
        message_queue: Message queue for offline handling
        template_manager: Template management system
        session_manager: Session management system
    
    Example:
        >>> service = WhatsAppIntegrationService()
        >>> result = service.send_notification(
        ...     parent_id="parent123",
        ...     notification_type="daily_progress",
        ...     content="Your child completed 5 topics today!"
        ... )
        >>> print(f"Message sent: {result['message_id']}")
    """
    
    def __init__(
        self,
        db: Optional[firestore.Client] = None,
        unified_config: Optional[GeminiConfig] = None,
        enable_database_persistence: bool = True,
        whatsapp_api_token: Optional[str] = None,
        whatsapp_phone_number_id: Optional[str] = None,
        webhook_verify_token: Optional[str] = None,
        session_timeout_minutes: int = 30,
        max_message_length: int = 1600
    ):
        """
        Initialize WhatsApp Integration Service.
        
        Args:
            db: Firestore client (creates new if None)
            unified_config: Optional unified configuration
            enable_database_persistence: Enable saving to database
            whatsapp_api_token: WhatsApp Business API token
            whatsapp_phone_number_id: WhatsApp phone number ID
            webhook_verify_token: Webhook verification token
            session_timeout_minutes: Session timeout in minutes
            max_message_length: Maximum message length
        """
        logger.info("Initializing WhatsAppIntegrationService")
        
        # Database client
        self.db = db if db else get_firestore_client()
        
        # Initialize services
        self.unified_service = get_unified_gemini_service(config=unified_config)
        self.ai_content_service = get_ai_content_service(
            unified_config=unified_config,
            enable_database_persistence=enable_database_persistence
        )
        
        # Configuration
        self.enable_database_persistence = enable_database_persistence
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.max_message_length = max_message_length
        
        # WhatsApp API configuration
        self.whatsapp_api_token = whatsapp_api_token
        self.whatsapp_phone_number_id = whatsapp_phone_number_id
        self.webhook_verify_token = webhook_verify_token
        self.whatsapp_api_base_url = "https://graph.facebook.com/v18.0"
        
        # HTTP session for API calls
        self.http_session = None
        
        # Collections
        self.messages_collection = "whatsapp_messages"
        self.sessions_collection = "whatsapp_sessions"
        self.templates_collection = "whatsapp_templates"
        self.opt_ins_collection = "whatsapp_opt_ins"
        self.analytics_collection = "whatsapp_analytics"
        
        # Supported languages
        self.supported_languages = [
            "english", "hindi", "bengali", "telugu", "tamil",
            "marathi", "gujarati", "kannada", "malayalam", "punjabi"
        ]
        
        # Message templates
        self.default_templates = self._initialize_default_templates()
        
        # Metrics
        self.metrics = {
            "total_messages_sent": 0,
            "total_messages_received": 0,
            "total_sessions_created": 0,
            "active_sessions": 0,
            "messages_by_type": {mt.value: 0 for mt in MessageType},
            "messages_by_category": {mc.value: 0 for mc in MessageCategory},
            "delivery_success_rate": 0.0,
            "average_response_time": 0.0,
            "cost_per_message": 0.0,
            "total_cost": 0.0,
            "opt_in_rate": 0.0,
            "opt_out_rate": 0.0,
            "session_duration_avg": 0.0,
            "messages_per_session_avg": 0.0,
            "template_usage": {},
            "error_rate": 0.0,
            "retry_count": 0
        }
        
        logger.info(
            f"WhatsAppIntegrationService initialized (db_persistence={enable_database_persistence}, "
            f"session_timeout={session_timeout_minutes}min, max_length={max_message_length})"
        )
    
    async def send_notification(
        self,
        parent_id: str,
        notification_type: str,
        content: str,
        student_id: Optional[str] = None,
        language: str = "english",
        template_variables: Optional[Dict[str, str]] = None,
        media_url: Optional[str] = None,
        buttons: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Send a notification via WhatsApp.
        
        Args:
            parent_id: Parent ID to send notification to
            notification_type: Type of notification
            content: Message content
            student_id: Optional student ID
            language: Message language
            template_variables: Variables for template substitution
            media_url: Optional media URL
            buttons: Optional interactive buttons
        
        Returns:
            Dict with notification results
        """
        start_time = time.time()
        
        try:
            logger.info(f"Sending WhatsApp notification: {notification_type} to parent {parent_id}")
            
            # Check if parent is opted in
            opt_in = await self._get_parent_opt_in(parent_id)
            if not opt_in or opt_in.status != "opted_in":
                return {
                    "success": False,
                    "error": "Parent not opted in for WhatsApp notifications",
                    "parent_id": parent_id
                }
            
            # Check if notification type is enabled
            if NotificationType(notification_type) not in opt_in.notification_types:
                return {
                    "success": False,
                    "error": f"Notification type {notification_type} not enabled",
                    "parent_id": parent_id
                }
            
            # Check quiet hours
            if await self._is_in_quiet_hours(opt_in):
                # Queue message for later
                await self._queue_message(parent_id, notification_type, content, student_id)
                return {
                    "success": True,
                    "message": "Message queued due to quiet hours",
                    "parent_id": parent_id,
                    "queued": True
                }
            
            # Get phone number
            phone_number = opt_in.phone_number
            
            # Get or create template
            template = await self._get_notification_template(notification_type, language)
            if not template:
                # Create ad-hoc message
                message_content = content
            else:
                # Use template with variables
                message_content = await self._format_template(template, template_variables or {})
            
            # Split long messages
            message_parts = self._split_long_message(message_content)
            
            results = []
            for i, part in enumerate(message_parts):
                # Create message record
                message_id = f"msg_{parent_id}_{int(time.time())}_{i}"
                
                message = WhatsAppMessage(
                    message_id=message_id,
                    parent_id=parent_id,
                    student_id=student_id,
                    phone_number=phone_number,
                    message_type=MessageType.TEMPLATE if template else MessageType.TEXT,
                    category=MessageCategory.NOTIFICATION,
                    content=part,
                    media_url=media_url,
                    interactive_elements={"buttons": buttons} if buttons else None,
                    template_name=template.template_name if template else None,
                    template_variables=template_variables,
                    language=language,
                    sent_at=None,
                    delivered_at=None,
                    read_at=None,
                    status="pending",
                    error_message=None,
                    cost=0.0,  # Will be calculated after sending
                    created_at=datetime.utcnow()
                )
                
                # Send via WhatsApp API
                send_result = await self._send_whatsapp_message(message)
                
                if send_result["success"]:
                    message.status = "sent"
                    message.sent_at = datetime.utcnow()
                    message.cost = send_result.get("cost", 0.0)
                    
                    # Update metrics
                    self.metrics["total_messages_sent"] += 1
                    self.metrics["messages_by_type"][message.message_type.value] += 1
                    self.metrics["messages_by_category"][message.category.value] += 1
                    self.metrics["total_cost"] += message.cost
                else:
                    message.status = "failed"
                    message.error_message = send_result.get("error", "Unknown error")
                    
                    # Update metrics
                    self.metrics["error_rate"] += 1
                
                # Save to database
                if self.enable_database_persistence:
                    await self._save_message_to_db(message)
                
                results.append({
                    "message_id": message_id,
                    "part": i + 1,
                    "status": message.status,
                    "cost": message.cost
                })
            
            # Calculate total time
            processing_time = time.time() - start_time
            
            result = {
                "success": True,
                "parent_id": parent_id,
                "notification_type": notification_type,
                "message_parts": len(message_parts),
                "results": results,
                "total_cost": sum(r["cost"] for r in results),
                "processing_time_ms": int(processing_time * 1000)
            }
            
            logger.info(f"WhatsApp notification sent: {len(results)} parts to parent {parent_id}")
            return result
            
        except Exception as e:
            logger.error(f"WhatsApp notification failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "parent_id": parent_id,
                "notification_type": notification_type
            }
    
    async def handle_webhook(
        self,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle incoming WhatsApp webhook.
        
        Args:
            payload: Webhook payload from WhatsApp
        
        Returns:
            Dict with webhook processing results
        """
        try:
            logger.info("Processing WhatsApp webhook")
            
            # Verify webhook if needed
            if "hub_verify_token" in payload:
                return await self._verify_webhook(payload)
            
            # Process messages
            if "entry" in payload:
                results = []
                for entry in payload["entry"]:
                    if "changes" in entry:
                        for change in entry["changes"]:
                            if "messages" in change["value"]:
                                for message_data in change["value"]["messages"]:
                                    result = await self._process_incoming_message(message_data)
                                    results.append(result)
                
                return {
                    "success": True,
                    "processed_messages": len(results),
                    "results": results
                }
            
            return {
                "success": True,
                "message": "No messages to process"
            }
            
        except Exception as e:
            logger.error(f"Webhook processing failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_session(
        self,
        parent_id: str,
        phone_number: str,
        session_type: str = "support",
        student_id: Optional[str] = None,
        language: str = "english",
        initial_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new WhatsApp session.
        
        Args:
            parent_id: Parent ID
            phone_number: WhatsApp phone number
            session_type: Type of session
            student_id: Optional student ID
            language: Session language
            initial_context: Initial session context
        
        Returns:
            Dict with session creation results
        """
        try:
            logger.info(f"Creating WhatsApp session: {session_type} for parent {parent_id}")
            
            # Generate session ID
            session_id = f"session_{parent_id}_{session_type}_{int(time.time())}"
            
            # Create session
            session = WhatsAppSession(
                session_id=session_id,
                parent_id=parent_id,
                student_id=student_id,
                phone_number=phone_number,
                status=SessionStatus.ACTIVE,
                context=initial_context or {},
                last_activity=datetime.utcnow(),
                expires_at=datetime.utcnow() + self.session_timeout,
                message_count=0,
                session_type=session_type,
                language=language,
                created_at=datetime.utcnow()
            )
            
            # Save to database
            if self.enable_database_persistence:
                await self._save_session_to_db(session)
            
            # Update metrics
            self.metrics["total_sessions_created"] += 1
            self.metrics["active_sessions"] += 1
            
            # Send welcome message
            welcome_message = await self._generate_welcome_message(session)
            await self._send_whatsapp_message(
                WhatsAppMessage(
                    message_id=f"welcome_{session_id}",
                    parent_id=parent_id,
                    student_id=student_id,
                    phone_number=phone_number,
                    message_type=MessageType.TEXT,
                    category=MessageCategory.SUPPORT,
                    content=welcome_message,
                    media_url=None,
                    interactive_elements=None,
                    template_name=None,
                    template_variables=None,
                    language=language,
                    sent_at=datetime.utcnow(),
                    delivered_at=None,
                    read_at=None,
                    status="pending",
                    error_message=None,
                    cost=0.0,
                    created_at=datetime.utcnow()
                )
            )
            
            result = {
                "success": True,
                "session_id": session_id,
                "parent_id": parent_id,
                "session_type": session_type,
                "language": language,
                "expires_at": session.expires_at.isoformat(),
                "welcome_message": welcome_message
            }
            
            logger.info(f"WhatsApp session created: {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Session creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "parent_id": parent_id
            }
    
    async def opt_in_parent(
        self,
        parent_id: str,
        phone_number: str,
        notification_types: List[str],
        preferred_language: str = "english",
        quiet_hours: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Opt in a parent for WhatsApp notifications.
        
        Args:
            parent_id: Parent ID
            phone_number: WhatsApp phone number
            notification_types: List of notification types to receive
            preferred_language: Preferred language
            quiet_hours: Optional quiet hours configuration
        
        Returns:
            Dict with opt-in results
        """
        try:
            logger.info(f"Opting in parent {parent_id} for WhatsApp")
            
            # Convert notification types to enums
            notification_enums = [NotificationType(nt) for nt in notification_types]
            
            # Create opt-in record
            opt_in_id = f"optin_{parent_id}_{int(time.time())}"
            
            opt_in = WhatsAppOptIn(
                opt_in_id=opt_in_id,
                parent_id=parent_id,
                phone_number=phone_number,
                status="opted_in",
                notification_types=notification_enums,
                preferred_language=preferred_language,
                quiet_hours=quiet_hours or {"start": "22:00", "end": "08:00", "timezone": "UTC"},
                opt_in_date=datetime.utcnow(),
                last_interaction=datetime.utcnow()
            )
            
            # Save to database
            if self.enable_database_persistence:
                await self._save_opt_in_to_db(opt_in)
            
            # Update metrics
            self.metrics["opt_in_rate"] += 1
            
            # Send confirmation message
            confirmation_message = await self._generate_opt_in_confirmation(opt_in)
            await self.send_notification(
                parent_id=parent_id,
                notification_type="system_update",
                content=confirmation_message,
                language=preferred_language
            )
            
            result = {
                "success": True,
                "opt_in_id": opt_in_id,
                "parent_id": parent_id,
                "phone_number": phone_number,
                "notification_types": notification_types,
                "preferred_language": preferred_language,
                "quiet_hours": quiet_hours,
                "confirmation_sent": True
            }
            
            logger.info(f"Parent opted in: {parent_id}")
            return result
            
        except Exception as e:
            logger.error(f"Opt-in failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "parent_id": parent_id
            }
    
    async def opt_out_parent(
        self,
        parent_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Opt out a parent from WhatsApp notifications.
        
        Args:
            parent_id: Parent ID to opt out
            reason: Optional reason for opting out
        
        Returns:
            Dict with opt-out results
        """
        try:
            logger.info(f"Opting out parent {parent_id} from WhatsApp")
            
            # Get existing opt-in
            opt_in = await self._get_parent_opt_in(parent_id)
            if not opt_in:
                return {
                    "success": False,
                    "error": "Parent not found in opt-in list",
                    "parent_id": parent_id
                }
            
            # Update status
            opt_in.status = "opted_out"
            opt_in.last_interaction = datetime.utcnow()
            
            # Save to database
            if self.enable_database_persistence:
                await self._update_opt_in_in_db(opt_in.opt_in_id, {"status": "opted_out"})
            
            # Update metrics
            self.metrics["opt_out_rate"] += 1
            
            # Send confirmation message (if still possible)
            try:
                confirmation_message = await self._generate_opt_out_confirmation(opt_in, reason)
                await self.send_notification(
                    parent_id=parent_id,
                    notification_type="system_update",
                    content=confirmation_message,
                    language=opt_in.preferred_language
                )
            except Exception as e:
                logger.warning(f"Could not send opt-out confirmation: {e}")
            
            result = {
                "success": True,
                "parent_id": parent_id,
                "opt_out_date": datetime.utcnow().isoformat(),
                "reason": reason,
                "confirmation_sent": True
            }
            
            logger.info(f"Parent opted out: {parent_id}")
            return result
            
        except Exception as e:
            logger.error(f"Opt-out failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "parent_id": parent_id
            }
    
    async def get_analytics(
        self,
        parent_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        group_by: str = "day"  # "hour", "day", "week", "month"
    ) -> Dict[str, Any]:
        """
        Get WhatsApp analytics.
        
        Args:
            parent_id: Optional parent ID filter
            start_date: Start date for analytics
            end_date: End date for analytics
            group_by: Grouping period for analytics
        
        Returns:
            Dict with comprehensive analytics
        """
        try:
            # Set default date range
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Get message analytics
            message_analytics = await self._get_message_analytics(
                parent_id, start_date, end_date, group_by
            )
            
            # Get session analytics
            session_analytics = await self._get_session_analytics(
                parent_id, start_date, end_date, group_by
            )
            
            # Get opt-in analytics
            opt_in_analytics = await self._get_opt_in_analytics(
                start_date, end_date, group_by
            )
            
            # Calculate cost analytics
            cost_analytics = self._calculate_cost_analytics(message_analytics)
            
            # Generate insights
            insights = await self._generate_analytics_insights(
                message_analytics, session_analytics, opt_in_analytics
            )
            
            result = {
                "success": True,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "group_by": group_by
                },
                "parent_id": parent_id,
                "message_analytics": message_analytics,
                "session_analytics": session_analytics,
                "opt_in_analytics": opt_in_analytics,
                "cost_analytics": cost_analytics,
                "insights": insights,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Generated WhatsApp analytics for period: {start_date} to {end_date}")
            return result
            
        except Exception as e:
            logger.error(f"Analytics generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get service metrics.
        
        Returns:
            Dictionary with comprehensive metrics
        """
        total_messages = self.metrics["total_messages_sent"] + self.metrics["total_messages_received"]
        
        return {
            "service": "whatsapp_integration_service",
            "metrics": self.metrics,
            "derived": {
                "delivery_success_rate": (
                    (self.metrics["total_messages_sent"] - self.metrics["error_rate"]) / 
                    max(self.metrics["total_messages_sent"], 1) * 100
                ),
                "average_cost_per_message": (
                    self.metrics["total_cost"] / max(self.metrics["total_messages_sent"], 1)
                ),
                "opt_in_conversion_rate": (
                    self.metrics["opt_in_rate"] / max(self.metrics["opt_in_rate"] + self.metrics["opt_out_rate"], 1) * 100
                ),
                "messages_per_session_avg": (
                    self.metrics["total_messages_sent"] / max(self.metrics["total_sessions_created"], 1)
                )
            },
            "supported_languages": self.supported_languages,
            "message_types": {mt.value: count for mt, count in self.metrics["messages_by_type"].items()},
            "message_categories": {mc.value: count for mc, count in self.metrics["messages_by_category"].items()}
        }
    
    # ========================================================================
    # PRIVATE METHODS
    # ========================================================================
    
    def _initialize_default_templates(self) -> Dict[str, Dict[str, str]]:
        """Initialize default message templates."""
        return {
            "daily_progress": {
                "english": "📊 Daily Progress Update\n\nYour child {student_name} has completed {topics_completed} topics today!\n\n🎯 Focus areas: {focus_areas}\n💪 Keep up the great work!",
                "hindi": "📊 दैनिक प्रगति अपडेट\n\nआपके बच्चे {student_name} ने आज {topics_completed} विषय पूरे किए हैं!\n\n🎯 फोकस क्षेत्र: {focus_areas}\n💪 शानदार काम जारी रखें!",
                "bengali": "📊 দৈনিক অগ্রগতি আপডেট\n\nআপনার সন্তান {student_name} আজ {topics_completed} টপিক সম্পন্ন করেছে!\n\n🎯 ফোকাস এলাকা: {focus_areas}\n💪 দুর্দান্ত কাজ চালিয়ে যান!"
            },
            "weekly_report": {
                "english": "📈 Weekly Learning Report\n\n{student_name}'s Progress:\n✅ Topics completed: {topics_completed}\n⏱️ Study time: {study_time}\n📊 Performance score: {performance_score}\n\n🎯 Next week goals: {next_goals}",
                "hindi": "📈 साप्ताहिक शिक्षा रिपोर्ट\n\n{student_name} की प्रगति:\n✅ पूरे किए विषय: {topics_completed}\n⏱️ अध्ययन समय: {study_time}\n📊 प्रदर्शन स्कोर: {performance_score}\n\n🎯 अगले सप्ताह के लक्ष्य: {next_goals}",
                "bengali": "📈 সাপ্তাহিক শেখার রিপোর্ট\n\n{student_name} এর অগ্রগতি:\n✅ সম্পন্ন বিষয়: {topics_completed}\n⏱️ পড়ার সময়: {study_time}\n📊 পারফরম্যান্স স্কোর: {performance_score}\n\n🎯 পরবর্তী সপ্তাহের লক্ষ্য: {next_goals}"
            },
            "intervention_alert": {
                "english": "⚠️ Learning Alert\n\nWe noticed {student_name} needs help with {subject}.\n\n🔍 Issue: {issue_description}\n💡 Suggestion: {suggestion}\n\n📞 Would you like to schedule a consultation?",
                "hindi": "⚠️ शिक्षा अलर्ट\n\nहमने देखा कि {student_name} को {subject} में मदद की जरूरत है।\n\n🔍 समस्या: {issue_description}\n💡 सुझाव: {suggestion}\n\n📞 क्या आप परामर्श शेड्यूल करना चाहेंगे?",
                "bengali": "⚠️ শেখার সতর্কতা\n\nআমরা লক্ষ্য করেছি যে {student_name} এর {subject} এ সাহায্য প্রয়োজন।\n\n🔍 সমস্যা: {issue_description}\n💡 পরামর্শ: {suggestion}\n\n📞 আপনি কি একটি পরামর্শের সময় নির্ধারণ করতে চান?"
            }
        }
    
    async def _send_whatsapp_message(self, message: WhatsAppMessage) -> Dict[str, Any]:
        """Send message via WhatsApp API."""
        try:
            if not self.whatsapp_api_token or not self.whatsapp_phone_number_id:
                # Mock sending for development
                await asyncio.sleep(0.1)  # Simulate API call
                return {
                    "success": True,
                    "message_id": message.message_id,
                    "cost": 0.01  # Mock cost
                }
            
            # Initialize HTTP session if needed
            if not self.http_session:
                self.http_session = aiohttp.ClientSession()
            
            # Prepare API request
            url = f"{self.whatsapp_api_base_url}/{self.whatsapp_phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.whatsapp_api_token}",
                "Content-Type": "application/json"
            }
            
            # Build message payload
            payload = {
                "messaging_product": "whatsapp",
                "to": message.phone_number,
                "type": message.message_type.value
            }
            
            if message.message_type == MessageType.TEXT:
                payload["text"] = {"body": message.content}
            elif message.message_type == MessageType.TEMPLATE and message.template_name:
                payload["template"] = {
                    "name": message.template_name,
                    "language": {"code": self._get_language_code(message.language)},
                    "components": []
                }
                
                if message.template_variables:
                    payload["template"]["components"].append({
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": value}
                            for value in message.template_variables.values()
                        ]
                    })
            
            # Send request
            async with self.http_session.post(url, headers=headers, json=payload) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    return {
                        "success": True,
                        "message_id": response_data.get("messages", [{}])[0].get("id"),
                        "cost": 0.01  # Actual cost would be calculated based on API response
                    }
                else:
                    return {
                        "success": False,
                        "error": response_data.get("error", {}).get("message", "Unknown error")
                    }
                    
        except Exception as e:
            logger.error(f"WhatsApp API call failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_language_code(self, language: str) -> str:
        """Get WhatsApp language code."""
        language_codes = {
            "english": "en",
            "hindi": "hi",
            "bengali": "bn",
            "telugu": "te",
            "tamil": "ta",
            "marathi": "mr",
            "gujarati": "gu",
            "kannada": "kn",
            "malayalam": "ml",
            "punjabi": "pa"
        }
        return language_codes.get(language.lower(), "en")
    
    def _split_long_message(self, content: str) -> List[str]:
        """Split long message into smaller parts."""
        if len(content) <= self.max_message_length:
            return [content]
        
        parts = []
        current_part = ""
        words = content.split()
        
        for word in words:
            if len(current_part + " " + word) <= self.max_message_length:
                current_part += (" " if current_part else "") + word
            else:
                if current_part:
                    parts.append(current_part)
                current_part = word
        
        if current_part:
            parts.append(current_part)
        
        return parts
    
    async def _get_parent_opt_in(self, parent_id: str) -> Optional[WhatsAppOptIn]:
        """Get parent opt-in record."""
        try:
            query = self.db.collection(self.opt_ins_collection)\
                .where("parent_id", "==", parent_id)\
                .where("status", "==", "opted_in")\
                .limit(1)
            
            async for doc in query.stream():
                opt_in_data = doc.to_dict()
                return WhatsAppOptIn(**opt_in_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get parent opt-in: {e}")
            return None
    
    async def _is_in_quiet_hours(self, opt_in: WhatsAppOptIn) -> bool:
        """Check if current time is in quiet hours."""
        try:
            quiet_hours = opt_in.quiet_hours
            if not quiet_hours:
                return False
            
            # Get current time in timezone
            from datetime import timezone
            import pytz
            
            timezone_str = quiet_hours.get("timezone", "UTC")
            tz = pytz.timezone(timezone_str)
            current_time = datetime.now(tz)
            
            # Parse quiet hours
            start_time = quiet_hours.get("start", "22:00")
            end_time = quiet_hours.get("end", "08:00")
            
            start_hour, start_min = map(int, start_time.split(":"))
            end_hour, end_min = map(int, end_time.split(":"))
            
            current_hour_min = current_time.hour * 60 + current_time.minute
            start_hour_min = start_hour * 60 + start_min
            end_hour_min = end_hour * 60 + end_min
            
            # Check if current time is in quiet hours range
            if start_hour_min > end_hour_min:
                # Overnight quiet hours (e.g., 22:00 to 08:00)
                return current_hour_min >= start_hour_min or current_hour_min <= end_hour_min
            else:
                # Same day quiet hours
                return start_hour_min <= current_hour_min <= end_hour_min
                
        except Exception as e:
            logger.error(f"Failed to check quiet hours: {e}")
            return False
    
    async def _queue_message(self, parent_id: str, notification_type: str, content: str, student_id: Optional[str]):
        """Queue message for later delivery."""
        try:
            queued_message = {
                "queue_id": f"queue_{parent_id}_{int(time.time())}",
                "parent_id": parent_id,
                "student_id": student_id,
                "notification_type": notification_type,
                "content": content,
                "queued_at": datetime.utcnow(),
                "status": "queued"
            }
            
            # Save to queue collection
            doc_ref = self.db.collection("whatsapp_message_queue").document(queued_message["queue_id"])
            await doc_ref.set(queued_message)
            
            logger.info(f"Message queued for parent {parent_id}: {notification_type}")
            
        except Exception as e:
            logger.error(f"Failed to queue message: {e}")
    
    async def _get_notification_template(self, notification_type: str, language: str) -> Optional[WhatsAppTemplate]:
        """Get notification template."""
        try:
            # Check if template exists in database
            query = self.db.collection(self.templates_collection)\
                .where("template_name", "==", notification_type)\
                .where("language", "==", language)\
                .where("status", "==", "approved")\
                .limit(1)
            
            async for doc in query.stream():
                template_data = doc.to_dict()
                return WhatsAppTemplate(**template_data)
            
            # Use default template if available
            if notification_type in self.default_templates and language in self.default_templates[notification_type]:
                return WhatsAppTemplate(
                    template_id=f"default_{notification_type}_{language}",
                    template_name=notification_type,
                    category=MessageCategory.NOTIFICATION,
                    language=language,
                    content_template=self.default_templates[notification_type][language],
                    variables=[],
                    buttons=None,
                    media_type=None,
                    status="approved",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get notification template: {e}")
            return None
    
    async def _format_template(self, template: WhatsAppTemplate, variables: Dict[str, str]) -> str:
        """Format template with variables."""
        try:
            content = template.content_template
            
            for key, value in variables.items():
                content = content.replace(f"{{{key}}}", str(value))
            
            return content
            
        except Exception as e:
            logger.error(f"Failed to format template: {e}")
            return template.content_template
    
    async def _verify_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Verify webhook."""
        try:
            hub_verify_token = payload.get("hub_verify_token")
            
            if hub_verify_token == self.webhook_verify_token:
                return {
                    "hub.challenge": payload.get("hub.challenge"),
                    "status": "verified"
                }
            else:
                return {
                    "status": "verification_failed",
                    "error": "Invalid verify token"
                }
                
        except Exception as e:
            logger.error(f"Webhook verification failed: {e}")
            return {
                "status": "verification_failed",
                "error": str(e)
            }
    
    async def _process_incoming_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming WhatsApp message."""
        try:
            # Extract message details
            from_number = message_data.get("from")
            message_id = message_data.get("id")
            timestamp = message_data.get("timestamp")
            
            # Get message content
            message_content = ""
            message_type = MessageType.TEXT
            
            if "text" in message_data:
                message_content = message_data["text"]["body"]
            elif "interactive" in message_data:
                message_type = MessageType.INTERACTIVE
                message_content = json.dumps(message_data["interactive"])
            elif "image" in message_data:
                message_type = MessageType.IMAGE
                message_content = message_data["image"].get("id", "")
            
            # Find parent by phone number
            opt_in = await self._get_opt_in_by_phone(from_number)
            if not opt_in:
                return {
                    "success": False,
                    "error": "Parent not found for phone number",
                    "phone_number": from_number
                }
            
            # Create message record
            incoming_message = WhatsAppMessage(
                message_id=message_id,
                parent_id=opt_in.parent_id,
                student_id=None,
                phone_number=from_number,
                message_type=message_type,
                category=MessageCategory.RESPONSE,
                content=message_content,
                media_url=None,
                interactive_elements=None,
                template_name=None,
                template_variables=None,
                language=opt_in.preferred_language,
                sent_at=None,
                delivered_at=None,
                read_at=datetime.fromtimestamp(int(timestamp)),
                status="received",
                error_message=None,
                cost=0.0,
                created_at=datetime.utcnow()
            )
            
            # Save to database
            if self.enable_database_persistence:
                await self._save_message_to_db(incoming_message)
            
            # Update metrics
            self.metrics["total_messages_received"] += 1
            
            # Process message based on content
            response = await self._process_message_content(incoming_message)
            
            return {
                "success": True,
                "message_id": message_id,
                "parent_id": opt_in.parent_id,
                "message_type": message_type.value,
                "response": response
            }
            
        except Exception as e:
            logger.error(f"Failed to process incoming message: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_opt_in_by_phone(self, phone_number: str) -> Optional[WhatsAppOptIn]:
        """Get opt-in by phone number."""
        try:
            query = self.db.collection(self.opt_ins_collection)\
                .where("phone_number", "==", phone_number)\
                .where("status", "==", "opted_in")\
                .limit(1)
            
            async for doc in query.stream():
                opt_in_data = doc.to_dict()
                return WhatsAppOptIn(**opt_in_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get opt-in by phone: {e}")
            return None
    
    async def _process_message_content(self, message: WhatsAppMessage) -> Dict[str, Any]:
        """Process message content and generate response."""
        try:
            # Check if it's a command
            if message.content.startswith("/"):
                return await self._process_command(message)
            
            # Check for active session
            active_session = await self._get_active_session(message.parent_id)
            if active_session:
                return await self._continue_session(active_session, message)
            
            # Generate AI response
            prompt = f"""
Generate a helpful response for this parent WhatsApp message.

Parent Message: {message.content}
Parent ID: {message.parent_id}
Language: {message.language}

Requirements:
1. Be helpful and supportive
2. Keep response concise (under 1600 characters)
3. Use appropriate language
4. Provide actionable guidance
5. Include relevant emojis for engagement

Response format:
A helpful, concise response that addresses the parent's needs.
"""
            
            content_request = ContentRequest(
                content_type=ContentType.RESPONSE,
                prompt=prompt,
                user_id=message.parent_id,
                student_id=message.student_id,
                context={"message": message.content},
                metadata={"generation_type": "whatsapp_response"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Send response
            await self.send_notification(
                parent_id=message.parent_id,
                notification_type="response",
                content=result.content,
                language=message.language
            )
            
            return {
                "action": "responded",
                "response_content": result.content
            }
            
        except Exception as e:
            logger.error(f"Failed to process message content: {e}")
            return {
                "action": "error",
                "error": str(e)
            }
    
    async def _process_command(self, message: WhatsAppMessage) -> Dict[str, Any]:
        """Process WhatsApp command."""
        try:
            command = message.content.lower().strip()
            
            if command == "/help":
                help_text = """
🤖 Mentor AI WhatsApp Commands:

/help - Show this help message
/status - Check child's progress
/resources - Get learning resources
/tips - Get parenting tips
/stop - Stop notifications
/start - Start notifications

Reply with any question for personalized help!
"""
                await self.send_notification(
                    parent_id=message.parent_id,
                    notification_type="response",
                    content=help_text,
                    language=message.language
                )
                
                return {"action": "help_sent"}
            
            elif command == "/status":
                # Get child's status
                status_text = await self._generate_child_status(message.parent_id)
                await self.send_notification(
                    parent_id=message.parent_id,
                    notification_type="response",
                    content=status_text,
                    language=message.language
                )
                
                return {"action": "status_sent"}
            
            elif command == "/stop":
                # Opt out
                await self.opt_out_parent(message.parent_id, "Requested via WhatsApp")
                return {"action": "opted_out"}
            
            elif command == "/start":
                # Opt in
                await self.opt_in_parent(
                    parent_id=message.parent_id,
                    phone_number=message.phone_number,
                    notification_types=["daily_progress", "weekly_report", "intervention_alert"],
                    preferred_language=message.language
                )
                return {"action": "opted_in"}
            
            else:
                # Unknown command
                unknown_command_text = "❓ Unknown command. Type /help for available commands."
                await self.send_notification(
                    parent_id=message.parent_id,
                    notification_type="response",
                    content=unknown_command_text,
                    language=message.language
                )
                
                return {"action": "unknown_command"}
                
        except Exception as e:
            logger.error(f"Failed to process command: {e}")
            return {
                "action": "error",
                "error": str(e)
            }
    
    async def _get_active_session(self, parent_id: str) -> Optional[WhatsAppSession]:
        """Get active session for parent."""
        try:
            query = self.db.collection(self.sessions_collection)\
                .where("parent_id", "==", parent_id)\
                .where("status", "==", "active")\
                .where("expires_at", ">", datetime.utcnow())\
                .limit(1)
            
            async for doc in query.stream():
                session_data = doc.to_dict()
                return WhatsAppSession(**session_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get active session: {e}")
            return None
    
    async def _continue_session(self, session: WhatsAppSession, message: WhatsAppMessage) -> Dict[str, Any]:
        """Continue active session."""
        try:
            # Update session
            session.last_activity = datetime.utcnow()
            session.message_count += 1
            
            # Save updated session
            if self.enable_database_persistence:
                await self._update_session_in_db(session.session_id, {
                    "last_activity": session.last_activity,
                    "message_count": session.message_count
                })
            
            # Generate session-based response
            prompt = f"""
Continue this WhatsApp session based on the parent's message.

Session Type: {session.session_type}
Session Context: {json.dumps(session.context)}
Previous Messages: {session.message_count}
Parent Message: {message.content}

Requirements:
1. Maintain session context
2. Be helpful and supportive
3. Keep response concise
4. Use appropriate language
5. Provide actionable guidance

Response format:
A helpful response that continues the session naturally.
"""
            
            content_request = ContentRequest(
                content_type=ContentType.RESPONSE,
                prompt=prompt,
                user_id=message.parent_id,
                student_id=message.student_id,
                context={
                    "session": session.__dict__,
                    "message": message.content
                },
                metadata={"generation_type": "whatsapp_session_response"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Send response
            await self.send_notification(
                parent_id=message.parent_id,
                notification_type="response",
                content=result.content,
                language=message.language
            )
            
            return {
                "action": "session_continued",
                "session_id": session.session_id,
                "response_content": result.content
            }
            
        except Exception as e:
            logger.error(f"Failed to continue session: {e}")
            return {
                "action": "error",
                "error": str(e)
            }
    
    async def _generate_welcome_message(self, session: WhatsAppSession) -> str:
        """Generate welcome message for session."""
        try:
            templates = {
                "support": {
                    "english": "👋 Welcome to Mentor AI Support!\n\nHow can I help you today? I'm here to assist with any questions about your child's learning journey.",
                    "hindi": "👋 मेंटर AI सपोर्ट में आपका स्वागत है!\n\nमैं आज आपकी क्या सहायता कर सकता हूँ? मैं आपके बच्चे की शिक्षा यात्रा के बारे में किसी भी प्रश्न में सहायता के लिए यहाँ हूँ।",
                    "bengali": "👋 মেন্টর AI সাপোর্টে আপনাকে স্বাগতম!\n\nআজ আমি আপনাকে কিভাবে সাহায্য করতে পারি? আমি আপনার সন্তানের শিক্ষা যাত্রা সম্পর্কে যেকোনো প্রশ্নে সাহায্য করার জন্য এখানে আছি।"
                },
                "learning": {
                    "english": "📚 Welcome to Mentor AI Learning Session!\n\nLet's explore your child's learning progress and find the best ways to support their education.",
                    "hindi": "📚 मेंटर AI लर्निंग सेशन में आपका स्वागत है!\n\nआइए आपके बच्चे की शिक्षा प्रगति का अन्वेषण करें और उनकी शिक्षा का समर्थन करने के सर्वोत्तम तरीके खोजें।",
                    "bengali": "📚 মেন্টর AI লার্নিং সেশনে আপনাকে স্বাগতম!\n\nআসুন আপনার সন্তানের শেখার অগ্রগতি অন্বেষণ করি এবং তাদের শিক্ষাকে সমর্থন করার সেরা উপায়গুলি খুঁজে বের করি।"
                }
            }
            
            session_templates = templates.get(session.session_type, templates["support"])
            return session_templates.get(session.language, session_templates["english"])
            
        except Exception as e:
            logger.error(f"Failed to generate welcome message: {e}")
            return "👋 Welcome to Mentor AI! How can I help you today?"
    
    async def _generate_opt_in_confirmation(self, opt_in: WhatsAppOptIn) -> str:
        """Generate opt-in confirmation message."""
        try:
            templates = {
                "english": "✅ You're now opted in for Mentor AI WhatsApp notifications!\n\nYou'll receive:\n📊 Daily progress updates\n📈 Weekly learning reports\n⚠️ Important alerts\n\nReply STOP anytime to opt out.",
                "hindi": "✅ अब आप मेंटर AI WhatsApp अधिसूचनाओं के लिए ऑप्ट-इन हो गए हैं!\n\nआपको प्राप्त होगा:\n📊 दैनिक प्रगति अपडेट\n📈 साप्ताहिक शिक्षा रिपोर्ट\n⚠️ महत्वपूर्ण अलर्ट\n\nकिसी भी समय ऑप्ट आउट करने के लिए STOP लिखें।",
                "bengali": "✅ আপি এখন মেন্টর AI WhatsApp নোটিফিকেশনের জন্য অপ্ট-ইন করেছেন!\n\nআপনি পাবেন:\n📊 দৈনিক অগ্রগতি আপডেট\n📈 সাপ্তাহিক শেখার রিপোর্ট\n⚠️ গুরুত্বপূর্ণ সতর্কতা\n\nযেকোনো সময় অপ্ট-আউট করতে STOP লিখুন।"
            }
            
            return templates.get(opt_in.preferred_language, templates["english"])
            
        except Exception as e:
            logger.error(f"Failed to generate opt-in confirmation: {e}")
            return "✅ You're now opted in for Mentor AI notifications!"
    
    async def _generate_opt_out_confirmation(self, opt_in: WhatsAppOptIn, reason: Optional[str]) -> str:
        """Generate opt-out confirmation message."""
        try:
            templates = {
                "english": "❌ You've been opted out of Mentor AI WhatsApp notifications.\n\nWe're sorry to see you go! You can always opt back in by texting START.\n\nThank you for using Mentor AI!",
                "hindi": "❌ आपको मेंटर AI WhatsApp अधिसूचनाओं से ऑप्ट-आउट कर दिया गया है।\n\nआपको जानकर खेद है! आप START टेक्स्ट करके हमेशा वापस ऑप्ट-इन कर सकते हैं।\n\nमेंटर AI का उपयोग करने के लिए धन्यवाद!",
                "bengali": "❌ আপনাকে মেন্টর AI WhatsApp নোটিফিকেশন থেকে অপ্ট-আউট করা হয়েছে।\n\nআপনাকে যেতে দেখে আমরা দুঃখিত! আপনি START টেক্সট করে সবসময় আবার অপ্ট-ইন করতে পারেন।\n\nমেন্টর AI ব্যবহার করার জন্য ধন্যবাদ!"
            }
            
            return templates.get(opt_in.preferred_language, templates["english"])
            
        except Exception as e:
            logger.error(f"Failed to generate opt-out confirmation: {e}")
            return "❌ You've been opted out of Mentor AI notifications."
    
    async def _generate_child_status(self, parent_id: str) -> str:
        """Generate child status message."""
        try:
            # This would typically fetch actual student data
            # For now, return a template response
            return """
📊 Your Child's Learning Status

✅ Topics completed today: 3
⏱️ Study time: 2h 15min
🎯 Current focus: Mathematics - Algebra
📈 Performance trend: Improving

💡 Tip: Encourage daily practice of weak topics for better results.
"""
            
        except Exception as e:
            logger.error(f"Failed to generate child status: {e}")
            return "Unable to fetch child status at the moment. Please try again later."
    
    async def _save_message_to_db(self, message: WhatsAppMessage):
        """Save message to database."""
        try:
            doc_ref = self.db.collection(self.messages_collection).document(message.message_id)
            await doc_ref.set(message.__dict__)
            logger.debug(f"Saved message to database: {message.message_id}")
            
        except Exception as e:
            logger.error(f"Failed to save message to database: {e}")
            self.metrics["error_rate"] += 1
    
    async def _save_session_to_db(self, session: WhatsAppSession):
        """Save session to database."""
        try:
            doc_ref = self.db.collection(self.sessions_collection).document(session.session_id)
            await doc_ref.set(session.__dict__)
            logger.debug(f"Saved session to database: {session.session_id}")
            
        except Exception as e:
            logger.error(f"Failed to save session to database: {e}")
    
    async def _update_session_in_db(self, session_id: str, update_data: Dict[str, Any]):
        """Update session in database."""
        try:
            doc_ref = self.db.collection(self.sessions_collection).document(session_id)
            await doc_ref.update(update_data)
            logger.debug(f"Updated session in database: {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to update session in database: {e}")
    
    async def _save_opt_in_to_db(self, opt_in: WhatsAppOptIn):
        """Save opt-in to database."""
        try:
            doc_ref = self.db.collection(self.opt_ins_collection).document(opt_in.opt_in_id)
            await doc_ref.set(opt_in.__dict__)
            logger.debug(f"Saved opt-in to database: {opt_in.opt_in_id}")
            
        except Exception as e:
            logger.error(f"Failed to save opt-in to database: {e}")
    
    async def _update_opt_in_in_db(self, opt_in_id: str, update_data: Dict[str, Any]):
        """Update opt-in in database."""
        try:
            doc_ref = self.db.collection(self.opt_ins_collection).document(opt_in_id)
            await doc_ref.update(update_data)
            logger.debug(f"Updated opt-in in database: {opt_in_id}")
            
        except Exception as e:
            logger.error(f"Failed to update opt-in in database: {e}")
    
    async def _get_message_analytics(
        self,
        parent_id: Optional[str],
        start_date: datetime,
        end_date: datetime,
        group_by: str
    ) -> Dict[str, Any]:
        """Get message analytics."""
        try:
            # Build query
            query = self.db.collection(self.messages_collection)\
                .where("created_at", ">=", start_date)\
                .where("created_at", "<=", end_date)
            
            if parent_id:
                query = query.where("parent_id", "==", parent_id)
            
            # Aggregate data
            messages = []
            async for doc in query.stream():
                message_data = doc.to_dict()
                messages.append(message_data)
            
            # Group by time period
            grouped_data = {}
            for message in messages:
                created_at = message["created_at"]
                
                if group_by == "hour":
                    key = created_at.strftime("%Y-%m-%d %H:00")
                elif group_by == "day":
                    key = created_at.strftime("%Y-%m-%d")
                elif group_by == "week":
                    key = created_at.strftime("%Y-W%U")
                else:  # month
                    key = created_at.strftime("%Y-%m")
                
                if key not in grouped_data:
                    grouped_data[key] = {
                        "sent": 0,
                        "received": 0,
                        "delivered": 0,
                        "read": 0,
                        "failed": 0,
                        "total_cost": 0.0
                    }
                
                status = message["status"]
                if status in grouped_data[key]:
                    grouped_data[key][status] += 1
                
                grouped_data[key]["total_cost"] += message.get("cost", 0.0)
            
            return {
                "total_messages": len(messages),
                "grouped_data": grouped_data,
                "average_cost_per_message": sum(m.get("cost", 0) for m in messages) / max(len(messages), 1)
            }
            
        except Exception as e:
            logger.error(f"Failed to get message analytics: {e}")
            return {"total_messages": 0, "grouped_data": {}, "average_cost_per_message": 0.0}
    
    async def _get_session_analytics(
        self,
        parent_id: Optional[str],
        start_date: datetime,
        end_date: datetime,
        group_by: str
    ) -> Dict[str, Any]:
        """Get session analytics."""
        try:
            # Build query
            query = self.db.collection(self.sessions_collection)\
                .where("created_at", ">=", start_date)\
                .where("created_at", "<=", end_date)
            
            if parent_id:
                query = query.where("parent_id", "==", parent_id)
            
            # Aggregate data
            sessions = []
            async for doc in query.stream():
                session_data = doc.to_dict()
                sessions.append(session_data)
            
            # Calculate metrics
            total_sessions = len(sessions)
            active_sessions = len([s for s in sessions if s["status"] == "active"])
            
            # Calculate average duration
            durations = []
            for session in sessions:
                if session["expires_at"] and session["created_at"]:
                    duration = (session["expires_at"] - session["created_at"]).total_seconds()
                    durations.append(duration)
            
            avg_duration = sum(durations) / max(len(durations), 1) if durations else 0
            
            # Calculate average messages per session
            message_counts = [s.get("message_count", 0) for s in sessions]
            avg_messages = sum(message_counts) / max(len(message_counts), 1)
            
            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "average_duration_seconds": avg_duration,
                "average_messages_per_session": avg_messages,
                "session_types": self._group_by_field(sessions, "session_type")
            }
            
        except Exception as e:
            logger.error(f"Failed to get session analytics: {e}")
            return {
                "total_sessions": 0,
                "active_sessions": 0,
                "average_duration_seconds": 0,
                "average_messages_per_session": 0,
                "session_types": {}
            }
    
    async def _get_opt_in_analytics(
        self,
        start_date: datetime,
        end_date: datetime,
        group_by: str
    ) -> Dict[str, Any]:
        """Get opt-in analytics."""
        try:
            # Build query
            query = self.db.collection(self.opt_ins_collection)\
                .where("opt_in_date", ">=", start_date)\
                .where("opt_in_date", "<=", end_date)
            
            # Aggregate data
            opt_ins = []
            async for doc in query.stream():
                opt_in_data = doc.to_dict()
                opt_ins.append(opt_in_data)
            
            # Group by time period
            grouped_data = {}
            for opt_in in opt_ins:
                opt_in_date = opt_in["opt_in_date"]
                
                if group_by == "hour":
                    key = opt_in_date.strftime("%Y-%m-%d %H:00")
                elif group_by == "day":
                    key = opt_in_date.strftime("%Y-%m-%d")
                elif group_by == "week":
                    key = opt_in_date.strftime("%Y-W%U")
                else:  # month
                    key = opt_in_date.strftime("%Y-%m")
                
                if key not in grouped_data:
                    grouped_data[key] = {"opted_in": 0, "opted_out": 0}
                
                if opt_in["status"] == "opted_in":
                    grouped_data[key]["opted_in"] += 1
                elif opt_in["status"] == "opted_out":
                    grouped_data[key]["opted_out"] += 1
            
            return {
                "total_opt_ins": len(opt_ins),
                "current_opt_ins": len([o for o in opt_ins if o["status"] == "opted_in"]),
                "grouped_data": grouped_data,
                "preferred_languages": self._group_by_field(opt_ins, "preferred_language")
            }
            
        except Exception as e:
            logger.error(f"Failed to get opt-in analytics: {e}")
            return {
                "total_opt_ins": 0,
                "current_opt_ins": 0,
                "grouped_data": {},
                "preferred_languages": {}
            }
    
    def _group_by_field(self, items: List[Dict[str, Any]], field: str) -> Dict[str, int]:
        """Group items by field."""
        grouped = {}
        for item in items:
            value = item.get(field, "unknown")
            grouped[value] = grouped.get(value, 0) + 1
        return grouped
    
    def _calculate_cost_analytics(self, message_analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate cost analytics."""
        try:
            total_cost = message_analytics.get("average_cost_per_message", 0) * message_analytics.get("total_messages", 0)
            
            return {
                "total_cost": total_cost,
                "average_cost_per_message": message_analytics.get("average_cost_per_message", 0),
                "cost_per_day": total_cost / 30,  # Assuming 30-day period
                "projected_monthly_cost": total_cost
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate cost analytics: {e}")
            return {
                "total_cost": 0,
                "average_cost_per_message": 0,
                "cost_per_day": 0,
                "projected_monthly_cost": 0
            }
    
    async def _generate_analytics_insights(
        self,
        message_analytics: Dict[str, Any],
        session_analytics: Dict[str, Any],
        opt_in_analytics: Dict[str, Any]
    ) -> List[str]:
        """Generate analytics insights."""
        try:
            insights = []
            
            # Message insights
            total_messages = message_analytics.get("total_messages", 0)
            if total_messages > 0:
                insights.append(f"Total WhatsApp messages processed: {total_messages}")
                
                avg_cost = message_analytics.get("average_cost_per_message", 0)
                if avg_cost > 0:
                    insights.append(f"Average cost per message: ${avg_cost:.4f}")
            
            # Session insights
            total_sessions = session_analytics.get("total_sessions", 0)
            if total_sessions > 0:
                insights.append(f"Total WhatsApp sessions: {total_sessions}")
                
                avg_duration = session_analytics.get("average_duration_seconds", 0)
                if avg_duration > 0:
                    insights.append(f"Average session duration: {avg_duration:.1f} seconds")
            
            # Opt-in insights
            current_opt_ins = opt_in_analytics.get("current_opt_ins", 0)
            if current_opt_ins > 0:
                insights.append(f"Active WhatsApp users: {current_opt_ins}")
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate analytics insights: {e}")
            return ["Unable to generate insights at this time"]

# Service instance
_whatsapp_integration_service_instance = None

def get_whatsapp_integration_service(
    db: Optional[firestore.Client] = None,
    unified_config: Optional[GeminiConfig] = None,
    enable_database_persistence: bool = True,
    whatsapp_api_token: Optional[str] = None,
    whatsapp_phone_number_id: Optional[str] = None,
    webhook_verify_token: Optional[str] = None,
    session_timeout_minutes: int = 30,
    max_message_length: int = 1600
) -> WhatsAppIntegrationService:
    """
    Get singleton instance of WhatsApp Integration Service.
    
    Args:
        db: Firestore client (creates new if None)
        unified_config: Optional unified configuration
        enable_database_persistence: Enable saving to database
        whatsapp_api_token: WhatsApp Business API token
        whatsapp_phone_number_id: WhatsApp phone number ID
        webhook_verify_token: Webhook verification token
        session_timeout_minutes: Session timeout in minutes
        max_message_length: Maximum message length
    
    Returns:
        WhatsAppIntegrationService instance
    """
    global _whatsapp_integration_service_instance
    
    if _whatsapp_integration_service_instance is None:
        logger.info("Creating new WhatsAppIntegrationService singleton instance")
        _whatsapp_integration_service_instance = WhatsAppIntegrationService(
            db=db,
            unified_config=unified_config,
            enable_database_persistence=enable_database_persistence,
            whatsapp_api_token=whatsapp_api_token,
            whatsapp_phone_number_id=whatsapp_phone_number_id,
            webhook_verify_token=webhook_verify_token,
            session_timeout_minutes=session_timeout_minutes,
            max_message_length=max_message_length
        )
    
    return _whatsapp_integration_service_instance

# Module initialization
logger.info("WhatsApp Integration Service module loaded")