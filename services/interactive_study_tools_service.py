"""
Interactive Parent-Child Study Tools Service

This service provides text-based collaborative study tools for parents
and children to learn together effectively using Firebase.

Features:
- Text-based collaborative study sessions
- Guided teaching prompts and activities
- Interactive exercises and discussions
- Progress sharing between parent and child
- Real-time collaboration using Firebase
- Multi-language support
- Study session analytics
- Achievement tracking
- Resource integration

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

# Study session types and statuses
class StudySessionType(Enum):
    """Types of study sessions."""
    COLLABORATIVE_LEARNING = "collaborative_learning"
    GUIDED_TEACHING = "guided_teaching"
    INTERACTIVE_DISCUSSION = "interactive_discussion"
    PROBLEM_SOLVING = "problem_solving"
    REVIEW_SESSION = "review_session"
    SKILL_PRACTICE = "skill_practice"
    CONCEPT_EXPLORATION = "concept_exploration"
    QUIZ_SESSION = "quiz_session"

class StudySessionStatus(Enum):
    """Status of study sessions."""
    PLANNED = "planned"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ActivityType(Enum):
    """Types of collaborative activities."""
    QUESTION_ANSWER = "question_answer"
    DISCUSSION = "discussion"
    EXERCISE = "exercise"
    EXPLANATION = "explanation"
    EXAMPLE = "example"
    PRACTICE = "practice"
    FEEDBACK = "feedback"
    REFLECTION = "reflection"

class ParticipantRole(Enum):
    """Roles in study session."""
    PARENT = "parent"
    CHILD = "child"
    BOTH = "both"

@dataclass
class StudySession:
    """Study session definition."""
    
    session_id: str
    parent_id: str
    child_id: str
    session_type: StudySessionType
    title: str
    description: str
    subject: str
    topic: str
    difficulty_level: str
    language: str
    status: StudySessionStatus
    scheduled_start: datetime
    actual_start: Optional[datetime]
    scheduled_end: datetime
    actual_end: Optional[datetime]
    participants: List[str]
    activities: List[Dict[str, Any]]
    resources: List[Dict[str, Any]]
    progress_percentage: float
    achievements: List[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class StudyActivity:
    """Study activity definition."""
    
    activity_id: str
    session_id: str
    activity_type: ActivityType
    participant_role: ParticipantRole
    content: str
    media_url: Optional[str]
    response_to: Optional[str]
    timestamp: datetime
    duration_minutes: int
    effectiveness_score: float
    engagement_level: str
    created_at: datetime

@dataclass
class TeachingPrompt:
    """Teaching prompt definition."""
    
    prompt_id: str
    session_id: str
    subject: str
    topic: str
    prompt_type: str
    content: str
    suggested_approach: str
    key_points: List[str]
    examples: List[Dict[str, Any]]
    questions: List[str]
    activities: List[Dict[str, Any]]
    difficulty_level: str
    age_appropriateness: str
    estimated_duration: int
    created_at: datetime

@dataclass
class CollaborativeExercise:
    """Collaborative exercise definition."""
    
    exercise_id: str
    session_id: str
    title: str
    description: str
    exercise_type: str
    subject: str
    topic: str
    instructions: List[str]
    parent_role: str
    child_role: str
    collaboration_method: str
    expected_outcome: str
    success_criteria: List[str]
    difficulty_level: str
    time_limit_minutes: Optional[int]
    resources_needed: List[str]
    created_at: datetime

class InteractiveStudyToolsService:
    """
    Service for interactive parent-child study tools.
    
    This service provides text-based collaborative study tools
    that enable parents and children to learn together effectively.
    
    Attributes:
        unified_service: Unified Gemini configuration service
        ai_content_service: AI content generation service
        db: Firestore database client
        session_manager: Study session management
        activity_tracker: Activity tracking system
        prompt_generator: Teaching prompt generation
        exercise_creator: Collaborative exercise creation
    
    Example:
        >>> service = InteractiveStudyToolsService()
        >>> result = service.create_study_session(
        ...     parent_id="parent123",
        ...     child_id="child123",
        ...     session_type=StudySessionType.COLLABORATIVE_LEARNING,
        ...     subject="Mathematics",
        ...     topic="Algebra Basics"
        ... )
        >>> print(f"Session created: {result['session_id']}")
    """
    
    def __init__(
        self,
        db: Optional[firestore.Client] = None,
        unified_config: Optional[GeminiConfig] = None,
        enable_database_persistence: bool = True,
        session_timeout_minutes: int = 120,
        max_activities_per_session: int = 50
    ):
        """
        Initialize Interactive Study Tools Service.
        
        Args:
            db: Firestore client (creates new if None)
            unified_config: Optional unified configuration
            enable_database_persistence: Enable saving to database
            session_timeout_minutes: Session timeout in minutes
            max_activities_per_session: Maximum activities per session
        """
        logger.info("Initializing InteractiveStudyToolsService")
        
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
        self.max_activities_per_session = max_activities_per_session
        
        # Collections
        self.sessions_collection = "study_sessions"
        self.activities_collection = "study_activities"
        self.prompts_collection = "teaching_prompts"
        self.exercises_collection = "collaborative_exercises"
        self.progress_collection = "study_progress"
        
        # Supported languages
        self.supported_languages = [
            "english", "hindi", "bengali", "telugu", "tamil",
            "marathi", "gujarati", "kannada", "malayalam", "punjabi"
        ]
        
        # Metrics
        self.metrics = {
            "total_sessions_created": 0,
            "total_activities_completed": 0,
            "total_prompts_generated": 0,
            "total_exercises_created": 0,
            "sessions_by_type": {st.value: 0 for st in StudySessionType},
            "activities_by_type": {at.value: 0 for at in ActivityType},
            "average_session_duration": 0.0,
            "average_participant_engagement": 0.0,
            "parent_effectiveness_score": 0.0,
            "child_learning_score": 0.0,
            "collaboration_quality": 0.0,
            "database_saves": 0,
            "database_failures": 0
        }
        
        logger.info(
            f"InteractiveStudyToolsService initialized (db_persistence={enable_database_persistence}, "
            f"session_timeout={session_timeout_minutes}min, max_activities={max_activities_per_session})"
        )
    
    async def create_study_session(
        self,
        parent_id: str,
        child_id: str,
        session_type: StudySessionType,
        subject: str,
        topic: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        difficulty_level: str = "intermediate",
        language: str = "english",
        scheduled_start: Optional[datetime] = None,
        scheduled_duration_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Create a new study session.
        
        Args:
            parent_id: Parent ID
            child_id: Child ID
            session_type: Type of study session
            subject: Subject for study
            topic: Specific topic
            title: Optional session title
            description: Optional session description
            difficulty_level: Difficulty level
            language: Session language
            scheduled_start: Optional scheduled start time
            scheduled_duration_minutes: Duration in minutes
        
        Returns:
            Dict with session creation results
        """
        try:
            # Generate session ID
            session_id = f"session_{parent_id}_{child_id}_{int(time.time())}_{hashlib.md5(f'{session_type.value}_{subject}_{topic}'.encode()).hexdigest()[:8]}"
            
            logger.info(f"Creating study session: {session_id}")
            
            # Set default values
            if not title:
                title = f"{session_type.value.replace('_', ' ').title()} - {topic}"
            
            if not description:
                description = f"Interactive {session_type.value.replace('_', ' ')} session for {subject}: {topic}"
            
            if not scheduled_start:
                scheduled_start = datetime.utcnow()
            
            # Create session
            session = StudySession(
                session_id=session_id,
                parent_id=parent_id,
                child_id=child_id,
                session_type=session_type,
                title=title,
                description=description,
                subject=subject,
                topic=topic,
                difficulty_level=difficulty_level,
                language=language,
                status=StudySessionStatus.PLANNED,
                scheduled_start=scheduled_start,
                actual_start=None,
                scheduled_end=scheduled_start + timedelta(minutes=scheduled_duration_minutes),
                actual_end=None,
                participants=[parent_id, child_id],
                activities=[],
                resources=[],
                progress_percentage=0.0,
                achievements=[],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Generate initial teaching prompts
            prompts = await self._generate_initial_prompts(session)
            
            # Generate collaborative exercises
            exercises = await self._generate_collaborative_exercises(session)
            
            # Save to database
            if self.enable_database_persistence:
                await self._save_session_to_db(session)
                
                # Save prompts and exercises
                for prompt in prompts:
                    await self._save_prompt_to_db(prompt)
                
                for exercise in exercises:
                    await self._save_exercise_to_db(exercise)
            
            # Update metrics
            self.metrics["total_sessions_created"] += 1
            self.metrics["sessions_by_type"][session_type.value] += 1
            self.metrics["total_prompts_generated"] += len(prompts)
            self.metrics["total_exercises_created"] += len(exercises)
            
            result = {
                "success": True,
                "session_id": session_id,
                "session_type": session_type.value,
                "title": title,
                "subject": subject,
                "topic": topic,
                "scheduled_start": scheduled_start.isoformat(),
                "scheduled_end": (scheduled_start + timedelta(minutes=scheduled_duration_minutes)).isoformat(),
                "teaching_prompts": len(prompts),
                "collaborative_exercises": len(exercises),
                "next_steps": [
                    "Start the session at scheduled time",
                    "Review teaching prompts before session",
                    "Prepare collaborative exercises"
                ]
            }
            
            logger.info(f"Study session created: {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Study session creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "parent_id": parent_id,
                "child_id": child_id
            }
    
    async def start_study_session(
        self,
        session_id: str,
        participant_id: str
    ) -> Dict[str, Any]:
        """
        Start a study session.
        
        Args:
            session_id: Session ID
            participant_id: ID of participant starting the session
        
        Returns:
            Dict with session start results
        """
        try:
            # Get session
            session = await self._get_session_by_id(session_id)
            if not session:
                return {
                    "success": False,
                    "error": "Session not found",
                    "session_id": session_id
                }
            
            # Check if participant is authorized
            if participant_id not in session.participants:
                return {
                    "success": False,
                    "error": "Participant not authorized for this session",
                    "session_id": session_id
                }
            
            # Update session status
            if session.status == StudySessionStatus.PLANNED:
                session.status = StudySessionStatus.ACTIVE
                session.actual_start = datetime.utcnow()
                session.updated_at = datetime.utcnow()
                
                # Save to database
                if self.enable_database_persistence:
                    await self._update_session_in_db(session_id, {
                        "status": session.status.value,
                        "actual_start": session.actual_start,
                        "updated_at": session.updated_at
                    })
                
                # Send notifications to other participants
                await self._notify_session_start(session, participant_id)
                
                result = {
                    "success": True,
                    "session_id": session_id,
                    "status": session.status.value,
                    "actual_start": session.actual_start.isoformat(),
                    "message": "Session started successfully"
                }
                
                logger.info(f"Study session started: {session_id} by {participant_id}")
                return result
            else:
                return {
                    "success": False,
                    "error": f"Session cannot be started from status: {session.status.value}",
                    "session_id": session_id
                }
                
        except Exception as e:
            logger.error(f"Session start failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
    
    async def add_activity(
        self,
        session_id: str,
        participant_id: str,
        activity_type: ActivityType,
        content: str,
        media_url: Optional[str] = None,
        response_to: Optional[str] = None,
        duration_minutes: int = 0
    ) -> Dict[str, Any]:
        """
        Add an activity to a study session.
        
        Args:
            session_id: Session ID
            participant_id: Participant ID
            activity_type: Type of activity
            content: Activity content
            media_url: Optional media URL
            response_to: Optional response to another activity
            duration_minutes: Activity duration in minutes
        
        Returns:
            Dict with activity addition results
        """
        try:
            # Get session
            session = await self._get_session_by_id(session_id)
            if not session:
                return {
                    "success": False,
                    "error": "Session not found",
                    "session_id": session_id
                }
            
            # Check if session is active
            if session.status != StudySessionStatus.ACTIVE:
                return {
                    "success": False,
                    "error": f"Activities can only be added to active sessions (current: {session.status.value})",
                    "session_id": session_id
                }
            
            # Check if participant is authorized
            if participant_id not in session.participants:
                return {
                    "success": False,
                    "error": "Participant not authorized for this session",
                    "session_id": session_id
                }
            
            # Check activity limit
            if len(session.activities) >= self.max_activities_per_session:
                return {
                    "success": False,
                    "error": f"Maximum activities per session reached ({self.max_activities_per_session})",
                    "session_id": session_id
                }
            
            # Generate activity ID
            activity_id = f"activity_{session_id}_{participant_id}_{int(time.time())}"
            
            # Determine participant role
            participant_role = ParticipantRole.PARENT if participant_id == session.parent_id else ParticipantRole.CHILD
            
            # Create activity
            activity = StudyActivity(
                activity_id=activity_id,
                session_id=session_id,
                activity_type=activity_type,
                participant_role=participant_role,
                content=content,
                media_url=media_url,
                response_to=response_to,
                timestamp=datetime.utcnow(),
                duration_minutes=duration_minutes,
                effectiveness_score=0.0,  # Will be calculated later
                engagement_level="medium",  # Will be calculated
                created_at=datetime.utcnow()
            )
            
            # Add to session activities
            session.activities.append({
                "activity_id": activity_id,
                "participant_id": participant_id,
                "activity_type": activity_type.value,
                "timestamp": activity.timestamp.isoformat(),
                "duration_minutes": duration_minutes
            })
            
            # Update session progress
            session.progress_percentage = min(len(session.activities) * 5, 100)  # Simple progress calculation
            session.updated_at = datetime.utcnow()
            
            # Save to database
            if self.enable_database_persistence:
                await self._save_activity_to_db(activity)
                await self._update_session_in_db(session_id, {
                    "activities": session.activities,
                    "progress_percentage": session.progress_percentage,
                    "updated_at": session.updated_at
                })
            
            # Update metrics
            self.metrics["total_activities_completed"] += 1
            self.metrics["activities_by_type"][activity_type.value] += 1
            
            # Generate AI response if needed
            ai_response = None
            if activity_type in [ActivityType.QUESTION, ActivityType.DISCUSSION]:
                ai_response = await self._generate_ai_response(session, activity)
            
            result = {
                "success": True,
                "activity_id": activity_id,
                "session_id": session_id,
                "activity_type": activity_type.value,
                "participant_role": participant_role.value,
                "progress_percentage": session.progress_percentage,
                "ai_response": ai_response,
                "message": "Activity added successfully"
            }
            
            logger.info(f"Activity added: {activity_id} to session {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Activity addition failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
    
    async def generate_teaching_prompt(
        self,
        session_id: str,
        subject: str,
        topic: str,
        prompt_type: str = "explanation",
        difficulty_level: str = "intermediate",
        child_age: Optional[int] = None,
        learning_style: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a teaching prompt for the session.
        
        Args:
            session_id: Session ID
            subject: Subject area
            topic: Specific topic
            prompt_type: Type of teaching prompt
            difficulty_level: Difficulty level
            child_age: Optional child age
            learning_style: Optional learning style
        
        Returns:
            Dict with teaching prompt generation results
        """
        try:
            # Get session
            session = await self._get_session_by_id(session_id)
            if not session:
                return {
                    "success": False,
                    "error": "Session not found",
                    "session_id": session_id
                }
            
            # Generate prompt ID
            prompt_id = f"prompt_{session_id}_{prompt_type}_{int(time.time())}"
            
            # Build prompt for AI generation
            ai_prompt = f"""
Generate a teaching prompt for parent-child study session.

Session Context:
- Subject: {subject}
- Topic: {topic}
- Prompt Type: {prompt_type}
- Difficulty Level: {difficulty_level}
- Child Age: {child_age or 'Not specified'}
- Learning Style: {learning_style or 'Not specified'}

Requirements:
1. Create age-appropriate content
2. Include step-by-step explanations
3. Provide examples and analogies
4. Suggest interactive elements
5. Include questions for engagement
6. Provide assessment methods
7. Consider both parent and child roles

Format as JSON:
{{
    "prompt_type": "{prompt_type}",
    "content": "Detailed teaching content",
    "suggested_approach": "How parent should approach teaching",
    "key_points": ["point1", "point2", "point3"],
    "examples": [
        {{
            "title": "Example Title",
            "description": "Example description",
            "interactive": true/false
        }}
    ],
    "questions": [
        "engagement question 1",
        "engagement question 2"
    ],
    "activities": [
        {{
            "title": "Activity Title",
            "description": "Activity description",
            "duration_minutes": 15,
            "materials_needed": ["material1", "material2"]
        }}
    ],
    "assessment_methods": [
        "method1 description",
        "method2 description"
    ],
    "estimated_duration": 30,
    "age_appropriateness": "age range description"
}}
"""
            
            # Generate content using AI service
            content_request = ContentRequest(
                content_type=ContentType.TEACHING_PROMPT,
                prompt=ai_prompt,
                user_id=session.parent_id,
                student_id=session.child_id,
                context={
                    "session_id": session_id,
                    "subject": subject,
                    "topic": topic,
                    "prompt_type": prompt_type,
                    "difficulty_level": difficulty_level,
                    "child_age": child_age,
                    "learning_style": learning_style
                },
                metadata={"generation_type": "teaching_prompt"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse teaching prompt
            try:
                import json
                prompt_data = json.loads(result.content)
            except json.JSONDecodeError:
                # Fallback prompt data
                prompt_data = {
                    "prompt_type": prompt_type,
                    "content": result.content,
                    "suggested_approach": "Interactive teaching approach",
                    "key_points": ["Key point 1", "Key point 2"],
                    "examples": [],
                    "questions": ["What do you think about this topic?"],
                    "activities": [],
                    "assessment_methods": ["Observe understanding"],
                    "estimated_duration": 30,
                    "age_appropriateness": "Age-appropriate content"
                }
            
            # Create teaching prompt
            teaching_prompt = TeachingPrompt(
                prompt_id=prompt_id,
                session_id=session_id,
                subject=subject,
                topic=topic,
                prompt_type=prompt_type,
                content=prompt_data.get("content", ""),
                suggested_approach=prompt_data.get("suggested_approach", ""),
                key_points=prompt_data.get("key_points", []),
                examples=prompt_data.get("examples", []),
                questions=prompt_data.get("questions", []),
                activities=prompt_data.get("activities", []),
                difficulty_level=difficulty_level,
                age_appropriateness=prompt_data.get("age_appropriateness", ""),
                estimated_duration=prompt_data.get("estimated_duration", 30),
                created_at=datetime.utcnow()
            )
            
            # Save to database
            if self.enable_database_persistence:
                await self._save_prompt_to_db(teaching_prompt)
            
            # Update metrics
            self.metrics["total_prompts_generated"] += 1
            
            result = {
                "success": True,
                "prompt_id": prompt_id,
                "session_id": session_id,
                "prompt_type": prompt_type,
                "content": teaching_prompt.content,
                "suggested_approach": teaching_prompt.suggested_approach,
                "key_points": teaching_prompt.key_points,
                "examples": teaching_prompt.examples,
                "questions": teaching_prompt.questions,
                "activities": teaching_prompt.activities,
                "estimated_duration": teaching_prompt.estimated_duration,
                "age_appropriateness": teaching_prompt.age_appropriateness,
                "message": "Teaching prompt generated successfully"
            }
            
            logger.info(f"Teaching prompt generated: {prompt_id}")
            return result
            
        except Exception as e:
            logger.error(f"Teaching prompt generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
    
    async def create_collaborative_exercise(
        self,
        session_id: str,
        title: str,
        description: str,
        exercise_type: str,
        instructions: List[str],
        collaboration_method: str = "guided_practice",
        time_limit_minutes: Optional[int] = None,
        resources_needed: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a collaborative exercise for the session.
        
        Args:
            session_id: Session ID
            title: Exercise title
            description: Exercise description
            exercise_type: Type of exercise
            instructions: Step-by-step instructions
            collaboration_method: How parent and child collaborate
            time_limit_minutes: Optional time limit
            resources_needed: Optional list of needed resources
        
        Returns:
            Dict with exercise creation results
        """
        try:
            # Get session
            session = await self._get_session_by_id(session_id)
            if not session:
                return {
                    "success": False,
                    "error": "Session not found",
                    "session_id": session_id
                }
            
            # Generate exercise ID
            exercise_id = f"exercise_{session_id}_{int(time.time())}"
            
            # Create collaborative exercise
            exercise = CollaborativeExercise(
                exercise_id=exercise_id,
                session_id=session_id,
                title=title,
                description=description,
                exercise_type=exercise_type,
                subject=session.subject,
                topic=session.topic,
                instructions=instructions,
                parent_role="Guide and facilitate learning",
                child_role="Active participant and learner",
                collaboration_method=collaboration_method,
                expected_outcome=f"Improved understanding of {session.topic}",
                success_criteria=[
                    "Child can explain the concept",
                    "Parent observes active engagement",
                    "Both participants complete the exercise"
                ],
                difficulty_level=session.difficulty_level,
                time_limit_minutes=time_limit_minutes,
                resources_needed=resources_needed or [],
                created_at=datetime.utcnow()
            )
            
            # Save to database
            if self.enable_database_persistence:
                await self._save_exercise_to_db(exercise)
            
            # Update metrics
            self.metrics["total_exercises_created"] += 1
            
            result = {
                "success": True,
                "exercise_id": exercise_id,
                "session_id": session_id,
                "title": title,
                "exercise_type": exercise_type,
                "collaboration_method": collaboration_method,
                "parent_role": exercise.parent_role,
                "child_role": exercise.child_role,
                "expected_outcome": exercise.expected_outcome,
                "success_criteria": exercise.success_criteria,
                "time_limit_minutes": time_limit_minutes,
                "resources_needed": exercise.resources_needed,
                "message": "Collaborative exercise created successfully"
            }
            
            logger.info(f"Collaborative exercise created: {exercise_id}")
            return result
            
        except Exception as e:
            logger.error(f"Collaborative exercise creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
    
    async def end_study_session(
        self,
        session_id: str,
        participant_id: str,
        final_reflection: Optional[str] = None,
        achievements: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        End a study session.
        
        Args:
            session_id: Session ID
            participant_id: ID of participant ending the session
            final_reflection: Optional final reflection
            achievements: Optional list of achievements
        
        Returns:
            Dict with session end results
        """
        try:
            # Get session
            session = await self._get_session_by_id(session_id)
            if not session:
                return {
                    "success": False,
                    "error": "Session not found",
                    "session_id": session_id
                }
            
            # Check if participant is authorized
            if participant_id not in session.participants:
                return {
                    "success": False,
                    "error": "Participant not authorized for this session",
                    "session_id": session_id
                }
            
            # Update session status
            if session.status == StudySessionStatus.ACTIVE:
                session.status = StudySessionStatus.COMPLETED
                session.actual_end = datetime.utcnow()
                session.progress_percentage = 100.0
                session.updated_at = datetime.utcnow()
                
                # Add achievements if provided
                if achievements:
                    session.achievements.extend(achievements)
                
                # Calculate session duration
                if session.actual_start:
                    duration_minutes = (session.actual_end - session.actual_start).total_seconds() / 60
                    self.metrics["average_session_duration"] = (
                        (self.metrics["average_session_duration"] + duration_minutes) / 2
                    )
                
                # Save to database
                if self.enable_database_persistence:
                    await self._update_session_in_db(session_id, {
                        "status": session.status.value,
                        "actual_end": session.actual_end,
                        "progress_percentage": session.progress_percentage,
                        "achievements": session.achievements,
                        "updated_at": session.updated_at
                    })
                
                # Generate session summary
                summary = await self._generate_session_summary(session, final_reflection)
                
                result = {
                    "success": True,
                    "session_id": session_id,
                    "status": session.status.value,
                    "actual_end": session.actual_end.isoformat(),
                    "duration_minutes": duration_minutes if session.actual_start else 0,
                    "progress_percentage": session.progress_percentage,
                    "achievements": session.achievements,
                    "session_summary": summary,
                    "message": "Session completed successfully"
                }
                
                logger.info(f"Study session ended: {session_id}")
                return result
            else:
                return {
                    "success": False,
                    "error": f"Session cannot be ended from status: {session.status.value}",
                    "session_id": session_id
                }
                
        except Exception as e:
            logger.error(f"Session end failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
    
    async def get_session_analytics(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Get analytics for a study session.
        
        Args:
            session_id: Session ID
        
        Returns:
            Dict with session analytics
        """
        try:
            # Get session
            session = await self._get_session_by_id(session_id)
            if not session:
                return {
                    "success": False,
                    "error": "Session not found",
                    "session_id": session_id
                }
            
            # Get activities for session
            activities = await self._get_session_activities(session_id)
            
            # Calculate analytics
            analytics = self._calculate_session_analytics(session, activities)
            
            # Generate insights
            insights = await self._generate_session_insights(session, activities, analytics)
            
            result = {
                "success": True,
                "session_id": session_id,
                "session_info": {
                    "title": session.title,
                    "subject": session.subject,
                    "topic": session.topic,
                    "session_type": session.session_type.value,
                    "status": session.status.value,
                    "duration_minutes": analytics["duration_minutes"],
                    "participant_count": len(session.participants)
                },
                "activity_analytics": analytics,
                "insights": insights,
                "recommendations": await self._generate_session_recommendations(session, analytics)
            }
            
            logger.info(f"Generated session analytics: {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Session analytics generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get service metrics.
        
        Returns:
            Dictionary with comprehensive metrics
        """
        return {
            "service": "interactive_study_tools_service",
            "metrics": self.metrics,
            "derived": {
                "average_activities_per_session": (
                    self.metrics["total_activities_completed"] / max(self.metrics["total_sessions_created"], 1)
                ),
                "prompts_per_session": (
                    self.metrics["total_prompts_generated"] / max(self.metrics["total_sessions_created"], 1)
                ),
                "exercises_per_session": (
                    self.metrics["total_exercises_created"] / max(self.metrics["total_sessions_created"], 1)
                ),
                "database_success_rate": (
                    (self.metrics["database_saves"] / 
                     max(self.metrics["database_saves"] + self.metrics["database_failures"], 1)) * 100
                )
            },
            "session_type_breakdown": {
                st: count for st, count in self.metrics["sessions_by_type"].items()
            },
            "activity_type_breakdown": {
                at: count for at, count in self.metrics["activities_by_type"].items()
            },
            "supported_languages": self.supported_languages
        }
    
    # ========================================================================
    # PRIVATE METHODS
    # ========================================================================
    
    async def _get_session_by_id(self, session_id: str) -> Optional[StudySession]:
        """Get session by ID."""
        try:
            doc_ref = self.db.collection(self.sessions_collection).document(session_id)
            doc = await doc_ref.get()
            
            if doc.exists:
                session_data = doc.to_dict()
                return StudySession(**session_data)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get session by ID: {e}")
            return None
    
    async def _save_session_to_db(self, session: StudySession):
        """Save session to database."""
        try:
            doc_ref = self.db.collection(self.sessions_collection).document(session.session_id)
            await doc_ref.set(session.__dict__)
            logger.debug(f"Saved session to database: {session.session_id}")
            
            self.metrics["database_saves"] += 1
            
        except Exception as e:
            logger.error(f"Failed to save session to database: {e}")
            self.metrics["database_failures"] += 1
    
    async def _update_session_in_db(self, session_id: str, update_data: Dict[str, Any]):
        """Update session in database."""
        try:
            doc_ref = self.db.collection(self.sessions_collection).document(session_id)
            await doc_ref.update(update_data)
            logger.debug(f"Updated session in database: {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to update session in database: {e}")
            self.metrics["database_failures"] += 1
    
    async def _save_activity_to_db(self, activity: StudyActivity):
        """Save activity to database."""
        try:
            doc_ref = self.db.collection(self.activities_collection).document(activity.activity_id)
            await doc_ref.set(activity.__dict__)
            logger.debug(f"Saved activity to database: {activity.activity_id}")
            
        except Exception as e:
            logger.error(f"Failed to save activity to database: {e}")
            self.metrics["database_failures"] += 1
    
    async def _save_prompt_to_db(self, prompt: TeachingPrompt):
        """Save teaching prompt to database."""
        try:
            doc_ref = self.db.collection(self.prompts_collection).document(prompt.prompt_id)
            await doc_ref.set(prompt.__dict__)
            logger.debug(f"Saved teaching prompt to database: {prompt.prompt_id}")
            
        except Exception as e:
            logger.error(f"Failed to save teaching prompt to database: {e}")
            self.metrics["database_failures"] += 1
    
    async def _save_exercise_to_db(self, exercise: CollaborativeExercise):
        """Save collaborative exercise to database."""
        try:
            doc_ref = self.db.collection(self.exercises_collection).document(exercise.exercise_id)
            await doc_ref.set(exercise.__dict__)
            logger.debug(f"Saved collaborative exercise to database: {exercise.exercise_id}")
            
        except Exception as e:
            logger.error(f"Failed to save collaborative exercise to database: {e}")
            self.metrics["database_failures"] += 1
    
    async def _generate_initial_prompts(self, session: StudySession) -> List[TeachingPrompt]:
        """Generate initial teaching prompts for session."""
        try:
            prompts = []
            
            # Generate different types of prompts based on session type
            if session.session_type == StudySessionType.COLLABORATIVE_LEARNING:
                prompt_types = ["explanation", "discussion", "practice"]
            elif session.session_type == StudySessionType.GUIDED_TEACHING:
                prompt_types = ["explanation", "demonstration", "assessment"]
            else:
                prompt_types = ["explanation", "practice"]
            
            for prompt_type in prompt_types:
                prompt_id = f"initial_{session.session_id}_{prompt_type}"
                
                # Generate simple prompt content
                content = f"Initial {prompt_type} prompt for {session.subject}: {session.topic}"
                
                prompt = TeachingPrompt(
                    prompt_id=prompt_id,
                    session_id=session.session_id,
                    subject=session.subject,
                    topic=session.topic,
                    prompt_type=prompt_type,
                    content=content,
                    suggested_approach="Interactive and engaging",
                    key_points=[f"Key point for {prompt_type}"],
                    examples=[],
                    questions=[f"Question for {prompt_type}"],
                    activities=[],
                    difficulty_level=session.difficulty_level,
                    age_appropriateness="Age-appropriate",
                    estimated_duration=30,
                    created_at=datetime.utcnow()
                )
                
                prompts.append(prompt)
            
            return prompts
            
        except Exception as e:
            logger.error(f"Failed to generate initial prompts: {e}")
            return []
    
    async def _generate_collaborative_exercises(self, session: StudySession) -> List[CollaborativeExercise]:
        """Generate collaborative exercises for session."""
        try:
            exercises = []
            
            # Generate 2-3 exercises based on session type
            exercise_count = 2 if session.session_type == StudySessionType.REVIEW_SESSION else 3
            
            for i in range(exercise_count):
                exercise_id = f"exercise_{session.session_id}_{i+1}"
                
                exercise = CollaborativeExercise(
                    exercise_id=exercise_id,
                    session_id=session.session_id,
                    title=f"Exercise {i+1}: {session.topic}",
                    description=f"Collaborative exercise for {session.topic}",
                    exercise_type="practice",
                    subject=session.subject,
                    topic=session.topic,
                    instructions=[
                        f"Step 1: Review {session.topic} concepts",
                        f"Step 2: Work through examples together",
                        f"Step 3: Practice independently with guidance"
                    ],
                    parent_role="Guide and facilitate",
                    child_role="Active participant",
                    collaboration_method="guided_practice",
                    expected_outcome=f"Improved understanding of {session.topic}",
                    success_criteria=[
                        "Child demonstrates understanding",
                        "Parent provides effective guidance"
                    ],
                    difficulty_level=session.difficulty_level,
                    time_limit_minutes=20,
                    resources_needed=["Notebook", "Pen"],
                    created_at=datetime.utcnow()
                )
                
                exercises.append(exercise)
            
            return exercises
            
        except Exception as e:
            logger.error(f"Failed to generate collaborative exercises: {e}")
            return []
    
    async def _notify_session_start(self, session: StudySession, initiator_id: str):
        """Notify other participants about session start."""
        try:
            # Get other participants
            other_participants = [p for p in session.participants if p != initiator_id]
            
            for participant_id in other_participants:
                # This would typically send a notification via push notification, email, etc.
                logger.info(f"Notified participant {participant_id} about session start: {session.session_id}")
                
        except Exception as e:
            logger.error(f"Failed to notify session start: {e}")
    
    async def _generate_ai_response(
        self,
        session: StudySession,
        activity: StudyActivity
    ) -> Optional[str]:
        """Generate AI response to activity."""
        try:
            # Build prompt for AI response
            prompt = f"""
Generate a helpful response for this study activity.

Session Context:
- Subject: {session.subject}
- Topic: {session.topic}
- Activity Type: {activity.activity_type.value}
- Participant Role: {activity.participant_role.value}
- Activity Content: {activity.content}

Requirements:
1. Provide educational support
2. Encourage further discussion
3. Suggest next steps
4. Be age-appropriate
5. Support collaborative learning

Response should be concise and helpful.
"""
            
            # Generate content using AI service
            content_request = ContentRequest(
                content_type=ContentType.RESPONSE,
                prompt=prompt,
                user_id=session.parent_id,
                student_id=session.child_id,
                context={
                    "session": session.__dict__,
                    "activity": activity.__dict__
                },
                metadata={"generation_type": "activity_response"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            return result.content
            
        except Exception as e:
            logger.error(f"Failed to generate AI response: {e}")
            return None
    
    async def _get_session_activities(self, session_id: str) -> List[StudyActivity]:
        """Get all activities for a session."""
        try:
            query = self.db.collection(self.activities_collection)\
                .where("session_id", "==", session_id)\
                .order_by("timestamp", direction="ASCENDING")
            
            activities = []
            async for doc in query.stream():
                activity_data = doc.to_dict()
                activities.append(StudyActivity(**activity_data))
            
            return activities
            
        except Exception as e:
            logger.error(f"Failed to get session activities: {e}")
            return []
    
    def _calculate_session_analytics(
        self,
        session: StudySession,
        activities: List[StudyActivity]
    ) -> Dict[str, Any]:
        """Calculate analytics for a session."""
        try:
            # Calculate duration
            duration_minutes = 0
            if session.actual_start and session.actual_end:
                duration_minutes = (session.actual_end - session.actual_start).total_seconds() / 60
            elif session.actual_start:
                duration_minutes = (datetime.utcnow() - session.actual_start).total_seconds() / 60
            
            # Calculate activity breakdown
            activity_breakdown = {}
            total_duration = 0
            
            for activity in activities:
                activity_type = activity.activity_type.value
                if activity_type not in activity_breakdown:
                    activity_breakdown[activity_type] = {
                        "count": 0,
                        "total_duration": 0,
                        "average_duration": 0
                    }
                
                activity_breakdown[activity_type]["count"] += 1
                activity_breakdown[activity_type]["total_duration"] += activity.duration_minutes
                total_duration += activity.duration_minutes
            
            # Calculate averages
            for activity_type, data in activity_breakdown.items():
                if data["count"] > 0:
                    data["average_duration"] = data["total_duration"] / data["count"]
            
            # Calculate participation balance
            parent_activities = len([a for a in activities if a.participant_role == ParticipantRole.PARENT])
            child_activities = len([a for a in activities if a.participant_role == ParticipantRole.CHILD])
            
            return {
                "duration_minutes": duration_minutes,
                "total_activities": len(activities),
                "activity_breakdown": activity_breakdown,
                "participation_balance": {
                    "parent_activities": parent_activities,
                    "child_activities": child_activities,
                    "balance_ratio": parent_activities / max(child_activities, 1)
                },
                "progress_rate": session.progress_percentage / 100 if session.progress_percentage > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate session analytics: {e}")
            return {
                "duration_minutes": 0,
                "total_activities": 0,
                "activity_breakdown": {},
                "participation_balance": {},
                "progress_rate": 0
            }
    
    async def _generate_session_summary(
        self,
        session: StudySession,
        final_reflection: Optional[str]
    ) -> Dict[str, Any]:
        """Generate session summary."""
        try:
            # Build prompt for session summary
            prompt = f"""
Generate a summary for this completed study session.

Session Details:
- Subject: {session.subject}
- Topic: {session.topic}
- Type: {session.session_type.value}
- Duration: {(session.actual_end - session.actual_start).total_seconds() / 60 if session.actual_start and session.actual_end else 0:.1f} minutes
- Progress: {session.progress_percentage}%
- Achievements: {session.achievements}

Final Reflection: {final_reflection or 'No reflection provided'}

Requirements:
1. Summarize key learning outcomes
2. Highlight engagement levels
3. Identify strengths and areas for improvement
4. Suggest follow-up activities
5. Provide positive reinforcement

Format as JSON:
{{
    "learning_outcomes": ["outcome1", "outcome2"],
    "engagement_summary": "description of engagement",
    "strengths": ["strength1", "strength2"],
    "improvement_areas": ["area1", "area2"],
    "follow_up_suggestions": ["suggestion1", "suggestion2"],
    "positive_reinforcement": "encouraging message",
    "next_session_topics": ["topic1", "topic2"]
}}
"""
            
            # Generate content using AI service
            content_request = ContentRequest(
                content_type=ContentType.SUMMARY,
                prompt=prompt,
                user_id=session.parent_id,
                student_id=session.child_id,
                context={
                    "session": session.__dict__,
                    "final_reflection": final_reflection
                },
                metadata={"generation_type": "session_summary"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse summary
            try:
                import json
                summary = json.loads(result.content)
            except json.JSONDecodeError:
                # Fallback summary
                summary = {
                    "learning_outcomes": [f"Studied {session.topic}"],
                    "engagement_summary": "Session completed successfully",
                    "strengths": ["Participation"],
                    "improvement_areas": ["Practice"],
                    "follow_up_suggestions": ["Review concepts", "Practice more examples"],
                    "positive_reinforcement": "Great job today!",
                    "next_session_topics": [session.topic]
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate session summary: {e}")
            return {
                "learning_outcomes": [f"Studied {session.topic}"],
                "engagement_summary": "Session completed",
                "strengths": [],
                "improvement_areas": [],
                "follow_up_suggestions": ["Continue learning"],
                "positive_reinforcement": "Good effort!",
                "next_session_topics": []
            }
    
    async def _generate_session_insights(
        self,
        session: StudySession,
        activities: List[StudyActivity],
        analytics: Dict[str, Any]
    ) -> List[str]:
        """Generate insights from session data."""
        try:
            # Build prompt for insights
            prompt = f"""
Generate insights from this study session data.

Session Analytics:
{json.dumps(analytics, indent=2)}

Session Details:
- Type: {session.session_type.value}
- Subject: {session.subject}
- Topic: {session.topic}
- Duration: {analytics.get('duration_minutes', 0)} minutes
- Activities: {len(activities)}

Requirements:
1. Analyze engagement patterns
2. Identify effective teaching approaches
3. Assess collaboration quality
4. Spot learning breakthroughs
5. Provide actionable insights

Format as JSON array of strings:
["insight 1", "insight 2", ...]
"""
            
            # Generate content using AI service
            content_request = ContentRequest(
                content_type=ContentType.INSIGHT,
                prompt=prompt,
                user_id=session.parent_id,
                student_id=session.child_id,
                context={
                    "session": session.__dict__,
                    "activities": [a.__dict__ for a in activities],
                    "analytics": analytics
                },
                metadata={"generation_type": "session_insights"}
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
            
            # Fallback insights
            return [
                "Session showed good participation balance",
                "Consider using more visual aids in future sessions",
                "Child engagement was highest during practical activities"
            ]
            
        except Exception as e:
            logger.error(f"Failed to generate session insights: {e}")
            return ["Unable to generate insights at this time"]
    
    async def _generate_session_recommendations(
        self,
        session: StudySession,
        analytics: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on session data."""
        try:
            # Build prompt for recommendations
            prompt = f"""
Generate recommendations for future study sessions.

Session Analytics:
{json.dumps(analytics, indent=2)}

Session Details:
- Type: {session.session_type.value}
- Subject: {session.subject}
- Topic: {session.topic}
- Progress Rate: {analytics.get('progress_rate', 0):.1%}

Requirements:
1. Suggest session structure improvements
2. Recommend activity types that worked well
3. Propose timing adjustments
4. Suggest resource additions
5. Provide engagement strategies

Format as JSON array of strings:
["recommendation 1", "recommendation 2", ...]
"""
            
            # Generate content using AI service
            content_request = ContentRequest(
                content_type=ContentType.RECOMMENDATION,
                prompt=prompt,
                user_id=session.parent_id,
                student_id=session.child_id,
                context={
                    "session": session.__dict__,
                    "analytics": analytics
                },
                metadata={"generation_type": "session_recommendations"}
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
            
            # Fallback recommendations
            return [
                "Include more hands-on activities",
                "Break complex topics into smaller sessions",
                "Use visual aids and examples",
                "Schedule regular practice sessions"
            ]
            
        except Exception as e:
            logger.error(f"Failed to generate session recommendations: {e}")
            return ["Continue with current approach and monitor progress"]

# Service instance
_interactive_study_tools_service_instance = None

def get_interactive_study_tools_service(
    db: Optional[firestore.Client] = None,
    unified_config: Optional[GeminiConfig] = None,
    enable_database_persistence: bool = True,
    session_timeout_minutes: int = 120,
    max_activities_per_session: int = 50
) -> InteractiveStudyToolsService:
    """
    Get singleton instance of Interactive Study Tools Service.
    
    Args:
        db: Firestore client (creates new if None)
        unified_config: Optional unified configuration
        enable_database_persistence: Enable saving to database
        session_timeout_minutes: Session timeout in minutes
        max_activities_per_session: Maximum activities per session
    
    Returns:
        InteractiveStudyToolsService instance
    """
    global _interactive_study_tools_service_instance
    
    if _interactive_study_tools_service_instance is None:
        logger.info("Creating new InteractiveStudyToolsService singleton instance")
        _interactive_study_tools_service_instance = InteractiveStudyToolsService(
            db=db,
            unified_config=unified_config,
            enable_database_persistence=enable_database_persistence,
            session_timeout_minutes=session_timeout_minutes,
            max_activities_per_session=max_activities_per_session
        )
    
    return _interactive_study_tools_service_instance

# Module initialization
logger.info("Interactive Study Tools Service module loaded")