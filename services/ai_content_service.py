"""
AI Content Service for Universal Persistence

This service provides a unified interface for all AI content generation
and persistence operations across the Mentor AI platform.

Features:
- Universal AI content generation with database persistence
- Content type detection and routing
- Multi-modal content support (text, questions, explanations, etc.)
- Comprehensive caching with database sync
- Cost tracking and optimization
- Content quality validation
- Version control for generated content
- Analytics and engagement tracking

Author: Mentor AI Team
Version: 1.0.0
"""

import logging
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps

from pydantic import BaseModel, Field
from google.cloud import firestore

from services.unified_gemini_config_service import get_unified_gemini_service, GeminiConfig
from utils.firebase_config import get_firestore_client

# Configure logging
logger = logging.getLogger(__name__)

# Content types for AI generation
class ContentType(Enum):
    """Types of AI content that can be generated."""
    QUESTION_GENERATION = "question_generation"
    CONTENT_GENERATION = "content_generation"
    EXPLANATION = "explanation"
    SUMMARY = "summary"
    ANALYSIS = "analysis"
    RECOMMENDATION = "recommendation"
    INSIGHT = "insight"
    TUTOR_RESPONSE = "tutor_response"
    LEARNING_MATERIAL = "learning_material"
    MIND_MAP = "mind_map"
    STUDY_PLAN = "study_plan"


@dataclass
class ContentRequest:
    """Request for AI content generation."""
    
    content_type: ContentType
    prompt: str
    user_id: str
    student_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    config_override: Optional[GeminiConfig] = None
    use_cache: bool = True
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ContentResult:
    """Result from AI content generation."""
    
    content_id: str
    content_type: ContentType
    content: Any  # Can be text, questions, analysis, etc.
    metadata: Dict[str, Any]
    quality_score: float
    generation_time_ms: int
    tokens_used: Dict[str, int]
    cost: float
    cached: bool
    interaction_id: Optional[str] = None


