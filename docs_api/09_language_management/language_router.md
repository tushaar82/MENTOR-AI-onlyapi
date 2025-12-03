# Language Router Testing Documentation

## Overview

The language router provides endpoints for managing language preferences, translations, and multilingual support in the Mentor AI EdTech Platform. It handles language validation, translation retrieval, and user language preferences.

## Endpoints

### GET /api/language/supported

Get list of all supported languages with their metadata.

#### Testing Steps

1. **Using curl:**
```bash
curl -X GET "http://localhost:8000/api/language/supported"
```

2. **Using Postman:**
- Method: GET
- URL: `{{base_url}}/api/language/supported`
- Headers: No special headers required

#### Expected Output

**Success Response (200):**
```json
{
    "success": true,
    "data": {
        "languages": [
            {
                "code": "en",
                "name": "English",
                "native_name": "English",
                "rtl": false,
                "flag_emoji": "🇺🇸"
            },
            {
                "code": "hi",
                "name": "Hindi",
                "native_name": "हिन्दी",
                "rtl": false,
                "flag_emoji": "🇮🇳"
            }
        ],
        "count": 2,
        "default": "en"
    }
}
```

#### Error Scenarios

**500 Internal Server Error:**
```json
{
    "detail": "Failed to retrieve supported languages"
}
```

---

### GET /api/language/info/{language_code}

Get detailed information about a specific language.

#### Testing Steps

1. **Using curl:**
```bash
curl -X GET "http://localhost:8000/api/language/info/hi"
```

2. **Using Postman:**
- Method: GET
- URL: `{{base_url}}/api/language/info/{language_code}`
- Headers: No special headers required

#### Request Examples

**Valid Language Codes:**
- `en` - English
- `hi` - Hindi
- `bn` - Bengali
- `mr` - Marathi
- `ta` - Tamil
- `te` - Telugu
- `gu` - Gujarati
- `kn` - Kannada
- `ml` - Malayalam
- `pa` - Punjabi

#### Expected Output

**Success Response (200):**
```json
{
    "success": true,
    "data": {
        "code": "hi",
        "name": "Hindi",
        "native_name": "हिन्दी",
        "rtl": false,
        "flag_emoji": "🇮🇳",
        "date_format": "DD/MM/YYYY",
        "time_format": "24-hour"
    }
}
```

#### Error Scenarios

**404 Not Found - Invalid Language:**
```json
{
    "detail": "Language not found"
}
```

**500 Internal Server Error:**
```json
{
    "detail": "Failed to retrieve language information"
}
```

---

### GET /api/language/translations/{language_code}

Get translations for a specific language, optionally filtered by namespace.

#### Testing Steps

1. **Using curl (without namespace):**
```bash
curl -X GET "http://localhost:8000/api/language/translations/hi" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN"
```

2. **Using curl (with namespace):**
```bash
curl -X GET "http://localhost:8000/api/language/translations/hi?namespace=auth" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN"
```

3. **Using Postman:**
- Method: GET
- URL: `{{base_url}}/api/language/translations/{language_code}?namespace={namespace}`
- Headers: `Authorization: Bearer YOUR_AUTH_TOKEN`

#### Query Parameters

- `language_code` (required): Language code (e.g., 'en', 'hi')
- `namespace` (optional): Namespace to filter translations (e.g., 'auth', 'dashboard')

#### Expected Output

**Success Response (200):**
```json
{
    "success": true,
    "data": {
        "language": "hi",
        "namespace": "auth",
        "translations": {
            "login": {
                "title": "लॉग इन करें",
                "email_placeholder": "ईमेल दर्ज करें",
                "password_placeholder": "पासवर्ड दर्ज करें",
                "submit_button": "लॉग इन"
            }
        },
        "count": 4
    }
}
```

#### Error Scenarios

**401 Unauthorized:**
```json
{
    "detail": "Authentication required"
}
```

**500 Internal Server Error:**
```json
{
    "detail": "Failed to retrieve translations"
}
```

---

