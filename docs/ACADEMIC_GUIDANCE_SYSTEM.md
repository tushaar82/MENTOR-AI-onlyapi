# AI-Powered Academic Guidance System

## Overview

The AI-Powered Academic Guidance System is a comprehensive backend service that analyzes student learning data and generates personalized recommendations to improve learning outcomes. The system ingests various types of learning activities, identifies patterns and knowledge gaps, and provides actionable insights for students and parents.

## Features

### 🎯 Core Capabilities

- **Multi-Modal Activity Logging**: Capture topic access, quiz attempts, learning sequences, and study sessions
- **Intelligent Pattern Recognition**: Identify learning patterns, time management issues, and subject preferences
- **Knowledge Gap Analysis**: Detect conceptual, procedural, and factual knowledge gaps with severity assessment
- **Personalized Recommendations**: Generate prerequisite reviews, alternative resources, and study strategies
- **Real-time Progress Tracking**: Monitor learning streaks, completion rates, and performance trends
- **Parent-Child Access Control**: Secure access control ensuring students and parents only see their data

### 📊 Data Analysis

#### Learning Patterns Identified
- Time management patterns (rushed learning, excessive time)
- Difficulty preference patterns (avoiding hard/easy questions)
- Subject transition patterns (frequent switching)
- Error patterns (consistent mistake types)
- Completion rate patterns (low completion, inconsistent effort)

#### Knowledge Gap Types
- **Conceptual Gaps**: Fundamental understanding issues
- **Procedural Gaps**: Step-by-step process problems
- **Factual Gaps**: Missing factual knowledge

#### Recommendation Categories
- **Prerequisite Review**: Foundational concepts before advanced topics
- **Alternative Resources**: Different learning approaches for struggling topics
- **Practice More**: Targeted practice for weak areas
- **Study Strategy**: Time management and learning approach improvements
- **Time Allocation**: Optimal study session duration recommendations

## Architecture

### 🏗️ System Components

#### 1. Data Models (`models/learning_analytics_models.py`)
- `TopicAccess`: Individual topic study records
- `QuizAttempt`: Comprehensive quiz performance data
- `QuestionError`: Detailed error analysis per question
- `LearningSequence`: Session-based topic exploration patterns
- `LearningPattern`: Identified behavioral patterns
- `KnowledgeGap`: Specific knowledge deficiencies
- `LearningStrength`: Student's mastered areas
- `Recommendation`: Personalized action items
- `StudentActivityLog`: Complete session records

#### 2. Analysis Engine (`services/learning_analysis_service.py`)
- Pattern recognition algorithms
- Statistical analysis of performance data
- Trend identification and prediction
- Gap severity classification
- Strength consistency scoring
- Learning progress metrics calculation

#### 3. Recommendation Engine (`services/recommendation_engine.py`)
- Rule-based recommendation logic
- Priority-based recommendation sorting
- Resource mapping and suggestion
- Time estimation for recommendations
- Action step generation

#### 4. Academic Guidance Service (`services/academic_guidance_service.py`)
- Complete pipeline orchestration
- Firestore integration for data persistence
- Caching for performance optimization
- Access control and security
- Real-time analysis triggering

#### 5. API Endpoints
- **Activity Logging** (`routers/academic_guidance_router.py`)
  - `POST /api/guidance/activity/log`: Log comprehensive activities
  - `POST /api/guidance/activity/topic-access`: Log topic-specific access
  - `POST /api/guidance/activity/quiz-attempt`: Log quiz with error analysis
  - `POST /api/guidance/activity/learning-sequence`: Log session patterns

- **Progress & Insights** (`routers/progress_insights_router.py`)
  - `GET /api/progress/{student_id}`: Comprehensive progress report
  - `GET /api/insights/{student_id}`: Specific guidance insights
  - `GET /api/insights/{student_id}/patterns`: Learning patterns only
  - `GET /api/insights/{student_id}/gaps`: Knowledge gaps only
  - `GET /api/insights/{student_id}/strengths`: Learning strengths only
  - `GET /api/recommendations/{student_id}`: Current recommendations

#### 6. Configuration (`config/academic_guidance_config.py`)
- Analysis parameters and thresholds
- Recommendation engine settings
- Cache configuration
- Feature flags for A/B testing
- Monitoring and alerting settings

#### 7. Validation (`utils/academic_guidance_validators.py`)
- Data consistency validation
- Business logic validation
- Error message formatting
- Pydantic model validators

## 🔧 Configuration

### Environment Variables

