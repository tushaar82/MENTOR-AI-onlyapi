"""
Parent AI Insights Service

This service provides AI-powered insights and recommendations for parents
using Gemini Flash for intelligent analysis and personalized suggestions.

Features:
- Predictive analytics for early warnings
- Personalized parenting recommendations
- Conversation starter suggestions
- Parent-child activity suggestions
- Mood-based communication strategies
- Performance trend analysis
- Risk factor identification
- Intervention recommendations

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
from models.database_models import ParentInsight, EngagementMetric, InterventionAlert

# Configure logging
logger = logging.getLogger(__name__)

# Insight types for categorization
class InsightType(Enum):
    """Types of parent insights."""
    PERFORMANCE = "performance"
    ENGAGEMENT = "engagement"
    WEAK_AREAS = "weak_areas"
    PROGRESS = "progress"
    RECOMMENDATION = "recommendation"
    WARNING = "warning"
    OPPORTUNITY = "opportunity"
    MILESTONE = "milestone"

class InsightSeverity(Enum):
    """Severity levels for insights."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class InsightRequest:
    """Request for insight generation."""
    
    parent_id: str
    student_id: str
    insight_type: InsightType
    context: Optional[Dict[str, Any]] = None
    time_period_days: int = 30
    include_recommendations: bool = True
    severity_threshold: InsightSeverity = InsightSeverity.MEDIUM
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class InsightResult:
    """Result from insight generation."""
    
    insight_id: str
    insight_type: InsightType
    title: str
    description: str
    severity: InsightSeverity
    data: Dict[str, Any]
    recommendations: List[str]
    action_required: bool
    confidence_score: float
    generation_time_ms: int
    created_at: datetime

