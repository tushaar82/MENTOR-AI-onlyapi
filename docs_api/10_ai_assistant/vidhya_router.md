# Vidhya AI Router Testing Documentation

## Overview

The Vidhya AI router provides endpoints for interacting with the Vidhya AI chat assistant in the Mentor AI EdTech Platform. It handles chat session management, message sending/receiving, chat history retrieval, and multilingual support for AI-powered educational assistance.

## Endpoints

### POST /api/vidhya/chat/start

Start a new chat session with Vidhya AI assistant.

#### Testing Steps

1. **Using curl:**
```bash
curl -X POST "http://localhost:8000/api/vidhya/chat/start" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
  -d '{
    "student_id": "student123",
    "language": "hi",
    "title": "Mathematics Doubts"
  }'
```

2. **Using Postman:**
- Method: POST
- URL: `{{base_url}}/api/vidhya/chat/start`
- Headers: 
  - `Content-Type: application/json`
  - `Authorization: Bearer YOUR_AUTH_TOKEN`
- Body (raw JSON):
```json
{
    "student_id": "student123",
    "language": "hi",
    "title": "Mathematics Doubts"
}
```

#### Request Examples

**Valid Request (with all fields):**
```json
{
    "student_id": "student123",
    "language": "hi",
    "title": "Mathematics Doubts"
}
```

**Valid Request (minimal):**
```json
{
    "language": "en"
}
```

**Invalid Request Examples:**
```json
// Invalid language code
{
    "language": "invalid_lang"
}

// Empty message (if required by service)
{
    "student_id": "student123",
    "language": "hi",
    "title": ""
}
```

#### Expected Output

**Success Response (200):**
```json
{
    "success": true,
    "data": {
        "session_id": "session_abc123xyz456",
        "user_id": "user123",
        "student_id": "student123",
        "language": "hi",
        "title": "Mathematics Doubts",
        "created_at": "2024-01-01T10:00:00Z",
        "welcome_message": "नमस्ते! मैं विद्या AI हूं। आज मैं आपकी कैसे मदद कर सकती हूं?"
    },
    "message": "Chat session started successfully"
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
    "detail": "Failed to start chat session"
}
```

---

### POST /api/vidhya/chat/send

Send a message to Vidhya AI and get response.

#### Testing Steps

1. **Using curl:**
```bash
curl -X POST "http://localhost:8000/api/vidhya/chat/send" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
  -d '{
    "message": "What is the Pythagorean theorem?",
    "session_id": "session_abc123xyz456",
    "language": "hi"
  }'
```

2. **Using Postman:**
- Method: POST
- URL: `{{base_url}}/api/vidhya/chat/send`
- Headers: 
  - `Content-Type: application/json`
  - `Authorization: Bearer YOUR_AUTH_TOKEN`
- Body (raw JSON):
```json
{
    "message": "What is the Pythagorean theorem?",
    "session_id": "session_abc123xyz456",
    "language": "hi"
}
```

#### Request Examples

**Valid Request:**
```json
{
    "message": "What is the Pythagorean theorem?",
    "session_id": "session_abc123xyz456",
    "language": "hi"
}
```

**Valid Request (without language override):**
```json
{
    "message": "Explain photosynthesis",
    "session_id": "session_abc123xyz456"
}
```

**Invalid Request Examples:**
```json
// Missing message
{
    "session_id": "session_abc123xyz456",
    "language": "hi"
}

// Missing session_id
{
    "message": "What is physics?",
    "language": "hi"
}

// Empty message
{
    "message": "",
    "session_id": "session_abc123xyz456",
    "language": "hi"
}
```

#### Expected Output

**Success Response (200):**
```json
{
    "success": true,
    "data": {
        "message_id": "msg_def789uvw012",
        "session_id": "session_abc123xyz456",
        "user_message": "What is the Pythagorean theorem?",
        "ai_response": "पाइथागोरस प्रमेय एक त्रिकोणमितीय सिद्धांत है जो बताता है कि एक समकोण त्रिभुज में, कर्ण का वर्ग अन्य दो भुजाओं के वर्गों के योग के बराबर होता है। सूत्र है: a² + b² = c²",
        "language": "hi",
        "timestamp": "2024-01-01T10:01:00Z",
        "response_time": 1.5
    },
    "message": "Message sent successfully"
}
```

#### Error Scenarios

**401 Unauthorized:**
```json
{
    "detail": "Authentication required"
}
```

**400 Bad Request - Invalid Session:**
```json
{
    "detail": "Invalid session ID"
}
```

**400 Bad Request - Validation Error:**
```json
{
    "detail": "Message cannot be empty"
}
```

