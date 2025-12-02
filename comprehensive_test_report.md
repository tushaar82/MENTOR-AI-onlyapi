# Comprehensive Endpoint Test Report
Generated: 2025-12-02T17:11:35.480868
Base URL: http://localhost:8000

## Summary
- Total Tests: 100
- Successful: 13 (13.0%)
- Failed: 87 (87.0%)

## Results by Category
- ai: 0/6 (0.0%)
- analytics: 0/3 (0.0%)
- auth: 1/5 (20.0%)
- diagnostic-test: 1/7 (14.3%)
- email: 0/2 (0.0%)
- gamification: 0/7 (0.0%)
- onboarding: 4/8 (50.0%)
- parent: 0/7 (0.0%)
- payment: 1/5 (20.0%)
- phone: 0/2 (0.0%)
- rag: 4/6 (66.7%)
- root: 2/3 (66.7%)
- schedule: 0/1 (0.0%)
- student: 0/12 (0.0%)
- study-center: 0/11 (0.0%)
- syllabus: 0/7 (0.0%)
- test_child_123: 0/1 (0.0%)
- vector-search: 0/7 (0.0%)

## Failed Tests
### POST /api/auth/register/parent/email
- Status Code: 400
- Error: An account with email testparent@example.com already exists. Please login instead.
- Response Time: 682.96ms

### POST /api/auth/register/parent/phone
- Status Code: 400
- Error: An account with phone number +919876543210 already exists. Please login instead.
- Response Time: 396.13ms

### POST /api/auth/register/simple
- Status Code: 400
- Error: An account with email testparent@example.com already exists. Please login instead.
- Response Time: 472.34ms

### POST /api/auth/login/phone
- Status Code: 422
- Error: [{'type': 'missing', 'loc': ['body', 'otp'], 'msg': 'Field required', 'input': {'phone': '+919876543210', 'password': 'TestPassword123'}, 'url': 'https://errors.pydantic.dev/2.4/v/missing'}]
- Response Time: 3.61ms

### POST /verify/email/send
- Status Code: 404
- Error: Not Found
- Response Time: 4.10ms

### POST /verify/email/confirm
- Status Code: 404
- Error: Not Found
- Response Time: 5.43ms

### POST /verify/phone/send
- Status Code: 404
- Error: Not Found
- Response Time: 7.21ms

### POST /verify/phone/confirm
- Status Code: 404
- Error: Not Found
- Response Time: 6.83ms

### POST /api/onboarding/preferences
- Status Code: 400
- Error: Preferences already exist for this parent. Use update endpoint to modify.
- Response Time: 74.39ms

### POST /child
- Status Code: 404
- Error: Not Found
- Response Time: 7.88ms

### GET /child/test_child_123
- Status Code: 404
- Error: Not Found
- Response Time: 6.93ms

### POST /api/onboarding/exam/select
- Status Code: 404
- Error: Child profile not found: test_child_123
- Response Time: 86.52ms

### GET /api/onboarding/exam/preferences
- Status Code: 404
- Error: Exam selection not found for child: test_child_123
- Response Time: 58.33ms

### PUT /api/onboarding/exam/preferences
- Status Code: 404
- Error: Child profile not found: test_child_123
- Response Time: 51.85ms

### POST /api/vector-search/embeddings/generate
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 5.53ms

### POST /api/vector-search/embeddings/batch
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 7.86ms

### GET /api/vector-search/embeddings/status
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 3.41ms

### POST /api/vector-search/query
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 6.68ms

### POST /api/vector-search/query/batch
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 4.53ms

### GET /api/vector-search/index/status
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 7.41ms

### GET /api/vector-search/syllabus/JEE_MAIN/Physics
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 9.27ms

### POST /api/rag/generate-questions
- Status Code: 0
- Error: 
- Response Time: 30033.97ms

