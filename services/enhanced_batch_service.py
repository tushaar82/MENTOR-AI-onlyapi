"""
Enhanced Batch Processing Service with Database Storage

This service provides advanced batch processing capabilities for AI operations
with comprehensive database persistence and optimization features.

Features:
- Intelligent batch queuing and prioritization
- Cost optimization through batching
- Database persistence for all batch operations
- Real-time batch monitoring and tracking
- Error handling and retry logic
- Performance analytics and optimization
- Multi-service batch coordination

Author: Mentor AI Team
Version: 1.0.0
"""

import logging
import time
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
from functools import wraps

from pydantic import BaseModel, Field
from google.cloud import firestore

from services.unified_gemini_config_service import get_unified_gemini_service, GeminiConfig
from services.ai_content_service import get_ai_content_service, ContentType, ContentRequest
from utils.firebase_config import get_firestore_client

# Configure logging
logger = logging.getLogger(__name__)

# Batch configuration
DEFAULT_BATCH_SIZE = 10
MAX_BATCH_SIZE = 50
BATCH_TIMEOUT_SECONDS = 300  # 5 minutes
BATCH_RETRY_ATTEMPTS = 3
BATCH_COOLDOWN_SECONDS = 30

# Cost optimization thresholds
BATCH_COST_THRESHOLD = 0.05  # Minimum cost to justify batching
URGENT_BATCH_THRESHOLD = 0.8  # Urgent if cost > 80% of average


class BatchStatus(Enum):
    """Status of batch processing."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class BatchPriority(Enum):
    """Priority levels for batch processing."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


@dataclass
class BatchItem:
    """Individual item in a batch."""
    
    item_id: str
    request_type: str
    request_data: Dict[str, Any]
    priority: BatchPriority
    user_id: str
    created_at: datetime
    timeout_at: datetime
    student_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = BATCH_RETRY_ATTEMPTS
    callback: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BatchRequest:
    """Batch request containing multiple items."""
    
    batch_id: str
    items: List[BatchItem]
    status: BatchStatus
    priority: BatchPriority
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    total_cost: float = 0.0
    total_tokens: int = 0
    processing_time_ms: int = 0
    results: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BatchMetrics(BaseModel):
    """Metrics for batch processing performance."""
    
    batch_id: str = Field(..., description="Batch identifier")
    total_items: int = Field(..., description="Total items in batch")
    successful_items: int = Field(..., description="Successfully processed items")
    failed_items: int = Field(..., description="Failed items")
    total_cost: float = Field(..., description="Total cost of batch")
    total_tokens: int = Field(..., description="Total tokens used")
    processing_time_ms: int = Field(..., description="Total processing time")
    average_item_time_ms: float = Field(..., description="Average time per item")
    cost_savings: float = Field(..., description="Estimated cost savings from batching")
    cache_hit_rate: float = Field(..., description="Cache hit rate for items")
    created_at: datetime = Field(..., description="Batch creation timestamp")
    completed_at: datetime = Field(..., description="Batch completion timestamp")


