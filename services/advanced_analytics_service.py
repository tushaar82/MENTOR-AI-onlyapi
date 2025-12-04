"""
Advanced Analytics Service for Parent-Child Learning Insights

This service provides comprehensive analytics for parents to understand:
1. Parent effectiveness metrics
2. Correlation between parent involvement and student progress
3. Comparative analytics and benchmarking
4. Visualization components
5. Predictive insights and recommendations
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import math

from services.database_service import DatabaseService
from services.translation_service import TranslationService
from services.gemini_service import GeminiService
from services.predictive_analytics_service import PredictiveAnalyticsService
from services.parent_ai_insights_service import ParentAIInsightsService
from services.parent_resource_library_service import ParentResourceLibraryService
from services.interactive_study_tools_service import InteractiveStudyToolsService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of analytics metrics"""
    EFFECTIVENESS = "effectiveness"
    ENGAGEMENT = "engagement"
    PROGRESS = "progress"
    CORRELATION = "correlation"
    COMPARATIVE = "comparative"
    PREDICTIVE = "predictive"

class TimePeriod(Enum):
    """Time periods for analytics"""
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class BenchmarkType(Enum):
    """Types of benchmarks for comparison"""
    PEER = "peer"  # Similar parents/students
    REGIONAL = "regional"  # Same geographical region
    SUBJECT = "subject"  # Same subject/exam
    GLOBAL = "global"  # All users

@dataclass
class ParentEffectivenessMetric:
    """Parent effectiveness metrics"""
    metric_id: str
    parent_id: str
    child_id: str
    metric_type: str
    value: float
    percentile: float
    trend: str  # improving, stable, declining
    period: str
    benchmark_value: float
    created_at: datetime

@dataclass
class CorrelationAnalysis:
    """Correlation analysis between parent involvement and student outcomes"""
    analysis_id: str
    parent_id: str
    child_id: str
    involvement_metric: str
    outcome_metric: str
    correlation_coefficient: float
    significance_level: float
    trend_direction: str
    insights: List[str]
    recommendations: List[str]
    created_at: datetime

@dataclass
class ComparativeAnalytics:
    """Comparative analytics against benchmarks"""
    analytics_id: str
    parent_id: str
    child_id: str
    benchmark_type: str
    metrics: Dict[str, Dict[str, Any]]  # metric_name -> {value, percentile, rank}
    strengths: List[str]
    improvement_areas: List[str]
    actionable_insights: List[str]
    created_at: datetime

@dataclass
class PredictiveInsight:
    """Predictive insights for future performance"""
    insight_id: str
    parent_id: str
    child_id: str
    prediction_type: str
    confidence_score: float
    timeframe: str
    predicted_outcome: Dict[str, Any]
    influencing_factors: List[str]
    recommendations: List[str]
    created_at: datetime

@dataclass
class VisualizationData:
    """Data structure for visualization components"""
    chart_type: str  # line, bar, pie, scatter, heatmap
    title: str
    data: List[Dict[str, Any]]
    x_axis: str
    y_axis: str
    filters: Dict[str, Any]
    metadata: Dict[str, Any]

class AdvancedAnalyticsService:
    """Advanced Analytics Service for comprehensive parent-child insights"""
    
    def __init__(
        self,
        db_service: DatabaseService,
        translation_service: TranslationService,
        gemini_service: GeminiService,
        predictive_analytics_service: PredictiveAnalyticsService,
        parent_ai_insights_service: ParentAIInsightsService,
        parent_resource_library_service: ParentResourceLibraryService,
        interactive_study_tools_service: InteractiveStudyToolsService
    ):
        self.db_service = db_service
        self.translation_service = translation_service
        self.gemini_service = gemini_service
        self.predictive_analytics_service = predictive_analytics_service
        self.parent_ai_insights_service = parent_ai_insights_service
        self.parent_resource_library_service = parent_resource_library_service
        self.interactive_study_tools_service = interactive_study_tools_service
        
        # Analytics configuration
        self.analytics_config = {
            "effectiveness_metrics": {
                "teaching_quality": {"weight": 0.3, "source": "study_sessions"},
                "communication_frequency": {"weight": 0.2, "source": "communications"},
                "resource_utilization": {"weight": 0.2, "source": "resource_usage"},
                "goal_achievement_rate": {"weight": 0.15, "source": "goals"},
                "intervention_timeliness": {"weight": 0.15, "source": "interventions"}
            },
            "correlation_thresholds": {
                "strong": 0.7,
                "moderate": 0.5,
                "weak": 0.3
            },
            "prediction_horizons": {
                "short_term": "2_weeks",
                "medium_term": "1_month",
                "long_term": "3_months"
            }
        }
        
        logger.info("Advanced Analytics Service initialized")
    
    async def calculate_parent_effectiveness(
        self,
        parent_id: str,
        child_id: str,
        period: TimePeriod = TimePeriod.MONTHLY,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive parent effectiveness metrics
        
        Args:
            parent_id: Parent identifier
            child_id: Child identifier
            period: Time period for analysis
            language: Language for insights
            
        Returns:
            Dictionary containing effectiveness metrics and insights
        """
        try:
            logger.info(f"Calculating parent effectiveness for parent {parent_id}, child {child_id}")
            
            # Get date range for the period
            end_date = datetime.now()
            start_date = self._get_period_start_date(end_date, period)
            
            # Calculate individual metrics
            metrics = {}
            total_score = 0
            total_weight = 0
            
            for metric_name, config in self.analytics_config["effectiveness_metrics"].items():
                metric_value = await self._calculate_individual_metric(
                    parent_id, child_id, metric_name, config["source"], start_date, end_date
                )
                
                if metric_value is not None:
                    weight = config["weight"]
                    weighted_score = metric_value * weight
                    total_score += weighted_score
                    total_weight += weight
                    
                    metrics[metric_name] = {
                        "value": metric_value,
                        "weight": weight,
                        "weighted_score": weighted_score,
                        "status": self._get_metric_status(metric_value)
                    }
            
            # Calculate overall effectiveness score
            overall_score = total_score / total_weight if total_weight > 0 else 0
            
            # Get benchmark data
            benchmark_data = await self._get_effectiveness_benchmarks(
                parent_id, child_id, period
            )
            
            # Calculate percentile
            percentile = self._calculate_percentile(overall_score, benchmark_data)
            
            # Determine trend
            trend = await self._calculate_effectiveness_trend(
                parent_id, child_id, period
            )
            
            # Generate AI-powered insights
            insights = await self._generate_effectiveness_insights(
                parent_id, child_id, metrics, overall_score, trend, language
            )
            
            # Create effectiveness metric record
            effectiveness_metric = ParentEffectivenessMetric(
                metric_id=f"effectiveness_{parent_id}_{child_id}_{int(end_date.timestamp())}",
                parent_id=parent_id,
                child_id=child_id,
                metric_type="overall_effectiveness",
                value=overall_score,
                percentile=percentile,
                trend=trend,
                period=period.value,
                benchmark_value=statistics.mean(benchmark_data) if benchmark_data else 0,
                created_at=end_date
            )
            
            # Store in database
            await self._store_effectiveness_metric(effectiveness_metric)
            
            return {
                "overall_score": overall_score,
                "percentile": percentile,
                "trend": trend,
                "individual_metrics": metrics,
                "benchmark": {
                    "average": statistics.mean(benchmark_data) if benchmark_data else 0,
                    "median": statistics.median(benchmark_data) if benchmark_data else 0,
                    "top_quartile": statistics.quantile(benchmark_data, 0.75) if len(benchmark_data) > 4 else 0
                },
                "insights": insights,
                "period": period.value,
                "calculated_at": end_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating parent effectiveness: {str(e)}")
            raise
    
    async def analyze_correlation(
        self,
        parent_id: str,
        child_id: str,
        involvement_metrics: List[str],
        outcome_metrics: List[str],
        period: TimePeriod = TimePeriod.MONTHLY,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Analyze correlation between parent involvement and student outcomes
        
        Args:
            parent_id: Parent identifier
            child_id: Child identifier
            involvement_metrics: List of parent involvement metrics to analyze
            outcome_metrics: List of student outcome metrics to analyze
            period: Time period for analysis
            language: Language for insights
            
        Returns:
            Dictionary containing correlation analysis results
        """
        try:
            logger.info(f"Analyzing correlation for parent {parent_id}, child {child_id}")
            
            # Get date range
            end_date = datetime.now()
            start_date = self._get_period_start_date(end_date, period)
            
            # Collect time series data for both metrics
            correlation_results = []
            
            for involvement_metric in involvement_metrics:
                for outcome_metric in outcome_metrics:
                    # Get time series data
                    involvement_data = await self._get_time_series_data(
                        parent_id, child_id, involvement_metric, start_date, end_date
                    )
                    outcome_data = await self._get_time_series_data(
                        parent_id, child_id, outcome_metric, start_date, end_date
                    )
                    
                    if len(involvement_data) >= 3 and len(outcome_data) >= 3:
                        # Calculate correlation
                        correlation_coefficient = self._calculate_pearson_correlation(
                            involvement_data, outcome_data
                        )
                        
                        # Calculate significance
                        significance_level = self._calculate_significance_level(
                            correlation_coefficient, len(involvement_data)
                        )
                        
                        # Determine trend direction
                        trend_direction = self._determine_correlation_trend(
                            correlation_coefficient
                        )
                        
                        # Generate insights
                        insights = await self._generate_correlation_insights(
                            involvement_metric, outcome_metric, correlation_coefficient,
                            significance_level, language
                        )
                        
                        # Generate recommendations
                        recommendations = await self._generate_correlation_recommendations(
                            involvement_metric, outcome_metric, correlation_coefficient,
                            trend_direction, language
                        )
                        
                        # Create correlation analysis record
                        correlation_analysis = CorrelationAnalysis(
                            analysis_id=f"corr_{parent_id}_{child_id}_{involvement_metric}_{outcome_metric}_{int(end_date.timestamp())}",
                            parent_id=parent_id,
                            child_id=child_id,
                            involvement_metric=involvement_metric,
                            outcome_metric=outcome_metric,
                            correlation_coefficient=correlation_coefficient,
                            significance_level=significance_level,
                            trend_direction=trend_direction,
                            insights=insights,
                            recommendations=recommendations,
                            created_at=end_date
                        )
                        
                        # Store in database
                        await self._store_correlation_analysis(correlation_analysis)
                        
                        correlation_results.append({
                            "involvement_metric": involvement_metric,
                            "outcome_metric": outcome_metric,
                            "correlation_coefficient": correlation_coefficient,
                            "significance_level": significance_level,
                            "trend_direction": trend_direction,
                            "strength": self._classify_correlation_strength(correlation_coefficient),
                            "insights": insights,
                            "recommendations": recommendations
                        })
            
            # Generate summary insights
            summary_insights = await self._generate_correlation_summary(
                correlation_results, language
            )
            
            return {
                "correlation_results": correlation_results,
                "summary_insights": summary_insights,
                "period": period.value,
                "analyzed_at": end_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing correlation: {str(e)}")
            raise
    
    async def generate_comparative_analytics(
        self,
        parent_id: str,
        child_id: str,
        benchmark_types: List[BenchmarkType],
        period: TimePeriod = TimePeriod.MONTHLY,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generate comparative analytics against various benchmarks
        
        Args:
            parent_id: Parent identifier
            child_id: Child identifier
            benchmark_types: List of benchmark types to compare against
            period: Time period for analysis
            language: Language for insights
            
        Returns:
            Dictionary containing comparative analytics results
        """
        try:
            logger.info(f"Generating comparative analytics for parent {parent_id}, child {child_id}")
            
            # Get current metrics
            current_metrics = await self._get_current_metrics(parent_id, child_id)
            
            comparative_results = {}
            
            for benchmark_type in benchmark_types:
                # Get benchmark data
                benchmark_data = await self._get_benchmark_data(
                    parent_id, child_id, benchmark_type, period
                )
                
                # Calculate comparisons
                metrics_comparison = {}
                strengths = []
                improvement_areas = []
                
                for metric_name, current_value in current_metrics.items():
                    if metric_name in benchmark_data:
                        benchmark_values = benchmark_data[metric_name]
                        
                        # Calculate percentile and rank
                        percentile = self._calculate_percentile(current_value, benchmark_values)
                        rank = self._calculate_rank(current_value, benchmark_values)
                        
                        metrics_comparison[metric_name] = {
                            "current_value": current_value,
                            "benchmark_average": statistics.mean(benchmark_values),
                            "percentile": percentile,
                            "rank": rank,
                            "total_compared": len(benchmark_values),
                            "performance_level": self._classify_performance_level(percentile)
                        }
                        
                        # Identify strengths and improvement areas
                        if percentile >= 75:
                            strengths.append(metric_name)
                        elif percentile <= 25:
                            improvement_areas.append(metric_name)
                
                # Generate actionable insights
                actionable_insights = await self._generate_comparative_insights(
                    metrics_comparison, strengths, improvement_areas, benchmark_type, language
                )
                
                # Create comparative analytics record
                comparative_analytics = ComparativeAnalytics(
                    analytics_id=f"comp_{parent_id}_{child_id}_{benchmark_type.value}_{int(datetime.now().timestamp())}",
                    parent_id=parent_id,
                    child_id=child_id,
                    benchmark_type=benchmark_type.value,
                    metrics=metrics_comparison,
                    strengths=strengths,
                    improvement_areas=improvement_areas,
                    actionable_insights=actionable_insights,
                    created_at=datetime.now()
                )
                
                # Store in database
                await self._store_comparative_analytics(comparative_analytics)
                
                comparative_results[benchmark_type.value] = {
                    "metrics_comparison": metrics_comparison,
                    "strengths": strengths,
                    "improvement_areas": improvement_areas,
                    "actionable_insights": actionable_insights
                }
            
            # Generate overall summary
            overall_summary = await self._generate_comparative_summary(
                comparative_results, language
            )
            
            return {
                "comparative_results": comparative_results,
                "overall_summary": overall_summary,
                "period": period.value,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating comparative analytics: {str(e)}")
            raise
    
    async def generate_predictive_insights(
        self,
        parent_id: str,
        child_id: str,
        prediction_types: List[str],
        timeframes: List[str],
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generate predictive insights for future performance
        
        Args:
            parent_id: Parent identifier
            child_id: Child identifier
            prediction_types: Types of predictions to generate
            timeframes: Timeframes for predictions
            language: Language for insights
            
        Returns:
            Dictionary containing predictive insights
        """
        try:
            logger.info(f"Generating predictive insights for parent {parent_id}, child {child_id}")
            
            predictive_results = {}
            
            for prediction_type in prediction_types:
                for timeframe in timeframes:
                    # Generate prediction using predictive analytics service
                    prediction_data = await self.predictive_analytics_service.generate_prediction(
                        child_id, prediction_type, timeframe
                    )
                    
                    if prediction_data:
                        # Calculate confidence score
                        confidence_score = prediction_data.get("confidence_score", 0.5)
                        
                        # Identify influencing factors
                        influencing_factors = await self._identify_influencing_factors(
                            parent_id, child_id, prediction_type, timeframe
                        )
                        
                        # Generate recommendations
                        recommendations = await self._generate_predictive_recommendations(
                            prediction_data, influencing_factors, language
                        )
                        
                        # Create predictive insight record
                        predictive_insight = PredictiveInsight(
                            insight_id=f"pred_{parent_id}_{child_id}_{prediction_type}_{timeframe}_{int(datetime.now().timestamp())}",
                            parent_id=parent_id,
                            child_id=child_id,
                            prediction_type=prediction_type,
                            confidence_score=confidence_score,
                            timeframe=timeframe,
                            predicted_outcome=prediction_data,
                            influencing_factors=influencing_factors,
                            recommendations=recommendations,
                            created_at=datetime.now()
                        )
                        
                        # Store in database
                        await self._store_predictive_insight(predictive_insight)
                        
                        if prediction_type not in predictive_results:
                            predictive_results[prediction_type] = {}
                        
                        predictive_results[prediction_type][timeframe] = {
                            "confidence_score": confidence_score,
                            "predicted_outcome": prediction_data,
                            "influencing_factors": influencing_factors,
                            "recommendations": recommendations,
                            "risk_level": self._classify_risk_level(prediction_data, confidence_score)
                        }
            
            # Generate overall insights
            overall_insights = await self._generate_predictive_summary(
                predictive_results, language
            )
            
            return {
                "predictive_results": predictive_results,
                "overall_insights": overall_insights,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating predictive insights: {str(e)}")
            raise
    
    async def create_visualization_data(
        self,
        parent_id: str,
        child_id: str,
        chart_types: List[str],
        filters: Dict[str, Any],
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Create data structures for visualization components
        
        Args:
            parent_id: Parent identifier
            child_id: Child identifier
            chart_types: Types of charts to generate
            filters: Filters for data selection
            language: Language for labels
            
        Returns:
            Dictionary containing visualization data
        """
        try:
            logger.info(f"Creating visualization data for parent {parent_id}, child {child_id}")
            
            visualization_results = {}
            
            for chart_type in chart_types:
                if chart_type == "effectiveness_trend":
                    visualization_data = await self._create_effectiveness_trend_chart(
                        parent_id, child_id, filters, language
                    )
                elif chart_type == "correlation_heatmap":
                    visualization_data = await self._create_correlation_heatmap(
                        parent_id, child_id, filters, language
                    )
                elif chart_type == "performance_radar":
                    visualization_data = await self._create_performance_radar_chart(
                        parent_id, child_id, filters, language
                    )
                elif chart_type == "progress_timeline":
                    visualization_data = await self._create_progress_timeline_chart(
                        parent_id, child_id, filters, language
                    )
                elif chart_type == "benchmark_comparison":
                    visualization_data = await self._create_benchmark_comparison_chart(
                        parent_id, child_id, filters, language
                    )
                else:
                    visualization_data = await self._create_generic_chart(
                        parent_id, child_id, chart_type, filters, language
                    )
                
                visualization_results[chart_type] = visualization_data
            
            return {
                "visualization_data": visualization_results,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating visualization data: {str(e)}")
            raise
    
    async def get_comprehensive_dashboard(
        self,
        parent_id: str,
        child_id: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data with all analytics
        
        Args:
            parent_id: Parent identifier
            child_id: Child identifier
            language: Language for content
            
        Returns:
            Dictionary containing comprehensive dashboard data
        """
        try:
            logger.info(f"Getting comprehensive dashboard for parent {parent_id}, child {child_id}")
            
            # Get all analytics components
            effectiveness = await self.calculate_parent_effectiveness(
                parent_id, child_id, TimePeriod.MONTHLY, language
            )
            
            correlation = await self.analyze_correlation(
                parent_id, child_id,
                ["teaching_quality", "communication_frequency", "resource_utilization"],
                ["academic_performance", "engagement_level", "learning_outcomes"],
                TimePeriod.MONTHLY, language
            )
            
            comparative = await self.generate_comparative_analytics(
                parent_id, child_id,
                [BenchmarkType.PEER, BenchmarkType.REGIONAL],
                TimePeriod.MONTHLY, language
            )
            
            predictive = await self.generate_predictive_insights(
                parent_id, child_id,
                ["academic_performance", "engagement_level"],
                ["short_term", "medium_term"],
                language
            )
            
            visualization = await self.create_visualization_data(
                parent_id, child_id,
                ["effectiveness_trend", "correlation_heatmap", "performance_radar"],
                {}, language
            )
            
            # Generate dashboard summary
            dashboard_summary = await self._generate_dashboard_summary(
                effectiveness, correlation, comparative, predictive, language
            )
            
            return {
                "effectiveness": effectiveness,
                "correlation": correlation,
                "comparative": comparative,
                "predictive": predictive,
                "visualization": visualization,
                "dashboard_summary": dashboard_summary,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive dashboard: {str(e)}")
            raise
    
    # Helper methods
    
    def _get_period_start_date(self, end_date: datetime, period: TimePeriod) -> datetime:
        """Get start date for a given period"""
        if period == TimePeriod.WEEKLY:
            return end_date - timedelta(weeks=1)
        elif period == TimePeriod.MONTHLY:
            return end_date - timedelta(days=30)
        elif period == TimePeriod.QUARTERLY:
            return end_date - timedelta(days=90)
        elif period == TimePeriod.YEARLY:
            return end_date - timedelta(days=365)
        return end_date - timedelta(days=30)
    
    async def _calculate_individual_metric(
        self,
        parent_id: str,
        child_id: str,
        metric_name: str,
        source: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[float]:
        """Calculate individual effectiveness metric"""
        try:
            if source == "study_sessions":
                # Get study session data
                sessions = await self.interactive_study_tools_service.get_parent_study_sessions(
                    parent_id, child_id, start_date, end_date
                )
                if sessions:
                    # Calculate teaching quality based on session ratings and outcomes
                    total_rating = sum(session.get("rating", 0) for session in sessions)
                    return min(total_rating / len(sessions), 5.0) / 5.0  # Normalize to 0-1
            
            elif source == "communications":
                # Get communication data
                communications = await self.parent_ai_insights_service.get_communication_history(
                    parent_id, child_id, start_date, end_date
                )
                if communications:
                    # Calculate frequency based on number of communications
                    days_period = (end_date - start_date).days
                    return min(len(communications) / days_period, 1.0)  # Normalize to 0-1
            
            elif source == "resource_usage":
                # Get resource usage data
                usage_data = await self.parent_resource_library_service.get_resource_usage_analytics(
                    parent_id, start_date, end_date
                )
                if usage_data:
                    # Calculate utilization based on resources accessed vs. recommended
                    accessed = usage_data.get("resources_accessed", 0)
                    recommended = usage_data.get("resources_recommended", 1)
                    return min(accessed / recommended, 1.0) if recommended > 0 else 0
            
            elif source == "goals":
                # Get goal achievement data
                goals = await self.parent_ai_insights_service.get_goal_progress(
                    parent_id, child_id, start_date, end_date
                )
                if goals:
                    # Calculate achievement rate
                    achieved = sum(1 for goal in goals if goal.get("achieved", False))
                    return achieved / len(goals)
            
            elif source == "interventions":
                # Get intervention data
                interventions = await self.predictive_analytics_service.get_intervention_history(
                    child_id, start_date, end_date
                )
                if interventions:
                    # Calculate timeliness based on intervention response time
                    timely_interventions = sum(
                        1 for intervention in interventions
                        if intervention.get("response_time_hours", 0) <= 24
                    )
                    return timely_interventions / len(interventions)
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating individual metric {metric_name}: {str(e)}")
            return None
    
    async def _get_effectiveness_benchmarks(
        self,
        parent_id: str,
        child_id: str,
        period: TimePeriod
    ) -> List[float]:
        """Get benchmark data for effectiveness metrics"""
        try:
            # Query database for similar parents' effectiveness scores
            benchmark_scores = []
            
            # Get peer benchmarks (similar demographic/education level)
            peer_query = {
                "collection": "parent_effectiveness_metrics",
                "filters": [
                    {"field": "period", "operator": "==", "value": period.value},
                    {"field": "metric_type", "operator": "==", "value": "overall_effectiveness"}
                ],
                "limit": 100
            }
            
            peer_results = await self.db_service.query_documents(peer_query)
            
            for result in peer_results:
                score = result.get("value", 0)
                if score > 0:
                    benchmark_scores.append(score)
            
            return benchmark_scores
            
        except Exception as e:
            logger.error(f"Error getting effectiveness benchmarks: {str(e)}")
            return []
    
    def _calculate_percentile(self, value: float, benchmark_data: List[float]) -> float:
        """Calculate percentile rank of value against benchmark data"""
        if not benchmark_data:
            return 50.0  # Default to 50th percentile
        
        sorted_data = sorted(benchmark_data)
        n = len(sorted_data)
        
        if value <= sorted_data[0]:
            return 0.0
        elif value >= sorted_data[-1]:
            return 100.0
        
        # Find rank
        rank = sum(1 for x in sorted_data if x < value)
        percentile = (rank / n) * 100
        
        return round(percentile, 2)
    
    def _calculate_rank(self, value: float, benchmark_data: List[float]) -> int:
        """Calculate rank of value in benchmark data"""
        if not benchmark_data:
            return 1
        
        sorted_data = sorted(benchmark_data, reverse=True)
        
        try:
            return sorted_data.index(value) + 1
        except ValueError:
            # Value not in list, find appropriate position
            rank = sum(1 for x in sorted_data if x > value) + 1
            return rank
    
    async def _calculate_effectiveness_trend(
        self,
        parent_id: str,
        child_id: str,
        period: TimePeriod
    ) -> str:
        """Calculate effectiveness trend over time"""
        try:
            # Get historical effectiveness data
            end_date = datetime.now()
            start_date = self._get_period_start_date(end_date, period)
            
            # Get multiple periods for trend analysis
            periods_data = []
            
            for i in range(3):  # Get last 3 periods
                period_end = end_date - timedelta(days=i * 30)
                period_start = self._get_period_start_date(period_end, period)
                
                # Calculate effectiveness for this period
                effectiveness = await self._calculate_historical_effectiveness(
                    parent_id, child_id, period_start, period_end
                )
                
                if effectiveness is not None:
                    periods_data.append(effectiveness)
            
            if len(periods_data) < 2:
                return "stable"
            
            # Determine trend
            if all(periods_data[i] < periods_data[i+1] for i in range(len(periods_data)-1)):
                return "improving"
            elif all(periods_data[i] > periods_data[i+1] for i in range(len(periods_data)-1)):
                return "declining"
            else:
                return "stable"
            
        except Exception as e:
            logger.error(f"Error calculating effectiveness trend: {str(e)}")
            return "stable"
    
    async def _calculate_historical_effectiveness(
        self,
        parent_id: str,
        child_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[float]:
        """Calculate historical effectiveness for a specific period"""
        try:
            # Query historical effectiveness metrics
            query = {
                "collection": "parent_effectiveness_metrics",
                "filters": [
                    {"field": "parent_id", "operator": "==", "value": parent_id},
                    {"field": "child_id", "operator": "==", "value": child_id},
                    {"field": "metric_type", "operator": "==", "value": "overall_effectiveness"},
                    {"field": "created_at", "operator": ">=", "value": start_date},
                    {"field": "created_at", "operator": "<=", "value": end_date}
                ],
                "limit": 1
            }
            
            results = await self.db_service.query_documents(query)
            
            if results:
                return results[0].get("value", 0)
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating historical effectiveness: {str(e)}")
            return None
    
    def _get_metric_status(self, value: float) -> str:
        """Get status classification for metric value"""
        if value >= 0.8:
            return "excellent"
        elif value >= 0.6:
            return "good"
        elif value >= 0.4:
            return "average"
        elif value >= 0.2:
            return "below_average"
        else:
            return "poor"
    
    async def _generate_effectiveness_insights(
        self,
        parent_id: str,
        child_id: str,
        metrics: Dict[str, Any],
        overall_score: float,
        trend: str,
        language: str
    ) -> List[str]:
        """Generate AI-powered insights for effectiveness metrics"""
        try:
            # Prepare prompt for AI
            prompt = f"""
            Generate insights for parent effectiveness based on the following data:
            
            Overall Score: {overall_score:.2f}/1.0
            Trend: {trend}
            
            Individual Metrics:
            {json.dumps(metrics, indent=2)}
            
            Provide 3-5 actionable insights in {language} that help the parent understand:
            1. What they're doing well
            2. Areas for improvement
            3. Specific actions to take
            4. How their involvement impacts their child's learning
            """
            
            # Generate insights using AI
            response = await self.gemini_service.generate_content(prompt)
            
            # Parse and return insights
            insights = []
            if response and "content" in response:
                content = response["content"]
                # Split by lines and filter empty ones
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                insights = lines[:5]  # Take first 5 insights
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating effectiveness insights: {str(e)}")
            return ["Unable to generate insights at this time."]
    
    async def _store_effectiveness_metric(self, metric: ParentEffectivenessMetric) -> None:
        """Store effectiveness metric in database"""
        try:
            await self.db_service.create_document(
                "parent_effectiveness_metrics",
                asdict(metric)
            )
        except Exception as e:
            logger.error(f"Error storing effectiveness metric: {str(e)}")
    
    def _calculate_pearson_correlation(
        self,
        x_data: List[float],
        y_data: List[float]
    ) -> float:
        """Calculate Pearson correlation coefficient"""
        try:
            if len(x_data) != len(y_data) or len(x_data) < 2:
                return 0.0
            
            n = len(x_data)
            sum_x = sum(x_data)
            sum_y = sum(y_data)
            sum_xy = sum(x * y for x, y in zip(x_data, y_data))
            sum_x2 = sum(x * x for x in x_data)
            sum_y2 = sum(y * y for y in y_data)
            
            numerator = n * sum_xy - sum_x * sum_y
            denominator = math.sqrt((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y))
            
            if denominator == 0:
                return 0.0
            
            correlation = numerator / denominator
            return round(correlation, 3)
            
        except Exception as e:
            logger.error(f"Error calculating Pearson correlation: {str(e)}")
            return 0.0
    
    def _calculate_significance_level(self, correlation: float, sample_size: int) -> float:
        """Calculate significance level (p-value) for correlation"""
        try:
            if sample_size < 3:
                return 1.0
            
            # Calculate t-statistic
            t = abs(correlation) * math.sqrt((sample_size - 2) / (1 - correlation * correlation))
            
            # Approximate p-value (simplified)
            if t > 3:
                return 0.01  # Highly significant
            elif t > 2:
                return 0.05  # Significant
            elif t > 1:
                return 0.1   # Marginally significant
            else:
                return 0.5   # Not significant
                
        except Exception as e:
            logger.error(f"Error calculating significance level: {str(e)}")
            return 1.0
    
    def _determine_correlation_trend(self, correlation: float) -> str:
        """Determine correlation trend direction"""
        if correlation > 0.1:
            return "positive"
        elif correlation < -0.1:
            return "negative"
        else:
            return "neutral"
    
    def _classify_correlation_strength(self, correlation: float) -> str:
        """Classify correlation strength"""
        abs_correlation = abs(correlation)
        
        if abs_correlation >= 0.7:
            return "strong"
        elif abs_correlation >= 0.5:
            return "moderate"
        elif abs_correlation >= 0.3:
            return "weak"
        else:
            return "very_weak"
    
    async def _get_time_series_data(
        self,
        parent_id: str,
        child_id: str,
        metric_name: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[float]:
        """Get time series data for a specific metric"""
        try:
            # This would query the appropriate data source based on metric_name
            # For now, return sample data
            data_points = []
            
            # Generate sample data points (in real implementation, query database)
            days_diff = (end_date - start_date).days
            for i in range(min(days_diff, 30)):  # Limit to 30 data points
                # Sample value - in real implementation, get from database
                value = 0.5 + (i * 0.01) + (hash(f"{metric_name}_{i}") % 10) * 0.05
                data_points.append(min(max(value, 0), 1))  # Clamp between 0 and 1
            
            return data_points
            
        except Exception as e:
            logger.error(f"Error getting time series data for {metric_name}: {str(e)}")
            return []
    
    async def _generate_correlation_insights(
        self,
        involvement_metric: str,
        outcome_metric: str,
        correlation: float,
        significance: float,
        language: str
    ) -> List[str]:
        """Generate insights for correlation analysis"""
        try:
            prompt = f"""
            Generate insights about the correlation between parent involvement and student outcomes:
            
            Involvement Metric: {involvement_metric}
            Outcome Metric: {outcome_metric}
            Correlation Coefficient: {correlation:.3f}
            Significance Level: {significance:.3f}
            
            Provide 2-3 insights in {language} explaining:
            1. What this correlation means in practical terms
            2. How strong this relationship is
            3. What parents should understand about this connection
            """
            
            response = await self.gemini_service.generate_content(prompt)
            
            insights = []
            if response and "content" in response:
                content = response["content"]
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                insights = lines[:3]
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating correlation insights: {str(e)}")
            return ["Unable to generate correlation insights at this time."]
    
    async def _generate_correlation_recommendations(
        self,
        involvement_metric: str,
        outcome_metric: str,
        correlation: float,
        trend_direction: str,
        language: str
    ) -> List[str]:
        """Generate recommendations based on correlation analysis"""
        try:
            prompt = f"""
            Generate actionable recommendations based on correlation analysis:
            
            Involvement Metric: {involvement_metric}
            Outcome Metric: {outcome_metric}
            Correlation: {correlation:.3f}
            Trend Direction: {trend_direction}
            
            Provide 3-4 specific recommendations in {language} for parents to:
            1. Leverage positive correlations
            2. Address negative correlations
            3. Improve the involvement metric
            4. Monitor the outcome metric
            """
            
            response = await self.gemini_service.generate_content(prompt)
            
            recommendations = []
            if response and "content" in response:
                content = response["content"]
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                recommendations = lines[:4]
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating correlation recommendations: {str(e)}")
            return ["Unable to generate recommendations at this time."]
    
    async def _store_correlation_analysis(self, analysis: CorrelationAnalysis) -> None:
        """Store correlation analysis in database"""
        try:
            await self.db_service.create_document(
                "correlation_analyses",
                asdict(analysis)
            )
        except Exception as e:
            logger.error(f"Error storing correlation analysis: {str(e)}")
    
    async def _get_current_metrics(
        self,
        parent_id: str,
        child_id: str
    ) -> Dict[str, float]:
        """Get current metrics for comparative analysis"""
        try:
            metrics = {}
            
            # Get effectiveness metrics
            effectiveness = await self.calculate_parent_effectiveness(
                parent_id, child_id, TimePeriod.MONTHLY
            )
            
            if effectiveness:
                metrics["overall_effectiveness"] = effectiveness.get("overall_score", 0)
                
                # Add individual metrics
                individual_metrics = effectiveness.get("individual_metrics", {})
                for metric_name, metric_data in individual_metrics.items():
                    metrics[metric_name] = metric_data.get("value", 0)
            
            # Get engagement metrics
            engagement = await self.parent_ai_insights_service.get_engagement_metrics(
                parent_id, child_id
            )
            
            if engagement:
                metrics["engagement_score"] = engagement.get("score", 0)
                metrics["interaction_frequency"] = engagement.get("frequency", 0)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting current metrics: {str(e)}")
            return {}
    
    async def _get_benchmark_data(
        self,
        parent_id: str,
        child_id: str,
        benchmark_type: BenchmarkType,
        period: TimePeriod
    ) -> Dict[str, List[float]]:
        """Get benchmark data for comparison"""
        try:
            benchmark_data = {}
            
            # Define filters based on benchmark type
            filters = [
                {"field": "period", "operator": "==", "value": period.value}
            ]
            
            if benchmark_type == BenchmarkType.PEER:
                # Similar demographic/education level
                filters.append({"field": "benchmark_type", "operator": "==", "value": "peer"})
            elif benchmark_type == BenchmarkType.REGIONAL:
                # Same geographical region
                filters.append({"field": "benchmark_type", "operator": "==", "value": "regional"})
            elif benchmark_type == BenchmarkType.SUBJECT:
                # Same subject/exam
                filters.append({"field": "benchmark_type", "operator": "==", "value": "subject"})
            elif benchmark_type == BenchmarkType.GLOBAL:
                # All users
                filters.append({"field": "benchmark_type", "operator": "==", "value": "global"})
            
            # Query benchmark data
            query = {
                "collection": "benchmark_metrics",
                "filters": filters,
                "limit": 500
            }
            
            results = await self.db_service.query_documents(query)
            
            # Organize data by metric
            for result in results:
                metric_name = result.get("metric_name")
                value = result.get("value", 0)
                
                if metric_name and value > 0:
                    if metric_name not in benchmark_data:
                        benchmark_data[metric_name] = []
                    benchmark_data[metric_name].append(value)
            
            return benchmark_data
            
        except Exception as e:
            logger.error(f"Error getting benchmark data: {str(e)}")
            return {}
    
    def _classify_performance_level(self, percentile: float) -> str:
        """Classify performance level based on percentile"""
        if percentile >= 90:
            return "outstanding"
        elif percentile >= 75:
            return "excellent"
        elif percentile >= 60:
            return "good"
        elif percentile >= 40:
            return "average"
        elif percentile >= 25:
            return "below_average"
        else:
            return "needs_improvement"
    
    async def _generate_comparative_insights(
        self,
        metrics_comparison: Dict[str, Any],
        strengths: List[str],
        improvement_areas: List[str],
        benchmark_type: BenchmarkType,
        language: str
    ) -> List[str]:
        """Generate insights for comparative analytics"""
        try:
            prompt = f"""
            Generate insights for comparative analytics against {benchmark_type.value} benchmarks:
            
            Strengths: {', '.join(strengths)}
            Improvement Areas: {', '.join(improvement_areas)}
            
            Metrics Comparison:
            {json.dumps(metrics_comparison, indent=2)}
            
            Provide 3-4 insights in {language} that help parents understand:
            1. How they compare to others
            2. What makes them stand out
            3. Where they should focus improvement
            4. Actionable steps to improve their ranking
            """
            
            response = await self.gemini_service.generate_content(prompt)
            
            insights = []
            if response and "content" in response:
                content = response["content"]
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                insights = lines[:4]
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating comparative insights: {str(e)}")
            return ["Unable to generate comparative insights at this time."]
    
    async def _store_comparative_analytics(self, analytics: ComparativeAnalytics) -> None:
        """Store comparative analytics in database"""
        try:
            await self.db_service.create_document(
                "comparative_analytics",
                asdict(analytics)
            )
        except Exception as e:
            logger.error(f"Error storing comparative analytics: {str(e)}")
    
    async def _identify_influencing_factors(
        self,
        parent_id: str,
        child_id: str,
        prediction_type: str,
        timeframe: str
    ) -> List[str]:
        """Identify factors influencing predictions"""
        try:
            # Get recent data that might influence predictions
            factors = []
            
            # Study session patterns
            sessions = await self.interactive_study_tools_service.get_parent_study_sessions(
                parent_id, child_id
            )
            if sessions:
                factors.append("Recent study session frequency and quality")
            
            # Resource utilization
            resource_usage = await self.parent_resource_library_service.get_resource_usage_analytics(
                parent_id
            )
            if resource_usage and resource_usage.get("resources_accessed", 0) > 0:
                factors.append("Resource utilization patterns")
            
            # Communication patterns
            communications = await self.parent_ai_insights_service.get_communication_history(
                parent_id, child_id
            )
            if communications:
                factors.append("Parent-child communication frequency")
            
            # Goal achievement
            goals = await self.parent_ai_insights_service.get_goal_progress(
                parent_id, child_id
            )
            if goals:
                achieved_goals = sum(1 for goal in goals if goal.get("achieved", False))
                if achieved_goals > 0:
                    factors.append("Recent goal achievement rate")
            
            return factors
            
        except Exception as e:
            logger.error(f"Error identifying influencing factors: {str(e)}")
            return []
    
    async def _generate_predictive_recommendations(
        self,
        prediction_data: Dict[str, Any],
        influencing_factors: List[str],
        language: str
    ) -> List[str]:
        """Generate recommendations based on predictions"""
        try:
            prompt = f"""
            Generate recommendations based on predictive analytics:
            
            Prediction Data:
            {json.dumps(prediction_data, indent=2)}
            
            Influencing Factors:
            {', '.join(influencing_factors)}
            
            Provide 3-4 specific recommendations in {language} to:
            1. Maximize positive predicted outcomes
            2. Mitigate potential negative outcomes
            3. Strengthen influencing factors
            4. Prepare for the predicted timeframe
            """
            
            response = await self.gemini_service.generate_content(prompt)
            
            recommendations = []
            if response and "content" in response:
                content = response["content"]
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                recommendations = lines[:4]
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating predictive recommendations: {str(e)}")
            return ["Unable to generate recommendations at this time."]
    
    def _classify_risk_level(self, prediction_data: Dict[str, Any], confidence: float) -> str:
        """Classify risk level based on prediction and confidence"""
        try:
            # Extract predicted outcome
            predicted_value = prediction_data.get("predicted_value", 0.5)
            
            # Consider both predicted value and confidence
            if confidence < 0.5:
                return "uncertain"
            elif predicted_value < 0.3:
                return "high"
            elif predicted_value < 0.6:
                return "moderate"
            else:
                return "low"
                
        except Exception:
            return "unknown"
    
    async def _store_predictive_insight(self, insight: PredictiveInsight) -> None:
        """Store predictive insight in database"""
        try:
            await self.db_service.create_document(
                "predictive_insights",
                asdict(insight)
            )
        except Exception as e:
            logger.error(f"Error storing predictive insight: {str(e)}")
    
    async def _create_effectiveness_trend_chart(
        self,
        parent_id: str,
        child_id: str,
        filters: Dict[str, Any],
        language: str
    ) -> Dict[str, Any]:
        """Create effectiveness trend chart data"""
        try:
            # Get historical effectiveness data
            end_date = datetime.now()
            data_points = []
            
            for i in range(6):  # Last 6 periods
                period_end = end_date - timedelta(days=i * 30)
                period_start = self._get_period_start_date(period_end, TimePeriod.MONTHLY)
                
                effectiveness = await self._calculate_historical_effectiveness(
                    parent_id, child_id, period_start, period_end
                )
                
                if effectiveness is not None:
                    data_points.append({
                        "date": period_start.strftime("%Y-%m-%d"),
                        "value": effectiveness
                    })
            
            # Reverse to show chronological order
            data_points.reverse()
            
            return VisualizationData(
                chart_type="line",
                title="Parent Effectiveness Trend",
                data=data_points,
                x_axis="date",
                y_axis="value",
                filters=filters,
                metadata={"unit": "score", "min": 0, "max": 1}
            ).__dict__
            
        except Exception as e:
            logger.error(f"Error creating effectiveness trend chart: {str(e)}")
            return {}
    
    async def _create_correlation_heatmap(
        self,
        parent_id: str,
        child_id: str,
        filters: Dict[str, Any],
        language: str
    ) -> Dict[str, Any]:
        """Create correlation heatmap data"""
        try:
            # Get correlation data
            correlation_data = await self.analyze_correlation(
                parent_id, child_id,
                ["teaching_quality", "communication_frequency", "resource_utilization"],
                ["academic_performance", "engagement_level", "learning_outcomes"],
                TimePeriod.MONTHLY, language
            )
            
            # Prepare heatmap data
            heatmap_data = []
            
            for result in correlation_data.get("correlation_results", []):
                heatmap_data.append({
                    "involvement_metric": result["involvement_metric"],
                    "outcome_metric": result["outcome_metric"],
                    "correlation": result["correlation_coefficient"],
                    "strength": result["strength"]
                })
            
            return VisualizationData(
                chart_type="heatmap",
                title="Parent Involvement vs Student Outcomes Correlation",
                data=heatmap_data,
                x_axis="outcome_metric",
                y_axis="involvement_metric",
                filters=filters,
                metadata={"color_scale": "RdYlBu", "min": -1, "max": 1}
            ).__dict__
            
        except Exception as e:
            logger.error(f"Error creating correlation heatmap: {str(e)}")
            return {}
    
    async def _create_performance_radar_chart(
        self,
        parent_id: str,
        child_id: str,
        filters: Dict[str, Any],
        language: str
    ) -> Dict[str, Any]:
        """Create performance radar chart data"""
        try:
            # Get current effectiveness metrics
            effectiveness = await self.calculate_parent_effectiveness(
                parent_id, child_id, TimePeriod.MONTHLY, language
            )
            
            # Prepare radar chart data
            radar_data = []
            
            individual_metrics = effectiveness.get("individual_metrics", {})
            for metric_name, metric_data in individual_metrics.items():
                radar_data.append({
                    "metric": metric_name.replace("_", " ").title(),
                    "value": metric_data.get("value", 0),
                    "benchmark": metric_data.get("benchmark_value", 0.5)
                })
            
            return VisualizationData(
                chart_type="radar",
                title="Parent Effectiveness Metrics",
                data=radar_data,
                x_axis="metric",
                y_axis="value",
                filters=filters,
                metadata={"axes": radar_data, "min": 0, "max": 1}
            ).__dict__
            
        except Exception as e:
            logger.error(f"Error creating performance radar chart: {str(e)}")
            return {}
    
    async def _create_progress_timeline_chart(
        self,
        parent_id: str,
        child_id: str,
        filters: Dict[str, Any],
        language: str
    ) -> Dict[str, Any]:
        """Create progress timeline chart data"""
        try:
            # Get progress data over time
            timeline_data = []
            
            # Get recent study sessions and their outcomes
            sessions = await self.interactive_study_tools_service.get_parent_study_sessions(
                parent_id, child_id
            )
            
            for session in sessions[:20]:  # Last 20 sessions
                timeline_data.append({
                    "date": session.get("created_at", ""),
                    "event_type": "study_session",
                    "outcome": session.get("outcome", "neutral"),
                    "rating": session.get("rating", 0)
                })
            
            return VisualizationData(
                chart_type="timeline",
                title="Parent-Child Learning Journey",
                data=timeline_data,
                x_axis="date",
                y_axis="event_type",
                filters=filters,
                metadata={"event_types": ["study_session", "goal_achieved", "intervention"]}
            ).__dict__
            
        except Exception as e:
            logger.error(f"Error creating progress timeline chart: {str(e)}")
            return {}
    
    async def _create_benchmark_comparison_chart(
        self,
        parent_id: str,
        child_id: str,
        filters: Dict[str, Any],
        language: str
    ) -> Dict[str, Any]:
        """Create benchmark comparison chart data"""
        try:
            # Get comparative analytics
            comparative = await self.generate_comparative_analytics(
                parent_id, child_id,
                [BenchmarkType.PEER, BenchmarkType.REGIONAL],
                TimePeriod.MONTHLY, language
            )
            
            # Prepare comparison chart data
            comparison_data = []
            
            for benchmark_type, data in comparative.get("comparative_results", {}).items():
                metrics_comparison = data.get("metrics_comparison", {})
                
                for metric_name, metric_data in metrics_comparison.items():
                    comparison_data.append({
                        "metric": metric_name,
                        "benchmark_type": benchmark_type,
                        "current_value": metric_data.get("current_value", 0),
                        "benchmark_average": metric_data.get("benchmark_average", 0),
                        "percentile": metric_data.get("percentile", 0)
                    })
            
            return VisualizationData(
                chart_type="bar",
                title="Performance vs Benchmarks",
                data=comparison_data,
                x_axis="metric",
                y_axis="value",
                filters=filters,
                metadata={"group_by": "benchmark_type"}
            ).__dict__
            
        except Exception as e:
            logger.error(f"Error creating benchmark comparison chart: {str(e)}")
            return {}
    
    async def _create_generic_chart(
        self,
        parent_id: str,
        child_id: str,
        chart_type: str,
        filters: Dict[str, Any],
        language: str
    ) -> Dict[str, Any]:
        """Create generic chart data"""
        try:
            # Return empty chart data for unsupported types
            return VisualizationData(
                chart_type=chart_type,
                title=f"{chart_type.title()} Chart",
                data=[],
                x_axis="",
                y_axis="",
                filters=filters,
                metadata={}
            ).__dict__
            
        except Exception as e:
            logger.error(f"Error creating generic chart: {str(e)}")
            return {}
    
    async def _generate_correlation_summary(
        self,
        correlation_results: List[Dict[str, Any]],
        language: str
    ) -> List[str]:
        """Generate summary insights for correlation analysis"""
        try:
            prompt = f"""
            Generate a summary of correlation analysis results:
            
            {json.dumps(correlation_results, indent=2)}
            
            Provide 2-3 key insights in {language} that summarize:
            1. The strongest correlations found
            2. The most surprising relationships
            3. Overall patterns in parent-child learning dynamics
            """
            
            response = await self.gemini_service.generate_content(prompt)
            
            insights = []
            if response and "content" in response:
                content = response["content"]
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                insights = lines[:3]
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating correlation summary: {str(e)}")
            return ["Unable to generate summary at this time."]
    
    async def _generate_comparative_summary(
        self,
        comparative_results: Dict[str, Any],
        language: str
    ) -> List[str]:
        """Generate summary insights for comparative analytics"""
        try:
            prompt = f"""
            Generate a summary of comparative analytics results:
            
            {json.dumps(comparative_results, indent=2)}
            
            Provide 2-3 key insights in {language} that summarize:
            1. How the parent compares across different benchmarks
            2. Consistent strengths and improvement areas
            3. Overall competitive position
            """
            
            response = await self.gemini_service.generate_content(prompt)
            
            insights = []
            if response and "content" in response:
                content = response["content"]
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                insights = lines[:3]
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating comparative summary: {str(e)}")
            return ["Unable to generate summary at this time."]
    
    async def _generate_predictive_summary(
        self,
        predictive_results: Dict[str, Any],
        language: str
    ) -> List[str]:
        """Generate summary insights for predictive analytics"""
        try:
            prompt = f"""
            Generate a summary of predictive analytics results:
            
            {json.dumps(predictive_results, indent=2)}
            
            Provide 2-3 key insights in {language} that summarize:
            1. Most likely future outcomes
            2. Key factors influencing predictions
            3. Priority areas for proactive intervention
            """
            
            response = await self.gemini_service.generate_content(prompt)
            
            insights = []
            if response and "content" in response:
                content = response["content"]
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                insights = lines[:3]
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating predictive summary: {str(e)}")
            return ["Unable to generate summary at this time."]
    
    async def _generate_dashboard_summary(
        self,
        effectiveness: Dict[str, Any],
        correlation: Dict[str, Any],
        comparative: Dict[str, Any],
        predictive: Dict[str, Any],
        language: str
    ) -> Dict[str, Any]:
        """Generate comprehensive dashboard summary"""
        try:
            # Extract key metrics
            overall_score = effectiveness.get("overall_score", 0)
            trend = effectiveness.get("trend", "stable")
            
            # Count significant correlations
            significant_correlations = sum(
                1 for result in correlation.get("correlation_results", [])
                if result.get("significance_level", 1) < 0.05
            )
            
            # Count strengths
            total_strengths = sum(
                len(data.get("strengths", []))
                for data in comparative.get("comparative_results", {}).values()
            )
            
            # Count high-confidence predictions
            high_confidence_predictions = sum(
                1 for prediction_type, timeframes in predictive.get("predictive_results", {}).items()
                for timeframe, data in timeframes.items()
                if data.get("confidence_score", 0) > 0.7
            )
            
            # Generate overall status
            if overall_score >= 0.8 and trend == "improving":
                status = "excellent"
                status_message = "Outstanding parent involvement with positive trends"
            elif overall_score >= 0.6:
                status = "good"
                status_message = "Strong parent involvement with room for growth"
            elif overall_score >= 0.4:
                status = "average"
                status_message = "Moderate parent involvement - focus on consistency"
            else:
                status = "needs_improvement"
                status_message = "Parent involvement needs significant attention"
            
            # Generate priority actions
            priority_actions = []
            
            if overall_score < 0.5:
                priority_actions.append("Increase overall engagement frequency")
            
            if significant_correlations > 0:
                priority_actions.append("Leverage strong correlations to boost learning")
            
            if total_strengths == 0:
                priority_actions.append("Develop core parenting strengths")
            
            if high_confidence_predictions > 0:
                priority_actions.append("Focus on high-impact areas identified by predictions")
            
            return {
                "status": status,
                "status_message": status_message,
                "key_metrics": {
                    "overall_score": round(overall_score, 2),
                    "trend": trend,
                    "significant_correlations": significant_correlations,
                    "total_strengths": total_strengths,
                    "high_confidence_predictions": high_confidence_predictions
                },
                "priority_actions": priority_actions,
                "next_steps": [
                    "Review detailed effectiveness metrics",
                    "Explore correlation insights",
                    "Compare against benchmarks",
                    "Review predictive recommendations"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error generating dashboard summary: {str(e)}")
            return {
                "status": "unknown",
                "status_message": "Unable to generate summary",
                "key_metrics": {},
                "priority_actions": [],
                "next_steps": []
            }