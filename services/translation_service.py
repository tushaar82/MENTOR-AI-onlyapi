"""
Translation Service

This module provides translation functionality for the Mentor AI EdTech Platform.
It handles loading translations, managing language preferences, and providing
translated text for backend responses.

Author: Mentor AI Team
Version: 1.0.0
"""

import json
import os
import logging
from typing import Dict, Any, Optional, List
from functools import lru_cache
from pathlib import Path

from config.language_config import (
    language_config,
    validate_language_code,
    LanguageConfig
)

# Configure logging
logger = logging.getLogger(__name__)

class TranslationService:
    """
    Translation service for backend internationalization.
    
    This service manages translations for all backend messages, API responses,
    and system notifications. It supports fallback to default language when
    translations are missing.
    """
    
    def __init__(self, translations_dir: str = "data/translations/backend"):
        """
        Initialize translation service.
        
        Args:
            translations_dir: Directory containing translation files
        """
        self.translations_dir = Path(translations_dir)
        self._translations: Dict[str, Dict[str, str]] = {}
        self._load_translations()
        
        logger.info(f"Translation service initialized with {len(self._translations)} languages")
        logger.info(f"Supported languages: {list(self._translations.keys())}")
    
    def _load_translations(self):
        """Load all translation files from the translations directory."""
        try:
            # Ensure translations directory exists
            if not self.translations_dir.exists():
                self.translations_dir.mkdir(parents=True, exist_ok=True)
                logger.warning(f"Created translations directory: {self.translations_dir}")
                return
            
            # Load translation files for each supported language
            for lang_code in LanguageConfig.SUPPORTED_LANGUAGES.keys():
                translation_file = self.translations_dir / f"{lang_code}.json"
                
                if translation_file.exists():
                    with open(translation_file, 'r', encoding='utf-8') as f:
                        self._translations[lang_code] = json.load(f)
                    logger.info(f"Loaded translations for {lang_code}: {len(self._translations[lang_code])} keys")
                else:
                    logger.warning(f"Translation file not found: {translation_file}")
                    # Create empty translations dict to prevent errors
                    self._translations[lang_code] = {}
                    
        except Exception as e:
            logger.error(f"Failed to load translations: {e}")
            self._translations = {lang_code: {} for lang_code in LanguageConfig.SUPPORTED_LANGUAGES.keys()}
    
    @lru_cache(maxsize=1024)
    def translate(
        self,
        key: str,
        language_code: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Get translated text for a given key.
        
        Args:
            key: Translation key (e.g., 'auth.login.success')
            language_code: Target language code (optional, uses default if not provided)
            **kwargs: Variables for string interpolation
        
        Returns:
            Translated text
        """
        # Validate and normalize language code
        target_lang = validate_language_code(language_code or LanguageConfig.DEFAULT_LANGUAGE)
        
        # Try to get translation in target language
        translation = self._get_translation_value(key, target_lang)
        
        # If not found, try fallback language
        if translation is None and target_lang != LanguageConfig.FALLBACK_LANGUAGE:
            translation = self._get_translation_value(key, LanguageConfig.FALLBACK_LANGUAGE)
            if translation:
                logger.debug(f"Used fallback translation for key '{key}' in {LanguageConfig.FALLBACK_LANGUAGE}")
        
        # If still not found, return the key itself
        if translation is None:
            logger.warning(f"Translation not found for key '{key}' in any language")
            translation = key
        
        # Apply string interpolation if variables are provided
        try:
            if kwargs:
                translation = translation.format(**kwargs)
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to interpolate translation for key '{key}': {e}")
        
        return translation
    
    def _get_translation_value(self, key: str, language_code: str) -> Optional[str]:
        """
        Get translation value for a specific key and language.
        
        Args:
            key: Translation key (supports dot notation)
            language_code: Language code
        
        Returns:
            Translation value or None if not found
        """
        if language_code not in self._translations:
            return None
        
        # Navigate through nested dictionary using dot notation
        current = self._translations[language_code]
        keys = key.split('.')
        
        try:
            for k in keys:
                current = current[k]
            return current
        except (KeyError, TypeError):
            return None
    
    def get_translations_dict(
        self,
        language_code: Optional[str] = None,
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get all translations for a language or specific namespace.
        
        Args:
            language_code: Language code (optional, uses default if not provided)
            namespace: Namespace prefix (e.g., 'auth', 'dashboard')
        
        Returns:
            Dictionary of translations
        """
        target_lang = validate_language_code(language_code or LanguageConfig.DEFAULT_LANGUAGE)
        
        if target_lang not in self._translations:
            return {}
        
        translations = self._translations[target_lang]
        
        # Filter by namespace if provided
        if namespace:
            namespace_parts = namespace.split('.')
            result = translations
            for part in namespace_parts:
                if isinstance(result, dict) and part in result:
                    result = result[part]
                else:
                    return {}
            return result if isinstance(result, dict) else {}
        
        return translations.copy()
    
    def translate_error_message(
        self,
        error_key: str,
        language_code: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a translated error response.
        
        Args:
            error_key: Error message key
            language_code: Language code
            **kwargs: Variables for string interpolation
        
        Returns:
            Formatted error response dictionary
        """
        translated_message = self.translate(f"errors.{error_key}", language_code, **kwargs)
        
        return {
            "success": False,
            "error": {
                "code": error_key,
                "message": translated_message,
                "language": validate_language_code(language_code or LanguageConfig.DEFAULT_LANGUAGE)
            }
        }
    
    def translate_success_message(
        self,
        message_key: str,
        data: Optional[Dict[str, Any]] = None,
        language_code: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a translated success response.
        
        Args:
            message_key: Success message key
            data: Additional data to include
            language_code: Language code
            **kwargs: Variables for string interpolation
        
        Returns:
            Formatted success response dictionary
        """
        translated_message = self.translate(f"success.{message_key}", language_code, **kwargs)
        
        response = {
            "success": True,
            "message": translated_message,
            "language": validate_language_code(language_code or LanguageConfig.DEFAULT_LANGUAGE)
        }
        
        if data:
            response["data"] = data
        
        return response
    
    def get_language_info_response(self, language_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Get language information for API responses.
        
        Args:
            language_code: Language code to get info for
        
        Returns:
            Language information dictionary
        """
        target_lang = validate_language_code(language_code or LanguageConfig.DEFAULT_LANGUAGE)
        lang_info = language_config.get_language_info(target_lang)
        
        if not lang_info:
            return {}
        
        return {
            "code": lang_info.code,
            "name": lang_info.name,
            "native_name": lang_info.native_name,
            "rtl": lang_info.rtl,
            "flag_emoji": lang_info.flag_emoji,
            "date_format": lang_info.date_format,
            "time_format": lang_info.time_format
        }
    
    def reload_translations(self):
        """Reload all translation files."""
        logger.info("Reloading translations...")
        self._translations.clear()
        self._load_translations()
        # Clear the LRU cache
        self.translate.cache_clear()
        logger.info("Translations reloaded successfully")
    
    def get_available_languages(self) -> List[Dict[str, Any]]:
        """
        Get list of available languages with their info.
        
        Returns:
            List of language dictionaries
        """
        return language_config.get_language_list()
    
    def is_language_supported(self, language_code: str) -> bool:
        """
        Check if a language is supported.
        
        Args:
            language_code: Language code to check
        
        Returns:
            True if supported, False otherwise
        """
        return language_config.is_supported(language_code)


# Global translation service instance
_translation_service: Optional[TranslationService] = None


def get_translation_service() -> TranslationService:
    """
    Get or create singleton TranslationService instance.
    
    Returns:
        TranslationService instance
    """
    global _translation_service
    
    if _translation_service is None:
        _translation_service = TranslationService()
    
    return _translation_service


# Convenience functions for common use cases
def t(key: str, language_code: Optional[str] = None, **kwargs) -> str:
    """
    Translate a text key.
    
    Args:
        key: Translation key
        language_code: Language code
        **kwargs: Variables for string interpolation
    
    Returns:
        Translated text
    """
    return get_translation_service().translate(key, language_code, **kwargs)


def translate_error(error_key: str, language_code: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Create a translated error response.
    
    Args:
        error_key: Error message key
        language_code: Language code
        **kwargs: Variables for string interpolation
    
    Returns:
        Formatted error response
    """
    return get_translation_service().translate_error_message(error_key, language_code, **kwargs)


def translate_success(message_key: str, data: Optional[Dict[str, Any]] = None, 
                     language_code: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Create a translated success response.
    
    Args:
        message_key: Success message key
        data: Additional data to include
        language_code: Language code
        **kwargs: Variables for string interpolation
    
    Returns:
        Formatted success response
    """
    return get_translation_service().translate_success_message(message_key, data, language_code, **kwargs)


# Module initialization
logger.info("Translation Service module loaded")