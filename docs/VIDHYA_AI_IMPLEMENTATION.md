# Vidhya AI Agent Implementation

## Overview

Vidhya is an AI-powered chat assistant for the Mentor AI EdTech Platform. She provides educational support to students in simple, understandable language, with full multilingual support for Indian languages.

## Features

### Core Features
- **Multilingual Chat Support**: Communicate in English, Hindi, Bengali, Telugu, Tamil, Marathi, Gujarati, Kannada, Malayalam, and Punjabi
- **Context-Aware Conversations**: Remembers previous messages in the same session for coherent dialogue
- **Simple & Understandable Responses**: Provides answers in easy-to-understand language
- **Educational Focus**: Specialized for JEE/NEET exam preparation and learning
- **Session Management**: Create, manage, and delete chat sessions
- **Chat History**: Access previous conversations and continue learning

### Technical Implementation

#### Backend Components
1. **Vidhya Service** (`services/vidhya_service.py`)
   - Core AI agent logic
   - Session management
   - Message handling
   - Language support
   - Integration with Gemini AI

2. **API Router** (`routers/vidhya_router.py`)
   - RESTful endpoints for chat functionality
   - Authentication middleware
   - Request/response validation

3. **Database Models** (`models/vidhya_models.py`)
   - Pydantic models for data validation
   - Chat message structure
   - Session management
   - User preferences

#### Frontend Components
1. **Vidhya Chat Component** (`frontend/src/components/vidhya/VidhyaChat.tsx`)
   - Interactive chat interface
   - Real-time messaging
   - Language selector
   - Session sidebar
   - Typing indicators

2. **Vidhya Page** (`frontend/src/app/vidhya/page.tsx`)
   - Main Vidhya AI interface
   - Feature highlights
   - Authentication check
   - Welcome screen for new users

## API Endpoints

### Chat Session Management
- `POST /api/vidhya/chat/start` - Start new chat session
- `GET /api/vidhya/chat/sessions` - Get user's chat sessions
- `DELETE /api/vidhya/chat/session/{session_id}` - Delete chat session

### Message Handling
- `POST /api/vidhya/chat/send` - Send message to Vidhya
- `GET /api/vidhya/chat/history/{session_id}` - Get chat history

### Utility Endpoints
- `GET /api/vidhya/languages` - Get supported languages
- `GET /api/vidhya/health` - Health check

## Supported Languages

| Code | Language | Native Name |
|-------|----------|-------------|
| en | English | English |
| hi | हिन्दी | Hindi |
| bn | বাংলা | Bengali |
| te | తెలుగు | Telugu |
| ta | தமிழ் | Tamil |
| mr | मराठी | Marathi |
| gu | ગુજરાતી | Gujarati |
| kn | ಕನ್ನಡ | Kannada |
| ml | മലയാളം | Malayalam |
| pa | ਪੰਜਾਬੀ | Punjabi |

## Usage Instructions

### For Students
1. Navigate to `/vidhya` in the application
2. Click "New Chat" to start a conversation
3. Select your preferred language from the dropdown
4. Type your question and press Enter to send
5. Vidhya will respond in your selected language

### For Developers
1. Backend service is initialized as a singleton: `get_vidhya_service()`
2. Frontend component: `<VidhyaChat userToken={token} />`
3. API integration follows RESTful conventions
4. All requests require authentication via Bearer token

## Architecture

### Backend Flow
1. User sends message → API endpoint
2. Request validated → Vidhya Service
3. Context built → Gemini AI
4. Response generated → Stored in session
5. Response returned → Frontend display

### Frontend Flow
1. User selects language → Stored in component state
2. User types message → Sent to backend API
3. Response received → Added to message list
4. UI updates → Scroll to latest message

## Testing

Run the test script to verify implementation:
```bash
python3 test_vidhya_simple.py
```

The test will verify:
- Service initialization
- Model creation
- Language support
- Basic functionality

## Integration Notes

### Authentication
Vidhya requires user authentication. The component checks for:
- `userToken` in localStorage
- Valid session with the backend

### Error Handling
- Network errors display user-friendly messages
- Invalid sessions redirect to welcome screen
- Language fallbacks to English if unsupported

### Performance Considerations
- Messages are cached for 30 days
- Sessions limited to 50 in memory
- API rate limiting applied (60 requests/minute)

## Future Enhancements

1. **Voice Support**: Text-to-speech for responses
2. **File Upload**: Share images/documents with Vidhya
3. **Study Mode**: Focused help for specific subjects
4. **Progress Tracking**: Monitor learning over time
5. **Offline Support**: Basic functionality without internet

## Security Considerations

1. All API endpoints require authentication
2. User sessions are isolated by user ID
3. Message content is validated and sanitized
4. Rate limiting prevents abuse
5. No sensitive data stored in plain text

## Deployment

### Environment Variables
Required:
- `GOOGLE_APPLICATION_CREDENTIALS` - Firebase service account
- `GEMINI_API_KEY` - Google Gemini API key

### Frontend Build
```bash
cd frontend
npm install
npm run build
```

### Backend Start
```bash
python3 main.py
```

## Support

For issues or questions about Vidhya AI:
1. Check the API documentation at `/api/docs`
2. Review logs for error messages
3. Verify environment configuration
4. Test with the provided test script

---

**Author**: Mentor AI Team  
**Version**: 1.0.0  
**Last Updated**: December 2025