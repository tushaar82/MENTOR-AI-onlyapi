'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { getLanguageList, validateLanguageCode, DEFAULT_LANGUAGE } from '@/lib/i18n/config';

// Types
export type Language = {
  code: string;
  name: string;
  native_name: string;
  flag: string;
  rtl: boolean;
};

export type Translations = Record<string, any>;

interface LanguageContextType {
  currentLanguage: string;
  languages: Language[];
  translations: Translations;
  setLanguage: (languageCode: string) => void;
  t: (key: string, params?: Record<string, string | number>) => string;
  isRTL: boolean;
  isLoading: boolean;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

interface LanguageProviderProps {
  children: ReactNode;
}

export function LanguageProvider({ children }: LanguageProviderProps) {
  const [currentLanguage, setCurrentLanguageState] = useState<string>(DEFAULT_LANGUAGE);
  const [translations, setTranslations] = useState<Translations>({});
  const [isLoading, setIsLoading] = useState<boolean>(true);
  
  const languages = getLanguageList();

  // Load translations for a specific language
  const loadTranslations = async (languageCode: string) => {
    try {
      setIsLoading(true);
      
      // Validate language code
      const validatedCode = validateLanguageCode(languageCode);
      
      // Load translations from API
      const response = await fetch(`/api/language/translations/${validatedCode}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setTranslations(data.data.translations);
          setCurrentLanguageState(validatedCode);
          
          // Save to localStorage
          localStorage.setItem('preferredLanguage', validatedCode);
          
          // Update HTML lang attribute
          document.documentElement.lang = validatedCode;
          
          // Update RTL direction
          const isRTL = languages.find((lang: Language) => lang.code === validatedCode)?.rtl || false;
          document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
        }
      } else {
        console.error('Failed to load translations:', response.statusText);
        // Fallback to default language
        if (validatedCode !== DEFAULT_LANGUAGE) {
          await loadTranslations(DEFAULT_LANGUAGE);
        }
      }
    } catch (error) {
      console.error('Error loading translations:', error);
      // Fallback to default language
      if (languageCode !== DEFAULT_LANGUAGE) {
        await loadTranslations(DEFAULT_LANGUAGE);
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Translation function
  const t = (key: string, params?: Record<string, string | number>): string => {
    const keys = key.split('.');
    let value: any = translations;
    
    // Navigate through nested object
    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        // Key not found, return the key itself
        return key;
      }
    }
    
    // If value is not a string, return it as is
    if (typeof value !== 'string') {
      return key;
    }
    
    // Replace parameters in the translation string
    if (params) {
      return value.replace(/\{(\w+)\}/g, (match: string, param: string) => {
        return params[param]?.toString() || match;
      });
    }
    
    return value;
  };

  // Set language function
  const setLanguage = async (languageCode: string) => {
    if (languageCode !== currentLanguage) {
      await loadTranslations(languageCode);
    }
  };

  // Check if current language is RTL
  const isRTL = languages.find((lang: Language) => lang.code === currentLanguage)?.rtl || false;

  // Initialize language on mount
  useEffect(() => {
    const initializeLanguage = async () => {
      // Get saved language from localStorage or browser preference
      const savedLanguage = localStorage.getItem('preferredLanguage');
      const browserLanguage = navigator.language.split('-')[0];
      
      // Priority: saved > browser > default
      const initialLanguage = savedLanguage || 
                           (validateLanguageCode(browserLanguage) ? browserLanguage : DEFAULT_LANGUAGE);
      
      await loadTranslations(initialLanguage);
    };

    initializeLanguage();
  }, []);

  const value: LanguageContextType = {
    currentLanguage,
    languages,
    translations,
    setLanguage,
    t,
    isRTL,
    isLoading,
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage(): LanguageContextType {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}

// Hook for translation function only
export function useTranslation() {
  const { t } = useLanguage();
  return { t };
}

// Hook for current language info
export function useCurrentLanguage() {
  const { currentLanguage, languages, isRTL } = useLanguage();
  const currentLangInfo = languages.find(lang => lang.code === currentLanguage);
  
  return {
    code: currentLanguage,
    info: currentLangInfo,
    isRTL,
  };
}