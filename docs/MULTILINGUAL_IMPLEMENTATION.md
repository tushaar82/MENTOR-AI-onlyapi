# Multi-Language Support Implementation

## Overview

Mentor AI now supports 10 local Indian languages plus English, making the platform accessible to students across India in their preferred language. This implementation includes both backend API support and frontend UI internationalization.

## Supported Languages

1. **English (en)** - Default language
2. **Hindi (hi)** - हिन्दी
3. **Bengali (bn)** - বাংলা
4. **Telugu (te)** - తెలుగు
5. **Tamil (ta)** - தமிழ்
6. **Marathi (mr)** - मराठी
7. **Gujarati (gu)** - ગુજરાતી
8. **Kannada (kn)** - ಕನ್ನಡ
9. **Malayalam (ml)** - മലയാളം
10. **Punjabi (pa)** - ਪੰਜਾਬੀ

## Architecture

### Backend Implementation

#### 1. Language Configuration (`config/language_config.py`)
- Centralized language metadata management
- Language validation and information retrieval
- Support for RTL languages (future expansion)
- Date/time formatting per language

#### 2. Translation Service (`services/translation_service.py`)
- Caching system for performance
- Nested translation key support with dot notation
- Fallback mechanism to default language
- Parameter interpolation in translations

#### 3. Language Router (`routers/language_router.py`)
- RESTful API endpoints for language management
- Get supported languages: `GET /api/language/supported`
- Get translations: `GET /api/language/translations/{lang}`
- Set preferences: `POST /api/language/preference`
- Get preferences: `GET /api/language/preference`

#### 4. Language Middleware (`middleware/language_middleware.py`)
- Automatic language detection from:
  - Query parameters (`?lang=hi`)
  - HTTP headers (`Accept-Language: hi-IN`)
  - Browser language settings
- Updates user preferences in database
- Validates language support

### Frontend Implementation

#### 1. Language Configuration (`frontend/src/lib/i18n/config.ts`)
- TypeScript language definitions
- Language validation utilities
- RTL detection functions
- Language formatting helpers

#### 2. Language Context (`frontend/src/contexts/LanguageContext.tsx`)
- React context for global language state
- Translation function with parameter support
- Automatic loading of translations from API
- Local storage persistence for preferences

#### 3. Language Switcher Component (`frontend/src/components/ui/LanguageSwitcher.tsx`)
- Dropdown language selector with flags
- Native language names display
- Compact version for mobile
- Form selector for settings pages

## Translation Files Structure

### Backend Translations (`data/translations/backend/`)
```json
{
  "hero": {
    "title": "Master Your Exams with",
    "subtitle": "AI Mentorship",
    "description": "Personalized learning paths..."
  },
  "auth": {
    "welcome": "Welcome",
    "signIn": "Sign In",
    "signUp": "Sign Up"
  }
}
```

### Frontend Translations (`data/translations/frontend/`)
```json
{
  "common": {
    "loading": "Loading...",
    "error": "Error",
    "success": "Success"
  },
  "navigation": {
    "dashboard": "Dashboard",
    "profile": "Profile",
    "settings": "Settings"
  }
}
```

## API Usage

### Getting Supported Languages
```bash
GET /api/language/supported

Response:
{
  "success": true,
  "data": {
    "languages": [
      {
        "code": "en",
        "name": "English",
        "native_name": "English",
        "flag": "🇺🇸",
        "rtl": false
      },
      {
        "code": "hi",
        "name": "Hindi",
        "native_name": "हिन्दी",
        "flag": "🇮🇳",
        "rtl": false
      }
    ]
  }
}
```

### Getting Translations
```bash
GET /api/language/translations/hi

Response:
{
  "success": true,
  "data": {
    "language": "hi",
    "translations": {
      "hero": {
        "title": "परीक्षाओं में महारत हासिल करें",
        "subtitle": "एआई मेंटॉरशिप"
      }
    }
  }
}
```

### Setting Language Preference
```bash
POST /api/language/preference
Authorization: Bearer {token}

{
  "language": "hi"
}

Response:
{
  "success": true,
  "message": "Language preference updated successfully",
  "data": {
    "language": "hi"
  }
}
```

## Frontend Usage

