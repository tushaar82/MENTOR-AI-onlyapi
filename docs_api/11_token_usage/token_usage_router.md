# Token Usage Router API Documentation

## Overview
The Token Usage Router provides endpoints for tracking and managing AI token usage for students based on their subscription plans. This helps monitor AI feature consumption and enforce usage limits.

## Base URL
```
/api/token-usage
```

## Endpoints

### 1. Get Student Token Usage

**GET** `/api/token-usage/student/{student_id}`

Retrieves detailed token usage information for a specific student.

#### Path Parameters
- `student_id` (string, required): Unique identifier of the student

#### Query Parameters
- `period` (string, optional): Time period for usage data
  - Values: `daily`, `weekly`, `monthly`, `all`
  - Default: `monthly`

#### Response
```json
{
  "success": true,
  "data": {
    "student_id": "student_123",
    "usage": {
      "daily": {
        "used": 150,
        "limit": 500,
        "remaining": 350,
        "reset_time": "2024-01-02T00:00:00Z"
      },
      "monthly": {
        "used": 2500,
        "limit": 10000,
        "remaining": 7500,
        "reset_time": "2024-02-01T00:00:00Z"
      }
    },
    "interactions": [
      {
        "interaction_id": "int_001",
        "type": "vidhya_chat",
        "tokens_used": 50,
        "timestamp": "2024-01-01T10:30:00Z",
        "endpoint": "/api/vidhya/chat/send",
        "metadata": {
          "session_id": "session_123"
        }
      }
    ],
    "subscription_plan": {
      "plan_id": "basic",
      "name": "Basic Plan",
      "daily_limit": 500,
      "monthly_limit": 10000
    }
  }
}
```

#### Error Response
```json
{
  "success": false,
  "error": {
    "code": "STUDENT_NOT_FOUND",
    "message": "Student not found"
  }
}
```

### 2. Get Student Token Limits

**GET** `/api/token-usage/limits/student/{student_id}`

Retrieves current token limits and remaining quota for a student.

#### Path Parameters
- `student_id` (string, required): Unique identifier of the student

#### Response
```json
{
  "success": true,
  "data": {
    "student_id": "student_123",
    "limits": {
      "daily": {
        "limit": 500,
        "used": 150,
        "remaining": 350,
        "reset_in_hours": 8
      },
      "monthly": {
        "limit": 10000,
        "used": 2500,
        "remaining": 7500,
        "reset_in_days": 15
      }
    },
    "subscription_plan": "basic",
    "last_updated": "2024-01-01T12:00:00Z"
  }
}
```

### 3. Get Parent Token Usage Summary

**GET** `/api/token-usage/parent`

Retrieves token usage summary for all children of a parent.

#### Headers
- `Authorization` (string, required): Bearer token for parent authentication

#### Query Parameters
- `period` (string, optional): Time period for usage data
  - Values: `daily`, `weekly`, `monthly`, `all`
  - Default: `monthly`

#### Response
```json
{
  "success": true,
  "data": {
    "parent_id": "parent_123",
    "children": [
      {
        "student_id": "student_123",
        "name": "John Doe",
        "usage": {
          "daily": { "used": 150, "limit": 500 },
          "monthly": { "used": 2500, "limit": 10000 }
        },
        "last_activity": "2024-01-01T10:30:00Z"
      }
    ],
    "summary": {
      "total_daily_used": 150,
      "total_daily_limit": 500,
      "total_monthly_used": 2500,
      "total_monthly_limit": 10000
    }
  }
}
```

### 4. Reset Daily Token Usage

**POST** `/api/token-usage/reset/daily/{student_id}`

Resets daily token usage for a student (admin only).

#### Path Parameters
- `student_id` (string, required): Unique identifier of the student

#### Headers
- `Authorization` (string, required): Bearer token with admin privileges

#### Request Body
```json
{
  "reason": "Manual reset for testing",
  "admin_id": "admin_123"
}
```

#### Response
```json
{
  "success": true,
  "message": "Daily token usage reset successfully",
  "data": {
    "student_id": "student_123",
    "previous_usage": 150,
    "new_usage": 0,
    "reset_at": "2024-01-01T12:00:00Z"
  }
}
```

### 5. Get Token Usage Summary for Parent

**GET** `/api/token-usage/summary/parent`

Retrieves comprehensive token usage summary for parent dashboard.

#### Headers
- `Authorization` (string, required): Bearer token for parent authentication

#### Query Parameters
- `period` (string, optional): Time period for usage data
  - Values: `daily`, `weekly`, `monthly`, `all`
  - Default: `monthly`
- `child_id` (string, optional): Filter by specific child

#### Response
```json
{
  "success": true,
  "data": {
    "parent_id": "parent_123",
    "period": "monthly",
    "summary": {
      "total_tokens_used": 2500,
      "total_tokens_limit": 10000,
      "usage_percentage": 25.0,
      "days_remaining": 15
    },
    "usage_by_feature": {
      "vidhya_chat": 1000,
      "question_generation": 800,
      "diagnostic_tests": 500,
      "schedule_generation": 200
    },
    "usage_trend": [
      {
        "date": "2024-01-01",
        "tokens_used": 150
      },
      {
        "date": "2024-01-02",
        "tokens_used": 120
      }
    ],
    "children_summary": [
      {
        "student_id": "student_123",
        "name": "John Doe",
        "tokens_used": 2500,
        "last_active": "2024-01-01T10:30:00Z"
      }
    ]
  }
}
```

## Error Codes

| Error Code | Description | HTTP Status |
|------------|-------------|-------------|
| `STUDENT_NOT_FOUND` | Student not found | 404 |
| `PARENT_NOT_FOUND` | Parent not found | 404 |
| `UNAUTHORIZED` | Invalid or missing authentication | 401 |
| `FORBIDDEN` | Insufficient permissions | 403 |
| `INVALID_PERIOD` | Invalid time period specified | 400 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |
| `INTERNAL_ERROR` | Server error | 500 |

## Rate Limits

| Endpoint | Rate Limit |
|----------|------------|
| GET `/student/{student_id}` | 60 requests/minute |
| GET `/limits/student/{student_id}` | 60 requests/minute |
| GET `/parent` | 30 requests/minute |
| POST `/reset/daily/{student_id}` | 10 requests/hour |
| GET `/summary/parent` | 30 requests/minute |

## Testing Examples

### Using curl

```bash
# Get student token usage
curl -X GET "http://localhost:8000/api/token-usage/student/student_123?period=monthly" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get student limits
curl -X GET "http://localhost:8000/api/token-usage/limits/student/student_123" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get parent summary
curl -X GET "http://localhost:8000/api/token-usage/summary/parent?period=monthly" \
  -H "Authorization: Bearer PARENT_TOKEN"

# Reset daily usage (admin only)
curl -X POST "http://localhost:8000/api/token-usage/reset/daily/student_123" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Manual reset", "admin_id": "admin_123"}'
```

### Using Postman

1. Import the Mentor AI Postman collection
2. Navigate to "Token Usage" folder
3. Set environment variables:
   - `BASE_URL`: http://localhost:8000
   - `STUDENT_TOKEN`: Valid student authentication token
   - `PARENT_TOKEN`: Valid parent authentication token
   - `ADMIN_TOKEN`: Valid admin authentication token
4. Execute requests with appropriate authentication

## Notes

- All timestamps are in UTC format (ISO 8601)
- Token counts are approximate and may vary slightly based on AI model
- Daily limits reset at 00:00 UTC
- Monthly limits reset on the 1st of each month at 00:00 UTC
- Usage data is retained for 90 days
- Admin privileges required for reset operations