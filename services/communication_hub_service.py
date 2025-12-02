"""
Enhanced Communication Hub Service

This service provides AI-powered communication suggestions and
management for parent-child interactions.

Features:
- AI communication suggestion engine
- Context-aware conversation starters
- Tone adjustment based on child's mood
- Communication history tracking
- Urgency-based message prioritization
- Multi-language support for suggestions
- Communication effectiveness analysis
- Automated follow-up reminders

Author: Mentor AI Team
Version: 1.0.0
"""

import logging
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import asyncio

from pydantic import BaseModel, Field
from google.cloud import firestore

from services.unified_gemini_config_service import get_unified_gemini_service, GeminiConfig
from services.ai_content_service import get_ai_content_service, ContentType, ContentRequest
from utils.firebase_config import get_firestore_client
from models.database_models import CommunicationRecord, CommunicationTemplate

# Configure logging
logger = logging.getLogger(__name__)

# Communication types and settings
class CommunicationType(Enum):
    """Types of communications."""
    NOTIFICATION = "notification"
    ALERT = "alert"
    INSIGHT = "insight"
    REPORT = "report"
    MESSAGE = "message"
    REMINDER = "reminder"
    ENCOURAGEMENT = "encouragement"

class Channel(Enum):
    """Communication channels."""
    EMAIL = "email"
    PUSH = "push"
    IN_APP = "in_app"
    SMS = "sms"
    WHATSAPP = "whatsapp"

