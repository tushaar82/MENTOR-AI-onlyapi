"""
Parent Resource Library Service

This service provides AI-curated educational resources
for parents to support their child's learning journey.

Features:
- AI-curated teaching resources
- Age-appropriate content filtering
- Multi-language resource support
- Resource effectiveness tracking
- Resource recommendation engine
- Community-contributed resources with moderation
- Downloadable materials library
- Resource quality assessment
- Parent community features
- Content rating and review system
- Resource sharing and collaboration
- Expert-verified content badges
- Community challenges and competitions

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

# Configure logging
logger = logging.getLogger(__name__)

# Resource types and categories
class ResourceType(Enum):
    """Types of educational resources."""
    ARTICLE = "article"
    VIDEO = "video"
    EXERCISE = "exercise"
    WORKSHEET = "worksheet"
    GUIDE = "guide"
    ACTIVITY = "activity"
    ASSESSMENT = "assessment"
    TOOL = "tool"
    TEMPLATE = "template"

class ResourceCategory(Enum):
    """Categories of educational resources."""
    STUDY_STRATEGIES = "study_strategies"
    SUBJECT_SPECIFIC = "subject_specific"
    EXAM_PREPARATION = "exam_preparation"
    MOTIVATION = "motivation"
    PARENTING_TIPS = "parenting_tips"
    LEARNING_DISABILITIES = "learning_disabilities"
    CAREER_GUIDANCE = "career_guidance"
    TIME_MANAGEMENT = "time_management"

class DifficultyLevel(Enum):
    """Difficulty levels for resources."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    MIXED = "mixed"

