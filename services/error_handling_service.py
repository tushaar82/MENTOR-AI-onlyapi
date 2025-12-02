"""
Comprehensive Error Handling and Logging Service

This service provides centralized error handling, logging, and monitoring
for all parent AI features services with proper error categorization,
alerting, and recovery mechanisms.

Author: Mentor AI Team
Version: 1.0.0
"""

import logging
import traceback
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from enum import Enum
import json
from functools import wraps
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels for categorization."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better organization and analysis."""
    AI_SERVICE = "ai_service"
    DATABASE = "database"
    API = "api"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    RATE_LIMITING = "rate_limiting"
    EXTERNAL_SERVICE = "external_service"
    SYSTEM = "system"
    BUSINESS_LOGIC = "business_logic"


class ServiceMetrics:
    """Service metrics tracking."""
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.success_count = 0
        self.total_response_time = 0.0
        self.errors_by_category = {}
        self.errors_by_severity = {}
        self.last_error_time = None
        self.uptime_start = datetime.utcnow()
    
    def record_request(self, response_time: float, success: bool = True):
        """Record a service request."""
        self.request_count += 1
        self.total_response_time += response_time
        
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
    
    def record_error(self, category: ErrorCategory, severity: ErrorSeverity):
        """Record an error occurrence."""
        category_key = category.value
        severity_key = severity.value
        
        self.errors_by_category[category_key] = self.errors_by_category.get(category_key, 0) + 1
        self.errors_by_severity[severity_key] = self.errors_by_severity.get(severity_key, 0) + 1
        self.last_error_time = datetime.utcnow()
    
    def get_uptime_percentage(self) -> float:
        """Calculate service uptime percentage."""
        total_time = (datetime.utcnow() - self.uptime_start).total_seconds()
        if total_time == 0:
            return 100.0
        
        # This is a simplified calculation - in production, you'd track actual downtime
        error_rate = self.error_count / max(self.request_count, 1)
        return max(0.0, (1.0 - error_rate) * 100)
    
    def get_average_response_time(self) -> float:
        """Calculate average response time."""
        return self.total_response_time / max(self.request_count, 1)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "success_count": self.success_count,
            "error_rate": self.error_count / max(self.request_count, 1),
            "success_rate": self.success_count / max(self.request_count, 1),
            "average_response_time_ms": self.get_average_response_time(),
            "uptime_percentage": self.get_uptime_percentage(),
            "errors_by_category": self.errors_by_category,
            "errors_by_severity": self.errors_by_severity,
            "last_error_time": self.last_error_time.isoformat() if self.last_error_time else None,
            "uptime_start": self.uptime_start.isoformat()
        }


