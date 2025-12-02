# Parent Features Router Testing Documentation

## Overview

The parent features router provides comprehensive API endpoints for parent-focused features including AI insights, predictive analytics, communication hub, gamified engagement, and resource library. These endpoints help parents monitor, engage with, and support their child's learning journey.

## Authentication

All endpoints require authentication. Include the following header in all requests:
```
Authorization: Bearer <your_jwt_token>
```

Get the token by logging in through the authentication endpoints.

## Endpoints

### POST /api/parent/insights/generate

Generate AI-powered insight for parent.

#### Testing Steps

1. **Using curl:**
```bash
curl -X POST "http://localhost:8000/api/parent/insights/generate?insight_type=performance&student_id=student123&time_period_days=30&include_recommendations=true&severity_threshold=medium" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_jwt_token>"
```

2. **Using Postman:**
- Method: POST
- URL: `{{base_url}}/api/parent/insights/generate`
- Headers: 
  - `Content-Type: application/json`
  - `Authorization: Bearer <your_jwt_token>`
- Query Parameters:
  - insight_type: `performance`
  - student_id: `student123`
  - time_period_days: `30`
  - include_recommendations: `true`
  - severity_threshold: `medium`

#### Request Examples

**Valid Request Parameters:**
- insight_type: `performance`, `engagement`, `weak_areas`, `strengths`, `progress`
- student_id: Any valid student ID string
- time_period_days: Number (7, 30, 90)
- include_recommendations: Boolean (true, false)
- severity_threshold: `low`, `medium`, `high`, `critical`

#### Expected Output

**Success Response (200):**
```json
{
    "success": true,
    "insight": {
        "insight_id": "ins_abc123",
        "insight_type": "performance",
        "title": "Performance Analysis",
        "description": "Your child has shown improvement in Mathematics...",
        "severity": "medium",
        "data": {
            "subjects": {
                "Mathematics": 85,
                "Physics": 78,
                "Chemistry": 82
            }
        },
        "recommendations": [
            "Focus on Physics problem-solving practice",
            "Maintain Mathematics consistency"
        ],
        "action_required": false,
        "confidence_score": 0.87,
        "generation_time_ms": 1250,
        "created_at": "2024-01-15T10:30:00.000Z"
    },
    "generated_at": "2024-01-15T10:30:00.000Z"
}
```

#### Error Scenarios

**400 Bad Request - Invalid Insight Type:**
```json
{
    "detail": "Invalid insight type: invalid_type"
}
```

**401 Unauthorized:**
```json
{
    "detail": "Not authenticated"
}
```

**500 Internal Server Error:**
```json
{
    "detail": "Insight generation failed. Please try again later."
}
```

---

### GET /api/parent/insights

Get parent insights with filtering and pagination.

#### Testing Steps

1. **Using curl:**
```bash
curl -X GET "http://localhost:8000/api/parent/insights?student_id=student123&insight_type=performance&severity=medium&limit=50" \
  -H "Authorization: Bearer <your_jwt_token>"
```

2. **Using Postman:**
- Method: GET
- URL: `{{base_url}}/api/parent/insights`
- Headers: 
  - `Authorization: Bearer <your_jwt_token>`
- Query Parameters:
  - student_id: `student123` (optional)
  - insight_type: `performance` (optional)
  - severity: `medium` (optional)
  - limit: `50` (optional)
  - start_after: `ins_abc123` (optional, for pagination)

#### Expected Output

**Success Response (200):**
```json
{
    "success": true,
    "insights": [
        {
            "insight_id": "ins_abc123",
            "insight_type": "performance",
            "title": "Performance Analysis",
            "description": "Your child has shown improvement...",
            "severity": "medium",
            "created_at": "2024-01-15T10:30:00.000Z"
        }
    ],
    "total_count": 1,
    "has_more": false,
    "next_cursor": null
}
```

---

### POST /api/parent/analytics/predict

Generate predictive analytics for early warnings.

#### Testing Steps

