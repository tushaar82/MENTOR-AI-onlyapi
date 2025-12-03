'use client';

import React, { useState } from 'react';
import { Check, ChevronDown, Globe } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useLanguage, useCurrentLanguage } from '@/contexts/LanguageContext';
import { getLanguageList } from '@/lib/i18n/config';

export function LanguageSwitcher() {
  const { setLanguage, isLoading } = useLanguage();
  const { code: currentLanguage, info: currentLangInfo } = useCurrentLanguage();
  const [isOpen, setIsOpen] = useState(false);
  
  const languages = getLanguageList();

  const handleLanguageSelect = (languageCode: string) => {
    setLanguage(languageCode);
    setIsOpen(false);
  };

  const currentLanguageDisplay = currentLangInfo ? (
    <div className="flex items-center gap-2">
      <span className="text-lg">{currentLangInfo.flag}</span>
      <span className="hidden sm:inline">{currentLangInfo.native_name}</span>
    </div>
  ) : (
    <div className="flex items-center gap-2">
      <Globe className="h-4 w-4" />
      <span className="hidden sm:inline">Language</span>
    </div>
  );

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <Button 
          variant="outline" 
          size="sm" 
          disabled={isLoading}
          className="flex items-center gap-2 min-w-[140px]"
        >
          {currentLanguageDisplay}
          <ChevronDown className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      
      <DropdownMenuContent 
        className="w-56 max-h-80 overflow-y-auto"
        align="end"
        sideOffset={8}
      >
        {languages.map((language) => (
          <DropdownMenuItem
            key={language.code}
            onClick={() => handleLanguageSelect(language.code)}
            className="flex items-center gap-3 cursor-pointer hover:bg-gray-50 focus:bg-gray-50"
          >
            <div className="flex items-center gap-2 flex-1">
              <span className="text-lg">{language.flag}</span>
              <div className="flex flex-col">
                <span className="font-medium">{language.native_name}</span>
                <span className="text-xs text-gray-500">{language.name}</span>
              </div>
            </div>
            
            {language.code === currentLanguage && (
              <Check className="h-4 w-4 text-blue-600" />
            )}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

// Compact version for mobile/small screens
export function LanguageSwitcherCompact() {
  const { setLanguage, isLoading } = useLanguage();
  const { code: currentLanguage, info: currentLangInfo } = useCurrentLanguage();
  
  const languages = getLanguageList();

  const handleLanguageSelect = (languageCode: string) => {
    setLanguage(languageCode);
  };

  return (
    <div className="flex items-center gap-1">
      {languages.map((language) => (
        <Button
          key={language.code}
          variant={language.code === currentLanguage ? "default" : "outline"}
          size="sm"
          onClick={() => handleLanguageSelect(language.code)}
          disabled={isLoading}
          className="p-2 h-8 w-8"
          title={language.native_name}
        >
          <span className="text-sm">{language.flag}</span>
        </Button>
      ))}
    </div>
  );
}

// Language selector for forms/settings
export function LanguageSelector({
  value,
  onChange,
  className = "",
}: {
  value: string;
  onChange: (languageCode: string) => void;
  className?: string;
}) {
  const languages = getLanguageList();

  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className={`flex items-center gap-2 p-2 border rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 ${className}`}
    >
      {languages.map((language) => (
        <option key={language.code} value={language.code}>
          {language.flag} {language.native_name} ({language.name})
        </option>
      ))}
    </select>
  );
}