### POST /api/language/preference

Set user's preferred language.

#### Testing Steps

1. **Using curl:**
```bash
curl -X POST "http://localhost:8000/api/language/preference" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
  -d '{
    "language": "hi"
  }'
```

2. **Using Postman:**
- Method: POST
- URL: `{{base_url}}/api/language/preference`
- Headers: 
  - `Content-Type: application/json`
  - `Authorization: Bearer YOUR_AUTH_TOKEN`
- Body (raw JSON):
```json
{
    "language": "hi"
}
```

#### Request Examples

**Valid Request:**
```json
{
    "language": "hi"
}
```

**Invalid Request Examples:**
```json
// Invalid language code
{
    "language": "invalid_lang"
}

// Empty language
{
    "language": ""
}
```

#### Expected Output

**Success Response (200):**
```json
{
    "success": true,
    "data": {
        "language": "hi",
        "message": "सेटिंग्स सफलतापूर्वक सहेजी गईं"
    }
}
```

#### Error Scenarios

**401 Unauthorized:**
```json
{
    "detail": "Authentication required"
}
```

**400 Bad Request - Invalid Language:**
```json
{
    "detail": "Invalid language code"
}
```

**500 Internal Server Error:**
```json
{
    "detail": "Failed to set language preference"
}
```

---

### GET /api/language/preference

Get user's preferred language.

#### Testing Steps

1. **Using curl:**
```bash
curl -X GET "http://localhost:8000/api/language/preference" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN"
```

2. **Using Postman:**
- Method: GET
- URL: `{{base_url}}/api/language/preference`
- Headers: `Authorization: Bearer YOUR_AUTH_TOKEN`

#### Expected Output

**Success Response (200):**
```json
{
    "success": true,
    "data": {
        "language": "hi",
        "language_info": {
            "code": "hi",
            "name": "Hindi",
            "native_name": "हिन्दी",
            "flag_emoji": "🇮🇳"
        }
    }
}
```

#### Error Scenarios

**401 Unauthorized:**
```json
{
    "detail": "Authentication required"
}
```

**500 Internal Server Error:**
```json
{
    "detail": "Failed to retrieve language preference"
}
```

---

### GET /api/language/translate

Translate a specific key to the requested language.

#### Testing Steps

1. **Using curl:**
```bash
curl -X GET "http://localhost:8000/api/language/translate?key=auth.login.title&language_code=hi" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN"
```

2. **Using Postman:**
- Method: GET
- URL: `{{base_url}}/api/language/translate?key={key}&language_code={language_code}`
- Headers: `Authorization: Bearer YOUR_AUTH_TOKEN`

#### Query Parameters

- `key` (required): Translation key (e.g., 'auth.login.title')
- `language_code` (optional): Target language code (defaults to 'en')

#### Expected Output

**Success Response (200):**
```json
{
    "success": true,
    "data": {
        "key": "auth.login.title",
        "language": "hi",
        "translation": "लॉग इन करें"
    }
}
```

#### Error Scenarios

**401 Unauthorized:**
```json
{
    "detail": "Authentication required"
}
```

**400 Bad Request - Missing Key:**
```json
{
    "detail": "Translation key is required"
}
```

**500 Internal Server Error:**
```json
{
    "detail": "Failed to translate text"
}
```

---

### GET /api/language/health

Health check endpoint for language service.

#### Testing Steps

1. **Using curl:**
```bash
curl -X GET "http://localhost:8000/api/language/health"
```

2. **Using Postman:**
- Method: GET
- URL: `{{base_url}}/api/language/health`
- Headers: No special headers required

#### Expected Output

**Success Response (200):**
```json
{
    "status": "healthy",
    "service": "language-service",
    "timestamp": "2024-01-01T00:00:00Z",
    "features": {
        "supported_languages": 10,
        "translation_service": true,
        "language_validation": true,
        "user_preferences": true
    },
    "supported_languages": ["en", "hi", "bn", "mr", "ta", "te", "gu", "kn", "ml", "pa"]
}
```

