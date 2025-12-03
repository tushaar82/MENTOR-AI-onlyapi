/**
 * Internationalization Configuration
 * 
 * This module defines language configuration for the frontend application.
 * It includes supported languages, default language settings, and utility functions.
 */

export type Language = {
  code: string;
  name: string;
  native_name: string;
  flag: string;
  rtl: boolean;
};

// Supported languages with their metadata
export const SUPPORTED_LANGUAGES: Language[] = [
  {
    code: "en",
    name: "English",
    native_name: "English",
    flag: "🇺🇸",
    rtl: false,
  },
  {
    code: "hi",
    name: "Hindi",
    native_name: "हिन्दी",
    flag: "🇮🇳",
    rtl: false,
  },
  {
    code: "bn",
    name: "Bengali",
    native_name: "বাংলা",
    flag: "🇧🇩",
    rtl: false,
  },
  {
    code: "te",
    name: "Telugu",
    native_name: "తెలుగు",
    flag: "🇮🇳",
    rtl: false,
  },
  {
    code: "ta",
    name: "Tamil",
    native_name: "தமிழ்",
    flag: "🇮🇳",
    rtl: false,
  },
  {
    code: "mr",
    name: "Marathi",
    native_name: "मराठी",
    flag: "🇮🇳",
    rtl: false,
  },
  {
    code: "gu",
    name: "Gujarati",
    native_name: "ગુજરાતી",
    flag: "🇮🇳",
    rtl: false,
  },
  {
    code: "kn",
    name: "Kannada",
    native_name: "ಕನ್ನಡ",
    flag: "🇮🇳",
    rtl: false,
  },
  {
    code: "ml",
    name: "Malayalam",
    native_name: "മലയാളം",
    flag: "🇮🇳",
    rtl: false,
  },
  {
    code: "pa",
    name: "Punjabi",
    native_name: "ਪੰਜਾਬੀ",
    flag: "🇮🇳",
    rtl: false,
  },
];

// Default language
export const DEFAULT_LANGUAGE = "en";

// Fallback language (used when translation is missing)
export const FALLBACK_LANGUAGE = "en";

// Local storage keys
export const LANGUAGE_STORAGE_KEY = "preferredLanguage";

// RTL languages list
export const RTL_LANGUAGES = ["ar", "he", "ur", "fa"];

/**
 * Get all supported languages.
 * 
 * @returns Array of supported languages
 */
export function getLanguageList(): Language[] {
  return SUPPORTED_LANGUAGES;
}

/**
 * Get language information for a specific language code.
 * 
 * @param languageCode Language code (e.g., 'en', 'hi')
 * @returns Language object or undefined if not found
 */
export function getLanguageInfo(languageCode: string): Language | undefined {
  return SUPPORTED_LANGUAGES.find(lang => lang.code === languageCode);
}

/**
 * Check if a language is supported.
 * 
 * @param languageCode Language code to check
 * @returns True if supported, false otherwise
 */
export function isSupportedLanguage(languageCode: string): boolean {
  return SUPPORTED_LANGUAGES.some(lang => lang.code === languageCode);
}

/**
 * Get mapping of language codes to native names.
 * 
 * @returns Dictionary mapping language codes to native names
 */
export function getNativeNames(): Record<string, string> {
  const result: Record<string, string> = {};
  SUPPORTED_LANGUAGES.forEach(lang => {
    result[lang.code] = lang.native_name;
  });
  return result;
}

/**
 * Get list of RTL (right-to-left) languages.
 * 
 * @returns Array of RTL language codes
 */
export function getRTLLanguages(): string[] {
  return RTL_LANGUAGES;
}

/**
 * Check if a language is RTL.
 * 
 * @param languageCode Language code to check
 * @returns True if RTL, false otherwise
 */
export function isRTLLanguage(languageCode: string): boolean {
  return RTL_LANGUAGES.includes(languageCode);
}

/**
 * Validate and normalize language code.
 * 
 * @param languageCode Language code to validate
 * @returns Valid language code (fallback to default if invalid)
 */
export function validateLanguageCode(languageCode: string): string {
  if (!languageCode || !isSupportedLanguage(languageCode)) {
    return DEFAULT_LANGUAGE;
  }
  return languageCode.toLowerCase();
}

/**
 * Get browser language preference.
 * 
 * @returns Browser language code or default language
 */
export function getBrowserLanguage(): string {
  if (typeof navigator === 'undefined') {
    return DEFAULT_LANGUAGE;
  }
  
  const browserLang = navigator.language.split('-')[0];
  return validateLanguageCode(browserLang);
}

/**
 * Format date according to language preferences.
 * 
 * @param date Date to format
 * @param languageCode Language code
 * @returns Formatted date string
 */
export function formatDate(date: Date, languageCode: string = DEFAULT_LANGUAGE): string {
  const lang = validateLanguageCode(languageCode);
  
  try {
    return new Intl.DateTimeFormat(lang, {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    }).format(date);
  } catch (error) {
    console.warn(`Failed to format date for language ${lang}:`, error);
    return date.toLocaleDateString();
  }
}

/**
 * Format time according to language preferences.
 * 
 * @param date Date to format
 * @param languageCode Language code
 * @returns Formatted time string
 */
export function formatTime(date: Date, languageCode: string = DEFAULT_LANGUAGE): string {
  const lang = validateLanguageCode(languageCode);
  
  try {
    return new Intl.DateTimeFormat(lang, {
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  } catch (error) {
    console.warn(`Failed to format time for language ${lang}:`, error);
    return date.toLocaleTimeString();
  }
}

/**
 * Format number according to language preferences.
 * 
 * @param number Number to format
 * @param languageCode Language code
 * @returns Formatted number string
 */
export function formatNumber(number: number, languageCode: string = DEFAULT_LANGUAGE): string {
  const lang = validateLanguageCode(languageCode);
  
  try {
    return new Intl.NumberFormat(lang).format(number);
  } catch (error) {
    console.warn(`Failed to format number for language ${lang}:`, error);
    return number.toString();
  }
}

/**
 * Get text direction for a language.
 * 
 * @param languageCode Language code
 * @returns 'rtl' or 'ltr'
 */
export function getTextDirection(languageCode: string): 'rtl' | 'ltr' {
  return isRTLLanguage(languageCode) ? 'rtl' : 'ltr';
}