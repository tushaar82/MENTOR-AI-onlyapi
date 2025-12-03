"""
Language Middleware

This middleware handles language detection and preference management for the Mentor AI application.
It extracts language from requests and makes it available throughout the application.
"""

import logging
from typing import Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from services.translation_service import get_translation_service
from config.language_config import LanguageConfig

# Configure logging
logger = logging.getLogger(__name__)


class LanguageMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle language detection and preference management.
    
    This middleware:
    1. Detects language from request headers, query parameters, or user preferences
    2. Validates the language is supported
    3. Makes the language available throughout the application
    4. Updates user language preference when specified
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Process the request and add language context.
        
        Args:
            request: The incoming HTTP request
            call_next: The next middleware in the chain
            
        Returns:
            The response from the next middleware
        """
        try:
            # Extract language from various sources in order of priority
            language = self._extract_language(request)
            
            # Validate language is supported
            if language not in LanguageConfig.SUPPORTED_LANGUAGES:
                logger.warning(f"Unsupported language '{language}', falling back to default '{LanguageConfig.DEFAULT_LANGUAGE}'")
                language = LanguageConfig.DEFAULT_LANGUAGE
            
            # Store language in request state for use in endpoints
            request.state.language = language
            
            # Get translation service for this language
            translation_service = get_translation_service()
            if translation_service:
                translations = translation_service.get_translations(language)
                request.state.translations = translations
            
            # Process the request
            response = await call_next(request)
            
            # Add language header to response for client reference
            if hasattr(response, "headers"):
                response.headers["X-Language"] = language
            
            return response
            
        except Exception as e:
            logger.error(f"Error in language middleware: {str(e)}")
            # Continue with default language if middleware fails
            request.state.language = LanguageConfig.DEFAULT_LANGUAGE
            return await call_next(request)
    
    def _extract_language(self, request: Request) -> str:
        """
        Extract language from request in order of priority:
        1. Query parameter (?lang=hi)
        2. Header (Accept-Language: hi-IN,hi;q=0.9)
        3. User preference (if authenticated)
        4. Browser language detection
        5. Default to English
        
        Args:
            request: The incoming HTTP request
            
        Returns:
            The detected language code
        """
        # 1. Check query parameter
        if "lang" in request.query_params:
            language = request.query_params["lang"]
            logger.info(f"Language from query parameter: {language}")
            return language
        
        # 2. Check Accept-Language header
        accept_language = request.headers.get("Accept-Language")
        if accept_language:
            # Parse Accept-Language header (e.g., "hi-IN,hi;q=0.9,en;q=0.8")
            language = self._parse_accept_language(accept_language)
            if language:
                logger.info(f"Language from Accept-Language header: {language}")
                return language
        
        # 3. Check user preference (if authenticated)
        # This would require authentication context, which we'll implement later
        # For now, we'll skip this step
        
        # 4. Check browser language from User-Agent or other headers
        # This is a simplified implementation
        user_agent = request.headers.get("User-Agent", "")
        browser_language = self._detect_browser_language(user_agent)
        if browser_language:
            logger.info(f"Language detected from browser: {browser_language}")
            return browser_language
        
        # 5. Default to English
        logger.info(f"Using default language: {LanguageConfig.DEFAULT_LANGUAGE}")
        return LanguageConfig.DEFAULT_LANGUAGE
    
    def _parse_accept_language(self, accept_language: str) -> Optional[str]:
        """
        Parse Accept-Language header and extract preferred language.
        
        Args:
            accept_language: The Accept-Language header value
            
        Returns:
            The language code if supported, None otherwise
        """
        try:
            # Split by comma to get multiple languages
            languages = accept_language.split(",")
            
            for lang in languages:
                # Extract language code (before semicolon)
                lang_code = lang.split(";")[0].strip()
                
                # Handle regional variants (e.g., "hi-IN" -> "hi")
                if "-" in lang_code:
                    lang_code = lang_code.split("-")[0]
                
                # Check if this language is supported
                if lang_code in LanguageConfig.SUPPORTED_LANGUAGES:
                    return lang_code
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing Accept-Language header: {str(e)}")
            return None
    
    def _detect_browser_language(self, user_agent: str) -> Optional[str]:
        """
        Detect browser language from User-Agent header.
        
        This is a simplified implementation. In production, you might want
        to use more sophisticated detection methods.
        
        Args:
            user_agent: The User-Agent header value
            
        Returns:
            The detected language code if supported, None otherwise
        """
        # This is a placeholder implementation
        # In a real scenario, you might use GeoIP or other methods
        # For now, we'll return None to rely on other detection methods
        return None


def get_language_from_request(request: Request) -> str:
    """
    Helper function to get language from request state.
    
    Args:
        request: The HTTP request object
        
    Returns:
        The language code from request state
    """
    if hasattr(request.state, "language"):
        return request.state.language
    return LanguageConfig.DEFAULT_LANGUAGE


def get_translations_from_request(request: Request) -> dict:
    """
    Helper function to get translations from request state.
    
    Args:
        request: The HTTP request object
        
    Returns:
        The translations dictionary from request state
    """
    if hasattr(request.state, "translations"):
        return request.state.translations
    return {}