```bash
# Academic Guidance System Configuration
ACADEMIC_GUIDANCE_MIN_DATA_POINTS_FOR_PATTERN=5
ACADEMIC_GUIDANCE_ERROR_PATTERN_THRESHOLD=0.6
ACADEMIC_GUIDANCE_STRENGTH_CONFIDENCE_THRESHOLD=0.8
ACADEMIC_GUIDANCE_RECOMMENDATIONS_VALIDITY_DAYS=14
ACADEMIC_GUIDANCE_MAX_RECOMMENDATIONS_PER_TYPE=3
ACADEMIC_GUIDANCE_CACHE_ENABLED=true
ACADEMIC_GUIDANCE_ANALYSIS_CACHE_HOURS=24
```

### Feature Flags

```bash
# Enable/Disable Features
ACADEMIC_GUIDANCE_ENABLE_ADVANCED_ANALYSIS=true
ACADEMIC_GUIDANCE_ENABLE_ML_RECOMMENDATIONS=false
ACADEMIC_GUIDANCE_ENABLE_REAL_TIME_ANALYSIS=true
ACADEMIC_GUIDANCE_ENABLE_PREDICTIVE_INSIGHTS=false
ACADEMIC_GUIDANCE_ENABLE_PARENT_NOTIFICATIONS=true
ACADEMIC_GUIDANCE_ROLLOUT_PERCENTAGE=100.0
```

## 📡 API Usage

### Authentication

All endpoints require valid Firebase authentication tokens. The system supports:
- **Student Access**: Students can access their own data
- **Parent Access**: Parents can access their linked children's data
- **Access Control**: Automatic verification of parent-child relationships

### Activity Logging Examples

#### Log Topic Access
```bash
curl -X POST "http://localhost:8000/api/guidance/activity/topic-access" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student_123",
    "topic_id": "topic_thermodynamics_001",
    "subject": "Physics",
    "chapter": "Thermodynamics",
    "time_spent_minutes": 45,
    "completion_percentage": 80.0,
    "activity_type": "topic_study"
  }'
```

#### Log Quiz Attempt
```bash
curl -X POST "http://localhost:8000/api/guidance/activity/quiz-attempt" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student_123",
    "quiz_id": "quiz_thermo_001",
    "subject": "Physics",
    "topic_id": "topic_thermodynamics_001",
    "difficulty": "medium",
    "start_time": "2024-01-15T14:00:00Z",
    "end_time": "2024-01-15T15:30:00Z",
    "total_time_minutes": 90,
    "total_questions": 20,
    "attempted_questions": 18,
    "correct_answers": 12,
    "score_percentage": 66.7,
    "question_errors": [
      {
        "question_number": 5,
        "error_type": "formula_error",
        "error_description": "Applied wrong formula for heat transfer",
        "student_answer": "25 J",
        "correct_answer": "35 J",
        "time_spent_seconds": 180
      }
    ]
  }'
```

### Progress Retrieval Examples

#### Get Comprehensive Progress
```bash
curl -X GET "http://localhost:8000/api/progress/student_123" \
  -H "Authorization: Bearer <token>"
```

#### Get Learning Patterns
```bash
curl -X GET "http://localhost:8000/api/insights/student_123/patterns" \
  -H "Authorization: Bearer <token>"
```

#### Get Knowledge Gaps
```bash
curl -X GET "http://localhost:8000/api/insights/student_123/gaps?severity_filter=critical" \
  -H "Authorization: Bearer <token>"
```

## 🎯 Recommendation System

### Recommendation Types

1. **Prerequisite Review**: Suggests reviewing foundational concepts
2. **Alternative Resources**: Provides different learning approaches
3. **Practice More**: Recommends additional practice for weak areas
4. **Study Strategy**: Suggests improvements in learning approach
5. **Time Allocation**: Recommends optimal study session duration

### Priority Levels

- **Urgent**: Critical knowledge gaps requiring immediate attention
- **High**: Important recommendations for significant improvement
- **Medium**: Beneficial recommendations for moderate improvement
- **Low**: Optional recommendations for enhancement

### Resource Categories

- **Videos**: Khan Academy, YouTube Education, Coursera
- **Practice**: Brilliant, IXL, Khan Practice
- **Reading**: NCERT, MIT OpenCourseWare, Textbook Solutions
- **Interactive**: PhET Simulations, GeoGebra, Desmos

## 🔍 Analysis Algorithms

### Pattern Detection

The system uses multiple algorithms to identify learning patterns:

#### Time Management Analysis
- **Rushed Learning**: Sessions significantly shorter than average
- **Excessive Time**: Sessions significantly longer than average
- **Optimal Time**: Sessions within ideal duration range

#### Performance Pattern Analysis
- **Consistent Low Performance**: Below 50% across recent attempts
- **Inconsistent Effort**: High performance on hard questions but low on medium
- **Difficulty Avoidance**: Avoiding specific difficulty levels

