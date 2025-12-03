"""
Vidhya AI Agent Router

This router handles all API endpoints for the Vidhya AI chat agent:
- Chat session management
- Message sending and receiving
- Chat history retrieval
- Multilingual support

Author: Mentor AI Team
Version: 1.0.0
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from services.vidhya_service import get_vidhya_service
from middleware.auth_middleware import get_current_user
from middleware.language_middleware import get_language_from_request, get_translations_from_request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/vidhya", tags=["Vidhya AI Agent"])


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class StartChatRequest(BaseModel):
    """Request model for starting a chat session."""
    student_id: Optional[str] = Field(None, description="Student ID (optional)")
    language: str = Field("en", description="Language code (e.g., en, hi, bn)")
    title: Optional[str] = Field(None, description="Session title (optional)")


class SendMessageRequest(BaseModel):
    """Request model for sending a message."""
    message: str = Field(..., description="Message content")
    session_id: str = Field(..., description="Chat session ID")
    language: Optional[str] = Field(None, description="Language override (optional)")


# ============================================================================
# CHAT SESSION ENDPOINTS
# ============================================================================

@router.post("/chat/start")
async def start_chat_session(
    request: StartChatRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Start a new chat session with Vidhya.
    
    Args:
        request: Start chat request data
        current_user: Authenticated user ID
    
    Returns:
        Session information with welcome message
    """
    try:
        vidhya_service = get_vidhya_service()
        
        # Get translations for response
        translations = get_translations_from_request(request)
        
        # Start new session
        session_info = await vidhya_service.start_chat_session(
            user_id=current_user,
            student_id=request.student_id,
            language=request.language,
            title=request.title
        )
        
        logger.info(f"Started new Vidhya chat session for user: {current_user}")
        
        # Translate success message if available
        success_message = "Chat session started successfully"
        if translations and "success" in translations and "chat_started" in translations["success"]:
            success_message = translations["success"]["chat_started"]
        
        return {
            "success": True,
            "data": session_info,
            "message": success_message
        }
        
    except Exception as e:
        # Get translated error message
        error_message = "Failed to start chat session"
        if translations and "errors" in translations and "general" in translations["errors"]:
            error_message = translations["errors"]["general"]
        
        logger.error(f"Failed to start chat session: {e}")
        raise HTTPException(status_code=500, detail=error_message)


@router.post("/chat/send")
async def send_message(
    request: SendMessageRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Send a message to Vidhya and get response.
    
    Args:
        request: Send message request data
        current_user: Authenticated user ID
    
    Returns:
        Vidhya's response
    """
    try:
        vidhya_service = get_vidhya_service()
        
        # Get translations for response
        translations = get_translations_from_request(request)
        
        # Send message and get response
        response = await vidhya_service.send_message(
            message=request.message,
            session_id=request.session_id,
            user_id=current_user,
            language=request.language
        )
        
        logger.info(f"Message sent to Vidhya for user: {current_user}")
        
        # Translate success message if available
        success_message = "Message sent successfully"
        if translations and "success" in translations and "message_sent" in translations["success"]:
            success_message = translations["success"]["message_sent"]
        
        return {
            "success": True,
            "data": response,
            "message": success_message
        }
        
    except ValueError as e:
        # Get translated error message
        error_message = str(e)
        if translations and "errors" in translations and "validation" in translations["errors"]:
            error_message = translations["errors"]["validation"]
        
        logger.error(f"Invalid request: {e}")
        raise HTTPException(status_code=400, detail=error_message)
    except Exception as e:
        # Get translated error message
        error_message = "Failed to send message"
        if translations and "errors" in translations and "general" in translations["errors"]:
            error_message = translations["errors"]["general"]
        
        logger.error(f"Failed to send message: {e}")
        raise HTTPException(status_code=500, detail=error_message)


@router.get("/chat/history/{session_id}")
async def get_chat_history(
    session_id: str,
    current_user: str = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of messages")
):
    """
    Get chat history for a session.
    
    Args:
        session_id: Chat session ID
        current_user: Authenticated user ID
        limit: Maximum number of messages to return
    
    Returns:
        Chat history
    """
    try:
        vidhya_service = get_vidhya_service()
        
        # Get chat history
        history = await vidhya_service.get_chat_history(
            session_id=session_id,
            user_id=current_user,
            limit=limit
        )
        
        return {
            "success": True,
            "data": history
        }
        
    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")


@router.get("/chat/sessions")
async def get_user_sessions(
    current_user: str = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of sessions")
):
    """
    Get all chat sessions for a user.
    
    Args:
        current_user: Authenticated user ID
        limit: Maximum number of sessions to return
    
    Returns:
        List of chat sessions
    """
    try:
        vidhya_service = get_vidhya_service()
        
        # Get user sessions
        sessions = await vidhya_service.get_user_sessions(
            user_id=current_user,
            limit=limit
        )
        
        return {
            "success": True,
            "data": {
                "sessions": sessions,
                "count": len(sessions)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get user sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat sessions")


@router.delete("/chat/session/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Delete a chat session.
    
    Args:
        session_id: Chat session ID
        current_user: Authenticated user ID
    
    Returns:
        Delete result
    """
    try:
        vidhya_service = get_vidhya_service()
        
        # Delete session
        success = await vidhya_service.delete_session(
            session_id=session_id,
            user_id=current_user
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        logger.info(f"Deleted Vidhya chat session: {session_id}")
        
        return {
            "success": True,
            "message": "Chat session deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete session: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete chat session")


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@router.get("/languages")
async def get_supported_languages():
    """
    Get list of supported languages.
    
    Returns:
        Supported languages
    """
    try:
        vidhya_service = get_vidhya_service()
        languages = vidhya_service.get_supported_languages()
        
        return {
            "success": True,
            "data": languages
        }
        
    except Exception as e:
        logger.error(f"Failed to get supported languages: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve supported languages")


@router.get("/health")
async def health_check():
    """
    Health check endpoint for Vidhya service.
    
    Returns:
        Health status
    """
    try:
        # Check Vidhya service
        vidhya_service = get_vidhya_service()
        service_status = "healthy" if vidhya_service else "unhealthy"
        
        return {
            "status": service_status,
            "service": "vidhya-ai-agent",
            "timestamp": datetime.utcnow().isoformat(),
            "features": {
                "multilingual_support": True,
                "chat_history": True,
                "session_management": True
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "vidhya-ai-agent",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }