"""
Predictive Analytics Service for Early Warnings

This service provides predictive analytics and early warning systems
for identifying potential issues before they become critical.

Features:
- Performance trend analysis
- Risk factor identification
- Early warning indicators
- Intervention recommendation engine
- Predictive performance models
- Automated alert system
- What-if scenario planning
- Intervention effectiveness tracking

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
from models.database_models import EngagementMetric, InterventionAlert

# Configure logging
logger = logging.getLogger(__name__)

# Risk levels and alert types
class RiskLevel(Enum):
    """Risk levels for predictive analytics."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(Enum):
    """Types of predictive alerts."""
    PERFORMANCE_DROP = "performance_drop"
    LOW_ENGAGEMENT = "low_engagement"
    MISSED_GOALS = "missed_goals"
    WEAK_PERFORMANCE = "weak_performance"
    CRITICAL_ISSUE = "critical_issue"
    BURNOUT_RISK = "burnout_risk"
    KNOWLEDGE_GAP = "knowledge_gap"

class PredictionType(Enum):
    """Types of predictions."""
    PERFORMANCE_TREND = "performance_trend"
    ENGAGEMENT_PATTERN = "engagement_pattern"
    RISK_ASSESSMENT = "risk_assessment"
    INTERVENTION_NEED = "intervention_need"
    MILESTONE_PREDICTION = "milestone_prediction"

@dataclass
class PredictionRequest:
    """Request for predictive analysis."""
    
    student_id: str
    parent_id: str
    prediction_type: PredictionType
    time_period_days: int = 30
    include_recommendations: bool = True
    threshold_sensitivity: float = 0.7  # 0-1, higher = more sensitive
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class PredictionResult:
    """Result from predictive analysis."""
    
    prediction_id: str
    prediction_type: PredictionType
    risk_level: RiskLevel
    confidence_score: float
    predictions: Dict[str, Any]
    risk_factors: List[str]
    recommendations: List[str]
    alerts_triggered: List[Dict[str, Any]]
    time_horizon_days: int
    generation_time_ms: int
    created_at: datetime

