"""
Gamified Parent Engagement Service

This service provides gamification features to increase
parent engagement and motivation.

Features:
- Parent engagement metrics tracking
- Weekly challenge system
- Achievement and badge system
- Parent-child activity tracking
- Streak rewards and milestones
- Level progression system
- Leaderboards for parent engagement
- Engagement analytics and insights

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
import statistics

from pydantic import BaseModel, Field
from google.cloud import firestore

from services.unified_gemini_config_service import get_unified_gemini_service, GeminiConfig
from services.ai_content_service import get_ai_content_service, ContentType, ContentRequest
from utils.firebase_config import get_firestore_client
from models.database_models import EngagementMetric, StudySession

# Configure logging
logger = logging.getLogger(__name__)

# Gamification enums and types
class EngagementType(Enum):
    """Types of engagement activities."""
    DAILY_CHECK_IN = "daily_check_in"
    WEEKLY_CHALLENGE = "weekly_challenge"
    ACTIVITY_LOGGING = "activity_logging"
    INSIGHT_REVIEW = "insight_review"
    COMMUNICATION_INITIATIVE = "communication_initiative"
    RESOURCE_EXPLORATION = "resource_exploration"
    GOAL_SETTING = "goal_setting"
    MILESTONE_CELEBRATION = "milestone_celebration"

class BadgeType(Enum):
    """Types of badges."""
    FIRST_STEPS = "first_steps"
    CONSISTENCY = "consistency"
    SUPER_PARENT = "super_parent"
    COMMUNICATOR = "communicator"
    ANALYZER = "analyzer"
    MOTIVATOR = "motivator"
    EXPLORER = "explorer"
    ACHIEVER = "achiever"
    MENTOR = "mentor"

class ChallengeType(Enum):
    """Types of weekly challenges."""
    ENGAGEMENT_BOOST = "engagement_boost"
    COMMUNICATION_FOCUS = "communication_focus"
    ACTIVITY_PLANNING = "activity_planning"
    INSIGHT_APPLICATION = "insight_application"
    GOAL_ACHIEVEMENT = "goal_achievement"
    LEARNING_TOGETHER = "learning_together"

class RewardType(Enum):
    """Types of rewards."""
    POINTS = "points"
    BADGE = "badge"
    LEVEL_UP = "level_up"
    STREAK = "streak"
    MILESTONE = "milestone"
    LEADERBOARD_RANK = "leaderboard_rank"

class DifficultyLevel(Enum):
    """Difficulty levels for challenges."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

@dataclass
class EngagementEvent:
    """Event for engagement tracking."""
    
    parent_id: str
    student_id: str
    engagement_type: EngagementType
    event_data: Dict[str, Any]
    timestamp: datetime
    points_earned: int
    engagement_score: float = 0.0
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Challenge:
    """Weekly challenge definition."""
    
    challenge_id: str
    title: str
    description: str
    challenge_type: ChallengeType
    requirements: List[str]
    points_reward: int
    badge_reward: Optional[BadgeType]
    duration_days: int
    difficulty: str
    created_at: datetime

@dataclass
class Achievement:
    """Achievement definition."""
    
    achievement_id: str
    title: str
    description: str
    badge_type: BadgeType
    points_reward: int
    requirements: Dict[str, Any]
    category: str
    created_at: datetime

@dataclass
class ParentProfile:
    """Parent engagement profile."""
    
    parent_id: str
    level: int
    total_points: int
    current_streak: int
    longest_streak: int
    badges_earned: List[BadgeType]
    challenges_completed: int
    weekly_rank: Optional[int] = None
    monthly_rank: Optional[int] = None
    last_active: Optional[datetime] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

