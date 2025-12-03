"""
Language Configuration Module

This module defines the language configuration for the Mentor AI EdTech Platform.
It includes supported languages, default language settings, and language metadata.

Author: Mentor AI Team
Version: 1.0.0
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import json
import os

@dataclass
class LanguageInfo:
    """Information about a supported language."""
    code: str
    name: str
    native_name: str
    rtl: bool = False
    flag_emoji: str = ""
    date_format: str = "%Y-%m-%d"
    time_format: str = "%H:%M:%S"

class LanguageConfig:
    """
    Language configuration manager for the Mentor AI Platform.
    
    This class manages all language-related settings including:
    - Supported languages
    - Default language
    - Language metadata
    - Translation file paths
    """
    
    # Supported languages with their metadata
    SUPPORTED_LANGUAGES: Dict[str, LanguageInfo] = {
        "en": LanguageInfo(
            code="en",
            name="English",
            native_name="English",
            rtl=False,
            flag_emoji="🇺🇸",
            date_format="%m/%d/%Y",
            time_format="%I:%M %p"
        ),
        "hi": LanguageInfo(
            code="hi",
            name="Hindi",
            native_name="हिन्दी",
            rtl=False,
            flag_emoji="🇮🇳",
            date_format="%d/%m/%Y",
            time_format="%I:%M %p"
        ),
        "bn": LanguageInfo(
            code="bn",
            name="Bengali",
            native_name="বাংলা",
            rtl=False,
            flag_emoji="🇧🇩",
            date_format="%d/%m/%Y",
            time_format="%I:%M %p"
        ),
        "te": LanguageInfo(
            code="te",
            name="Telugu",
            native_name="తెలుగు",
            rtl=False,
            flag_emoji="🇮🇳",
            date_format="%d/%m/%Y",
            time_format="%I:%M %p"
        ),
        "ta": LanguageInfo(
            code="ta",
            name="Tamil",
            native_name="தமிழ்",
            rtl=False,
            flag_emoji="🇮🇳",
            date_format="%d/%m/%Y",
            time_format="%I:%M %p"
        ),
        "mr": LanguageInfo(
            code="mr",
            name="Marathi",
            native_name="मराठी",
            rtl=False,
            flag_emoji="🇮🇳",
            date_format="%d/%m/%Y",
            time_format="%I:%M %p"
        ),
        "gu": LanguageInfo(
            code="gu",
            name="Gujarati",
            native_name="ગુજરાતી",
            rtl=False,
            flag_emoji="🇮🇳",
            date_format="%d/%m/%Y",
            time_format="%I:%M %p"
        ),
        "kn": LanguageInfo(
            code="kn",
            name="Kannada",
            native_name="ಕನ್ನಡ",
            rtl=False,
            flag_emoji="🇮🇳",
            date_format="%d/%m/%Y",
            time_format="%I:%M %p"
        ),
        "ml": LanguageInfo(
            code="ml",
            name="Malayalam",
            native_name="മലയാളം",
            rtl=False,
            flag_emoji="🇮🇳",
            date_format="%d/%m/%Y",
            time_format="%I:%M %p"
        ),
        "pa": LanguageInfo(
            code="pa",
            name="Punjabi",
            native_name="ਪੰਜਾਬੀ",
            rtl=False,
            flag_emoji="🇮🇳",
            date_format="%d/%m/%Y",
            time_format="%I:%M %p"
        )
    }
    
    # Default language
    DEFAULT_LANGUAGE = "en"
    
    # Fallback language (used when translation is missing)
    FALLBACK_LANGUAGE = "en"
    
    # Translation file paths
    TRANSLATIONS_DIR = "data/translations"
    BACKEND_TRANSLATIONS_DIR = "data/translations/backend"
    FRONTEND_TRANSLATIONS_DIR = "data/translations/frontend"
    
    @classmethod
    def get_supported_languages(cls) -> Dict[str, LanguageInfo]:
        """
        Get all supported languages.
        
        Returns:
            Dictionary mapping language codes to LanguageInfo objects
        """
        return cls.SUPPORTED_LANGUAGES.copy()
    
    @classmethod
    def get_language_info(cls, language_code: str) -> Optional[LanguageInfo]:
        """
        Get language information for a specific language code.
        
        Args:
            language_code: Language code (e.g., 'en', 'hi')
        
        Returns:
            LanguageInfo object or None if not found
        """
        return cls.SUPPORTED_LANGUAGES.get(language_code)
    
    @classmethod
    def is_supported(cls, language_code: str) -> bool:
        """
        Check if a language is supported.
        
        Args:
            language_code: Language code to check
        
        Returns:
            True if supported, False otherwise
        """
        return language_code in cls.SUPPORTED_LANGUAGES
    
    @classmethod
    def get_native_names(cls) -> Dict[str, str]:
        """
        Get mapping of language codes to native names.
        
        Returns:
            Dictionary mapping language codes to native names
        """
        return {code: info.native_name for code, info in cls.SUPPORTED_LANGUAGES.items()}
    
    @classmethod
    def get_language_list(cls) -> List[Dict[str, str]]:
        """
        Get list of languages for dropdown/select components.
        
        Returns:
            List of dictionaries with language info
        """
        return [
            {
                "code": code,
                "name": info.name,
                "native_name": info.native_name,
                "flag": info.flag_emoji,
                "rtl": info.rtl
            }
            for code, info in cls.SUPPORTED_LANGUAGES.items()
        ]
    
    @classmethod
    def get_rtl_languages(cls) -> List[str]:
        """
        Get list of RTL (right-to-left) languages.
        
        Returns:
            List of RTL language codes
        """
        return [code for code, info in cls.SUPPORTED_LANGUAGES.items() if info.rtl]
    
    @classmethod
    def is_rtl_language(cls, language_code: str) -> bool:
        """
        Check if a language is RTL.
        
        Args:
            language_code: Language code to check
        
        Returns:
            True if RTL, False otherwise
        """
        info = cls.SUPPORTED_LANGUAGES.get(language_code)
        return info.rtl if info else False
    
    @classmethod
    def get_date_format(cls, language_code: str) -> str:
        """
        Get date format for a language.
        
        Args:
            language_code: Language code
        
        Returns:
            Date format string
        """
        info = cls.SUPPORTED_LANGUAGES.get(language_code)
        return info.date_format if info else cls.SUPPORTED_LANGUAGES[cls.DEFAULT_LANGUAGE].date_format
    
    @classmethod
    def get_time_format(cls, language_code: str) -> str:
        """
        Get time format for a language.
        
        Args:
            language_code: Language code
        
        Returns:
            Time format string
        """
        info = cls.SUPPORTED_LANGUAGES.get(language_code)
        return info.time_format if info else cls.SUPPORTED_LANGUAGES[cls.DEFAULT_LANGUAGE].time_format
    
    @classmethod
    def validate_language_code(cls, language_code: str) -> str:
        """
        Validate and normalize language code.
        
        Args:
            language_code: Language code to validate
        
        Returns:
            Valid language code (fallback to default if invalid)
        """
        if not language_code or not cls.is_supported(language_code):
            return cls.DEFAULT_LANGUAGE
        return language_code.lower()


# Global language configuration instance
language_config = LanguageConfig()

# Export commonly used functions
get_supported_languages = language_config.get_supported_languages
get_language_info = language_config.get_language_info
is_supported_language = language_config.is_supported
get_language_list = language_config.get_language_list
is_rtl_language = language_config.is_rtl_language
validate_language_code = language_config.validate_language_code