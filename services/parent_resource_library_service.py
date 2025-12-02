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
- Community-contributed resources
- Downloadable materials library
- Resource quality assessment

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
            "database_failures": 0
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

# Module initialization
logger.info("Parent Resource Library Service module loaded")