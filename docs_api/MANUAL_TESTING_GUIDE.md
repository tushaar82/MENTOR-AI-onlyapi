# Mentor AI Backend - Manual Testing Guide

## Overview

This guide provides comprehensive instructions for manually testing all Mentor AI Backend API endpoints. It includes setup instructions, authentication flow, and detailed testing scenarios for each router.

## Prerequisites

### 1. Environment Setup

1. **Install Required Tools:**
   - Python 3.8+
   - curl (command-line tool)
   - Postman (recommended for GUI testing)
   - Git

2. **Clone and Setup Repository:**
   ```bash
   git clone <repository_url>
   cd Mentor-AI
   pip install -r requirements.txt
   ```

3. **Environment Configuration:**
   - Copy `.env.example` to `.env`
   - Configure Firebase credentials
   - Set up Gemini API key
   - Configure database settings

4. **Start the Server:**
   ```bash
   python3 main.py
   ```
   - Server should start on `http://localhost:8000`
   - API docs available at `http://localhost:8000/docs`

### 2. Authentication Setup

Before testing protected endpoints, you need to authenticate:

1. **Register a Parent Account:**
   ```bash
   curl -X POST "http://localhost:8000/register/parent/email" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "testparent@example.com",
       "password": "TestPass123",
       "language": "en"
     }'
   ```

2. **Login to Get JWT Token:**
   ```bash
   curl -X POST "http://localhost:8000/login/email" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "testparent@example.com",
       "password": "TestPass123"
     }'
   ```

3. **Extract Token from Response:**
   - Save the `access_token` from the login response
   - Use this token in `Authorization: Bearer <token>` header for all protected endpoints

## Testing Workflow

### 1. Health Check

Always start with a health check to ensure the server is running:

```bash
curl -X GET "http://localhost:8000/health"
```

Expected response: `{"status": "healthy"}`

### 2. Authentication Endpoints

#### Parent Registration
```bash
# Email Registration
curl -X POST "http://localhost:8000/register/parent/email" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "parent@example.com",
    "password": "SecurePass123",
    "language": "en"
  }'

# Phone Registration
curl -X POST "http://localhost:8000/register/parent/phone" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+919876543210",
    "language": "hi"
  }'

# Google OAuth Registration
curl -X POST "http://localhost:8000/register/parent/google" \
  -H "Content-Type: application/json" \
  -d '{
    "id_token": "your_google_id_token",
    "language": "en"
  }'
```

#### Parent Login
```bash
# Email Login
curl -X POST "http://localhost:8000/login/email" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "parent@example.com",
    "password": "SecurePass123"
  }'

# Phone Login
curl -X POST "http://localhost:8000/login/phone" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+919876543210",
    "otp": "123456"
  }'
```

### 3. Onboarding Endpoints

#### Child Profile Creation
```bash
curl -X POST "http://localhost:8000/api/onboarding/child" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -d '{
    "name": "Test Child",
    "age": 15,
    "grade": "10",
    "exam_type": "jee_main",
    "subjects": ["Mathematics", "Physics", "Chemistry"]
  }'
```

#### Exam Selection
```bash
curl -X POST "http://localhost:8000/api/onboarding/exam/select" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -d '{
    "exam_type": "jee_main",
    "exam_date": "2024-04-05",
    "target_score": 250
  }'
```

### 4. Diagnostic Test Endpoints

#### Generate Diagnostic Test
```bash
curl -X POST "http://localhost:8000/api/diagnostic-test/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -d '{
    "student_id": "test_student_123",
    "subject": "Mathematics",
    "difficulty": "medium",
    "num_questions": 20
  }'
```

#### Get Test Details
```bash
curl -X GET "http://localhost:8000/api/diagnostic-test/test_123" \
  -H "Authorization: Bearer <your_jwt_token>"
```

### 5. Study Center Endpoints

#### Get Topics
```bash
curl -X GET "http://localhost:8000/api/study-center/topics" \
  -H "Authorization: Bearer <your_jwt_token>"
```