1. **Using curl:**
```bash
curl -X POST "http://localhost:8000/api/parent/analytics/predict?prediction_type=performance_trend&student_id=student123&time_period_days=30&threshold_sensitivity=0.7" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_jwt_token>"
```

2. **Using Postman:**
- Method: POST
- URL: `{{base_url}}/api/parent/analytics/predict`
- Headers: 
  - `Content-Type: application/json`
  - `Authorization: Bearer <your_jwt_token>`
- Query Parameters:
  - prediction_type: `performance_trend`
  - student_id: `student123`
  - time_period_days: `30`
  - threshold_sensitivity: `0.7`

#### Request Examples

**Valid Prediction Types:**
- `performance_trend`: Predict future performance based on current trends
- `engagement_pattern`: Analyze engagement patterns
- `risk_assessment`: Identify at-risk areas
- `goal_achievement`: Predict likelihood of achieving goals

#### Expected Output

**Success Response (200):**
```json
{
    "success": true,
    "prediction": {
        "prediction_id": "pred_xyz789",
        "prediction_type": "performance_trend",
        "risk_level": "low",
        "confidence_score": 0.82,
        "predictions": {
            "mathematics": {
                "current": 85,
                "predicted": 88,
                "trend": "improving"
            },
            "physics": {
                "current": 78,
                "predicted": 80,
                "trend": "stable"
            }
        },
        "risk_factors": [
            {
                "factor": "inconsistent_practice",
                "impact": "medium",
                "description": "Physics practice is inconsistent"
            }
        ],
        "recommendations": [
            "Maintain current Mathematics study pattern",
            "Increase Physics practice frequency"
        ],
        "alerts_triggered": [],
        "time_horizon_days": 30,
        "generation_time_ms": 1850,
        "created_at": "2024-01-15T11:00:00.000Z"
    },
    "generated_at": "2024-01-15T11:00:00.000Z"
}
```

---

### POST /api/parent/communication/generate

Generate AI-powered communication suggestions.

#### Testing Steps

1. **Using curl:**
```bash
curl -X POST "http://localhost:8000/api/parent/communication/generate?communication_type=message&student_id=student123&child_mood=stressed&priority=medium&language=english" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_jwt_token>"
```

2. **Using Postman:**
- Method: POST
- URL: `{{base_url}}/api/parent/communication/generate`
- Headers: 
  - `Content-Type: application/json`
  - `Authorization: Bearer <your_jwt_token>`
- Query Parameters:
  - communication_type: `message`
  - student_id: `student123`
  - child_mood: `stressed` (optional)
  - channel: `in_person` (optional)
  - priority: `medium`
  - language: `english`

#### Request Examples

**Valid Communication Types:**
- `notification`: Quick updates and announcements
- `alert`: Important alerts requiring attention
- `message`: General conversation messages
- `feedback`: Performance feedback discussions
- `motivation`: Encouragement and praise

**Valid Child Moods:**
- `happy`, `stressed`, `tired`, `frustrated`, `motivated`, `confused`

**Valid Channels:**
- `in_person`, `phone_call`, `text_message`, `email`, `video_call`

**Valid Priority Levels:**
- `low`, `medium`, `high`, `critical`

#### Expected Output

**Success Response (200):**
```json
{
    "success": true,
    "communication": {
        "communication_id": "comm_def456",
        "communication_type": "message",
        "channel": "in_person",
        "subject": "Discussion about recent test performance",
        "content": "I noticed you've been working hard on your studies. Let's talk about your recent test results and see how we can improve together...",
        "tone": "supportive",
        "priority": "medium",
        "suggested_timing": "2024-01-15T19:00:00.000Z",
        "follow_up_actions": [
            "Review test papers together",
            "Create improvement plan"
        ],
        "effectiveness_score": 0.85,
        "generation_time_ms": 950,
        "created_at": "2024-01-15T12:00:00.000Z"
    },
    "generated_at": "2024-01-15T12:00:00.000Z"
}
```