class QualityScore(Enum):
    """Quality assessment levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"

@dataclass
class CommunityResource:
    """Community-contributed resource definition."""
    
    resource_id: str
    parent_id: str
    title: str
    description: str
    resource_type: ResourceType
    category: ResourceCategory
    subject: Optional[str]
    difficulty_level: DifficultyLevel
    age_group: str
    language: str
    content: str
    download_url: Optional[str]
    tags: List[str]
    quality_score: QualityScore
    effectiveness_rating: float
    usage_count: int
    user_ratings: List[float]
    reviews: List[Dict[str, Any]]
    expert_verified: bool
    expert_badge: Optional[str]
    community_likes: int
    community_shares: int
    moderation_status: str  # "pending", "approved", "rejected"
    moderation_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class Resource:
    """Educational resource definition."""
    
    resource_id: str
    title: str
    description: str
    resource_type: ResourceType
    category: ResourceCategory
    subject: Optional[str]
    difficulty_level: DifficultyLevel
    age_group: str
    language: str
    content: str
    download_url: Optional[str]
    tags: List[str]
    quality_score: QualityScore
    effectiveness_rating: float
    usage_count: int
    user_ratings: List[float]
    ai_generated: bool
    community_contributed: bool
    created_at: datetime
    updated_at: datetime

@dataclass
class CommunityChallenge:
    """Community challenge definition."""
    
    challenge_id: str
    title: str
    description: str
    challenge_type: str  # "resource_creation", "review", "sharing"
    category: ResourceCategory
    subject: Optional[str]
    difficulty_level: DifficultyLevel
    start_date: datetime
    end_date: datetime
    participation_count: int
    reward_points: int
    reward_badge: str
    requirements: List[str]
    evaluation_criteria: List[str]
    created_at: datetime

@dataclass
class ParentContribution:
    """Parent contribution tracking."""
    
    contribution_id: str
    parent_id: str
    contribution_type: str  # "resource", "review", "challenge_participation"
    resource_id: Optional[str]
    challenge_id: Optional[str]
    content: str
    quality_score: float
    community_impact: int
    reward_points: int
    badges_earned: List[str]
    created_at: datetime

@dataclass
class ResourceRequest:
    """Request for resource generation/recommendation."""
    
    parent_id: str
    student_id: str
    request_type: str  # "generate", "recommend", "search"
    resource_type: Optional[ResourceType] = None
    category: Optional[ResourceCategory] = None
    subject: Optional[str] = None
    difficulty_level: Optional[DifficultyLevel] = None
    age_group: Optional[str] = None
    language: str = "english"
    query: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    limit: int = 10

@dataclass
class ResourceResult:
    """Result from resource operation."""
    
    resources: List[Resource]
    total_found: int
    search_time_ms: int
    quality_filtered: bool
    personalized: bool
    recommendations: List[str]
    next_steps: List[str]

class ParentResourceLibraryService:
    """
    Service for AI-curated educational resource library.
    
    This service provides comprehensive resource management with AI-powered
    curation, personalization, and quality assessment.
    
    Attributes:
        unified_service: Unified Gemini configuration service
        ai_content_service: AI content generation service
        db: Firestore database client
        resource_curator: AI-powered resource curation
        quality_assessor: Resource quality assessment
        recommendation_engine: Personalized recommendation system
    
    Example:
        >>> service = ParentResourceLibraryService()
        >>> result = service.search_resources(
        ...     parent_id="parent123",
        ...     student_id="student123",
        ...     query="physics study tips"
        ... )
        >>> print(f"Found {len(result.resources)} resources")
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
        Initialize Parent Resource Library Service.
        
        Args:
            db: Firestore client (creates new if None)
            unified_config: Optional unified configuration
            enable_database_persistence: Enable saving to database
            cache_size: Maximum cache size
            cache_ttl_hours: Cache TTL in hours
        """
        logger.info("Initializing ParentResourceLibraryService")
        
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
        
        # Resource cache
        self.resource_cache: Dict[str, ResourceResult] = {}
        
        # Collections
        self.resources_collection = "parent_resources"
        self.resource_usage_collection = "resource_usage"
        self.community_resources_collection = "community_resources"
        self.community_challenges_collection = "community_challenges"
        self.parent_contributions_collection = "parent_contributions"
        self.resource_reviews_collection = "resource_reviews"
        
        # Supported languages
        self.supported_languages = [
            "english", "hindi", "spanish", "french", "german",
            "chinese", "japanese", "korean", "portuguese", "russian"
        ]
        
        # Quality assessment criteria
        self.quality_criteria = {
            "content_accuracy": 0.3,
            "educational_value": 0.25,
            "engagement_level": 0.2,
            "appropriateness": 0.15,
            "clarity": 0.1
        }
        
        # Metrics
        self.metrics = {
            "total_resources_generated": 0,
            "total_resources_recommended": 0,
            "total_searches": 0,
            "resources_by_type": {rt.value: 0 for rt in ResourceType},
            "resources_by_category": {rc.value: 0 for rc in ResourceCategory},
            "average_quality_score": 0.0,
            "total_downloads": 0,
            "user_satisfaction": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
            "database_saves": 0,
            "database_failures": 0,
            # Community metrics
            "community_resources_submitted": 0,
            "community_resources_approved": 0,
            "community_resources_pending": 0,
            "community_challenges_created": 0,
            "community_challenges_participated": 0,
            "parent_contributions": 0,
            "expert_verifications": 0,
            "community_engagement_score": 0.0,
            "total_community_likes": 0,
            "total_community_shares": 0
        }
        
        logger.info(
            f"ParentResourceLibraryService initialized (db_persistence={enable_database_persistence}, "
            f"cache_size={cache_size}, cache_ttl={cache_ttl_hours}h)"
        )
    
    async def generate_resource(
        self,
        request: ResourceRequest
    ) -> ResourceResult:
        """
        Generate AI-powered educational resource.
        
        Args:
            request: ResourceRequest with generation parameters
        
        Returns:
            ResourceResult with generated resource and metadata
        
        Raises:
            ValueError: If request is invalid
            Exception: If generation fails
        """
        start_time = time.time()
        
        logger.info(f"Generating resource for parent {request.parent_id}")
        
        try:
            # Check cache
            cache_key = self._generate_cache_key(request)
            if cache_key in self.resource_cache:
                cached_result = self.resource_cache[cache_key]
                logger.info(f"Cache hit for resource generation")
                
                # Update metrics
                self.metrics["cache_hits"] += 1
                
                return cached_result
            
            self.metrics["cache_misses"] += 1
            
            # Get student context for personalization
            student_context = await self._get_student_context(request.student_id)
            
            # Build prompt for resource generation
            prompt = self._build_resource_generation_prompt(
                request, student_context
            )
            
            # Generate resource using AI service
            content_request = ContentRequest(
                content_type=ContentType.LEARNING_MATERIAL,
                prompt=prompt,
                user_id=request.parent_id,
                student_id=request.student_id,
                context={
                    "request": request.__dict__,
                    "student_context": student_context
                },
                metadata={"generation_type": "resource_generation"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse generated resource
            resource = self._parse_generated_resource(result.content, request)
            
            # Assess quality
            quality_score = await self._assess_resource_quality(resource)
            
            # Create resource record
            resource_record = {
                "resource_id": f"res_{request.parent_id}_{int(time.time())}_{hashlib.md5(result.content.encode()).hexdigest()[:8]}",
                "parent_id": request.parent_id,
                "student_id": request.student_id,
                "title": resource.get("title", "Generated Resource"),
                "description": resource.get("description", ""),
                "resource_type": resource.get("resource_type", ResourceType.ARTICLE.value),
                "category": resource.get("category", ResourceCategory.STUDY_STRATEGIES.value),
                "subject": request.subject,
                "difficulty_level": resource.get("difficulty_level", DifficultyLevel.INTERMEDIATE.value),
                "age_group": resource.get("age_group", "middle_school"),
                "language": request.language,
                "content": resource.get("content", ""),
                "download_url": None,
                "tags": resource.get("tags", []),
                "quality_score": quality_score.value,
                "effectiveness_rating": 0.0,
                "usage_count": 0,
                "user_ratings": [],
                "ai_generated": True,
                "community_contributed": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Save to database
            if self.enable_database_persistence:
                await self._save_resource_to_db(resource_record)
            
            # Calculate generation time
            search_time_ms = int((time.time() - start_time) * 1000)
            
            # Create result
            resource_obj = Resource(**resource_record)
            result = ResourceResult(
                resources=[resource_obj],
                total_found=1,
                search_time_ms=search_time_ms,
                quality_filtered=True,
                personalized=True,
                recommendations=resource.get("recommendations", []),
                next_steps=resource.get("next_steps", [])
            )
            
            # Cache result
            if len(self.resource_cache) < self.cache_size:
                self.resource_cache[cache_key] = result
            
            # Update metrics
            self.metrics["total_resources_generated"] += 1
            self.metrics["resources_by_type"][resource_obj.resource_type.value] += 1
            self.metrics["resources_by_category"][resource_obj.category.value] += 1
            self._update_average_quality(quality_score)
            
            logger.info(f"Generated resource: {resource_obj.title}")
            return result
            
        except Exception as e:
            logger.error(f"Resource generation failed: {e}")
            
            # Update metrics
            if self.enable_database_persistence:
                self.metrics["database_failures"] += 1
            
            return ResourceResult(
                resources=[],
                total_found=0,
                search_time_ms=int((time.time() - start_time) * 1000),
                quality_filtered=False,
                personalized=False,
                recommendations=[],
                next_steps=[]
            )
    
    async def search_resources(
        self,
        request: ResourceRequest
    ) -> ResourceResult:
        """
        Search for educational resources with AI-powered filtering.
        
        Args:
            request: ResourceRequest with search parameters
        
        Returns:
            ResourceResult with matching resources and recommendations
        """
        start_time = time.time()
        
        logger.info(f"Searching resources for parent {request.parent_id}")
        
        try:
            # Check cache
            cache_key = self._generate_cache_key(request)
            if cache_key in self.resource_cache:
                cached_result = self.resource_cache[cache_key]
                logger.info(f"Cache hit for resource search")
                
                # Update metrics
                self.metrics["cache_hits"] += 1
                
                return cached_result
            
            self.metrics["cache_misses"] += 1
            
            # Build database query
            query = self._build_search_query(request)
            
            # Execute search
            resources = []
            async for doc in query.stream():
                resource_data = doc.to_dict()
                resources.append(Resource(**resource_data))
            
            # Apply AI-powered filtering and ranking
            filtered_resources = await self._apply_ai_filtering(resources, request)
            
            # Generate recommendations based on search
            recommendations = await self._generate_search_recommendations(
                request, filtered_resources
            )
            
            # Calculate search time
            search_time_ms = int((time.time() - start_time) * 1000)
            
            # Create result
            result = ResourceResult(
                resources=filtered_resources,
                total_found=len(filtered_resources),
                search_time_ms=search_time_ms,
                quality_filtered=True,
                personalized=request.context is not None,
                recommendations=recommendations,
                next_steps=await self._generate_next_steps(request, filtered_resources)
            )
            
            # Cache result
            if len(self.resource_cache) < self.cache_size:
                self.resource_cache[cache_key] = result
            
            # Update metrics
            self.metrics["total_searches"] += 1
            
            logger.info(f"Search completed: {len(filtered_resources)} resources found")
            return result
            
        except Exception as e:
            logger.error(f"Resource search failed: {e}")
            
            # Update metrics
            if self.enable_database_persistence:
                self.metrics["database_failures"] += 1
            
            return ResourceResult(
                resources=[],
                total_found=0,
                search_time_ms=int((time.time() - start_time) * 1000),
                quality_filtered=False,
                personalized=False,
                recommendations=[],
                next_steps=[]
            )
    
    async def recommend_resources(
        self,
        parent_id: str,
        student_id: str,
        context: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> ResourceResult:
        """
        Generate personalized resource recommendations.
        
        Args:
            parent_id: Parent ID
            student_id: Student ID
            context: Optional context for recommendations
            limit: Maximum number of recommendations
        
        Returns:
            ResourceResult with recommended resources
        """
        start_time = time.time()
        
        logger.info(f"Generating recommendations for parent {parent_id}")
        
        try:
            # Get student context and history
            student_context = await self._get_student_context(student_id)
            usage_history = await self._get_resource_usage_history(parent_id, student_id, 30)
            
            # Build prompt for recommendations
            prompt = self._build_recommendation_prompt(
                student_context, usage_history, context, limit
            )
            
            # Generate recommendations using AI service
            content_request = ContentRequest(
                content_type=ContentType.RECOMMENDATION,
                prompt=prompt,
                user_id=parent_id,
                student_id=student_id,
                context={
                    "student_context": student_context,
                    "usage_history": usage_history,
                    "additional_context": context
                },
                metadata={"generation_type": "resource_recommendations"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse recommendations
            recommended_resources = self._parse_recommendations(result.content)
            
            # Get full resource objects
            resource_ids = [r.get("resource_id") for r in recommended_resources]
            resources = await self._get_resources_by_ids(resource_ids)
            
            # Calculate generation time
            search_time_ms = int((time.time() - start_time) * 1000)
            
            # Create result
            resource_result = ResourceResult(
                resources=resources,
                total_found=len(resources),
                search_time_ms=search_time_ms,
                quality_filtered=True,
                personalized=True,
                recommendations=await self._generate_recommendation_insights(
                    student_context, usage_history, resources
                ),
                next_steps=await self._generate_next_steps_from_recommendations(resources)
            )
            
            # Update metrics
            self.metrics["total_resources_recommended"] += 1
            
            logger.info(f"Generated {len(resources)} recommendations")
            return resource_result
            
        except Exception as e:
            logger.error(f"Resource recommendation failed: {e}")
            
            # Update metrics
            if self.enable_database_persistence:
                self.metrics["database_failures"] += 1
            
            return ResourceResult(
                resources=[],
                total_found=0,
                search_time_ms=int((time.time() - start_time) * 1000),
                quality_filtered=False,
                personalized=False,
                recommendations=[],
                next_steps=[]
            )
    
    async def rate_resource(
        self,
        resource_id: str,
        parent_id: str,
        rating: float,
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Rate a resource and update its effectiveness.
        
        Args:
            resource_id: Resource ID
            parent_id: Parent ID providing rating
            rating: Rating score (1-5)
            feedback: Optional feedback text
        
        Returns:
            Dict with rating results
        """
        try:
            # Get resource
            resource = await self._get_resource_by_id(resource_id)
            if not resource:
                return {
                    "success": False,
                    "error": "Resource not found"
                }
            
            # Validate rating
            if not 1 <= rating <= 5:
                return {
                    "success": False,
                    "error": "Rating must be between 1 and 5"
                }
            
            # Update resource ratings
            new_ratings = resource.user_ratings + [rating]
            new_effectiveness = sum(new_ratings) / len(new_ratings)
            
            # Update usage record
            usage_record = {
                "usage_id": f"usage_{parent_id}_{resource_id}_{int(time.time())}",
                "parent_id": parent_id,
                "resource_id": resource_id,
                "rating": rating,
                "feedback": feedback,
                "used_at": datetime.utcnow(),
                "effectiveness_at_time": new_effectiveness
            }
            
            # Update resource in database
            resource_update = {
                "user_ratings": new_ratings,
                "effectiveness_rating": new_effectiveness,
                "usage_count": resource.usage_count + 1,
                "updated_at": datetime.utcnow()
            }
            
            if self.enable_database_persistence:
                await self._save_resource_usage(usage_record)
                await self._update_resource_in_db(resource_id, resource_update)
            
            result = {
                "success": True,
                "resource_id": resource_id,
                "new_rating": rating,
                "new_average_rating": new_effectiveness,
                "total_ratings": len(new_ratings),
                "usage_count": resource.usage_count + 1
            }
            
            logger.info(f"Rated resource {resource_id}: {rating}")
            return result
            
        except Exception as e:
            logger.error(f"Resource rating failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_resource_analytics(
        self,
        resource_id: str,
        time_period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get analytics for a specific resource.
        
        Args:
            resource_id: Resource ID
            time_period_days: Period to analyze
        
        Returns:
            Dict with resource analytics and insights
        """
        try:
            # Get resource details
            resource = await self._get_resource_by_id(resource_id)
            if not resource:
                return {
                    "success": False,
                    "error": "Resource not found"
                }
            
            # Get usage history
            usage_history = await self._get_resource_usage_analytics(
                resource_id, time_period_days
            )
            
            # Calculate analytics
            analytics = self._calculate_resource_analytics(resource, usage_history)
            
            # Generate insights
            insights = await self._generate_resource_insights(resource, analytics)
            
            result = {
                "success": True,
                "resource_id": resource_id,
                "resource": resource.__dict__,
                "period_days": time_period_days,
                "analytics": analytics,
                "insights": insights,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Generated analytics for resource {resource_id}")
            return result
            
        except Exception as e:
            logger.error(f"Resource analytics failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "resource_id": resource_id
            }
    
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
            "service": "parent_resource_library_service",
            "metrics": self.metrics,
            "derived": {
                "cache_hit_rate": cache_hit_rate,
                "average_quality_score": self.metrics["average_quality_score"],
                "database_success_rate": (
                    (self.metrics["database_saves"] / 
                     max(self.metrics["database_saves"] + self.metrics["database_failures"], 1)) * 100
                )
            },
            "resource_type_breakdown": {
                rt: count for rt, count in self.metrics["resources_by_type"].items()
            },
            "category_breakdown": {
                rc: count for rc, count in self.metrics["resources_by_category"].items()
            },
            "supported_languages": self.supported_languages,
            "quality_criteria": self.quality_criteria
        }
    
    # ========================================================================
    # PRIVATE METHODS
    # ========================================================================
    
    def _generate_cache_key(self, request: ResourceRequest) -> str:
        """Generate cache key for resource request."""
        key_data = {
            "parent_id": request.parent_id,
            "student_id": request.student_id,
            "request_type": request.request_type,
            "resource_type": request.resource_type.value if request.resource_type else None,
            "category": request.category.value if request.category else None,
            "subject": request.subject,
            "difficulty_level": request.difficulty_level.value if request.difficulty_level else None,
            "language": request.language,
            "query": request.query,
            "limit": request.limit
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    async def _get_student_context(self, student_id: str) -> Dict[str, Any]:
        """Get student context for resource personalization."""
        try:
            # This would typically fetch from student profiles, performance data, etc.
            # For now, return basic context
            return {
                "student_id": student_id,
                "age_group": "middle_school",  # This would be calculated
                "current_subjects": ["Mathematics", "Physics", "Chemistry"],
                "performance_level": "intermediate",
                "learning_style": "visual",  # This would be assessed
                "interests": ["Science", "Technology"],
                "challenges": ["Time management", "Concept understanding"]
            }
            
        except Exception as e:
            logger.error(f"Failed to get student context: {e}")
            return {"student_id": student_id, "error": str(e)}
    
    async def _get_resource_usage_history(
        self,
        parent_id: str,
        student_id: str,
        days: int
    ) -> List[Dict[str, Any]]:
        """Get resource usage history."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            query = self.db.collection(self.resource_usage_collection)\
                .where("parent_id", "==", parent_id)\
                .where("student_id", "==", student_id)\
                .where("used_at", ">=", start_date)\
                .where("used_at", "<=", end_date)\
                .order_by("used_at", direction="DESCENDING")
            
            history = []
            async for doc in query.stream():
                history.append(doc.to_dict())
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get resource usage history: {e}")
            return []
    
    def _build_resource_generation_prompt(
        self,
        request: ResourceRequest,
        student_context: Dict[str, Any]
    ) -> str:
        """Build prompt for resource generation."""
        return f"""
Generate an educational resource for parent-child learning.

Request Details:
- Type: {request.resource_type.value if request.resource_type else 'any'}
- Category: {request.category.value if request.category else 'any'}
- Subject: {request.subject or 'general'}
- Difficulty: {request.difficulty_level.value if request.difficulty_level else 'intermediate'}
- Language: {request.language}
- Query: {request.query or ''}

Student Context:
{json.dumps(student_context, indent=2)}

Requirements:
1. Create high-quality, educational content
2. Make it appropriate for the specified age group and difficulty
3. Include practical examples and exercises
4. Ensure it's engaging and interactive
5. Provide clear learning objectives
6. Include assessment or practice components

Format as JSON:
{{
    "title": "Resource Title",
    "description": "Detailed description",
    "resource_type": "{request.resource_type.value if request.resource_type else 'article'}",
    "category": "{request.category.value if request.category else 'study_strategies'}",
    "difficulty_level": "{request.difficulty_level.value if request.difficulty_level else 'intermediate'}",
    "age_group": "appropriate age group",
    "content": "Full educational content",
    "tags": ["tag1", "tag2", "tag3"],
    "recommendations": ["next_step1", "next_step2"],
    "next_steps": ["action1", "action2"]
}}
"""
    
    def _parse_generated_resource(self, content: str, request: ResourceRequest) -> Dict[str, Any]:
        """Parse generated resource from AI response."""
        try:
            # Try to parse as JSON
            import json
            resource_data = json.loads(content)
            
            if isinstance(resource_data, dict):
                return resource_data
            else:
                # Fallback: return as basic resource
                return {
                    "title": "Generated Resource",
                    "description": content,
                    "resource_type": request.resource_type.value if request.resource_type else ResourceType.ARTICLE.value,
                    "category": request.category.value if request.category else ResourceCategory.STUDY_STRATEGIES.value,
                    "difficulty_level": request.difficulty_level.value if request.difficulty_level else DifficultyLevel.INTERMEDIATE.value,
                    "age_group": "middle_school",
                    "content": content,
                    "tags": ["generated"],
                    "recommendations": ["Review and practice"],
                    "next_steps": ["Apply learning"]
                }
                
        except json.JSONDecodeError:
            # Fallback: return basic resource
            return {
                "title": "Generated Resource",
                "description": content,
                "resource_type": request.resource_type.value if request.resource_type else ResourceType.ARTICLE.value,
                "category": request.category.value if request.category else ResourceCategory.STUDY_STRATEGIES.value,
                "difficulty_level": request.difficulty_level.value if request.difficulty_level else DifficultyLevel.INTERMEDIATE.value,
                "age_group": "middle_school",
                "content": content,
                "tags": ["generated"],
                "recommendations": ["Review and practice"],
                "next_steps": ["Apply learning"]
            }
    
    async def _assess_resource_quality(self, resource: Dict[str, Any]) -> QualityScore:
        """Assess quality of generated resource."""
        try:
            # Build prompt for quality assessment
            prompt = f"""
Assess the quality of this educational resource.

Resource Content:
{json.dumps(resource, indent=2)}

Quality Criteria:
- Content Accuracy (30%): Factual correctness
- Educational Value (25%): Learning effectiveness
- Engagement Level (20%): Interest and interaction
- Appropriateness (15%): Age and level suitability
- Clarity (10%): Clear explanations

Requirements:
1. Assess each criterion on a scale of 1-10
2. Calculate weighted overall score
3. Provide quality level (excellent/good/average/poor)
4. Include specific feedback

Format as JSON:
{{
    "content_accuracy": 8,
    "educational_value": 7,
    "engagement_level": 6,
    "appropriateness": 8,
    "clarity": 7,
    "overall_score": 7.1,
    "quality_level": "good",
    "feedback": "Specific feedback for improvement"
}}
"""
            
            # Generate quality assessment using AI service
            content_request = ContentRequest(
                content_type=ContentType.ANALYSIS,
                prompt=prompt,
                user_id="system",
                student_id="system",
                context={"resource": resource},
                metadata={"generation_type": "quality_assessment"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse quality assessment
            try:
                import json
                quality_data = json.loads(result.content)
                
                if isinstance(quality_data, dict):
                    overall_score = quality_data.get("overall_score", 5.0)
                    
                    if overall_score >= 8.5:
                        return QualityScore.EXCELLENT
                    elif overall_score >= 6.5:
                        return QualityScore.GOOD
                    elif overall_score >= 4.5:
                        return QualityScore.AVERAGE
                    else:
                        return QualityScore.POOR
                        
            except json.JSONDecodeError:
                pass
            
            # Default to good if assessment fails
            return QualityScore.GOOD
            
        except Exception as e:
            logger.error(f"Failed to assess resource quality: {e}")
            return QualityScore.AVERAGE
    
    def _update_average_quality(self, quality_score: QualityScore):
        """Update running average quality score."""
        # Convert quality to numeric score
        quality_values = {
            QualityScore.EXCELLENT: 9.0,
            QualityScore.GOOD: 7.0,
            QualityScore.AVERAGE: 5.0,
            QualityScore.POOR: 3.0
        }
        
        numeric_score = quality_values.get(quality_score, 5.0)
        
        total_resources = self.metrics["total_resources_generated"] + self.metrics["total_resources_recommended"]
        if total_resources > 0:
            current_avg = self.metrics["average_quality_score"]
            self.metrics["average_quality_score"] = (
                (current_avg * (total_resources - 1) + numeric_score) / total_resources
            )
    
    async def _save_resource_to_db(self, resource_record: Dict[str, Any]):
        """Save resource to database."""
        try:
            doc_ref = self.db.collection(self.resources_collection).document(resource_record["resource_id"])
            await doc_ref.set(resource_record)
            logger.debug(f"Saved resource to database: {resource_record['resource_id']}")
            
        except Exception as e:
            logger.error(f"Failed to save resource to database: {e}")
            self.metrics["database_failures"] += 1
    
    def _build_search_query(self, request: ResourceRequest):
        """Build Firestore query for resource search."""
        query = self.db.collection(self.resources_collection)
        
        # Add filters
        if request.resource_type:
            query = query.where("resource_type", "==", request.resource_type.value)
        
        if request.category:
            query = query.where("category", "==", request.category.value)
        
        if request.subject:
            query = query.where("subject", "==", request.subject)
        
        if request.difficulty_level:
            query = query.where("difficulty_level", "==", request.difficulty_level.value)
        
        if request.language:
            query = query.where("language", "==", request.language)
        
        # Add text search if query provided
        if request.query:
            # This would typically use a full-text search index
            # For now, we'll do a basic filter
            query = query.where("tags", "array_contains", [request.query])
        
        # Add limit
        query = query.limit(request.limit)
        
        # Order by quality and usage
        query = query.order_by("effectiveness_rating", direction="DESCENDING")
        
        return query
    
    async def _apply_ai_filtering(
        self,
        resources: List[Resource],
        request: ResourceRequest
    ) -> List[Resource]:
        """Apply AI-powered filtering and ranking to resources."""
        try:
            if not resources:
                return []
            
            # Build prompt for AI filtering
            prompt = f"""
Filter and rank these educational resources based on the request.

Request:
{json.dumps(request.__dict__, indent=2)}

Resources:
{json.dumps([r.__dict__ for r in resources[:10]], indent=2)}

Requirements:
1. Filter by relevance to request
2. Consider quality and effectiveness
3. Personalize based on context if provided
4. Rank by overall suitability
5. Return top {len(resources)} resources

Format as JSON array of resource IDs in ranking order:
["resource_id1", "resource_id2", ...]
"""
            
            # Generate filtering using AI service
            content_request = ContentRequest(
                content_type=ContentType.ANALYSIS,
                prompt=prompt,
                user_id=request.parent_id,
                student_id=request.student_id,
                context={"request": request.__dict__, "resources": [r.__dict__ for r in resources]},
                metadata={"generation_type": "ai_filtering"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse filtered resource IDs
            try:
                import json
                filtered_ids = json.loads(result.content)
                
                if isinstance(filtered_ids, list):
                    # Create resource map for quick lookup
                    resource_map = {r.resource_id: r for r in resources}
                    
                    # Return filtered resources in ranking order
                    filtered_resources = []
                    for resource_id in filtered_ids:
                        if resource_id in resource_map:
                            filtered_resources.append(resource_map[resource_id])
                    
                    return filtered_resources
                    
            except json.JSONDecodeError:
                pass
            
            # Fallback: return original resources
            return resources
            
        except Exception as e:
            logger.error(f"AI filtering failed: {e}")
            return resources
    
    async def _generate_search_recommendations(
        self,
        request: ResourceRequest,
        resources: List[Resource]
    ) -> List[str]:
        """Generate recommendations based on search results."""
        try:
            # Build prompt for recommendations
            prompt = f"""
Generate recommendations based on these search results.

Search Request:
{json.dumps(request.__dict__, indent=2)}

Found Resources:
{json.dumps([r.__dict__ for r in resources[:5]], indent=2)}

Requirements:
1. Analyze gaps in search results
2. Suggest related topics or resources
3. Provide alternative approaches
4. Recommend next steps
5. Consider user's context and needs

Format as JSON array of strings:
[
    "recommendation 1",
    "recommendation 2",
    ...
]
"""
            
            # Generate recommendations using AI service
            content_request = ContentRequest(
                content_type=ContentType.RECOMMENDATION,
                prompt=prompt,
                user_id=request.parent_id,
                student_id=request.student_id,
                context={"request": request.__dict__, "resources": [r.__dict__ for r in resources]},
                metadata={"generation_type": "search_recommendations"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse recommendations
            try:
                import json
                recommendations = json.loads(result.content)
                
                if isinstance(recommendations, list):
                    return [str(rec) for rec in recommendations]
                    
            except json.JSONDecodeError:
                pass
            
            # Fallback: return basic recommendations
            return [
                "Try different search terms",
                "Explore related categories",
                "Check resource effectiveness ratings"
            ]
            
        except Exception as e:
            logger.error(f"Search recommendations failed: {e}")
            return ["Unable to generate recommendations"]
    
    async def _generate_next_steps(
        self,
        request: ResourceRequest,
        resources: List[Resource]
    ) -> List[str]:
        """Generate next steps based on resources found."""
        try:
            # Build prompt for next steps
            prompt = f"""
Generate next steps based on these resources.

Request:
{json.dumps(request.__dict__, indent=2)}

Resources:
{json.dumps([r.__dict__ for r in resources[:3]], indent=2)}

Requirements:
1. Suggest how to use these resources effectively
2. Provide implementation guidance
3. Recommend complementary activities
4. Suggest follow-up resources
5. Include practical tips

Format as JSON array of strings:
[
    "next step 1",
    "next step 2",
    ...
]
"""
            
            # Generate next steps using AI service
            content_request = ContentRequest(
                content_type=ContentType.RECOMMENDATION,
                prompt=prompt,
                user_id=request.parent_id,
                student_id=request.student_id,
                context={"request": request.__dict__, "resources": [r.__dict__ for r in resources]},
                metadata={"generation_type": "next_steps"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse next steps
            try:
                import json
                next_steps = json.loads(result.content)
                
                if isinstance(next_steps, list):
                    return [str(step) for step in next_steps]
                    
            except json.JSONDecodeError:
                pass
            
            # Fallback: return basic next steps
            return [
                "Download and review resources",
                "Create learning schedule",
                "Track progress and effectiveness"
            ]
            
        except Exception as e:
            logger.error(f"Next steps generation failed: {e}")
            return ["Review available resources"]
    
    async def _get_resources_by_ids(self, resource_ids: List[str]) -> List[Resource]:
        """Get resources by their IDs."""
        try:
            if not resource_ids:
                return []
            
            # Batch get resources
            resources = []
            for resource_id in resource_ids:
                doc_ref = self.db.collection(self.resources_collection).document(resource_id)
                doc = await doc_ref.get()
                
                if doc.exists:
                    resource_data = doc.to_dict()
                    resources.append(Resource(**resource_data))
            
            return resources
            
        except Exception as e:
            logger.error(f"Failed to get resources by IDs: {e}")
            return []
    
    def _build_recommendation_prompt(
        self,
        student_context: Dict[str, Any],
        usage_history: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]],
        limit: int
    ) -> str:
        """Build prompt for resource recommendations."""
        return f"""
Generate personalized resource recommendations.

Student Context:
{json.dumps(student_context, indent=2)}

Usage History:
{json.dumps(usage_history[:5], indent=2)}

Additional Context:
{json.dumps(context or {}, indent=2)}

Requirements:
1. Analyze learning patterns and preferences
2. Identify gaps in current resources
3. Recommend specific, actionable resources
4. Consider effectiveness of past resources
5. Personalize for student's needs
6. Limit to {limit} high-quality recommendations

Format as JSON array of resource recommendations:
[
    {{
        "resource_id": "suggested_id_1",
        "title": "Resource Title 1",
        "description": "Why this resource is recommended",
        "priority": "high|medium|low",
        "reason": "Specific reason for recommendation"
    }},
    ...
]
"""
    
    def _parse_recommendations(self, content: str) -> List[Dict[str, Any]]:
        """Parse recommendations from AI response."""
        try:
            # Try to parse as JSON
            import json
            recommendations = json.loads(content)
            
            if isinstance(recommendations, list):
                return recommendations
            else:
                # Fallback: return as single recommendation
                return [{
                    "resource_id": "recommended",
                    "title": "Recommended Resource",
                    "description": content,
                    "priority": "medium",
                    "reason": "Based on analysis"
                }]
                
        except json.JSONDecodeError:
            # Fallback: return basic recommendation
            return [{
                "resource_id": "recommended",
                "title": "Recommended Resource",
                "description": content,
                "priority": "medium",
                "reason": "Based on analysis"
            }]
    
    async def _generate_recommendation_insights(
        self,
        student_context: Dict[str, Any],
        usage_history: List[Dict[str, Any]],
        resources: List[Resource]
    ) -> List[str]:
        """Generate insights about recommendations."""
        try:
            # Build prompt for insights
            prompt = f"""
Generate insights about these resource recommendations.

Student Context:
{json.dumps(student_context, indent=2)}

Usage History:
{json.dumps(usage_history[:3], indent=2)}

Recommended Resources:
{json.dumps([r.__dict__ for r in resources[:3]], indent=2)}

Requirements:
1. Analyze recommendation patterns
2. Identify learning opportunities
3. Highlight potential challenges
4. Suggest optimization strategies
5. Provide actionable insights

Format as JSON array of strings:
[
    "insight 1",
    "insight 2",
    ...
]
"""
            
            # Generate insights using AI service
            content_request = ContentRequest(
                content_type=ContentType.INSIGHT,
                prompt=prompt,
                user_id="system",
                student_id="system",
                context={
                    "student_context": student_context,
                    "usage_history": usage_history,
                    "resources": [r.__dict__ for r in resources]
                },
                metadata={"generation_type": "recommendation_insights"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse insights
            try:
                import json
                insights = json.loads(result.content)
                
                if isinstance(insights, list):
                    return [str(insight) for insight in insights]
                    
            except json.JSONDecodeError:
                pass
            
            # Fallback: return basic insights
            return [
                "Resources selected based on learning patterns",
                "Focus on consistent usage for best results"
            ]
            
        except Exception as e:
            logger.error(f"Recommendation insights failed: {e}")
            return ["Unable to generate insights"]
    
    async def _generate_next_steps_from_recommendations(
        self,
        resources: List[Resource]
    ) -> List[str]:
        """Generate next steps from recommendations."""
        try:
            # Build prompt for next steps
            prompt = f"""
Generate next steps for these recommended resources.

Resources:
{json.dumps([r.__dict__ for r in resources[:3]], indent=2)}

Requirements:
1. Suggest implementation order
2. Provide integration tips
3. Recommend complementary activities
4. Suggest tracking methods
5. Include timeline suggestions

Format as JSON array of strings:
[
    "next step 1",
    "next step 2",
    ...
]
"""
            
            # Generate next steps using AI service
            content_request = ContentRequest(
                content_type=ContentType.RECOMMENDATION,
                prompt=prompt,
                user_id="system",
                student_id="system",
                context={"resources": [r.__dict__ for r in resources]},
                metadata={"generation_type": "recommendation_next_steps"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse next steps
            try:
                import json
                next_steps = json.loads(result.content)
                
                if isinstance(next_steps, list):
                    return [str(step) for step in next_steps]
                    
            except json.JSONDecodeError:
                pass
            
            # Fallback: return basic next steps
            return [
                "Start with highest priority resource",
                "Create implementation schedule",
                "Set up tracking and review process"
            ]
            
        except Exception as e:
            logger.error(f"Next steps from recommendations failed: {e}")
            return ["Review and implement recommended resources"]
    
    async def _get_resource_by_id(self, resource_id: str) -> Optional[Resource]:
        """Get resource by ID."""
        try:
            doc_ref = self.db.collection(self.resources_collection).document(resource_id)
            doc = await doc_ref.get()
            
            if doc.exists:
                resource_data = doc.to_dict()
                return Resource(**resource_data)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get resource by ID: {e}")
            return None
    
    async def _save_resource_usage(self, usage_record: Dict[str, Any]):
        """Save resource usage record."""
        try:
            doc_ref = self.db.collection(self.resource_usage_collection).document(usage_record["usage_id"])
            await doc_ref.set(usage_record)
            logger.debug(f"Saved resource usage: {usage_record['usage_id']}")
            
        except Exception as e:
            logger.error(f"Failed to save resource usage: {e}")
            self.metrics["database_failures"] += 1
    
    async def _update_resource_in_db(self, resource_id: str, update_data: Dict[str, Any]):
        """Update resource in database."""
        try:
            doc_ref = self.db.collection(self.resources_collection).document(resource_id)
            await doc_ref.update(update_data)
            logger.debug(f"Updated resource in database: {resource_id}")
            
        except Exception as e:
            logger.error(f"Failed to update resource in database: {e}")
            self.metrics["database_failures"] += 1
    
    async def _get_resource_usage_analytics(
        self,
        resource_id: str,
        days: int
    ) -> List[Dict[str, Any]]:
        """Get resource usage analytics."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            query = self.db.collection(self.resource_usage_collection)\
                .where("resource_id", "==", resource_id)\
                .where("used_at", ">=", start_date)\
                .where("used_at", "<=", end_date)\
                .order_by("used_at", direction="DESCENDING")
            
            analytics = []
            async for doc in query.stream():
                analytics.append(doc.to_dict())
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get resource usage analytics: {e}")
            return []
    
    def _calculate_resource_analytics(
        self,
        resource: Resource,
        usage_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate analytics for a resource."""
        if not usage_history:
            return {
                "total_usage": 0,
                "average_rating": 0.0,
                "usage_frequency": 0.0,
                "effectiveness_trend": "stable"
            }
        
        # Calculate basic metrics
        total_usage = len(usage_history)
        ratings = [usage.get("rating", 0) for usage in usage_history if usage.get("rating")]
        average_rating = sum(ratings) / len(ratings) if ratings else 0.0
        
        # Calculate usage frequency
        if total_usage > 0:
            first_use = usage_history[-1].get("used_at")
            last_use = usage_history[0].get("used_at")
            days_span = (last_use - first_use).days if first_use and last_use else 1
            usage_frequency = total_usage / max(days_span, 1)
        else:
            usage_frequency = 0.0
        
        # Calculate effectiveness trend
        effectiveness_scores = [
            usage.get("effectiveness_at_time", 0) 
            for usage in usage_history 
            if usage.get("effectiveness_at_time")
        ]
        
        if len(effectiveness_scores) > 1:
            recent_avg = sum(effectiveness_scores[:5]) / min(5, len(effectiveness_scores))
            older_avg = sum(effectiveness_scores[5:]) / max(len(effectiveness_scores) - 5, 1)
            
            if recent_avg > older_avg:
                trend = "improving"
            elif recent_avg < older_avg:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "total_usage": total_usage,
            "average_rating": average_rating,
            "usage_frequency": usage_frequency,
            "effectiveness_trend": trend,
            "rating_distribution": self._calculate_rating_distribution(ratings),
            "usage_by_day": self._calculate_usage_by_day(usage_history)
        }
    
    def _calculate_rating_distribution(self, ratings: List[float]) -> Dict[str, int]:
        """Calculate distribution of ratings."""
        if not ratings:
            return {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
        
        distribution = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
        for rating in ratings:
            rating_key = str(int(rating))
            if rating_key in distribution:
                distribution[rating_key] += 1
        
        return distribution
    
    def _calculate_usage_by_day(self, usage_history: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate usage distribution by day of week."""
        usage_by_day = {
            "Monday": 0, "Tuesday": 0, "Wednesday": 0, "Thursday": 0,
            "Friday": 0, "Saturday": 0, "Sunday": 0
        }
        
        for usage in usage_history:
            used_at = usage.get("used_at")
            if used_at:
                day_name = used_at.strftime("%A")
                if day_name in usage_by_day:
                    usage_by_day[day_name] += 1
        
        return usage_by_day
    
    async def _generate_resource_insights(
        self,
        resource: Resource,
        analytics: Dict[str, Any]
    ) -> List[str]:
        """Generate insights about resource performance."""
        try:
            # Build prompt for insights
            prompt = f"""
        Generate insights about this resource's performance.
        
        Resource:
        {json.dumps(resource.__dict__, indent=2)}
        
        Analytics:
        {json.dumps(analytics, indent=2)}
        
        Requirements:
        1. Analyze usage patterns and effectiveness
        2. Identify strengths and weaknesses
        3. Compare with similar resources
        4. Suggest improvements
        5. Provide actionable recommendations
        
        Format as JSON array of strings:
        [
            "insight 1",
            "insight 2",
            ...
        ]
        """
            
            # Generate insights using AI service
            content_request = ContentRequest(
                content_type=ContentType.INSIGHT,
                prompt=prompt,
                user_id="system",
                student_id="system",
                context={"resource": resource.__dict__, "analytics": analytics},
                metadata={"generation_type": "resource_insights"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse insights
            try:
                import json
                insights = json.loads(result.content)
                
                if isinstance(insights, list):
                    return [str(insight) for insight in insights]
                    
            except json.JSONDecodeError:
                pass
            
            # Fallback: return basic insights
            return [
                "Resource shows consistent usage patterns",
                "Consider updating content based on feedback",
                "Effectiveness rating is above average"
            ]
            
        except Exception as e:
            logger.error(f"Resource insights generation failed: {e}")
            return ["Unable to generate insights at this time"]
    
    # ========================================================================
    # COMMUNITY FEATURES METHODS
    # ========================================================================
    
    async def submit_community_resource(
        self,
        parent_id: str,
        resource_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit a community-contributed resource for moderation.
        
        Args:
            parent_id: Parent ID submitting the resource
            resource_data: Resource data including content, title, etc.
        
        Returns:
            Dict with submission results and resource ID
        """
        try:
            # Generate resource ID
            resource_id = f"community_{parent_id}_{int(time.time())}_{hashlib.md5(resource_data.get('title', '').encode()).hexdigest()[:8]}"
            
            logger.info(f"Submitting community resource: {resource_id}")
            
            # Assess quality automatically
            quality_score = await self._assess_community_resource_quality(resource_data)
            
            # Create community resource record
            community_resource = CommunityResource(
                resource_id=resource_id,
                parent_id=parent_id,
                title=resource_data.get("title", ""),
                description=resource_data.get("description", ""),
                resource_type=ResourceType(resource_data.get("resource_type", "article")),
                category=ResourceCategory(resource_data.get("category", "study_strategies")),
                subject=resource_data.get("subject"),
                difficulty_level=DifficultyLevel(resource_data.get("difficulty_level", "intermediate")),
                age_group=resource_data.get("age_group", "middle_school"),
                language=resource_data.get("language", "english"),
                content=resource_data.get("content", ""),
                download_url=resource_data.get("download_url"),
                tags=resource_data.get("tags", []),
                quality_score=quality_score,
                effectiveness_rating=0.0,
                usage_count=0,
                user_ratings=[],
                reviews=[],
                expert_verified=False,
                expert_badge=None,
                community_likes=0,
                community_shares=0,
                moderation_status="pending",
                moderation_notes=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Save to database
            if self.enable_database_persistence:
                await self._save_community_resource_to_db(community_resource)
            
            # Track parent contribution
            await self._track_parent_contribution(
                parent_id, "resource", resource_id, resource_data.get("content", "")
            )
            
            # Update metrics
            self.metrics["community_resources_submitted"] += 1
            self.metrics["community_resources_pending"] += 1
            
            result = {
                "success": True,
                "resource_id": resource_id,
                "moderation_status": "pending",
                "quality_score": quality_score.value,
                "message": "Resource submitted successfully. Pending moderation review.",
                "estimated_review_time": "24-48 hours"
            }
            
            logger.info(f"Community resource submitted: {resource_id}")
            return result
            
        except Exception as e:
            logger.error(f"Community resource submission failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to submit resource. Please try again."
            }
    
    async def moderate_community_resource(
        self,
        resource_id: str,
        moderator_id: str,
        action: str,  # "approve", "reject", "request_changes"
        moderation_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Moderate a community-submitted resource.
        
        Args:
            resource_id: Resource ID to moderate
            moderator_id: Moderator ID
            action: Moderation action
            moderation_notes: Optional moderation notes
        
        Returns:
            Dict with moderation results
        """
        try:
            # Get resource
            resource = await self._get_community_resource_by_id(resource_id)
            if not resource:
                return {
                    "success": False,
                    "error": "Resource not found"
                }
            
            # Update moderation status
            resource.moderation_status = action
            resource.moderation_notes = moderation_notes
            resource.updated_at = datetime.utcnow()
            
            # If approved, add to main resource library
            if action == "approve":
                resource.expert_verified = True
                resource.expert_badge = "community_approved"
                
                # Add to main resources collection
                main_resource = {
                    "resource_id": resource.resource_id,
                    "parent_id": resource.parent_id,
                    "title": resource.title,
                    "description": resource.description,
                    "resource_type": resource.resource_type.value,
                    "category": resource.category.value,
                    "subject": resource.subject,
                    "difficulty_level": resource.difficulty_level.value,
                    "age_group": resource.age_group,
                    "language": resource.language,
                    "content": resource.content,
                    "download_url": resource.download_url,
                    "tags": resource.tags,
                    "quality_score": resource.quality_score.value,
                    "effectiveness_rating": resource.effectiveness_rating,
                    "usage_count": resource.usage_count,
                    "user_ratings": resource.user_ratings,
                    "ai_generated": False,
                    "community_contributed": True,
                    "created_at": resource.created_at,
                    "updated_at": resource.updated_at
                }
                
                if self.enable_database_persistence:
                    await self._save_resource_to_db(main_resource)
                
                # Update metrics
                self.metrics["community_resources_approved"] += 1
                self.metrics["community_resources_pending"] -= 1
                self.metrics["expert_verifications"] += 1
                
                # Notify resource contributor
                await self._notify_resource_approval(resource.parent_id, resource_id)
                
            elif action == "reject":
                # Update metrics
                self.metrics["community_resources_pending"] -= 1
                
                # Notify resource contributor
                await self._notify_resource_rejection(resource.parent_id, resource_id, moderation_notes)
            
            # Save updated community resource
            if self.enable_database_persistence:
                await self._update_community_resource_in_db(resource_id, resource.__dict__)
            
            result = {
                "success": True,
                "resource_id": resource_id,
                "action": action,
                "moderation_notes": moderation_notes,
                "message": f"Resource {action}d successfully"
            }
            
            logger.info(f"Community resource moderated: {resource_id} - {action}")
            return result
            
        except Exception as e:
            logger.error(f"Resource moderation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to moderate resource"
            }
    
    async def create_community_challenge(
        self,
        challenge_data: Dict[str, Any],
        creator_id: str
    ) -> Dict[str, Any]:
        """
        Create a community challenge.
        
        Args:
            challenge_data: Challenge details
            creator_id: Creator's parent ID
        
        Returns:
            Dict with challenge creation results
        """
        try:
            # Generate challenge ID
            challenge_id = f"challenge_{creator_id}_{int(time.time())}_{hashlib.md5(challenge_data.get('title', '').encode()).hexdigest()[:8]}"
            
            logger.info(f"Creating community challenge: {challenge_id}")
            
            # Create challenge record
            challenge = CommunityChallenge(
                challenge_id=challenge_id,
                title=challenge_data.get("title", ""),
                description=challenge_data.get("description", ""),
                challenge_type=challenge_data.get("challenge_type", "resource_creation"),
                category=ResourceCategory(challenge_data.get("category", "study_strategies")),
                subject=challenge_data.get("subject"),
                difficulty_level=DifficultyLevel(challenge_data.get("difficulty_level", "intermediate")),
                start_date=datetime.fromisoformat(challenge_data.get("start_date", datetime.utcnow().isoformat())),
                end_date=datetime.fromisoformat(challenge_data.get("end_date", (datetime.utcnow() + timedelta(days=30)).isoformat())),
                participation_count=0,
                reward_points=challenge_data.get("reward_points", 100),
                reward_badge=challenge_data.get("reward_badge", "challenge_winner"),
                requirements=challenge_data.get("requirements", []),
                evaluation_criteria=challenge_data.get("evaluation_criteria", []),
                created_at=datetime.utcnow()
            )
            
            # Save to database
            if self.enable_database_persistence:
                await self._save_community_challenge_to_db(challenge)
            
            # Update metrics
            self.metrics["community_challenges_created"] += 1
            
            result = {
                "success": True,
                "challenge_id": challenge_id,
                "title": challenge.title,
                "start_date": challenge.start_date.isoformat(),
                "end_date": challenge.end_date.isoformat(),
                "reward_points": challenge.reward_points,
                "message": "Community challenge created successfully"
            }
            
            logger.info(f"Community challenge created: {challenge_id}")
            return result
            
        except Exception as e:
            logger.error(f"Community challenge creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create challenge"
            }
    
    async def participate_in_challenge(
        self,
        parent_id: str,
        challenge_id: str,
        participation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Participate in a community challenge.
        
        Args:
            parent_id: Parent ID participating
            challenge_id: Challenge ID
            participation_data: Participation details
        
        Returns:
            Dict with participation results
        """
        try:
            # Get challenge
            challenge = await self._get_community_challenge_by_id(challenge_id)
            if not challenge:
                return {
                    "success": False,
                    "error": "Challenge not found"
                }
            
            # Check if challenge is still active
            if datetime.utcnow() > challenge.end_date:
                return {
                    "success": False,
                    "error": "Challenge has ended"
                }
            
            # Track participation
            contribution_id = f"participation_{parent_id}_{challenge_id}_{int(time.time())}"
            
            contribution = ParentContribution(
                contribution_id=contribution_id,
                parent_id=parent_id,
                contribution_type="challenge_participation",
                resource_id=None,
                challenge_id=challenge_id,
                content=participation_data.get("content", ""),
                quality_score=0.0,  # Will be evaluated later
                community_impact=0,  # Will be calculated later
                reward_points=0,  # Will be awarded based on performance
                badges_earned=[],
                created_at=datetime.utcnow()
            )
            
            # Save to database
            if self.enable_database_persistence:
                await self._save_parent_contribution_to_db(contribution)
            
            # Update challenge participation count
            challenge.participation_count += 1
            await self._update_community_challenge_in_db(challenge_id, {"participation_count": challenge.participation_count})
            
            # Update metrics
            self.metrics["community_challenges_participated"] += 1
            self.metrics["parent_contributions"] += 1
            
            result = {
                "success": True,
                "contribution_id": contribution_id,
                "challenge_id": challenge_id,
                "challenge_title": challenge.title,
                "message": "Successfully joined the challenge",
                "next_steps": [
                    "Complete the challenge requirements",
                    "Submit your work before deadline",
                    "Wait for evaluation and results"
                ]
            }
            
            logger.info(f"Parent {parent_id} joined challenge {challenge_id}")
            return result
            
        except Exception as e:
            logger.error(f"Challenge participation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to join challenge"
            }
    
    async def like_community_resource(
        self,
        parent_id: str,
        resource_id: str
    ) -> Dict[str, Any]:
        """
        Like a community resource.
        
        Args:
            parent_id: Parent ID liking the resource
            resource_id: Resource ID to like
        
        Returns:
            Dict with like results
        """
        try:
            # Get resource
            resource = await self._get_community_resource_by_id(resource_id)
            if not resource:
                return {
                    "success": False,
                    "error": "Resource not found"
                }
            
            # Check if already liked
            like_key = f"like_{parent_id}_{resource_id}"
            existing_like = await self._check_existing_like(like_key)
            
            if existing_like:
                # Unlike if already liked
                resource.community_likes -= 1
                await self._remove_like_record(like_key)
                action = "unliked"
            else:
                # Add like
                resource.community_likes += 1
                await self._save_like_record(like_key, parent_id, resource_id)
                action = "liked"
            
            # Update resource in database
            if self.enable_database_persistence:
                await self._update_community_resource_in_db(resource_id, {"community_likes": resource.community_likes})
            
            # Update metrics
            self.metrics["total_community_likes"] = resource.community_likes
            
            result = {
                "success": True,
                "resource_id": resource_id,
                "action": action,
                "total_likes": resource.community_likes,
                "message": f"Resource {action} successfully"
            }
            
            logger.info(f"Parent {parent_id} {action} resource {resource_id}")
            return result
            
        except Exception as e:
            logger.error(f"Resource like failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to like resource"
            }
    
    async def share_community_resource(
        self,
        parent_id: str,
        resource_id: str,
        share_platform: str
    ) -> Dict[str, Any]:
        """
        Share a community resource.
        
        Args:
            parent_id: Parent ID sharing the resource
            resource_id: Resource ID to share
            share_platform: Platform where resource is shared
        
        Returns:
            Dict with share results
        """
        try:
            # Get resource
            resource = await self._get_community_resource_by_id(resource_id)
            if not resource:
                return {
                    "success": False,
                    "error": "Resource not found"
                }
            
            # Track share
            share_record = {
                "share_id": f"share_{parent_id}_{resource_id}_{int(time.time())}",
                "parent_id": parent_id,
                "resource_id": resource_id,
                "platform": share_platform,
                "shared_at": datetime.utcnow()
            }
            
            # Save share record
            if self.enable_database_persistence:
                await self._save_share_record(share_record)
            
            # Update resource share count
            resource.community_shares += 1
            await self._update_community_resource_in_db(resource_id, {"community_shares": resource.community_shares})
            
            # Update metrics
            self.metrics["total_community_shares"] = resource.community_shares
            
            result = {
                "success": True,
                "resource_id": resource_id,
                "share_platform": share_platform,
                "total_shares": resource.community_shares,
                "share_url": f"https://mentor.ai/resources/{resource_id}",
                "message": "Resource shared successfully"
            }
            
            logger.info(f"Parent {parent_id} shared resource {resource_id} on {share_platform}")
            return result
            
        except Exception as e:
            logger.error(f"Resource share failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to share resource"
            }
    
    async def get_community_leaderboard(
        self,
        category: Optional[str] = None,
        time_period: str = "monthly",  # "weekly", "monthly", "all_time"
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get community leaderboard.
        
        Args:
            category: Optional category filter
            time_period: Time period for leaderboard
            limit: Maximum number of results
        
        Returns:
            Dict with leaderboard data
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            if time_period == "weekly":
                start_date = end_date - timedelta(weeks=1)
            elif time_period == "monthly":
                start_date = end_date - timedelta(days=30)
            else:  # all_time
                start_date = datetime(2020, 1, 1)  # Far past date
            
            # Get top contributors
            contributors = await self._get_top_contributors(start_date, end_date, category, limit)
            
            # Get top resources
            top_resources = await self._get_top_community_resources(start_date, end_date, category, limit)
            
            # Calculate engagement scores
            leaderboard_data = []
            for contributor in contributors:
                engagement_score = self._calculate_engagement_score(contributor)
                leaderboard_data.append({
                    "parent_id": contributor["parent_id"],
                    "contributions_count": contributor["contributions_count"],
                    "likes_received": contributor["likes_received"],
                    "shares_generated": contributor["shares_generated"],
                    "engagement_score": engagement_score,
                    "badges_earned": contributor.get("badges_earned", []),
                    "rank": 0  # Will be set after sorting
                })
            
            # Sort by engagement score and assign ranks
            leaderboard_data.sort(key=lambda x: x["engagement_score"], reverse=True)
            for i, entry in enumerate(leaderboard_data, 1):
                entry["rank"] = i
            
            result = {
                "success": True,
                "time_period": time_period,
                "category": category,
                "leaderboard": leaderboard_data[:limit],
                "top_resources": top_resources,
                "generated_at": datetime.utcnow().isoformat(),
                "total_participants": len(leaderboard_data)
            }
            
            logger.info(f"Generated community leaderboard: {len(leaderboard_data)} participants")
            return result
            
        except Exception as e:
            logger.error(f"Community leaderboard generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate leaderboard"
            }
    
    async def get_parent_community_profile(
        self,
        parent_id: str
    ) -> Dict[str, Any]:
        """
        Get parent's community profile and contributions.
        
        Args:
            parent_id: Parent ID
        
        Returns:
            Dict with parent's community profile
        """
        try:
            # Get parent contributions
            contributions = await self._get_parent_contributions(parent_id)
            
            # Get parent's submitted resources
            submitted_resources = await self._get_parent_submitted_resources(parent_id)
            
            # Get parent's challenge participations
            challenge_participations = await self._get_parent_challenge_participations(parent_id)
            
            # Calculate community metrics
            total_contributions = len(contributions)
            total_likes_received = sum(c.get("likes_received", 0) for c in contributions)
            total_shares_generated = sum(c.get("shares_generated", 0) for c in contributions)
            badges_earned = list(set([badge for c in contributions for badge in c.get("badges_earned", [])]))
            
            # Calculate engagement score
            engagement_score = self._calculate_engagement_score({
                "parent_id": parent_id,
                "contributions_count": total_contributions,
                "likes_received": total_likes_received,
                "shares_generated": total_shares_generated,
                "badges_earned": badges_earned
            })
            
            result = {
                "success": True,
                "parent_id": parent_id,
                "community_stats": {
                    "total_contributions": total_contributions,
                    "submitted_resources": len(submitted_resources),
                    "challenge_participations": len(challenge_participations),
                    "total_likes_received": total_likes_received,
                    "total_shares_generated": total_shares_generated,
                    "badges_earned": badges_earned,
                    "engagement_score": engagement_score
                },
                "recent_contributions": contributions[:5],
                "submitted_resources": submitted_resources[:10],
                "challenge_participations": challenge_participations[:5],
                "achievements": await self._get_parent_achievements(parent_id),
                "community_rank": await self._get_parent_community_rank(parent_id),
                "profile_updated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Generated community profile for parent {parent_id}")
            return result
            
        except Exception as e:
            logger.error(f"Community profile generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate community profile"
            }
    
    # ========================================================================
    # COMMUNITY HELPER METHODS
    # ========================================================================
    
    async def _assess_community_resource_quality(self, resource_data: Dict[str, Any]) -> QualityScore:
        """Assess quality of community-submitted resource."""
        try:
            # Build prompt for quality assessment
            prompt = f"""
Assess the quality of this community-submitted educational resource.

Resource Content:
{json.dumps(resource_data, indent=2)}

Quality Criteria:
- Content Accuracy (30%): Factual correctness
- Educational Value (25%): Learning effectiveness
- Engagement Level (20%): Interest and interaction
- Appropriateness (15%): Age and level suitability
- Clarity (10%): Clear explanations
- Originality (5%): Unique contribution

Requirements:
1. Assess each criterion on a scale of 1-10
2. Calculate weighted overall score
3. Provide quality level (excellent/good/average/poor)
4. Include specific feedback

Format as JSON:
{{
    "content_accuracy": 8,
    "educational_value": 7,
    "engagement_level": 6,
    "appropriateness": 8,
    "clarity": 7,
    "originality": 7,
    "overall_score": 7.1,
    "quality_level": "good",
    "feedback": "Specific feedback for improvement"
}}
"""
            
            # Generate quality assessment using AI service
            content_request = ContentRequest(
                content_type=ContentType.ANALYSIS,
                prompt=prompt,
                user_id="system",
                student_id="system",
                context={"resource": resource_data},
                metadata={"generation_type": "community_quality_assessment"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse quality assessment
            try:
                quality_data = json.loads(result.content)
                
                if isinstance(quality_data, dict):
                    overall_score = quality_data.get("overall_score", 5.0)
                    
                    if overall_score >= 8.5:
                        return QualityScore.EXCELLENT
                    elif overall_score >= 6.5:
                        return QualityScore.GOOD
                    elif overall_score >= 4.5:
                        return QualityScore.AVERAGE
                    else:
                        return QualityScore.POOR
                        
            except json.JSONDecodeError:
                pass
            
            # Default to average if assessment fails
            return QualityScore.AVERAGE
            
        except Exception as e:
            logger.error(f"Failed to assess community resource quality: {e}")
            return QualityScore.AVERAGE
    
    async def _save_community_resource_to_db(self, resource: CommunityResource):
        """Save community resource to database."""
        try:
            doc_ref = self.db.collection(self.community_resources_collection).document(resource.resource_id)
            await doc_ref.set(resource.__dict__)
            logger.debug(f"Saved community resource to database: {resource.resource_id}")
            
        except Exception as e:
            logger.error(f"Failed to save community resource to database: {e}")
            self.metrics["database_failures"] += 1
    
    async def _track_parent_contribution(
        self,
        parent_id: str,
        contribution_type: str,
        resource_id: Optional[str],
        content: str
    ):
        """Track parent contribution for metrics."""
        try:
            contribution_id = f"contrib_{parent_id}_{contribution_type}_{int(time.time())}"
            
            contribution = ParentContribution(
                contribution_id=contribution_id,
                parent_id=parent_id,
                contribution_type=contribution_type,
                resource_id=resource_id,
                challenge_id=None,
                content=content,
                quality_score=0.0,  # Will be evaluated later
                community_impact=0,  # Will be calculated later
                reward_points=0,  # Will be awarded based on performance
                badges_earned=[],
                created_at=datetime.utcnow()
            )
            
            if self.enable_database_persistence:
                await self._save_parent_contribution_to_db(contribution)
            
            # Update metrics
            self.metrics["parent_contributions"] += 1
            
        except Exception as e:
            logger.error(f"Failed to track parent contribution: {e}")
    
    async def _get_community_resource_by_id(self, resource_id: str) -> Optional[CommunityResource]:
        """Get community resource by ID."""
        try:
            doc_ref = self.db.collection(self.community_resources_collection).document(resource_id)
            doc = await doc_ref.get()
            
            if doc.exists:
                resource_data = doc.to_dict()
                return CommunityResource(**resource_data)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get community resource by ID: {e}")
            return None
    
    async def _update_community_resource_in_db(self, resource_id: str, update_data: Dict[str, Any]):
        """Update community resource in database."""
        try:
            doc_ref = self.db.collection(self.community_resources_collection).document(resource_id)
            await doc_ref.update(update_data)
            logger.debug(f"Updated community resource in database: {resource_id}")
            
        except Exception as e:
            logger.error(f"Failed to update community resource in database: {e}")
            self.metrics["database_failures"] += 1
    
    async def _notify_resource_approval(self, parent_id: str, resource_id: str):
        """Notify parent about resource approval."""
        try:
            # This would typically send a notification via email, push notification, etc.
            logger.info(f"Notified parent {parent_id} about resource approval: {resource_id}")
            
        except Exception as e:
            logger.error(f"Failed to notify resource approval: {e}")
    
    async def _notify_resource_rejection(self, parent_id: str, resource_id: str, notes: Optional[str]):
        """Notify parent about resource rejection."""
        try:
            # This would typically send a notification via email, push notification, etc.
            logger.info(f"Notified parent {parent_id} about resource rejection: {resource_id} - {notes}")
            
        except Exception as e:
            logger.error(f"Failed to notify resource rejection: {e}")
    
    async def _save_community_challenge_to_db(self, challenge: CommunityChallenge):
        """Save community challenge to database."""
        try:
            doc_ref = self.db.collection(self.community_challenges_collection).document(challenge.challenge_id)
            await doc_ref.set(challenge.__dict__)
            logger.debug(f"Saved community challenge to database: {challenge.challenge_id}")
            
        except Exception as e:
            logger.error(f"Failed to save community challenge to database: {e}")
            self.metrics["database_failures"] += 1
    
    async def _get_community_challenge_by_id(self, challenge_id: str) -> Optional[CommunityChallenge]:
        """Get community challenge by ID."""
        try:
            doc_ref = self.db.collection(self.community_challenges_collection).document(challenge_id)
            doc = await doc_ref.get()
            
            if doc.exists:
                challenge_data = doc.to_dict()
                return CommunityChallenge(**challenge_data)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get community challenge by ID: {e}")
            return None
    
    async def _update_community_challenge_in_db(self, challenge_id: str, update_data: Dict[str, Any]):
        """Update community challenge in database."""
        try:
            doc_ref = self.db.collection(self.community_challenges_collection).document(challenge_id)
            await doc_ref.update(update_data)
            logger.debug(f"Updated community challenge in database: {challenge_id}")
            
        except Exception as e:
            logger.error(f"Failed to update community challenge in database: {e}")
            self.metrics["database_failures"] += 1
    
    async def _save_parent_contribution_to_db(self, contribution: ParentContribution):
        """Save parent contribution to database."""
        try:
            doc_ref = self.db.collection(self.parent_contributions_collection).document(contribution.contribution_id)
            await doc_ref.set(contribution.__dict__)
            logger.debug(f"Saved parent contribution to database: {contribution.contribution_id}")
            
        except Exception as e:
            logger.error(f"Failed to save parent contribution to database: {e}")
            self.metrics["database_failures"] += 1
    
    async def _check_existing_like(self, like_key: str) -> bool:
        """Check if like already exists."""
        try:
            doc_ref = self.db.collection("resource_likes").document(like_key)
            doc = await doc_ref.get()
            return doc.exists
            
        except Exception as e:
            logger.error(f"Failed to check existing like: {e}")
            return False
    
    async def _save_like_record(self, like_key: str, parent_id: str, resource_id: str):
        """Save like record to database."""
        try:
            like_record = {
                "like_key": like_key,
                "parent_id": parent_id,
                "resource_id": resource_id,
                "liked_at": datetime.utcnow()
            }
            
            doc_ref = self.db.collection("resource_likes").document(like_key)
            await doc_ref.set(like_record)
            logger.debug(f"Saved like record: {like_key}")
            
        except Exception as e:
            logger.error(f"Failed to save like record: {e}")
            self.metrics["database_failures"] += 1
    
    async def _remove_like_record(self, like_key: str):
        """Remove like record from database."""
        try:
            doc_ref = self.db.collection("resource_likes").document(like_key)
            await doc_ref.delete()
            logger.debug(f"Removed like record: {like_key}")
            
        except Exception as e:
            logger.error(f"Failed to remove like record: {e}")
            self.metrics["database_failures"] += 1
    
    async def _save_share_record(self, share_record: Dict[str, Any]):
        """Save share record to database."""
        try:
            doc_ref = self.db.collection("resource_shares").document(share_record["share_id"])
            await doc_ref.set(share_record)
            logger.debug(f"Saved share record: {share_record['share_id']}")
            
        except Exception as e:
            logger.error(f"Failed to save share record: {e}")
            self.metrics["database_failures"] += 1
    
    async def _get_top_contributors(
        self,
        start_date: datetime,
        end_date: datetime,
        category: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get top contributors for leaderboard."""
        try:
            # Query contributions in date range
            query = self.db.collection(self.parent_contributions_collection)\
                .where("created_at", ">=", start_date)\
                .where("created_at", "<=", end_date)\
                .order_by("created_at", direction="DESCENDING")
            
            # Aggregate contributions by parent
            parent_contributions = {}
            async for doc in query.stream():
                contribution = doc.to_dict()
                parent_id = contribution["parent_id"]
                
                if parent_id not in parent_contributions:
                    parent_contributions[parent_id] = {
                        "parent_id": parent_id,
                        "contributions_count": 0,
                        "likes_received": 0,
                        "shares_generated": 0,
                        "badges_earned": []
                    }
                
                parent_contributions[parent_id]["contributions_count"] += 1
                
                # Add badges earned
                badges = contribution.get("badges_earned", [])
                parent_contributions[parent_id]["badges_earned"].extend(badges)
            
            # Get likes and shares for each parent's resources
            for parent_id in parent_contributions:
                # Get likes received
                likes_query = self.db.collection(self.community_resources_collection)\
                    .where("parent_id", "==", parent_id)\
                    .where("moderation_status", "==", "approved")
                
                total_likes = 0
                total_shares = 0
                async for doc in likes_query.stream():
                    resource = doc.to_dict()
                    total_likes += resource.get("community_likes", 0)
                    total_shares += resource.get("community_shares", 0)
                
                parent_contributions[parent_id]["likes_received"] = total_likes
                parent_contributions[parent_id]["shares_generated"] = total_shares
                
                # Remove duplicate badges
                parent_contributions[parent_id]["badges_earned"] = list(set(
                    parent_contributions[parent_id]["badges_earned"]
                ))
            
            # Sort by contributions count and return top contributors
            contributors = sorted(
                parent_contributions.values(),
                key=lambda x: x["contributions_count"],
                reverse=True
            )
            
            return contributors[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get top contributors: {e}")
            return []
    
    async def _get_top_community_resources(
        self,
        start_date: datetime,
        end_date: datetime,
        category: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get top community resources for leaderboard."""
        try:
            # Query approved resources in date range
            query = self.db.collection(self.community_resources_collection)\
                .where("moderation_status", "==", "approved")\
                .where("created_at", ">=", start_date)\
                .where("created_at", "<=", end_date)
            
            if category:
                query = query.where("category", "==", category)
            
            # Order by community engagement (likes + shares)
            resources = []
            async for doc in query.stream():
                resource = doc.to_dict()
                engagement_score = (
                    resource.get("community_likes", 0) +
                    resource.get("community_shares", 0) * 2  # Weight shares more
                )
                resource["engagement_score"] = engagement_score
                resources.append(resource)
            
            # Sort by engagement score and return top resources
            top_resources = sorted(
                resources,
                key=lambda x: x["engagement_score"],
                reverse=True
            )
            
            return top_resources[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get top community resources: {e}")
            return []
    
    def _calculate_engagement_score(self, contributor: Dict[str, Any]) -> float:
        """Calculate engagement score for a contributor."""
        try:
            contributions = contributor.get("contributions_count", 0)
            likes = contributor.get("likes_received", 0)
            shares = contributor.get("shares_generated", 0)
            badges = len(contributor.get("badges_earned", []))
            
            # Weighted engagement score
            engagement_score = (
                contributions * 10 +      # Base points for contributions
                likes * 2 +               # Points for likes received
                shares * 5 +              # Higher points for shares
                badges * 20               # Bonus points for badges
            )
            
            return float(engagement_score)
            
        except Exception as e:
            logger.error(f"Failed to calculate engagement score: {e}")
            return 0.0
    
    async def _get_parent_contributions(self, parent_id: str) -> List[Dict[str, Any]]:
        """Get parent's contributions."""
        try:
            query = self.db.collection(self.parent_contributions_collection)\
                .where("parent_id", "==", parent_id)\
                .order_by("created_at", direction="DESCENDING")
            
            contributions = []
            async for doc in query.stream():
                contribution = doc.to_dict()
                contributions.append(contribution)
            
            return contributions
            
        except Exception as e:
            logger.error(f"Failed to get parent contributions: {e}")
            return []
    
    async def _get_parent_submitted_resources(self, parent_id: str) -> List[Dict[str, Any]]:
        """Get parent's submitted resources."""
        try:
            query = self.db.collection(self.community_resources_collection)\
                .where("parent_id", "==", parent_id)\
                .order_by("created_at", direction="DESCENDING")
            
            resources = []
            async for doc in query.stream():
                resource = doc.to_dict()
                resources.append(resource)
            
            return resources
            
        except Exception as e:
            logger.error(f"Failed to get parent submitted resources: {e}")
            return []
    
    async def _get_parent_challenge_participations(self, parent_id: str) -> List[Dict[str, Any]]:
        """Get parent's challenge participations."""
        try:
            query = self.db.collection(self.parent_contributions_collection)\
                .where("parent_id", "==", parent_id)\
                .where("contribution_type", "==", "challenge_participation")\
                .order_by("created_at", direction="DESCENDING")
            
            participations = []
            async for doc in query.stream():
                participation = doc.to_dict()
                participations.append(participation)
            
            return participations
            
        except Exception as e:
            logger.error(f"Failed to get parent challenge participations: {e}")
            return []
    
    async def _get_parent_achievements(self, parent_id: str) -> List[Dict[str, Any]]:
        """Get parent's achievements."""
        try:
            # This would typically query an achievements collection
            # For now, return basic achievements based on contributions
            contributions = await self._get_parent_contributions(parent_id)
            
            achievements = []
            
            # Contribution-based achievements
            if len(contributions) >= 1:
                achievements.append({
                    "achievement_id": "first_contribution",
                    "title": "First Contribution",
                    "description": "Made your first community contribution",
                    "badge": "contributor_starter",
                    "earned_at": contributions[0]["created_at"]
                })
            
            if len(contributions) >= 10:
                achievements.append({
                    "achievement_id": "active_contributor",
                    "title": "Active Contributor",
                    "description": "Made 10+ community contributions",
                    "badge": "contributor_active",
                    "earned_at": contributions[9]["created_at"]
                })
            
            if len(contributions) >= 50:
                achievements.append({
                    "achievement_id": "expert_contributor",
                    "title": "Expert Contributor",
                    "description": "Made 50+ community contributions",
                    "badge": "contributor_expert",
                    "earned_at": contributions[49]["created_at"]
                })
            
            return achievements
            
        except Exception as e:
            logger.error(f"Failed to get parent achievements: {e}")
            return []
    
    async def _get_parent_community_rank(self, parent_id: str) -> Dict[str, Any]:
        """Get parent's community rank."""
        try:
            # Get all parents' engagement scores
            all_contributors = await self._get_top_contributors(
                datetime(2020, 1, 1),
                datetime.utcnow(),
                None,
                1000  # Get a large sample
            )
            
            # Find the parent in the list
            parent_rank = None
            for i, contributor in enumerate(all_contributors, 1):
                if contributor["parent_id"] == parent_id:
                    parent_rank = {
                        "rank": i,
                        "total_parents": len(all_contributors),
                        "percentile": (i / len(all_contributors)) * 100,
                        "engagement_score": self._calculate_engagement_score(contributor)
                    }
                    break
            
            if not parent_rank:
                # Parent not found in top contributors
                parent_rank = {
                    "rank": len(all_contributors) + 1,
                    "total_parents": len(all_contributors) + 1,
                    "percentile": 100,
                    "engagement_score": 0.0
                }
            
            return parent_rank
            
        except Exception as e:
            logger.error(f"Failed to get parent community rank: {e}")
            return {
                "rank": 0,
                "total_parents": 0,
                "percentile": 0,
                "engagement_score": 0.0
            }

# Service instance
_parent_resource_library_service_instance = None

def get_parent_resource_library_service(
    db: Optional[firestore.Client] = None,
    unified_config: Optional[GeminiConfig] = None,
    enable_database_persistence: bool = True,
    cache_size: int = 200,
    cache_ttl_hours: int = 12
) -> ParentResourceLibraryService:
    """
    Get singleton instance of Parent Resource Library Service.
    
    Args:
        db: Firestore client (creates new if None)
        unified_config: Optional unified configuration
        enable_database_persistence: Enable saving to database
        cache_size: Maximum cache size
        cache_ttl_hours: Cache TTL in hours
    
    Returns:
        ParentResourceLibraryService instance
    """
    global _parent_resource_library_service_instance
    
    if _parent_resource_library_service_instance is None:
        logger.info("Creating new ParentResourceLibraryService singleton instance")
        _parent_resource_library_service_instance = ParentResourceLibraryService(
            db=db,
            unified_config=unified_config,
            enable_database_persistence=enable_database_persistence,
            cache_size=cache_size,
            cache_ttl_hours=cache_ttl_hours
        )
    
    return _parent_resource_library_service_instance

# Module initialization
logger.info("Parent Resource Library Service module loaded")