### Using Translation Context
```typescript
import { useTranslation } from '@/contexts/LanguageContext';

function MyComponent() {
  const { t, currentLanguage, setLanguage } = useTranslation();
  
  return (
    <div>
      <h1>{t('hero.title')}</h1>
      <p>{t('hero.description')}</p>
      
      <LanguageSwitcher />
      
      <button onClick={() => setLanguage('hi')}>
        Switch to Hindi
      </button>
    </div>
  );
}
```

### Parameter Interpolation
```typescript
// Translation: "Welcome, {name}!"
const message = t('welcome', { name: 'John' });
// Result: "Welcome, John!"
```

### Nested Keys
```typescript
// Translation: {"user": {"profile": {"name": "Name"}}}
const name = t('user.profile.name');
```

## Vidhya AI Multilingual Support

The Vidhya AI chat assistant supports all implemented languages:

### Starting a Chat in Specific Language
```bash
POST /api/vidhya/chat/start
{
  "language": "hi",
  "title": "हिंदी में चैट"
}

Response:
{
  "success": true,
  "data": {
    "session_id": "session_123",
    "welcome_message": "नमस्ते! मैं विद्या एआई हूं...",
    "language": "hi"
  }
}
```

### Language Detection in Chat
- Automatic language detection from user messages
- Context-aware responses in detected language
- Seamless language switching during conversation

## Implementation Checklist

### Backend ✅
- [x] Language configuration system
- [x] Translation service with caching
- [x] Language router with REST endpoints
- [x] Language middleware for detection
- [x] Translation files for all 10 languages
- [x] Integration with Vidhya AI

### Frontend ✅
- [x] Language context and provider
- [x] Language switcher component
- [x] Translation files for all 10 languages
- [x] Integration in key components:
  - [x] Landing page (Hero, Features)
  - [x] Authentication pages (Login, Register)
  - [x] Dashboard pages (Student, Parent)
  - [x] Vidhya AI Chat
- [x] Language persistence in localStorage

## Testing

### Backend Testing
Run the test script to verify backend functionality:
```bash
python test_language_switching.py
```

### Frontend Testing
1. Start the frontend: `npm run dev`
2. Navigate to different pages
3. Use the language switcher to change languages
4. Verify translations appear correctly
5. Test Vidhya AI in different languages

### Test Scenarios
- [x] Language switching updates all UI text
- [x] Language preference persists across sessions
- [x] Vidhya AI responds in selected language
- [x] URL language parameters work (`?lang=hi`)
- [x] Browser language detection works
- [x] Fallback to English for unsupported languages

## Performance Considerations

### Caching Strategy
- Backend: In-memory caching of loaded translations
- Frontend: Local storage of translation files
- API: Response caching for translation endpoints

### Optimization
- Lazy loading of translation files
- Minimal bundle size impact
- Efficient language switching without page reload

## Future Enhancements

### Planned Features
1. **RTL Language Support**: For languages like Arabic, Urdu
2. **Regional Variations**: Different Hindi/Bengali dialects
3. **Auto-translation**: Dynamic translation of new content
4. **Voice Support**: Text-to-speech in different languages
5. **Offline Support**: Cached translations for offline mode

### Scalability
- Easy addition of new languages
- Modular translation system
- Community contribution support for translations

## Troubleshooting

### Common Issues

#### 1. Translations Not Loading
- Check API connectivity: `/api/language/supported`
- Verify language code is valid
- Check browser console for errors

#### 2. Language Not Persisting
- Clear browser localStorage
- Check authentication status
- Verify network connectivity

#### 3. Vidhya AI Not Responding in Selected Language
- Check if language is supported in backend
- Verify chat session language setting
- Check API response for language field

### Debug Mode
Enable debug mode in browser console:
```javascript
localStorage.setItem('debug_language', 'true');
```

This will log:
- Translation loading attempts
- Language switching events
- API request/response details

## Conclusion

The multi-language support implementation makes Mentor AI accessible to millions of Indian students in their native languages. The system is designed to be:

1. **Comprehensive**: Covering major Indian languages
2. **Performant**: With caching and optimization
3. **Maintainable**: Easy to add new languages
4. **User-friendly**: Seamless language switching
5. **Scalable**: Ready for future expansion

This implementation significantly improves the platform's reach and effectiveness in the Indian education market.