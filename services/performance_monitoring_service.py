"""
Performance Monitoring and Analytics Service

This service provides comprehensive performance monitoring, analytics collection,
and reporting for all parent AI features with real-time metrics,
performance optimization insights, and automated alerting.

Author: Mentor AI Team
Version: 1.0.0
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
import time
import psutil
import gc
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    timestamp: datetime
    service_name: str
    operation: str
    response_time_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float
    database_query_time_ms: Optional[float] = None
    ai_tokens_used: Optional[int] = None
    cache_hit: bool = False
    error_occurred: bool = False
    user_id: Optional[str] = None
    student_id: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemHealthMetrics:
    """System health monitoring metrics."""
    timestamp: datetime
    memory_usage_mb: float
    memory_available_mb: float
    cpu_usage_percent: float
    cpu_count: int
    disk_usage_percent: float
    network_io: Dict[str, float]
    active_connections: int
    gc_collections: int
    uptime_seconds: float


@dataclass
class AIPerformanceMetrics:
    """AI-specific performance metrics."""
    timestamp: datetime
    model_name: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    response_time_ms: float
    cost_usd: float
    cache_hit: bool
    error_type: Optional[str] = None
    confidence_score: Optional[float] = None


class PerformanceMonitoringService:
    """Comprehensive performance monitoring service."""
    
    def __init__(self, max_metrics_history: int = 10000):
        self.max_metrics_history = max_metrics_history
        self.metrics_history = deque(maxlen=max_metrics_history)
        self.real_time_metrics = defaultdict(list)
        self.performance_alerts = []
        self.baseline_metrics = {}
        self.optimization_suggestions = []
        self.start_time = datetime.utcnow()
        
        # Performance thresholds
        self.thresholds = {
            "response_time_ms": 3000,  # 3 seconds
            "memory_usage_percent": 80,
            "cpu_usage_percent": 75,
            "error_rate_percent": 5,
            "cache_hit_rate_percent": 70
        }
        
        # Aggregated metrics
        self.hourly_metrics = defaultdict(list)
        self.daily_metrics = defaultdict(list)
        self.service_metrics = defaultdict(lambda: {
            "total_requests": 0,
            "total_errors": 0,
            "total_response_time": 0.0,
            "avg_response_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0
        })
    
    async def record_performance_metric(self, metric: PerformanceMetrics):
        """Record a performance metric."""
        # Add to history
        self.metrics_history.append(metric)
        
        # Add to real-time metrics
        self.real_time_metrics[metric.service_name].append(metric)
        
        # Update service metrics
        service_stats = self.service_metrics[metric.service_name]
        service_stats["total_requests"] += 1
        service_stats["total_response_time"] += metric.response_time_ms
        service_stats["avg_response_time"] = service_stats["total_response_time"] / service_stats["total_requests"]
        
        if metric.cache_hit:
            service_stats["cache_hits"] += 1
        else:
            service_stats["cache_misses"] += 1
        
        if metric.error_occurred:
            service_stats["total_errors"] += 1
        
        # Check for performance alerts
        await self._check_performance_alerts(metric)
        
        # Log metric
        logger.info(f"Performance metric recorded: {metric.service_name}.{metric.operation} - {metric.response_time_ms}ms")
    
    async def record_ai_performance(self, metric: AIPerformanceMetrics):
        """Record AI-specific performance metrics."""
        # Add to history
        ai_metric = PerformanceMetrics(
            timestamp=metric.timestamp,
            service_name="ai_service",
            operation=f"ai_{metric.model_name}",
            response_time_ms=metric.response_time_ms,
            memory_usage_mb=0.0,  # Will be captured separately
            cpu_usage_percent=0.0,   # Will be captured separately
            ai_tokens_used=metric.total_tokens,
            cache_hit=metric.cache_hit,
            additional_data={
                "model_name": metric.model_name,
                "prompt_tokens": metric.prompt_tokens,
                "completion_tokens": metric.completion_tokens,
                "cost_usd": metric.cost_usd,
                "confidence_score": metric.confidence_score,
                "error_type": metric.error_type
            }
        )
        await self.record_performance_metric(ai_metric)
        
        # Log AI-specific metric
        logger.info(f"AI Performance: {metric.model_name} - {metric.total_tokens} tokens - ${metric.cost_usd:.4f}")
    
    async def get_system_health_metrics(self) -> SystemHealthMetrics:
        """Get current system health metrics."""
        # Memory usage
        memory = psutil.virtual_memory()
        memory_usage_mb = memory.used / (1024 * 1024)
        memory_available_mb = memory.available / (1024 * 1024)
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_usage_percent = disk.percent
        
        # Network I/O
        network = psutil.net_io_counters()
        network_io = {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv
        }
        
        # GC metrics
        gc_stats = gc.get_stats()
        gc_collections = gc_stats.get('count', 0)
        
        # Uptime
        uptime_seconds = (datetime.utcnow() - self.start_time).total_seconds()
        
        return SystemHealthMetrics(
            timestamp=datetime.utcnow(),
            memory_usage_mb=memory_usage_mb,
            memory_available_mb=memory_available_mb,
            cpu_usage_percent=cpu_percent,
            cpu_count=cpu_count,
            disk_usage_percent=disk_usage_percent,
            network_io=network_io,
            active_connections=len(self.real_time_metrics),
            gc_collections=gc_collections,
            uptime_seconds=uptime_seconds
        )
    
    async def _check_performance_alerts(self, metric: PerformanceMetrics):
        """Check if metric triggers any performance alerts."""
        alerts = []
        
        # Response time alert
        if metric.response_time_ms > self.thresholds["response_time_ms"]:
            alerts.append({
                "type": "response_time",
                "severity": "high" if metric.response_time_ms > self.thresholds["response_time_ms"] * 2 else "medium",
                "message": f"High response time detected: {metric.response_time_ms}ms (threshold: {self.thresholds['response_time_ms']}ms)",
                "service": metric.service_name,
                "operation": metric.operation,
                "timestamp": metric.timestamp
            })
        
        # Memory usage alert
        system_metrics = await self.get_system_health_metrics()
        if system_metrics.memory_usage_mb > (system_metrics.memory_available_mb + system_metrics.memory_usage_mb) * (self.thresholds["memory_usage_percent"] / 100):
            alerts.append({
                "type": "memory_usage",
                "severity": "high",
                "message": f"High memory usage: {system_metrics.memory_usage_mb:.1f}MB ({(system_metrics.memory_usage_mb/(system_metrics.memory_available_mb + system_metrics.memory_usage_mb)*100:.1f}%)",
                "timestamp": metric.timestamp
            })
        
        # CPU usage alert
        if system_metrics.cpu_usage_percent > self.thresholds["cpu_usage_percent"]:
            alerts.append({
                "type": "cpu_usage",
                "severity": "high" if system_metrics.cpu_usage_percent > 90 else "medium",
                "message": f"High CPU usage: {system_metrics.cpu_usage_percent:.1f}%",
                "timestamp": metric.timestamp
            })
        
        # Add to performance alerts
        self.performance_alerts.extend(alerts)
        
        # Keep only recent alerts
        if len(self.performance_alerts) > 1000:
            self.performance_alerts = self.performance_alerts[-1000:]
        
        # Log alerts
        for alert in alerts:
            logger.warning(f"Performance Alert: {alert['message']}")
    
    async def get_performance_summary(
        self,
        service_name: Optional[str] = None,
        period_minutes: int = 60,
        include_system_metrics: bool = True
    ) -> Dict[str, Any]:
        """Get performance summary for a specific period."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=period_minutes)
        
        # Filter metrics by time and service
        recent_metrics = [
            m for m in self.metrics_history
            if m.timestamp >= cutoff_time and (service_name is None or m.service_name == service_name)
        ]
        
        if not recent_metrics:
            return {"error": "No metrics found for the specified period"}
        
        # Calculate summary statistics
        response_times = [m.response_time_ms for m in recent_metrics]
        error_count = sum(1 for m in recent_metrics if m.error_occurred)
        cache_hits = sum(1 for m in recent_metrics if m.cache_hit)
        cache_misses = sum(1 for m in recent_metrics if not m.cache_hit)
        
        summary = {
            "period_minutes": period_minutes,
            "service_name": service_name,
            "total_requests": len(recent_metrics),
            "error_count": error_count,
            "error_rate_percent": (error_count / len(recent_metrics)) * 100,
            "avg_response_time_ms": sum(response_times) / len(response_times),
            "min_response_time_ms": min(response_times),
            "max_response_time_ms": max(response_times),
            "p95_response_time_ms": self._percentile(response_times, 95),
            "p99_response_time_ms": self._percentile(response_times, 99),
            "cache_hits": cache_hits,
            "cache_misses": cache_misses,
            "cache_hit_rate_percent": (cache_hits / (cache_hits + cache_misses)) * 100 if (cache_hits + cache_misses) > 0 else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add system metrics if requested
        if include_system_metrics:
            system_metrics = await self.get_system_health_metrics()
            summary["system_metrics"] = {
                "memory_usage_mb": system_metrics.memory_usage_mb,
                "cpu_usage_percent": system_metrics.cpu_usage_percent,
                "disk_usage_percent": system_metrics.disk_usage_percent,
                "uptime_seconds": system_metrics.uptime_seconds
            }
        
        return summary
    
    async def get_service_performance_comparison(
        self,
        service_names: List[str],
        period_minutes: int = 60
    ) -> Dict[str, Any]:
        """Compare performance across multiple services."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=period_minutes)
        
        comparison = {}
        for service_name in service_names:
            service_metrics = [
                m for m in self.metrics_history
                if m.service_name == service_name and m.timestamp >= cutoff_time
            ]
            
            if service_metrics:
                response_times = [m.response_time_ms for m in service_metrics]
                comparison[service_name] = {
                    "avg_response_time_ms": sum(response_times) / len(response_times),
                    "request_count": len(service_metrics),
                    "error_count": sum(1 for m in service_metrics if m.error_occurred),
                    "cache_hit_rate_percent": (sum(1 for m in service_metrics if m.cache_hit) / len(service_metrics)) * 100
                }
        
        # Add ranking
        if comparison:
            avg_times = {name: data["avg_response_time_ms"] for name, data in comparison.items()}
            sorted_services = sorted(avg_times.items(), key=lambda x: x[1])
            
            comparison["ranking"] = {
                name: rank + 1 for rank, (name, _) in enumerate(sorted_services)
            }
            comparison["best_service"] = sorted_services[0][0]
            comparison["worst_service"] = sorted_services[-1][0]
        
        return comparison
    
    async def get_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """Generate performance optimization suggestions."""
        suggestions = []
        
        # Analyze recent metrics
        recent_metrics = list(self.metrics_history)[-1000:]  # Last 1000 metrics
        
        if not recent_metrics:
            return suggestions
        
        # Response time optimization
        response_times = [m.response_time_ms for m in recent_metrics]
        avg_response_time = sum(response_times) / len(response_times)
        
        if avg_response_time > self.thresholds["response_time_ms"]:
            suggestions.append({
                "type": "response_time",
                "priority": "high",
                "title": "Optimize Response Time",
                "description": f"Average response time is {avg_response_time:.1f}ms, above threshold of {self.thresholds['response_time_ms']}ms",
                "suggestions": [
                    "Implement response caching",
                    "Optimize database queries",
                    "Add response time monitoring",
                    "Consider load balancing"
                ],
                "potential_improvement_percent": 30
            })
        
        # Cache optimization
        cache_hits = sum(1 for m in recent_metrics if m.cache_hit)
        cache_total = len(recent_metrics)
        cache_hit_rate = (cache_hits / cache_total) * 100 if cache_total > 0 else 0
        
        if cache_hit_rate < self.thresholds["cache_hit_rate_percent"]:
            suggestions.append({
                "type": "cache",
                "priority": "medium",
                "title": "Improve Cache Hit Rate",
                "description": f"Cache hit rate is {cache_hit_rate:.1f}%, below threshold of {self.thresholds['cache_hit_rate_percent']}%",
                "suggestions": [
                    "Increase cache TTL",
                    "Optimize cache key strategy",
                    "Implement cache warming",
                    "Review cache eviction policy"
                ],
                "potential_improvement_percent": 25
            })
        
        # Error rate optimization
        error_count = sum(1 for m in recent_metrics if m.error_occurred)
        error_rate = (error_count / len(recent_metrics)) * 100
        
        if error_rate > self.thresholds["error_rate_percent"]:
            suggestions.append({
                "type": "error_rate",
                "priority": "high",
                "title": "Reduce Error Rate",
                "description": f"Error rate is {error_rate:.1f}%, above threshold of {self.thresholds['error_rate_percent']}%",
                "suggestions": [
                    "Implement better error handling",
                    "Add input validation",
                    "Improve retry mechanisms",
                    "Add comprehensive logging"
                ],
                "potential_improvement_percent": 50
            })
        
        self.optimization_suggestions = suggestions
        return suggestions
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    async def export_metrics(
        self,
        format: str = "json",
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        service_name: Optional[str] = None
    ) -> Union[str, bytes]:
        """Export performance metrics in specified format."""
        # Filter metrics
        metrics_to_export = self.metrics_history
        if start_time:
            metrics_to_export = [m for m in metrics_to_export if m.timestamp >= start_time]
        if end_time:
            metrics_to_export = [m for m in metrics_to_export if m.timestamp <= end_time]
        if service_name:
            metrics_to_export = [m for m in metrics_to_export if m.service_name == service_name]
        
        # Convert to serializable format
        export_data = [
            {
                "timestamp": m.timestamp.isoformat(),
                "service_name": m.service_name,
                "operation": m.operation,
                "response_time_ms": m.response_time_ms,
                "memory_usage_mb": m.memory_usage_mb,
                "cpu_usage_percent": m.cpu_usage_percent,
                "database_query_time_ms": m.database_query_time_ms,
                "ai_tokens_used": m.ai_tokens_used,
                "cache_hit": m.cache_hit,
                "error_occurred": m.error_occurred,
                "user_id": m.user_id,
                "student_id": m.student_id,
                "additional_data": m.additional_data
            }
            for m in metrics_to_export
        ]
        
        if format.lower() == "json":
            return json.dumps(export_data, indent=2, default=str)
        elif format.lower() == "csv":
            # Simple CSV export
            if not export_data:
                return ""
            
            headers = export_data[0].keys()
            csv_lines = [",".join(headers)]
            
            for metric in export_data:
                csv_lines.append(",".join(str(metric.get(h, "")) for h in headers))
            
            return "\n".join(csv_lines)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    async def cleanup_old_metrics(self, days_to_keep: int = 30):
        """Clean up old metrics data."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        original_count = len(self.metrics_history)
        self.metrics_history = deque(
            [m for m in self.metrics_history if m.timestamp >= cutoff_date],
            maxlen=self.max_metrics_history
        )
        
        cleaned_count = original_count - len(self.metrics_history)
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} old metrics entries (older than {days_to_keep} days)")