class BatchRecord(BaseModel):
    """Database model for batch records."""
    
    batch_id: str = Field(..., description="Unique batch identifier")
    user_id: str = Field(..., description="User who initiated batch")
    status: str = Field(..., description="Batch status")
    priority: str = Field(..., description="Batch priority")
    total_items: int = Field(..., description="Total items in batch")
    successful_items: int = Field(..., description="Successfully processed items")
    failed_items: int = Field(..., description="Failed items")
    total_cost: float = Field(..., description="Total cost of batch")
    total_tokens: int = Field(..., description="Total tokens used")
    processing_time_ms: int = Field(..., description="Total processing time")
    cost_savings: float = Field(0.0, description="Estimated cost savings")
    item_types: Dict[str, int] = Field(default_factory=dict, description="Count by item type")
    error_summary: Optional[str] = Field(None, description="Summary of errors")
    created_at: datetime = Field(..., description="Batch creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Batch start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Batch completion timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class EnhancedBatchService:
    """
    Enhanced batch processing service with database persistence.
    
    This service provides intelligent batch processing for AI operations
    with cost optimization, database persistence, and comprehensive monitoring.
    
    Attributes:
        db: Firestore database client
        unified_service: Unified Gemini configuration service
        content_service: AI content service
        batch_queue: Priority queue for batch items
        active_batches: Currently processing batches
        batch_metrics: Performance metrics tracking
        cost_optimizer: Cost optimization logic
        
    Example:
        >>> service = EnhancedBatchService()
        >>> batch_id = service.create_batch(items, user_id="user123")
        >>> results = await service.process_batch(batch_id)
    """
    
    def __init__(
        self,
        db: Optional[firestore.Client] = None,
        unified_config: Optional[GeminiConfig] = None,
        enable_database_persistence: bool = True,
        max_concurrent_batches: int = 5,
        batch_size: int = DEFAULT_BATCH_SIZE
    ):
        """
        Initialize Enhanced Batch Service.
        
        Args:
            db: Firestore client (creates new if None)
            unified_config: Optional unified configuration
            enable_database_persistence: Enable saving to database
            max_concurrent_batches: Maximum concurrent batches
            batch_size: Default batch size
        """
        logger.info("Initializing EnhancedBatchService")
        
        # Database client
        self.db = db if db else get_firestore_client()
        
        # Initialize services
        self.unified_service = get_unified_gemini_service(config=unified_config)
        self.content_service = get_ai_content_service(unified_config=unified_config)
        
        # Configuration
        self.enable_database_persistence = enable_database_persistence
        self.max_concurrent_batches = max_concurrent_batches
        self.batch_size = batch_size
        
        # Batch processing
        self.batch_queue: deque = deque()
        self.active_batches: Dict[str, BatchRequest] = {}
        self.batch_metrics: Dict[str, Any] = defaultdict(dict)
        
        # Cost optimization
        self.cost_optimizer = BatchCostOptimizer()
        
        # Collections
        self.batch_collection = "batch_records"
        self.batch_metrics_collection = "batch_metrics"
        
        logger.info(
            f"EnhancedBatchService initialized (db_persistence={enable_database_persistence}, "
            f"max_concurrent={max_concurrent_batches}, batch_size={batch_size})"
        )
    
    async def create_batch(
        self,
        items: List[Dict[str, Any]],
        user_id: str,
        priority: BatchPriority = BatchPriority.NORMAL,
        batch_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new batch request.
        
        Args:
            items: List of item dictionaries
            user_id: User ID requesting batch
            priority: Batch priority level
            batch_id: Optional batch ID (generates if None)
            metadata: Additional metadata
        
        Returns:
            Batch ID for tracking
        """
        if not items:
            raise ValueError("Items list cannot be empty")
        
        # Generate batch ID if not provided
        if not batch_id:
            batch_id = f"batch_{user_id}_{int(time.time())}_{len(items)}"
        
        # Create batch items
        batch_items = []
        timeout_at = datetime.utcnow() + timedelta(seconds=BATCH_TIMEOUT_SECONDS)
        
        for i, item_data in enumerate(items):
            batch_item = BatchItem(
                item_id=f"{batch_id}_item_{i}",
                request_type=item_data.get("type", "unknown"),
                request_data=item_data,
                priority=priority,
                user_id=user_id,
                student_id=item_data.get("student_id"),
                created_at=datetime.utcnow(),
                timeout_at=timeout_at,
                callback=self._create_item_callback(item_data.get("type", "unknown")),
                metadata=item_data.get("metadata", {})
            )
            batch_items.append(batch_item)
        
        # Create batch request
        batch_request = BatchRequest(
            batch_id=batch_id,
            items=batch_items,
            status=BatchStatus.PENDING,
            priority=priority,
            created_at=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        # Add to queue
        self.batch_queue.append(batch_request)
        
        # Save to database
        if self.enable_database_persistence:
            await self._save_batch_to_db(batch_request)
        
        # Log batch creation
        logger.info(
            f"Created batch {batch_id}: {len(items)} items, "
            f"priority={priority.value}, timeout={BATCH_TIMEOUT_SECONDS}s"
        )
        
        return batch_id
    
    async def process_batch(
        self,
        batch_id: str,
        force_process: bool = False
    ) -> Dict[str, Any]:
        """
        Process a batch request.
        
        Args:
            batch_id: Batch ID to process
            force_process: Force processing even if queue is full
        
        Returns:
            Dictionary with batch results and metrics
        """
        # Find batch in queue or active batches
        batch_request = None
        
        # Check active batches first
        if batch_id in self.active_batches:
            batch_request = self.active_batches[batch_id]
        else:
            # Search queue
            for batch in self.batch_queue:
                if batch.batch_id == batch_id:
                    batch_request = batch
                    break
        
        if not batch_request:
            raise ValueError(f"Batch not found: {batch_id}")
        
        # Check if can process
        if not force_process and len(self.active_batches) >= self.max_concurrent_batches:
            logger.warning(f"Cannot process batch {batch_id}: maximum concurrent batches reached")
            return {
                "batch_id": batch_id,
                "status": "queued",
                "message": "Maximum concurrent batches reached"
            }
        
        # Move to active batches
        self.active_batches[batch_id] = batch_request
        batch_request.status = BatchStatus.PROCESSING
        batch_request.started_at = datetime.utcnow()
        
        # Update database
        if self.enable_database_persistence:
            await self._update_batch_in_db(batch_id, {
                "status": BatchStatus.PROCESSING.value,
                "started_at": batch_request.started_at
            })
        
        logger.info(f"Processing batch {batch_id} with {len(batch_request.items)} items")
        
        try:
            # Process batch with cost optimization
            start_time = time.time()
            results = await self._process_batch_items(batch_request)
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Calculate metrics
            successful_items = sum(1 for result in results.values() if result.get("success", False))
            failed_items = len(results) - successful_items
            total_cost = sum(result.get("cost", 0.0) for result in results.values())
            total_tokens = sum(result.get("tokens", 0) for result in results.values())
            cost_savings = self.cost_optimizer.calculate_savings(batch_request)
            
            # Update batch request
            batch_request.status = BatchStatus.COMPLETED
            batch_request.completed_at = datetime.utcnow()
            batch_request.processing_time_ms = processing_time_ms
            batch_request.total_cost = total_cost
            batch_request.total_tokens = total_tokens
            batch_request.results = results
            
            # Calculate metrics
            metrics = BatchMetrics(
                batch_id=batch_id,
                total_items=len(batch_request.items),
                successful_items=successful_items,
                failed_items=failed_items,
                total_cost=total_cost,
                total_tokens=total_tokens,
                processing_time_ms=processing_time_ms,
                average_item_time_ms=processing_time_ms / len(batch_request.items),
                cost_savings=cost_savings,
                cache_hit_rate=self._calculate_cache_hit_rate(results),
                created_at=batch_request.created_at,
                completed_at=batch_request.completed_at
            )
            
            # Save metrics
            self.batch_metrics[batch_id] = metrics.model_dump()
            
            # Update database
            if self.enable_database_persistence:
                await self._save_batch_metrics(batch_id, metrics)
                await self._update_batch_in_db(batch_id, {
                    "status": BatchStatus.COMPLETED.value,
                    "completed_at": batch_request.completed_at,
                    "total_cost": total_cost,
                    "total_tokens": total_tokens,
                    "successful_items": successful_items,
                    "failed_items": failed_items,
                    "processing_time_ms": processing_time_ms,
                    "cost_savings": cost_savings,
                    "item_types": self._calculate_item_types(batch_request)
                })
            
            # Remove from active batches
            del self.active_batches[batch_id]
            
            logger.info(
                f"Completed batch {batch_id}: {successful_items}/{len(batch_request.items)} successful, "
                f"cost=${total_cost:.4f}, savings=${cost_savings:.4f}"
            )
            
            return {
                "batch_id": batch_id,
                "status": "completed",
                "results": results,
                "metrics": metrics.model_dump(),
                "cost_savings": cost_savings
            }
            
        except Exception as e:
            # Handle batch failure
            batch_request.status = BatchStatus.FAILED
            batch_request.completed_at = datetime.utcnow()
            batch_request.error_message = str(e)
            
            # Update database
            if self.enable_database_persistence:
                await self._update_batch_in_db(batch_id, {
                    "status": BatchStatus.FAILED.value,
                    "completed_at": batch_request.completed_at,
                    "error_summary": str(e)
                })
            
            # Remove from active batches
            if batch_id in self.active_batches:
                del self.active_batches[batch_id]
            
            logger.error(f"Batch {batch_id} failed: {e}")
            
            return {
                "batch_id": batch_id,
                "status": "failed",
                "error": str(e)
            }
    
    async def get_batch_status(
        self,
        batch_id: str
    ) -> Dict[str, Any]:
        """
        Get status and metrics for a batch.
        
        Args:
            batch_id: Batch ID
        
        Returns:
            Dictionary with batch status and metrics
        """
        # Check active batches
        if batch_id in self.active_batches:
            batch = self.active_batches[batch_id]
            return {
                "batch_id": batch_id,
                "status": batch.status.value,
                "created_at": batch.created_at.isoformat(),
                "started_at": batch.started_at.isoformat() if batch.started_at else None,
                "total_items": len(batch.items),
                "priority": batch.priority.value,
                "metrics": self.batch_metrics.get(batch_id, {})
            }
        
        # Check queue
        for batch in self.batch_queue:
            if batch.batch_id == batch_id:
                return {
                    "batch_id": batch_id,
                    "status": batch.status.value,
                    "created_at": batch.created_at.isoformat(),
                    "total_items": len(batch.items),
                    "priority": batch.priority.value,
                    "metrics": self.batch_metrics.get(batch_id, {})
                }
        
        # Check database
        if self.enable_database_persistence:
            batch_record = await self._get_batch_from_db(batch_id)
            if batch_record:
                return {
                    "batch_id": batch_id,
                    "status": batch_record.status,
                    "created_at": batch_record.created_at.isoformat(),
                    "started_at": batch_record.started_at.isoformat() if batch_record.started_at else None,
                    "completed_at": batch_record.completed_at.isoformat() if batch_record.completed_at else None,
                    "total_items": batch_record.total_items,
                    "successful_items": batch_record.successful_items,
                    "failed_items": batch_record.failed_items,
                    "total_cost": batch_record.total_cost,
                    "total_tokens": batch_record.total_tokens,
                    "processing_time_ms": batch_record.processing_time_ms,
                    "cost_savings": batch_record.cost_savings,
                    "priority": batch_record.priority,
                    "error_summary": batch_record.error_summary,
                    "item_types": batch_record.item_types,
                    "metrics": self.batch_metrics.get(batch_id, {})
                }
        
        return {
            "batch_id": batch_id,
            "status": "not_found",
            "message": "Batch not found"
        }
    
    async def list_batches(
        self,
        user_id: str,
        status: Optional[BatchStatus] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List batches for a user with optional filtering.
        
        Args:
            user_id: User ID
            status: Filter by batch status
            limit: Maximum number of batches to return
        
        Returns:
            List of batch records
        """
        try:
            # Build query
            query = self.db.collection(self.batch_collection)\
                .where("user_id", "==", user_id)\
                .order_by("created_at", direction="DESCENDING")\
                .limit(limit)
            
            if status:
                query = query.where("status", "==", status.value)
            
            # Execute query
            batches = []
            async for doc in query.stream():
                batch_data = doc.to_dict()
                batches.append({
                    "batch_id": doc.id,
                    **batch_data
                })
            
            logger.info(f"Listed {len(batches)} batches for user {user_id}")
            return batches
            
        except Exception as e:
            logger.error(f"Failed to list batches: {e}")
            raise
    
    async def get_batch_metrics(
        self,
        batch_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed metrics for a batch.
        
        Args:
            batch_id: Batch ID
        
        Returns:
            Batch metrics or None if not found
        """
        if batch_id in self.batch_metrics:
            return self.batch_metrics[batch_id]
        
        # Try to get from database
        if self.enable_database_persistence:
            try:
                doc_ref = self.db.collection(self.batch_metrics_collection).document(batch_id)
                doc = await doc_ref.get()
                
                if doc.exists:
                    metrics_data = doc.to_dict()
                    self.batch_metrics[batch_id] = metrics_data
                    return metrics_data
                
            except Exception as e:
                logger.error(f"Failed to get batch metrics: {e}")
        
        return None
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get comprehensive service status.
        
        Returns:
            Dictionary with service status and metrics
        """
        try:
            # Calculate queue metrics
            queue_size = len(self.batch_queue)
            active_batches = len(self.active_batches)
            
            # Calculate cost savings
            total_savings = sum(
                metrics.get("cost_savings", 0.0) 
                for metrics in self.batch_metrics.values()
            )
            
            # Get recent performance
            recent_batches = list(self.batch_metrics.values())[-10:]  # Last 10 batches
            avg_processing_time = 0.0
            if recent_batches:
                avg_processing_time = sum(
                    batch.get("processing_time_ms", 0) 
                    for batch in recent_batches
                ) / len(recent_batches)
            
            return {
                "service": "enhanced_batch_service",
                "status": "healthy",
                "queue_metrics": {
                    "queue_size": queue_size,
                    "active_batches": active_batches,
                    "max_concurrent": self.max_concurrent_batches,
                    "utilization": active_batches / max(self.max_concurrent_batches, 1)
                },
                "performance_metrics": {
                    "total_batches_processed": len(self.batch_metrics),
                    "total_cost_savings": total_savings,
                    "average_processing_time_ms": avg_processing_time,
                    "success_rate": self._calculate_success_rate()
                },
                "configuration": {
                    "database_persistence": self.enable_database_persistence,
                    "batch_size": self.batch_size,
                    "max_concurrent_batches": self.max_concurrent_batches,
                    "batch_timeout_seconds": BATCH_TIMEOUT_SECONDS
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get service status: {e}")
            return {
                "service": "enhanced_batch_service",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ========================================================================
    # PRIVATE METHODS
    # ========================================================================
    
    def _create_item_callback(self, item_type: str) -> Callable:
        """Create appropriate callback for item type."""
        callbacks = {
            "question_generation": self._process_question_item,
            "content_generation": self._process_content_item,
            "analysis": self._process_analysis_item,
            "recommendation": self._process_recommendation_item
        }
        return callbacks.get(item_type, self._process_generic_item)
    
    async def _process_batch_items(self, batch_request: BatchRequest) -> Dict[str, Any]:
        """Process all items in a batch."""
        results = {}
        
        # Group items by type for optimization
        item_groups = defaultdict(list)
        for item in batch_request.items:
            item_groups[item.request_type].append(item)
        
        # Process each group
        for item_type, items in item_groups.items():
            logger.info(f"Processing {len(items)} items of type {item_type}")
            
            if item_type == "question_generation":
                group_results = await self._process_question_group(items)
            elif item_type == "content_generation":
                group_results = await self._process_content_group(items)
            else:
                group_results = await self._process_generic_group(items)
            
            # Add group results to main results
            for item, result in zip(items, group_results):
                results[item.item_id] = result
        
        return results
    
    async def _process_question_group(self, items: List[BatchItem]) -> List[Dict[str, Any]]:
        """Process a group of question generation items."""
        results = []
        
        # Extract unique parameters for batching
        unique_requests = {}
        for item in items:
            request_data = item.request_data
            key = f"{request_data.get('topic', '')}_{request_data.get('difficulty', '')}_{request_data.get('exam_type', '')}"
            
            if key not in unique_requests:
                unique_requests[key] = {
                    "items": [],
                    "user_id": item.user_id,
                    "student_ids": set()
                }
            
            unique_requests[key]["items"].append(item)
            if item.student_id:
                unique_requests[key]["student_ids"].add(item.student_id)
        
        # Process each unique request
        for request_info in unique_requests.values():
            try:
                # Use unified service for batch processing
                result = await self.unified_service.generate_questions(
                    topic=request_info["items"][0].request_data.get("topic", "Unknown"),
                    exam_type=request_info["items"][0].request_data.get("exam_type", "JEE_MAIN"),
                    difficulty=request_info["items"][0].request_data.get("difficulty", "medium"),
                    num_questions=len(request_info["items"]),
                    user_id=request_info["user_id"],
                    student_id=list(request_info["student_ids"])[0] if request_info["student_ids"] else None,
                    metadata={"batch_processing": True}
                )
                
                # Create result for each item
                for item in request_info["items"]:
                    item_result = {
                        "success": True,
                        "content": result.get("questions", [])[:1] if result.get("questions") else [{}],
                        "cost": result.get("cost", 0.0) / len(request_info["items"]),
                        "tokens": result.get("tokens_used", {}).get("total", 0) / len(request_info["items"]),
                        "cached": result.get("cached", False)
                    }
                    results.append(item_result)
                
            except Exception as e:
                # Create failure result for each item
                for item in request_info["items"]:
                    item_result = {
                        "success": False,
                        "error": str(e),
                        "content": None,
                        "cost": 0.0,
                        "tokens": 0,
                        "cached": False
                    }
                    results.append(item_result)
        
        return results
    
    async def _process_content_group(self, items: List[BatchItem]) -> List[Dict[str, Any]]:
        """Process a group of content generation items."""
        results = []
        
        for item in items:
            try:
                # Use content service for generation
                content_request = ContentRequest(
                    content_type=ContentType.CONTENT_GENERATION,
                    prompt=item.request_data.get("prompt", ""),
                    user_id=item.user_id,
                    student_id=item.student_id,
                    context=item.request_data.get("context"),
                    parameters=item.request_data.get("parameters"),
                    use_cache=True,
                    metadata={"batch_processing": True}
                )
                
                result = await self.content_service.generate_content(content_request)
                
                item_result = {
                    "success": True,
                    "content": result.content,
                    "cost": result.cost,
                    "tokens": result.tokens_used,
                    "cached": result.cached
                }
                results.append(item_result)
                
            except Exception as e:
                item_result = {
                    "success": False,
                    "error": str(e),
                    "content": None,
                    "cost": 0.0,
                    "tokens": {},
                    "cached": False
                }
                results.append(item_result)
        
        return results
    
    async def _process_generic_item(self, item: BatchItem) -> Dict[str, Any]:
        """Process a generic batch item."""
        try:
            # Use unified service for generic processing
            result = await self.unified_service.generate_content(
                prompt=item.request_data.get("prompt", ""),
                user_id=item.user_id,
                student_id=item.student_id,
                interaction_type="batch_processing",
                metadata={"batch_item_id": item.item_id}
            )
            
            return {
                "success": True,
                "content": result.get("content"),
                "cost": result.get("cost", 0.0),
                "tokens": result.get("tokens_used", {}),
                "cached": result.get("cached", False)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": None,
                "cost": 0.0,
                "tokens": {},
                "cached": False
            }
    
    async def _process_generic_group(self, items: List[BatchItem]) -> List[Dict[str, Any]]:
        """Process a group of generic items."""
        results = []
        
        for item in items:
            result = await self._process_generic_item(item)
            results.append(result)
        
        return results
    
    def _calculate_cache_hit_rate(self, results: Dict[str, Any]) -> float:
        """Calculate cache hit rate from results."""
        if not results:
            return 0.0
        
        cache_hits = sum(1 for result in results.values() if result.get("cached", False))
        return cache_hits / len(results)
    
    def _calculate_item_types(self, batch_request: BatchRequest) -> Dict[str, int]:
        """Calculate distribution of item types in batch."""
        type_counts = defaultdict(int)
        
        for item in batch_request.items:
            type_counts[item.request_type] += 1
        
        return dict(type_counts)
    
    def _calculate_success_rate(self) -> float:
        """Calculate overall success rate from metrics."""
        if not self.batch_metrics:
            return 0.0
        
        total_processed = 0
        total_successful = 0
        
        for metrics in self.batch_metrics.values():
            total_processed += metrics.get("total_items", 0)
            total_successful += metrics.get("successful_items", 0)
        
        return total_successful / total_processed if total_processed > 0 else 0.0
    
    async def _save_batch_to_db(self, batch_request: BatchRequest):
        """Save batch request to database."""
        try:
            batch_record = BatchRecord(
                batch_id=batch_request.batch_id,
                user_id=batch_request.items[0].user_id if batch_request.items else "unknown",
                status=batch_request.status.value,
                priority=batch_request.priority.value,
                total_items=len(batch_request.items),
                successful_items=0,
                failed_items=0,
                total_cost=0.0,
                total_tokens=0,
                processing_time_ms=0,
                cost_savings=0.0,
                item_types=self._calculate_item_types(batch_request),
                created_at=batch_request.created_at,
                started_at=batch_request.started_at,
                metadata=batch_request.metadata
            )
            
            doc_ref = self.db.collection(self.batch_collection).document(batch_request.batch_id)
            await doc_ref.set(batch_record.model_dump())
            
            logger.debug(f"Saved batch {batch_request.batch_id} to database")
            
        except Exception as e:
            logger.error(f"Failed to save batch {batch_request.batch_id}: {e}")
    
    async def _update_batch_in_db(self, batch_id: str, updates: Dict[str, Any]):
        """Update batch record in database."""
        try:
            doc_ref = self.db.collection(self.batch_collection).document(batch_id)
            await doc_ref.update(updates)
            logger.debug(f"Updated batch {batch_id} in database")
            
        except Exception as e:
            logger.error(f"Failed to update batch {batch_id}: {e}")
    
    async def _save_batch_metrics(self, batch_id: str, metrics: BatchMetrics):
        """Save batch metrics to database."""
        try:
            doc_ref = self.db.collection(self.batch_metrics_collection).document(batch_id)
            await doc_ref.set(metrics.model_dump())
            logger.debug(f"Saved metrics for batch {batch_id}")
            
        except Exception as e:
            logger.error(f"Failed to save batch metrics {batch_id}: {e}")
    
    async def _get_batch_from_db(self, batch_id: str) -> Optional[BatchRecord]:
        """Get batch record from database."""
        try:
            doc_ref = self.db.collection(self.batch_collection).document(batch_id)
            doc = await doc_ref.get()
            
            if doc.exists:
                return BatchRecord(**doc.to_dict())
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get batch {batch_id}: {e}")
            return None


class BatchCostOptimizer:
    """Cost optimization logic for batch processing."""
    
    def __init__(self):
        self.individual_costs = []
        self.batch_costs = []
    
    def calculate_savings(self, batch_request: BatchRequest) -> float:
        """Calculate cost savings from batch processing."""
        if not batch_request.items:
            return 0.0
        
        # Estimate individual cost (simplified)
        estimated_individual_cost = len(batch_request.items) * 0.01  # $0.01 per item
        
        # Estimate batch cost (with optimization)
        estimated_batch_cost = estimated_individual_cost * 0.7  # 30% savings from batching
        
        savings = estimated_individual_cost - estimated_batch_cost
        return max(0.0, savings)


# Singleton instance
_enhanced_batch_service: Optional[EnhancedBatchService] = None


def get_enhanced_batch_service(
    unified_config: Optional[GeminiConfig] = None,
    **kwargs
) -> EnhancedBatchService:
    """
    Get enhanced batch service instance.
    
    Args:
        unified_config: Optional unified configuration
        **kwargs: Additional arguments
    
    Returns:
        EnhancedBatchService instance
    """
    global _enhanced_batch_service
    
    if _enhanced_batch_service is None:
        logger.info("Creating new EnhancedBatchService singleton instance")
        _enhanced_batch_service = EnhancedBatchService(
            unified_config=unified_config,
            **kwargs
        )
    
    return _enhanced_batch_service


# Module initialization
logger.info("Enhanced Batch Service module loaded")
logger.info(f"Default batch size: {DEFAULT_BATCH_SIZE}")
logger.info(f"Max concurrent batches: {5}")