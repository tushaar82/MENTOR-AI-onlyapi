"""
Parent Training Academy Service

This service provides AI-powered training modules and courses for parents
to help them become effective mentors and teachers for their children.

Features:
- Self-paced micro-learning modules (5-10 minutes each)
- Subject-specific teaching methodologies
- "Teach Mathematics in 30 Days" crash courses
- Parent teaching readiness assessment
- Progress tracking and certification
- Personalized learning paths

Author: Mentor AI Team
Version: 1.0.0
"""

import logging
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
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

# Training module types and categories
class ModuleType(Enum):
    """Types of training modules."""
    SUBJECT_MASTERY = "subject_mastery"
    TEACHING_METHODS = "teaching_methods"
    PSYCHOLOGY = "psychology"
    COMMUNICATION = "communication"
    TIME_MANAGEMENT = "time_management"
    ASSESSMENT = "assessment"
    MOTIVATION = "motivation"
    CRASH_COURSE = "crash_course"

class ModuleCategory(Enum):
    """Categories for training modules."""
    MATHEMATICS = "mathematics"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"
    GENERAL_PARENTING = "general_parenting"
    EXAM_STRATEGIES = "exam_strategies"

class DifficultyLevel(Enum):
    """Difficulty levels for training modules."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

@dataclass
class TrainingModuleRequest:
    """Request for training module generation."""
    
    parent_id: str
    module_type: ModuleType
    category: Optional[ModuleCategory] = None
    subject_focus: Optional[str] = None
    difficulty_level: DifficultyLevel = DifficultyLevel.BEGINNER
    language: str = "english"
    duration_minutes: int = 10
    include_assessment: bool = True
    context: Optional[Dict[str, Any]] = None

@dataclass
class TrainingModuleResult:
    """Result from training module generation."""
    
    module_id: str
    title: str
    description: str
    content: str
    duration_minutes: int
    difficulty_level: DifficultyLevel
    learning_objectives: List[str]
    key_concepts: List[str]
    teaching_tips: List[str]
    assessment_questions: List[Dict[str, Any]]
    resources: List[Dict[str, Any]]
    confidence_score: float
    generation_time_ms: int
    created_at: datetime

@dataclass
class ParentProgress:
    """Parent training progress tracking."""
    
    parent_id: str
    modules_completed: List[str]
    modules_in_progress: List[str]
    total_time_spent_minutes: int
    assessment_scores: Dict[str, float]
    skill_levels: Dict[str, str]
    last_activity: datetime
    streak_days: int

class ParentTrainingAcademyService:
    """
    Service for AI-powered parent training and education.
    
    This service leverages Gemini Flash to create personalized training modules
    for parents to become effective mentors and teachers.
    
    Attributes:
        unified_service: Unified Gemini configuration service
        ai_content_service: AI content generation service
        db: Firestore database client
        module_cache: In-memory cache for training modules
        progress_tracker: Parent progress tracking
        assessment_engine: Module assessment functionality
    
    Example:
        >>> service = ParentTrainingAcademyService()
        >>> result = service.generate_training_module(
        ...     parent_id="parent123",
        ...     module_type=ModuleType.SUBJECT_MASTERY,
        ...     category=ModuleCategory.MATHEMATICS
        ... )
        >>> print(f"Generated module: {result.title}")
    """
    
    def __init__(
        self,
        db: Optional[firestore.Client] = None,
        unified_config: Optional[GeminiConfig] = None,
        enable_database_persistence: bool = True,
        cache_size: int = 100,
        cache_ttl_hours: int = 24
    ):
        """
        Initialize Parent Training Academy Service.
        
        Args:
            db: Firestore client (creates new if None)
            unified_config: Optional unified configuration
            enable_database_persistence: Enable saving to database
            cache_size: Maximum cache size
            cache_ttl_hours: Cache TTL in hours
        """
        logger.info("Initializing ParentTrainingAcademyService")
        
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
        
        # Module cache
        self.module_cache: Dict[str, TrainingModuleResult] = {}
        
        # Collections
        self.training_modules_collection = "parent_training_modules"
        self.parent_progress_collection = "parent_training_progress"
        self.assessments_collection = "parent_training_assessments"
        
        # Metrics
        self.metrics = {
            "total_modules_generated": 0,
            "modules_by_type": {mt.value: 0 for mt in ModuleType},
            "modules_by_category": {mc.value: 0 for mc in ModuleCategory},
            "average_generation_time_ms": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
            "database_saves": 0,
            "database_failures": 0,
            "assessments_completed": 0,
            "average_completion_rate": 0.0
        }
        
        logger.info(
            f"ParentTrainingAcademyService initialized (db_persistence={enable_database_persistence}, "
            f"cache_size={cache_size}, cache_ttl={cache_ttl_hours}h)"
        )
    
    async def generate_training_module(
        self,
        request: TrainingModuleRequest
    ) -> TrainingModuleResult:
        """
        Generate AI-powered training module for parent.
        
        Args:
            request: TrainingModuleRequest with all generation parameters
        
        Returns:
            TrainingModuleResult with generated module and metadata
        
        Raises:
            ValueError: If request is invalid
            Exception: If generation fails
        """
        start_time = time.time()
        
        # Generate module ID
        module_id = f"module_{request.parent_id}_{request.module_type.value}_{int(time.time())}_{hashlib.md5(f'{request.category.value if request.category else \"general\"}_{request.subject_focus or \"general\"}'.encode()).hexdigest()[:8]}"
        
        logger.info(
            f"Generating {request.module_type.value} training module: {module_id}"
        )
        
        try:
            # Check cache
            cache_key = self._generate_cache_key(request)
            if cache_key in self.module_cache:
                cached_result = self.module_cache[cache_key]
                logger.info(f"Cache hit for training module: {module_id}")
                
                # Update metrics
                self.metrics["cache_hits"] += 1
                
                return cached_result
            
            self.metrics["cache_misses"] += 1
            
            # Get parent context for personalization
            parent_context = await self._get_parent_context(request.parent_id)
            
            # Route to appropriate generator
            generator = self._get_module_generator(request.module_type)
            
            # Generate training module
            module_data, generation_metadata = await generator(request, parent_context)
            
            # Calculate metrics
            generation_time_ms = int((time.time() - start_time) * 1000)
            
            # Create result
            result = TrainingModuleResult(
                module_id=module_id,
                title=module_data.get("title", "New Training Module"),
                description=module_data.get("description", ""),
                content=module_data.get("content", ""),
                duration_minutes=request.duration_minutes,
                difficulty_level=request.difficulty_level,
                learning_objectives=module_data.get("learning_objectives", []),
                key_concepts=module_data.get("key_concepts", []),
                teaching_tips=module_data.get("teaching_tips", []),
                assessment_questions=module_data.get("assessment_questions", []),
                resources=module_data.get("resources", []),
                confidence_score=module_data.get("confidence_score", 0.7),
                generation_time_ms=generation_time_ms,
                created_at=datetime.utcnow()
            )
            
            # Cache result
            if len(self.module_cache) < self.cache_size:
                self.module_cache[cache_key] = result
            
            # Save to database
            if self.enable_database_persistence:
                await self._save_module_to_db(result, request)
            
            # Update metrics
            self.metrics["total_modules_generated"] += 1
            self.metrics["modules_by_type"][request.module_type.value] += 1
            if request.category:
                self.metrics["modules_by_category"][request.category.value] += 1
            self._update_average_generation_time(generation_time_ms)
            
            logger.info(
                f"Generated {request.module_type.value} training module: {module_id}, "
                f"duration={result.duration_minutes}min, confidence={result.confidence_score:.2f}, "
                f"time={generation_time_ms}ms"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Training module generation failed: {e}")
            
            # Update metrics
            if self.enable_database_persistence:
                self.metrics["database_failures"] += 1
            
            raise
    
    async def get_recommended_learning_path(
        self,
        parent_id: str,
        student_id: str,
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized learning path for parent based on student needs.
        
        Args:
            parent_id: Parent ID
            student_id: Student ID
            focus_areas: Optional list of focus areas
        
        Returns:
            Personalized learning path with module recommendations
        """
        try:
            # Get student data and parent progress
            student_data = await self._get_student_context(student_id)
            parent_progress = await self._get_parent_progress(parent_id)
            
            # Build prompt for learning path generation
            prompt = self._build_learning_path_prompt(
                student_data, parent_progress, focus_areas
            )
            
            # Generate learning path using AI service
            content_request = ContentRequest(
                content_type=ContentType.RECOMMENDATION,
                prompt=prompt,
                user_id=parent_id,
                student_id=student_id,
                context={
                    "student_data": student_data,
                    "parent_progress": parent_progress,
                    "focus_areas": focus_areas
                },
                metadata={"generation_type": "learning_path"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse learning path from response
            learning_path = self._parse_learning_path(result.content)
            
            logger.info(f"Generated personalized learning path for parent {parent_id}")
            return learning_path
            
        except Exception as e:
            logger.error(f"Failed to generate learning path: {e}")
            raise
    
    async def assess_parent_readiness(
        self,
        parent_id: str,
        subject_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Assess parent's teaching readiness and provide recommendations.
        
        Args:
            parent_id: Parent ID
            subject_areas: Optional list of subject areas to assess
        
        Returns:
            Assessment results with readiness scores and recommendations
        """
        try:
            # Get parent progress and context
            parent_progress = await self._get_parent_progress(parent_id)
            parent_context = await self._get_parent_context(parent_id)
            
            # Build prompt for readiness assessment
            prompt = self._build_readiness_assessment_prompt(
                parent_progress, parent_context, subject_areas
            )
            
            # Generate assessment using AI service
            content_request = ContentRequest(
                content_type=ContentType.ASSESSMENT,
                prompt=prompt,
                user_id=parent_id,
                context={
                    "parent_progress": parent_progress,
                    "parent_context": parent_context,
                    "subject_areas": subject_areas
                },
                metadata={"generation_type": "readiness_assessment"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse assessment from response
            assessment = self._parse_readiness_assessment(result.content)
            
            logger.info(f"Assessed parent readiness for parent {parent_id}")
            return assessment
            
        except Exception as e:
            logger.error(f"Failed to assess parent readiness: {e}")
            raise
    
    async def get_training_modules(
        self,
        parent_id: str,
        module_type: Optional[ModuleType] = None,
        category: Optional[ModuleCategory] = None,
        difficulty_level: Optional[DifficultyLevel] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Retrieve training modules from database.
        
        Args:
            parent_id: Parent ID
            module_type: Optional module type filter
            category: Optional category filter
            difficulty_level: Optional difficulty level filter
            limit: Maximum number of results
        
        Returns:
            List of training modules
        """
        try:
            query = self.db.collection(self.training_modules_collection)\
                .where("parent_id", "==", parent_id)\
                .order_by("created_at", direction="DESCENDING")\
                .limit(limit)
            
            if module_type:
                query = query.where("module_type", "==", module_type.value)
            
            if category:
                query = query.where("category", "==", category.value)
            
            if difficulty_level:
                query = query.where("difficulty_level", "==", difficulty_level.value)
            
            results = []
            async for doc in query.stream():
                module_data = doc.to_dict()
                results.append(module_data)
            
            logger.info(f"Retrieved {len(results)} training modules for parent {parent_id}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to get training modules: {e}")
            raise
    
    async def update_parent_progress(
        self,
        parent_id: str,
        module_id: str,
        progress_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update parent's training progress.
        
        Args:
            parent_id: Parent ID
            module_id: Module ID
            progress_data: Progress update data
        
        Returns:
            Updated progress information
        """
        try:
            # Get current progress
            current_progress = await self._get_parent_progress(parent_id)
            
            # Update progress based on module completion
            if progress_data.get("completed", False):
                if module_id not in current_progress.modules_completed:
                    current_progress.modules_completed.append(module_id)
                
                if module_id in current_progress.modules_in_progress:
                    current_progress.modules_in_progress.remove(module_id)
            
            # Update time spent
            time_spent = progress_data.get("time_spent_minutes", 0)
            current_progress.total_time_spent_minutes += time_spent
            
            # Update assessment scores
            if "assessment_score" in progress_data:
                current_progress.assessment_scores[module_id] = progress_data["assessment_score"]
            
            # Update last activity and streak
            current_progress.last_activity = datetime.utcnow()
            current_progress.streak_days = self._calculate_streak(current_progress)
            
            # Save updated progress
            await self._save_parent_progress(parent_id, current_progress)
            
            # Update metrics
            self.metrics["assessments_completed"] += 1
            self._update_average_completion_rate(current_progress)
            
            logger.info(f"Updated progress for parent {parent_id}, module {module_id}")
            
            return {
                "success": True,
                "updated_progress": current_progress,
                "streak_days": current_progress.streak_days,
                "total_modules_completed": len(current_progress.modules_completed)
            }
            
        except Exception as e:
            logger.error(f"Failed to update parent progress: {e}")
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
            "service": "parent_training_academy_service",
            "metrics": self.metrics,
            "derived": {
                "cache_hit_rate": cache_hit_rate,
                "average_generation_time_ms": self.metrics["average_generation_time_ms"],
                "database_success_rate": (
                    (self.metrics["database_saves"] / 
                     max(self.metrics["database_saves"] + self.metrics["database_failures"], 1)) * 100
                ),
                "average_completion_rate": self.metrics["average_completion_rate"]
            },
            "module_type_breakdown": {
                mt: count for mt, count in self.metrics["modules_by_type"].items()
            },
            "category_breakdown": {
                mc: count for mc, count in self.metrics["modules_by_category"].items()
            }
        }
    
    # ========================================================================
    # PRIVATE METHODS
    # ========================================================================
    
    def _generate_cache_key(self, request: TrainingModuleRequest) -> str:
        """Generate cache key for training module request."""
        key_data = {
            "parent_id": request.parent_id,
            "module_type": request.module_type.value,
            "category": request.category.value if request.category else None,
            "subject_focus": request.subject_focus,
            "difficulty_level": request.difficulty_level.value,
            "duration_minutes": request.duration_minutes,
            "language": request.language
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    async def _get_parent_context(self, parent_id: str) -> Dict[str, Any]:
        """Get parent context for personalization."""
        try:
            # Get parent progress
            progress_doc = await self.db.collection(self.parent_progress_collection).document(parent_id).get()
            progress_data = progress_doc.to_dict() if progress_doc.exists else {}
            
            return {
                "parent_id": parent_id,
                "progress": progress_data,
                "modules_completed": progress_data.get("modules_completed", []),
                "skill_levels": progress_data.get("skill_levels", {}),
                "total_time_spent": progress_data.get("total_time_spent_minutes", 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get parent context: {e}")
            return {"parent_id": parent_id, "error": str(e)}
    
    async def _get_student_context(self, student_id: str) -> Dict[str, Any]:
        """Get student context for learning path generation."""
        try:
            # Get student data from existing collections
            # This would integrate with existing student services
            return {
                "student_id": student_id,
                "weak_areas": [],  # Would get from analytics service
                "strong_areas": [],  # Would get from analytics service
                "recent_performance": {},  # Would get from analytics service
                "exam_info": {}  # Would get from exam service
            }
            
        except Exception as e:
            logger.error(f"Failed to get student context: {e}")
            return {"student_id": student_id, "error": str(e)}
    
    async def _get_parent_progress(self, parent_id: str) -> ParentProgress:
        """Get parent training progress."""
        try:
            doc = await self.db.collection(self.parent_progress_collection).document(parent_id).get()
            
            if doc.exists:
                progress_data = doc.to_dict()
                return ParentProgress(
                    parent_id=parent_id,
                    modules_completed=progress_data.get("modules_completed", []),
                    modules_in_progress=progress_data.get("modules_in_progress", []),
                    total_time_spent_minutes=progress_data.get("total_time_spent_minutes", 0),
                    assessment_scores=progress_data.get("assessment_scores", {}),
                    skill_levels=progress_data.get("skill_levels", {}),
                    last_activity=progress_data.get("last_activity", datetime.utcnow()),
                    streak_days=progress_data.get("streak_days", 0)
                )
            else:
                # Create new progress record
                new_progress = ParentProgress(
                    parent_id=parent_id,
                    modules_completed=[],
                    modules_in_progress=[],
                    total_time_spent_minutes=0,
                    assessment_scores={},
                    skill_levels={},
                    last_activity=datetime.utcnow(),
                    streak_days=0
                )
                
                await self._save_parent_progress(parent_id, new_progress)
                return new_progress
                
        except Exception as e:
            logger.error(f"Failed to get parent progress: {e}")
            return ParentProgress(
                parent_id=parent_id,
                modules_completed=[],
                modules_in_progress=[],
                total_time_spent_minutes=0,
                assessment_scores={},
                skill_levels={},
                last_activity=datetime.utcnow(),
                streak_days=0
            )
    
    def _get_module_generator(self, module_type: ModuleType):
        """Get appropriate module generator function."""
        generators = {
            ModuleType.SUBJECT_MASTERY: self._generate_subject_mastery_module,
            ModuleType.TEACHING_METHODS: self._generate_teaching_methods_module,
            ModuleType.PSYCHOLOGY: self._generate_psychology_module,
            ModuleType.COMMUNICATION: self._generate_communication_module,
            ModuleType.TIME_MANAGEMENT: self._generate_time_management_module,
            ModuleType.ASSESSMENT: self._generate_assessment_module,
            ModuleType.MOTIVATION: self._generate_motivation_module,
            ModuleType.CRASH_COURSE: self._generate_crash_course_module
        }
        return generators.get(module_type, self._generate_general_module)
    
    async def _generate_subject_mastery_module(
        self,
        request: TrainingModuleRequest,
        parent_context: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate subject mastery training module."""
        prompt = f"""
        Generate a comprehensive training module for parents to master {request.category.value if request.category else request.subject_focus or 'a subject'}.
        
        Parent Context:
        {json.dumps(parent_context, indent=2)}
        
        Requirements:
        1. Create content suitable for {request.difficulty_level.value} level parents
        2. Focus on {request.category.value if request.category else 'general'} teaching strategies
        3. Duration: {request.duration_minutes} minutes of focused learning
        4. Include practical examples and exercises
        5. Provide assessment questions to test understanding
        6. Generate in {request.language} language
        
        Format as JSON:
        {{
            "title": "Engaging title for the module",
            "description": "Brief description of what parent will learn",
            "content": "Detailed training content with sections and examples",
            "learning_objectives": ["objective1", "objective2", "objective3"],
            "key_concepts": ["concept1", "concept2", "concept3"],
            "teaching_tips": ["tip1", "tip2", "tip3"],
            "assessment_questions": [
                {{"question": "Q1", "options": ["A", "B", "C", "D"], "correct": "A", "explanation": "Why A is correct"}},
                {{"question": "Q2", "options": ["A", "B", "C", "D"], "correct": "B", "explanation": "Why B is correct"}}
            ],
            "resources": [{"type": "video", "url": "example_url"}, {"type": "article", "title": "Example article"}],
            "confidence_score": 0.8
        }}
        """
        
        # Generate content using AI service
        content_request = ContentRequest(
            content_type=ContentType.TRAINING,
            prompt=prompt,
            user_id=request.parent_id,
            context={"parent_context": parent_context},
            metadata={"module_type": "subject_mastery"}
        )
        
        result = await self.ai_content_service.generate_content(content_request)
        
        # Parse response
        try:
            module_data = json.loads(result.content)
        except json.JSONDecodeError:
            # Fallback module
            module_data = {
                "title": f"{request.category.value if request.category else 'Subject'} Mastery Training",
                "description": "Comprehensive training for effective subject teaching",
                "content": result.content,
                "learning_objectives": ["Understand key concepts", "Learn teaching strategies", "Practice effective communication"],
                "key_concepts": ["Concept understanding", "Teaching methodology", "Practice techniques"],
                "teaching_tips": ["Be patient", "Use real-world examples", "Encourage questions"],
                "assessment_questions": [],
                "resources": [],
                "confidence_score": 0.7
            }
        
        generation_metadata = {
            "tokens_used": result.tokens_used,
            "cost": result.cost,
            "generation_time_ms": result.generation_time_ms
        }
        
        return module_data, generation_metadata
    
    async def _generate_teaching_methods_module(
        self,
        request: TrainingModuleRequest,
        parent_context: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate teaching methods training module."""
        prompt = f"""
        Generate a training module on effective teaching methods for parents.
        
        Parent Context:
        {json.dumps(parent_context, indent=2)}
        
        Requirements:
        1. Focus on proven teaching methodologies
        2. Include age-appropriate strategies
        3. Cover different learning styles
        4. Provide practical classroom management tips
        5. Duration: {request.duration_minutes} minutes
        6. Generate in {request.language} language
        
        Format as JSON:
        {{
            "title": "Effective Teaching Methods for Parents",
            "description": "Learn proven strategies to teach your child effectively",
            "content": "Detailed content covering various teaching methodologies",
            "learning_objectives": ["objective1", "objective2", "objective3"],
            "key_concepts": ["concept1", "concept2", "concept3"],
            "teaching_tips": ["tip1", "tip2", "tip3"],
            "assessment_questions": [
                {{"question": "Q1", "options": ["A", "B", "C", "D"], "correct": "A", "explanation": "Why A is correct"}}
            ],
            "resources": [{"type": "guide", "title": "Teaching guide"}],
            "confidence_score": 0.8
        }}
        """
        
        # Generate content using AI service
        content_request = ContentRequest(
            content_type=ContentType.TRAINING,
            prompt=prompt,
            user_id=request.parent_id,
            context={"parent_context": parent_context},
            metadata={"module_type": "teaching_methods"}
        )
        
        result = await self.ai_content_service.generate_content(content_request)
        
        # Parse response
        try:
            module_data = json.loads(result.content)
        except json.JSONDecodeError:
            # Fallback module
            module_data = {
                "title": "Effective Teaching Methods",
                "description": "Learn proven strategies to teach your child effectively",
                "content": result.content,
                "learning_objectives": ["Understand teaching methodologies", "Learn classroom management", "Practice effective communication"],
                "key_concepts": ["Teaching strategies", "Learning styles", "Classroom management"],
                "teaching_tips": ["Be patient", "Adapt to learning style", "Use positive reinforcement"],
                "assessment_questions": [],
                "resources": [],
                "confidence_score": 0.7
            }
        
        generation_metadata = {
            "tokens_used": result.tokens_used,
            "cost": result.cost,
            "generation_time_ms": result.generation_time_ms
        }
        
        return module_data, generation_metadata
    
    async def _generate_psychology_module(
        self,
        request: TrainingModuleRequest,
        parent_context: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate child psychology training module."""
        prompt = f"""
        Generate a training module on child psychology for parents.
        
        Parent Context:
        {json.dumps(parent_context, indent=2)}
        
        Requirements:
        1. Focus on developmental psychology
        2. Cover motivation and learning behavior
        3. Address common psychological challenges
        4. Provide strategies for positive reinforcement
        5. Duration: {request.duration_minutes} minutes
        6. Generate in {request.language} language
        
        Format as JSON:
        {{
            "title": "Understanding Child Psychology",
            "description": "Learn psychological principles to support your child's learning",
            "content": "Comprehensive content on child psychology and development",
            "learning_objectives": ["objective1", "objective2", "objective3"],
            "key_concepts": ["concept1", "concept2", "concept3"],
            "teaching_tips": ["tip1", "tip2", "tip3"],
            "assessment_questions": [
                {{"question": "Q1", "options": ["A", "B", "C", "D"], "correct": "A", "explanation": "Why A is correct"}}
            ],
            "resources": [{"type": "book", "title": "Child psychology guide"}],
            "confidence_score": 0.8
        }}
        """
        
        # Generate content using AI service
        content_request = ContentRequest(
            content_type=ContentType.TRAINING,
            prompt=prompt,
            user_id=request.parent_id,
            context={"parent_context": parent_context},
            metadata={"module_type": "psychology"}
        )
        
        result = await self.ai_content_service.generate_content(content_request)
        
        # Parse response
        try:
            module_data = json.loads(result.content)
        except json.JSONDecodeError:
            # Fallback module
            module_data = {
                "title": "Understanding Child Psychology",
                "description": "Learn psychological principles to support your child's learning",
                "content": result.content,
                "learning_objectives": ["Understand developmental stages", "Learn motivation techniques", "Recognize learning barriers"],
                "key_concepts": ["Developmental psychology", "Motivation", "Learning barriers"],
                "teaching_tips": ["Be supportive", "Recognize effort", "Create positive environment"],
                "assessment_questions": [],
                "resources": [],
                "confidence_score": 0.7
            }
        
        generation_metadata = {
            "tokens_used": result.tokens_used,
            "cost": result.cost,
            "generation_time_ms": result.generation_time_ms
        }
        
        return module_data, generation_metadata
    
    async def _generate_communication_module(
        self,
        request: TrainingModuleRequest,
        parent_context: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate parent-child communication training module."""
        prompt = f"""
        Generate a training module on effective parent-child communication.
        
        Parent Context:
        {json.dumps(parent_context, indent=2)}
        
        Requirements:
        1. Focus on constructive communication strategies
        2. Cover academic and personal communication
        3. Address conflict resolution
        4. Provide active listening techniques
        5. Duration: {request.duration_minutes} minutes
        6. Generate in {request.language} language
        
        Format as JSON:
        {{
            "title": "Effective Parent-Child Communication",
            "description": "Learn to communicate effectively with your child about studies and life",
            "content": "Comprehensive content on communication strategies and techniques",
            "learning_objectives": ["objective1", "objective2", "objective3"],
            "key_concepts": ["concept1", "concept2", "concept3"],
            "teaching_tips": ["tip1", "tip2", "tip3"],
            "assessment_questions": [
                {{"question": "Q1", "options": ["A", "B", "C", "D"], "correct": "A", "explanation": "Why A is correct"}}
            ],
            "resources": [{"type": "guide", "title": "Communication guide"}],
            "confidence_score": 0.8
        }}
        """
        
        # Generate content using AI service
        content_request = ContentRequest(
            content_type=ContentType.TRAINING,
            prompt=prompt,
            user_id=request.parent_id,
            context={"parent_context": parent_context},
            metadata={"module_type": "communication"}
        )
        
        result = await self.ai_content_service.generate_content(content_request)
        
        # Parse response
        try:
            module_data = json.loads(result.content)
        except json.JSONDecodeError:
            # Fallback module
            module_data = {
                "title": "Effective Parent-Child Communication",
                "description": "Learn to communicate effectively with your child about studies and life",
                "content": result.content,
                "learning_objectives": ["Learn active listening", "Master constructive feedback", "Build trust and openness"],
                "key_concepts": ["Active listening", "Constructive feedback", "Trust building"],
                "teaching_tips": ["Listen first", "Ask open-ended questions", "Validate feelings"],
                "assessment_questions": [],
                "resources": [],
                "confidence_score": 0.7
            }
        
        generation_metadata = {
            "tokens_used": result.tokens_used,
            "cost": result.cost,
            "generation_time_ms": result.generation_time_ms
        }
        
        return module_data, generation_metadata
    
    async def _generate_time_management_module(
        self,
        request: TrainingModuleRequest,
        parent_context: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate time management training module."""
        prompt = f"""
        Generate a training module on time management for parent-child learning.
        
        Parent Context:
        {json.dumps(parent_context, indent=2)}
        
        Requirements:
        1. Focus on creating effective study schedules
        2. Cover balancing academics and personal time
        3. Provide productivity techniques
        4. Address procrastination and burnout prevention
        5. Duration: {request.duration_minutes} minutes
        6. Generate in {request.language} language
        
        Format as JSON:
        {{
            "title": "Time Management for Effective Learning",
            "description": "Learn to manage time effectively for optimal learning outcomes",
            "content": "Comprehensive content on time management strategies and techniques",
            "learning_objectives": ["objective1", "objective2", "objective3"],
            "key_concepts": ["concept1", "concept2", "concept3"],
            "teaching_tips": ["tip1", "tip2", "tip3"],
            "assessment_questions": [
                {{"question": "Q1", "options": ["A", "B", "C", "D"], "correct": "A", "explanation": "Why A is correct"}}
            ],
            "resources": [{"type": "planner", "title": "Study schedule template"}],
            "confidence_score": 0.8
        }}
        """
        
        # Generate content using AI service
        content_request = ContentRequest(
            content_type=ContentType.TRAINING,
            prompt=prompt,
            user_id=request.parent_id,
            context={"parent_context": parent_context},
            metadata={"module_type": "time_management"}
        )
        
        result = await self.ai_content_service.generate_content(content_request)
        
        # Parse response
        try:
            module_data = json.loads(result.content)
        except json.JSONDecodeError:
            # Fallback module
            module_data = {
                "title": "Time Management for Effective Learning",
                "description": "Learn to manage time effectively for optimal learning outcomes",
                "content": result.content,
                "learning_objectives": ["Create effective schedules", "Balance study and rest", "Avoid burnout"],
                "key_concepts": ["Schedule planning", "Time blocking", "Break management"],
                "teaching_tips": ["Set realistic goals", "Use timers", "Take regular breaks"],
                "assessment_questions": [],
                "resources": [],
                "confidence_score": 0.7
            }
        
        generation_metadata = {
            "tokens_used": result.tokens_used,
            "cost": result.cost,
            "generation_time_ms": result.generation_time_ms
        }
        
        return module_data, generation_metadata
    
    async def _generate_assessment_module(
        self,
        request: TrainingModuleRequest,
        parent_context: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate assessment training module."""
        prompt = f"""
        Generate a training module on effective student assessment for parents.
        
        Parent Context:
        {json.dumps(parent_context, indent=2)}
        
        Requirements:
        1. Focus on formative and summative assessment
        2. Cover different assessment types and methods
        3. Provide rubric creation guidance
        4. Address feedback techniques
        5. Duration: {request.duration_minutes} minutes
        6. Generate in {request.language} language
        
        Format as JSON:
        {{
            "title": "Effective Student Assessment for Parents",
            "description": "Learn to assess your child's learning effectively and constructively",
            "content": "Comprehensive content on assessment methods and techniques",
            "learning_objectives": ["objective1", "objective2", "objective3"],
            "key_concepts": ["concept1", "concept2", "concept3"],
            "teaching_tips": ["tip1", "tip2", "tip3"],
            "assessment_questions": [
                {{"question": "Q1", "options": ["A", "B", "C", "D"], "correct": "A", "explanation": "Why A is correct"}}
            ],
            "resources": [{"type": "rubric", "title": "Assessment rubric template"}],
            "confidence_score": 0.8
        }}
        """
        
        # Generate content using AI service
        content_request = ContentRequest(
            content_type=ContentType.TRAINING,
            prompt=prompt,
            user_id=request.parent_id,
            context={"parent_context": parent_context},
            metadata={"module_type": "assessment"}
        )
        
        result = await self.ai_content_service.generate_content(content_request)
        
        # Parse response
        try:
            module_data = json.loads(result.content)
        except json.JSONDecodeError:
            # Fallback module
            module_data = {
                "title": "Effective Student Assessment for Parents",
                "description": "Learn to assess your child's learning effectively and constructively",
                "content": result.content,
                "learning_objectives": ["Understand assessment types", "Learn feedback techniques", "Create effective rubrics"],
                "key_concepts": ["Formative assessment", "Summative assessment", "Feedback techniques"],
                "teaching_tips": ["Assess regularly", "Focus on improvement", "Provide specific feedback"],
                "assessment_questions": [],
                "resources": [],
                "confidence_score": 0.7
            }
        
        generation_metadata = {
            "tokens_used": result.tokens_used,
            "cost": result.cost,
            "generation_time_ms": result.generation_time_ms
        }
        
        return module_data, generation_metadata
    
    async def _generate_motivation_module(
        self,
        request: TrainingModuleRequest,
        parent_context: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate motivation training module."""
        prompt = f"""
        Generate a training module on motivating children for learning.
        
        Parent Context:
        {json.dumps(parent_context, indent=2)}
        
        Requirements:
        1. Focus on intrinsic and extrinsic motivation
        2. Cover age-appropriate motivation strategies
        3. Address dealing with lack of motivation
        4. Provide celebration and recognition techniques
        5. Duration: {request.duration_minutes} minutes
        6. Generate in {request.language} language
        
        Format as JSON:
        {{
            "title": "Motivating Your Child for Learning",
            "description": "Learn effective strategies to keep your child motivated and engaged",
            "content": "Comprehensive content on motivation techniques and strategies",
            "learning_objectives": ["objective1", "objective2", "objective3"],
            "key_concepts": ["concept1", "concept2", "concept3"],
            "teaching_tips": ["tip1", "tip2", "tip3"],
            "assessment_questions": [
                {{"question": "Q1", "options": ["A", "B", "C", "D"], "correct": "A", "explanation": "Why A is correct"}}
            ],
            "resources": [{"type": "checklist", "title": "Motivation checklist"}],
            "confidence_score": 0.8
        }}
        """
        
        # Generate content using AI service
        content_request = ContentRequest(
            content_type=ContentType.TRAINING,
            prompt=prompt,
            user_id=request.parent_id,
            context={"parent_context": parent_context},
            metadata={"module_type": "motivation"}
        )
        
        result = await self.ai_content_service.generate_content(content_request)
        
        # Parse response
        try:
            module_data = json.loads(result.content)
        except json.JSONDecodeError:
            # Fallback module
            module_data = {
                "title": "Motivating Your Child for Learning",
                "description": "Learn effective strategies to keep your child motivated and engaged",
                "content": result.content,
                "learning_objectives": ["Understand motivation types", "Learn motivation techniques", "Create positive environment"],
                "key_concepts": ["Intrinsic motivation", "Extrinsic motivation", "Positive reinforcement"],
                "teaching_tips": ["Celebrate effort", "Set achievable goals", "Provide autonomy"],
                "assessment_questions": [],
                "resources": [],
                "confidence_score": 0.7
            }
        
        generation_metadata = {
            "tokens_used": result.tokens_used,
            "cost": result.cost,
            "generation_time_ms": result.generation_time_ms
        }
        
        return module_data, generation_metadata
    
    async def _generate_crash_course_module(
        self,
        request: TrainingModuleRequest,
        parent_context: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate crash course training module."""
        prompt = f"""
        Generate a comprehensive crash course for parents to teach {request.category.value if request.category else request.subject_focus or 'a subject'} in 30 days.
        
        Parent Context:
        {json.dumps(parent_context, indent=2)}
        
        Requirements:
        1. Create a 30-day structured learning plan
        2. Break down complex topics into daily lessons
        3. Include progressive difficulty levels
        4. Provide daily practice exercises
        5. Include weekly assessments
        6. Duration: {request.duration_minutes} minutes per day
        7. Generate in {request.language} language
        
        Format as JSON:
        {{
            "title": "Teach {request.category.value if request.category else request.subject_focus or 'Subject'} in 30 Days",
            "description": "Comprehensive 30-day crash course to master teaching this subject",
            "content": "Detailed 30-day structured curriculum with daily lessons",
            "learning_objectives": ["objective1", "objective2", "objective3"],
            "key_concepts": ["concept1", "concept2", "concept3"],
            "teaching_tips": ["tip1", "tip2", "tip3"],
            "assessment_questions": [
                {{"question": "Q1", "options": ["A", "B", "C", "D"], "correct": "A", "explanation": "Why A is correct"}}
            ],
            "resources": [{"type": "curriculum", "title": "30-day teaching plan"}],
            "confidence_score": 0.8
        }}
        """
        
        # Generate content using AI service
        content_request = ContentRequest(
            content_type=ContentType.TRAINING,
            prompt=prompt,
            user_id=request.parent_id,
            context={"parent_context": parent_context},
            metadata={"module_type": "crash_course"}
        )
        
        result = await self.ai_content_service.generate_content(content_request)
        
        # Parse response
        try:
            module_data = json.loads(result.content)
        except json.JSONDecodeError:
            # Fallback module
            module_data = {
                "title": f"Teach {request.category.value if request.category else request.subject_focus or 'Subject'} in 30 Days",
                "description": "Comprehensive 30-day crash course to master teaching this subject",
                "content": result.content,
                "learning_objectives": ["Master key concepts", "Learn teaching strategies", "Practice effectively"],
                "key_concepts": ["Core concepts", "Teaching methodologies", "Practice techniques"],
                "teaching_tips": ["Follow the schedule", "Practice daily", "Assess regularly"],
                "assessment_questions": [],
                "resources": [],
                "confidence_score": 0.7
            }
        
        generation_metadata = {
            "tokens_used": result.tokens_used,
            "cost": result.cost,
            "generation_time_ms": result.generation_time_ms
        }
        
        return module_data, generation_metadata
    
    async def _generate_general_module(
        self,
        request: TrainingModuleRequest,
        parent_context: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate general training module."""
        prompt = f"""
        Generate a comprehensive training module for parents.
        
        Parent Context:
        {json.dumps(parent_context, indent=2)}
        
        Requirements:
        1. Create engaging, practical content
        2. Include clear learning objectives
        3. Provide actionable teaching tips
        4. Include assessment questions
        5. Duration: {request.duration_minutes} minutes
        6. Generate in {request.language} language
        
        Format as JSON:
        {{
            "title": "Parent Training Module",
            "description": "Comprehensive training to enhance your teaching skills",
            "content": "Detailed training content with practical examples",
            "learning_objectives": ["objective1", "objective2", "objective3"],
            "key_concepts": ["concept1", "concept2", "concept3"],
            "teaching_tips": ["tip1", "tip2", "tip3"],
            "assessment_questions": [
                {{"question": "Q1", "options": ["A", "B", "C", "D"], "correct": "A", "explanation": "Why A is correct"}}
            ],
            "resources": [{"type": "guide", "title": "Training guide"}],
            "confidence_score": 0.7
        }}
        """
        
        # Generate content using AI service
        content_request = ContentRequest(
            content_type=ContentType.TRAINING,
            prompt=prompt,
            user_id=request.parent_id,
            context={"parent_context": parent_context},
            metadata={"module_type": "general"}
        )
        
        result = await self.ai_content_service.generate_content(content_request)
        
        # Parse response
        try:
            module_data = json.loads(result.content)
        except json.JSONDecodeError:
            # Fallback module
            module_data = {
                "title": "Parent Training Module",
                "description": "Comprehensive training to enhance your teaching skills",
                "content": result.content,
                "learning_objectives": ["Understand key concepts", "Learn teaching strategies", "Practice effectively"],
                "key_concepts": ["Core concepts", "Teaching methodologies", "Practice techniques"],
                "teaching_tips": ["Be patient", "Use examples", "Encourage questions"],
                "assessment_questions": [],
                "resources": [],
                "confidence_score": 0.7
            }
        
        generation_metadata = {
            "tokens_used": result.tokens_used,
            "cost": result.cost,
            "generation_time_ms": result.generation_time_ms
        }
        
        return module_data, generation_metadata
    
    def _build_learning_path_prompt(
        self,
        student_data: Dict[str, Any],
        parent_progress: ParentProgress,
        focus_areas: Optional[List[str]]
    ) -> str:
        """Build prompt for learning path generation."""
        return f"""
        Generate a personalized learning path for a parent based on student needs and parent progress.
        
        Student Data:
        {json.dumps(student_data, indent=2)}
        
        Parent Progress:
        {json.dumps(parent_progress.__dict__, indent=2)}
        
        Focus Areas: {focus_areas or 'general'}
        
        Requirements:
        1. Analyze student's weak areas and learning needs
        2. Consider parent's current skill level and completed modules
        3. Recommend specific training modules in logical order
        4. Prioritize high-impact areas first
        5. Include estimated completion time for each module
        6. Create a balanced learning schedule
        
        Format as JSON:
        {{
            "learning_path": [
                {{
                    "module_type": "subject_mastery",
                    "category": "mathematics",
                    "priority": "high",
                    "estimated_duration_hours": 5,
                    "prerequisites": [],
                    "description": "Master mathematics teaching fundamentals"
                }},
                {{
                    "module_type": "teaching_methods",
                    "category": "general",
                    "priority": "medium",
                    "estimated_duration_hours": 3,
                    "prerequisites": ["subject_mastery"],
                    "description": "Learn effective teaching methodologies"
                }}
            ],
            "total_estimated_hours": 20,
            "recommended_schedule": "2-3 modules per week",
            "milestones": [
                "Week 1: Complete mathematics fundamentals",
                "Week 2: Master teaching methods",
                "Week 3: Practice with real examples"
            ],
            "confidence_score": 0.8
        }}
        """
    
    def _build_readiness_assessment_prompt(
        self,
        parent_progress: ParentProgress,
        parent_context: Dict[str, Any],
        subject_areas: Optional[List[str]]
    ) -> str:
        """Build prompt for readiness assessment."""
        return f"""
        Assess parent's readiness to teach their child effectively.
        
        Parent Progress:
        {json.dumps(parent_progress.__dict__, indent=2)}
        
        Parent Context:
        {json.dumps(parent_context, indent=2)}
        
        Subject Areas: {subject_areas or 'all'}
        
        Requirements:
        1. Assess knowledge level in each subject area
        2. Evaluate teaching confidence and skills
        3. Identify strengths and areas for improvement
        4. Provide specific recommendations
        5. Score readiness on a scale of 1-10
        6. Provide confidence score for assessment
        
        Format as JSON:
        {{
            "overall_readiness_score": 7.5,
            "subject_assessments": [
                {{
                    "subject": "mathematics",
                    "knowledge_score": 6,
                    "confidence_score": 7,
                    "readiness_level": "intermediate",
                    "strengths": ["basic concepts", "patience"],
                    "improvement_areas": ["advanced topics", "assessment techniques"]
                }}
            ],
            "overall_strengths": ["patience", "communication", "dedication"],
            "overall_improvement_areas": ["subject matter expertise", "assessment skills"],
            "recommendations": [
                "Complete subject mastery modules for weak areas",
                "Practice assessment techniques",
                "Join parent community for support"
            ],
            "confidence_score": 0.8
        }}
        """
    
    def _parse_learning_path(self, content: str) -> Dict[str, Any]:
        """Parse learning path from AI response."""
        try:
            # Try to parse as JSON
            import json
            learning_path = json.loads(content)
            
            if isinstance(learning_path, dict) and "learning_path" in learning_path:
                return learning_path
            else:
                # Fallback: return as single path
                return {
                    "learning_path": [{
                        "module_type": "general",
                        "category": "general",
                        "priority": "medium",
                        "estimated_duration_hours": 10,
                        "description": "General parent training path"
                    }],
                    "total_estimated_hours": 10,
                    "recommended_schedule": "1 module per week",
                    "milestones": ["Complete basic training", "Practice with child"],
                    "confidence_score": 0.6
                }
                
        except json.JSONDecodeError:
            # Fallback: return basic learning path
            return {
                "learning_path": [{
                    "module_type": "general",
                    "category": "general",
                    "priority": "medium",
                    "estimated_duration_hours": 10,
                    "description": "General parent training path"
                }],
                "total_estimated_hours": 10,
                "recommended_schedule": "1 module per week",
                "milestones": ["Complete basic training", "Practice with child"],
                "confidence_score": 0.6
            }
    
    def _parse_readiness_assessment(self, content: str) -> Dict[str, Any]:
        """Parse readiness assessment from AI response."""
        try:
            # Try to parse as JSON
            import json
            assessment = json.loads(content)
            
            if isinstance(assessment, dict):
                return assessment
            else:
                # Fallback: return as single assessment
                return {
                    "overall_readiness_score": 5.0,
                    "subject_assessments": [],
                    "overall_strengths": ["dedication", "patience"],
                    "overall_improvement_areas": ["subject knowledge", "teaching techniques"],
                    "recommendations": ["Complete training modules", "Practice regularly"],
                    "confidence_score": 0.6
                }
                
        except json.JSONDecodeError:
            # Fallback: return basic assessment
            return {
                "overall_readiness_score": 5.0,
                "subject_assessments": [],
                "overall_strengths": ["dedication", "patience"],
                "overall_improvement_areas": ["subject knowledge", "teaching techniques"],
                "recommendations": ["Complete training modules", "Practice regularly"],
                "confidence_score": 0.6
            }
    
    async def _save_module_to_db(self, result: TrainingModuleResult, request: TrainingModuleRequest):
        """Save training module to database."""
        try:
            module_record = {
                "module_id": result.module_id,
                "parent_id": request.parent_id,
                "module_type": request.module_type.value,
                "category": request.category.value if request.category else None,
                "subject_focus": request.subject_focus,
                "title": result.title,
                "description": result.description,
                "content": result.content,
                "duration_minutes": result.duration_minutes,
                "difficulty_level": result.difficulty_level.value,
                "learning_objectives": result.learning_objectives,
                "key_concepts": result.key_concepts,
                "teaching_tips": result.teaching_tips,
                "assessment_questions": result.assessment_questions,
                "resources": result.resources,
                "confidence_score": result.confidence_score,
                "generation_time_ms": result.generation_time_ms,
                "created_at": result.created_at,
                "metadata": {
                    "language": request.language,
                    "include_assessment": request.include_assessment
                }
            }
            
            doc_ref = self.db.collection(self.training_modules_collection).document(result.module_id)
            await doc_ref.set(module_record)
            
            self.metrics["database_saves"] += 1
            logger.debug(f"Saved training module to database: {result.module_id}")
            
        except Exception as e:
            logger.error(f"Failed to save training module to database: {e}")
            self.metrics["database_failures"] += 1
    
    async def _save_parent_progress(self, parent_id: str, progress: ParentProgress):
        """Save parent progress to database."""
        try:
            progress_record = {
                "parent_id": parent_id,
                "modules_completed": progress.modules_completed,
                "modules_in_progress": progress.modules_in_progress,
                "total_time_spent_minutes": progress.total_time_spent_minutes,
                "assessment_scores": progress.assessment_scores,
                "skill_levels": progress.skill_levels,
                "last_activity": progress.last_activity,
                "streak_days": progress.streak_days,
                "updated_at": datetime.utcnow()
            }
            
            doc_ref = self.db.collection(self.parent_progress_collection).document(parent_id)
            await doc_ref.set(progress_record)
            
            logger.debug(f"Saved parent progress to database: {parent_id}")
            
        except Exception as e:
            logger.error(f"Failed to save parent progress to database: {e}")
    
    def _update_average_generation_time(self, new_time_ms: int):
        """Update running average generation time."""
        total_modules = self.metrics["total_modules_generated"]
        if total_modules > 0:
            current_avg = self.metrics["average_generation_time_ms"]
            self.metrics["average_generation_time_ms"] = (
                (current_avg * (total_modules - 1) + new_time_ms) / total_modules
            )
    
    def _calculate_streak(self, progress: ParentProgress) -> int:
        """Calculate learning streak based on activity."""
        if not progress.last_activity:
            return 0
        
        days_since_last = (datetime.utcnow() - progress.last_activity).days
        
        if days_since_last <= 1:
            return progress.streak_days + 1
        elif days_since_last <= 3:
            return progress.streak_days
        else:
            return 0  # Reset streak if more than 3 days inactive
    
    def _update_average_completion_rate(self, progress: ParentProgress):
        """Update average completion rate metric."""
        total_available = len(progress.modules_completed) + len(progress.modules_in_progress)
        if total_available > 0:
            completion_rate = len(progress.modules_completed) / total_available
            current_avg = self.metrics["average_completion_rate"]
            self.metrics["average_completion_rate"] = (
                (current_avg + completion_rate) / 2
            )

# Module initialization
logger.info("Parent Training Academy Service module loaded")

# Service factory function
def get_parent_training_academy_service(
    unified_config: Optional[GeminiConfig] = None,
    **kwargs
) -> ParentTrainingAcademyService:
    """
    Get Parent Training Academy service instance.
    
    Args:
        unified_config: Optional unified configuration
        **kwargs: Additional arguments for service initialization
    
    Returns:
        ParentTrainingAcademyService instance
    """
    service = ParentTrainingAcademyService(unified_config=unified_config, **kwargs)
    return service