---

### POST /api/parent/engagement/track

Track parent engagement event and award points.

#### Testing Steps

1. **Using curl:**
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

2. **Using Postman:**
- Method: POST
- URL: `{{base_url}}/api/parent/engagement/track`
- Headers: 
  - `Content-Type: application/json`
  - `Authorization: Bearer <your_jwt_token>`
- Query Parameters:
  - engagement_type: `daily_check_in`
  - student_id: `student123`
- Body (raw JSON):
```json
{
    "event_data": {
        "duration_minutes": 15,
        "activities": ["reviewed_progress", "set_goals"]
    }
}
```

#### Request Examples

**Valid Engagement Types:**
- `daily_check_in`: Daily parent engagement
- `weekly_challenge`: Weekly challenge completion
- `activity_logging`: Logging learning activities
- `insight_review`: Reviewing AI insights
- `communication_initiative`: Initiating conversations
- `resource_exploration`: Exploring educational resources
- `goal_setting`: Setting learning goals
- `milestone_celebration`: Celebrating achievements

#### Expected Output

**Success Response (200):**
```json
{
    "success": true,
    "tracking_result": {
        "event_id": "eng_ghi789",
        "points_earned": 10,
        "multiplier": 1.0,
        "new_streak": 5,
        "level_up": false,
        "new_level": 3,
        "badges_earned": [],
        "engagement_score": 75.5,
        "generation_time_ms": 450,
        "updated_profile": {
            "parent_id": "parent123",
            "level": 3,
            "total_points": 350,
            "current_streak": 5,
            "longest_streak": 7,
            "engagement_score": 75.5
        }
    },
    "tracked_at": "2024-01-15T12:30:00.000Z",
    "engagement_type": "daily_check_in"
}
```

---

### POST /api/parent/engagement/weekly-challenge

Generate AI-powered weekly challenge.

#### Testing Steps

1. **Using curl:**
```bash
curl -X POST "http://localhost:8000/api/parent/engagement/weekly-challenge?difficulty=medium&personalized=true&student_id=student123" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_jwt_token>"
```

2. **Using Postman:**
- Method: POST
- URL: `{{base_url}}/api/parent/engagement/weekly-challenge`
- Headers: 
  - `Content-Type: application/json`
  - `Authorization: Bearer <your_jwt_token>`
- Query Parameters:
  - challenge_type: `engagement_boost` (optional)
  - difficulty: `medium`
  - personalized: `true`
  - student_id: `student123`

#### Request Examples

**Valid Challenge Types:**
- `engagement_boost`: Increase overall engagement
- `communication_focus`: Improve parent-child communication
- `activity_planning`: Plan learning activities
- `insight_application`: Apply AI insights
- `goal_achievement`: Work towards specific goals
- `learning_together`: Joint learning activities

**Valid Difficulty Levels:**
- `easy`, `medium`, `hard`

#### Expected Output

**Success Response (200):**
```json
{
    "success": true,
    "weekly_challenge": {
        "challenge_id": "chal_jkl012",
        "title": "Science Exploration Week",
        "description": "This week, explore 3 new science concepts with your child...",
        "challenge_type": "learning_together",
        "requirements": [
            "Complete one science experiment together",
            "Visit a science museum or watch documentary",
            "Discuss real-world science applications"
        ],
        "points_reward": 50,
        "badge_reward": "explorer",
        "duration_days": 7,
        "difficulty": "medium",
        "status": "active",
        "created_at": "2024-01-15T13:00:00.000Z"
    },
    "generated_at": "2024-01-15T13:00:00.000Z",
    "challenge_type": "learning_together",
    "difficulty": "medium",
    "personalized": true
}
```

---

### POST /api/parent/resources/generate

Generate AI-powered educational resource.

#### Testing Steps

1. **Using curl:**
```bash
curl -X POST "http://localhost:8000/api/parent/resources/generate?resource_type=article&student_id=student123&category=study_strategies&subject=mathematics&difficulty_level=intermediate&language=english" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_jwt_token>"
```