class Priority(Enum):
    """Message priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Tone(Enum):
    """Communication tones."""
    SUPPORTIVE = "supportive"
    MOTIVATIONAL = "motivational"
    CONCERNED = "concerned"
    CELEBRATORY = "celebratory"
    NEUTRAL = "neutral"
    URGENT = "urgent"

class Mood(Enum):
    """Child mood states."""
    HAPPY = "happy"
    STRESSED = "stressed"
    FRUSTRATED = "frustrated"
    TIRED = "tired"
    MOTIVATED = "motivated"
    DISCOURAGED = "discouraged"
    NEUTRAL = "neutral"

@dataclass
class CommunicationRequest:
    """Request for communication generation."""
    
    parent_id: str
    student_id: str
    communication_type: CommunicationType
    context: Optional[Dict[str, Any]] = None
    child_mood: Optional[Mood] = None
    recent_performance: Optional[Dict[str, Any]] = None
    channel: Optional[Channel] = None
    priority: Priority = Priority.MEDIUM
    language: str = "english"
    include_history: bool = True
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CommunicationResult:
    """Result from communication generation."""
    
    communication_id: str
    communication_type: CommunicationType
    channel: Channel
    subject: str
    content: str
    tone: Tone
    priority: Priority
    suggested_timing: Optional[datetime]
    follow_up_actions: List[str]
    effectiveness_score: float
    generation_time_ms: int
    created_at: datetime

class CommunicationHubService:
    """
    Service for enhanced communication management with AI suggestions.
    
    This service leverages AI to generate context-aware communications,
    track history, and optimize parent-child interactions.
    
    Attributes:
        unified_service: Unified Gemini configuration service
        ai_content_service: AI content generation service
        db: Firestore database client
        communication_generators: Handlers for different communication types
        tone_adjuster: AI-powered tone adjustment
        history_analyzer: Communication history analysis
    
    Example:
        >>> service = CommunicationHubService()
        >>> result = service.generate_communication(
        ...     parent_id="parent123",
        ...     student_id="student123",
        ...     communication_type=CommunicationType.ENCOURAGEMENT
        ... )
        >>> print(f"Generated: {result.subject}")
    """
    
    def __init__(
        self,
        db: Optional[firestore.Client] = None,
        unified_config: Optional[GeminiConfig] = None,
        enable_database_persistence: bool = True,
        cache_size: int = 150,
        cache_ttl_hours: int = 8
    ):
        """
        Initialize Communication Hub Service.
        
        Args:
            db: Firestore client (creates new if None)
            unified_config: Optional unified configuration
            enable_database_persistence: Enable saving to database
            cache_size: Maximum cache size
            cache_ttl_hours: Cache TTL in hours
        """
        logger.info("Initializing CommunicationHubService")
        
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
        self.cache_size = cache_size
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        
        # Communication cache
        self.communication_cache: Dict[str, CommunicationResult] = {}
        
        # Collections
        self.communications_collection = "communication_history"
        self.templates_collection = "communication_templates"
        self.engagement_metrics_collection = "engagement_metrics"
        
        # Multi-language support
        self.supported_languages = [
            "english", "hindi", "spanish", "french", "german", 
            "chinese", "japanese", "korean", "portuguese"
        ]
        
        # Metrics
        self.metrics = {
            "total_communications_generated": 0,
            "communications_by_type": {ct.value: 0 for ct in CommunicationType},
            "communications_by_channel": {ch.value: 0 for ch in Channel},
            "communications_by_priority": {pr.value: 0 for pr in Priority},
            "average_effectiveness_score": 0.0,
            "tone_adjustments": 0,
            "language_requests": {lang: 0 for lang in self.supported_languages},
            "cache_hits": 0,
            "cache_misses": 0,
            "database_saves": 0,
            "database_failures": 0
        }
        
        logger.info(
            f"CommunicationHubService initialized (db_persistence={enable_database_persistence}, "
            f"cache_size={cache_size}, cache_ttl={cache_ttl_hours}h)"
        )
    
    async def generate_communication(
        self,
        request: CommunicationRequest
    ) -> CommunicationResult:
        """
        Generate AI-powered communication.
        
        Args:
            request: CommunicationRequest with all generation parameters
        
        Returns:
            CommunicationResult with generated content and metadata
        
        Raises:
            ValueError: If request is invalid
            Exception: If generation fails
        """
        start_time = time.time()
        
        # Generate communication ID
        communication_id = f"comm_{request.parent_id}_{request.student_id}_{int(time.time())}_{hashlib.md5(f'{request.communication_type.value}_{request.language}'.encode()).hexdigest()[:8]}"
        
        logger.info(
            f"Generating {request.communication_type.value} communication: {communication_id}"
        )
        
        try:
            # Check cache
            cache_key = self._generate_cache_key(request)
            if cache_key in self.communication_cache:
                cached_result = self.communication_cache[cache_key]
                logger.info(f"Cache hit for communication: {communication_id}")
                
                # Update metrics
                self.metrics["cache_hits"] += 1
                
                return cached_result
            
            self.metrics["cache_misses"] += 1
            
            # Get communication history and context
            context_data = await self._get_communication_context(request)
            
            # Route to appropriate generator
            generator = self.communication_generators.get(request.communication_type)
            if not generator:
                raise ValueError(f"No generator for communication type: {request.communication_type.value}")
            
            # Generate communication
            communication_data, generation_metadata = await generator(request, context_data)
            
            # Calculate metrics
            generation_time_ms = int((time.time() - start_time) * 1000)
            
            # Determine optimal tone based on mood
            tone = self._determine_optimal_tone(
                request.communication_type,
                request.child_mood,
                communication_data
            )
            
            # Adjust content for tone if needed
            if tone != communication_data.get("tone", Tone.NEUTRAL):
                communication_data = await self._adjust_tone(
                    communication_data,
                    tone,
                    request.child_mood
                )
                self.metrics["tone_adjustments"] += 1
            
            # Determine channel
            channel = request.channel or self._recommend_channel(
                request.communication_type,
                request.priority
            )
            
            # Calculate effectiveness score
            effectiveness_score = self._calculate_effectiveness_score(
                communication_data,
                context_data,
                request
            )
            
            # Create result
            result = CommunicationResult(
                communication_id=communication_id,
                communication_type=request.communication_type,
                channel=channel,
                subject=communication_data.get("subject", "Communication"),
                content=communication_data.get("content", ""),
                tone=tone,
                priority=request.priority,
                suggested_timing=communication_data.get("suggested_timing"),
                follow_up_actions=communication_data.get("follow_up_actions", []),
                effectiveness_score=effectiveness_score,
                generation_time_ms=generation_time_ms,
                created_at=datetime.utcnow()
            )
            
            # Cache result
            if len(self.communication_cache) < self.cache_size:
                self.communication_cache[cache_key] = result
            
            # Save to database
            if self.enable_database_persistence:
                await self._save_communication_to_db(result, request)
            
            # Update metrics
            self.metrics["total_communications_generated"] += 1
            self.metrics["communications_by_type"][request.communication_type.value] += 1
            self.metrics["communications_by_channel"][channel.value] += 1
            self.metrics["communications_by_priority"][request.priority.value] += 1
            self.metrics["language_requests"][request.language] += 1
            self._update_average_effectiveness(effectiveness_score)
            
            logger.info(
                f"Generated {request.communication_type.value} communication: {communication_id}, "
                f"channel={channel.value}, tone={tone.value}, effectiveness={effectiveness_score:.2f}, "
                f"time={generation_time_ms}ms"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Communication generation failed: {e}")
            
            # Update metrics
            if self.enable_database_persistence:
                self.metrics["database_failures"] += 1
            
            raise
    
    async def generate_conversation_starters(
        self,
        parent_id: str,
        student_id: str,
        mood_context: Optional[Mood] = None,
        recent_performance: Optional[Dict[str, Any]] = None,
        conversation_goal: Optional[str] = None,
        language: str = "english"
    ) -> List[str]:
        """
        Generate AI-powered conversation starters.
        
        Args:
            parent_id: Parent ID
            student_id: Student ID
            mood_context: Optional mood context
            recent_performance: Optional recent performance data
            conversation_goal: Optional goal for conversation
            language: Language for starters
        
        Returns:
            List of conversation starter suggestions
        """
        try:
            # Get communication context
            context_data = await self._get_communication_context(
                CommunicationRequest(
                    parent_id=parent_id,
                    student_id=student_id,
                    communication_type=CommunicationType.MESSAGE,
                    child_mood=mood_context,
                    recent_performance=recent_performance,
                    language=language
                )
            )
            
            # Build prompt for conversation starters
            prompt = self._build_conversation_starter_prompt(
                context_data, mood_context, recent_performance, conversation_goal, language
            )
            
            # Generate content using AI service
            content_request = ContentRequest(
                content_type=ContentType.RECOMMENDATION,
                prompt=prompt,
                user_id=parent_id,
                student_id=student_id,
                context={
                    "mood_context": mood_context.value if mood_context else None,
                    "recent_performance": recent_performance,
                    "conversation_goal": conversation_goal,
                    "language": language,
                    "context_data": context_data
                },
                metadata={"generation_type": "conversation_starters"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse conversation starters
            conversation_starters = self._parse_conversation_starters(result.content, language)
            
            logger.info(f"Generated {len(conversation_starters)} conversation starters")
            return conversation_starters
            
        except Exception as e:
            logger.error(f"Failed to generate conversation starters: {e}")
            raise
    
    async def analyze_communication_effectiveness(
        self,
        parent_id: str,
        student_id: str,
        time_period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze communication effectiveness over time.
        
        Args:
            parent_id: Parent ID
            student_id: Student ID
            time_period_days: Period to analyze
        
        Returns:
            Dict with effectiveness analysis and insights
        """
        try:
            # Get communication history
            history = await self._get_communication_history(
                parent_id, student_id, time_period_days
            )
            
            # Analyze effectiveness patterns
            effectiveness_analysis = self._analyze_effectiveness_patterns(history)
            
            # Generate insights
            insights = await self._generate_effectiveness_insights(
                history, effectiveness_analysis
            )
            
            result = {
                "period_days": time_period_days,
                "total_communications": len(history),
                "effectiveness_analysis": effectiveness_analysis,
                "insights": insights,
                "recommendations": await self._generate_effectiveness_recommendations(
                    effectiveness_analysis
                ),
                "analysis_date": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Analyzed communication effectiveness for {parent_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze communication effectiveness: {e}")
            raise
    
    async def schedule_follow_up_reminders(
        self,
        communication_id: str,
        follow_up_actions: List[str],
        parent_id: str,
        student_id: str
    ) -> List[Dict[str, Any]]:
        """
        Schedule follow-up reminders for communications.
        
        Args:
            communication_id: Original communication ID
            follow_up_actions: List of follow-up actions
            parent_id: Parent ID
            student_id: Student ID
        
        Returns:
            List of scheduled reminders
        """
        try:
            reminders = []
            
            for action in follow_up_actions:
                # Determine optimal timing for each action
                timing = self._determine_follow_up_timing(action)
                
                reminder = {
                    "reminder_id": f"rem_{communication_id}_{int(time.time())}_{hashlib.md5(action.encode()).hexdigest()[:8]}",
                    "communication_id": communication_id,
                    "parent_id": parent_id,
                    "student_id": student_id,
                    "action": action,
                    "scheduled_time": timing.isoformat(),
                    "status": "scheduled",
                    "created_at": datetime.utcnow().isoformat()
                }
                reminders.append(reminder)
                
                # Save to database
                if self.enable_database_persistence:
                    await self._save_reminder_to_db(reminder)
            
            logger.info(f"Scheduled {len(reminders)} follow-up reminders")
            return reminders
            
        except Exception as e:
            logger.error(f"Failed to schedule follow-up reminders: {e}")
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get service metrics.
        
        Returns:
            Dictionary with comprehensive metrics
        """
        total_cache_attempts = self.metrics["cache_hits"] + self.metrics["cache_misses"]
        cache_hit_rate = (
            self.metrics["cache_hits"] / total_cache_attempts
            if total_cache_attempts > 0 else 0.0
        )
        
        return {
            "service": "communication_hub_service",
            "metrics": self.metrics,
            "derived": {
                "cache_hit_rate": cache_hit_rate,
                "average_effectiveness_score": self.metrics["average_effectiveness_score"],
                "tone_adjustment_rate": (
                    self.metrics["tone_adjustments"] / max(self.metrics["total_communications_generated"], 1)
                ),
                "database_success_rate": (
                    (self.metrics["database_saves"] / 
                     max(self.metrics["database_saves"] + self.metrics["database_failures"], 1)) * 100
                )
            },
            "communication_type_breakdown": {
                ct: count for ct, count in self.metrics["communications_by_type"].items()
            },
            "channel_breakdown": {
                ch: count for ch, count in self.metrics["communications_by_channel"].items()
            },
            "priority_breakdown": {
                pr: count for pr, count in self.metrics["communications_by_priority"].items()
            },
            "language_breakdown": {
                lang: count for lang, count in self.metrics["language_requests"].items()
            },
            "supported_languages": self.supported_languages
        }
    
    # ========================================================================
    # PRIVATE METHODS
    # ========================================================================
    
    def _generate_cache_key(self, request: CommunicationRequest) -> str:
        """Generate cache key for communication request."""
        key_data = {
            "parent_id": request.parent_id,
            "student_id": request.student_id,
            "communication_type": request.communication_type.value,
            "child_mood": request.child_mood.value if request.child_mood else None,
            "context": request.context,
            "language": request.language,
            "priority": request.priority.value
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    async def _get_communication_context(
        self, 
        request: CommunicationRequest
    ) -> Dict[str, Any]:
        """Get communication context and history."""
        try:
            context = {
                "student_id": request.student_id,
                "parent_id": request.parent_id,
                "current_mood": request.child_mood.value if request.child_mood else None,
                "recent_performance": request.recent_performance,
                "additional_context": request.context or {}
            }
            
            if request.include_history:
                # Get recent communication history
                history = await self._get_communication_history(
                    request.parent_id, request.student_id, 7  # Last week
                )
                context["recent_communications"] = history
                
                # Get recent engagement metrics
                engagement_query = self.db.collection(self.engagement_metrics_collection)\
                    .where("student_id", "==", request.student_id)\
                    .where("date", ">=", datetime.utcnow() - timedelta(days=7))\
                    .order_by("date", direction="DESCENDING")\
                    .limit(10)
                
                engagement_metrics = []
                async for doc in engagement_query.stream():
                    engagement_metrics.append(doc.to_dict())
                
                context["recent_engagement"] = engagement_metrics
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to get communication context: {e}")
            return {
                "student_id": request.student_id,
                "parent_id": request.parent_id,
                "error": str(e)
            }
    
    async def _get_communication_history(
        self,
        parent_id: str,
        student_id: str,
        days: int
    ) -> List[Dict[str, Any]]:
        """Get communication history."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            query = self.db.collection(self.communications_collection)\
                .where("parent_id", "==", parent_id)\
                .where("student_id", "==", student_id)\
                .where("created_at", ">=", start_date)\
                .where("created_at", "<=", end_date)\
                .order_by("created_at", direction="DESCENDING")
            
            history = []
            async for doc in query.stream():
                history.append(doc.to_dict())
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get communication history: {e}")
            return []
    
    def _determine_optimal_tone(
        self,
        communication_type: CommunicationType,
        child_mood: Optional[Mood],
        communication_data: Dict[str, Any]
    ) -> Tone:
        """Determine optimal tone based on context."""
        # Base tone by communication type
        tone_by_type = {
            CommunicationType.ENCOURAGEMENT: Tone.MOTIVATIONAL,
            CommunicationType.ALERT: Tone.CONCERNED,
            CommunicationType.CELEBRATORY: Tone.CELEBRATORY,
            CommunicationType.REMINDER: Tone.SUPPORTIVE,
            CommunicationType.INSIGHT: Tone.NEUTRAL,
            CommunicationType.REPORT: Tone.NEUTRAL,
            CommunicationType.MESSAGE: Tone.SUPPORTIVE
        }
        
        base_tone = tone_by_type.get(communication_type, Tone.NEUTRAL)
        
        # Adjust based on mood
        if child_mood:
            if child_mood in [Mood.STRESSED, Mood.FRUSTRATED]:
                return Tone.SUPPORTIVE
            elif child_mood in [Mood.DISCOURAGED, Mood.TIRED]:
                return Tone.MOTIVATIONAL
            elif child_mood == Mood.HAPPY:
                return Tone.CELEBRATORY
            elif child_mood == Mood.MOTIVATED:
                return Tone.SUPPORTIVE
        
        return base_tone
    
    async def _adjust_tone(
        self,
        communication_data: Dict[str, Any],
        target_tone: Tone,
        child_mood: Optional[Mood]
    ) -> Dict[str, Any]:
        """Adjust communication content for target tone."""
        try:
            # Build prompt for tone adjustment
            prompt = f"""
Adjust the tone of this communication to be more {target_tone.value}.

Original Content:
Subject: {communication_data.get('subject', '')}
Content: {communication_data.get('content', '')}

Target Tone: {target_tone.value}
Child Mood: {child_mood.value if child_mood else 'neutral'}

Requirements:
1. Maintain the core message and intent
2. Adjust language and phrasing for target tone
3. Consider the child's current mood
4. Keep the communication age-appropriate
5. Preserve any important details or instructions

Format as JSON:
{
    "subject": "Adjusted subject",
    "content": "Adjusted content with target tone",
    "tone_adjustments_made": ["adjustment1", "adjustment2"]
}
"""
            
            # Generate content using AI service
            content_request = ContentRequest(
                content_type=ContentType.CONTENT_GENERATION,
                prompt=prompt,
                user_id="system",
                student_id="system",
                context={
                    "target_tone": target_tone.value,
                    "child_mood": child_mood.value if child_mood else None
                },
                metadata={"generation_type": "tone_adjustment"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse adjusted content
            try:
                import json
                adjusted_data = json.loads(result.content)
                
                # Merge with original data
                communication_data["subject"] = adjusted_data.get("subject", communication_data.get("subject"))
                communication_data["content"] = adjusted_data.get("content", communication_data.get("content"))
                communication_data["tone_adjustments"] = adjusted_data.get("tone_adjustments", [])
                
            except json.JSONDecodeError:
                # Fallback: use original content
                communication_data["tone_adjustments"] = ["Failed to adjust tone"]
            
            communication_data["tone"] = target_tone
            return communication_data
            
        except Exception as e:
            logger.error(f"Failed to adjust tone: {e}")
            communication_data["tone_adjustments"] = ["Error adjusting tone"]
            return communication_data
    
    def _recommend_channel(
        self,
        communication_type: CommunicationType,
        priority: Priority
    ) -> Channel:
        """Recommend optimal channel for communication."""
        # Channel recommendations by type and priority
        if priority == Priority.CRITICAL:
            return Channel.SMS
        
        if communication_type in [CommunicationType.ALERT, CommunicationType.REMINDER]:
            if priority in [Priority.HIGH, Priority.CRITICAL]:
                return Channel.SMS
            else:
                return Channel.PUSH
        
        if communication_type in [CommunicationType.REPORT, CommunicationType.INSIGHT]:
            return Channel.EMAIL
        
        # Default for messages and encouragement
        return Channel.IN_APP
    
    def _calculate_effectiveness_score(
        self,
        communication_data: Dict[str, Any],
        context_data: Dict[str, Any],
        request: CommunicationRequest
    ) -> float:
        """Calculate effectiveness score for communication."""
        try:
            score = 0.5  # Base score
            
            # Channel appropriateness
            recommended_channel = self._recommend_channel(
                request.communication_type, request.priority
            )
            if request.channel == recommended_channel:
                score += 0.1
            
            # Tone appropriateness
            optimal_tone = self._determine_optimal_tone(
                request.communication_type, request.child_mood, communication_data
            )
            if communication_data.get("tone") == optimal_tone:
                score += 0.1
            
            # Context relevance
            if request.context and communication_data.get("context_relevance", False):
                score += 0.1
            
            # Personalization
            if communication_data.get("personalization_level", 0) > 0.5:
                score += 0.1
            
            # Timing appropriateness
            if communication_data.get("timing_appropriate", False):
                score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Failed to calculate effectiveness score: {e}")
            return 0.5
    
    async def _save_communication_to_db(
        self, 
        result: CommunicationResult, 
        request: CommunicationRequest
    ):
        """Save communication result to database."""
        try:
            communication_record = CommunicationRecord(
                communication_id=result.communication_id,
                parent_id=request.parent_id,
                student_id=request.student_id,
                communication_type=result.communication_type.value,
                channel=result.channel.value,
                direction="sent",
                subject=result.subject,
                content=result.content,
                priority=result.priority.value,
                status="sent",
                sent_at=result.created_at,
                delivered_at=None,
                read_at=None,
                metadata={
                    "tone": result.tone.value,
                    "effectiveness_score": result.effectiveness_score,
                    "suggested_timing": result.suggested_timing.isoformat() if result.suggested_timing else None,
                    "follow_up_actions": result.follow_up_actions,
                    "generation_time_ms": result.generation_time_ms,
                    "language": request.language,
                    "child_mood": request.child_mood.value if request.child_mood else None
                }
            )
            
            doc_ref = self.db.collection(self.communications_collection).document(result.communication_id)
            await doc_ref.set(communication_record.model_dump())
            
            self.metrics["database_saves"] += 1
            logger.debug(f"Saved communication to database: {result.communication_id}")
            
        except Exception as e:
            logger.error(f"Failed to save communication to database: {e}")
            self.metrics["database_failures"] += 1
    
    async def _save_reminder_to_db(self, reminder: Dict[str, Any]):
        """Save follow-up reminder to database."""
        try:
            doc_ref = self.db.collection("follow_up_reminders").document(reminder["reminder_id"])
            await doc_ref.set(reminder)
            logger.debug(f"Saved reminder to database: {reminder['reminder_id']}")
            
        except Exception as e:
            logger.error(f"Failed to save reminder to database: {e}")
    
    def _update_average_effectiveness(self, new_score: float):
        """Update running average effectiveness score."""
        total_communications = self.metrics["total_communications_generated"]
        if total_communications > 0:
            current_avg = self.metrics["average_effectiveness_score"]
            self.metrics["average_effectiveness_score"] = (
                (current_avg * (total_communications - 1) + new_score) / total_communications
            )
    
    def _build_conversation_starter_prompt(
        self,
        context_data: Dict[str, Any],
        mood_context: Optional[Mood],
        recent_performance: Optional[Dict[str, Any]],
        conversation_goal: Optional[str],
        language: str
    ) -> str:
        """Build prompt for conversation starter generation."""
        return f"""
Generate 5 thoughtful conversation starters in {language}.

Context:
{json.dumps(context_data, indent=2)}
Child Mood: {mood_context.value if mood_context else 'neutral'}
Recent Performance: {json.dumps(recent_performance or {}, indent=2)}
Conversation Goal: {conversation_goal or 'general check-in'}

Requirements:
1. Each starter should be open-ended and engaging
2. Consider the child's current mood and performance
3. Align with the conversation goal if specified
4. Use age-appropriate language
5. Include cultural considerations if relevant
6. Make them natural and conversational

Format as JSON array:
[
    "conversation starter 1 in {language}",
    "conversation starter 2 in {language}",
    ...
]
"""
    
    def _parse_conversation_starters(self, content: str, language: str) -> List[str]:
        """Parse conversation starters from AI response."""
        try:
            # Try to parse as JSON
            import json
            starters = json.loads(content)
            
            if isinstance(starters, list):
                return [str(starter) for starter in starters]
            else:
                # Fallback: return as single starter
                return [str(content)]
                
        except json.JSONDecodeError:
            # Fallback: split by newlines and clean up
            lines = content.strip().split('\n')
            starters = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('[') and not line.startswith(']') and not line.startswith('{'):
                    # Remove numbering and quotes
                    cleaned = line.replace('"', '').replace("'", "")
                    # Remove numbering at start
                    if cleaned and (cleaned[0].isdigit() or cleaned.startswith('-') or cleaned.startswith('*')):
                        cleaned = ' '.join(cleaned.split(' ')[1:]).strip()
                    
                    if cleaned and len(cleaned) > 10:
                        starters.append(cleaned)
            
            return starters[:5]  # Return max 5 starters
    
    def _analyze_effectiveness_patterns(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze effectiveness patterns in communication history."""
        try:
            if not history:
                return {"analysis": "No history available"}
            
            # Group by communication type
            type_effectiveness = {}
            channel_effectiveness = {}
            tone_effectiveness = {}
            
            for comm in history:
                comm_type = comm.get("communication_type", "unknown")
                channel = comm.get("channel", "unknown")
                tone = comm.get("metadata", {}).get("tone", "neutral")
                effectiveness = comm.get("metadata", {}).get("effectiveness_score", 0.5)
                
                # Track by type
                if comm_type not in type_effectiveness:
                    type_effectiveness[comm_type] = []
                type_effectiveness[comm_type].append(effectiveness)
                
                # Track by channel
                if channel not in channel_effectiveness:
                    channel_effectiveness[channel] = []
                channel_effectiveness[channel].append(effectiveness)
                
                # Track by tone
                if tone not in tone_effectiveness:
                    tone_effectiveness[tone] = []
                tone_effectiveness[tone].append(effectiveness)
            
            # Calculate averages
            def safe_average(values):
                return sum(values) / len(values) if values else 0.0
            
            return {
                "by_type": {t: safe_average(v) for t, v in type_effectiveness.items()},
                "by_channel": {c: safe_average(v) for c, v in channel_effectiveness.items()},
                "by_tone": {t: safe_average(v) for t, v in tone_effectiveness.items()},
                "overall_average": safe_average([c.get("metadata", {}).get("effectiveness_score", 0.5) for c in history]),
                "total_communications": len(history)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze effectiveness patterns: {e}")
            return {"analysis": "Failed to analyze", "error": str(e)}
    
    async def _generate_effectiveness_insights(
        self,
        history: List[Dict[str, Any]],
        effectiveness_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate insights from effectiveness analysis."""
        try:
            # Build prompt for insights generation
            prompt = f"""
Analyze communication effectiveness data and generate insights.

Effectiveness Analysis:
{json.dumps(effectiveness_analysis, indent=2)}

Recent History Summary:
- Total communications: {len(history)}
- Date range: {history[0].get('created_at') if history else 'N/A'} to {history[-1].get('created_at') if history else 'N/A'}

Requirements:
1. Identify patterns in effective vs ineffective communications
2. Highlight best practices and areas for improvement
3. Consider timing, channel, and tone effectiveness
4. Generate actionable insights for parent
5. Focus on practical, implementable suggestions

Format as JSON array of strings:
[
    "insight 1",
    "insight 2",
    ...
]
"""
            
            # Generate content using AI service
            content_request = ContentRequest(
                content_type=ContentType.INSIGHT,
                prompt=prompt,
                user_id="system",
                student_id="system",
                context={"effectiveness_analysis": effectiveness_analysis},
                metadata={"generation_type": "effectiveness_insights"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse insights
            try:
                import json
                insights = json.loads(result.content)
                
                if isinstance(insights, list):
                    return [str(insight) for insight in insights]
                else:
                    return [str(result.content)]
                    
            except json.JSONDecodeError:
                return [str(result.content)]
                
        except Exception as e:
            logger.error(f"Failed to generate effectiveness insights: {e}")
            return ["Unable to generate insights at this time"]
    
    async def _generate_effectiveness_recommendations(
        self,
        effectiveness_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on effectiveness analysis."""
        try:
            # Build prompt for recommendations
            prompt = f"""
Generate communication improvement recommendations based on effectiveness analysis.

Effectiveness Analysis:
{json.dumps(effectiveness_analysis, indent=2)}

Requirements:
1. Identify specific areas for improvement
2. Suggest concrete, actionable changes
3. Focus on timing, channel, tone, and content
4. Prioritize recommendations by impact
5. Provide implementation guidance

Format as JSON array of strings:
[
    "recommendation 1",
    "recommendation 2",
    ...
]
"""
            
            # Generate content using AI service
            content_request = ContentRequest(
                content_type=ContentType.RECOMMENDATION,
                prompt=prompt,
                user_id="system",
                student_id="system",
                context={"effectiveness_analysis": effectiveness_analysis},
                metadata={"generation_type": "effectiveness_recommendations"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse recommendations
            try:
                import json
                recommendations = json.loads(result.content)
                
                if isinstance(recommendations, list):
                    return [str(rec) for rec in recommendations]
                else:
                    return [str(result.content)]
                    
            except json.JSONDecodeError:
                return [str(result.content)]
                
        except Exception as e:
            logger.error(f"Failed to generate effectiveness recommendations: {e}")
            return ["Continue monitoring communication patterns"]
    
    def _determine_follow_up_timing(self, action: str) -> datetime:
        """Determine optimal timing for follow-up action."""
        # Base timing by action type
        action_lower = action.lower()
        
        if "urgent" in action_lower or "immediate" in action_lower:
            return datetime.utcnow() + timedelta(hours=2)
        elif "check" in action_lower or "follow" in action_lower:
            return datetime.utcnow() + timedelta(days=1)
        elif "review" in action_lower or "assess" in action_lower:
            return datetime.utcnow() + timedelta(days=3)
        elif "celebrate" in action_lower or "acknowledge" in action_lower:
            return datetime.utcnow() + timedelta(hours=6)
        else:
            # Default timing
            return datetime.utcnow() + timedelta(days=2)

# Initialize communication generators
def _init_communication_generators(service: 'CommunicationHubService'):
    """Initialize communication generators for different types."""
    return {
        CommunicationType.NOTIFICATION: service._generate_notification,
        CommunicationType.ALERT: service._generate_alert,
        CommunicationType.INSIGHT: service._generate_insight,
        CommunicationType.REPORT: service._generate_report,
        CommunicationType.MESSAGE: service._generate_message,
        CommunicationType.REMINDER: service._generate_reminder,
        CommunicationType.ENCOURAGEMENT: service._generate_encouragement
    }

# Add communication generators to CommunicationHubService class
CommunicationHubService.communication_generators = None

def get_communication_hub_service(
    unified_config: Optional[GeminiConfig] = None,
    **kwargs
) -> CommunicationHubService:
    """
    Get Communication Hub service instance.
    
    Args:
        unified_config: Optional unified configuration
        **kwargs: Additional arguments for service initialization
    
    Returns:
        CommunicationHubService instance
    """
    service = CommunicationHubService(unified_config=unified_config, **kwargs)
    
    # Initialize communication generators after service creation
    service.communication_generators = _init_communication_generators(service)
    
    return service

# Module initialization
logger.info("Communication Hub Service module loaded")