# Decorator for automatic performance monitoring
def monitor_performance(
    service_name: str,
    operation: str = "unknown",
    user_id_param: str = "user_id",
    student_id_param: str = "student_id"
):
    """Decorator for automatic performance monitoring."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            monitoring_service = PerformanceMonitoringService()
            start_time = time.time()
            
            # Get system metrics before
            system_before = await monitoring_service.get_system_health_metrics()
            
            try:
                # Extract user and student IDs
                user_id = kwargs.get(user_id_param)
                student_id = kwargs.get(student_id_param)
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Get system metrics after
                system_after = await monitoring_service.get_system_health_metrics()
                
                # Calculate performance metrics
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                memory_delta = system_after.memory_usage_mb - system_before.memory_usage_mb
                cpu_delta = system_after.cpu_usage_percent - system_before.cpu_usage_percent
                
                # Create performance metric
                metric = PerformanceMetrics(
                    timestamp=datetime.utcnow(),
                    service_name=service_name,
                    operation=operation,
                    response_time_ms=response_time,
                    memory_usage_mb=system_after.memory_usage_mb,
                    cpu_usage_percent=system_after.cpu_usage_percent,
                    user_id=user_id,
                    student_id=student_id,
                    additional_data={
                        "memory_delta_mb": memory_delta,
                        "cpu_delta_percent": cpu_delta,
                        "function_name": func.__name__
                    }
                )
                
                # Record metric
                await monitoring_service.record_performance_metric(metric)
                
                return result
                
            except Exception as e:
                # Record error metric
                response_time = (time.time() - start_time) * 1000
                system_after = await monitoring_service.get_system_health_metrics()
                
                metric = PerformanceMetrics(
                    timestamp=datetime.utcnow(),
                    service_name=service_name,
                    operation=operation,
                    response_time_ms=response_time,
                    memory_usage_mb=system_after.memory_usage_mb,
                    cpu_usage_percent=system_after.cpu_usage_percent,
                    error_occurred=True,
                    user_id=kwargs.get(user_id_param),
                    student_id=kwargs.get(student_id_param),
                    additional_data={
                        "error_message": str(e),
                        "function_name": func.__name__
                    }
                )
                
                await monitoring_service.record_performance_metric(metric)
                raise
        
        return wrapper
    return decorator


# Global performance monitoring service instance
performance_monitoring_service = PerformanceMonitoringService()