2. **Using Postman:**
- Method: POST
- URL: `{{base_url}}/api/parent/resources/generate`
- Headers: 
  - `Content-Type: application/json`
  - `Authorization: Bearer <your_jwt_token>`
- Query Parameters:
  - resource_type: `article`
  - student_id: `student123`
  - category: `study_strategies` (optional)
  - subject: `mathematics` (optional)
  - difficulty_level: `intermediate` (optional)
  - language: `english`

#### Request Examples

**Valid Resource Types:**
- `article`: Educational articles
- `video`: Video content
- `exercise`: Practice exercises
- `worksheet`: Printable worksheets
- `guide`: Step-by-step guides
- `activity`: Interactive activities
- `assessment`: Assessment tools
- `tool`: Learning tools
- `template`: Templates for learning

**Valid Categories:**
- `study_strategies`, `subject_specific`, `exam_preparation`, `motivation`, `parenting_tips`, `learning_disabilities`, `career_guidance`, `time_management`

**Valid Difficulty Levels:**
- `beginner`, `intermediate`, `advanced`, `mixed`

#### Expected Output

**Success Response (200):**
```json
{
    "success": true,
    "resource": {
        "resource_id": "res_mno345",
        "title": "Effective Mathematics Study Strategies for Teens",
        "description": "Comprehensive guide to studying mathematics effectively...",
        "resource_type": "article",
        "category": "study_strategies",
        "subject": "mathematics",
        "difficulty_level": "intermediate",
        "age_group": "high_school",
        "language": "english",
        "content": "Mathematics can be challenging, but with the right strategies...",
        "tags": ["study_tips", "mathematics", "problem_solving"],
        "quality_score": "good",
        "effectiveness_rating": 0.0,
        "usage_count": 0,
        "user_ratings": [],
        "ai_generated": true,
        "community_contributed": false,
        "created_at": "2024-01-15T14:00:00.000Z",
        "updated_at": "2024-01-15T14:00:00.000Z"
    },
    "generated_at": "2024-01-15T14:00:00.000Z",
    "resource_type": "article",
    "quality_score": "good",
    "personalized": true
}
```

---

### POST /api/parent/resources/search

Search for educational resources with AI-powered filtering.

#### Testing Steps

1. **Using curl:**
```bash
curl -X POST "http://localhost:8000/api/parent/resources/search?query=physics+study+tips&resource_type=article&category=study_strategies&difficulty_level=intermediate&language=english&limit=10" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_jwt_token>"
```

2. **Using Postman:**
- Method: POST
- URL: `{{base_url}}/api/parent/resources/search`
- Headers: 
  - `Content-Type: application/json`
  - `Authorization: Bearer <your_jwt_token>`
- Query Parameters:
  - query: `physics+study+tips`
  - resource_type: `article` (optional)
  - category: `study_strategies` (optional)
  - subject: `physics` (optional)
  - difficulty_level: `intermediate` (optional)
  - language: `english`
  - limit: `10` (optional)

#### Expected Output

**Success Response (200):**
```json
{
    "success": true,
    "search_results": [
        {
            "resource_id": "res_pqr678",
            "title": "Physics Problem-Solving Techniques",
            "description": "Learn effective strategies for solving physics problems...",
            "resource_type": "article",
            "category": "study_strategies",
            "subject": "physics",
            "difficulty_level": "intermediate",
            "quality_score": "excellent",
            "effectiveness_rating": 4.2,
            "usage_count": 156
        }
    ],
    "total_found": 1,
    "search_time_ms": 320,
    "quality_filtered": true,
    "recommendations": [
        "Try searching for 'quantum mechanics basics' for advanced topics",
        "Consider video resources for visual learning"
    ],
    "next_steps": [
        "Download and review the top resources",
        "Create a study schedule using these materials"
    ],
    "searched_at": "2024-01-15T14:30:00.000Z",
    "query": "physics+study+tips"
}
```

---

