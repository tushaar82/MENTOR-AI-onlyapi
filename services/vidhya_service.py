"""
Vidhya AI Agent Service

This module provides the Vidhya AI agent service for the Mentor AI EdTech Platform.
Vidhya is an AI assistant that can answer questions in simple and understandable language,
including support for local languages.

Features:
- Multilingual chat support (English + local languages)
- Context-aware conversations
- Simple and understandable responses
- Educational content assistance
- Integration with Gemini AI for responses
- Chat history persistence

Author: Mentor AI Team
Version: 1.0.0
"""

import logging
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from functools import lru_cache

from services.unified_gemini_config_service import get_unified_gemini_service, GeminiConfig
from services.gemini_service import get_gemini_service
from services.token_usage_service import get_token_usage_service
from utils.firebase_config import get_firestore_client

# Configure logging
logger = logging.getLogger(__name__)

# Supported languages
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "हिन्दी (Hindi)",
    "bn": "বাংলা (Bengali)",
    "te": "తెలుగు (Telugu)",
    "ta": "தமிழ் (Tamil)",
    "mr": "मराठी (Marathi)",
    "gu": "ગુજરાતી (Gujarati)",
    "kn": "ಕನ್ನಡ (Kannada)",
    "ml": "മലയാളം (Malayalam)",
    "pa": "ਪੰਜਾਬੀ (Punjabi)"
}

# Default language
DEFAULT_LANGUAGE = "en"

# Chat history settings
MAX_CHAT_HISTORY = 50  # Maximum messages to keep in memory
CHAT_HISTORY_TTL = timedelta(days=30)  # How long to keep chat history


