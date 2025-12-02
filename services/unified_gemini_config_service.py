"""
Unified Gemini Flash Configuration Service

This module provides a centralized configuration and management service
for all Gemini Flash operations across the Mentor AI platform.

Features:
- Centralized Gemini Flash configuration
- Database persistence for all AI interactions
- Cost tracking and optimization
- Rate limiting and quota management
- Performance monitoring
- Error handling and retry logic
- Cache management with database sync

Author: Mentor AI Team
Version: 1.0.0
"""

import logging
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from functools import lru_cache
from collections import defaultdict, deque

from google.cloud import firestore
from pydantic import BaseModel, Field

from utils.firebase_config import get_firestore_client
from utils.gemini_client import GeminiClient, GeminiClientError

# Configure logging
logger = logging.getLogger(__name__)

# Gemini Flash pricing (updated 2024)
GEMINI_FLASH_INPUT_COST_PER_1K = 0.000125
GEMINI_FLASH_OUTPUT_COST_PER_1K = 0.000375
GEMINI_FLASH_CONTEXT_WINDOW = 1_048_576  # 1M tokens
GEMINI_FLASH_MAX_OUTPUT = 8192  # 8K tokens

# Rate limiting
DEFAULT_RATE_LIMIT = 60  # requests per minute
DEFAULT_QUOTA_LIMIT = 15000  # requests per day

# Cache settings
DEFAULT_CACHE_TTL = timedelta(hours=24)
DEFAULT_CACHE_SIZE = 1000