#### Generate Study Materials
```bash
curl -X POST "http://localhost:8000/api/study-center/materials/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -d '{
    "topic_id": "math_calculus",
    "material_type": "notes",
    "difficulty": "medium",
    "language": "en"
  }'
```

### 6. Parent Features Endpoints

#### Generate AI Insights
```bash
curl -X POST "http://localhost:8000/api/parent/insights/generate?insight_type=performance&student_id=student123&time_period_days=30" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_jwt_token>"
```

#### Generate Predictive Analytics
```bash
curl -X POST "http://localhost:8000/api/parent/analytics/predict?prediction_type=performance_trend&student_id=student123&time_period_days=30" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_jwt_token>"
```

#### Generate Communication Suggestions
```bash
curl -X POST "http://localhost:8000/api/parent/communication/generate?communication_type=message&student_id=student123&child_mood=stressed&priority=medium" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_jwt_token>"
```

#### Track Engagement
```bash
curl -X POST "http://localhost:8000/api/parent/engagement/track?engagement_type=daily_check_in&student_id=student123" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -d '{
    "event_data": {
      "duration_minutes": 15,
      "activities": ["reviewed_progress", "set_goals"]
    }
  }'
```

#### Generate Weekly Challenge
```bash
curl -X POST "http://localhost:8000/api/parent/engagement/weekly-challenge?difficulty=medium&personalized=true&student_id=student123" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_jwt_token>"
```

#### Generate Educational Resource
```bash
curl -X POST "http://localhost:8000/api/parent/resources/generate?resource_type=article&student_id=student123&category=study_strategies&subject=mathematics" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_jwt_token>"
```

#### Search Resources
```bash
curl -X POST "http://localhost:8000/api/parent/resources/search?query=physics+study+tips&language=english&limit=10" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_jwt_token>"
```

### 7. AI Features Endpoints

#### Generate Embeddings
```bash
curl -X POST "http://localhost:8000/api/vector-search/embeddings/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -d '{
    "texts": [
      "Newton's laws of motion",
      "Calculus fundamentals",
      "Chemical bonding"
    ]
  }'
```

#### Vector Search Query
```bash
curl -X POST "http://localhost:8000/api/vector-search/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -d '{
    "query": "physics mechanics",
    "top_k": 10,
    "similarity_threshold": 0.7
  }'
```

#### Generate RAG Questions
```bash
curl -X POST "http://localhost:8000/api/rag/generate-questions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -d '{
    "topic": "calculus",
    "difficulty": "medium",
    "num_questions": 5,
    "question_types": ["multiple_choice", "short_answer"]
  }'
```

## Testing Scenarios

### 1. Success Scenario Testing

For each endpoint, test:
- Valid request format
- All required parameters present
- Valid parameter values
- Proper authentication

### 2. Error Scenario Testing

For each endpoint, test:
- Missing required parameters
- Invalid parameter values
- Missing authentication
- Invalid authentication token
- Resource not found scenarios

### 3. Edge Case Testing

Test boundary conditions:
- Maximum/minimum parameter values
- Empty strings and null values
- Special characters in text fields
- Very long text inputs
- Concurrent requests

### 4. Performance Testing

Monitor:
- Response times for AI-powered endpoints
- Database query performance
- Memory usage during batch operations
- Rate limiting behavior

## Postman Collection

Import the provided Postman collection:
1. Open Postman
2. Click "Import"
3. Select `docs/Mentor_AI_Postman_Collection.json`
4. Update environment variables:
   - `base_url`: `http://localhost:8000`
   - `jwt_token`: Your authentication token

## Common Issues and Solutions

### 1. Authentication Failures

**Problem**: 401 Unauthorized errors
**Solution**:
- Check JWT token is valid and not expired
- Ensure `Authorization: Bearer <token>` header format
- Verify token is properly URL-encoded in curl

### 2. CORS Issues

**Problem**: Cross-origin errors in browser
**Solution**:
- Test with curl/Postman instead of browser
- Configure CORS settings if needed
- Use same origin for frontend and API

### 3. Firebase Connection Issues