class PredictiveAnalyticsService:
    """
    Service for predictive analytics and early warning systems.
    
    This service leverages AI and statistical analysis to identify potential
    issues before they become critical, providing early warnings and
    intervention recommendations.
    
    Attributes:
        unified_service: Unified Gemini configuration service
        ai_content_service: AI content generation service
        db: Firestore database client
        prediction_models: Handlers for different prediction types
        risk_thresholds: Configurable risk thresholds
        alert_history: Historical alert data
    
    Example:
        >>> service = PredictiveAnalyticsService()
        >>> result = service.generate_prediction(
        ...     student_id="student123",
        ...     parent_id="parent123",
        ...     prediction_type=PredictionType.PERFORMANCE_TREND
        ... )
        >>> print(f"Risk level: {result.risk_level.value}")
    """
    
    def __init__(
        self,
        db: Optional[firestore.Client] = None,
        unified_config: Optional[GeminiConfig] = None,
        enable_database_persistence: bool = True,
        cache_size: int = 100,
        cache_ttl_hours: int = 6
    ):
        """
        Initialize Predictive Analytics Service.
        
        Args:
            db: Firestore client (creates new if None)
            unified_config: Optional unified configuration
            enable_database_persistence: Enable saving to database
            cache_size: Maximum cache size
            cache_ttl_hours: Cache TTL in hours
        """
        logger.info("Initializing PredictiveAnalyticsService")
        
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
        
        # Prediction cache
        self.prediction_cache: Dict[str, PredictionResult] = {}
        
        # Collections
        self.predictions_collection = "predictions"
        self.engagement_metrics_collection = "engagement_metrics"
        self.intervention_alerts_collection = "intervention_alerts"
        
        # Risk thresholds (configurable)
        self.risk_thresholds = {
            "performance_decline_threshold": 0.15,  # 15% decline
            "engagement_drop_threshold": 0.25,     # 25% drop
            "consecutive_missed_days": 3,            # 3 days
            "accuracy_drop_threshold": 0.20,          # 20% drop
            "study_time_drop_threshold": 0.30,        # 30% drop
            "goal_miss_rate_threshold": 0.40,          # 40% miss rate
        }
        
        # Metrics
        self.metrics = {
            "total_predictions_generated": 0,
            "predictions_by_type": {pt.value: 0 for pt in PredictionType},
            "alerts_triggered": 0,
            "alerts_by_type": {at.value: 0 for at in AlertType},
            "average_confidence_score": 0.0,
            "false_positive_rate": 0.0,
            "intervention_effectiveness": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
            "database_saves": 0,
            "database_failures": 0
        }
        
        logger.info(
            f"PredictiveAnalyticsService initialized (db_persistence={enable_database_persistence}, "
            f"cache_size={cache_size}, cache_ttl={cache_ttl_hours}h)"
        )
    
    async def generate_prediction(
        self,
        request: PredictionRequest
    ) -> PredictionResult:
        """
        Generate predictive analysis for student.
        
        Args:
            request: PredictionRequest with all analysis parameters
        
        Returns:
            PredictionResult with predictions and recommendations
        
        Raises:
            ValueError: If request is invalid
            Exception: If prediction fails
        """
        start_time = time.time()
        
        # Generate prediction ID
        prediction_id = f"pred_{request.student_id}_{int(time.time())}_{hashlib.md5(f'{request.prediction_type.value}_{request.time_period_days}'.encode()).hexdigest()[:8]}"
        
        logger.info(
            f"Generating {request.prediction_type.value} prediction: {prediction_id}"
        )
        
        try:
            # Check cache
            cache_key = self._generate_cache_key(request)
            if cache_key in self.prediction_cache:
                cached_result = self.prediction_cache[cache_key]
                logger.info(f"Cache hit for prediction: {prediction_id}")
                
                # Update metrics
                self.metrics["cache_hits"] += 1
                
                return cached_result
            
            self.metrics["cache_misses"] += 1
            
            # Get historical data for analysis
            historical_data = await self._get_historical_data(
                request.student_id, 
                request.time_period_days * 2  # Get double period for trend analysis
            )
            
            # Route to appropriate predictor
            predictor = self.prediction_models.get(request.prediction_type)
            if not predictor:
                raise ValueError(f"No predictor for type: {request.prediction_type.value}")
            
            # Generate prediction
            prediction_data, generation_metadata = await predictor(request, historical_data)
            
            # Calculate metrics
            generation_time_ms = int((time.time() - start_time) * 1000)
            
            # Determine risk level
            risk_level = self._assess_risk_level(
                prediction_data.get("risk_score", 0.5),
                request.threshold_sensitivity
            )
            
            # Generate alerts if needed
            alerts_triggered = self._generate_alerts(
                prediction_data,
                risk_level,
                request.student_id,
                request.parent_id
            )
            
            # Create result
            result = PredictionResult(
                prediction_id=prediction_id,
                prediction_type=request.prediction_type,
                risk_level=risk_level,
                confidence_score=prediction_data.get("confidence_score", 0.7),
                predictions=prediction_data.get("predictions", {}),
                risk_factors=prediction_data.get("risk_factors", []),
                recommendations=prediction_data.get("recommendations", []),
                alerts_triggered=alerts_triggered,
                time_horizon_days=prediction_data.get("time_horizon_days", 14),
                generation_time_ms=generation_time_ms,
                created_at=datetime.utcnow()
            )
            
            # Cache result
            if len(self.prediction_cache) < self.cache_size:
                self.prediction_cache[cache_key] = result
            
            # Save to database
            if self.enable_database_persistence:
                await self._save_prediction_to_db(result, request)
                
                # Save alerts if any were triggered
                if alerts_triggered:
                    await self._save_alerts_to_db(alerts_triggered, request)
            
            # Update metrics
            self.metrics["total_predictions_generated"] += 1
            self.metrics["predictions_by_type"][request.prediction_type.value] += 1
            self.metrics["alerts_triggered"] += len(alerts_triggered)
            for alert in alerts_triggered:
                self.metrics["alerts_by_type"][alert.get("alert_type", "unknown")] += 1
            self._update_average_confidence(result.confidence_score)
            
            logger.info(
                f"Generated {request.prediction_type.value} prediction: {prediction_id}, "
                f"risk={risk_level.value}, confidence={result.confidence_score:.2f}, "
                f"alerts={len(alerts_triggered)}, time={generation_time_ms}ms"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction generation failed: {e}")
            
            # Update metrics
            if self.enable_database_persistence:
                self.metrics["database_failures"] += 1
            
            raise
    
    async def analyze_what_if_scenario(
        self,
        student_id: str,
        parent_id: str,
        scenario: Dict[str, Any],
        time_horizon_days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze what-if scenarios for planning purposes.
        
        Args:
            student_id: Student ID
            parent_id: Parent ID
            scenario: Scenario parameters (e.g., increased study time, new subjects)
            time_horizon_days: Time horizon for prediction
        
        Returns:
            Dict with scenario analysis and predictions
        """
        try:
            # Get current baseline data
            baseline_data = await self._get_historical_data(student_id, 30)
            
            # Build prompt for what-if analysis
            prompt = self._build_what_if_prompt(
                baseline_data, scenario, time_horizon_days
            )
            
            # Generate content using AI service
            content_request = ContentRequest(
                content_type=ContentType.ANALYSIS,
                prompt=prompt,
                user_id=parent_id,
                student_id=student_id,
                context={
                    "scenario": scenario,
                    "time_horizon_days": time_horizon_days,
                    "baseline_data": baseline_data
                },
                metadata={"analysis_type": "what_if_scenario"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse what-if analysis
            scenario_analysis = self._parse_what_if_response(result.content)
            
            logger.info(f"Generated what-if scenario analysis for student {student_id}")
            return scenario_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze what-if scenario: {e}")
            raise
    
    async def get_intervention_recommendations(
        self,
        student_id: str,
        parent_id: str,
        risk_factors: List[str],
        current_performance: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate intervention recommendations based on risk factors.
        
        Args:
            student_id: Student ID
            parent_id: Parent ID
            risk_factors: List of identified risk factors
            current_performance: Current performance data
        
        Returns:
            List of intervention recommendations with details
        """
        try:
            # Build prompt for intervention recommendations
            prompt = self._build_intervention_prompt(
                risk_factors, current_performance
            )
            
            # Generate content using AI service
            content_request = ContentRequest(
                content_type=ContentType.RECOMMENDATION,
                prompt=prompt,
                user_id=parent_id,
                student_id=student_id,
                context={
                    "risk_factors": risk_factors,
                    "current_performance": current_performance
                },
                metadata={"generation_type": "intervention_recommendations"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse intervention recommendations
            interventions = self._parse_intervention_recommendations(result.content)
            
            logger.info(f"Generated {len(interventions)} intervention recommendations")
            return interventions
            
        except Exception as e:
            logger.error(f"Failed to generate intervention recommendations: {e}")
            raise
    
    async def track_intervention_effectiveness(
        self,
        intervention_id: str,
        student_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Track and analyze effectiveness of interventions.
        
        Args:
            intervention_id: ID of the intervention
            student_id: Student ID
            start_date: Intervention start date
            end_date: Intervention end date
        
        Returns:
            Dict with effectiveness analysis
        """
        try:
            # Get data before and after intervention
            before_data = await self._get_historical_data(
                student_id, 
                days=(start_date - datetime.utcnow()).days
            )
            after_data = await self._get_historical_data(
                student_id,
                days=(end_date - start_date).days
            )
            
            # Analyze effectiveness
            effectiveness = self._calculate_intervention_effectiveness(
                before_data, after_data
            )
            
            logger.info(f"Analyzed intervention effectiveness: {intervention_id}")
            return effectiveness
            
        except Exception as e:
            logger.error(f"Failed to track intervention effectiveness: {e}")
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
            "service": "predictive_analytics_service",
            "metrics": self.metrics,
            "derived": {
                "cache_hit_rate": cache_hit_rate,
                "average_confidence_score": self.metrics["average_confidence_score"],
                "alerts_per_prediction": (
                    self.metrics["alerts_triggered"] / max(self.metrics["total_predictions_generated"], 1)
                ),
                "database_success_rate": (
                    (self.metrics["database_saves"] / 
                     max(self.metrics["database_saves"] + self.metrics["database_failures"], 1)) * 100
                )
            },
            "prediction_type_breakdown": {
                pt: count for pt, count in self.metrics["predictions_by_type"].items()
            },
            "alert_type_breakdown": {
                at: count for at, count in self.metrics["alerts_by_type"].items()
            },
            "risk_thresholds": self.risk_thresholds
        }
    
    # ========================================================================
    # PRIVATE METHODS
    # ========================================================================
    
    def _generate_cache_key(self, request: PredictionRequest) -> str:
        """Generate cache key for prediction request."""
        key_data = {
            "student_id": request.student_id,
            "prediction_type": request.prediction_type.value,
            "time_period_days": request.time_period_days,
            "threshold_sensitivity": request.threshold_sensitivity,
            "context": request.context
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    async def _get_historical_data(
        self, 
        student_id: str, 
        days: int
    ) -> Dict[str, Any]:
        """Get historical data for analysis."""
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
                .where("created_at", "<=", end_date)\
                .order_by("created_at", direction="DESCENDING")
            
            alerts = []
            async for doc in alerts_query.stream():
                alerts.append(doc.to_dict())
            
            return {
                "student_id": student_id,
                "period_days": days,
                "engagement_metrics": metrics,
                "intervention_alerts": alerts,
                "data_points": len(metrics),
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get historical data: {e}")
            return {
                "student_id": student_id,
                "period_days": days,
                "engagement_metrics": [],
                "intervention_alerts": [],
                "data_points": 0,
                "error": str(e)
            }
    
    def _assess_risk_level(
        self, 
        risk_score: float, 
        sensitivity: float
    ) -> RiskLevel:
        """Assess risk level based on score and sensitivity."""
        # Adjust thresholds based on sensitivity
        if sensitivity > 0.8:  # High sensitivity
            if risk_score >= 0.6:
                return RiskLevel.CRITICAL
            elif risk_score >= 0.4:
                return RiskLevel.HIGH
            elif risk_score >= 0.2:
                return RiskLevel.MEDIUM
            else:
                return RiskLevel.LOW
        elif sensitivity > 0.5:  # Medium sensitivity
            if risk_score >= 0.8:
                return RiskLevel.CRITICAL
            elif risk_score >= 0.6:
                return RiskLevel.HIGH
            elif risk_score >= 0.3:
                return RiskLevel.MEDIUM
            else:
                return RiskLevel.LOW
        else:  # Low sensitivity
            if risk_score >= 0.9:
                return RiskLevel.CRITICAL
            elif risk_score >= 0.7:
                return RiskLevel.HIGH
            elif risk_score >= 0.4:
                return RiskLevel.MEDIUM
            else:
                return RiskLevel.LOW
    
    def _generate_alerts(
        self,
        prediction_data: Dict[str, Any],
        risk_level: RiskLevel,
        student_id: str,
        parent_id: str
    ) -> List[Dict[str, Any]]:
        """Generate alerts based on prediction data and risk level."""
        alerts = []
        
        # Only generate alerts for medium risk and above
        if risk_level in [RiskLevel.LOW]:
            return alerts
        
        risk_factors = prediction_data.get("risk_factors", [])
        
        # Generate alerts based on risk factors
        for risk_factor in risk_factors:
            alert_type = self._map_risk_factor_to_alert_type(risk_factor)
            if alert_type:
                alert = {
                    "alert_id": f"alert_{student_id}_{int(time.time())}_{hashlib.md5(risk_factor.encode()).hexdigest()[:8]}",
                    "student_id": student_id,
                    "parent_id": parent_id,
                    "alert_type": alert_type.value,
                    "severity": risk_level.value,
                    "title": f"{alert_type.value.replace('_', ' ').title()} Alert",
                    "description": f"Risk factor detected: {risk_factor}",
                    "data": {
                        "risk_factor": risk_factor,
                        "prediction_data": prediction_data,
                        "risk_score": prediction_data.get("risk_score", 0.5)
                    },
                    "threshold_triggered": True,
                    "recommended_actions": prediction_data.get("recommendations", []),
                    "status": "new",
                    "created_at": datetime.utcnow().isoformat()
                }
                alerts.append(alert)
        
        return alerts
    
    def _map_risk_factor_to_alert_type(self, risk_factor: str) -> Optional[AlertType]:
        """Map risk factors to alert types."""
        risk_factor_lower = risk_factor.lower()
        
        if "performance" in risk_factor_lower and "decline" in risk_factor_lower:
            return AlertType.PERFORMANCE_DROP
        elif "engagement" in risk_factor_lower and ("low" in risk_factor_lower or "drop" in risk_factor_lower):
            return AlertType.LOW_ENGAGEMENT
        elif "goal" in risk_factor_lower and ("miss" in risk_factor_lower or "incomplete" in risk_factor_lower):
            return AlertType.MISSED_GOALS
        elif "weak" in risk_factor_lower or "poor" in risk_factor_lower:
            return AlertType.WEAK_PERFORMANCE
        elif "burnout" in risk_factor_lower or "stress" in risk_factor_lower:
            return AlertType.BURNOUT_RISK
        elif "gap" in risk_factor_lower or "missing" in risk_factor_lower:
            return AlertType.KNOWLEDGE_GAP
        elif "critical" in risk_factor_lower or "urgent" in risk_factor_lower:
            return AlertType.CRITICAL_ISSUE
        else:
            return None
    
    async def _save_prediction_to_db(self, result: PredictionResult, request: PredictionRequest):
        """Save prediction result to database."""
        try:
            prediction_record = {
                "prediction_id": result.prediction_id,
                "student_id": request.student_id,
                "parent_id": request.parent_id,
                "prediction_type": result.prediction_type.value,
                "risk_level": result.risk_level.value,
                "confidence_score": result.confidence_score,
                "predictions": result.predictions,
                "risk_factors": result.risk_factors,
                "recommendations": result.recommendations,
                "alerts_triggered": len(result.alerts_triggered),
                "time_horizon_days": result.time_horizon_days,
                "generation_time_ms": result.generation_time_ms,
                "threshold_sensitivity": request.threshold_sensitivity,
                "created_at": result.created_at,
                "metadata": request.metadata or {}
            }
            
            doc_ref = self.db.collection(self.predictions_collection).document(result.prediction_id)
            await doc_ref.set(prediction_record)
            
            self.metrics["database_saves"] += 1
            logger.debug(f"Saved prediction to database: {result.prediction_id}")
            
        except Exception as e:
            logger.error(f"Failed to save prediction to database: {e}")
            self.metrics["database_failures"] += 1
    
    async def _save_alerts_to_db(self, alerts: List[Dict[str, Any]], request: PredictionRequest):
        """Save alerts to database."""
        try:
            for alert in alerts:
                doc_ref = self.db.collection(self.intervention_alerts_collection).document(alert["alert_id"])
                await doc_ref.set(alert)
            
            logger.debug(f"Saved {len(alerts)} alerts to database")
            
        except Exception as e:
            logger.error(f"Failed to save alerts to database: {e}")
    
    def _update_average_confidence(self, new_confidence: float):
        """Update running average confidence score."""
        total_predictions = self.metrics["total_predictions_generated"]
        if total_predictions > 0:
            current_avg = self.metrics["average_confidence_score"]
            self.metrics["average_confidence_score"] = (
                (current_avg * (total_predictions - 1) + new_confidence) / total_predictions
            )
    
    def _build_what_if_prompt(
        self,
        baseline_data: Dict[str, Any],
        scenario: Dict[str, Any],
        time_horizon_days: int
    ) -> str:
        """Build prompt for what-if scenario analysis."""
        return f"""
Analyze a what-if scenario for student performance and engagement.

Baseline Data:
{json.dumps(baseline_data, indent=2)}

Scenario:
{json.dumps(scenario, indent=2)}

Time Horizon: {time_horizon_days} days

Requirements:
1. Analyze the impact of the scenario changes
2. Predict performance outcomes
3. Identify potential risks and benefits
4. Provide actionable insights
5. Consider both short-term and long-term effects

Format as JSON:
{{
    "scenario_summary": "Summary of the scenario",
    "predicted_outcomes": {{
        "performance_change": "percentage or description",
        "engagement_impact": "description",
        "risk_factors": ["factor1", "factor2"],
        "opportunities": ["opportunity1", "opportunity2"]
    }},
    "recommendations": ["recommendation1", "recommendation2"],
    "confidence_score": 0.8,
    "time_to_impact": "days or timeframe"
}}
"""
    
    def _build_intervention_prompt(
        self,
        risk_factors: List[str],
        current_performance: Dict[str, Any]
    ) -> str:
        """Build prompt for intervention recommendations."""
        return f"""
Generate targeted intervention recommendations based on risk factors.

Risk Factors:
{json.dumps(risk_factors, indent=2)}

Current Performance:
{json.dumps(current_performance, indent=2)}

Requirements:
1. Generate specific, actionable interventions
2. Prioritize interventions by impact and feasibility
3. Consider different intervention types (academic, motivational, structural)
4. Provide implementation guidance
5. Include expected outcomes and timelines

Format as JSON array:
[
    {{
        "intervention_type": "academic|motivational|structural|behavioral",
        "title": "Intervention Title",
        "description": "Detailed description",
        "priority": "high|medium|low",
        "implementation_steps": ["step1", "step2"],
        "expected_outcome": "description of expected result",
        "time_to_effect": "days or weeks",
        "resources_needed": ["resource1", "resource2"],
        "success_indicators": ["indicator1", "indicator2"]
    }},
    ...
]
"""
    
    def _parse_what_if_response(self, content: str) -> Dict[str, Any]:
        """Parse what-if scenario analysis from AI response."""
        try:
            # Try to parse as JSON
            import json
            analysis = json.loads(content)
            
            if isinstance(analysis, dict):
                return analysis
            else:
                # Fallback: return as basic analysis
                return {
                    "scenario_summary": "Analysis completed",
                    "predicted_outcomes": {"analysis": content},
                    "recommendations": ["Monitor changes closely"],
                    "confidence_score": 0.6,
                    "time_to_impact": "2-4 weeks"
                }
                
        except json.JSONDecodeError:
            # Fallback: return basic analysis
            return {
                "scenario_summary": "What-if analysis",
                "predicted_outcomes": {"analysis": content},
                "recommendations": ["Monitor changes closely"],
                "confidence_score": 0.6,
                "time_to_impact": "2-4 weeks"
            }
    
    def _parse_intervention_recommendations(self, content: str) -> List[Dict[str, Any]]:
        """Parse intervention recommendations from AI response."""
        try:
            # Try to parse as JSON
            import json
            interventions = json.loads(content)
            
            if isinstance(interventions, list):
                return interventions
            elif isinstance(interventions, dict) and "interventions" in interventions:
                return interventions["interventions"]
            else:
                # Fallback: return as single intervention
                return [{
                    "intervention_type": "general",
                    "title": "Recommended Intervention",
                    "description": content,
                    "priority": "medium",
                    "implementation_steps": ["Analyze situation", "Implement changes"],
                    "expected_outcome": "Improved performance",
                    "time_to_effect": "2-4 weeks",
                    "resources_needed": [],
                    "success_indicators": ["Better engagement", "Improved scores"]
                }]
                
        except json.JSONDecodeError:
            # Fallback: return basic intervention
            return [{
                "intervention_type": "general",
                "title": "Recommended Intervention",
                "description": content,
                "priority": "medium",
                "implementation_steps": ["Analyze situation", "Implement changes"],
                "expected_outcome": "Improved performance",
                "time_to_effect": "2-4 weeks",
                "resources_needed": [],
                "success_indicators": ["Better engagement", "Improved scores"]
            }]
    
    # ========================================================================
    # PREDICTION MODEL METHODS
    # ========================================================================
    
    async def _predict_performance_trend(
        self, 
        request: PredictionRequest, 
        historical_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Predict performance trends."""
        try:
            # Build prompt for performance trend prediction
            prompt = f"""
Analyze historical performance data and predict future trends.

Historical Data:
{json.dumps(historical_data, indent=2)}

Time Period: {request.time_period_days} days

Requirements:
1. Analyze performance trends and patterns
2. Identify potential declines or improvements
3. Predict future performance trajectory
4. Assess risk factors and confidence
5. Provide actionable insights

Format as JSON:
{{
    "predictions": {{
        "trend_direction": "improving|declining|stable",
        "predicted_performance_change": 15.5,
        "confidence_interval": [10.2, 20.8],
        "time_to_impact": "2-3 weeks"
    }},
    "risk_factors": ["factor1", "factor2"],
    "recommendations": ["recommendation1", "recommendation2"],
    "confidence_score": 0.8,
    "risk_score": 0.3
}}
"""
            
            # Generate content using AI service
            content_request = ContentRequest(
                content_type=ContentType.ANALYSIS,
                prompt=prompt,
                user_id=request.parent_id,
                student_id=request.student_id,
                context={"historical_data": historical_data, "time_period_days": request.time_period_days},
                metadata={"prediction_type": "performance_trend"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse response
            try:
                prediction_data = json.loads(result.content)
            except json.JSONDecodeError:
                # Fallback prediction
                prediction_data = {
                    "predictions": {"trend": "stable", "analysis": result.content},
                    "risk_factors": ["Insufficient data"],
                    "recommendations": ["Continue monitoring"],
                    "confidence_score": 0.6,
                    "risk_score": 0.4
                }
            
            generation_metadata = {
                "tokens_used": result.tokens_used,
                "cost": result.cost,
                "generation_time_ms": result.generation_time_ms
            }
            
            return prediction_data, generation_metadata
            
        except Exception as e:
            logger.error(f"Failed to predict performance trend: {e}")
            return {
                "predictions": {"error": str(e)},
                "risk_factors": ["Analysis failed"],
                "recommendations": ["Try again later"],
                "confidence_score": 0.3,
                "risk_score": 0.7
            }, {"error": str(e)}
    
    async def _predict_engagement_pattern(
        self, 
        request: PredictionRequest, 
        historical_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Predict engagement patterns."""
        try:
            # Build prompt for engagement pattern prediction
            prompt = f"""
Analyze historical engagement data and predict future patterns.

Historical Data:
{json.dumps(historical_data, indent=2)}

Time Period: {request.time_period_days} days

Requirements:
1. Analyze engagement patterns and consistency
2. Identify potential disengagement risks
3. Predict future engagement levels
4. Assess motivation and study habits
5. Provide actionable insights

Format as JSON:
{{
    "predictions": {{
        "engagement_trend": "increasing|decreasing|stable",
        "predicted_engagement_level": "high|medium|low",
        "consistency_score": 0.75,
        "risk_of_disengagement": 0.2,
        "critical_periods": ["period1", "period2"]
    }},
    "risk_factors": ["factor1", "factor2"],
    "recommendations": ["recommendation1", "recommendation2"],
    "confidence_score": 0.8,
    "risk_score": 0.3
}}
"""
            
            # Generate content using AI service
            content_request = ContentRequest(
                content_type=ContentType.ANALYSIS,
                prompt=prompt,
                user_id=request.parent_id,
                student_id=request.student_id,
                context={"historical_data": historical_data, "time_period_days": request.time_period_days},
                metadata={"prediction_type": "engagement_pattern"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse response
            try:
                prediction_data = json.loads(result.content)
            except json.JSONDecodeError:
                # Fallback prediction
                prediction_data = {
                    "predictions": {"engagement_trend": "stable", "analysis": result.content},
                    "risk_factors": ["Insufficient data"],
                    "recommendations": ["Continue monitoring"],
                    "confidence_score": 0.6,
                    "risk_score": 0.4
                }
            
            generation_metadata = {
                "tokens_used": result.tokens_used,
                "cost": result.cost,
                "generation_time_ms": result.generation_time_ms
            }
            
            return prediction_data, generation_metadata
            
        except Exception as e:
            logger.error(f"Failed to predict engagement pattern: {e}")
            return {
                "predictions": {"error": str(e)},
                "risk_factors": ["Analysis failed"],
                "recommendations": ["Try again later"],
                "confidence_score": 0.3,
                "risk_score": 0.7
            }, {"error": str(e)}
    
    async def _predict_risk_assessment(
        self, 
        request: PredictionRequest, 
        historical_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Predict risk assessment."""
        try:
            # Build prompt for risk assessment prediction
            prompt = f"""
Analyze historical data and assess potential risks.

Historical Data:
{json.dumps(historical_data, indent=2)}

Time Period: {request.time_period_days} days

Risk Thresholds:
- Performance decline: {self.risk_thresholds['performance_decline_threshold'] * 100}%
- Engagement drop: {self.risk_thresholds['engagement_drop_threshold'] * 100}%
- Consecutive missed days: {self.risk_thresholds['consecutive_missed_days']}

Requirements:
1. Assess multiple risk dimensions (performance, engagement, consistency)
2. Identify early warning signs
3. Calculate overall risk score
4. Prioritize risks by impact and urgency
5. Provide mitigation strategies

Format as JSON:
{{
    "predictions": {{
        "overall_risk_score": 0.4,
        "risk_breakdown": {{
            "performance_risk": 0.3,
            "engagement_risk": 0.5,
            "consistency_risk": 0.4
        }},
        "high_risk_areas": ["area1", "area2"],
        "early_warning_signs": ["sign1", "sign2"]
    }},
    "risk_factors": ["factor1", "factor2"],
    "recommendations": ["recommendation1", "recommendation2"],
    "confidence_score": 0.8,
    "risk_score": 0.4
}}
"""
            
            # Generate content using AI service
            content_request = ContentRequest(
                content_type=ContentType.ANALYSIS,
                prompt=prompt,
                user_id=request.parent_id,
                student_id=request.student_id,
                context={"historical_data": historical_data, "time_period_days": request.time_period_days},
                metadata={"prediction_type": "risk_assessment"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse response
            try:
                prediction_data = json.loads(result.content)
            except json.JSONDecodeError:
                # Fallback prediction
                prediction_data = {
                    "predictions": {"overall_risk": "moderate", "analysis": result.content},
                    "risk_factors": ["Insufficient data"],
                    "recommendations": ["Continue monitoring"],
                    "confidence_score": 0.6,
                    "risk_score": 0.5
                }
            
            generation_metadata = {
                "tokens_used": result.tokens_used,
                "cost": result.cost,
                "generation_time_ms": result.generation_time_ms
            }
            
            return prediction_data, generation_metadata
            
        except Exception as e:
            logger.error(f"Failed to predict risk assessment: {e}")
            return {
                "predictions": {"error": str(e)},
                "risk_factors": ["Analysis failed"],
                "recommendations": ["Try again later"],
                "confidence_score": 0.3,
                "risk_score": 0.7
            }, {"error": str(e)}
    
    async def _predict_intervention_need(
        self, 
        request: PredictionRequest, 
        historical_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Predict intervention needs."""
        try:
            # Build prompt for intervention need prediction
            prompt = f"""
Analyze historical data and predict intervention needs.

Historical Data:
{json.dumps(historical_data, indent=2)}

Time Period: {request.time_period_days} days

Requirements:
1. Identify areas needing intervention
2. Assess urgency and impact
3. Predict optimal intervention timing
4. Suggest intervention types
5. Estimate intervention effectiveness

Format as JSON:
{{
    "predictions": {{
        "intervention_urgency": "high|medium|low",
        "intervention_types": ["type1", "type2"],
        "optimal_timing": "immediate|within_week|within_month",
        "expected_effectiveness": 0.8,
        "critical_intervention_areas": ["area1", "area2"]
    }},
    "risk_factors": ["factor1", "factor2"],
    "recommendations": ["recommendation1", "recommendation2"],
    "confidence_score": 0.8,
    "risk_score": 0.4
}}
"""
            
            # Generate content using AI service
            content_request = ContentRequest(
                content_type=ContentType.RECOMMENDATION,
                prompt=prompt,
                user_id=request.parent_id,
                student_id=request.student_id,
                context={"historical_data": historical_data, "time_period_days": request.time_period_days},
                metadata={"prediction_type": "intervention_need"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse response
            try:
                prediction_data = json.loads(result.content)
            except json.JSONDecodeError:
                # Fallback prediction
                prediction_data = {
                    "predictions": {"intervention_urgency": "medium", "analysis": result.content},
                    "risk_factors": ["Insufficient data"],
                    "recommendations": ["Continue monitoring"],
                    "confidence_score": 0.6,
                    "risk_score": 0.5
                }
            
            generation_metadata = {
                "tokens_used": result.tokens_used,
                "cost": result.cost,
                "generation_time_ms": result.generation_time_ms
            }
            
            return prediction_data, generation_metadata
            
        except Exception as e:
            logger.error(f"Failed to predict intervention need: {e}")
            return {
                "predictions": {"error": str(e)},
                "risk_factors": ["Analysis failed"],
                "recommendations": ["Try again later"],
                "confidence_score": 0.3,
                "risk_score": 0.7
            }, {"error": str(e)}
    
    async def _predict_milestone_achievement(
        self, 
        request: PredictionRequest, 
        historical_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Predict milestone achievement."""
        try:
            # Build prompt for milestone achievement prediction
            prompt = f"""
Analyze historical data and predict milestone achievement.

Historical Data:
{json.dumps(historical_data, indent=2)}

Time Period: {request.time_period_days} days

Requirements:
1. Predict achievement of upcoming milestones
2. Assess current progress towards goals
3. Identify potential blockers or accelerators
4. Estimate achievement timelines
5. Provide milestone optimization strategies

Format as JSON:
{{
    "predictions": {{
        "upcoming_milestones": [
            {{
                "milestone": "milestone1",
                "predicted_achievement": "on_time|early|delayed",
                "confidence": 0.8,
                "estimated_date": "2024-02-15"
            }}
        ],
        "overall_milestone_trend": "on_track|ahead|behind",
        "achievement_probability": 0.75,
        "time_to_next_milestone": "2 weeks"
    }},
    "risk_factors": ["factor1", "factor2"],
    "recommendations": ["recommendation1", "recommendation2"],
    "confidence_score": 0.8,
    "risk_score": 0.3
}}
"""
            
            # Generate content using AI service
            content_request = ContentRequest(
                content_type=ContentType.ANALYSIS,
                prompt=prompt,
                user_id=request.parent_id,
                student_id=request.student_id,
                context={"historical_data": historical_data, "time_period_days": request.time_period_days},
                metadata={"prediction_type": "milestone_prediction"}
            )
            
            result = await self.ai_content_service.generate_content(content_request)
            
            # Parse response
            try:
                prediction_data = json.loads(result.content)
            except json.JSONDecodeError:
                # Fallback prediction
                prediction_data = {
                    "predictions": {"milestone_trend": "on_track", "analysis": result.content},
                    "risk_factors": ["Insufficient data"],
                    "recommendations": ["Continue monitoring"],
                    "confidence_score": 0.6,
                    "risk_score": 0.4
                }
            
            generation_metadata = {
                "tokens_used": result.tokens_used,
                "cost": result.cost,
                "generation_time_ms": result.generation_time_ms
            }
            
            return prediction_data, generation_metadata
            
        except Exception as e:
            logger.error(f"Failed to predict milestone achievement: {e}")
            return {
                "predictions": {"error": str(e)},
                "risk_factors": ["Analysis failed"],
                "recommendations": ["Try again later"],
                "confidence_score": 0.3,
                "risk_score": 0.7
            }, {"error": str(e)}
    
    def _calculate_intervention_effectiveness(
        self,
        before_data: Dict[str, Any],
        after_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate intervention effectiveness."""
        try:
            # Extract key metrics
            before_metrics = before_data.get("engagement_metrics", [])
            after_metrics = after_data.get("engagement_metrics", [])
            
            # Calculate averages before and after
            before_avg = self._calculate_metric_averages(before_metrics)
            after_avg = self._calculate_metric_averages(after_metrics)
            
            # Calculate improvements
            improvements = {}
            for metric in before_avg:
                if metric in after_avg:
                    if before_avg[metric] > 0:
                        improvement = ((after_avg[metric] - before_avg[metric]) / before_avg[metric]) * 100
                        improvements[metric] = improvement
            
            # Overall effectiveness score
            overall_effectiveness = statistics.mean(improvements.values()) if improvements else 0
            
            return {
                "overall_effectiveness_score": overall_effectiveness,
                "metric_improvements": improvements,
                "before_averages": before_avg,
                "after_averages": after_avg,
                "assessment_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate intervention effectiveness: {e}")
            return {
                "overall_effectiveness_score": 0,
                "metric_improvements": {},
                "error": str(e)
            }
    
    def _calculate_metric_averages(self, metrics: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate average values for metrics."""
        averages = {}
        
        if not metrics:
            return averages
        
        # Group by metric type
        metric_groups = {}
        for metric in metrics:
            metric_type = metric.get("metric_type", "unknown")
            if metric_type not in metric_groups:
                metric_groups[metric_type] = []
            metric_groups[metric_type].append(metric.get("value", 0))
        
        # Calculate averages
        for metric_type, values in metric_groups.items():
            if values:
                averages[metric_type] = statistics.mean(values)
        
        return averages

# Initialize prediction models
def _init_prediction_models(service: 'PredictiveAnalyticsService'):
    """Initialize prediction models for different types."""
    return {
        PredictionType.PERFORMANCE_TREND: service._predict_performance_trend,
        PredictionType.ENGAGEMENT_PATTERN: service._predict_engagement_pattern,
        PredictionType.RISK_ASSESSMENT: service._predict_risk_assessment,
        PredictionType.INTERVENTION_NEED: service._predict_intervention_need,
        PredictionType.MILESTONE_PREDICTION: service._predict_milestone_achievement
    }

# Add prediction models to PredictiveAnalyticsService class
PredictiveAnalyticsService.prediction_models = None

def get_predictive_analytics_service(
    unified_config: Optional[GeminiConfig] = None,
    **kwargs
) -> PredictiveAnalyticsService:
    """
    Get Predictive Analytics service instance.
    
    Args:
        unified_config: Optional unified configuration
        **kwargs: Additional arguments for service initialization
    
    Returns:
        PredictiveAnalyticsService instance
    """
    service = PredictiveAnalyticsService(unified_config=unified_config, **kwargs)
    
    # Initialize prediction models after service creation
    service.prediction_models = _init_prediction_models(service)
    
    return service

# Module initialization
logger.info("Predictive Analytics Service module loaded")