### POST /api/rag/generate-batch
- Status Code: 422
- Error: [{'type': 'string_type', 'loc': ['body', 'topics', 0], 'msg': 'Input should be a valid string', 'input': {'topic': 'Kinematics', 'question_count': 3}, 'url': 'https://errors.pydantic.dev/2.4/v/string_type'}, {'type': 'string_type', 'loc': ['body', 'topics', 1], 'msg': 'Input should be a valid string', 'input': {'topic': 'Thermodynamics', 'question_count': 2}, 'url': 'https://errors.pydantic.dev/2.4/v/string_type'}]
- Response Time: 19222.57ms

### POST /api/diagnostic-test/generate
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 2.08ms

### POST /api/diagnostic-test/test_123/start
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 2.00ms

### POST /api/diagnostic-test/test_123/submit
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 3.12ms

### GET /api/diagnostic-test/test_123/results
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 7.97ms

### GET /api/diagnostic-test/test_123/status
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 7.68ms

### PATCH /api/diagnostic-test/test_123/status
- Status Code: 403
- Error: Admin privileges required
- Response Time: 6.18ms

### POST /api/schedule/generate
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 9.64ms

### POST /api/payment/create-order
- Status Code: 500
- Error: {'success': False, 'error': {'type': 'RazorpayConfigurationError', 'message': 'RAZORPAY_KEY_ID is not set. Please set the RAZORPAY_KEY_ID environment variable or pass it as a parameter.', 'detail': 'An internal server error occurred. Please try again later.'}}
- Response Time: 19.94ms

### GET /api/payment/subscription/test_parent_123
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 6.35ms

### GET /api/payment/transactions/test_parent_123
- Status Code: 500
- Error: {'success': False, 'error': {'type': 'RazorpayConfigurationError', 'message': 'RAZORPAY_KEY_ID is not set. Please set the RAZORPAY_KEY_ID environment variable or pass it as a parameter.', 'detail': 'An internal server error occurred. Please try again later.'}}
- Response Time: 11.42ms

### POST /api/payment/cancel/test_parent_123
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 8.09ms

### GET /api/study-center/topics
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 2.18ms

### GET /api/study-center/topics/topic_123
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 2.29ms

### GET /api/study-center/materials/topic_123
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 1.90ms

### POST /api/study-center/materials/generate
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 2.12ms

### GET /api/study-center/mindmap/topic_123
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 1.86ms

### GET /api/study-center/teach/topic_123
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 1.97ms

### GET /api/study-center/progress/test_student_123
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 2.32ms

### POST /api/study-center/progress/start
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 2.29ms

### POST /api/study-center/progress/complete
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 1.94ms

### GET /api/study-center/journey/test_student_123
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 1.84ms

### GET /api/study-center/parent-progress/child_123
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 2.99ms

### POST /api/ai/tutor/ask
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 4.26ms

### GET /api/ai/tutor/history/test_student_123
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 3.91ms

### GET /api/ai/recommend/topics/test_student_123
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 4.31ms

### GET /api/ai/recommend/resources/topic_123
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 5.03ms

### GET /api/ai/readiness/test_student_123
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 4.76ms

### GET /api/ai/analysis/mistakes/test_student_123
- Status Code: 401
- Error: Invalid token. Please login again.
- Response Time: 4.38ms

### POST /api/analytics/generate
- Status Code: 404
- Error: Not Found
- Response Time: 3.29ms

### GET /api/analytics/student/test_student_123
- Status Code: 404
- Error: Not Found
- Response Time: 3.54ms

### GET /api/analytics/test/test_123
- Status Code: 404
- Error: Not Found
- Response Time: 3.49ms

### GET /api/syllabus/coverage/test_student_123
- Status Code: 404
- Error: Not Found
- Response Time: 3.35ms

### GET /api/syllabus/coverage/test_student_123/untested
- Status Code: 404
- Error: Not Found
- Response Time: 3.21ms

### GET /api/syllabus/coverage/test_student_123/weak
- Status Code: 404
- Error: Not Found
- Response Time: 2.91ms