**Problem**: Authentication or database errors
**Solution**:
- Verify Firebase credentials in `.env`
- Check Firebase project settings
- Ensure service account has required permissions

### 4. AI Service Errors

**Problem**: Gemini API errors
**Solution**:
- Check API key configuration
- Verify rate limits and quotas
- Monitor API usage and billing

### 5. Database Connection Issues

**Problem**: Firestore connection errors
**Solution**:
- Check network connectivity
- Verify Firestore permissions
- Ensure proper Firebase initialization

## Test Data Management

### 1. Test Users

Create dedicated test accounts:
- `testparent@example.com` / `TestPass123`
- `testparent2@example.com` / `TestPass123`
- `testparent+phone@example.com` / `TestPass123`

### 2. Test Students

Create test student profiles:
- `test_student_123` - Age 15, Grade 10
- `test_student_456` - Age 16, Grade 11
- `test_student_789` - Age 17, Grade 12

### 3. Cleanup

Regularly clean up test data:
- Delete test users from Firebase Auth
- Clear test documents from Firestore
- Reset test counters and metrics

## Automation Script

For automated testing, create a shell script:

```bash
#!/bin/bash

# Configuration
BASE_URL="http://localhost:8000"
EMAIL="testparent@example.com"
PASSWORD="TestPass123"

# Login and get token
echo "Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/login/email" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASSWORD}\"}")

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')

# Test endpoints
echo "Testing health check..."
curl -s -X GET "${BASE_URL}/health"

echo "Testing parent insights..."
curl -s -X POST "${BASE_URL}/api/parent/insights/generate?insight_type=performance&student_id=test123" \
  -H "Authorization: Bearer ${TOKEN}"

# Add more tests as needed
```

## Reporting and Documentation

### 1. Test Results

Document test results in a structured format:
- Endpoint tested
- Request parameters
- Response status code
- Response body
- Pass/Fail status
- Issues encountered

### 2. Bug Reporting

For bugs found during testing:
1. Document exact steps to reproduce
2. Include full request and response
3. Note environment and configuration
4. Provide expected vs actual behavior
5. Include logs and error messages

### 3. Performance Metrics

Track and report:
- Response times for each endpoint
- Success/failure rates
- Resource utilization
- Database query times
- AI service response times

## Best Practices

1. **Test Early and Often**: Run tests after each code change
2. **Use Version Control**: Track test scripts and results
3. **Document Everything**: Keep detailed test documentation
4. **Automate When Possible**: Use scripts for repetitive tests
5. **Monitor Continuously**: Set up ongoing health checks
6. **Test Security**: Verify authentication and authorization
7. **Test Scalability**: Check performance under load
8. **Test Compatibility**: Verify across different environments

## Troubleshooting AI Prompt

When encountering issues with AI-powered endpoints, use this prompt:

```
I'm testing Mentor AI endpoint [ENDPOINT_NAME] and encountering issues:

Request:
[Method]: [HTTP Method]
[URL]: [Full URL with parameters]
[Headers]: [All headers including auth]
[Body]: [Request body if applicable]

Response:
[Status Code]: [HTTP status code]
[Headers]: [Response headers]
[Body]: [Full response body]

Expected Behavior:
[What should happen]

Actual Behavior:
[What actually happened]

Environment:
- Server URL: http://localhost:8000
- Authentication: Bearer token present
- Client: curl/Postman/browser
- Time: [Current timestamp]

Please help me debug by:
1. Analyzing the request/response for issues
2. Checking if format matches API documentation
3. Identifying potential configuration problems
4. Suggesting specific fixes
5. Providing alternative approaches if needed
```

## Resources

- [API Documentation](./ENDPOINTS_GUIDE.md)
- [Postman Collection](../Mentor_AI_Postman_Collection.json)
- [Troubleshooting Guide](./TROUBLESHOOTING_GUIDE.md)
- [Testing Workflow](./TESTING_WORKFLOW.md)
- [Router-Specific Documentation](./01_authentication/, ./02_onboarding/, etc.)

Remember to consult the specific router documentation for detailed endpoint information and examples.