class DetailedError(Exception):
    """Enhanced error class with context and metadata."""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        student_id: Optional[str] = None,
        service_name: Optional[str] = None,
        error_code: Optional[str] = None,
        recoverable: bool = True,
        suggested_action: Optional[str] = None,
        original_exception: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.context = context or {}
        self.user_id = user_id
        self.student_id = student_id
        self.service_name = service_name
        self.error_code = error_code
        self.recoverable = recoverable
        self.suggested_action = suggested_action
        self.original_exception = original_exception
        self.timestamp = datetime.utcnow()
        self.traceback = traceback.format_exc()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging."""
        return {
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "context": self.context,
            "user_id": self.user_id,
            "student_id": self.student_id,
            "service_name": self.service_name,
            "error_code": self.error_code,
            "recoverable": self.recoverable,
            "suggested_action": self.suggested_action,
            "timestamp": self.timestamp.isoformat(),
            "traceback": self.traceback
        }


class ErrorHandlingService:
    """Centralized error handling and logging service."""
    
    def __init__(self):
        self.metrics = ServiceMetrics()
        self.error_callbacks = []
        self.circuit_breakers = {}
        self.retry_configs = {}
    
    def log_error(self, error: DetailedError, extra_context: Optional[Dict[str, Any]] = None):
        """Log an error with full context."""
        # Update metrics
        self.metrics.record_error(error.category, error.severity)
        
        # Prepare log data
        log_data = error.to_dict()
        if extra_context:
            log_data["extra_context"] = extra_context
        
        # Log based on severity
        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(f"CRITICAL ERROR: {json.dumps(log_data, default=str)}")
        elif error.severity == ErrorSeverity.HIGH:
            logger.error(f"HIGH SEVERITY ERROR: {json.dumps(log_data, default=str)}")
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(f"MEDIUM SEVERITY ERROR: {json.dumps(log_data, default=str)}")
        else:
            logger.info(f"LOW SEVERITY ERROR: {json.dumps(log_data, default=str)}")
        
        # Trigger error callbacks
        for callback in self.error_callbacks:
            try:
                callback(error)
            except Exception as e:
                logger.error(f"Error in error callback: {e}")
    
    def handle_ai_service_error(
        self,
        error: Exception,
        service_name: str,
        user_id: Optional[str] = None,
        student_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> DetailedError:
        """Handle AI service errors with proper categorization."""
        if "rate limit" in str(error).lower():
            return DetailedError(
                message=f"AI service rate limit exceeded: {str(error)}",
                category=ErrorCategory.RATE_LIMITING,
                severity=ErrorSeverity.HIGH,
                context=context,
                user_id=user_id,
                student_id=student_id,
                service_name=service_name,
                original_exception=error,
                suggested_action="Wait before retrying or implement exponential backoff"
            )
        elif "timeout" in str(error).lower():
            return DetailedError(
                message=f"AI service timeout: {str(error)}",
                category=ErrorCategory.EXTERNAL_SERVICE,
                severity=ErrorSeverity.MEDIUM,
                context=context,
                user_id=user_id,
                student_id=student_id,
                service_name=service_name,
                original_exception=error,
                suggested_action="Increase timeout or implement retry mechanism"
            )
        elif "quota" in str(error).lower():
            return DetailedError(
                message=f"AI service quota exceeded: {str(error)}",
                category=ErrorCategory.EXTERNAL_SERVICE,
                severity=ErrorSeverity.HIGH,
                context=context,
                user_id=user_id,
                student_id=student_id,
                service_name=service_name,
                original_exception=error,
                suggested_action="Check quota usage and upgrade if necessary"
            )
        else:
            return DetailedError(
                message=f"AI service error: {str(error)}",
                category=ErrorCategory.AI_SERVICE,
                severity=ErrorSeverity.MEDIUM,
                context=context,
                user_id=user_id,
                student_id=student_id,
                service_name=service_name,
                original_exception=error
            )
    
    def handle_database_error(
        self,
        error: Exception,
        operation: str,
        user_id: Optional[str] = None,
        student_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> DetailedError:
        """Handle database errors with proper categorization."""
        if "connection" in str(error).lower():
            return DetailedError(
                message=f"Database connection error during {operation}: {str(error)}",
                category=ErrorCategory.DATABASE,
                severity=ErrorSeverity.HIGH,
                context={**(context or {}), "operation": operation},
                user_id=user_id,
                student_id=student_id,
                original_exception=error,
                suggested_action="Check database connection and retry"
            )
        elif "timeout" in str(error).lower():
            return DetailedError(
                message=f"Database timeout during {operation}: {str(error)}",
                category=ErrorCategory.DATABASE,
                severity=ErrorSeverity.MEDIUM,
                context={**(context or {}), "operation": operation},
                user_id=user_id,
                student_id=student_id,
                original_exception=error,
                suggested_action="Optimize query or increase timeout"
            )
        else:
            return DetailedError(
                message=f"Database error during {operation}: {str(error)}",
                category=ErrorCategory.DATABASE,
                severity=ErrorSeverity.MEDIUM,
                context={**(context or {}), "operation": operation},
                user_id=user_id,
                student_id=student_id,
                original_exception=error
            )
    
    def handle_validation_error(
        self,
        error: Exception,
        field: str,
        value: Any,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> DetailedError:
        """Handle validation errors."""
        return DetailedError(
            message=f"Validation error for field '{field}': {str(error)}",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            context={**(context or {}), "field": field, "value": str(value)},
            user_id=user_id,
            original_exception=error,
            suggested_action=f"Provide valid value for {field}"
        )
    
    def register_error_callback(self, callback):
        """Register a callback to be called on errors."""
        self.error_callbacks.append(callback)
    
    def set_circuit_breaker(self, service_name: str, failure_threshold: int = 5, timeout_seconds: int = 60):
        """Configure circuit breaker for a service."""
        self.circuit_breakers[service_name] = {
            "failure_threshold": failure_threshold,
            "timeout_seconds": timeout_seconds,
            "failure_count": 0,
            "last_failure_time": None,
            "state": "closed"  # closed, open, half-open
        }
    
    def check_circuit_breaker(self, service_name: str) -> bool:
        """Check if circuit breaker is open for a service."""
        if service_name not in self.circuit_breakers:
            return False
        
        breaker = self.circuit_breakers[service_name]
        
        # Reset if timeout has passed
        if breaker["state"] == "open" and breaker["last_failure_time"]:
            if datetime.utcnow() - breaker["last_failure_time"] > timedelta(seconds=breaker["timeout_seconds"]):
                breaker["state"] = "half-open"
                breaker["failure_count"] = 0
                logger.info(f"Circuit breaker for {service_name} reset to half-open")
        
        return breaker["state"] == "open"
    
    def record_circuit_breaker_failure(self, service_name: str):
        """Record a failure for circuit breaker."""
        if service_name in self.circuit_breakers:
            breaker = self.circuit_breakers[service_name]
            breaker["failure_count"] += 1
            breaker["last_failure_time"] = datetime.utcnow()
            
            if breaker["failure_count"] >= breaker["failure_threshold"]:
                breaker["state"] = "open"
                logger.warning(f"Circuit breaker for {service_name} opened due to {breaker['failure_count']} failures")
    
    def record_circuit_breaker_success(self, service_name: str):
        """Record a success for circuit breaker."""
        if service_name in self.circuit_breakers:
            breaker = self.circuit_breakers[service_name]
            if breaker["state"] == "half-open":
                breaker["failure_count"] = max(0, breaker["failure_count"] - 1)
                if breaker["failure_count"] == 0:
                    breaker["state"] = "closed"
                    logger.info(f"Circuit breaker for {service_name} closed after successful requests")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current service metrics."""
        return self.metrics.to_dict()
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status."""
        metrics = self.metrics.to_dict()
        uptime = metrics["uptime_percentage"]
        error_rate = metrics["error_rate"]
        
        if uptime >= 99.5 and error_rate < 0.01:
            status = "healthy"
            status_code = 200
        elif uptime >= 95.0 and error_rate < 0.05:
            status = "degraded"
            status_code = 200
        else:
            status = "unhealthy"
            status_code = 503
        
        return {
            "status": status,
            "status_code": status_code,
            "uptime_percentage": uptime,
            "error_rate": error_rate,
            "average_response_time_ms": metrics["average_response_time_ms"],
            "total_requests": metrics["request_count"],
            "total_errors": metrics["error_count"],
            "circuit_breakers": {
                name: breaker["state"] for name, breaker in self.circuit_breakers.items()
            }
        }


# Decorator for automatic error handling
def handle_service_errors(
    service_name: str,
    user_id_param: str = "user_id",
    student_id_param: str = "student_id"
):
    """Decorator for automatic error handling in service methods."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            error_handler = ErrorHandlingService()
            start_time = time.time()
            
            try:
                # Check circuit breaker
                if error_handler.check_circuit_breaker(service_name):
                    raise DetailedError(
                        message=f"Circuit breaker open for {service_name}",
                        category=ErrorCategory.SYSTEM,
                        severity=ErrorSeverity.HIGH,
                        service_name=service_name,
                        recoverable=False,
                        suggested_action="Wait for circuit breaker to reset"
                    )
                
                # Extract user and student IDs from kwargs
                user_id = kwargs.get(user_id_param)
                student_id = kwargs.get(student_id_param)
                
                result = await func(*args, **kwargs)
                
                # Record success
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                error_handler.metrics.record_request(response_time, True)
                error_handler.record_circuit_breaker_success(service_name)
                
                return result
                
            except DetailedError as e:
                # Record detailed error
                response_time = (time.time() - start_time) * 1000
                error_handler.metrics.record_request(response_time, False)
                error_handler.log_error(e)
                error_handler.record_circuit_breaker_failure(service_name)
                raise
                
            except Exception as e:
                # Handle unexpected errors
                response_time = (time.time() - start_time) * 1000
                error_handler.metrics.record_request(response_time, False)
                
                detailed_error = DetailedError(
                    message=f"Unexpected error in {service_name}: {str(e)}",
                    category=ErrorCategory.SYSTEM,
                    severity=ErrorSeverity.HIGH,
                    user_id=user_id,
                    student_id=student_id,
                    service_name=service_name,
                    original_exception=e
                )
                
                error_handler.log_error(detailed_error)
                error_handler.record_circuit_breaker_failure(service_name)
                raise detailed_error
        
        return wrapper
    return decorator


# Global error handling service instance
error_handling_service = ErrorHandlingService()