### GET /api/syllabus/coverage/test_student_123/recommendations
- Status Code: 404
- Error: Not Found
- Response Time: 3.41ms

### GET /api/syllabus/coverage/test_student_123/progress
- Status Code: 404
- Error: Not Found
- Response Time: 3.37ms

### GET /api/syllabus/coverage/test_student_123/topic/topic_123
- Status Code: 404
- Error: Not Found
- Response Time: 3.58ms

### GET /api/syllabus/coverage/health
- Status Code: 404
- Error: Not Found
- Response Time: 3.77ms

### GET /api/parent/dashboard/child_123
- Status Code: 404
- Error: Not Found
- Response Time: 4.76ms

### GET /api/parent/reports/weekly/child_123
- Status Code: 404
- Error: Not Found
- Response Time: 3.55ms

### POST /api/parent/reports/email-schedule
- Status Code: 404
- Error: Not Found
- Response Time: 2.81ms

### GET /api/parent/notifications/settings
- Status Code: 404
- Error: Not Found
- Response Time: 3.01ms

### PUT /api/parent/notifications/settings
- Status Code: 404
- Error: Not Found
- Response Time: 2.08ms

### POST /api/parent/goals/child_123
- Status Code: 404
- Error: Not Found
- Response Time: 2.60ms

### GET /api/parent/goals/child_123
- Status Code: 404
- Error: Not Found
- Response Time: 3.02ms

### GET /api/student/today/test_student_123
- Status Code: 404
- Error: Not Found
- Response Time: 3.31ms

### GET /api/student/topic/topic_123/resources
- Status Code: 404
- Error: Not Found
- Response Time: 3.04ms

### POST /api/student/practice/quick
- Status Code: 404
- Error: Not Found
- Response Time: 3.56ms

### POST /api/student/doubts
- Status Code: 404
- Error: Not Found
- Response Time: 4.30ms

### GET /api/student/doubts/doubt_123/explanation
- Status Code: 404
- Error: Not Found
- Response Time: 3.20ms

### GET /api/student/revision/due
- Status Code: 404
- Error: Not Found
- Response Time: 3.28ms

### POST /api/student/revision/mark-complete/topic_123
- Status Code: 404
- Error: Not Found
- Response Time: 3.99ms

### POST /api/student/bookmarks
- Status Code: 404
- Error: Not Found
- Response Time: 3.76ms

### GET /api/student/bookmarks
- Status Code: 404
- Error: Not Found
- Response Time: 4.59ms

### DELETE /api/student/bookmarks/bookmark_123
- Status Code: 404
- Error: Not Found
- Response Time: 3.17ms

### GET /api/student/insights/test_student_123
- Status Code: 404
- Error: Not Found
- Response Time: 2.92ms

### GET /api/student/compare/percentile
- Status Code: 404
- Error: Not Found
- Response Time: 3.27ms

### GET /api/gamification/achievements
- Status Code: 404
- Error: Not Found
- Response Time: 3.02ms

### POST /api/gamification/achievements/claim/ach_123
- Status Code: 404
- Error: Not Found
- Response Time: 2.98ms

### GET /api/gamification/challenge/daily
- Status Code: 404
- Error: Not Found
- Response Time: 3.03ms

### POST /api/gamification/challenge/daily/submit
- Status Code: 404
- Error: Not Found
- Response Time: 3.14ms

### GET /api/gamification/challenge/leaderboard
- Status Code: 404
- Error: Not Found
- Response Time: 3.12ms

### GET /api/gamification/streak
- Status Code: 404
- Error: Not Found
- Response Time: 3.58ms

### GET /api/gamification/points/history
- Status Code: 404
- Error: Not Found
- Response Time: 3.01ms

## Slow Tests (>2000ms)
### POST /api/rag/generate-questions
- Response Time: 30033.97ms
- Status Code: 0

### POST /api/rag/generate-batch
- Response Time: 19222.57ms
- Status Code: 422