class GamifiedEngagementService:
    """
    Service for gamified parent engagement tracking and rewards.
    
    This service provides comprehensive gamification features to increase
    parent motivation and consistent engagement with their child's education.
    
    Attributes:
        unified_service: Unified Gemini configuration service
        ai_content_service: AI content generation service
        db: Firestore database client
        challenge_generator: AI-powered challenge generator
        badge_system: Badge and achievement tracking
        leaderboard_manager: Leaderboard calculations and rankings
    
    Example:
        >>> service = GamifiedEngagementService()
        >>> result = service.track_engagement(
        ...     parent_id="parent123",
        ...     student_id="student123",
        ...     engagement_type=EngagementType.DAILY_CHECK_IN
        ... )
        >>> print(f"Points earned: {result.points_earned}")
    """
    
    def __init__(
        self,
        db: Optional[firestore.Client] = None,
        unified_config: Optional[GeminiConfig] = None,
        enable_database_persistence: bool = True,
        cache_size: int = 100,
        cache_ttl_hours: int = 4
    ):
        """
        Initialize Gamified Engagement Service.
        
        Args:
            db: Firestore client (creates new if None)
            unified_config: Optional unified configuration
            enable_database_persistence: Enable saving to database
            cache_size: Maximum cache size
            cache_ttl_hours: Cache TTL in hours
        """
        logger.info("Initializing GamifiedEngagementService")
        
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
        
        # Engagement cache
        self.engagement_cache: Dict[str, Any] = {}
        
        # Collections
        self.engagement_events_collection = "engagement_events"
        self.parent_profiles_collection = "parent_profiles"
        self.weekly_challenges_collection = "weekly_challenges"
        self.achievements_collection = "achievements"
        self.leaderboards_collection = "leaderboards"
        
        # Gamification settings
        self.point_values = {
            EngagementType.DAILY_CHECK_IN: 10,
            EngagementType.WEEKLY_CHALLENGE: 50,
            EngagementType.ACTIVITY_LOGGING: 15,
            EngagementType.INSIGHT_REVIEW: 25,
            EngagementType.COMMUNICATION_INITIATIVE: 20,
            EngagementType.RESOURCE_EXPLORATION: 15,
            EngagementType.GOAL_SETTING: 30,
            EngagementType.MILESTONE_CELEBRATION: 40
        }
        
        self.level_requirements = {
            1: 0,      # Starting level
            2: 100,     # Level 2 requires 100 points
            3: 250,     # Level 3 requires 250 points
            4: 500,     # Level 4 requires 500 points
            5: 1000,    # Level 5 requires 1000 points
            6: 2000,    # Level 6 requires 2000 points
            7: 3500,    # Level 7 requires 3500 points
            8: 5500,    # Level 8 requires 5500 points
            9: 8000,    # Level 9 requires 8000 points
            10: 12000   # Level 10 requires 12000 points
        }
        
        # Metrics
        self.metrics = {
            "total_engagement_events": 0,
            "engagement_by_type": {et.value: 0 for et in EngagementType},
            "total_points_awarded": 0,
            "total_badges_earned": 0,
            "total_challenges_completed": 0,
            "average_engagement_score": 0.0,
            "active_parents": 0,
            "weekly_challenges_generated": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "database_saves": 0,
            "database_failures": 0
        }
        
        logger.info(
            f"GamifiedEngagementService initialized (db_persistence={enable_database_persistence}, "
            f"cache_size={cache_size}, cache_ttl={cache_ttl_hours}h)"
        )
    
    async def track_engagement(
        self,
        event: EngagementEvent
    ) -> Dict[str, Any]:
        """
        Track parent engagement event and award points.
        
        Args:
            event: EngagementEvent with all event details
        
        Returns:
            Dict with tracking results and rewards
        
        Raises:
            ValueError: If event is invalid
            Exception: If tracking fails
        """
        start_time = time.time()
        
        logger.info(
            f"Tracking engagement event: {event.engagement_type.value} for parent {event.parent_id}"
        )
        
        try:
            # Get parent profile
            profile = await self._get_parent_profile(event.parent_id)
            
            # Calculate points earned
            base_points = self.point_values.get(event.engagement_type, 0)
            multiplier = self._calculate_point_multiplier(profile, event)
            points_earned = int(base_points * multiplier)
            
            # Update streak
            new_streak = self._update_streak(profile, event)
            
            # Check for level up
            new_level = self._check_level_up(profile, points_earned)
            
            # Check for new badges
            new_badges = await self._check_badge_achievements(profile, event)
            
            # Create engagement record
            engagement_record = {
                "event_id": f"eng_{event.parent_id}_{int(time.time())}_{hashlib.md5(event.engagement_type.value.encode()).hexdigest()[:8]}",
                "parent_id": event.parent_id,
                "student_id": event.student_id,
                "engagement_type": event.engagement_type.value,
                "event_data": event.event_data,
                "timestamp": event.timestamp,
                "points_earned": points_earned,
                "multiplier": multiplier,
                "streak_before": profile.current_streak,
                "streak_after": new_streak,
                "level_before": profile.level,
                "level_after": new_level,
                "badges_earned": [badge.value for badge in new_badges],
                "metadata": event.metadata or {}
            }
            
            # Update profile
            updated_profile = await self._update_parent_profile(
                profile, points_earned, new_streak, new_level, new_badges
            )
            
            # Save to database
            if self.enable_database_persistence:
                await self._save_engagement_event(engagement_record)
                await self._save_parent_profile(updated_profile)
            
            # Calculate generation time
            generation_time_ms = int((time.time() - start_time) * 1000)
            
            # Update metrics
            self.metrics["total_engagement_events"] += 1
            self.metrics["engagement_by_type"][event.engagement_type.value] += 1
            self.metrics["total_points_awarded"] += points_earned
            self.metrics["total_badges_earned"] += len(new_badges)
            if new_level > profile.level:
                self.metrics["level_ups"] = self.metrics.get("level_ups", 0) + 1
            
            # Update engagement score
            engagement_score = self._calculate_engagement_score(updated_profile)
            
            result = {
                "success": True,
                "event_id": engagement_record["event_id"],
                "points_earned": points_earned,
                "multiplier": multiplier,
                "new_streak": new_streak,
                "level_up": new_level > profile.level,
                "new_level": new_level,
                "badges_earned": [badge.value for badge in new_badges],
                "engagement_score": engagement_score,
                "generation_time_ms": generation_time_ms,
                "updated_profile": updated_profile
            }
            
            logger.info(
                f"Engagement tracked: {points_earned} points, streak: {new_streak}, "
                f"level: {new_level}, badges: {len(new_badges)}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Engagement tracking failed: {e}")
            
            # Update metrics
            if self.enable_database_persistence:
                self.metrics["database_failures"] += 1
            
            return {
                "success": False,
                "error": str(e),
                "points_earned": 0,
                "generation_time_ms": int((time.time() - start_time) * 1000)
            }
    
    async def generate_weekly_challenge(
        self,
        parent_id: str,
        student_id: str,
        challenge_type: Optional[ChallengeType] = None,
        difficulty: str = "medium",
        personalized: bool = True
    ) -> Dict[str, Any]:
        """
        Generate AI-powered weekly challenge.
        
        Args:
            parent_id: Parent ID
            student_id: Student ID
            challenge_type: Optional type of challenge
            difficulty: Challenge difficulty (easy, medium, hard)
            personalized: Whether to personalize based on history
        
        Returns:
            Dict with generated challenge and metadata
        """
        start_time = time.time()
        
        logger.info(f"Generating weekly challenge for parent {parent_id}")
        
        try:
            # Get parent profile and engagement history
            profile = await self._get_parent_profile(parent_id)
            engagement_history = await self._get_engagement_history(parent_id, 30)  # Last 30 days
            
            # Build prompt for challenge generation
            prompt = self._build_challenge_prompt(
                profile, engagement_history, student_id, challenge_type, difficulty, personalized
            )
            
            # Generate challenge using AI service
            content_request = ContentRequest(
                content_type=ContentType.RECOMMENDATION,
                prompt=prompt,
                user_id=parent_id,
                student_id=student_id,
                context={
                    "profile": profile,
                    "engagement_history": engagement_history,
                    "challenge_type": challenge_type.value if challenge_type else None,
                    "difficulty": difficulty,
                    "personalized": personalized
                },
                metadata={"generation_type": "weekly_challenge"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse challenge
            challenge_data = self._parse_challenge_response(result.content)
            
            # Create challenge record
            challenge_record = {
                "challenge_id": f"chal_{parent_id}_{int(time.time())}_{hashlib.md5(result.content.encode()).hexdigest()[:8]}",
                "parent_id": parent_id,
                "student_id": student_id,
                "title": challenge_data.get("title", "Weekly Challenge"),
                "description": challenge_data.get("description", ""),
                "challenge_type": challenge_data.get("challenge_type", ChallengeType.ENGAGEMENT_BOOST.value),
                "requirements": challenge_data.get("requirements", []),
                "points_reward": challenge_data.get("points_reward", 50),
                "badge_reward": challenge_data.get("badge_reward"),
                "duration_days": 7,
                "difficulty": difficulty,
                "created_at": datetime.utcnow(),
                "status": "active",
                "ai_generated": True,
                "personalized": personalized
            }
            
            # Save to database
            if self.enable_database_persistence:
                await self._save_weekly_challenge(challenge_record)
            
            # Calculate generation time
            generation_time_ms = int((time.time() - start_time) * 1000)
            
            # Update metrics
            self.metrics["weekly_challenges_generated"] += 1
            
            result = {
                "success": True,
                "challenge": challenge_record,
                "generation_time_ms": generation_time_ms
            }
            
            logger.info(f"Generated weekly challenge: {challenge_record['title']}")
            return result
            
        except Exception as e:
            logger.error(f"Challenge generation failed: {e}")
            
            # Update metrics
            if self.enable_database_persistence:
                self.metrics["database_failures"] += 1
            
            return {
                "success": False,
                "error": str(e),
                "generation_time_ms": int((time.time() - start_time) * 1000)
            }
    
    async def complete_challenge(
        self,
        challenge_id: str,
        parent_id: str,
        completion_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Mark weekly challenge as completed and award rewards.
        
        Args:
            challenge_id: Challenge ID
            parent_id: Parent ID
            completion_data: Completion details and evidence
        
        Returns:
            Dict with completion results and rewards
        """
        try:
            # Get challenge details
            challenge = await self._get_weekly_challenge(challenge_id)
            if not challenge:
                return {
                    "success": False,
                    "error": "Challenge not found"
                }
            
            # Get parent profile
            profile = await self._get_parent_profile(parent_id)
            
            # Calculate rewards
            points_reward = challenge.get("points_reward", 50)
            badge_reward = challenge.get("badge_reward")
            
            # Update challenge status
            challenge_update = {
                "status": "completed",
                "completed_at": datetime.utcnow(),
                "completion_data": completion_data,
                "points_awarded": points_reward,
                "badge_awarded": badge_reward.value if badge_reward else None
            }
            
            # Update challenge in database
            if self.enable_database_persistence:
                await self._update_weekly_challenge(challenge_id, challenge_update)
            
            # Track completion as engagement event
            completion_event = EngagementEvent(
                parent_id=parent_id,
                student_id=challenge.get("student_id"),
                engagement_type=EngagementType.WEEKLY_CHALLENGE,
                event_data={
                    "challenge_id": challenge_id,
                    "challenge_type": challenge.get("challenge_type"),
                    "completion_data": completion_data
                },
                timestamp=datetime.utcnow(),
                points_earned=points_reward
            )
            
            # Track engagement and update profile
            tracking_result = await self.track_engagement(completion_event)
            
            result = {
                "success": True,
                "challenge_id": challenge_id,
                "points_awarded": points_reward,
                "badge_awarded": badge_reward.value if badge_reward else None,
                "updated_profile": tracking_result.get("updated_profile"),
                "completion_tracking": tracking_result
            }
            
            logger.info(f"Challenge completed: {challenge_id}, points: {points_reward}")
            return result
            
        except Exception as e:
            logger.error(f"Challenge completion failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_leaderboard(
        self,
        leaderboard_type: str = "weekly",
        limit: int = 50,
        include_self: bool = True,
        parent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get engagement leaderboard rankings.
        
        Args:
            leaderboard_type: Type of leaderboard (weekly, monthly, all_time)
            limit: Maximum number of results
            include_self: Include requesting parent in results
            parent_id: Parent ID for highlighting
        
        Returns:
            Dict with leaderboard data and rankings
        """
        try:
            # Get all parent profiles
            profiles_query = self.db.collection(self.parent_profiles_collection)\
                .order_by("total_points", direction="DESCENDING")\
                .limit(limit)
            
            profiles = []
            async for doc in profiles_query.stream():
                profile_data = doc.to_dict()
                profiles.append(profile_data)
            
            # Calculate rankings
            leaderboard = []
            for i, profile in enumerate(profiles, 1):
                rank_data = {
                    "rank": i,
                    "parent_id": profile["parent_id"],
                    "level": profile["level"],
                    "total_points": profile["total_points"],
                    "current_streak": profile["current_streak"],
                    "engagement_score": profile["engagement_score"],
                    "badges_count": len(profile.get("badges_earned", [])),
                    "challenges_completed": profile.get("challenges_completed", 0),
                    "last_active": profile.get("last_active"),
                    "is_self": profile["parent_id"] == parent_id if parent_id else False
                }
                leaderboard.append(rank_data)
            
            # Filter by time period if needed
            if leaderboard_type != "all_time":
                filtered_leaderboard = await self._filter_leaderboard_by_period(
                    leaderboard, leaderboard_type
                )
            else:
                filtered_leaderboard = leaderboard
            
            result = {
                "leaderboard_type": leaderboard_type,
                "total_parents": len(filtered_leaderboard),
                "leaderboard": filtered_leaderboard,
                "generated_at": datetime.utcnow().isoformat(),
                "period_start": self._get_period_start(leaderboard_type).isoformat(),
                "period_end": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Generated {leaderboard_type} leaderboard with {len(filtered_leaderboard)} parents")
            return result
            
        except Exception as e:
            logger.error(f"Leaderboard generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "leaderboard_type": leaderboard_type
            }
    
    async def get_engagement_analytics(
        self,
        parent_id: str,
        time_period_days: int = 30,
        include_benchmarks: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive engagement analytics for parent.
        
        Args:
            parent_id: Parent ID
            time_period_days: Period to analyze
            include_benchmarks: Include benchmark comparisons
        
        Returns:
            Dict with engagement analytics and insights
        """
        try:
            # Get parent profile
            profile = await self._get_parent_profile(parent_id)
            
            # Get engagement history
            engagement_history = await self._get_engagement_history(parent_id, time_period_days)
            
            # Calculate analytics
            analytics = self._calculate_engagement_analytics(
                profile, engagement_history, time_period_days
            )
            
            # Generate benchmarks if requested
            benchmarks = {}
            if include_benchmarks:
                benchmarks = await self._generate_engagement_benchmarks(
                    profile, analytics
                )
            
            # Generate insights
            insights = await self._generate_engagement_insights(
                profile, analytics, benchmarks
            )
            
            result = {
                "parent_id": parent_id,
                "period_days": time_period_days,
                "profile": profile,
                "analytics": analytics,
                "benchmarks": benchmarks,
                "insights": insights,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Generated engagement analytics for parent {parent_id}")
            return result
            
        except Exception as e:
            logger.error(f"Engagement analytics failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "parent_id": parent_id
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
            "service": "gamified_engagement_service",
            "metrics": self.metrics,
            "derived": {
                "cache_hit_rate": cache_hit_rate,
                "average_points_per_event": (
                    self.metrics["total_points_awarded"] / max(self.metrics["total_engagement_events"], 1)
                ),
                "database_success_rate": (
                    (self.metrics["database_saves"] / 
                     max(self.metrics["database_saves"] + self.metrics["database_failures"], 1)) * 100
                )
            },
            "engagement_type_breakdown": {
                et: count for et, count in self.metrics["engagement_by_type"].items()
            },
            "point_values": self.point_values,
            "level_requirements": self.level_requirements
        }
    
    # ========================================================================
    # PRIVATE METHODS
    # ========================================================================
    
    async def _get_parent_profile(self, parent_id: str) -> ParentProfile:
        """Get or create parent profile."""
        try:
            doc_ref = self.db.collection(self.parent_profiles_collection).document(parent_id)
            doc = await doc_ref.get()
            
            if doc.exists:
                profile_data = doc.to_dict()
                return ParentProfile(**profile_data)
            else:
                # Create new profile
                new_profile = ParentProfile(
                    parent_id=parent_id,
                    level=1,
                    total_points=0,
                    current_streak=0,
                    longest_streak=0,
                    badges_earned=[],
                    challenges_completed=0,
                    engagement_score=0.0,
                    last_active=datetime.utcnow(),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                if self.enable_database_persistence:
                    await doc_ref.set(new_profile.model_dump())
                    self.metrics["database_saves"] += 1
                
                return new_profile
                
        except Exception as e:
            logger.error(f"Failed to get parent profile: {e}")
            # Return default profile
            return ParentProfile(
                parent_id=parent_id,
                level=1,
                total_points=0,
                current_streak=0,
                longest_streak=0,
                badges_earned=[],
                challenges_completed=0,
                engagement_score=0.0,
                last_active=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
    
    async def _get_engagement_history(
        self,
        parent_id: str,
        days: int
    ) -> List[Dict[str, Any]]:
        """Get engagement history for parent."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            query = self.db.collection(self.engagement_events_collection)\
                .where("parent_id", "==", parent_id)\
                .where("timestamp", ">=", start_date)\
                .where("timestamp", "<=", end_date)\
                .order_by("timestamp", direction="DESCENDING")
            
            history = []
            async for doc in query.stream():
                history.append(doc.to_dict())
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get engagement history: {e}")
            return []
    
    async def _get_weekly_challenge(self, challenge_id: str) -> Optional[Dict[str, Any]]:
        """Get weekly challenge details."""
        try:
            doc_ref = self.db.collection(self.weekly_challenges_collection).document(challenge_id)
            doc = await doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get weekly challenge: {e}")
            return None
    
    def _calculate_point_multiplier(self, profile: ParentProfile, event: EngagementEvent) -> float:
        """Calculate point multiplier based on profile and event."""
        base_multiplier = 1.0
        
        # Streak bonus
        if profile.current_streak >= 7:
            base_multiplier += 0.5
        elif profile.current_streak >= 14:
            base_multiplier += 1.0
        
        # Level bonus
        if profile.level >= 5:
            base_multiplier += 0.2
        elif profile.level >= 8:
            base_multiplier += 0.5
        
        # Engagement diversity bonus
        # This would be calculated based on recent engagement types
        
        return base_multiplier
    
    def _update_streak(self, profile: ParentProfile, event: EngagementEvent) -> int:
        """Update engagement streak."""
        today = event.timestamp.date()
        last_active = profile.last_active.date()
        
        if today == last_active:
            # Same day, maintain streak
            return profile.current_streak
        elif today == last_active + timedelta(days=1):
            # Next day, increment streak
            return profile.current_streak + 1
        else:
            # Gap in engagement, reset streak
            return 1
    
    def _check_level_up(self, profile: ParentProfile, points_earned: int) -> int:
        """Check if parent levels up."""
        new_total_points = profile.total_points + points_earned
        
        for level, required_points in self.level_requirements.items():
            if new_total_points >= required_points and profile.level < level:
                return level
        
        return profile.level
    
    async def _check_badge_achievements(self, profile: ParentProfile, event: EngagementEvent) -> List[BadgeType]:
        """Check for new badge achievements."""
        new_badges = []
        badges_earned_set = set(profile.badges_earned)
        
        # Check various badge conditions
        if event.engagement_type == EngagementType.DAILY_CHECK_IN and profile.current_streak >= 7:
            if BadgeType.CONSISTENCY not in badges_earned_set:
                new_badges.append(BadgeType.CONSISTENCY)
        
        if profile.total_points >= 500 and BadgeType.ACHIEVER not in badges_earned_set:
            new_badges.append(BadgeType.ACHIEVER)
        
        if profile.challenges_completed >= 5 and BadgeType.SUPER_PARENT not in badges_earned_set:
            new_badges.append(BadgeType.SUPER_PARENT)
        
        # Add more badge checks as needed
        
        return new_badges
    
    async def _update_parent_profile(
        self,
        profile: ParentProfile,
        points_earned: int,
        new_streak: int,
        new_level: int,
        new_badges: List[BadgeType]
    ) -> ParentProfile:
        """Update parent profile with new achievements."""
        updated_profile = ParentProfile(
            parent_id=profile.parent_id,
            level=new_level,
            total_points=profile.total_points + points_earned,
            current_streak=new_streak,
            longest_streak=max(profile.longest_streak, new_streak),
            badges_earned=profile.badges_earned + new_badges,
            challenges_completed=profile.challenges_completed + (1 if new_level > profile.level else 0),
            engagement_score=0.0,  # Will be recalculated
            last_active=datetime.utcnow(),
            created_at=profile.created_at,
            updated_at=datetime.utcnow()
        )
        
        # Recalculate engagement score
        updated_profile.engagement_score = self._calculate_engagement_score(updated_profile)
        
        # Save to database
        if self.enable_database_persistence:
            doc_ref = self.db.collection(self.parent_profiles_collection).document(profile.parent_id)
            await doc_ref.set(updated_profile.model_dump())
            self.metrics["database_saves"] += 1
        
        return updated_profile
    
    def _calculate_engagement_score(self, profile: ParentProfile) -> float:
        """Calculate overall engagement score."""
        # Weighted components
        level_score = profile.level * 10  # Max 100
        points_score = min(profile.total_points / 100, 50)  # Max 50
        streak_score = min(profile.current_streak * 2, 20)  # Max 20
        badges_score = len(profile.badges_earned) * 3  # Max 30
        
        total_score = level_score + points_score + streak_score + badges_score
        return min(total_score, 100.0)  # Cap at 100
    
    async def _save_engagement_event(self, event_record: Dict[str, Any]):
        """Save engagement event to database."""
        try:
            doc_ref = self.db.collection(self.engagement_events_collection).document(event_record["event_id"])
            await doc_ref.set(event_record)
            logger.debug(f"Saved engagement event: {event_record['event_id']}")
            
        except Exception as e:
            logger.error(f"Failed to save engagement event: {e}")
            self.metrics["database_failures"] += 1
    
    async def _save_parent_profile(self, profile: ParentProfile):
        """Save parent profile to database."""
        try:
            doc_ref = self.db.collection(self.parent_profiles_collection).document(profile.parent_id)
            await doc_ref.set(profile.model_dump())
            logger.debug(f"Saved parent profile: {profile.parent_id}")
            
        except Exception as e:
            logger.error(f"Failed to save parent profile: {e}")
            self.metrics["database_failures"] += 1
    
    async def _save_weekly_challenge(self, challenge_record: Dict[str, Any]):
        """Save weekly challenge to database."""
        try:
            doc_ref = self.db.collection(self.weekly_challenges_collection).document(challenge_record["challenge_id"])
            await doc_ref.set(challenge_record)
            logger.debug(f"Saved weekly challenge: {challenge_record['challenge_id']}")
            
        except Exception as e:
            logger.error(f"Failed to save weekly challenge: {e}")
            self.metrics["database_failures"] += 1
    
    async def _update_weekly_challenge(self, challenge_id: str, update_data: Dict[str, Any]):
        """Update weekly challenge in database."""
        try:
            doc_ref = self.db.collection(self.weekly_challenges_collection).document(challenge_id)
            await doc_ref.update(update_data)
            logger.debug(f"Updated weekly challenge: {challenge_id}")
            
        except Exception as e:
            logger.error(f"Failed to update weekly challenge: {e}")
            self.metrics["database_failures"] += 1
    
    def _build_challenge_prompt(
        self,
        profile: ParentProfile,
        engagement_history: List[Dict[str, Any]],
        student_id: str,
        challenge_type: Optional[ChallengeType],
        difficulty: str,
        personalized: bool
    ) -> str:
        """Build prompt for challenge generation."""
        return f"""
Generate an engaging weekly challenge for parent engagement.

Parent Profile:
- Level: {profile.level}
- Current Streak: {profile.current_streak} days
- Badges Earned: {len(profile.badges_earned)}
- Engagement Score: {profile.engagement_score}

Recent Engagement:
{json.dumps(engagement_history[:5], indent=2)}

Challenge Parameters:
- Type: {challenge_type.value if challenge_type else 'any'}
- Difficulty: {difficulty}
- Personalized: {personalized}
- Duration: 7 days

Requirements:
1. Create an engaging, achievable challenge
2. Align with parent's current level and engagement patterns
3. Include clear requirements and success criteria
4. Provide appropriate difficulty progression
5. Make it meaningful for parent-child relationship
6. Include learning or growth opportunity

Format as JSON:
{{
    "title": "Challenge Title",
    "description": "Detailed description of the challenge",
    "challenge_type": "challenge_type",
    "requirements": ["requirement1", "requirement2", "requirement3"],
    "points_reward": 50,
    "badge_reward": "badge_type",
    "difficulty": "{difficulty}",
    "success_criteria": ["criteria1", "criteria2"],
    "tips": ["tip1", "tip2"],
    "learning_outcome": "description of learning outcome"
}}
"""
    
    def _parse_challenge_response(self, content: str) -> Dict[str, Any]:
        """Parse challenge from AI response."""
        try:
            # Try to parse as JSON
            import json
            challenge_data = json.loads(content)
            
            if isinstance(challenge_data, dict):
                return challenge_data
            else:
                # Fallback: return as basic challenge
                return {
                    "title": "Weekly Challenge",
                    "description": content,
                    "challenge_type": ChallengeType.ENGAGEMENT_BOOST.value,
                    "requirements": ["Complete the challenge"],
                    "points_reward": 50,
                    "badge_reward": None
                }
                
        except json.JSONDecodeError:
            # Fallback: return basic challenge
            return {
                "title": "Weekly Challenge",
                "description": content,
                "challenge_type": ChallengeType.ENGAGEMENT_BOOST.value,
                "requirements": ["Complete the challenge"],
                "points_reward": 50,
                "badge_reward": None
            }
    
    async def _filter_leaderboard_by_period(
        self,
        leaderboard: List[Dict[str, Any]],
        period_type: str
    ) -> List[Dict[str, Any]]:
        """Filter leaderboard by time period."""
        if period_type == "all_time":
            return leaderboard
        
        # Calculate period start date
        period_start = self._get_period_start(period_type)
        
        # Filter parents active in period
        filtered_leaderboard = []
        for entry in leaderboard:
            last_active = datetime.fromisoformat(entry["last_active"])
            if last_active >= period_start:
                filtered_leaderboard.append(entry)
        
        # Recalculate rankings for filtered list
        for i, entry in enumerate(filtered_leaderboard, 1):
            entry["rank"] = i
        
        return filtered_leaderboard
    
    def _get_period_start(self, period_type: str) -> datetime:
        """Get start date for leaderboard period."""
        now = datetime.utcnow()
        
        if period_type == "weekly":
            return now - timedelta(days=7)
        elif period_type == "monthly":
            return now - timedelta(days=30)
        else:
            return now - timedelta(days=365)  # All time
    
    def _calculate_engagement_analytics(
        self,
        profile: ParentProfile,
        engagement_history: List[Dict[str, Any]],
        time_period_days: int
    ) -> Dict[str, Any]:
        """Calculate engagement analytics."""
        if not engagement_history:
            return {
                "total_events": 0,
                "engagement_frequency": 0.0,
                "engagement_diversity": 0.0,
                "points_per_day": 0.0
            }
        
        # Calculate basic metrics
        total_events = len(engagement_history)
        engagement_frequency = total_events / time_period_days
        
        # Calculate diversity (different engagement types)
        engagement_types = set()
        for event in engagement_history:
            engagement_types.add(event["engagement_type"])
        engagement_diversity = len(engagement_types) / len(EngagementType)
        
        # Calculate points per day
        total_points = sum(event["points_earned"] for event in engagement_history)
        points_per_day = total_points / time_period_days
        
        # Calculate engagement type breakdown
        type_breakdown = {}
        for event in engagement_history:
            event_type = event["engagement_type"]
            if event_type not in type_breakdown:
                type_breakdown[event_type] = {"count": 0, "points": 0}
            type_breakdown[event_type]["count"] += 1
            type_breakdown[event_type]["points"] += event["points_earned"]
        
        return {
            "total_events": total_events,
            "engagement_frequency": engagement_frequency,
            "engagement_diversity": engagement_diversity,
            "points_per_day": points_per_day,
            "type_breakdown": type_breakdown,
            "average_points_per_event": total_points / total_events if total_events > 0 else 0
        }
    
    async def _generate_engagement_benchmarks(
        self,
        profile: ParentProfile,
        analytics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate engagement benchmarks."""
        try:
            # Build prompt for benchmark generation
            prompt = f"""
Generate engagement benchmarks for parent comparison.

Parent Profile:
- Level: {profile.level}
- Engagement Score: {profile.engagement_score}
- Current Streak: {profile.current_streak}

Current Analytics:
{json.dumps(analytics, indent=2)}

Requirements:
1. Generate realistic benchmarks for different engagement levels
2. Compare current performance with benchmarks
3. Identify areas above/below benchmarks
4. Provide percentile rankings
5. Suggest improvement targets

Format as JSON:
{{
    "benchmarks": {{
        "beginner": {{
            "engagement_frequency": 0.5,
            "points_per_day": 10,
            "streak_days": 3
        }},
        "intermediate": {{
            "engagement_frequency": 1.0,
            "points_per_day": 25,
            "streak_days": 7
        }},
        "advanced": {{
            "engagement_frequency": 2.0,
            "points_per_day": 50,
            "streak_days": 14
        }}
    }},
    "current_percentile": 75,
    "areas_above_benchmark": ["area1", "area2"],
    "areas_below_benchmark": ["area3", "area4"],
    "improvement_targets": ["target1", "target2"]
}}
"""
            
            # Generate content using AI service
            content_request = ContentRequest(
                content_type=ContentType.ANALYSIS,
                prompt=prompt,
                user_id=profile.parent_id,
                student_id="system",
                context={"profile": profile, "analytics": analytics},
                metadata={"generation_type": "engagement_benchmarks"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse benchmarks
            try:
                import json
                benchmarks = json.loads(result.content)
                
                if isinstance(benchmarks, dict):
                    return benchmarks
                    
            except json.JSONDecodeError:
                # Fallback benchmarks
                return {
                    "benchmarks": {"analysis": result.content},
                    "current_percentile": 50,
                    "areas_above_benchmark": [],
                    "areas_below_benchmark": [],
                    "improvement_targets": ["Continue consistent engagement"]
                }
                
        except Exception as e:
            logger.error(f"Failed to generate benchmarks: {e}")
            return {
                "benchmarks": {"error": str(e)},
                "current_percentile": 50,
                "areas_above_benchmark": [],
                "areas_below_benchmark": [],
                "improvement_targets": ["Continue consistent engagement"]
            }
    
    async def _generate_engagement_insights(
        self,
        profile: ParentProfile,
        analytics: Dict[str, Any],
        benchmarks: Dict[str, Any]
    ) -> List[str]:
        """Generate engagement insights."""
        try:
            # Build prompt for insights generation
            prompt = f"""
Generate insights about parent engagement patterns.

Parent Profile:
- Level: {profile.level}
- Engagement Score: {profile.engagement_score}
- Current Streak: {profile.current_streak}

Analytics:
{json.dumps(analytics, indent=2)}

Benchmarks:
{json.dumps(benchmarks, indent=2)}

Requirements:
1. Identify positive engagement patterns
2. Highlight areas for improvement
3. Recognize achievements and milestones
4. Provide actionable insights
5. Suggest specific engagement strategies

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
                user_id=profile.parent_id,
                student_id="system",
                context={"profile": profile, "analytics": analytics, "benchmarks": benchmarks},
                metadata={"generation_type": "engagement_insights"}
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
            logger.error(f"Failed to generate insights: {e}")
            return ["Unable to generate insights at this time"]

# Service instance
_gamified_engagement_service_instance = None

def get_gamified_engagement_service(
    db: Optional[firestore.Client] = None,
    unified_config: Optional[GeminiConfig] = None,
    enable_database_persistence: bool = True,
    cache_size: int = 100,
    cache_ttl_hours: int = 4
) -> GamifiedEngagementService:
    """
    Get singleton instance of Gamified Engagement Service.
    
    Args:
        db: Firestore client (creates new if None)
        unified_config: Optional unified configuration
        enable_database_persistence: Enable saving to database
        cache_size: Maximum cache size
        cache_ttl_hours: Cache TTL in hours
    
    Returns:
        GamifiedEngagementService instance
    """
    global _gamified_engagement_service_instance
    
    if _gamified_engagement_service_instance is None:
        logger.info("Creating new GamifiedEngagementService singleton instance")
        _gamified_engagement_service_instance = GamifiedEngagementService(
            db=db,
            unified_config=unified_config,
            enable_database_persistence=enable_database_persistence,
            cache_size=cache_size,
            cache_ttl_hours=cache_ttl_hours
        )
    
    return _gamified_engagement_service_instance

# Module initialization
logger.info("Gamified Engagement Service module loaded")