@dataclass
class ChatMessage:
    """Model for a chat message."""
    
    message_id: str
    user_id: str
    session_id: str
    role: str  # "user" or "assistant"
    content: str
    language: str = DEFAULT_LANGUAGE
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatSession:
    """Model for a chat session."""
    
    session_id: str
    user_id: str
    student_id: Optional[str] = None
    title: Optional[str] = None
    language: str = DEFAULT_LANGUAGE
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    message_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class VidhyaService:
    """
    Vidhya AI Agent Service
    
    This service provides the Vidhya AI assistant functionality with multilingual support
    and context-aware conversations.
    
    Attributes:
        gemini_service: Gemini AI service for generating responses
        unified_service: Unified Gemini configuration service
        chat_sessions: In-memory storage for active sessions
        chat_history: In-memory storage for chat messages
    
    Example:
        >>> service = VidhyaService()
        >>> response = service.chat("What is photosynthesis?", user_id="user123")
        >>> print(response["response"])
    """
    
    def __init__(
        self,
        gemini_service=None,
        unified_service=None,
        enable_persistence: bool = True
    ):
        """
        Initialize Vidhya Service.
        
        Args:
            gemini_service: Optional Gemini service instance
            unified_service: Optional unified Gemini service instance
            enable_persistence: Enable database persistence
        """
        logger.info("Initializing Vidhya AI Agent Service")
        
        # Initialize Firebase client
        self.db = get_firestore_client() if enable_persistence else None
        
        # Initialize services
        self.gemini_service = gemini_service if gemini_service else get_gemini_service()
        self.unified_service = unified_service if unified_service else get_unified_gemini_service()
        
        # Configuration
        self.enable_persistence = enable_persistence
        
        # Collections
        self.sessions_collection = "vidhya_chat_sessions"
        self.messages_collection = "vidhya_chat_messages"
        
        # In-memory storage (for active sessions)
        self.chat_sessions: Dict[str, ChatSession] = {}
        self.chat_history: Dict[str, List[ChatMessage]] = {}
        
        logger.info(f"Vidhya Service initialized with {len(SUPPORTED_LANGUAGES)} supported languages")
        logger.info(f"Default language: {SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE]}")
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get list of supported languages.
        
        Returns:
            Dictionary mapping language codes to language names
        """
        return SUPPORTED_LANGUAGES.copy()
    
    async def start_chat_session(
        self,
        user_id: str,
        student_id: Optional[str] = None,
        language: str = DEFAULT_LANGUAGE,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start a new chat session.
        
        Args:
            user_id: User ID
            student_id: Optional student ID
            language: Language code (default: English)
            title: Optional session title
        
        Returns:
            Session information
        """
        # Validate language
        if language not in SUPPORTED_LANGUAGES:
            language = DEFAULT_LANGUAGE
            logger.warning(f"Unsupported language '{language}', using default '{DEFAULT_LANGUAGE}'")
        
        # Generate session ID
        session_id = f"vidhya_{user_id}_{int(time.time())}"
        
        # Create session
        session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            student_id=student_id,
            title=title or f"Chat - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            language=language
        )
        
        # Store session
        self.chat_sessions[session_id] = session
        self.chat_history[session_id] = []
        
        # Send welcome message
        welcome_message = self._get_welcome_message(language)
        welcome_msg = ChatMessage(
            message_id=f"{session_id}_welcome",
            user_id=user_id,
            session_id=session_id,
            role="assistant",
            content=welcome_message,
            language=language
        )
        self.chat_history[session_id].append(welcome_msg)
        
        logger.info(f"Started new chat session: {session_id} for user: {user_id}")
        
        # Save to database if persistence is enabled
        if self.enable_persistence and self.db:
            self._save_session_to_db(session)
        
        return {
            "session_id": session_id,
            "title": session.title,
            "language": session.language,
            "welcome_message": welcome_message,
            "supported_languages": SUPPORTED_LANGUAGES
        }
    
    async def send_message(
        self,
        message: str,
        session_id: str,
        user_id: str,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a message to Vidhya and get response.
        
        Args:
            message: User message
            session_id: Chat session ID
            user_id: User ID
            language: Optional language override
        
        Returns:
            Response with Vidhya's answer
        """
        # Validate session
        if session_id not in self.chat_sessions:
            raise ValueError(f"Invalid session ID: {session_id}")
        
        session = self.chat_sessions[session_id]
        if session.user_id != user_id:
            raise ValueError("Session does not belong to user")
        
        # Use session language or override
        target_language = language if language else session.language
        if target_language not in SUPPORTED_LANGUAGES:
            target_language = DEFAULT_LANGUAGE
        
        # Get student ID from session
        student_id = session.student_id
        
        # Estimate tokens needed
        estimated_input_tokens = len(message) // 4
        estimated_output_tokens = 150  # Base estimate for response
        estimated_total_tokens = estimated_input_tokens + estimated_output_tokens
        
        # Check token limits if student_id is available
        if student_id:
            token_service = get_token_usage_service()
            limit_check = await token_service.check_token_limit(
                student_id=student_id,
                tokens_requested=estimated_total_tokens
            )
            
            if not limit_check["allowed"]:
                logger.warning(
                    f"Token limit exceeded for student {student_id}: "
                    f"requested={estimated_total_tokens}, "
                    f"daily_remaining={limit_check['daily_remaining']}, "
                    f"monthly_remaining={limit_check['monthly_remaining']}"
                )
                raise ValueError(
                    f"Token limit exceeded. Daily remaining: {limit_check['daily_remaining']}, "
                    f"Monthly remaining: {limit_check['monthly_remaining']}. "
                    f"Please upgrade your plan or try again tomorrow."
                )
        
        # Store user message
        user_msg = ChatMessage(
            message_id=f"{session_id}_{len(self.chat_history[session_id])}",
            user_id=user_id,
            session_id=session_id,
            role="user",
            content=message,
            language=target_language
        )
        self.chat_history[session_id].append(user_msg)
        
        # Generate response
        try:
            # Build context-aware prompt
            prompt = self._build_chat_prompt(
                message=message,
                session_id=session_id,
                language=target_language
            )
            
            # Generate response using Gemini
            response_text = await self._generate_response(prompt, user_id, target_language)
            
            # Calculate actual tokens used
            actual_input_tokens = len(message) // 4
            actual_output_tokens = len(response_text) // 4
            actual_total_tokens = actual_input_tokens + actual_output_tokens
            
            # Store assistant response
            assistant_msg = ChatMessage(
                message_id=f"{session_id}_{len(self.chat_history[session_id])}",
                user_id=user_id,
                session_id=session_id,
                role="assistant",
                content=response_text,
                language=target_language
            )
            self.chat_history[session_id].append(assistant_msg)
            
            # Update session
            session.updated_at = datetime.utcnow()
            session.message_count = len(self.chat_history[session_id])
            
            # Track token usage if student_id is available
            if student_id:
                token_service = get_token_usage_service()
                await token_service.track_token_usage(
                    student_id=student_id,
                    tokens_used=actual_total_tokens,
                    interaction_type="vidhya_chat",
                    metadata={
                        "session_id": session_id,
                        "message_length": len(message),
                        "response_length": len(response_text),
                        "language": target_language
                    }
                )
            
            # Save to database if persistence is enabled
            if self.enable_persistence and self.db:
                self._save_message_to_db(user_msg)
                self._save_message_to_db(assistant_msg)
                self._update_session_in_db(session)
            
            logger.info(f"Generated response for session {session_id}: {len(response_text)} chars, {actual_total_tokens} tokens")
            
            return {
                "session_id": session_id,
                "response": response_text,
                "language": target_language,
                "timestamp": assistant_msg.timestamp.isoformat(),
                "message_count": session.message_count,
                "tokens_used": actual_total_tokens,
                "token_breakdown": {
                    "input": actual_input_tokens,
                    "output": actual_output_tokens,
                    "total": actual_total_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            
            # Return error message
            error_response = self._get_error_message(target_language)
            error_msg = ChatMessage(
                message_id=f"{session_id}_{len(self.chat_history[session_id])}",
                user_id=user_id,
                session_id=session_id,
                role="assistant",
                content=error_response,
                language=target_language
            )
            self.chat_history[session_id].append(error_msg)
            
            # Track minimal token usage for error responses
            if student_id:
                token_service = get_token_usage_service()
                error_tokens = len(error_response) // 4
                await token_service.track_token_usage(
                    student_id=student_id,
                    tokens_used=error_tokens,
                    interaction_type="vidhya_chat_error",
                    metadata={
                        "session_id": session_id,
                        "error": True,
                        "language": target_language
                    }
                )
            
            # Save error message to database if persistence is enabled
            if self.enable_persistence and self.db:
                self._save_message_to_db(error_msg)
            
            return {
                "session_id": session_id,
                "response": error_response,
                "language": target_language,
                "timestamp": error_msg.timestamp.isoformat(),
                "error": True,
                "tokens_used": error_tokens
            }
    
    async def get_chat_history(
        self,
        session_id: str,
        user_id: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get chat history for a session.
        
        Args:
            session_id: Chat session ID
            user_id: User ID
            limit: Maximum number of messages to return
        
        Returns:
            Chat history
        """
        # Validate session
        if session_id not in self.chat_sessions:
            raise ValueError(f"Invalid session ID: {session_id}")
        
        session = self.chat_sessions[session_id]
        if session.user_id != user_id:
            raise ValueError("Session does not belong to user")
        
        # Get messages
        messages = self.chat_history.get(session_id, [])
        
        # Apply limit
        if limit > 0:
            messages = messages[-limit:]
        
        return {
            "session_id": session_id,
            "title": session.title,
            "language": session.language,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "message_count": len(messages),
            "messages": [
                {
                    "message_id": msg.message_id,
                    "role": msg.role,
                    "content": msg.content,
                    "language": msg.language,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in messages
            ]
        }
    
    async def get_user_sessions(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get all chat sessions for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of sessions to return
        
        Returns:
            List of chat sessions
        """
        user_sessions = [
            session for session in self.chat_sessions.values()
            if session.user_id == user_id
        ]
        
        # Sort by updated_at (most recent first)
        user_sessions.sort(key=lambda s: s.updated_at, reverse=True)
        
        # Apply limit
        if limit > 0:
            user_sessions = user_sessions[:limit]
        
        return [
            {
                "session_id": session.session_id,
                "title": session.title,
                "language": session.language,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "message_count": session.message_count
            }
            for session in user_sessions
        ]
    
    async def delete_session(
        self,
        session_id: str,
        user_id: str
    ) -> bool:
        """
        Delete a chat session.
        
        Args:
            session_id: Chat session ID
            user_id: User ID
        
        Returns:
            True if deleted successfully
        """
        # Validate session
        if session_id not in self.chat_sessions:
            return False
        
        session = self.chat_sessions[session_id]
        if session.user_id != user_id:
            return False
        
        # Delete session and history
        del self.chat_sessions[session_id]
        if session_id in self.chat_history:
            del self.chat_history[session_id]
        
        logger.info(f"Deleted chat session: {session_id}")
        return True
    
    def _get_welcome_message(self, language: str) -> str:
        """
        Get welcome message in specified language.
        
        Args:
            language: Language code
        
        Returns:
            Welcome message
        """
        welcome_messages = {
            "en": "Hello! I'm Vidhya, your AI learning assistant. I'm here to help you with your studies and answer any questions you might have. What would you like to learn about today?",
            "hi": "नमस्ते! मैं विद्या हूं, आपकी AI लर्निंग सहायक। मैं आपकी पढ़ाई में मदद करने और आपके किसी भी सवाल का जवाब देने के लिए यहां हूं। आप आज क्या सीखना चाहेंगे?",
            "bn": "হ্যালো! আমি বিদ্যা, আপনার AI লার্নিং সহকারী। আমি আপনার পড়াশোনায় সাহায্য করতে এবং আপনার যেকোনো প্রশ্নের উত্তর দিতে এখানে আছি। আজ আপনি কী শিখতে চান?",
            "te": "హలో! నేను విద్య, మీ AI లెర్నింగ్ అసిస్టెంట్. నేను మీ చదువులో సహాయం చేయడానికి మరియు మీ ఏవైనా ప్రశ్నలకు సమాధానాలు ఇవ్వడానికి ఇక్కడ ఉన్నాను. మీరు ఈరోజు ఏమి నేర్చుకోవాలనుకుంటున్నారు?",
            "ta": "வணக்கம்! நான் வித்யா, உங்கள் AI கற்றல் உதவியாளர். நான் உங்கள் படிப்பில் உதவவும், உங்களுக்கு எந்த கேள்விகள் இருந்தாலும் பதிலளிக்கவும் இங்கே இருக்கிறேன். இன்று நீங்கள் என்ன கற்றுக்கொள்ள விரும்புகிறீர்கள்?",
            "mr": "नमस्कार! मी विद्या, तुमची AI शिक्षण सहाय्यक. मी तुमच्या अभ्यासात मदत करण्यासाठी आणि तुमच्या कोणत्याही प्रश्नांची उत्तरे देण्यासाठी इथे आहे. तुम्ही आज काय शिकायला इच्छिता?"
        }
        
        return welcome_messages.get(language, welcome_messages["en"])
    
    def _get_error_message(self, language: str) -> str:
        """
        Get error message in specified language.
        
        Args:
            language: Language code
        
        Returns:
            Error message
        """
        error_messages = {
            "en": "Sorry, I'm having trouble understanding right now. Could you please rephrase your question or try again later?",
            "hi": "क्षमा करें, मुझे अभी समझने में परेशानी हो रही है। क्या आप कृपया अपने प्रश्न को फिर से व्यक्त कर सकते हैं या बाद में प्रयास कर सकते हैं?",
            "bn": "দুঃখিত, আমি এখন বুঝতে সমস্যা হচ্ছে। আপনি কি দয়া করে আপনার প্রশ্নটি পুনরায় প্রকাশ করতে পারেন বা পরে আবার চেষ্টা করতে পারেন?",
            "te": "క్షమించండి, నేను ఇప్పుడు అర్థం చేసుకోవడంలో ఇబ్బంది పడుతున్నాను. మీరు దయచేసి మీ ప్రశ్నను తిరిగి వ్యక్తపరచవచ్చు లేదా తరువాత మళ్ళీ ప్రయత్నించవచ్చు?",
            "ta": "மன்னிக்கவும், நான் இப்போது புரிந்து கொள்ளும் சிக்கலில் உள்ளேன். நீங்கள் தயவுசெய்து உங்கள் கேள்வியை மீண்டும் வார்த்தையில் கூறலாமா அல்லது பின்னர் மீண்டும் முயற்சிக்கலாமா?",
            "mr": "क्षमस्व, मला आता समजून घेण्यात त्रुटी होत आहे. तुम्ही कृपया तुमचा प्रश्न पुन्हा व्यक्त करू शकता किंवा नंतर पुन्हा प्रयत्न करू शकता?"
        }
        
        return error_messages.get(language, error_messages["en"])
    
    def _build_chat_prompt(
        self,
        message: str,
        session_id: str,
        language: str
    ) -> str:
        """
        Build context-aware prompt for chat.
        
        Args:
            message: Current user message
            session_id: Chat session ID
            language: Target language
        
        Returns:
            Complete prompt for AI
        """
        # Get recent chat history
        history = self.chat_history.get(session_id, [])
        recent_history = history[-10:] if len(history) > 10 else history  # Last 10 messages
        
        # Build conversation context
        context_parts = []
        
        # Add system prompt based on language
        system_prompts = {
            "en": """You are Vidhya, a friendly and helpful AI learning assistant for students. 
            Your goal is to provide clear, simple, and understandable answers to educational questions.
            Always explain concepts in a way that's easy to understand.
            Be encouraging and supportive in your responses.
            If you don't know something, admit it honestly and suggest where the student might find the answer.""",
            
            "hi": """आप विद्या हैं, छात्रों के लिए एक मैत्रीपूर्ण और सहायक AI लर्निंग सहायक।
            आपका लक्ष्य शैक्षणिक प्रश्नों के स्पष्ट, सरल और समझने योग्य उत्तर प्रदान करना है।
            हमेशा अवधारणाओं को ऐसे तरीके से समझाएं जो समझना आसान हो।
            अपनी प्रतिक्रियाओं में प्रोत्साहित करने वाले और सहायक हों।
            यदि आप कुछ नहीं जानते हैं, तो ईमानदारी से स्वीकार करें और छात्र को उत्तर कहां मिल सकता है इसका सुझाव दें।""",
            
            "bn": """আপনি বিদ্যা, শিক্ষার্থীদের জন্য একটি বন্ধুত্বপূর্ণ এবং সহায়ক AI লার্নিং সহায়ক।
            আপনার লক্ষ্য শিক্ষাগত প্রশ্নের স্পষ্ট, সহজ এবং বোধগম্য উত্তর প্রদান করা।
            সর্বদা ধারণাগুলিকে এমনভাবে ব্যাখ্যা করুন যা বোঝা সহজ।
            আপনার প্রতিক্রিয়ায় উৎসাহজনক এবং সহায়ক হন।
            যদি আপনি কিছু জানেন না, তবে সৎভাবে স্বীকার করুন এবং শিক্ষার্থীকে উত্তর কোথায় পেতে পারে তার পরামর্শ দিন।"""
        }
        
        system_prompt = system_prompts.get(language, system_prompts["en"])
        context_parts.append(f"System: {system_prompt}")
        
        # Add conversation history
        for msg in recent_history:
            role = "User" if msg.role == "user" else "Vidhya"
            context_parts.append(f"{role}: {msg.content}")
        
        # Add current message
        context_parts.append(f"User: {message}")
        context_parts.append("Vidhya:")
        
        return "\n\n".join(context_parts)
    
    async def _generate_response(
        self,
        prompt: str,
        user_id: str,
        language: str
    ) -> str:
        """
        Generate AI response using Gemini.
        
        Args:
            prompt: Complete prompt
            user_id: User ID
            language: Target language
        
        Returns:
            Generated response
        """
        try:
            # Use unified service for generation with tracking
            result = await self.unified_service.generate_content(
                prompt=prompt,
                user_id=user_id,
                interaction_type="vidhya_chat",
                metadata={
                    "agent": "vidhya",
                    "language": language
                }
            )
            
            response = result.get("content", "")
            
            # Clean up response (remove any "Vidhya:" prefix if present)
            if response.startswith("Vidhya:"):
                response = response[7:].strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            raise
    
    def _save_session_to_db(self, session: ChatSession):
        """Save chat session to Firestore."""
        try:
            if not self.db:
                return
                
            doc_ref = self.db.collection(self.sessions_collection).document(session.session_id)
            doc_ref.set({
                "session_id": session.session_id,
                "user_id": session.user_id,
                "student_id": session.student_id,
                "title": session.title,
                "language": session.language,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "message_count": session.message_count,
                "metadata": session.metadata
            })
            logger.debug(f"Saved session to database: {session.session_id}")
        except Exception as e:
            logger.error(f"Failed to save session to database: {e}")
    
    def _update_session_in_db(self, session: ChatSession):
        """Update chat session in Firestore."""
        try:
            if not self.db:
                return
                
            doc_ref = self.db.collection(self.sessions_collection).document(session.session_id)
            doc_ref.update({
                "updated_at": session.updated_at,
                "message_count": session.message_count,
                "title": session.title
            })
            logger.debug(f"Updated session in database: {session.session_id}")
        except Exception as e:
            logger.error(f"Failed to update session in database: {e}")
    
    def _save_message_to_db(self, message: ChatMessage):
        """Save chat message to Firestore."""
        try:
            if not self.db:
                return
                
            doc_ref = self.db.collection(self.messages_collection).document(message.message_id)
            doc_ref.set({
                "message_id": message.message_id,
                "user_id": message.user_id,
                "session_id": message.session_id,
                "role": message.role,
                "content": message.content,
                "language": message.language,
                "timestamp": message.timestamp,
                "metadata": message.metadata
            })
            logger.debug(f"Saved message to database: {message.message_id}")
        except Exception as e:
            logger.error(f"Failed to save message to database: {e}")
    
    async def _load_sessions_from_db(self, user_id: str):
        """Load user sessions from Firestore."""
        try:
            if not self.db:
                return
                
            sessions_query = self.db.collection(self.sessions_collection)\
                .where("user_id", "==", user_id)\
                .order_by("updated_at", direction="DESCENDING")\
                .limit(20)
            
            sessions = []
            async for doc in sessions_query.stream():
                data = doc.to_dict()
                session = ChatSession(
                    session_id=data["session_id"],
                    user_id=data["user_id"],
                    student_id=data.get("student_id"),
                    title=data.get("title"),
                    language=data.get("language", DEFAULT_LANGUAGE),
                    created_at=data["created_at"],
                    updated_at=data["updated_at"],
                    message_count=data.get("message_count", 0),
                    metadata=data.get("metadata", {})
                )
                sessions.append(session)
                self.chat_sessions[session.session_id] = session
            
            logger.info(f"Loaded {len(sessions)} sessions from database for user: {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to load sessions from database: {e}")
    
    async def _load_messages_from_db(self, session_id: str):
        """Load chat messages from Firestore."""
        try:
            if not self.db:
                return
                
            messages_query = self.db.collection(self.messages_collection)\
                .where("session_id", "==", session_id)\
                .order_by("timestamp", direction="ASCENDING")\
                .limit(50)
            
            messages = []
            async for doc in messages_query.stream():
                data = doc.to_dict()
                message = ChatMessage(
                    message_id=data["message_id"],
                    user_id=data["user_id"],
                    session_id=data["session_id"],
                    role=data["role"],
                    content=data["content"],
                    language=data.get("language", DEFAULT_LANGUAGE),
                    timestamp=data["timestamp"],
                    metadata=data.get("metadata", {})
                )
                messages.append(message)
            
            self.chat_history[session_id] = messages
            logger.info(f"Loaded {len(messages)} messages from database for session: {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to load messages from database: {e}")


# Singleton instance
_vidhya_service: Optional[VidhyaService] = None


def get_vidhya_service() -> VidhyaService:
    """
    Get or create singleton VidhyaService instance.
    
    Returns:
        VidhyaService instance
    """
    global _vidhya_service
    
    if _vidhya_service is None:
        logger.info("Creating new VidhyaService singleton instance")
        _vidhya_service = VidhyaService()
    
    return _vidhya_service


# Module initialization
logger.info("Vidhya AI Agent Service module loaded")
logger.info(f"Supported languages: {list(SUPPORTED_LANGUAGES.keys())}")