## Detailed Results
### ai
❌ POST /api/ai/tutor/ask - 401 (4.26ms)
❌ GET /api/ai/tutor/history/test_student_123 - 401 (3.91ms)
❌ GET /api/ai/recommend/topics/test_student_123 - 401 (4.31ms)
❌ GET /api/ai/recommend/resources/topic_123 - 401 (5.03ms)
❌ GET /api/ai/readiness/test_student_123 - 401 (4.76ms)
❌ GET /api/ai/analysis/mistakes/test_student_123 - 401 (4.38ms)
### analytics
❌ POST /api/analytics/generate - 404 (3.29ms)
❌ GET /api/analytics/student/test_student_123 - 404 (3.54ms)
❌ GET /api/analytics/test/test_123 - 404 (3.49ms)
### auth
❌ POST /api/auth/register/parent/email - 400 (682.96ms)
❌ POST /api/auth/register/parent/phone - 400 (396.13ms)
❌ POST /api/auth/register/simple - 400 (472.34ms)
✅ POST /api/auth/login/email - 200 (1153.80ms)
❌ POST /api/auth/login/phone - 422 (3.61ms)
### diagnostic-test
❌ POST /api/diagnostic-test/generate - 401 (2.08ms)
❌ POST /api/diagnostic-test/test_123/start - 401 (2.00ms)
❌ POST /api/diagnostic-test/test_123/submit - 401 (3.12ms)
❌ GET /api/diagnostic-test/test_123/results - 401 (7.97ms)
❌ GET /api/diagnostic-test/test_123/status - 401 (7.68ms)
❌ PATCH /api/diagnostic-test/test_123/status - 403 (6.18ms)
✅ GET /api/diagnostic-test/management/health - 200 (5.19ms)
### email
❌ POST /verify/email/send - 404 (4.10ms)
❌ POST /verify/email/confirm - 404 (5.43ms)
### gamification
❌ GET /api/gamification/achievements - 404 (3.02ms)
❌ POST /api/gamification/achievements/claim/ach_123 - 404 (2.98ms)
❌ GET /api/gamification/challenge/daily - 404 (3.03ms)
❌ POST /api/gamification/challenge/daily/submit - 404 (3.14ms)
❌ GET /api/gamification/challenge/leaderboard - 404 (3.12ms)
❌ GET /api/gamification/streak - 404 (3.58ms)
❌ GET /api/gamification/points/history - 404 (3.01ms)
### onboarding
❌ POST /api/onboarding/preferences - 400 (74.39ms)
✅ GET /api/onboarding/preferences - 200 (70.86ms)
✅ PUT /api/onboarding/preferences - 200 (223.34ms)
✅ GET /api/onboarding/exams/available - 200 (9.06ms)
❌ POST /api/onboarding/exam/select - 404 (86.52ms)
❌ GET /api/onboarding/exam/preferences - 404 (58.33ms)
❌ PUT /api/onboarding/exam/preferences - 404 (51.85ms)
✅ GET /api/onboarding/status - 200 (158.25ms)
### parent
❌ GET /api/parent/dashboard/child_123 - 404 (4.76ms)
❌ GET /api/parent/reports/weekly/child_123 - 404 (3.55ms)
❌ POST /api/parent/reports/email-schedule - 404 (2.81ms)
❌ GET /api/parent/notifications/settings - 404 (3.01ms)
❌ PUT /api/parent/notifications/settings - 404 (2.08ms)
❌ POST /api/parent/goals/child_123 - 404 (2.60ms)
❌ GET /api/parent/goals/child_123 - 404 (3.02ms)
### payment
✅ GET /api/payment/plans - 200 (7.63ms)
❌ POST /api/payment/create-order - 500 (19.94ms)
❌ GET /api/payment/subscription/test_parent_123 - 401 (6.35ms)
❌ GET /api/payment/transactions/test_parent_123 - 500 (11.42ms)
❌ POST /api/payment/cancel/test_parent_123 - 401 (8.09ms)
### phone
❌ POST /verify/phone/send - 404 (7.21ms)
❌ POST /verify/phone/confirm - 404 (6.83ms)
### rag
❌ POST /api/rag/generate-questions - 0 (30033.97ms)
❌ POST /api/rag/generate-batch - 422 (19222.57ms)
✅ POST /api/rag/context/build - 200 (12.58ms)
✅ POST /api/rag/context/preview - 200 (10.35ms)
✅ GET /api/rag/pipeline/status - 200 (57.47ms)
✅ GET /api/rag/metrics - 200 (1.93ms)
### root
✅ GET / - 200 (9.41ms)
✅ GET /health - 200 (1.75ms)
❌ POST /child - 404 (7.88ms)
### schedule
❌ POST /api/schedule/generate - 401 (9.64ms)
### student
❌ GET /api/student/today/test_student_123 - 404 (3.31ms)
❌ GET /api/student/topic/topic_123/resources - 404 (3.04ms)
❌ POST /api/student/practice/quick - 404 (3.56ms)
❌ POST /api/student/doubts - 404 (4.30ms)
❌ GET /api/student/doubts/doubt_123/explanation - 404 (3.20ms)
❌ GET /api/student/revision/due - 404 (3.28ms)
❌ POST /api/student/revision/mark-complete/topic_123 - 404 (3.99ms)
❌ POST /api/student/bookmarks - 404 (3.76ms)
❌ GET /api/student/bookmarks - 404 (4.59ms)
❌ DELETE /api/student/bookmarks/bookmark_123 - 404 (3.17ms)
❌ GET /api/student/insights/test_student_123 - 404 (2.92ms)
❌ GET /api/student/compare/percentile - 404 (3.27ms)
### study-center
❌ GET /api/study-center/topics - 401 (2.18ms)
❌ GET /api/study-center/topics/topic_123 - 401 (2.29ms)
❌ GET /api/study-center/materials/topic_123 - 401 (1.90ms)
❌ POST /api/study-center/materials/generate - 401 (2.12ms)
❌ GET /api/study-center/mindmap/topic_123 - 401 (1.86ms)
❌ GET /api/study-center/teach/topic_123 - 401 (1.97ms)
❌ GET /api/study-center/progress/test_student_123 - 401 (2.32ms)
❌ POST /api/study-center/progress/start - 401 (2.29ms)
❌ POST /api/study-center/progress/complete - 401 (1.94ms)
❌ GET /api/study-center/journey/test_student_123 - 401 (1.84ms)
❌ GET /api/study-center/parent-progress/child_123 - 401 (2.99ms)
### syllabus
❌ GET /api/syllabus/coverage/test_student_123 - 404 (3.35ms)
❌ GET /api/syllabus/coverage/test_student_123/untested - 404 (3.21ms)
❌ GET /api/syllabus/coverage/test_student_123/weak - 404 (2.91ms)
❌ GET /api/syllabus/coverage/test_student_123/recommendations - 404 (3.41ms)
❌ GET /api/syllabus/coverage/test_student_123/progress - 404 (3.37ms)
❌ GET /api/syllabus/coverage/test_student_123/topic/topic_123 - 404 (3.58ms)
❌ GET /api/syllabus/coverage/health - 404 (3.77ms)
### test_child_123
❌ GET /child/test_child_123 - 404 (6.93ms)
### vector-search
❌ POST /api/vector-search/embeddings/generate - 401 (5.53ms)
❌ POST /api/vector-search/embeddings/batch - 401 (7.86ms)
❌ GET /api/vector-search/embeddings/status - 401 (3.41ms)
❌ POST /api/vector-search/query - 401 (6.68ms)
❌ POST /api/vector-search/query/batch - 401 (4.53ms)
❌ GET /api/vector-search/index/status - 401 (7.41ms)
❌ GET /api/vector-search/syllabus/JEE_MAIN/Physics - 401 (9.27ms)