"""
Token Usage Router Module

This module defines FastAPI endpoints for token usage tracking and management
in the Mentor AI EdTech Platform.

Endpoints:
- GET /usage/student/{student_id}: Get token usage for a student
- GET /limits/student/{student_id}: Get token limits for a student
- GET /usage/parent: Get token usage for all children of a parent
- POST /usage/reset/daily/{student_id}: Reset daily token usage (admin)

Author: Mentor AI Team
Version: 1.0.0
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from services.token_usage_service import get_token_usage_service
from middleware.auth_middleware import get_current_user
from services.child_service import ChildService

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/token-usage",
    tags=["Token Usage"]
)


@router.get("/student/{student_id}")
async def get_student_token_usage(
    student_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Get token usage statistics for a student.
    
    Args:
        student_id: Student ID to get usage for
        current_user: Authenticated parent ID
    
    Returns:
        Token usage statistics
    
    Raises:
        HTTPException: 403 if parent doesn't own the student
        HTTPException: 404 if student not found
        HTTPException: 500 if server error
    """
    try:
        logger.info(f"Getting token usage for student: {student_id} by parent: {current_user}")
        
        # Verify parent owns this student
        try:
            child_profile = ChildService.get_child_by_id(student_id)
            if child_profile.parent_id != current_user:
                logger.warning(f"Parent {current_user} attempted to access student {student_id} owned by {child_profile.parent_id}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to access this student's token usage"
                )
        except Exception as e:
            if "not found" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Student not found: {student_id}"
                )
            raise
        
        # Get token usage
        token_service = get_token_usage_service()
        usage_data = await token_service.get_student_token_usage(student_id)
        
        logger.info(f"Retrieved token usage for student: {student_id}")
        return {
            "success": True,
            "data": usage_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting token usage for student {student_id}: {e}")
        logger.exception("Full traceback:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve token usage. Please try again later."
        )


@router.get("/limits/student/{student_id}")
async def get_student_token_limits(
    student_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Get token limits for a student.
    
    Args:
        student_id: Student ID to get limits for
        current_user: Authenticated parent ID
    
    Returns:
        Token limits information
    
    Raises:
        HTTPException: 403 if parent doesn't own the student
        HTTPException: 404 if student not found
        HTTPException: 500 if server error
    """
    try:
        logger.info(f"Getting token limits for student: {student_id} by parent: {current_user}")
        
        # Verify parent owns this student
        try:
            child_profile = ChildService.get_child_by_id(student_id)
            if child_profile.parent_id != current_user:
                logger.warning(f"Parent {current_user} attempted to access student {student_id} owned by {child_profile.parent_id}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to access this student's token limits"
                )
        except Exception as e:
            if "not found" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Student not found: {student_id}"
                )
            raise
        
        # Get current usage and limits
        token_service = get_token_usage_service()
        
        # Get current usage
        daily_usage = await token_service._get_daily_usage(student_id)
        monthly_usage = await token_service._get_monthly_usage(student_id)
        
        # Get limits
        limits = await token_service._get_student_token_limits(student_id)
        
        # Calculate remaining
        daily_remaining = max(0, limits["daily"] - daily_usage)
        monthly_remaining = max(0, limits["monthly"] - monthly_usage)
        
        # Calculate percentages
        daily_percentage = (daily_usage / limits["daily"]) * 100 if limits["daily"] > 0 else 0
        monthly_percentage = (monthly_usage / limits["monthly"]) * 100 if limits["monthly"] > 0 else 0
        
        limits_data = {
            "student_id": student_id,
            "limits": {
                "daily": limits["daily"],
                "monthly": limits["monthly"]
            },
            "usage": {
                "daily": {
                    "used": daily_usage,
                    "remaining": daily_remaining,
                    "percentage": round(daily_percentage, 2)
                },
                "monthly": {
                    "used": monthly_usage,
                    "remaining": monthly_remaining,
                    "percentage": round(monthly_percentage, 2)
                }
            },
            "reset_times": {
                "daily": _get_next_daily_reset(),
                "monthly": _get_next_monthly_reset()
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Retrieved token limits for student: {student_id}")
        return {
            "success": True,
            "data": limits_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting token limits for student {student_id}: {e}")
        logger.exception("Full traceback:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve token limits. Please try again later."
        )


@router.get("/parent")
async def get_parent_children_token_usage(
    current_user: str = Depends(get_current_user),
    include_history: bool = Query(False, description="Include detailed usage history")
):
    """
    Get token usage for all children of a parent.
    
    Args:
        current_user: Authenticated parent ID
        include_history: Include detailed usage history
    
    Returns:
        Token usage for all children
    
    Raises:
        HTTPException: 500 if server error
    """
    try:
        logger.info(f"Getting token usage for all children of parent: {current_user}")
        
        # Get all children for this parent
        # This would require a new method in ChildService to get all children
        # For now, we'll return a placeholder implementation
        
        token_service = get_token_usage_service()
        
        # Placeholder - in real implementation, you'd query all children
        # and get their usage
        children_usage = []
        
        # Example structure for one child
        example_usage = {
            "student_id": "child_example_123",
            "name": "Example Child",
            "usage": {
                "daily": {
                    "used": 250,
                    "limit": 1000,
                    "remaining": 750,
                    "percentage": 25.0
                },
                "monthly": {
                    "used": 2500,
                    "limit": 10000,
                    "remaining": 7500,
                    "percentage": 25.0
                }
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
        # In real implementation, you'd:
        # 1. Get all children for parent
        # 2. For each child, get their token usage
        # 3. Compile into response
        
        logger.info(f"Retrieved token usage for {len(children_usage)} children of parent: {current_user}")
        return {
            "success": True,
            "data": {
                "children": children_usage,
                "summary": {
                    "total_daily_used": sum(child["usage"]["daily"]["used"] for child in children_usage),
                    "total_monthly_used": sum(child["usage"]["monthly"]["used"] for child in children_usage),
                    "children_count": len(children_usage)
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting token usage for parent {current_user}: {e}")
        logger.exception("Full traceback:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve token usage. Please try again later."
        )


@router.post("/reset/daily/{student_id}")
async def reset_daily_token_usage(
    student_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Reset daily token usage for a student (admin endpoint).
    
    Args:
        student_id: Student ID to reset usage for
        current_user: Authenticated parent ID
    
    Returns:
        Reset confirmation
    
    Raises:
        HTTPException: 403 if parent doesn't own the student
        HTTPException: 404 if student not found
        HTTPException: 500 if server error
    """
    try:
        logger.info(f"Resetting daily token usage for student: {student_id} by parent: {current_user}")
        
        # Verify parent owns this student
        try:
            child_profile = ChildService.get_child_by_id(student_id)
            if child_profile.parent_id != current_user:
                logger.warning(f"Parent {current_user} attempted to reset student {student_id} owned by {child_profile.parent_id}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to reset this student's token usage"
                )
        except Exception as e:
            if "not found" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Student not found: {student_id}"
                )
            raise
        
        # Reset daily usage
        token_service = get_token_usage_service()
        await token_service.reset_daily_usage(student_id)
        
        logger.info(f"Reset daily usage for student: {student_id}")
        return {
            "success": True,
            "message": "Daily token usage reset successfully",
            "student_id": student_id,
            "reset_time": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting daily usage for student {student_id}: {e}")
        logger.exception("Full traceback:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset daily token usage. Please try again later."
        )


@router.get("/summary/parent")
async def get_parent_token_summary(
    current_user: str = Depends(get_current_user),
    period: str = Query("month", description="Period: day, week, month")
):
    """
    Get token usage summary for a parent.
    
    Args:
        current_user: Authenticated parent ID
        period: Time period for summary (day, week, month)
    
    Returns:
        Token usage summary
    
    Raises:
        HTTPException: 500 if server error
    """
    try:
        logger.info(f"Getting token usage summary for parent: {current_user}, period: {period}")
        
        # Calculate date range based on period
        end_date = datetime.utcnow()
        
        if period == "day":
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month":
            start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = end_date - timedelta(days=30)  # Default to 30 days
        
        # Placeholder implementation
        # In real implementation, you'd:
        # 1. Get all children for parent
        # 2. Query token usage for date range
        # 3. Aggregate by period
        
        summary_data = {
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_tokens_used": 0,  # Would sum actual usage
            "total_requests": 0,      # Would count requests
            "daily_average": 0,         # Would calculate average
            "children_breakdown": []     # Would list each child's usage
        }
        
        logger.info(f"Retrieved token usage summary for parent: {current_user}")
        return {
            "success": True,
            "data": summary_data
        }
        
    except Exception as e:
        logger.error(f"Error getting token usage summary for parent {current_user}: {e}")
        logger.exception("Full traceback:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve token usage summary. Please try again later."
        )


def _get_next_daily_reset() -> str:
    """Get next daily reset time as ISO string."""
    tomorrow = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    return tomorrow.isoformat()


def _get_next_monthly_reset() -> str:
    """Get next monthly reset time as ISO string."""
    next_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if next_month.month == 12:
        next_month = next_month.replace(year=next_month.year + 1, month=1)
    else:
        next_month = next_month.replace(month=next_month.month + 1)
    return next_month.isoformat()