**500 Internal Server Error:**
```json
{
    "detail": "Failed to send message"
}
```

---

### GET /api/vidhya/chat/history/{session_id}

Get chat history for a specific session.

#### Testing Steps

1. **Using curl:**
```bash
curl -X GET "http://localhost:8000/api/vidhya/chat/history/session_abc123xyz456?limit=50" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN"
```

2. **Using Postman:**
- Method: GET
- URL: `{{base_url}}/api/vidhya/chat/history/{session_id}?limit={limit}`
- Headers: `Authorization: Bearer YOUR_AUTH_TOKEN`

#### Path Parameters

- `session_id` (required): Chat session ID

#### Query Parameters

- `limit` (optional): Maximum number of messages to return (1-200, default: 50)

#### Expected Output

**Success Response (200):**
```json
{
    "success": true,
    "data": {
        "session_id": "session_abc123xyz456",
        "messages": [
            {
                "message_id": "msg_def789uvw012",
                "sender": "user",
                "content": "What is the Pythagorean theorem?",
                "timestamp": "2024-01-01T10:01:00Z"
            },
            {
                "message_id": "msg_ghi345rst678",
                "sender": "ai",
                "content": "पाइथागोरस प्रमेय एक त्रिकोणमितीय सिद्धांत है...",
                "timestamp": "2024-01-01T10:01:01Z"
            }
        ],
        "total_messages": 2,
        "session_info": {
            "language": "hi",
            "title": "Mathematics Doubts",
            "created_at": "2024-01-01T10:00:00Z"
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

**400 Bad Request - Invalid Session:**
```json
{
    "detail": "Invalid session ID"
}
```

**400 Bad Request - Invalid Limit:**
```json
{
    "detail": "Limit must be between 1 and 200"
}
```

**500 Internal Server Error:**
```json
{
    "detail": "Failed to retrieve chat history"
}
```

---

### GET /api/vidhya/chat/sessions

Get all chat sessions for the authenticated user.

#### Testing Steps

1. **Using curl:**
```bash
curl -X GET "http://localhost:8000/api/vidhya/chat/sessions?limit=20" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN"
```

2. **Using Postman:**
- Method: GET
- URL: `{{base_url}}/api/vidhya/chat/sessions?limit={limit}`
- Headers: `Authorization: Bearer YOUR_AUTH_TOKEN`

#### Query Parameters

- `limit` (optional): Maximum number of sessions to return (1-100, default: 20)

#### Expected Output

**Success Response (200):**
```json
{
    "success": true,
    "data": {
        "sessions": [
            {
                "session_id": "session_abc123xyz456",
                "title": "Mathematics Doubts",
                "language": "hi",
                "student_id": "student123",
                "created_at": "2024-01-01T10:00:00Z",
                "last_message_at": "2024-01-01T10:05:00Z",
                "message_count": 5
            },
            {
                "session_id": "session_jkl012mno345",
                "title": "Physics Questions",
                "language": "en",
                "student_id": "student123",
                "created_at": "2024-01-01T09:30:00Z",
                "last_message_at": "2024-01-01T09:45:00Z",
                "message_count": 8
            }
        ],
        "count": 2
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

**400 Bad Request - Invalid Limit:**
```json
{
    "detail": "Limit must be between 1 and 100"
}
```

**500 Internal Server Error:**
```json
{
    "detail": "Failed to retrieve chat sessions"
}
```

---

### DELETE /api/vidhya/chat/session/{session_id}

Delete a chat session.

#### Testing Steps

1. **Using curl:**
```bash
curl -X DELETE "http://localhost:8000/api/vidhya/chat/session/session_abc123xyz456" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN"
```

2. **Using Postman:**
- Method: DELETE
- URL: `{{base_url}}/api/vidhya/chat/session/{session_id}`
- Headers: `Authorization: Bearer YOUR_AUTH_TOKEN`

#### Path Parameters

- `session_id` (required): Chat session ID to delete

#### Expected Output

**Success Response (200):**
```json
{
    "success": true,
    "message": "Chat session deleted successfully"
}
```

#### Error Scenarios

**401 Unauthorized:**
```json
{
    "detail": "Authentication required"
}
```

**404 Not Found - Session Not Found:**
```json
{
    "detail": "Session not found"
}
```

**500 Internal Server Error:**
```json
{
    "detail": "Failed to delete chat session"
}
```

---

### GET /api/vidhya/languages

Get list of languages supported by Vidhya AI.

#### Testing Steps

1. **Using curl:**
```bash
curl -X GET "http://localhost:8000/api/vidhya/languages"
```

2. **Using Postman:**
- Method: GET
- URL: `{{base_url}}/api/vidhya/languages`
- Headers: No special headers required

#### Expected Output

**Success Response (200):**
```json
{
    "success": true,
    "data": [
        {
            "code": "en",
            "name": "English",
            "native_name": "English",
            "supported": true
        },
        {
            "code": "hi",
            "name": "Hindi",
            "native_name": "हिन्दी",
            "supported": true
        },
        {
            "code": "bn",
            "name": "Bengali",
            "native_name": "বাংলা",
            "supported": true
        }
    ]
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

### GET /api/vidhya/health

Health check endpoint for Vidhya AI service.

#### Testing Steps

1. **Using curl:**
```bash
curl -X GET "http://localhost:8000/api/vidhya/health"
```

2. **Using Postman:**
- Method: GET
- URL: `{{base_url}}/api/vidhya/health`
- Headers: No special headers required

#### Expected Output

**Success Response (200):**
```json
{
    "status": "healthy",
    "service": "vidhya-ai-agent",
    "timestamp": "2024-01-01T10:00:00Z",
    "features": {
        "multilingual_support": true,
        "chat_history": true,
        "session_management": true
    }
}
```

#### Error Scenarios

**503 Service Unavailable:**
```json
{
    "status": "unhealthy",
    "service": "vidhya-ai-agent",
    "error": "AI service not available",
    "timestamp": "2024-01-01T10:00:00Z"
}
```

## Common Issues Across All Endpoints

### Authentication
- All endpoints except `/languages` and `/health` require authentication
- Include `Authorization: Bearer YOUR_AUTH_TOKEN` header
- Use valid JWT token from authentication endpoints

### Session Management
- Session IDs are generated when starting a new chat
- Sessions are user-specific and cannot be accessed by other users
- Invalid session IDs will result in 404 errors
- Sessions can be deleted but not modified

### Language Support
- Supported languages: "en", "hi", "bn", "mr", "ta", "te", "gu", "kn", "ml", "pa"
- Language can be set per session or per message
- Default language is "en" if not specified
- AI responses will be in the requested language

### Message Limits
- History endpoint: 1-200 messages (default: 50)
- Sessions endpoint: 1-100 sessions (default: 20)
- Limits prevent excessive data transfer

### General Testing Tips
1. Always start a session before sending messages
2. Use valid session IDs for history and deletion
3. Test with different languages to verify multilingual support
4. Check health endpoint to verify AI service status
5. Test error scenarios with invalid session IDs

## AI Troubleshooting Prompts

### General Vidhya AI Issues

```
I'm testing the Mentor AI Vidhya AI router and encountering the following error:

[Insert error message here]

My request is:
[Insert full request details including URL, headers, and body]

The response I'm getting is:
[Insert full response here]

Environment details:
- API URL: http://localhost:8000
- Session ID: [Specify session ID if applicable]
- Language: [Specify language code]
- Using curl/Postman: [Specify which tool]

Please help me debug this issue by:
1. Analyzing the error and identifying the root cause
2. Checking if the request format is correct according to the models in routers/vidhya_router.py
3. Verifying the Vidhya service initialization in services/vidhya_service.py
4. Checking session management and authentication
5. Providing specific steps to fix the issue

Context: This endpoint is part of the Mentor AI EdTech Platform's AI assistant system using FastAPI and Vidhya AI service.
```

### Chat Session Issues

```
I'm having issues with chat session management in the Vidhya AI router:

[Insert specific issue with sessions]

My request to start/send/get chat sessions is failing with:
[Insert error details]

Environment details:
- API URL: http://localhost:8000
- Session ID: [Specify session ID]
- User ID: [Specify user ID]
- Student ID: [Specify student ID if applicable]

Please help me debug this by:
1. Checking if the session creation process is working correctly
2. Verifying session storage and retrieval mechanisms
3. Checking user authorization for session access
4. Providing steps to fix session management issues

Context: Chat sessions should allow users to interact with Vidhya AI in multiple languages and maintain conversation history.
```

### Multilingual Support Issues

```
I'm testing multilingual support in the Vidhya AI router and encountering issues:

[Insert specific language-related issue]

My request with language parameter is failing:
[Insert error details]

Environment details:
- API URL: http://localhost:8000
- Language code: [Specify language code]
- Session ID: [Specify session ID]
- Translation files: [Verify if they exist]

Please help me debug this by:
1. Checking if the requested language is supported
2. Verifying translation service integration
3. Checking language-specific AI model configuration
4. Providing steps to fix multilingual support issues

Context: Vidhya AI should respond in the user's preferred language and maintain language context throughout the conversation.