#### Error Scenarios

**503 Service Unavailable:**
```json
{
    "status": "unhealthy",
    "service": "language-service",
    "error": "Translation service not available",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

---

### GET /api/language/rtl

Get list of RTL (right-to-left) languages.

#### Testing Steps

1. **Using curl:**
```bash
curl -X GET "http://localhost:8000/api/language/rtl"
```

2. **Using Postman:**
- Method: GET
- URL: `{{base_url}}/api/language/rtl`
- Headers: No special headers required

#### Expected Output

**Success Response (200):**
```json
{
    "success": true,
    "data": {
        "rtl_languages": [],
        "count": 0
    }
}
```

#### Error Scenarios

**500 Internal Server Error:**
```json
{
    "detail": "Failed to retrieve RTL languages"
}
```

---

### GET /api/language/validate/{language_code}

Validate if a language code is supported.

#### Testing Steps

1. **Using curl:**
```bash
curl -X GET "http://localhost:8000/api/language/validate/hi"
```

2. **Using Postman:**
- Method: GET
- URL: `{{base_url}}/api/language/validate/{language_code}`
- Headers: No special headers required

#### Expected Output

**Success Response (200) - Valid Language:**
```json
{
    "success": true,
    "data": {
        "input_code": "hi",
        "is_supported": true,
        "validated_code": "hi",
        "is_rtl": false
    }
}
```

**Success Response (200) - Invalid Language:**
```json
{
    "success": true,
    "data": {
        "input_code": "invalid_lang",
        "is_supported": false,
        "validated_code": null,
        "is_rtl": false
    }
}
```

#### Error Scenarios

**500 Internal Server Error:**
```json
{
    "detail": "Failed to validate language"
}
```

## Common Issues Across All Endpoints

### Authentication
- Endpoints marked with `@Depends(get_current_user)` require authentication
- Include `Authorization: Bearer YOUR_AUTH_TOKEN` header
- Use valid JWT token from authentication endpoints

### Language Validation
- Supported languages: "en", "hi", "bn", "mr", "ta", "te", "gu", "kn", "ml", "pa"
- Default language is "en" if not specified
- Invalid language codes will cause validation errors

### Translation Service
- Ensure translation files exist in `data/translations/backend/` directory
- Translation files must be valid JSON format
- Namespace filtering only works if translations are organized by namespace

### General Testing Tips
1. Test with both valid and invalid language codes
2. Verify authentication tokens are valid and not expired
3. Check translation files exist for requested languages
4. Test namespace filtering with valid and invalid namespaces
5. Use the health check endpoint to verify service status

## AI Troubleshooting Prompts

### General Language Router Issues

```
I'm testing the Mentor AI language router and encountering the following error:

[Insert error message here]

My request is:
[Insert full request details including URL, headers, and body]

The response I'm getting is:
[Insert full response here]

Environment details:
- API URL: http://localhost:8000
- Language code: [Specify language code]
- Using curl/Postman: [Specify which tool]

Please help me debug this issue by:
1. Analyzing the error and identifying the root cause
2. Checking if the request format is correct according to the models in routers/language_router.py
3. Verifying the language configuration in config/language_config.py
4. Checking translation files in data/translations/backend/
5. Providing specific steps to fix the issue

Context: This endpoint is part of the Mentor AI EdTech Platform's multilingual support system using FastAPI.
```

### Translation Service Issues

```
I'm having issues with the translation service in the Mentor AI language router:

[Insert specific issue with translations]

My request to GET /api/language/translations/{language_code} is failing with:
[Insert error details]

Environment details:
- API URL: http://localhost:8000
- Language code: [Specify language code]
- Namespace: [Specify namespace if used]
- Translation file location: [Verify file exists]

Please help me debug this by:
1. Checking if translation files exist and are valid JSON
2. Verifying the translation service initialization
3. Checking the namespace filtering logic
4. Providing steps to fix translation loading issues

Context: The translation service should load JSON files from data/translations/backend/ and provide multilingual support.