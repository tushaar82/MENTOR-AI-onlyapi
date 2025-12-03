"""
Language Router

This router handles all language-related API endpoints for the Mentor AI EdTech Platform.
It provides endpoints for:
- Getting supported languages
- Getting translations
- Setting user language preference
- Getting language-specific content

Author: Mentor AI Team
Version: 1.0.0
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from services.translation_service import get_translation_service
from config.language_config import (
    get_language_list,
    get_language_info,
    validate_language_code,
    LanguageConfig
)
from middleware.auth_middleware import get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/language", tags=["Language Management"])


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class LanguagePreferenceRequest(BaseModel):
    """Request model for setting language preference."""
    language: str

class LanguagePreferenceResponse(BaseModel):
    """Response model for language preference."""
    success: bool
    language: str
    message: str


# ============================================================================
# LANGUAGE ENDPOINTS
# ============================================================================

@router.get("/supported")
async def get_supported_languages():
    """
    Get list of all supported languages.
    
    Returns:
        List of supported languages with their metadata
    """
    try:
        languages = get_language_list()
        
        return {
            "success": True,
            "data": {
                "languages": languages,
                "count": len(languages),
                "default": LanguageConfig.DEFAULT_LANGUAGE
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get supported languages: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve supported languages")


@router.get("/info/{language_code}")
async def get_language_info_endpoint(language_code: str):
    """
    Get detailed information about a specific language.
    
    Args:
        language_code: Language code (e.g., 'en', 'hi')
    
    Returns:
        Language information
    """
    try:
        # Validate language code
        validated_code = validate_language_code(language_code)
        
        # Get language info
        lang_info = get_language_info(validated_code)
        
        if not lang_info:
            raise HTTPException(status_code=404, detail="Language not found")
        
        return {
            "success": True,
            "data": {
                "code": lang_info.code,
                "name": lang_info.name,
                "native_name": lang_info.native_name,
                "rtl": lang_info.rtl,
                "flag_emoji": lang_info.flag_emoji,
                "date_format": lang_info.date_format,
                "time_format": lang_info.time_format
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get language info: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve language information")


@router.get("/translations/{language_code}")
async def get_translations(
    language_code: str,
    namespace: Optional[str] = Query(None, description="Namespace to filter translations (e.g., 'auth', 'dashboard')"),
    current_user: str = Depends(get_current_user)
):
    """
    Get translations for a specific language.
    
    Args:
        language_code: Language code
        namespace: Optional namespace filter
        current_user: Authenticated user ID
    
    Returns:
        Translations dictionary
    """
    try:
        # Validate language code
        validated_code = validate_language_code(language_code)
        
        # Get translation service
        translation_service = get_translation_service()
        
        # Get translations
        translations = translation_service.get_translations_dict(
            language_code=validated_code,
            namespace=namespace
        )
        
        return {
            "success": True,
            "data": {
                "language": validated_code,
                "namespace": namespace,
                "translations": translations,
                "count": len(translations) if isinstance(translations, dict) else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get translations: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve translations")


@router.post("/preference")
async def set_language_preference(
    request: LanguagePreferenceRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Set user's preferred language.
    
    Args:
        request: Language preference request
        current_user: Authenticated user ID
    
    Returns:
        Success response
    """
    try:
        # Validate language code
        validated_code = validate_language_code(request.language)
        
        # Get translation service
        translation_service = get_translation_service()
        
        # Here you would typically save this to user preferences in database
        # For now, we'll just return a success response
        # TODO: Implement user preference storage in database
        
        logger.info(f"User {current_user} set language preference to {validated_code}")
        
        return {
            "success": True,
            "data": {
                "language": validated_code,
                "message": translation_service.translate(
                    "success.settings_saved",
                    language_code=validated_code
                )
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to set language preference: {e}")
        raise HTTPException(status_code=500, detail="Failed to set language preference")


@router.get("/preference")
async def get_language_preference(current_user: str = Depends(get_current_user)):
    """
    Get user's preferred language.
    
    Args:
        current_user: Authenticated user ID
    
    Returns:
        User's language preference
    """
    try:
        # Here you would typically get this from user preferences in database
        # For now, we'll return the default language
        # TODO: Implement user preference retrieval from database
        
        user_language = LanguageConfig.DEFAULT_LANGUAGE  # Default fallback
        
        # Get language info
        lang_info = get_language_info(user_language)
        
        return {
            "success": True,
            "data": {
                "language": user_language,
                "language_info": {
                    "code": lang_info.code,
                    "name": lang_info.name,
                    "native_name": lang_info.native_name,
                    "flag_emoji": lang_info.flag_emoji
                } if lang_info else None
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get language preference: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve language preference")


@router.get("/translate")
async def translate_text(
    key: str = Query(..., description="Translation key"),
    language_code: Optional[str] = Query(None, description="Target language code"),
    current_user: str = Depends(get_current_user)
):
    """
    Translate a specific key to the requested language.
    
    Args:
        key: Translation key (e.g., 'auth.login.title')
        language_code: Target language code (optional)
        current_user: Authenticated user ID
    
    Returns:
        Translated text
    """
    try:
        # Validate language code
        validated_code = validate_language_code(language_code) if language_code else LanguageConfig.DEFAULT_LANGUAGE
        
        # Get translation service
        translation_service = get_translation_service()
        
        # Get translation
        translated_text = translation_service.translate(
            key=key,
            language_code=validated_code
        )
        
        return {
            "success": True,
            "data": {
                "key": key,
                "language": validated_code,
                "translation": translated_text
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to translate text: {e}")
        raise HTTPException(status_code=500, detail="Failed to translate text")


@router.get("/health")
async def health_check():
    """
    Health check endpoint for language service.
    
    Returns:
        Health status
    """
    try:
        # Check translation service
        translation_service = get_translation_service()
        service_status = "healthy" if translation_service else "unhealthy"
        
        # Get supported languages count
        languages = get_language_list()
        
        return {
            "status": service_status,
            "service": "language-service",
            "timestamp": "2024-01-01T00:00:00Z",  # Would use actual timestamp
            "features": {
                "supported_languages": len(languages),
                "translation_service": translation_service is not None,
                "language_validation": True,
                "user_preferences": True  # TODO: Implement database storage
            },
            "supported_languages": [lang["code"] for lang in languages]
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "language-service",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"  # Would use actual timestamp
        }


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@router.get("/rtl")
async def get_rtl_languages():
    """
    Get list of RTL (right-to-left) languages.
    
    Returns:
        List of RTL language codes
    """
    try:
        from config.language_config import get_rtl_languages
        
        rtl_languages = get_rtl_languages()
        
        return {
            "success": True,
            "data": {
                "rtl_languages": rtl_languages,
                "count": len(rtl_languages)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get RTL languages: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve RTL languages")


@router.get("/validate/{language_code}")
async def validate_language(language_code: str):
    """
    Validate if a language code is supported.
    
    Args:
        language_code: Language code to validate
    
    Returns:
        Validation result
    """
    try:
        from config.language_config import is_supported_language
        
        is_supported = is_supported_language(language_code)
        validated_code = validate_language_code(language_code) if is_supported else None
        
        return {
            "success": True,
            "data": {
                "input_code": language_code,
                "is_supported": is_supported,
                "validated_code": validated_code,
                "is_rtl": get_language_info(validated_code).rtl if validated_code else False
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to validate language: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate language")