class ParentAIInsightsService:
    """
    Service for generating AI-powered insights for parents.
    
    This service leverages Gemini Flash to analyze student data and generate
    personalized insights, recommendations, and early warnings for parents.
    
    Attributes:
        unified_service: Unified Gemini configuration service
        ai_content_service: AI content generation service
        db: Firestore database client
        insight_generators: Handlers for different insight types
        cache: In-memory cache for insights
        analytics_data: Student performance and engagement data
    
    Example:
        >>> service = ParentAIInsightsService()
        >>> result = service.generate_insight(
        ...     parent_id="parent123",
        ...     student_id="student123",
        ...     insight_type=InsightType.PERFORMANCE
        ... )
        >>> print(f"Generated insight: {result.title}")
    """
    
    def __init__(
        self,
        db: Optional[firestore.Client] = None,
        unified_config: Optional[GeminiConfig] = None,
        enable_database_persistence: bool = True,
        cache_size: int = 200,
        cache_ttl_hours: int = 12
    ):
        """
        Initialize Parent AI Insights Service.
        
        Args:
            db: Firestore client (creates new if None)
            unified_config: Optional unified configuration
            enable_database_persistence: Enable saving to database
            cache_size: Maximum cache size
            cache_ttl_hours: Cache TTL in hours
        """
        logger.info("Initializing ParentAIInsightsService")
        
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
        
        # Insight cache
        self.insight_cache: Dict[str, InsightResult] = {}
        
        # Collections
        self.insights_collection = "parent_insights"
        self.engagement_metrics_collection = "engagement_metrics"
        self.intervention_alerts_collection = "intervention_alerts"
        
        # Metrics
        self.metrics = {
            "total_insights_generated": 0,
            "insights_by_type": {it.value: 0 for it in InsightType},
            "insights_by_severity": {isv.value: 0 for isv in InsightSeverity},
            "average_generation_time_ms": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
            "database_saves": 0,
            "database_failures": 0
        }
        
        logger.info(
            f"ParentAIInsightsService initialized (db_persistence={enable_database_persistence}, "
            f"cache_size={cache_size}, cache_ttl={cache_ttl_hours}h)"
        )
    
    async def generate_insight(
        self,
        request: InsightRequest
    ) -> InsightResult:
        """
        Generate AI-powered insight for parent.
        
        Args:
            request: InsightRequest with all generation parameters
        
        Returns:
            InsightResult with generated insight and metadata
        
        Raises:
            ValueError: If request is invalid
            Exception: If generation fails
        """
        start_time = time.time()
        
        # Generate insight ID
        insight_id = f"insight_{request.parent_id}_{request.student_id}_{int(time.time())}_{hashlib.md5(f'{request.insight_type.value}_{request.time_period_days}'.encode()).hexdigest()[:8]}"
        
        logger.info(
            f"Generating {request.insight_type.value} insight: {insight_id}"
        )
        
        try:
            # Check cache
            cache_key = self._generate_cache_key(request)
            if cache_key in self.insight_cache:
                cached_result = self.insight_cache[cache_key]
                logger.info(f"Cache hit for insight: {insight_id}")
                
                # Update metrics
                self.metrics["cache_hits"] += 1
                
                return cached_result
            
            self.metrics["cache_misses"] += 1
            
            # Get student data for analysis
            student_data = await self._get_student_data(
                request.student_id, 
                request.time_period_days
            )
            
            # Route to appropriate generator
            generator = self.insight_generators.get(request.insight_type)
            if not generator:
                raise ValueError(f"No generator for insight type: {request.insight_type.value}")
            
            # Generate insight
            insight_data, generation_metadata = await generator(request, student_data)
            
            # Calculate metrics
            generation_time_ms = int((time.time() - start_time) * 1000)
            
            # Create result
            result = InsightResult(
                insight_id=insight_id,
                insight_type=request.insight_type,
                title=insight_data.get("title", "New Insight"),
                description=insight_data.get("description", ""),
                severity=InsightSeverity(insight_data.get("severity", "medium")),
                data=insight_data.get("data", {}),
                recommendations=insight_data.get("recommendations", []),
                action_required=insight_data.get("action_required", False),
                confidence_score=insight_data.get("confidence_score", 0.7),
                generation_time_ms=generation_time_ms,
                created_at=datetime.utcnow()
            )
            
            # Cache result
            if len(self.insight_cache) < self.cache_size:
                self.insight_cache[cache_key] = result
            
            # Save to database
            if self.enable_database_persistence:
                await self._save_insight_to_db(result, request)
            
            # Update metrics
            self.metrics["total_insights_generated"] += 1
            self.metrics["insights_by_type"][request.insight_type.value] += 1
            self.metrics["insights_by_severity"][result.severity.value] += 1
            self._update_average_generation_time(generation_time_ms)
            
            logger.info(
                f"Generated {request.insight_type.value} insight: {insight_id}, "
                f"severity={result.severity.value}, confidence={result.confidence_score:.2f}, "
                f"time={generation_time_ms}ms"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            
            # Update metrics
            if self.enable_database_persistence:
                self.metrics["database_failures"] += 1
            
            raise
    
    async def generate_conversation_starters(
        self,
        parent_id: str,
        student_id: str,
        mood_context: Optional[str] = None,
        recent_performance: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Generate AI-powered conversation starters for parents.
        
        Args:
            parent_id: Parent ID
            student_id: Student ID
            mood_context: Optional mood context (stressed, happy, frustrated, etc.)
            recent_performance: Optional recent performance data
        
        Returns:
            List of conversation starter suggestions
        """
        try:
            # Get student context
            student_data = await self._get_student_data(student_id, 7)  # Last week
            
            # Build prompt for conversation starters
            prompt = self._build_conversation_starter_prompt(
                student_data, mood_context, recent_performance
            )
            
            # Generate content using AI service
            content_request = ContentRequest(
                content_type=ContentType.RECOMMENDATION,
                prompt=prompt,
                user_id=parent_id,
                student_id=student_id,
                context={
                    "mood_context": mood_context,
                    "recent_performance": recent_performance,
                    "student_data": student_data
                },
                metadata={"generation_type": "conversation_starters"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse conversation starters from response
            conversation_starters = self._parse_conversation_starters(result.content)
            
            logger.info(f"Generated {len(conversation_starters)} conversation starters")
            return conversation_starters
            
        except Exception as e:
            logger.error(f"Failed to generate conversation starters: {e}")
            raise
    
    async def generate_activity_suggestions(
        self,
        parent_id: str,
        student_id: str,
        activity_type: str = "educational",
        time_available_minutes: int = 30,
        subject_focus: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate parent-child activity suggestions.
        
        Args:
            parent_id: Parent ID
            student_id: Student ID
            activity_type: Type of activity (educational, recreational, bonding)
            time_available_minutes: Time available in minutes
            subject_focus: Optional subject to focus on
        
        Returns:
            List of activity suggestions with details
        """
        try:
            # Get student context
            student_data = await self._get_student_data(student_id, 14)  # Last 2 weeks
            
            # Build prompt for activity suggestions
            prompt = self._build_activity_suggestion_prompt(
                student_data, activity_type, time_available_minutes, subject_focus
            )
            
            # Generate content using AI service
            content_request = ContentRequest(
                content_type=ContentType.RECOMMENDATION,
                prompt=prompt,
                user_id=parent_id,
                student_id=student_id,
                context={
                    "activity_type": activity_type,
                    "time_available_minutes": time_available_minutes,
                    "subject_focus": subject_focus,
                    "student_data": student_data
                },
                metadata={"generation_type": "activity_suggestions"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse activity suggestions from response
            activity_suggestions = self._parse_activity_suggestions(result.content)
            
            logger.info(f"Generated {len(activity_suggestions)} activity suggestions")
            return activity_suggestions
            
        except Exception as e:
            logger.error(f"Failed to generate activity suggestions: {e}")
            raise
    
    async def get_insights(
        self,
        parent_id: str,
        student_id: Optional[str] = None,
        insight_type: Optional[InsightType] = None,
        severity: Optional[InsightSeverity] = None,
        limit: int = 50,
        start_after: Optional[str] = None
    ) -> List[ParentInsight]:
        """
        Retrieve insights from database.
        
        Args:
            parent_id: Parent ID
            student_id: Optional student ID filter
            insight_type: Optional insight type filter
            severity: Optional severity filter
            limit: Maximum number of results
            start_after: Pagination cursor
        
        Returns:
            List of ParentInsight records
        """
        try:
            query = self.db.collection(self.insights_collection)\
                .where("parent_id", "==", parent_id)\
                .order_by("created_at", direction="DESCENDING")\
                .limit(limit)
            
            if student_id:
                query = query.where("student_id", "==", student_id)
            
            if insight_type:
                query = query.where("insight_type", "==", insight_type.value)
            
            if severity:
                query = query.where("severity", "==", severity.value)
            
            if start_after:
                # Get the start document
                start_doc = await self.db.collection(self.insights_collection).document(start_after).get()
                if start_doc.exists:
                    query = query.start_after(start_doc)
            
            results = []
            async for doc in query.stream():
                insight_data = doc.to_dict()
                results.append(ParentInsight(**insight_data))
            
            logger.info(f"Retrieved {len(results)} insights for parent {parent_id}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to get insights: {e}")
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
            "service": "parent_ai_insights_service",
            "metrics": self.metrics,
            "derived": {
                "cache_hit_rate": cache_hit_rate,
                "average_generation_time_ms": self.metrics["average_generation_time_ms"],
                "database_success_rate": (
                    (self.metrics["database_saves"] / 
                     max(self.metrics["database_saves"] + self.metrics["database_failures"], 1)) * 100
                )
            },
            "insight_type_breakdown": {
                it: count for it, count in self.metrics["insights_by_type"].items()
            },
            "severity_breakdown": {
                isv: count for isv, count in self.metrics["insights_by_severity"].items()
            }
        }
    
    # ========================================================================
    # PRIVATE METHODS
    # ========================================================================
    
    def _generate_cache_key(self, request: InsightRequest) -> str:
        """Generate cache key for insight request."""
        key_data = {
            "parent_id": request.parent_id,
            "student_id": request.student_id,
            "insight_type": request.insight_type.value,
            "time_period_days": request.time_period_days,
            "context": request.context
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    async def _get_student_data(
        self, 
        student_id: str, 
        days: int
    ) -> Dict[str, Any]:
        """Get student performance and engagement data."""
        try:
            # Get engagement metrics
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            metrics_query = self.db.collection(self.engagement_metrics_collection)\
                .where("student_id", "==", student_id)\
                .where("date", ">=", start_date)\
                .where("date", "<=", end_date)\
                .order_by("date", direction="DESCENDING")
            
            metrics = []
            async for doc in metrics_query.stream():
                metrics.append(doc.to_dict())
            
            # Get intervention alerts
            alerts_query = self.db.collection(self.intervention_alerts_collection)\
                .where("student_id", "==", student_id)\
                .where("created_at", ">=", start_date)\
                .order_by("created_at", direction="DESCENDING")
            
            alerts = []
            async for doc in alerts_query.stream():
                alerts.append(doc.to_dict())
            
            return {
                "student_id": student_id,
                "period_days": days,
                "engagement_metrics": metrics,
                "intervention_alerts": alerts,
                "data_points": len(metrics)
            }
            
        except Exception as e:
            logger.error(f"Failed to get student data: {e}")
            return {
                "student_id": student_id,
                "period_days": days,
                "engagement_metrics": [],
                "intervention_alerts": [],
                "data_points": 0,
                "error": str(e)
            }
    
    async def _save_insight_to_db(self, result: InsightResult, request: InsightRequest):
        """Save insight result to database."""
        try:
            insight_record = ParentInsight(
                insight_id=result.insight_id,
                parent_id=request.parent_id,
                student_id=request.student_id,
                insight_type=result.insight_type.value,
                title=result.title,
                description=result.description,
                severity=result.severity.value,
                data=result.data,
                action_required=result.action_required,
                action_taken=None,
                status="new",
                created_at=result.created_at,
                resolved_at=None,
                metadata={
                    "confidence_score": result.confidence_score,
                    "generation_time_ms": result.generation_time_ms,
                    "request_context": request.context,
                    "recommendations": result.recommendations
                }
            )
            
            doc_ref = self.db.collection(self.insights_collection).document(result.insight_id)
            await doc_ref.set(insight_record.model_dump())
            
            self.metrics["database_saves"] += 1
            logger.debug(f"Saved insight to database: {result.insight_id}")
            
        except Exception as e:
            logger.error(f"Failed to save insight to database: {e}")
            self.metrics["database_failures"] += 1
    
    def _update_average_generation_time(self, new_time_ms: int):
        """Update running average generation time."""
        total_insights = self.metrics["total_insights_generated"]
        if total_insights > 0:
            current_avg = self.metrics["average_generation_time_ms"]
            self.metrics["average_generation_time_ms"] = (
                (current_avg * (total_insights - 1) + new_time_ms) / total_insights
            )
    
    def _build_conversation_starter_prompt(
        self,
        student_data: Dict[str, Any],
        mood_context: Optional[str],
        recent_performance: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for conversation starter generation."""
        prompt = f"""
Generate 5 thoughtful conversation starters for a parent to discuss with their child.

Context:
- Student data: {json.dumps(student_data, indent=2)}
- Mood context: {mood_context or 'neutral'}
- Recent performance: {json.dumps(recent_performance or {}, indent=2)}

Requirements:
1. Each starter should be open-ended and encouraging
2. Consider the child's current mood and performance
3. Focus on positive reinforcement and support
4. Avoid academic pressure if mood is stressed
5. Include a mix of academic and personal topics
6. Make them age-appropriate and engaging

Format as a JSON array of strings:
[
    "conversation starter 1",
    "conversation starter 2",
    ...
]
"""
        return prompt
    
    def _build_activity_suggestion_prompt(
        self,
        student_data: Dict[str, Any],
        activity_type: str,
        time_available_minutes: int,
        subject_focus: Optional[str]
    ) -> str:
        """Build prompt for activity suggestion generation."""
        prompt = f"""
Generate 5 engaging parent-child activity suggestions.

Context:
- Student data: {json.dumps(student_data, indent=2)}
- Activity type: {activity_type}
- Time available: {time_available_minutes} minutes
- Subject focus: {subject_focus or 'general'}

Requirements:
1. Activities must fit within the time constraint
2. Align with the specified activity type
3. Consider the student's current interests and performance
4. Include learning objectives if educational
5. Provide clear instructions for parents
6. Suggest materials needed (if any)

Format as JSON array with structure:
[
    {{
        "title": "Activity Title",
        "description": "Detailed description",
        "duration_minutes": 30,
        "materials": ["item1", "item2"],
        "learning_objectives": ["objective1", "objective2"],
        "instructions": "Step-by-step instructions"
    }},
    ...
]
"""
        return prompt
    
    def _parse_conversation_starters(self, content: str) -> List[str]:
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
                if line and not line.startswith('[') and not line.startswith(']'):
                    # Remove numbering and quotes
                    cleaned = line.replace('"', '').replace("'", "")
                    if cleaned.endswith('.'):
                        cleaned = cleaned[:-1]
                    if cleaned and len(cleaned) > 10:
                        starters.append(cleaned)
            
            return starters[:5]  # Return max 5 starters
    
    def _parse_activity_suggestions(self, content: str) -> List[Dict[str, Any]]:
        """Parse activity suggestions from AI response."""
        try:
            # Try to parse as JSON
            import json
            suggestions = json.loads(content)
            
            if isinstance(suggestions, list):
                return suggestions
            elif isinstance(suggestions, dict) and "activities" in suggestions:
                return suggestions["activities"]
            else:
                # Fallback: return as single activity
                return [{
                    "title": "Suggested Activity",
                    "description": content,
                    "duration_minutes": 30,
                    "materials": [],
                    "learning_objectives": [],
                    "instructions": content
                }]
                
        except json.JSONDecodeError:
            # Fallback: return basic activity
            return [{
                "title": "Parent-Child Activity",
                "description": content,
                "duration_minutes": 30,
                "materials": [],
                "learning_objectives": [],
                "instructions": content
            }]
    # ========================================================================
    # INSIGHT GENERATOR METHODS
    # ========================================================================
    
    async def _generate_performance_insight(
        self, 
        request: InsightRequest, 
        student_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate performance-based insight."""
        try:
            # Build prompt for performance analysis
            prompt = f"""
Analyze student performance data and generate insights.

Student Data:
{json.dumps(student_data, indent=2)}

Requirements:
1. Analyze performance trends over the last {request.time_period_days} days
2. Identify patterns and anomalies
3. Compare against expected progress
4. Generate actionable insights
5. Provide confidence score (0-1)

Format as JSON:
{{
    "title": "Performance Analysis Insight",
    "description": "Detailed analysis of student performance",
    "severity": "low|medium|high|critical",
    "data": {{
        "trend": "improving|declining|stable",
        "key_metrics": {{"metric": value}},
        "comparisons": {{"period1": value, "period2": value}}
    }},
    "recommendations": ["recommendation1", "recommendation2"],
    "action_required": true/false,
    "confidence_score": 0.8
}}
"""
            
            # Generate content using AI service
            content_request = ContentRequest(
                content_type=ContentType.ANALYSIS,
                prompt=prompt,
                user_id=request.parent_id,
                student_id=request.student_id,
                context={"student_data": student_data, "time_period_days": request.time_period_days},
                metadata={"insight_type": "performance"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse response
            try:
                insight_data = json.loads(result.content)
            except json.JSONDecodeError:
                # Fallback insight
                insight_data = {
                    "title": "Performance Analysis",
                    "description": "Analysis of recent performance trends",
                    "severity": "medium",
                    "data": {"trend": "stable", "analysis": result.content},
                    "recommendations": ["Continue monitoring progress"],
                    "action_required": False,
                    "confidence_score": 0.6
                }
            
            generation_metadata = {
                "tokens_used": result.tokens_used,
                "cost": result.cost,
                "generation_time_ms": result.generation_time_ms
            }
            
            return insight_data, generation_metadata
            
        except Exception as e:
            logger.error(f"Failed to generate performance insight: {e}")
            # Return fallback insight
            return {
                "title": "Performance Analysis",
                "description": f"Unable to generate detailed performance analysis: {str(e)}",
                "severity": "low",
                "data": {"error": str(e)},
                "recommendations": ["Try again later or contact support"],
                "action_required": False,
                "confidence_score": 0.3
            }, {"error": str(e)}
    
    async def _generate_engagement_insight(
        self, 
        request: InsightRequest, 
        student_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate engagement-based insight."""
        try:
            # Build prompt for engagement analysis
            prompt = f"""
Analyze student engagement data and generate insights.

Student Data:
{json.dumps(student_data, indent=2)}

Requirements:
1. Analyze study patterns and engagement levels
2. Identify engagement trends and potential issues
3. Assess consistency and motivation
4. Generate actionable insights for parents
5. Provide confidence score (0-1)

Format as JSON:
{{
    "title": "Engagement Analysis Insight",
    "description": "Analysis of student engagement and study patterns",
    "severity": "low|medium|high|critical",
    "data": {{
        "engagement_level": "high|medium|low",
        "study_consistency": "consistent|inconsistent",
        "key_patterns": ["pattern1", "pattern2"],
        "risk_factors": ["factor1", "factor2"]
    }},
    "recommendations": ["recommendation1", "recommendation2"],
    "action_required": true/false,
    "confidence_score": 0.8
}}
"""
            
            # Generate content using AI service
            content_request = ContentRequest(
                content_type=ContentType.ANALYSIS,
                prompt=prompt,
                user_id=request.parent_id,
                student_id=request.student_id,
                context={"student_data": student_data, "time_period_days": request.time_period_days},
                metadata={"insight_type": "engagement"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse response
            try:
                insight_data = json.loads(result.content)
            except json.JSONDecodeError:
                # Fallback insight
                insight_data = {
                    "title": "Engagement Analysis",
                    "description": "Analysis of study engagement patterns",
                    "severity": "medium",
                    "data": {"engagement_level": "moderate", "analysis": result.content},
                    "recommendations": ["Monitor daily study habits"],
                    "action_required": False,
                    "confidence_score": 0.6
                }
            
            generation_metadata = {
                "tokens_used": result.tokens_used,
                "cost": result.cost,
                "generation_time_ms": result.generation_time_ms
            }
            
            return insight_data, generation_metadata
            
        except Exception as e:
            logger.error(f"Failed to generate engagement insight: {e}")
            return {
                "title": "Engagement Analysis",
                "description": f"Unable to generate detailed engagement analysis: {str(e)}",
                "severity": "low",
                "data": {"error": str(e)},
                "recommendations": ["Try again later or contact support"],
                "action_required": False,
                "confidence_score": 0.3
            }, {"error": str(e)}
    
    async def _generate_weak_areas_insight(
        self, 
        request: InsightRequest, 
        student_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate weak areas identification insight."""
        try:
            # Build prompt for weak areas analysis
            prompt = f"""
Analyze student data to identify weak areas and knowledge gaps.

Student Data:
{json.dumps(student_data, indent=2)}

Requirements:
1. Identify subjects/topics with low performance
2. Analyze patterns in mistakes and difficulties
3. Prioritize weak areas by impact and urgency
4. Suggest specific improvement strategies
5. Provide confidence score (0-1)

Format as JSON:
{{
    "title": "Weak Areas Analysis",
    "description": "Identification of subjects and topics needing improvement",
    "severity": "low|medium|high|critical",
    "data": {{
        "weak_subjects": [{{"subject": "Physics", "topics": ["Thermodynamics"], "accuracy": 45}}],
        "knowledge_gaps": ["gap1", "gap2"],
        "priority_areas": ["area1", "area2"]
    }},
    "recommendations": ["recommendation1", "recommendation2"],
    "action_required": true/false,
    "confidence_score": 0.8
}}
"""
            
            # Generate content using AI service
            content_request = ContentRequest(
                content_type=ContentType.ANALYSIS,
                prompt=prompt,
                user_id=request.parent_id,
                student_id=request.student_id,
                context={"student_data": student_data, "time_period_days": request.time_period_days},
                metadata={"insight_type": "weak_areas"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse response
            try:
                insight_data = json.loads(result.content)
            except json.JSONDecodeError:
                # Fallback insight
                insight_data = {
                    "title": "Weak Areas Analysis",
                    "description": "Analysis of subjects and topics needing improvement",
                    "severity": "medium",
                    "data": {"weak_areas": "Unable to analyze", "analysis": result.content},
                    "recommendations": ["Review recent test results"],
                    "action_required": True,
                    "confidence_score": 0.6
                }
            
            generation_metadata = {
                "tokens_used": result.tokens_used,
                "cost": result.cost,
                "generation_time_ms": result.generation_time_ms
            }
            
            return insight_data, generation_metadata
            
        except Exception as e:
            logger.error(f"Failed to generate weak areas insight: {e}")
            return {
                "title": "Weak Areas Analysis",
                "description": f"Unable to analyze weak areas: {str(e)}",
                "severity": "low",
                "data": {"error": str(e)},
                "recommendations": ["Try again later or contact support"],
                "action_required": False,
                "confidence_score": 0.3
            }, {"error": str(e)}
    
    async def _generate_progress_insight(
        self, 
        request: InsightRequest, 
        student_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate progress tracking insight."""
        try:
            # Build prompt for progress analysis
            prompt = f"""
Analyze student progress over time and generate insights.

Student Data:
{json.dumps(student_data, indent=2)}

Requirements:
1. Track progress over the last {request.time_period_days} days
2. Compare current performance with previous periods
3. Identify milestones achieved and missed
4. Assess pace relative to goals
5. Provide confidence score (0-1)

Format as JSON:
{{
    "title": "Progress Tracking Insight",
    "description": "Analysis of student progress towards goals",
    "severity": "low|medium|high|critical",
    "data": {{
        "progress_percentage": 75,
        "pace": "on_track|ahead|behind",
        "milestones_achieved": ["milestone1", "milestone2"],
        "areas_of_improvement": ["area1", "area2"]
    }},
    "recommendations": ["recommendation1", "recommendation2"],
    "action_required": true/false,
    "confidence_score": 0.8
}}
"""
            
            # Generate content using AI service
            content_request = ContentRequest(
                content_type=ContentType.ANALYSIS,
                prompt=prompt,
                user_id=request.parent_id,
                student_id=request.student_id,
                context={"student_data": student_data, "time_period_days": request.time_period_days},
                metadata={"insight_type": "progress"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse response
            try:
                insight_data = json.loads(result.content)
            except json.JSONDecodeError:
                # Fallback insight
                insight_data = {
                    "title": "Progress Tracking",
                    "description": "Analysis of progress towards learning goals",
                    "severity": "medium",
                    "data": {"progress": "Unable to analyze", "analysis": result.content},
                    "recommendations": ["Continue monitoring progress"],
                    "action_required": False,
                    "confidence_score": 0.6
                }
            
            generation_metadata = {
                "tokens_used": result.tokens_used,
                "cost": result.cost,
                "generation_time_ms": result.generation_time_ms
            }
            
            return insight_data, generation_metadata
            
        except Exception as e:
            logger.error(f"Failed to generate progress insight: {e}")
            return {
                "title": "Progress Tracking",
                "description": f"Unable to analyze progress: {str(e)}",
                "severity": "low",
                "data": {"error": str(e)},
                "recommendations": ["Try again later or contact support"],
                "action_required": False,
                "confidence_score": 0.3
            }, {"error": str(e)}
    
    async def _generate_recommendation_insight(
        self, 
        request: InsightRequest, 
        student_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate personalized recommendations insight."""
        try:
            # Build prompt for recommendations
            prompt = f"""
Generate personalized recommendations based on student data.

Student Data:
{json.dumps(student_data, indent=2)}

Requirements:
1. Analyze student's current performance and engagement
2. Identify specific areas needing attention
3. Generate actionable, personalized recommendations
4. Prioritize recommendations by impact and feasibility
5. Provide confidence score (0-1)

Format as JSON:
{{
    "title": "Personalized Recommendations",
    "description": "AI-generated recommendations for improvement",
    "severity": "low|medium|high|critical",
    "data": {{
        "top_recommendations": ["rec1", "rec2"],
        "study_strategies": ["strategy1", "strategy2"],
        "resource_suggestions": ["resource1", "resource2"],
        "parent_actions": ["action1", "action2"]
    }},
    "recommendations": ["recommendation1", "recommendation2"],
    "action_required": true/false,
    "confidence_score": 0.8
}}
"""
            
            # Generate content using AI service
            content_request = ContentRequest(
                content_type=ContentType.RECOMMENDATION,
                prompt=prompt,
                user_id=request.parent_id,
                student_id=request.student_id,
                context={"student_data": student_data, "time_period_days": request.time_period_days},
                metadata={"insight_type": "recommendation"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse response
            try:
                insight_data = json.loads(result.content)
            except json.JSONDecodeError:
                # Fallback insight
                insight_data = {
                    "title": "Personalized Recommendations",
                    "description": "AI-generated recommendations for student improvement",
                    "severity": "medium",
                    "data": {"recommendations": "Unable to generate", "analysis": result.content},
                    "recommendations": ["Focus on consistent study habits"],
                    "action_required": True,
                    "confidence_score": 0.6
                }
            
            generation_metadata = {
                "tokens_used": result.tokens_used,
                "cost": result.cost,
                "generation_time_ms": result.generation_time_ms
            }
            
            return insight_data, generation_metadata
            
        except Exception as e:
            logger.error(f"Failed to generate recommendation insight: {e}")
            return {
                "title": "Personalized Recommendations",
                "description": f"Unable to generate recommendations: {str(e)}",
                "severity": "low",
                "data": {"error": str(e)},
                "recommendations": ["Try again later or contact support"],
                "action_required": False,
                "confidence_score": 0.3
            }, {"error": str(e)}
    
    async def _generate_warning_insight(
        self, 
        request: InsightRequest, 
        student_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate early warning insight."""
        try:
            # Build prompt for warning analysis
            prompt = f"""
Analyze student data for early warning signs and potential issues.

Student Data:
{json.dumps(student_data, indent=2)}

Requirements:
1. Identify risk factors and warning signs
2. Assess urgency and potential impact
3. Detect patterns that may indicate problems
4. Generate early warning alerts
5. Provide confidence score (0-1)

Format as JSON:
{{
    "title": "Early Warning Alert",
    "description": "Identification of potential issues requiring attention",
    "severity": "low|medium|high|critical",
    "data": {{
        "warning_signs": ["sign1", "sign2"],
        "risk_factors": ["factor1", "factor2"],
        "urgency_level": "low|medium|high|critical",
        "potential_impact": "impact description"
    }},
    "recommendations": ["recommendation1", "recommendation2"],
    "action_required": true/false,
    "confidence_score": 0.8
}}
"""
            
            # Generate content using AI service
            content_request = ContentRequest(
                content_type=ContentType.ANALYSIS,
                prompt=prompt,
                user_id=request.parent_id,
                student_id=request.student_id,
                context={"student_data": student_data, "time_period_days": request.time_period_days},
                metadata={"insight_type": "warning"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse response
            try:
                insight_data = json.loads(result.content)
            except json.JSONDecodeError:
                # Fallback insight
                insight_data = {
                    "title": "Early Warning Analysis",
                    "description": "Analysis of potential issues and warning signs",
                    "severity": "medium",
                    "data": {"warnings": "Unable to analyze", "analysis": result.content},
                    "recommendations": ["Monitor student closely"],
                    "action_required": True,
                    "confidence_score": 0.6
                }
            
            generation_metadata = {
                "tokens_used": result.tokens_used,
                "cost": result.cost,
                "generation_time_ms": result.generation_time_ms
            }
            
            return insight_data, generation_metadata
            
        except Exception as e:
            logger.error(f"Failed to generate warning insight: {e}")
            return {
                "title": "Early Warning Analysis",
                "description": f"Unable to analyze warning signs: {str(e)}",
                "severity": "low",
                "data": {"error": str(e)},
                "recommendations": ["Try again later or contact support"],
                "action_required": False,
                "confidence_score": 0.3
            }, {"error": str(e)}
    
    async def _generate_opportunity_insight(
        self, 
        request: InsightRequest, 
        student_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate opportunity identification insight."""
        try:
            # Build prompt for opportunity analysis
            prompt = f"""
Analyze student data to identify opportunities for growth and improvement.

Student Data:
{json.dumps(student_data, indent=2)}

Requirements:
1. Identify strengths that can be leveraged
2. Find opportunities for accelerated learning
3. Suggest advanced topics or challenges
4. Recognize potential for achievement
5. Provide confidence score (0-1)

Format as JSON:
{{
    "title": "Growth Opportunity Insight",
    "description": "Identification of opportunities for student growth",
    "severity": "low|medium|high|critical",
    "data": {{
        "strengths": ["strength1", "strength2"],
        "opportunities": ["opportunity1", "opportunity2"],
        "advanced_topics": ["topic1", "topic2"],
        "achievement_potential": "potential description"
    }},
    "recommendations": ["recommendation1", "recommendation2"],
    "action_required": true/false,
    "confidence_score": 0.8
}}
"""
            
            # Generate content using AI service
            content_request = ContentRequest(
                content_type=ContentType.RECOMMENDATION,
                prompt=prompt,
                user_id=request.parent_id,
                student_id=request.student_id,
                context={"student_data": student_data, "time_period_days": request.time_period_days},
                metadata={"insight_type": "opportunity"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse response
            try:
                insight_data = json.loads(result.content)
            except json.JSONDecodeError:
                # Fallback insight
                insight_data = {
                    "title": "Growth Opportunities",
                    "description": "Analysis of opportunities for student growth",
                    "severity": "medium",
                    "data": {"opportunities": "Unable to analyze", "analysis": result.content},
                    "recommendations": ["Explore advanced topics of interest"],
                    "action_required": False,
                    "confidence_score": 0.6
                }
            
            generation_metadata = {
                "tokens_used": result.tokens_used,
                "cost": result.cost,
                "generation_time_ms": result.generation_time_ms
            }
            
            return insight_data, generation_metadata
            
        except Exception as e:
            logger.error(f"Failed to generate opportunity insight: {e}")
            return {
                "title": "Growth Opportunities",
                "description": f"Unable to identify opportunities: {str(e)}",
                "severity": "low",
                "data": {"error": str(e)},
                "recommendations": ["Try again later or contact support"],
                "action_required": False,
                "confidence_score": 0.3
            }, {"error": str(e)}
    
    async def _generate_milestone_insight(
        self, 
        request: InsightRequest, 
        student_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate milestone achievement insight."""
        try:
            # Build prompt for milestone analysis
            prompt = f"""
Analyze student data to identify milestones and achievements.

Student Data:
{json.dumps(student_data, indent=2)}

Requirements:
1. Identify achieved milestones and accomplishments
2. Recognize significant progress markers
3. Celebrate achievements and successes
4. Set next milestone targets
5. Provide confidence score (0-1)

Format as JSON:
{{
    "title": "Milestone Achievement Insight",
    "description": "Recognition of student milestones and achievements",
    "severity": "low|medium|high|critical",
    "data": {{
        "achieved_milestones": ["milestone1", "milestone2"],
        "significant_progress": ["progress1", "progress2"],
        "next_targets": ["target1", "target2"],
        "celebration_points": ["point1", "point2"]
    }},
    "recommendations": ["recommendation1", "recommendation2"],
    "action_required": true/false,
    "confidence_score": 0.8
}}
"""
            
            # Generate content using AI service
            content_request = ContentRequest(
                content_type=ContentType.ANALYSIS,
                prompt=prompt,
                user_id=request.parent_id,
                student_id=request.student_id,
                context={"student_data": student_data, "time_period_days": request.time_period_days},
                metadata={"insight_type": "milestone"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse response
            try:
                insight_data = json.loads(result.content)
            except json.JSONDecodeError:
                # Fallback insight
                insight_data = {
                    "title": "Milestone Achievements",
                    "description": "Analysis of student milestones and progress",
                    "severity": "medium",
                    "data": {"milestones": "Unable to analyze", "analysis": result.content},
                    "recommendations": ["Continue celebrating achievements"],
                    "action_required": False,
                    "confidence_score": 0.6
                }
            
            generation_metadata = {
                "tokens_used": result.tokens_used,
                "cost": result.cost,
                "generation_time_ms": result.generation_time_ms
            }
            
            return insight_data, generation_metadata
            
        except Exception as e:
            logger.error(f"Failed to generate milestone insight: {e}")
            return {
                "title": "Milestone Achievements",
                "description": f"Unable to analyze milestones: {str(e)}",
                "severity": "low",
                "data": {"error": str(e)},
                "recommendations": ["Try again later or contact support"],
                "action_required": False,
                "confidence_score": 0.3
            }, {"error": str(e)}


# Initialize insight generators
def _init_insight_generators(service: 'ParentAIInsightsService'):
    """Initialize insight generators for different types."""
    return {
        InsightType.PERFORMANCE: service._generate_performance_insight,
        InsightType.ENGAGEMENT: service._generate_engagement_insight,
        InsightType.WEAK_AREAS: service._generate_weak_areas_insight,
        InsightType.PROGRESS: service._generate_progress_insight,
        InsightType.RECOMMENDATION: service._generate_recommendation_insight,
        InsightType.WARNING: service._generate_warning_insight,
        InsightType.OPPORTUNITY: service._generate_opportunity_insight,
        InsightType.MILESTONE: service._generate_milestone_insight
    }

# Add insight generators to ParentAIInsightsService class
ParentAIInsightsService.insight_generators = None

def get_parent_ai_insights_service(
    unified_config: Optional[GeminiConfig] = None,
    **kwargs
) -> ParentAIInsightsService:
    """
    Get Parent AI Insights service instance.
    
    Args:
        unified_config: Optional unified configuration
        **kwargs: Additional arguments for service initialization
    
    Returns:
        ParentAIInsightsService instance
    """
    service = ParentAIInsightsService(unified_config=unified_config, **kwargs)
    
    # Initialize insight generators after service creation
    service.insight_generators = _init_insight_generators(service)
    
    return service

# Module initialization
logger.info("Parent AI Insights Service module loaded")