class AIContentRecord(BaseModel):
    """Database model for AI content records."""
    
    content_id: str = Field(..., description="Unique content identifier")
    content_type: str = Field(..., description="Type of content generated")
    user_id: str = Field(..., description="User who requested content")
    student_id: Optional[str] = Field(None, description="Student ID if applicable")
    request_data: Dict[str, Any] = Field(..., description="Request parameters and context")
    response_data: Dict[str, Any] = Field(..., description="Generated content data")
    quality_score: float = Field(..., description="Content quality score (0-100)")
    status: str = Field(..., description="Status (pending, completed, failed)")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    tokens_used: Dict[str, int] = Field(default_factory=dict, description="Token usage breakdown")
    cost: float = Field(0.0, description="Cost of this generation")
    generation_time_ms: int = Field(0, description="Generation time in milliseconds")
    cached: bool = Field(False, description="Whether result was from cache")
    version: int = Field(1, description="Content version")
    parent_content_id: Optional[str] = Field(None, description="Parent content ID if derived")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class AIContentService:
    """
    Universal AI content service with database persistence.
    
    This service provides a unified interface for all AI content generation
    operations including questions, explanations, analysis, and more.
    
    Attributes:
        unified_service: Unified Gemini configuration service
        db: Firestore database client
        content_generators: Handlers for different content types
        cache: In-memory cache for content
        quality_validators: Validators for different content types
        version_tracker: Version control for content updates
    
    Example:
        >>> service = AIContentService()
        >>> result = service.generate_content(
        ...     content_type=ContentType.QUESTION_GENERATION,
        ...     prompt="Generate physics questions",
        ...     user_id="user123"
        ... )
        >>> print(f"Generated {len(result.content)} questions")
    """
    
    def __init__(
        self,
        db: Optional[firestore.Client] = None,
        unified_config: Optional[GeminiConfig] = None,
        enable_database_persistence: bool = True,
        cache_size: int = 500,
        cache_ttl_hours: int = 24
    ):
        """
        Initialize AI Content Service.
        
        Args:
            db: Firestore client (creates new if None)
            unified_config: Optional unified configuration
            enable_database_persistence: Enable saving to database
            cache_size: Maximum cache size
            cache_ttl_hours: Cache TTL in hours
        """
        logger.info("Initializing AIContentService")
        
        # Database client
        self.db = db if db else get_firestore_client()
        
        # Initialize unified service
        self.unified_service = get_unified_gemini_service(config=unified_config)
        
        # Configuration
        self.enable_database_persistence = enable_database_persistence
        self.cache_size = cache_size
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        
        # Content cache
        self.content_cache: Dict[str, ContentResult] = {}
        
        # Quality validators
        self.quality_validators: Dict[ContentType, Callable] = {
            ContentType.QUESTION_GENERATION: self._validate_question_content,
            ContentType.CONTENT_GENERATION: self._validate_text_content,
            ContentType.EXPLANATION: self._validate_text_content,
            ContentType.ANALYSIS: self._validate_analysis_content,
            ContentType.RECOMMENDATION: self._validate_text_content,
            ContentType.INSIGHT: self._validate_text_content,
            ContentType.TUTOR_RESPONSE: self._validate_text_content,
            ContentType.LEARNING_MATERIAL: self._validate_text_content,
            ContentType.MIND_MAP: self._validate_text_content,
            ContentType.STUDY_PLAN: self._validate_text_content
        }
        
        # Collections
        self.content_collection = "ai_content"
        self.content_versions_collection = "ai_content_versions"
        
        # Metrics
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_cost": 0.0,
            "total_tokens": 0,
            "average_quality_score": 0.0,
            "content_type_distribution": {ct.value: 0 for ct in ContentType}
        }
        
        logger.info(
            f"AIContentService initialized (db_persistence={enable_database_persistence}, "
            f"cache_size={cache_size}, cache_ttl={cache_ttl_hours}h)"
        )
    
    async def generate_content(
        self,
        request: ContentRequest
    ) -> ContentResult:
        """
        Generate AI content with universal persistence.
        
        Args:
            request: ContentRequest with all generation parameters
        
        Returns:
            ContentResult with generated content and metadata
        
        Raises:
            ValueError: If request is invalid
            Exception: If generation fails
        """
        start_time = time.time()
        
        # Generate content ID
        content_id = f"content_{request.user_id}_{int(time.time())}_{hashlib.md5(request.prompt.encode()).hexdigest()[:8]}"
        
        logger.info(
            f"Generating {request.content_type.value} content: {content_id}"
        )
        
        try:
            # Check cache
            cache_key = self._generate_cache_key(request)
            if request.use_cache and cache_key in self.content_cache:
                cached_result = self.content_cache[cache_key]
                logger.info(f"Cache hit for content: {content_id}")
                
                # Update metrics
                self.metrics["cache_hits"] += 1
                self.metrics["content_type_distribution"][request.content_type.value] += 1
                
                return cached_result
            
            self.metrics["cache_misses"] += 1
            
            # Route to appropriate generator
            generator = self.content_generators.get(request.content_type)
            if not generator:
                raise ValueError(f"No generator for content type: {request.content_type.value}")
            
            # Generate content
            content, generation_metadata = await generator(request)
            
            # Calculate metrics
            generation_time_ms = int((time.time() - start_time) * 1000)
            tokens_used = generation_metadata.get("tokens_used", {"total": 0})
            cost = generation_metadata.get("cost", 0.0)
            
            # Validate quality
            quality_score = self._validate_content_quality(request.content_type, content)
            
            # Create result
            result = ContentResult(
                content_id=content_id,
                content_type=request.content_type,
                content=content,
                metadata={
                    "request_data": {
                        "prompt": request.prompt,
                        "context": request.context,
                        "parameters": request.parameters
                    },
                    "generation_metadata": generation_metadata,
                    **(request.metadata or {})
                },
                quality_score=quality_score,
                generation_time_ms=generation_time_ms,
                tokens_used=tokens_used,
                cost=cost,
                cached=False
            )
            
            # Cache result
            if len(self.content_cache) < self.cache_size:
                self.content_cache[cache_key] = result
            
            # Save to database
            if self.enable_database_persistence:
                await self._save_content_to_db(result, request)
            
            # Update metrics
            self.metrics["total_requests"] += 1
            self.metrics["successful_requests"] += 1
            self.metrics["total_cost"] += cost
            self.metrics["total_tokens"] += tokens_used.get("total", 0)
            self.metrics["content_type_distribution"][request.content_type.value] += 1
            self._update_average_quality(quality_score)
            
            logger.info(
                f"Generated {request.content_type.value} content: {content_id}, "
                f"quality={quality_score:.1f}, cost=${cost:.6f}, "
                f"time={generation_time_ms}ms"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            
            # Update metrics
            self.metrics["total_requests"] += 1
            self.metrics["failed_requests"] += 1
            
            # Save failed attempt to database
            if self.enable_database_persistence:
                failed_result = ContentResult(
                    content_id=content_id,
                    content_type=request.content_type,
                    content=None,
                    metadata={"error": str(e)},
                    quality_score=0.0,
                    generation_time_ms=int((time.time() - start_time) * 1000),
                    tokens_used={},
                    cost=0.0,
                    cached=False
                )
                await self._save_content_to_db(failed_result, request)
            
            raise
    
    async def get_content(
        self,
        content_id: str,
        user_id: Optional[str] = None
    ) -> Optional[AIContentRecord]:
        """
        Retrieve AI content from database.
        
        Args:
            content_id: Content identifier
            user_id: Optional user ID for access control
        
        Returns:
            AI content record or None if not found
        """
        try:
            doc_ref = self.db.collection(self.content_collection).document(content_id)
            doc = await doc_ref.get()
            
            if not doc.exists:
                logger.warning(f"Content not found: {content_id}")
                return None
            
            content_data = doc.to_dict()
            
            # Check access control if user_id provided
            if user_id and content_data.get("user_id") != user_id:
                logger.warning(f"Access denied for content: {content_id}")
                return None
            
            return AIContentRecord(**content_data)
            
        except Exception as e:
            logger.error(f"Failed to get content: {e}")
            raise
    
    async def update_content(
        self,
        content_id: str,
        updates: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> AIContentRecord:
        """
        Update AI content in database.
        
        Args:
            content_id: Content identifier
            updates: Fields to update
            user_id: Optional user ID for access control
        
        Returns:
            Updated AI content record
        """
        try:
            doc_ref = self.db.collection(self.content_collection).document(content_id)
            doc = await doc_ref.get()
            
            if not doc.exists:
                raise ValueError(f"Content not found: {content_id}")
            
            # Check access control
            content_data = doc.to_dict()
            if user_id and content_data.get("user_id") != user_id:
                raise ValueError(f"Access denied for content: {content_id}")
            
            # Update with new version
            updates["version"] = content_data.get("version", 1) + 1
            updates["updated_at"] = datetime.utcnow()
            
            await doc_ref.update(updates)
            
            # Get updated record
            updated_doc = await doc_ref.get()
            return AIContentRecord(**updated_doc.to_dict())
            
        except Exception as e:
            logger.error(f"Failed to update content: {e}")
            raise
    
    async def list_content(
        self,
        user_id: str,
        content_type: Optional[ContentType] = None,
        limit: int = 50,
        start_after: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[AIContentRecord]:
        """
        List AI content with filtering and pagination.
        
        Args:
            user_id: User ID
            content_type: Filter by content type
            limit: Maximum number of results
            start_after: Pagination cursor (content_id)
            filters: Additional filters
        
        Returns:
            List of AI content records
        """
        try:
            query = self.db.collection(self.content_collection)\
                .where("user_id", "==", user_id)\
                .order_by("created_at", direction="DESCENDING")\
                .limit(limit)
            
            if content_type:
                query = query.where("content_type", "==", content_type.value)
            
            if start_after:
                # Get the start document
                start_doc = await self.db.collection(self.content_collection).document(start_after).get()
                if start_doc.exists:
                    query = query.start_after(start_doc)
            
            # Apply additional filters
            if filters:
                for field, value in filters.items():
                    query = query.where(field, "==", value)
            
            results = []
            async for doc in query.stream():
                content_data = doc.to_dict()
                results.append(AIContentRecord(**content_data))
            
            logger.info(f"Listed {len(results)} content items for user {user_id}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to list content: {e}")
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
            "service": "ai_content_service",
            "metrics": self.metrics,
            "derived": {
                "cache_hit_rate": cache_hit_rate,
                "average_cost_per_request": (
                    self.metrics["total_cost"] / max(self.metrics["total_requests"], 1)
                ),
                "success_rate": (
                    self.metrics["successful_requests"] / max(self.metrics["total_requests"], 1)
                )
            },
            "content_type_breakdown": {
                ct: count for ct, count in self.metrics["content_type_distribution"].items()
            }
        }
    
    # ========================================================================
    # PRIVATE METHODS
    # ========================================================================
    
    def _generate_cache_key(self, request: ContentRequest) -> str:
        """Generate cache key for content request."""
        key_data = {
            "content_type": request.content_type.value,
            "prompt": request.prompt,
            "context": request.context,
            "parameters": request.parameters
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def _validate_content_quality(self, content_type: ContentType, content: Any) -> float:
        """Validate content quality and return score (0-100)."""
        validator = self.quality_validators.get(content_type)
        if validator:
            return validator(content)
        return 75.0  # Default score
    
    def _validate_question_content(self, content: List[Dict[str, Any]]) -> float:
        """Validate question content quality."""
        if not content:
            return 0.0
        
        total_score = 0.0
        for question in content:
            score = 0.0
            
            # Check required fields
            if "question" in question and question["question"]:
                score += 20.0
            
            if "options" in question and len(question["options"]) == 4:
                score += 15.0
            
            if "correct_answer" in question and question["correct_answer"]:
                score += 15.0
            
            if "explanation" in question and question["explanation"]:
                score += 20.0
            
            # Check content quality
            if "question" in question:
                q_text = question["question"]
                if len(q_text) > 20:  # Reasonable length
                    score += 10.0
                if "?" in q_text or "." in q_text:  # Proper punctuation
                    score += 5.0
            
            total_score += score
        
        return min(100.0, total_score / len(content))
    
    def _validate_text_content(self, content: str) -> float:
        """Validate text content quality."""
        if not content or not isinstance(content, str):
            return 0.0
        
        score = 50.0  # Base score
        
        # Length check
        if len(content) > 100:
            score += 20.0
        
        # Structure check
        sentences = content.split(".")
        if len(sentences) > 1:
            score += 15.0
        
        # Content indicators
        if any(indicator in content.lower() for indicator in ["because", "therefore", "however", "additionally"]):
            score += 10.0
        
        return min(100.0, score)
    
    def _validate_analysis_content(self, content: Dict[str, Any]) -> float:
        """Validate analysis content quality."""
        if not content or not isinstance(content, dict):
            return 0.0
        
        score = 50.0  # Base score
        
        # Check for key analysis components
        if "insights" in content and content["insights"]:
            score += 20.0
        
        if "recommendations" in content and content["recommendations"]:
            score += 15.0
        
        if "data" in content and content["data"]:
            score += 15.0
        
        return min(100.0, score)
    
    def _update_average_quality(self, new_score: float):
        """Update running average quality score."""
        total_requests = self.metrics["total_requests"]
        if total_requests > 0:
            current_avg = self.metrics["average_quality_score"]
            self.metrics["average_quality_score"] = (
                (current_avg * (total_requests - 1) + new_score) / total_requests
            )
    
    async def _save_content_to_db(self, result: ContentResult, request: ContentRequest):
        """Save content result to database."""
        try:
            content_record = AIContentRecord(
                content_id=result.content_id,
                content_type=result.content_type.value,
                user_id=request.user_id,
                student_id=request.student_id,
                request_data={
                    "prompt": request.prompt,
                    "context": request.context,
                    "parameters": request.parameters,
                    "config_override": request.config_override.dict() if request.config_override else None
                },
                response_data=result.metadata,
                quality_score=result.quality_score,
                status="completed" if result.content else "failed",
                error_message=None if result.content else "Generation failed",
                tokens_used=result.tokens_used,
                cost=result.cost,
                generation_time_ms=result.generation_time_ms,
                cached=result.cached,
                metadata=result.metadata
            )
            
            doc_ref = self.db.collection(self.content_collection).document(result.content_id)
            await doc_ref.set(content_record.model_dump())
            
            logger.debug(f"Saved content to database: {result.content_id}")
            
        except Exception as e:
            logger.error(f"Failed to save content to database: {e}")


    async def _generate_questions(self, request: ContentRequest) -> tuple:
        """Generate questions using unified service."""
        from services.gemini_service import get_gemini_service
        
        gemini_service = get_gemini_service()
        
        # Extract parameters from request
        params = request.parameters or {}
        topic = params.get("topic", "General")
        exam_type = params.get("exam_type", "JEE_MAIN")
        difficulty = params.get("difficulty", "medium")
        num_questions = params.get("num_questions", 5)
        
        # Generate questions
        questions = await gemini_service.generate_questions(
            prompt=request.prompt,
            num_questions=num_questions,
            user_id=request.user_id,
            student_id=request.student_id,
            metadata=request.metadata
        )
        
        # Convert to dict format
        questions_data = []
        for q in questions:
            questions_data.append({
                "question": q.question_text,
                "options": q.options,
                "correct_answer": q.correct_answer,
                "explanation": q.explanation
            })
        
        return questions_data, {
            "tokens_used": {"total": len(request.prompt) // 4},
            "cost": 0.0001  # Estimated cost
        }
    
    async def _generate_text_content(self, request: ContentRequest) -> tuple:
        """Generate text content using unified service."""
        unified_service = self.unified_service
        
        result = await unified_service.generate_content(
            prompt=request.prompt,
            user_id=request.user_id,
            student_id=request.student_id,
            interaction_type=request.content_type.value,
            metadata=request.metadata
        )
        
        return result.get("content", ""), {
            "tokens_used": result.get("tokens_used", {}),
            "cost": result.get("cost", 0.0)
        }
    
    async def _generate_analysis(self, request: ContentRequest) -> tuple:
        """Generate analysis content."""
        # Generate text content first
        content, metadata = await self._generate_text_content(request)
        
        # Try to parse as analysis
        try:
            import json
            analysis_data = json.loads(content)
            return analysis_data, metadata
        except:
            # Return as text analysis
            return {
                "analysis": content,
                "insights": [],
                "recommendations": []
            }, metadata
    
    async def _generate_mind_map(self, request: ContentRequest) -> tuple:
        """Generate mind map content."""
        # Generate text content first
        content, metadata = await self._generate_text_content(request)
        
        # Format as mind map
        return {
            "title": request.parameters.get("title", "Mind Map"),
            "content": content,
            "nodes": [],
            "connections": []
        }, metadata
    
    async def _generate_study_plan(self, request: ContentRequest) -> tuple:
        """Generate study plan content."""
        # Generate text content first
        content, metadata = await self._generate_text_content(request)
        
        # Format as study plan
        return {
            "title": request.parameters.get("title", "Study Plan"),
            "content": content,
            "tasks": [],
            "timeline": [],
            "milestones": []
        }, metadata


# Initialize content generators
def _init_content_generators(service: 'AIContentService'):
    """Initialize content generators for different types."""
    return {
        ContentType.QUESTION_GENERATION: service._generate_questions,
        ContentType.CONTENT_GENERATION: service._generate_text_content,
        ContentType.EXPLANATION: service._generate_text_content,
        ContentType.SUMMARY: service._generate_text_content,
        ContentType.ANALYSIS: service._generate_analysis,
        ContentType.RECOMMENDATION: service._generate_text_content,
        ContentType.INSIGHT: service._generate_text_content,
        ContentType.TUTOR_RESPONSE: service._generate_text_content,
        ContentType.LEARNING_MATERIAL: service._generate_text_content,
        ContentType.MIND_MAP: service._generate_mind_map,
        ContentType.STUDY_PLAN: service._generate_study_plan
    }


# Add content generators to AIContentService class
AIContentService.content_generators = None

def get_ai_content_service(
    unified_config: Optional[GeminiConfig] = None,
    **kwargs
) -> AIContentService:
    """
    Get AI content service instance.
    
    Args:
        unified_config: Optional unified configuration
        **kwargs: Additional arguments for service initialization
    
    Returns:
        AIContentService instance
    """
    service = AIContentService(unified_config=unified_config, **kwargs)
    
    # Initialize content generators after service creation
    service.content_generators = _init_content_generators(service)
    
    return service


# Module initialization
logger.info("AI Content Service module loaded")