#### Learning Sequence Analysis
- **Subject Switching**: Frequent changes between subjects
- **Topic Hopping**: Rapid topic changes without completion
- **Focused Learning**: Deep dive into single topics

### Gap Detection

Knowledge gaps are identified through:

#### Performance Thresholds
- **Critical**: Below 30% average performance
- **Moderate**: Below 50% average performance
- **Minor**: Below 70% average performance

#### Error Pattern Analysis
- **Formula Errors**: Consistent mistakes in formula application
- **Conceptual Errors**: Fundamental misunderstanding of concepts
- **Procedural Errors**: Step-by-step process mistakes
- **Careless Mistakes**: Errors due to lack of attention

## 📊 Data Flow

### 1. Data Ingestion
```
Student Activity → Activity Logging → Firestore Storage
     ↓
Multiple Activity Types → Data Validation → Analysis Queue
```

### 2. Analysis Pipeline
```
Analysis Queue → Pattern Detection → Gap Analysis → Strength Identification
     ↓
Analysis Results → Recommendation Engine → Prioritization → Cache Storage
```

### 3. Insight Generation
```
Cache Storage → Progress Compilation → Report Generation → API Response
     ↓
Real-time Updates → Parent Notifications → Dashboard Display
```

## 🔒 Security & Access Control

### Authentication
- Firebase Authentication integration
- JWT token validation
- Session management
- Token revocation checking

### Authorization
- **Student Access**: Full access to own data
- **Parent Access**: Access to linked children's data only
- **Role-based Permissions**: Different access levels for different user types
- **Data Privacy**: Complete data isolation between users

### Data Validation
- Input validation for all API endpoints
- Business logic validation
- Data consistency checks
- Error handling and logging

## 🚀 Deployment

### Environment Setup

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Firebase Setup**
```bash
# Download service account credentials
# Place at config/firebase-credentials.json
# Update Firebase project settings
```

### Running the Service

```bash
# Development
python main.py

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📈 Monitoring & Analytics

### Performance Metrics
- Analysis processing time
- Recommendation generation time
- Cache hit/miss rates
- API response times
- Error rates by endpoint

### Health Checks
- `/health`: Basic service health
- `/api/health`: Detailed component health
- Database connection checks
- External service availability

## 🔧 Development

### Adding New Analysis Patterns

1. Create pattern detection algorithm in `LearningAnalysisService`
2. Add pattern type to `LearningPattern` model
3. Update recommendation logic in `RecommendationEngine`
4. Add tests for new pattern

### Adding New Recommendation Types

1. Define recommendation type in `RecommendationType` enum
2. Add generation logic in `RecommendationEngine`
3. Create resource mappings in `RecommendationEngine`
4. Add API endpoints for new type

### Extending Data Models

1. Add new fields to existing models
2. Create new model classes as needed
3. Update validators for new fields
4. Update API request/response models

## 🧪 Testing

### Unit Tests
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_learning_analysis_service.py
```

### Integration Tests
```bash
# Test API endpoints
pytest tests/test_academic_guidance_api.py

# Test database operations
pytest tests/test_database_integration.py
```

### Load Testing
```bash
# Performance testing
locust -f tests/locustfile.py

# Stress testing
ab -n 1000 -c 10 http://localhost:8000/api/health
```

## 📚 Documentation

### API Documentation
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`
- OpenAPI Spec: `http://localhost:8000/api/openapi.json`

### Code Documentation
- Inline documentation with docstrings
- Type hints throughout the codebase
- Architecture decision records (ADRs)
- API usage examples

## 🔄 Version History

### v1.0.0 (Current)
- Initial release with core functionality
- Activity logging for all learning types
- Pattern recognition and gap analysis
- Personalized recommendation generation
- Progress tracking and reporting
- Parent-child access control

### Future Roadmap
- **Machine Learning Integration**: ML-based recommendation engine
- **Predictive Analytics**: Performance prediction models
- **Real-time Notifications**: WebSocket-based live updates
- **Advanced Analytics**: Deeper learning pattern analysis
- **Mobile App Support**: Native mobile applications
- **Integration APIs**: LMS and educational platform integrations

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch
3. Implement changes with tests
4. Submit pull request with description
5. Code review and integration

### Code Standards
- Follow PEP 8 style guidelines
- Use type hints throughout
- Write comprehensive docstrings
- Add unit tests for new features
- Update documentation for changes

### Git Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## 📞 Support

### Issues & Bug Reports
- Create GitHub issues with detailed descriptions
- Include steps to reproduce
- Provide environment details
- Attach relevant logs and screenshots

### Feature Requests
- Submit feature requests with use cases
- Include priority and business impact
- Discuss implementation approach
- Consider community feedback

---

**Last Updated**: January 2024
**Version**: 1.0.0
**Maintainers**: Mentor AI Team