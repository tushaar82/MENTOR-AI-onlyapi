"""
Vidhya AI Agent Database Models

This module contains Pydantic models for Vidhya AI agent database operations:
- Chat sessions
- Chat messages
- User preferences

Author: Mentor AI Team
Version: 1.0.0
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Model for a chat message."""
    
    message_id: str = Field(..., description="Unique message identifier")
    user_id: str = Field(..., description="User who sent the message")
    session_id: str = Field(..., description="Chat session ID")
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    language: str = Field("en", description="Language code")
    timestamp: datetime = Field(..., description="Message timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ChatSession(BaseModel):
    """Model for a chat session."""
    
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User who owns the session")
    student_id: Optional[str] = Field(None, description="Student ID if applicable")
    title: Optional[str] = Field(None, description="Session title")
    language: str = Field("en", description="Primary language for session")
    created_at: datetime = Field(..., description="Session creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    message_count: int = Field(0, description="Number of messages in session")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class VidhyaUserPreferences(BaseModel):
    """Model for Vidhya user preferences."""
    
    user_id: str = Field(..., description="User ID")
    default_language: str = Field("en", description="Default language for chats")
    auto_translate: bool = Field(False, description="Auto-translate responses")
    voice_enabled: bool = Field(False, description="Voice response enabled")
    typing_indicators: bool = Field(True, description="Show typing indicators")
    message_sound: bool = Field(True, description="Play message sound")
    theme: str = Field("default", description="Chat theme")
    font_size: str = Field("medium", description="Font size (small/medium/large)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Preferences creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class VidhyaAnalytics(BaseModel):
    """Model for Vidhya usage analytics."""
    
    analytics_id: str = Field(..., description="Unique analytics identifier")
    user_id: str = Field(..., description="User ID")
    session_id: Optional[str] = Field(None, description="Session ID if applicable")
    event_type: str = Field(..., description="Event type (session_start, message_sent, etc.)")
    event_data: Dict[str, Any] = Field(default_factory=dict, description="Event-specific data")
    language: str = Field("en", description="Language used")
    timestamp: datetime = Field(..., description="Event timestamp")
    duration_ms: Optional[int] = Field(None, description="Event duration in milliseconds")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class VidhyaFeedback(BaseModel):
    """Model for Vidhya response feedback."""
    
    feedback_id: str = Field(..., description="Unique feedback identifier")
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Chat session ID")
    message_id: str = Field(..., description="Message ID being rated")
    rating: int = Field(..., ge=1, le=5, description="Rating (1-5)")
    feedback_type: str = Field("helpful", description="Feedback type (helpful, not_helpful, inappropriate)")
    comment: Optional[str] = Field(None, description="Additional feedback comment")
    timestamp: datetime = Field(..., description="Feedback timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class VidhyaKnowledgeBase(BaseModel):
    """Model for Vidhya knowledge base entries."""
    
    entry_id: str = Field(..., description="Unique entry identifier")
    topic: str = Field(..., description="Knowledge topic")
    subject: str = Field(..., description="Subject area")
    exam_type: str = Field(..., description="Exam type (JEE_MAIN, JEE_ADVANCED, NEET)")
    language: str = Field("en", description="Language of content")
    question: str = Field(..., description="Common question")
    answer: str = Field(..., description="Simple, understandable answer")
    difficulty: str = Field("medium", description="Difficulty level")
    tags: List[str] = Field(default_factory=list, description="Search tags")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    usage_count: int = Field(0, description="Number of times used")
    rating: float = Field(0.0, description="Average rating")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ============================================================================
# REQUEST MODELS
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


class UpdatePreferencesRequest(BaseModel):
    """Request model for updating user preferences."""
    
    default_language: Optional[str] = Field(None, description="Default language for chats")
    auto_translate: Optional[bool] = Field(None, description="Auto-translate responses")
    voice_enabled: Optional[bool] = Field(None, description="Voice response enabled")
    typing_indicators: Optional[bool] = Field(None, description="Show typing indicators")
    message_sound: Optional[bool] = Field(None, description="Play message sound")
    theme: Optional[str] = Field(None, description="Chat theme")
    font_size: Optional[str] = Field(None, description="Font size (small/medium/large)")


class SubmitFeedbackRequest(BaseModel):
    """Request model for submitting feedback."""
    
    session_id: str = Field(..., description="Chat session ID")
    message_id: str = Field(..., description="Message ID being rated")
    rating: int = Field(..., ge=1, le=5, description="Rating (1-5)")
    feedback_type: str = Field("helpful", description="Feedback type (helpful, not_helpful, inappropriate)")
    comment: Optional[str] = Field(None, description="Additional feedback comment")


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class ChatResponse(BaseModel):
    """Response model for chat interactions."""
    
    session_id: str = Field(..., description="Chat session ID")
    response: str = Field(..., description="Vidhya's response")
    language: str = Field(..., description="Response language")
    timestamp: str = Field(..., description="Response timestamp")
    message_count: int = Field(..., description="Total messages in session")
    error: Optional[bool] = Field(None, description="Error indicator")


class SessionInfo(BaseModel):
    """Response model for session information."""
    
    session_id: str = Field(..., description="Chat session ID")
    title: str = Field(..., description="Session title")
    language: str = Field(..., description="Session language")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    message_count: int = Field(..., description="Number of messages")


class ChatHistoryResponse(BaseModel):
    """Response model for chat history."""
    
    session_id: str = Field(..., description="Chat session ID")
    title: str = Field(..., description="Session title")
    language: str = Field(..., description="Session language")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    message_count: int = Field(..., description="Number of messages")
    messages: List[Dict[str, Any]] = Field(..., description="Chat messages")


class UserSessionsResponse(BaseModel):
    """Response model for user sessions."""
    
    sessions: List[SessionInfo] = Field(..., description="User's chat sessions")
    count: int = Field(..., description="Total number of sessions")


class ApiResponse(BaseModel):
    """Generic API response model."""
    
    success: bool = Field(..., description="Request success status")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message if any")