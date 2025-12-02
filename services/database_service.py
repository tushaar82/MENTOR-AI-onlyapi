"""
Database Service for AI Interactions and Parent Features

This service handles all database operations for new collections using Firestore:
- AI interactions
- Parent insights
- Engagement metrics
- Communication history
- Intervention alerts

Author: Mentor AI Team
Version: 1.0.0
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from google.cloud import firestore
from google.api_core.exceptions import GoogleAPICallError

from models.database_models import (
    AIInteraction, AIInteractionSummary, ParentInsight, ParentDashboardConfig,
    EngagementMetric, EngagementSummary, StudySession, CommunicationRecord,
    CommunicationTemplate, InterventionAlert, InterventionRule,
    PredictionResult, CommunicationSuggestion, EngagementChallenge, Achievement,
    ParentResource, ResourceUsage, DATABASE_SCHEMAS
)
from utils.firebase_config import get_firestore_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for Firestore database operations."""
    
    def __init__(self):
        """Initialize database service."""
        self.db = None
        self.collections = {}
    
    async def connect(self):
        """Connect to Firestore."""
        try:
            self.db = get_firestore_client()
            
            # Initialize collections
            for collection_name in DATABASE_SCHEMAS.keys():
                self.collections[collection_name] = self.db.collection(collection_name)
            
            # Ensure indexes exist (Firestore handles this automatically)
            await self._ensure_indexes()
            
            logger.info("Connected to Firestore successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Firestore: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from Firestore."""
        # Firestore client doesn't require explicit disconnection
        logger.info("Firestore connection closed")
    
    async def _ensure_indexes(self):
        """Ensure all required indexes exist."""
        try:
            # Firestore handles index creation automatically based on query patterns
            # Log the collections that will be used
            for collection_name in DATABASE_SCHEMAS.keys():
                logger.info(f"Firestore collection ready: {collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to ensure indexes: {e}")
    
    # ============================================================================
    # AI INTERACTIONS METHODS
    # ============================================================================
    
    async def save_ai_interaction(self, interaction: AIInteraction) -> str:
        """Save an AI interaction to Firestore."""
        try:
            collection = self.collections["ai_interactions"]
            
            # Convert to dict
            interaction_dict = interaction.model_dump()
            
            # Insert interaction
            doc_ref = collection.document(interaction.interaction_id)
            await doc_ref.set(interaction_dict)
            
            logger.info(f"Saved AI interaction: {interaction.interaction_id}")
            return interaction.interaction_id
            
        except Exception as e:
            logger.error(f"Failed to save AI interaction: {e}")
            raise
    
    async def get_ai_interactions(
        self,
        user_id: Optional[str] = None,
        student_id: Optional[str] = None,
        interaction_type: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[AIInteraction]:
        """Get AI interactions with optional filters."""
        try:
            collection = self.collections["ai_interactions"]
            
            # Build query
            query = collection
            if user_id:
                query = query.where("user_id", "==", user_id)
            if student_id:
                query = query.where("student_id", "==", student_id)
            if interaction_type:
                query = query.where("interaction_type", "==", interaction_type)
            if status:
                query = query.where("status", "==", status)
            if start_date:
                query = query.where("created_at", ">=", start_date)
            if end_date:
                query = query.where("created_at", "<=", end_date)
            
            # Execute query
            query = query.order_by("created_at", direction=firestore.Query.DESCENDING)
            if skip > 0:
                # Firestore doesn't have skip, we'll handle this in the client
                docs = []
                query_stream = query.stream()
                for i, doc in enumerate(query_stream):
                    if i >= skip + limit:
                        break
                    if i >= skip:
                        docs.append(doc)
            else:
                docs = list(query.limit(limit).stream())
            
            # Convert to AIInteraction objects
            interactions = []
            for doc in docs:
                result = doc.to_dict()
                result["document_id"] = doc.id
                interactions.append(AIInteraction(**result))
            
            return interactions
            
        except Exception as e:
            logger.error(f"Failed to get AI interactions: {e}")
            raise
    
    async def update_ai_interaction_status(
        self,
        interaction_id: str,
        status: str,
        response_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        tokens_used: Optional[Dict[str, int]] = None,
        cost: Optional[float] = None,
        response_time_ms: Optional[int] = None,
        cached: Optional[bool] = None
    ) -> bool:
        """Update AI interaction status and related fields."""
        try:
            collection = self.collections["ai_interactions"]
            
            # Build update document
            update_doc = {
                "status": status,
                "completed_at": datetime.utcnow()
            }
            
            if response_data is not None:
                update_doc["response_data"] = response_data
            if error_message is not None:
                update_doc["error_message"] = error_message
            if tokens_used is not None:
                update_doc["tokens_used"] = tokens_used
            if cost is not None:
                update_doc["cost"] = cost
            if response_time_ms is not None:
                update_doc["response_time_ms"] = response_time_ms
            if cached is not None:
                update_doc["cached"] = cached
            
            # Update interaction
            doc_ref = collection.document(interaction_id)
            await doc_ref.update(update_doc)
            
            logger.info(f"Updated AI interaction status: {interaction_id} -> {status}")
            return True
            
        except GoogleAPICallError as e:
            if "NOT_FOUND" in str(e):
                logger.warning(f"AI interaction not found for update: {interaction_id}")
                return False
            else:
                logger.error(f"Failed to update AI interaction status: {e}")
                raise
        except Exception as e:
            logger.error(f"Failed to update AI interaction status: {e}")
            raise
    
    async def get_ai_interaction_summary(
        self,
        user_id: str,
        period_start: datetime,
        period_end: datetime
    ) -> AIInteractionSummary:
        """Get AI interaction summary for a user and period."""
        try:
            collection = self.collections["ai_interactions"]
            
            # Query interactions
            query = collection.where("user_id", "==", user_id)\
                           .where("created_at", ">=", period_start)\
                           .where("created_at", "<=", period_end)
            
            docs = list(query.stream())
            
            if not docs:
                # Return empty summary
                return AIInteractionSummary(
                    user_id=user_id,
                    period_start=period_start,
                    period_end=period_end,
                    total_interactions=0,
                    successful_interactions=0,
                    failed_interactions=0,
                    total_cost=0.0,
                    total_tokens=0,
                    average_response_time_ms=0.0,
                    interaction_types={}
                )
            
            # Calculate summary
            total_interactions = len(docs)
            successful_interactions = sum(1 for doc in docs if doc.to_dict().get("status") == "completed")
            failed_interactions = sum(1 for doc in docs if doc.to_dict().get("status") == "failed")
            total_cost = sum(doc.to_dict().get("cost", 0.0) for doc in docs)
            total_tokens = sum(sum(doc.to_dict().get("tokens_used", {}).values()) for doc in docs)
            avg_response_time = sum(doc.to_dict().get("response_time_ms", 0) for doc in docs) / total_interactions if total_interactions > 0 else 0
            
            # Count interaction types
            interaction_types = {}
            for doc in docs:
                interaction_type = doc.to_dict().get("interaction_type", "unknown")
                interaction_types[interaction_type] = interaction_types.get(interaction_type, 0) + 1
            
            return AIInteractionSummary(
                user_id=user_id,
                period_start=period_start,
                period_end=period_end,
                total_interactions=total_interactions,
                successful_interactions=successful_interactions,
                failed_interactions=failed_interactions,
                total_cost=total_cost,
                total_tokens=total_tokens,
                average_response_time_ms=avg_response_time,
                interaction_types=interaction_types
            )
            
        except Exception as e:
            logger.error(f"Failed to get AI interaction summary: {e}")
            raise
    
    # ============================================================================
    # PARENT INSIGHTS METHODS
    # ============================================================================
    
    async def save_parent_insight(self, insight: ParentInsight) -> str:
        """Save a parent insight to Firestore."""
        try:
            collection = self.collections["parent_insights"]
            
            # Convert to dict
            insight_dict = insight.model_dump()
            
            # Insert insight
            doc_ref = collection.document(insight.insight_id)
            await doc_ref.set(insight_dict)
            
            logger.info(f"Saved parent insight: {insight.insight_id}")
            return insight.insight_id
            
        except Exception as e:
            logger.error(f"Failed to save parent insight: {e}")
            raise
    
    async def get_parent_insights(
        self,
        parent_id: str,
        student_id: Optional[str] = None,
        insight_type: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[ParentInsight]:
        """Get parent insights with optional filters."""
        try:
            collection = self.collections["parent_insights"]
            
            # Build query
            query = collection.where("parent_id", "==", parent_id)
            if student_id:
                query = query.where("student_id", "==", student_id)
            if insight_type:
                query = query.where("insight_type", "==", insight_type)
            if severity:
                query = query.where("severity", "==", severity)
            if status:
                query = query.where("status", "==", status)
            if start_date:
                query = query.where("created_at", ">=", start_date)
            if end_date:
                query = query.where("created_at", "<=", end_date)
            
            # Execute query
            query = query.order_by("created_at", direction=firestore.Query.DESCENDING)
            docs = list(query.limit(limit).stream())
            
            # Convert to ParentInsight objects
            insights = []
            for doc in docs:
                result = doc.to_dict()
                result["document_id"] = doc.id
                insights.append(ParentInsight(**result))
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get parent insights: {e}")
            raise
    
    async def update_parent_insight_status(
        self,
        insight_id: str,
        status: str,
        action_taken: Optional[str] = None
    ) -> bool:
        """Update parent insight status."""
        try:
            collection = self.collections["parent_insights"]
            
            # Build update document
            update_doc = {"status": status}
            
            if status == "resolved":
                update_doc["resolved_at"] = datetime.utcnow()
            
            if action_taken is not None:
                update_doc["action_taken"] = action_taken
            
            # Update insight
            doc_ref = collection.document(insight_id)
            await doc_ref.update(update_doc)
            
            logger.info(f"Updated parent insight status: {insight_id} -> {status}")
            return True
            
        except GoogleAPICallError as e:
            if "NOT_FOUND" in str(e):
                logger.warning(f"Parent insight not found for update: {insight_id}")
                return False
            else:
                logger.error(f"Failed to update parent insight status: {e}")
                raise
        except Exception as e:
            logger.error(f"Failed to update parent insight status: {e}")
            raise
    
    # ============================================================================
    # ENGAGEMENT METRICS METHODS
    # ============================================================================
    
    async def save_engagement_metric(self, metric: EngagementMetric) -> str:
        """Save an engagement metric to Firestore."""
        try:
            collection = self.collections["engagement_metrics"]
            
            # Convert to dict
            metric_dict = metric.model_dump()
            
            # Insert metric
            doc_ref = collection.document(metric.metric_id)
            await doc_ref.set(metric_dict)
            
            logger.info(f"Saved engagement metric: {metric.metric_id}")
            return metric.metric_id
            
        except Exception as e:
            logger.error(f"Failed to save engagement metric: {e}")
            raise
    
    async def get_engagement_metrics(
        self,
        student_id: str,
        metric_type: Optional[str] = None,
        period: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[EngagementMetric]:
        """Get engagement metrics with optional filters."""
        try:
            collection = self.collections["engagement_metrics"]
            
            # Build query
            query = collection.where("student_id", "==", student_id)
            if metric_type:
                query = query.where("metric_type", "==", metric_type)
            if period:
                query = query.where("period", "==", period)
            if start_date:
                query = query.where("date", ">=", start_date)
            if end_date:
                query = query.where("date", "<=", end_date)
            
            # Execute query
            query = query.order_by("date", direction=firestore.Query.DESCENDING)
            docs = list(query.limit(limit).stream())
            
            # Convert to EngagementMetric objects
            metrics = []
            for doc in docs:
                result = doc.to_dict()
                result["document_id"] = doc.id
                metrics.append(EngagementMetric(**result))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get engagement metrics: {e}")
            raise
    
    async def save_study_session(self, session: StudySession) -> str:
        """Save a study session to Firestore."""
        try:
            collection = self.collections["engagement_metrics"]
            
            # Convert to dict
            session_dict = session.model_dump()
            
            # Insert session
            doc_ref = collection.document(session.session_id)
            await doc_ref.set(session_dict)
            
            logger.info(f"Saved study session: {session.session_id}")
            return session.session_id
            
        except Exception as e:
            logger.error(f"Failed to save study session: {e}")
            raise
    
    # ============================================================================
    # COMMUNICATION HISTORY METHODS
    # ============================================================================
    
    async def save_communication_record(self, record: CommunicationRecord) -> str:
        """Save a communication record to Firestore."""
        try:
            collection = self.collections["communication_history"]
            
            # Convert to dict
            record_dict = record.model_dump()
            
            # Insert record
            doc_ref = collection.document(record.communication_id)
            await doc_ref.set(record_dict)
            
            logger.info(f"Saved communication record: {record.communication_id}")
            return record.communication_id
            
        except Exception as e:
            logger.error(f"Failed to save communication record: {e}")
            raise
    
    async def get_communication_history(
        self,
        parent_id: str,
        student_id: Optional[str] = None,
        communication_type: Optional[str] = None,
        channel: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[CommunicationRecord]:
        """Get communication history with optional filters."""
        try:
            collection = self.collections["communication_history"]
            
            # Build query
            query = collection.where("parent_id", "==", parent_id)
            if student_id:
                query = query.where("student_id", "==", student_id)
            if communication_type:
                query = query.where("communication_type", "==", communication_type)
            if channel:
                query = query.where("channel", "==", channel)
            if status:
                query = query.where("status", "==", status)
            if start_date:
                query = query.where("created_at", ">=", start_date)
            if end_date:
                query = query.where("created_at", "<=", end_date)
            
            # Execute query
            query = query.order_by("created_at", direction=firestore.Query.DESCENDING)
            docs = list(query.limit(limit).stream())
            
            # Convert to CommunicationRecord objects
            records = []
            for doc in docs:
                result = doc.to_dict()
                result["document_id"] = doc.id
                records.append(CommunicationRecord(**result))
            
            return records
            
        except Exception as e:
            logger.error(f"Failed to get communication history: {e}")
            raise
    
    # ============================================================================
    # INTERVENTION ALERTS METHODS
    # ============================================================================
    
    async def save_intervention_alert(self, alert: InterventionAlert) -> str:
        """Save an intervention alert to Firestore."""
        try:
            collection = self.collections["intervention_alerts"]
            
            # Convert to dict
            alert_dict = alert.model_dump()
            
            # Insert alert
            doc_ref = collection.document(alert.alert_id)
            await doc_ref.set(alert_dict)
            
            logger.info(f"Saved intervention alert: {alert.alert_id}")
            return alert.alert_id
            
        except Exception as e:
            logger.error(f"Failed to save intervention alert: {e}")
            raise
    
    async def get_intervention_alerts(
        self,
        parent_id: str,
        student_id: Optional[str] = None,
        alert_type: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[InterventionAlert]:
        """Get intervention alerts with optional filters."""
        try:
            collection = self.collections["intervention_alerts"]
            
            # Build query
            query = collection.where("parent_id", "==", parent_id)
            if student_id:
                query = query.where("student_id", "==", student_id)
            if alert_type:
                query = query.where("alert_type", "==", alert_type)
            if severity:
                query = query.where("severity", "==", severity)
            if status:
                query = query.where("status", "==", status)
            if start_date:
                query = query.where("created_at", ">=", start_date)
            if end_date:
                query = query.where("created_at", "<=", end_date)
            
            # Execute query
            query = query.order_by("created_at", direction=firestore.Query.DESCENDING)
            docs = list(query.limit(limit).stream())
            
            # Convert to InterventionAlert objects
            alerts = []
            for doc in docs:
                result = doc.to_dict()
                result["document_id"] = doc.id
                alerts.append(InterventionAlert(**result))
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to get intervention alerts: {e}")
            raise
    
    async def update_intervention_alert_status(
        self,
        alert_id: str,
        status: str,
        resolved_by: Optional[str] = None,
        resolution_notes: Optional[str] = None
    ) -> bool:
        """Update intervention alert status."""
        try:
            collection = self.collections["intervention_alerts"]
            
            # Build update document
            update_doc = {"status": status}
            
            if status == "acknowledged":
                update_doc["acknowledged_at"] = datetime.utcnow()
            elif status == "resolved":
                update_doc["resolved_at"] = datetime.utcnow()
                if resolved_by:
                    update_doc["resolved_by"] = resolved_by
                if resolution_notes:
                    update_doc["resolution_notes"] = resolution_notes
            
            # Update alert
            doc_ref = collection.document(alert_id)
            await doc_ref.update(update_doc)
            
            logger.info(f"Updated intervention alert status: {alert_id} -> {status}")
            return True
            
        except GoogleAPICallError as e:
            if "NOT_FOUND" in str(e):
                logger.warning(f"Intervention alert not found for update: {alert_id}")
                return False
            else:
                logger.error(f"Failed to update intervention alert status: {e}")
                raise
        except Exception as e:
            logger.error(f"Failed to update intervention alert status: {e}")
            raise
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    async def get_dashboard_stats(self, parent_id: str, student_id: Optional[str] = None) -> Dict[str, Any]:
        """Get dashboard statistics for a parent."""
        try:
            # Get recent insights
            insights_collection = self.collections["parent_insights"]
            insights_query = insights_collection.where("parent_id", "==", parent_id)
            if student_id:
                insights_query = insights_query.where("student_id", "==", student_id)
            
            recent_insights = list(insights_query.order_by("created_at", direction=firestore.Query.DESCENDING).limit(5).stream())
            recent_insights = [doc.to_dict() for doc in recent_insights]
            
            # Get active alerts
            alerts_collection = self.collections["intervention_alerts"]
            alerts_query = alerts_collection.where("parent_id", "==", parent_id)\
                                     .where("status", "in", ["new", "acknowledged", "in_progress"])
            if student_id:
                alerts_query = alerts_query.where("student_id", "==", student_id)
            
            active_alerts = list(alerts_query.order_by("created_at", direction=firestore.Query.DESCENDING).limit(5).stream())
            active_alerts = [doc.to_dict() for doc in active_alerts]
            
            # Get recent communications
            comm_collection = self.collections["communication_history"]
            comm_query = comm_collection.where("parent_id", "==", parent_id)
            if student_id:
                comm_query = comm_query.where("student_id", "==", student_id)
            
            recent_communications = list(comm_query.order_by("created_at", direction=firestore.Query.DESCENDING).limit(5).stream())
            recent_communications = [doc.to_dict() for doc in recent_communications]
            
            return {
                "recent_insights": recent_insights,
                "active_alerts": active_alerts,
                "recent_communications": recent_communications,
                "insights_count": len(recent_insights),
                "alerts_count": len(active_alerts),
                "communications_count": len(recent_communications)
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard stats: {e}")
            raise
    
    async def cleanup_old_data(self, days_to_keep: int = 90) -> Dict[str, int]:
        """Clean up old data from collections."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            deleted_counts = {}
            
            # Clean up old AI interactions (keep successful ones longer)
            ai_collection = self.collections["ai_interactions"]
            ai_query = ai_collection.where("created_at", "<", cutoff_date)\
                                 .where("status", "!=", "completed")
            ai_docs = list(ai_query.stream())
            for doc in ai_docs:
                await doc.reference.delete()
            deleted_counts["ai_interactions"] = len(ai_docs)
            
            # Clean up old communication records
            comm_collection = self.collections["communication_history"]
            comm_query = comm_collection.where("created_at", "<", cutoff_date)
            comm_docs = list(comm_query.stream())
            for doc in comm_docs:
                await doc.reference.delete()
            deleted_counts["communication_history"] = len(comm_docs)
            
            # Clean up resolved intervention alerts
            alerts_collection = self.collections["intervention_alerts"]
            alerts_query = alerts_collection.where("created_at", "<", cutoff_date)\
                                      .where("status", "==", "resolved")
            alerts_docs = list(alerts_query.stream())
            for doc in alerts_docs:
                await doc.reference.delete()
            deleted_counts["intervention_alerts"] = len(alerts_docs)
            
            logger.info(f"Cleaned up old data: {deleted_counts}")
            return deleted_counts
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            raise
    
    # ============================================================================
    # PHASE 2 PARENT AI FEATURES METHODS
    # ============================================================================
    
    # Prediction Results Methods
    async def save_prediction_result(self, prediction: PredictionResult) -> str:
        """Save a prediction result to Firestore."""
        try:
            collection = self.collections["prediction_results"]
            
            # Convert to dict
            prediction_dict = prediction.model_dump()
            
            # Insert prediction
            doc_ref = collection.document(prediction.prediction_id)
            await doc_ref.set(prediction_dict)
            
            logger.info(f"Saved prediction result: {prediction.prediction_id}")
            return prediction.prediction_id
            
        except Exception as e:
            logger.error(f"Failed to save prediction result: {e}")
            raise
    
    async def get_prediction_results(
        self,
        parent_id: str,
        student_id: Optional[str] = None,
        prediction_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[PredictionResult]:
        """Get prediction results with optional filters."""
        try:
            collection = self.collections["prediction_results"]
            
            # Build query
            query = collection.where("parent_id", "==", parent_id)
            if student_id:
                query = query.where("student_id", "==", student_id)
            if prediction_type:
                query = query.where("prediction_type", "==", prediction_type)
            if start_date:
                query = query.where("created_at", ">=", start_date)
            if end_date:
                query = query.where("created_at", "<=", end_date)
            
            # Execute query
            query = query.order_by("created_at", direction=firestore.Query.DESCENDING)
            docs = list(query.limit(limit).stream())
            
            # Convert to PredictionResult objects
            predictions = []
            for doc in docs:
                result = doc.to_dict()
                result["document_id"] = doc.id
                predictions.append(PredictionResult(**result))
            
            return predictions
            
        except Exception as e:
            logger.error(f"Failed to get prediction results: {e}")
            raise
    
    # Communication Suggestions Methods
    async def save_communication_suggestion(self, suggestion: CommunicationSuggestion) -> str:
        """Save a communication suggestion to Firestore."""
        try:
            collection = self.collections["communication_suggestions"]
            
            # Convert to dict
            suggestion_dict = suggestion.model_dump()
            
            # Insert suggestion
            doc_ref = collection.document(suggestion.suggestion_id)
            await doc_ref.set(suggestion_dict)
            
            logger.info(f"Saved communication suggestion: {suggestion.suggestion_id}")
            return suggestion.suggestion_id
            
        except Exception as e:
            logger.error(f"Failed to save communication suggestion: {e}")
            raise
    
    async def get_communication_suggestions(
        self,
        parent_id: str,
        student_id: Optional[str] = None,
        communication_type: Optional[str] = None,
        used: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[CommunicationSuggestion]:
        """Get communication suggestions with optional filters."""
        try:
            collection = self.collections["communication_suggestions"]
            
            # Build query
            query = collection.where("parent_id", "==", parent_id)
            if student_id:
                query = query.where("student_id", "==", student_id)
            if communication_type:
                query = query.where("communication_type", "==", communication_type)
            if used is not None:
                query = query.where("used", "==", used)
            if start_date:
                query = query.where("created_at", ">=", start_date)
            if end_date:
                query = query.where("created_at", "<=", end_date)
            
            # Execute query
            query = query.order_by("created_at", direction=firestore.Query.DESCENDING)
            docs = list(query.limit(limit).stream())
            
            # Convert to CommunicationSuggestion objects
            suggestions = []
            for doc in docs:
                result = doc.to_dict()
                result["document_id"] = doc.id
                suggestions.append(CommunicationSuggestion(**result))
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to get communication suggestions: {e}")
            raise
    
    async def update_communication_suggestion_usage(
        self,
        suggestion_id: str,
        used: bool,
        feedback: Optional[str] = None,
        effectiveness_score: Optional[float] = None
    ) -> bool:
        """Update communication suggestion usage and feedback."""
        try:
            collection = self.collections["communication_suggestions"]
            
            # Build update document
            update_doc = {"used": used}
            if used:
                update_doc["used_at"] = datetime.utcnow()
            
            if feedback is not None:
                update_doc["feedback"] = feedback
            if effectiveness_score is not None:
                update_doc["effectiveness_score"] = effectiveness_score
            
            # Update suggestion
            doc_ref = collection.document(suggestion_id)
            await doc_ref.update(update_doc)
            
            logger.info(f"Updated communication suggestion usage: {suggestion_id}")
            return True
            
        except GoogleAPICallError as e:
            if "NOT_FOUND" in str(e):
                logger.warning(f"Communication suggestion not found for update: {suggestion_id}")
                return False
            else:
                logger.error(f"Failed to update communication suggestion usage: {e}")
                raise
        except Exception as e:
            logger.error(f"Failed to update communication suggestion usage: {e}")
            raise
    
    # Engagement Challenges Methods
    async def save_engagement_challenge(self, challenge: EngagementChallenge) -> str:
        """Save an engagement challenge to Firestore."""
        try:
            collection = self.collections["engagement_challenges"]
            
            # Convert to dict
            challenge_dict = challenge.model_dump()
            
            # Insert challenge
            doc_ref = collection.document(challenge.challenge_id)
            await doc_ref.set(challenge_dict)
            
            logger.info(f"Saved engagement challenge: {challenge.challenge_id}")
            return challenge.challenge_id
            
        except Exception as e:
            logger.error(f"Failed to save engagement challenge: {e}")
            raise
    
    async def get_engagement_challenges(
        self,
        parent_id: str,
        student_id: Optional[str] = None,
        challenge_type: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[EngagementChallenge]:
        """Get engagement challenges with optional filters."""
        try:
            collection = self.collections["engagement_challenges"]
            
            # Build query
            query = collection.where("parent_id", "==", parent_id)
            if student_id:
                query = query.where("student_id", "==", student_id)
            if challenge_type:
                query = query.where("challenge_type", "==", challenge_type)
            if status:
                query = query.where("status", "==", status)
            if start_date:
                query = query.where("created_at", ">=", start_date)
            if end_date:
                query = query.where("created_at", "<=", end_date)
            
            # Execute query
            query = query.order_by("created_at", direction=firestore.Query.DESCENDING)
            docs = list(query.limit(limit).stream())
            
            # Convert to EngagementChallenge objects
            challenges = []
            for doc in docs:
                result = doc.to_dict()
                result["document_id"] = doc.id
                challenges.append(EngagementChallenge(**result))
            
            return challenges
            
        except Exception as e:
            logger.error(f"Failed to get engagement challenges: {e}")
            raise
    
    async def update_engagement_challenge_progress(
        self,
        challenge_id: str,
        current_progress: Dict[str, Any],
        status: Optional[str] = None
    ) -> bool:
        """Update engagement challenge progress and status."""
        try:
            collection = self.collections["engagement_challenges"]
            
            # Build update document
            update_doc = {"current_progress": current_progress}
            if status:
                update_doc["status"] = status
                if status == "completed":
                    update_doc["completed_at"] = datetime.utcnow()
            
            # Update challenge
            doc_ref = collection.document(challenge_id)
            await doc_ref.update(update_doc)
            
            logger.info(f"Updated engagement challenge progress: {challenge_id}")
            return True
            
        except GoogleAPICallError as e:
            if "NOT_FOUND" in str(e):
                logger.warning(f"Engagement challenge not found for update: {challenge_id}")
                return False
            else:
                logger.error(f"Failed to update engagement challenge progress: {e}")
                raise
        except Exception as e:
            logger.error(f"Failed to update engagement challenge progress: {e}")
            raise
    
    # Achievements Methods
    async def save_achievement(self, achievement: Achievement) -> str:
        """Save an achievement to Firestore."""
        try:
            collection = self.collections["achievements"]
            
            # Convert to dict
            achievement_dict = achievement.model_dump()
            
            # Insert achievement
            doc_ref = collection.document(achievement.achievement_id)
            await doc_ref.set(achievement_dict)
            
            logger.info(f"Saved achievement: {achievement.achievement_id}")
            return achievement.achievement_id
            
        except Exception as e:
            logger.error(f"Failed to save achievement: {e}")
            raise
    
    async def get_achievements(
        self,
        parent_id: str,
        student_id: Optional[str] = None,
        achievement_type: Optional[str] = None,
        rarity: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Achievement]:
        """Get achievements with optional filters."""
        try:
            collection = self.collections["achievements"]
            
            # Build query
            query = collection.where("parent_id", "==", parent_id)
            if student_id:
                query = query.where("student_id", "==", student_id)
            if achievement_type:
                query = query.where("achievement_type", "==", achievement_type)
            if rarity:
                query = query.where("rarity", "==", rarity)
            if start_date:
                query = query.where("earned_at", ">=", start_date)
            if end_date:
                query = query.where("earned_at", "<=", end_date)
            
            # Execute query
            query = query.order_by("earned_at", direction=firestore.Query.DESCENDING)
            docs = list(query.limit(limit).stream())
            
            # Convert to Achievement objects
            achievements = []
            for doc in docs:
                result = doc.to_dict()
                result["document_id"] = doc.id
                achievements.append(Achievement(**result))
            
            return achievements
            
        except Exception as e:
            logger.error(f"Failed to get achievements: {e}")
            raise
    
    # Parent Resources Methods
    async def save_parent_resource(self, resource: ParentResource) -> str:
        """Save a parent resource to Firestore."""
        try:
            collection = self.collections["parent_resources"]
            
            # Convert to dict
            resource_dict = resource.model_dump()
            
            # Insert resource
            doc_ref = collection.document(resource.resource_id)
            await doc_ref.set(resource_dict)
            
            logger.info(f"Saved parent resource: {resource.resource_id}")
            return resource.resource_id
            
        except Exception as e:
            logger.error(f"Failed to save parent resource: {e}")
            raise
    
    async def get_parent_resources(
        self,
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
        difficulty_level: Optional[str] = None,
        language: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_quality_score: Optional[float] = None,
        limit: int = 100
    ) -> List[ParentResource]:
        """Get parent resources with optional filters."""
        try:
            collection = self.collections["parent_resources"]
            
            # Build query
            query = collection
            if category:
                query = query.where("category", "==", category)
            if resource_type:
                query = query.where("resource_type", "==", resource_type)
            if difficulty_level:
                query = query.where("difficulty_level", "==", difficulty_level)
            if language:
                query = query.where("language", "==", language)
            if min_quality_score:
                query = query.where("quality_score", ">=", min_quality_score)
            
            # Execute query
            query = query.order_by("quality_score", direction=firestore.Query.DESCENDING)
            docs = list(query.limit(limit).stream())
            
            # Filter by tags if provided (client-side filtering)
            resources = []
            for doc in docs:
                result = doc.to_dict()
                result["document_id"] = doc.id
                
                # Tag filtering
                if tags:
                    resource_tags = set(result.get("tags", []))
                    tag_filter = set(tags)
                    if not resource_tags.intersection(tag_filter):
                        continue
                
                resources.append(ParentResource(**result))
            
            return resources
            
        except Exception as e:
            logger.error(f"Failed to get parent resources: {e}")
            raise
    
    async def update_resource_usage(
        self,
        resource_id: str,
        usage_type: str,
        increment: int = 1
    ) -> bool:
        """Update resource usage statistics."""
        try:
            collection = self.collections["parent_resources"]
            
            # Get current resource
            doc_ref = collection.document(resource_id)
            doc = await doc_ref.get()
            
            if not doc.exists:
                logger.warning(f"Resource not found for usage update: {resource_id}")
                return False
            
            # Update usage count based on type
            update_doc = {}
            if usage_type == "viewed":
                update_doc["usage_count"] = firestore.Increment(increment)
            elif usage_type == "downloaded":
                update_doc["download_count"] = firestore.Increment(increment)
            
            update_doc["last_updated"] = datetime.utcnow()
            
            # Update resource
            await doc_ref.update(update_doc)
            
            logger.info(f"Updated resource usage: {resource_id} -> {usage_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update resource usage: {e}")
            raise
    
    # Resource Usage Methods
    async def save_resource_usage(self, usage: ResourceUsage) -> str:
        """Save a resource usage record to Firestore."""
        try:
            collection = self.collections["resource_usage"]
            
            # Convert to dict
            usage_dict = usage.model_dump()
            
            # Insert usage
            doc_ref = collection.document(usage.usage_id)
            await doc_ref.set(usage_dict)
            
            logger.info(f"Saved resource usage: {usage.usage_id}")
            return usage.usage_id
            
        except Exception as e:
            logger.error(f"Failed to save resource usage: {e}")
            raise
    
    async def get_resource_usage(
        self,
        parent_id: str,
        resource_id: Optional[str] = None,
        usage_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[ResourceUsage]:
        """Get resource usage records with optional filters."""
        try:
            collection = self.collections["resource_usage"]
            
            # Build query
            query = collection.where("parent_id", "==", parent_id)
            if resource_id:
                query = query.where("resource_id", "==", resource_id)
            if usage_type:
                query = query.where("usage_type", "==", usage_type)
            if start_date:
                query = query.where("created_at", ">=", start_date)
            if end_date:
                query = query.where("created_at", "<=", end_date)
            
            # Execute query
            query = query.order_by("created_at", direction=firestore.Query.DESCENDING)
            docs = list(query.limit(limit).stream())
            
            # Convert to ResourceUsage objects
            usage_records = []
            for doc in docs:
                result = doc.to_dict()
                result["document_id"] = doc.id
                usage_records.append(ResourceUsage(**result))
            
            return usage_records
            
        except Exception as e:
            logger.error(f"Failed to get resource usage: {e}")
            raise


# Global database service instance
database_service = DatabaseService()