### GET /api/parent/health

Health check endpoint for parent features service.

#### Testing Steps

1. **Using curl:**
```bash
curl -X GET "http://localhost:8000/api/parent/health" \
  -H "Authorization: Bearer <your_jwt_token>"
```

2. **Using Postman:**
- Method: GET
- URL: `{{base_url}}/api/parent/health`
- Headers: 
  - `Authorization: Bearer <your_jwt_token>`

#### Expected Output

**Success Response (200):**
```json
{
    "status": "healthy",
    "timestamp": "2024-01-15T15:00:00.000Z",
    "services": {
        "parent_ai_insights": {
            "status": "healthy",
            "metrics": {
                "total_insights_generated": 125,
                "average_generation_time_ms": 1200,
                "cache_hit_rate": 0.75
            }
        },
        "predictive_analytics": {
            "status": "healthy",
            "metrics": {
                "total_predictions": 45,
                "accuracy_score": 0.82,
                "risk_alerts_triggered": 8
            }
        },
        "communication_hub": {
            "status": "healthy",
            "metrics": {
                "total_communications_generated": 89,
                "average_effectiveness_score": 0.78,
                "most_used_tone": "supportive"
            }
        },
        "gamified_engagement": {
            "status": "healthy",
            "metrics": {
                "total_engagement_events": 342,
                "active_parents": 28,
                "average_engagement_score": 72.5
            }
        },
        "parent_resource_library": {
            "status": "healthy",
            "metrics": {
                "total_resources_generated": 167,
                "average_quality_score": 7.2,
                "total_downloads": 523
            }
        }
    }
}
```

---

## Common Testing Scenarios

### Authentication Flow

1. Register a new parent account using `/register/parent/email`
2. Login using the credentials to get JWT token
3. Use the token in `Authorization: Bearer <token>` header for all parent features endpoints

### Error Handling

All endpoints follow consistent error handling:
- **400 Bad Request**: Invalid parameters or validation errors
- **401 Unauthorized**: Missing or invalid authentication token
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server-side errors

### Rate Limiting

Some endpoints may have rate limiting. If you encounter 429 responses:
- Wait before retrying
- Implement exponential backoff in automated tests
- Check response headers for rate limit information

### Testing Best Practices

1. **Use Test Data**: Create test student IDs and use consistent data
2. **Test Error Cases**: Verify proper error handling for invalid inputs
3. **Check Response Times**: Monitor generation times for AI-powered endpoints
4. **Validate Data Structure**: Ensure response matches documented format
5. **Test Authentication**: Verify both authenticated and unauthenticated scenarios

### AI Troubleshooting Prompt

```
I'm testing Mentor AI parent features endpoint [ENDPOINT_NAME] and encountering the following error:

[Insert error message here]

My request is:
[Insert full request including headers, parameters, and body here]

The response I'm getting is:
[Insert full response here]

Environment details:
- API URL: http://localhost:8000
- Authentication: Bearer token present
- Using curl/Postman: [Specify which tool]

Please help me debug this issue by:
1. Analyzing the error and identifying root cause
2. Checking if request format matches the expected models
3. Verifying service configuration and dependencies
4. Providing specific steps to fix the issue

Context: This endpoint is part of Mentor AI EdTech Platform's parent features system using AI-powered insights and recommendations.
```

## Performance Monitoring

Use the metrics endpoints to monitor service performance:
- `/api/parent/metrics/insights` - AI insights service metrics
- `/api/parent/metrics/analytics` - Predictive analytics metrics
- `/api/parent/metrics/communication` - Communication hub metrics
- `/api/parent/metrics/engagement` - Gamified engagement metrics
- `/api/parent/metrics/resource-library` - Resource library metrics

## Integration Testing

For comprehensive testing:
1. Test the complete workflow from insight generation to resource recommendation
2. Verify engagement tracking and point system
3. Test communication generation with different moods and priorities
4. Validate predictive analytics accuracy over time
5. Check resource quality assessment and filtering