@dataclass
class GeminiConfig:
    """Configuration for Gemini Flash operations."""
    
    model_name: str = "gemini-1.5-flash"
    temperature: float = 0.7
    max_output_tokens: int = 8192
    top_p: float = 0.95
    top_k: int = 40
    candidate_count: int = 1
    stop_sequences: List[str] = field(default_factory=list)
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls."""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_output_tokens": self.max_output_tokens,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "candidate_count": self.candidate_count,
            "stop_sequences": self.stop_sequences,
            "presence_penalty": self.presence_penalty,
            "frequency_penalty": self.frequency_penalty
        }


class AIInteraction(BaseModel):
    """Model for AI interaction database storage."""
    
    interaction_id: str = Field(..., description="Unique interaction identifier")
    user_id: str = Field(..., description="User who initiated the interaction")
    student_id: Optional[str] = Field(None, description="Student ID if applicable")
    interaction_type: str = Field(..., description="Type of interaction (question_generation, content_generation, etc.)")
    request_data: Dict[str, Any] = Field(..., description="Request parameters and context")
    response_data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    status: str = Field(..., description="Status (pending, completed, failed)")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    tokens_used: Dict[str, int] = Field(default_factory=dict, description="Token usage breakdown")
    cost: float = Field(0.0, description="Cost of this interaction")
    response_time_ms: int = Field(0, description="Response time in milliseconds")
    cached: bool = Field(False, description="Whether result was from cache")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class CostTracker(BaseModel):
    """Model for cost tracking."""
    
    date: datetime = Field(..., description="Date for cost tracking")
    user_id: Optional[str] = Field(None, description="User ID if user-specific")
    service: str = Field(..., description="Service name (gemini_flash, etc.)")
    total_requests: int = Field(0, description="Total requests")
    total_input_tokens: int = Field(0, description="Total input tokens")
    total_output_tokens: int = Field(0, description="Total output tokens")
    total_cost: float = Field(0.0, description="Total cost")
    cache_hits: int = Field(0, description="Number of cache hits")
    cache_misses: int = Field(0, description="Number of cache misses")


class UnifiedGeminiConfigService:
    """
    Unified service for Gemini Flash configuration and management.
    
    This service provides centralized management for all Gemini Flash operations,
    including configuration, database persistence, cost tracking, and performance monitoring.
    
    Attributes:
        db: Firestore database client
        gemini_client: Gemini API client
        config: Default Gemini configuration
        rate_limiters: Per-user rate limiting
        cost_trackers: Cost tracking by user and date
        interaction_cache: In-memory cache for interactions
    
    Example:
        >>> service = UnifiedGeminiConfigService()
        >>> config = service.get_config()
        >>> result = service.generate_content("Explain physics", user_id="user123")
    """
    
    def __init__(
        self,
        db: Optional[firestore.Client] = None,
        config: Optional[GeminiConfig] = None,
        enable_database_persistence: bool = True,
        enable_cost_tracking: bool = True,
        enable_rate_limiting: bool = True
    ):
        """
        Initialize Unified Gemini Config Service.
        
        Args:
            db: Firestore client (creates new if None)
            config: Default Gemini configuration
            enable_database_persistence: Enable saving to database
            enable_cost_tracking: Enable cost tracking
            enable_rate_limiting: Enable rate limiting
        """
        logger.info("Initializing UnifiedGeminiConfigService")
        
        # Database client
        self.db = db if db else get_firestore_client()
        
        # Gemini client
        self.gemini_client = GeminiClient()
        
        # Configuration
        self.config = config if config else GeminiConfig()
        
        # Feature flags
        self.enable_database_persistence = enable_database_persistence
        self.enable_cost_tracking = enable_cost_tracking
        self.enable_rate_limiting = enable_rate_limiting
        
        # Rate limiting (per user)
        self.rate_limiters: Dict[str, deque] = defaultdict(lambda: deque(maxlen=DEFAULT_RATE_LIMIT))
        
        # Cost tracking
        self.cost_trackers: Dict[str, CostTracker] = {}
        
        # Interaction cache
        self.interaction_cache: Dict[str, AIInteraction] = {}
        self.cache_max_size = DEFAULT_CACHE_SIZE
        
        # Collections
        self.interactions_collection = "ai_interactions"
        self.cost_tracking_collection = "cost_tracking"
        
        logger.info(
            f"UnifiedGeminiConfigService initialized "
            f"(db_persistence={enable_database_persistence}, "
            f"cost_tracking={enable_cost_tracking}, "
            f"rate_limiting={enable_rate_limiting})"
        )
    
    def get_config(self) -> GeminiConfig:
        """
        Get current Gemini configuration.
        
        Returns:
            GeminiConfig: Current configuration
        """
        return self.config
    
    def update_config(self, **kwargs) -> GeminiConfig:
        """
        Update Gemini configuration.
        
        Args:
            **kwargs: Configuration parameters to update
        
        Returns:
            GeminiConfig: Updated configuration
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.info(f"Updated config: {key} = {value}")
        
        # Save to database if enabled
        if self.enable_database_persistence:
            self._save_config_to_db()
        
        return self.config
    
    async def generate_content(
        self,
        prompt: str,
        user_id: str,
        student_id: Optional[str] = None,
        interaction_type: str = "content_generation",
        config_override: Optional[GeminiConfig] = None,
        use_cache: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate content using Gemini Flash with full tracking.
        
        Args:
            prompt: Input prompt for generation
            user_id: User ID requesting the generation
            student_id: Student ID if applicable
            interaction_type: Type of interaction for tracking
            config_override: Override configuration for this request
            use_cache: Use cached results if available
            metadata: Additional metadata
        
        Returns:
            Dict containing generated content and metadata
        
        Raises:
            GeminiClientError: If API call fails
            ValueError: If rate limit exceeded
        """
        start_time = time.time()
        
        # Generate interaction ID
        interaction_id = f"ai_{user_id}_{int(time.time())}_{hashlib.md5(prompt.encode()).hexdigest()[:8]}"
        
        # Check cache
        cache_key = self._generate_cache_key(prompt, user_id, interaction_type)
        if use_cache and cache_key in self.interaction_cache:
            cached_interaction = self.interaction_cache[cache_key]
            logger.info(f"Cache hit for interaction: {interaction_id}")
            
            # Update cache hit tracking
            if self.enable_cost_tracking:
                self._track_cache_hit(user_id)
            
            return {
                "content": cached_interaction.response_data.get("content", ""),
                "interaction_id": cached_interaction.interaction_id,
                "cached": True,
                "response_time_ms": 0,
                "tokens_used": cached_interaction.tokens_used,
                "cost": 0.0
            }
        
        # Check rate limit
        if self.enable_rate_limiting and not self._check_rate_limit(user_id):
            wait_time = self._get_rate_limit_wait_time(user_id)
            raise ValueError(f"Rate limit exceeded. Please wait {wait_time:.1f} seconds")
        
        # Create interaction record
        interaction = AIInteraction(
            interaction_id=interaction_id,
            user_id=user_id,
            student_id=student_id,
            interaction_type=interaction_type,
            request_data={
                "prompt": prompt,
                "config": (config_override or self.config).to_dict(),
                "metadata": metadata or {}
            },
            status="pending",
            created_at=datetime.utcnow()
        )
        
        # Save to database if enabled
        if self.enable_database_persistence:
            await self._save_interaction_async(interaction)
        
        try:
            # Use config override if provided
            config = config_override if config_override else self.config
            
            # Call Gemini API
            response_text = self.gemini_client.generate_content(
                prompt=prompt,
                temperature=config.temperature,
                max_output_tokens=config.max_output_tokens,
                top_p=config.top_p,
                top_k=config.top_k
            )
            
            # Calculate metrics
            response_time_ms = int((time.time() - start_time) * 1000)
            input_tokens = len(prompt) // 4  # Rough estimate
            output_tokens = len(response_text) // 4
            total_tokens = input_tokens + output_tokens
            cost = self._calculate_cost(input_tokens, output_tokens)
            
            # Update interaction
            interaction.response_data = {"content": response_text}
            interaction.status = "completed"
            interaction.tokens_used = {
                "input": input_tokens,
                "output": output_tokens,
                "total": total_tokens
            }
            interaction.cost = cost
            interaction.response_time_ms = response_time_ms
            interaction.completed_at = datetime.utcnow()
            
            # Cache result
            if use_cache and len(self.interaction_cache) < self.cache_max_size:
                self.interaction_cache[cache_key] = interaction
            
            # Update cost tracking
            if self.enable_cost_tracking:
                self._track_cost(user_id, input_tokens, output_tokens, cost)
            
            # Update database
            if self.enable_database_persistence:
                await self._update_interaction_async(interaction)
            
            logger.info(
                f"Generated content for {interaction_id}: "
                f"{len(response_text)} chars, {total_tokens} tokens, "
                f"${cost:.6f}, {response_time_ms}ms"
            )
            
            return {
                "content": response_text,
                "interaction_id": interaction_id,
                "cached": False,
                "response_time_ms": response_time_ms,
                "tokens_used": interaction.tokens_used,
                "cost": cost
            }
            
        except Exception as e:
            # Update interaction with error
            interaction.status = "failed"
            interaction.error_message = str(e)
            interaction.response_time_ms = int((time.time() - start_time) * 1000)
            interaction.completed_at = datetime.utcnow()
            
            # Update database
            if self.enable_database_persistence:
                await self._update_interaction_async(interaction)
            
            logger.error(f"Content generation failed for {interaction_id}: {e}")
            raise
    
    async def generate_questions(
        self,
        topic: str,
        exam_type: str,
        difficulty: str,
        num_questions: int,
        user_id: str,
        student_id: Optional[str] = None,
        config_override: Optional[GeminiConfig] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Generate questions using Gemini Flash with full tracking.
        
        Args:
            topic: Topic for question generation
            exam_type: Type of exam (JEE_MAIN, JEE_ADVANCED, NEET)
            difficulty: Difficulty level (easy, medium, hard)
            num_questions: Number of questions to generate
            user_id: User ID requesting the generation
            student_id: Student ID if applicable
            config_override: Override configuration for this request
            use_cache: Use cached results if available
        
        Returns:
            Dict containing generated questions and metadata
        """
        start_time = time.time()
        
        # Generate interaction ID
        interaction_id = f"qgen_{user_id}_{int(time.time())}_{hashlib.md5(topic.encode()).hexdigest()[:8]}"
        
        # Check cache
        cache_key = self._generate_cache_key(
            f"{topic}_{exam_type}_{difficulty}_{num_questions}",
            user_id,
            "question_generation"
        )
        if use_cache and cache_key in self.interaction_cache:
            cached_interaction = self.interaction_cache[cache_key]
            logger.info(f"Cache hit for question generation: {interaction_id}")
            
            if self.enable_cost_tracking:
                self._track_cache_hit(user_id)
            
            return {
                "questions": cached_interaction.response_data.get("questions", []),
                "interaction_id": cached_interaction.interaction_id,
                "cached": True,
                "response_time_ms": 0,
                "tokens_used": cached_interaction.tokens_used,
                "cost": 0.0
            }
        
        # Check rate limit
        if self.enable_rate_limiting and not self._check_rate_limit(user_id):
            wait_time = self._get_rate_limit_wait_time(user_id)
            raise ValueError(f"Rate limit exceeded. Please wait {wait_time:.1f} seconds")
        
        # Build prompt for question generation
        prompt = self._build_question_generation_prompt(
            topic, exam_type, difficulty, num_questions
        )
        
        # Create interaction record
        interaction = AIInteraction(
            interaction_id=interaction_id,
            user_id=user_id,
            student_id=student_id,
            interaction_type="question_generation",
            request_data={
                "topic": topic,
                "exam_type": exam_type,
                "difficulty": difficulty,
                "num_questions": num_questions,
                "config": (config_override or self.config).to_dict()
            },
            status="pending",
            created_at=datetime.utcnow()
        )
        
        # Save to database if enabled
        if self.enable_database_persistence:
            await self._save_interaction_async(interaction)
        
        try:
            # Use config override if provided
            config = config_override if config_override else self.config
            
            # Call Gemini API
            response_text = self.gemini_client.generate_content(
                prompt=prompt,
                temperature=config.temperature,
                max_output_tokens=config.max_output_tokens,
                top_p=config.top_p,
                top_k=config.top_k
            )
            
            # Parse questions from response
            questions = self._parse_questions_from_response(response_text)
            
            # Calculate metrics
            response_time_ms = int((time.time() - start_time) * 1000)
            input_tokens = len(prompt) // 4
            output_tokens = len(response_text) // 4
            total_tokens = input_tokens + output_tokens
            cost = self._calculate_cost(input_tokens, output_tokens)
            
            # Update interaction
            interaction.response_data = {"questions": questions}
            interaction.status = "completed"
            interaction.tokens_used = {
                "input": input_tokens,
                "output": output_tokens,
                "total": total_tokens
            }
            interaction.cost = cost
            interaction.response_time_ms = response_time_ms
            interaction.completed_at = datetime.utcnow()
            
            # Cache result
            if use_cache and len(self.interaction_cache) < self.cache_max_size:
                self.interaction_cache[cache_key] = interaction
            
            # Update cost tracking
            if self.enable_cost_tracking:
                self._track_cost(user_id, input_tokens, output_tokens, cost)
            
            # Update database
            if self.enable_database_persistence:
                await self._update_interaction_async(interaction)
            
            logger.info(
                f"Generated questions for {interaction_id}: "
                f"{len(questions)} questions, {total_tokens} tokens, "
                f"${cost:.6f}, {response_time_ms}ms"
            )
            
            return {
                "questions": questions,
                "interaction_id": interaction_id,
                "cached": False,
                "response_time_ms": response_time_ms,
                "tokens_used": interaction.tokens_used,
                "cost": cost
            }
            
        except Exception as e:
            # Update interaction with error
            interaction.status = "failed"
            interaction.error_message = str(e)
            interaction.response_time_ms = int((time.time() - start_time) * 1000)
            interaction.completed_at = datetime.utcnow()
            
            # Update database
            if self.enable_database_persistence:
                await self._update_interaction_async(interaction)
            
            logger.error(f"Question generation failed for {interaction_id}: {e}")
            raise
    
    def get_user_interactions(
        self,
        user_id: str,
        limit: int = 50,
        interaction_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[AIInteraction]:
        """
        Get AI interactions for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of interactions to return
            interaction_type: Filter by interaction type
            start_date: Filter by start date
            end_date: Filter by end date
        
        Returns:
            List of AI interactions
        """
        try:
            query = self.db.collection(self.interactions_collection)\
                .where("user_id", "==", user_id)\
                .order_by("created_at", direction="DESCENDING")\
                .limit(limit)
            
            if interaction_type:
                query = query.where("interaction_type", "==", interaction_type)
            
            if start_date:
                query = query.where("created_at", ">=", start_date)
            
            if end_date:
                query = query.where("created_at", "<=", end_date)
            
            interactions = []
            for doc in query.stream():
                data = doc.to_dict()
                interactions.append(AIInteraction(**data))
            
            logger.info(f"Retrieved {len(interactions)} interactions for user {user_id}")
            return interactions
            
        except Exception as e:
            logger.error(f"Failed to get user interactions: {e}")
            raise
    
    def get_cost_tracking(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[CostTracker]:
        """
        Get cost tracking information.
        
        Args:
            user_id: Filter by user ID
            start_date: Filter by start date
            end_date: Filter by end date
        
        Returns:
            List of cost tracking records
        """
        try:
            query = self.db.collection(self.cost_tracking_collection)\
                .order_by("date", direction="DESCENDING")
            
            if user_id:
                query = query.where("user_id", "==", user_id)
            
            if start_date:
                query = query.where("date", ">=", start_date)
            
            if end_date:
                query = query.where("date", "<=", end_date)
            
            cost_records = []
            for doc in query.stream():
                data = doc.to_dict()
                cost_records.append(CostTracker(**data))
            
            logger.info(f"Retrieved {len(cost_records)} cost tracking records")
            return cost_records
            
        except Exception as e:
            logger.error(f"Failed to get cost tracking: {e}")
            raise
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get comprehensive service status.
        
        Returns:
            Dict containing service status and metrics
        """
        try:
            # Get current date cost tracking
            today = datetime.utcnow().date()
            today_start = datetime.combine(today, datetime.min.time())
            
            today_costs = self.get_cost_tracking(
                start_date=today_start,
                end_date=datetime.utcnow()
            )
            
            total_today_cost = sum(record.total_cost for record in today_costs)
            total_today_requests = sum(record.total_requests for record in today_costs)
            
            # Cache status
            cache_size = len(self.interaction_cache)
            cache_hit_rate = 0.0
            
            if self.enable_cost_tracking:
                total_cache_hits = sum(record.cache_hits for record in today_costs)
                total_cache_misses = sum(record.cache_misses for record in today_costs)
                total_cache_attempts = total_cache_hits + total_cache_misses
                cache_hit_rate = total_cache_hits / total_cache_attempts if total_cache_attempts > 0 else 0.0
            
            return {
                "service": "unified_gemini_config",
                "status": "healthy",
                "config": self.config.to_dict(),
                "features": {
                    "database_persistence": self.enable_database_persistence,
                    "cost_tracking": self.enable_cost_tracking,
                    "rate_limiting": self.enable_rate_limiting
                },
                "metrics": {
                    "cache_size": cache_size,
                    "cache_hit_rate": cache_hit_rate,
                    "total_today_cost": total_today_cost,
                    "total_today_requests": total_today_requests,
                    "active_rate_limiters": len(self.rate_limiters)
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get service status: {e}")
            return {
                "service": "unified_gemini_config",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================
    
    def _generate_cache_key(
        self,
        content: str,
        user_id: str,
        interaction_type: str
    ) -> str:
        """Generate cache key for interaction."""
        key_string = f"{user_id}:{interaction_type}:{hashlib.md5(content.encode()).hexdigest()}"
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def _check_rate_limit(self, user_id: str) -> bool:
        """Check if user has exceeded rate limit."""
        if not self.enable_rate_limiting:
            return True
        
        current_time = time.time()
        user_requests = self.rate_limiters[user_id]
        
        # Remove old requests (older than 1 minute)
        while user_requests and current_time - user_requests[0] > 60:
            user_requests.popleft()
        
        # Check if under limit
        return len(user_requests) < DEFAULT_RATE_LIMIT
    
    def _get_rate_limit_wait_time(self, user_id: str) -> float:
        """Get wait time until rate limit resets."""
        user_requests = self.rate_limiters[user_id]
        if not user_requests:
            return 0.0
        
        current_time = time.time()
        oldest_request = user_requests[0]
        return max(0.0, 60.0 - (current_time - oldest_request))
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for Gemini Flash API."""
        input_cost = (input_tokens / 1000.0) * GEMINI_FLASH_INPUT_COST_PER_1K
        output_cost = (output_tokens / 1000.0) * GEMINI_FLASH_OUTPUT_COST_PER_1K
        return input_cost + output_cost
    
    def _track_cost(
        self,
        user_id: str,
        input_tokens: int,
        output_tokens: int,
        cost: float
    ):
        """Track cost for user and date."""
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time())
        date_key = today_start.isoformat()
        
        if date_key not in self.cost_trackers:
            self.cost_trackers[date_key] = CostTracker(
                date=today_start,
                user_id=user_id,
                service="gemini_flash"
            )
        
        tracker = self.cost_trackers[date_key]
        tracker.total_requests += 1
        tracker.total_input_tokens += input_tokens
        tracker.total_output_tokens += output_tokens
        tracker.total_cost += cost
        tracker.cache_misses += 1
        
        # Save to database periodically
        if tracker.total_requests % 10 == 0:
            self._save_cost_tracker(tracker)
    
    def _track_cache_hit(self, user_id: str):
        """Track cache hit for user."""
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time())
        date_key = today_start.isoformat()
        
        if date_key not in self.cost_trackers:
            self.cost_trackers[date_key] = CostTracker(
                date=today_start,
                user_id=user_id,
                service="gemini_flash"
            )
        
        self.cost_trackers[date_key].cache_hits += 1
    
    def _build_question_generation_prompt(
        self,
        topic: str,
        exam_type: str,
        difficulty: str,
        num_questions: int
    ) -> str:
        """Build prompt for question generation."""
        return f"""
Generate {num_questions} high-quality multiple-choice questions for {exam_type} exam.

Topic: {topic}
Difficulty: {difficulty}

Requirements:
1. Each question must have 4 options (A, B, C, D)
2. Clearly mark the correct answer
3. Include detailed explanation for the correct answer
4. Questions should test conceptual understanding
5. Format as JSON array with structure:
   {{
     "question": "question text",
     "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
     "correct_answer": "A",
     "explanation": "detailed explanation"
   }}

Generate exactly {num_questions} questions.
"""
    
    def _parse_questions_from_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse questions from Gemini response."""
        try:
            # Try to parse as JSON
            import json
            questions = json.loads(response_text)
            
            if isinstance(questions, list):
                return questions
            elif isinstance(questions, dict) and "questions" in questions:
                return questions["questions"]
            else:
                # Fallback: return as single question
                return [questions]
                
        except json.JSONDecodeError:
            # Fallback: return raw response as single question
            return [{
                "question": response_text,
                "options": ["A) N/A", "B) N/A", "C) N/A", "D) N/A"],
                "correct_answer": "A",
                "explanation": "Response could not be parsed as JSON"
            }]
    
    async def _save_interaction_async(self, interaction: AIInteraction):
        """Save interaction to Firestore asynchronously."""
        try:
            doc_ref = self.db.collection(self.interactions_collection).document(interaction.interaction_id)
            await doc_ref.set(interaction.model_dump())
        except Exception as e:
            logger.error(f"Failed to save interaction: {e}")
    
    async def _update_interaction_async(self, interaction: AIInteraction):
        """Update interaction in Firestore asynchronously."""
        try:
            doc_ref = self.db.collection(self.interactions_collection).document(interaction.interaction_id)
            await doc_ref.update(interaction.model_dump(exclude_none=True))
        except Exception as e:
            logger.error(f"Failed to update interaction: {e}")
    
    def _save_config_to_db(self):
        """Save current configuration to database."""
        try:
            config_data = {
                "config": self.config.to_dict(),
                "updated_at": datetime.utcnow(),
                "features": {
                    "database_persistence": self.enable_database_persistence,
                    "cost_tracking": self.enable_cost_tracking,
                    "rate_limiting": self.enable_rate_limiting
                }
            }
            
            doc_ref = self.db.collection("gemini_config").document("current_config")
            doc_ref.set(config_data)
            
            logger.info("Configuration saved to database")
            
        except Exception as e:
            logger.error(f"Failed to save config to database: {e}")
    
    def _save_cost_tracker(self, tracker: CostTracker):
        """Save cost tracker to database."""
        try:
            doc_id = f"{tracker.date.isoformat()}_{tracker.user_id or 'global'}_{tracker.service}"
            doc_ref = self.db.collection(self.cost_tracking_collection).document(doc_id)
            doc_ref.set(tracker.model_dump())
            
        except Exception as e:
            logger.error(f"Failed to save cost tracker: {e}")


# Singleton instance
_unified_gemini_service: Optional[UnifiedGeminiConfigService] = None


def get_unified_gemini_service(
    config: Optional[GeminiConfig] = None,
    **kwargs
) -> UnifiedGeminiConfigService:
    """
    Get or create singleton UnifiedGeminiConfigService instance.
    
    Args:
        config: Optional Gemini configuration
        **kwargs: Additional arguments for service initialization
    
    Returns:
        UnifiedGeminiConfigService instance
    """
    global _unified_gemini_service
    
    if _unified_gemini_service is None:
        logger.info("Creating new UnifiedGeminiConfigService singleton instance")
        _unified_gemini_service = UnifiedGeminiConfigService(config=config, **kwargs)
    
    return _unified_gemini_service


# Module initialization
logger.info("Unified Gemini Config Service module loaded")
logger.info(f"Gemini Flash pricing: ${GEMINI_FLASH_INPUT_COST_PER_1K}/1K input, ${GEMINI_FLASH_OUTPUT_COST_PER_1K}/1K output")