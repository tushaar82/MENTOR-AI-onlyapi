# Advanced Analytics Service API Documentation

## Overview

The Advanced Analytics Service provides sophisticated analytics capabilities for the Mentor AI platform, including predictive modeling, performance trend analysis, learning pattern recognition, and AI-powered insights generation. It processes student performance data to generate comprehensive analytics with machine learning models and statistical analysis.

## Base URL
```
/api/advanced-analytics
```

## Endpoints

### 1. Generate Predictive Analytics

**Endpoint:** `POST /api/advanced-analytics/predictive/generate`

**Description:** Generate predictive analytics for student performance, including future score predictions, risk assessment, and achievement probability calculations.

**Authentication:** Required (JWT token)

#### Request Example
```bash
curl -X POST "http://localhost:8000/api/advanced-analytics/predictive/generate" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student_123",
    "prediction_type": "performance_forecast",
    "time_horizon_days": 90,
    "subjects": ["Physics", "Chemistry", "Mathematics"],
    "include_confidence_intervals": true,
    "use_historical_data": true
  }'
```

#### Request Body
- `student_id`: ID of the student (required)
- `prediction_type`: Type of prediction (performance_forecast, risk_assessment, goal_achievement, learning_path_optimization)
- `time_horizon_days`: Future prediction period in days (default: 90)
- `subjects`: List of subjects to analyze (optional)
- `include_confidence_intervals`: Include statistical confidence intervals (default: true)
- `use_historical_data`: Use historical performance data (default: true)

#### Expected Response (200 OK)
```json
{
  "success": true,
  "prediction_id": "pred_abc123",
  "student_id": "student_123",
  "prediction_type": "performance_forecast",
  "generated_at": "2024-01-15T10:30:00Z",
  "predictions": {
    "overall_performance": {
      "current_score": 72.5,
      "predicted_score": 78.3,
      "improvement_potential": 5.8,
      "confidence_interval": {
        "lower_bound": 75.2,
        "upper_bound": 81.4,
        "confidence_level": 0.95
      }
    },
    "subject_predictions": {
      "Physics": {
        "current_score": 68.0,
        "predicted_score": 74.5,
        "trend": "improving",
        "key_factors": ["consistent_practice", "concept_mastery"]
      },
      "Chemistry": {
        "current_score": 75.0,
        "predicted_score": 77.8,
        "trend": "stable",
        "key_factors": ["strong_foundation", "regular_revision"]
      },
      "Mathematics": {
        "current_score": 74.5,
        "predicted_score": 82.6,
        "trend": "rapidly_improving",
        "key_factors": ["problem_solving_skills", "practice_frequency"]
      }
    }
  },
  "risk_assessment": {
    "overall_risk_level": "low",
    "risk_factors": [],
    "mitigation_strategies": [
      "Maintain current study pattern",
      "Focus on advanced problem solving"
    ]
  },
  "recommendations": [
    {
      "priority": "high",
      "area": "Mathematics",
      "action": "Increase practice frequency by 20%",
      "expected_impact": "+3.5 points",
      "timeframe": "4 weeks"
    }
  ],
  "model_accuracy": {
    "historical_accuracy": 0.87,
    "sample_size": 245,
    "last_updated": "2024-01-10T00:00:00Z"
  }
}
```

#### Error Scenarios
- **400 Bad Request:** Invalid prediction type or parameters
- **401 Unauthorized:** Authentication required
- **404 Not Found:** Student not found or insufficient data
- **500 Internal Server Error:** Prediction generation failed

---

### 2. Get Learning Pattern Analysis

**Endpoint:** `GET /api/advanced-analytics/patterns/{student_id}`

**Description:** Analyze student's learning patterns including study habits, optimal learning times, knowledge retention patterns, and learning style preferences.

**Authentication:** Required (JWT token)

#### Request Example
```bash
curl -X GET "http://localhost:8000/api/advanced-analytics/patterns/student_123?analysis_period=30&include_recommendations=true" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Query Parameters
- `student_id`: ID of the student (required)
- `analysis_period`: Analysis period in days (default: 30)
- `include_recommendations`: Include AI-generated recommendations (default: true)

#### Expected Response (200 OK)
```json
{
  "success": true,
  "student_id": "student_123",
  "analysis_period": 30,
  "generated_at": "2024-01-15T11:00:00Z",
  "learning_patterns": {
    "study_habits": {
      "preferred_study_times": [
        {"time": "09:00-11:00", "effectiveness_score": 0.85},
        {"time": "19:00-21:00", "effectiveness_score": 0.72}
      ],
      "average_session_duration": 45,
      "optimal_session_length": 50,
      "study_frequency": {
        "days_per_week": 5.2,
        "sessions_per_day": 1.8,
        "consistency_score": 0.78
      }
    },
    "knowledge_retention": {
      "retention_curve": {
        "immediate": 0.95,
        "after_1_day": 0.82,
        "after_1_week": 0.68,
        "after_1_month": 0.54
      },
      "optimal_review_intervals": {
        "initial_review": "1 day",
        "first_revision": "3 days",
        "second_revision": "1 week",
        "final_revision": "1 month"
      },
      "forgetting_rate": 0.12,
      "retention_strategies": ["spaced_repetition", "active_recall", "interleaved_practice"]
    },
    "learning_style": {
      "primary_style": "visual",
      "secondary_style": "kinesthetic",
      "style_scores": {
        "visual": 0.72,
        "auditory": 0.45,
        "kinesthetic": 0.68,
        "reading": 0.58
      },
      "preferred_content_types": ["videos", "diagrams", "interactive_exercises"],
      "effectiveness_by_content_type": {
        "text": 0.65,
        "video": 0.85,
        "interactive": 0.78,
        "audio": 0.52
      }
    },
    "performance_patterns": {
      "best_performance_times": ["morning", "afternoon"],
      "difficulty_progression": {
        "easy": {"accuracy": 0.92, "time_per_question": 45},
        "medium": {"accuracy": 0.74, "time_per_question": 78},
        "hard": {"accuracy": 0.58, "time_per_question": 125}
      },
      "fatigue_patterns": {
        "performance_decline_after_minutes": 60,
        "optimal_break_duration": 15,
        "recommended_study_blocks": ["45-50 minutes"]
      }
    }
  },
  "recommendations": [
    {
      "category": "study_schedule",
      "recommendation": "Schedule Mathematics practice in morning sessions (09:00-11:00)",
      "reason": "85% effectiveness score during this time period",
      "expected_improvement": "+12% accuracy"
    },
    {
      "category": "learning_style",
      "recommendation": "Use more visual content for Physics concepts",
      "reason": "Strong visual learning preference detected",
      "expected_improvement": "+18% concept retention"
    }
  ],
  "pattern_confidence": 0.84
}
```

#### Error Scenarios
- **401 Unauthorized:** Authentication required
- **404 Not Found:** Student not found or insufficient data
- **500 Internal Server Error:** Pattern analysis failed

---

### 3. Generate Comparative Analytics

**Endpoint:** `POST /api/advanced-analytics/comparative/generate`

**Description:** Generate comparative analytics comparing student performance against peer groups, benchmarks, and historical data.

**Authentication:** Required (JWT token)

#### Request Example
```bash
curl -X POST "http://localhost:8000/api/advanced-analytics/comparative/generate" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student_123",
    "comparison_groups": ["same_exam_type", "similar_performance", "same_region"],
    "subjects": ["Physics", "Chemistry", "Mathematics"],
    "time_period_days": 60,
    "include_percentiles": true
  }'
```

#### Request Body
- `student_id`: ID of the student (required)
- `comparison_groups`: Groups to compare against (same_exam_type, similar_performance, same_region, national_average)
- `subjects`: List of subjects for comparison (optional)
- `time_period_days`: Time period for comparison (default: 60)
- `include_percentiles`: Include percentile rankings (default: true)

#### Expected Response (200 OK)
```json
{
  "success": true,
  "comparison_id": "comp_def456",
  "student_id": "student_123",
  "generated_at": "2024-01-15T11:30:00Z",
  "comparative_analysis": {
    "overall_ranking": {
      "total_students_compared": 1250,
      "student_rank": 312,
      "percentile": 75.2,
      "grade": "A",
      "performance_category": "top_quarter"
    },
    "subject_comparisons": {
      "Physics": {
        "student_score": 68.0,
        "peer_average": 62.5,
        "percentile": 78.3,
        "rank": 271,
        "performance_gap": "+5.5",
        "standing": "above_average"
      },
      "Chemistry": {
        "student_score": 75.0,
        "peer_average": 71.2,
        "percentile": 72.1,
        "rank": 349,
        "performance_gap": "+3.8",
        "standing": "above_average"
      },
      "Mathematics": {
        "student_score": 74.5,
        "peer_average": 68.9,
        "percentile": 76.8,
        "rank": 290,
        "performance_gap": "+5.6",
        "standing": "above_average"
      }
    },
    "skill_comparisons": {
      "problem_solving": {
        "student_level": "advanced",
        "peer_level": "intermediate",
        "relative_strength": "strong",
        "percentile": 82.5
      },
      "conceptual_understanding": {
        "student_level": "intermediate",
        "peer_level": "intermediate",
        "relative_strength": "average",
        "percentile": 65.2
      },
      "speed_accuracy": {
        "student_level": "intermediate",
        "peer_level": "intermediate",
        "relative_strength": "average",
        "percentile": 58.7
      }
    },
    "improvement_trends": {
      "student_improvement_rate": 2.8,
      "peer_improvement_rate": 1.9,
      "relative_improvement": "+47%",
      "trend_direction": "outperforming_peers"
    }
  },
  "benchmark_analysis": {
    "exam_targets": {
      "target_score": 85.0,
      "current_gap": 12.5,
      "on_track_probability": 0.73,
      "required_improvement_rate": 3.2
    },
    "top_performer_analysis": {
      "top_10_percentile_score": 88.5,
      "gap_to_top": 14.0,
      "key_differences": ["consistency", "advanced_problem_practice", "revision_frequency"]
    }
  },
  "recommendations": [
    {
      "priority": "high",
      "area": "speed_accuracy",
      "recommendation": "Practice time-bound problem solving",
      "reason": "Below peer average in speed accuracy",
      "expected_improvement": "+8 percentile points"
    }
  ]
}
```

#### Error Scenarios
- **400 Bad Request:** Invalid comparison groups or parameters
- **401 Unauthorized:** Authentication required
- **404 Not Found:** Student not found or insufficient comparison data
- **500 Internal Server Error:** Comparative analysis failed

---

### 4. Get Learning Path Optimization

**Endpoint:** `GET /api/advanced-analytics/learning-path/{student_id}`

**Description:** Generate optimized learning path recommendations based on performance analytics, learning patterns, and predictive models.

**Authentication:** Required (JWT token)

#### Request Example
```bash
curl -X GET "http://localhost:8000/api/advanced-analytics/learning-path/student_123?goal_score=85&time_available_weeks=12&focus_areas=Physics,Mathematics" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Query Parameters
- `student_id`: ID of the student (required)
- `goal_score`: Target score goal (default: 80)
- `time_available_weeks`: Available study time in weeks (default: 16)
- `focus_areas`: Specific subjects to focus on (optional)
- `include_alternatives`: Include alternative paths (default: true)

#### Expected Response (200 OK)
```json
{
  "success": true,
  "student_id": "student_123",
  "learning_path_id": "path_ghi789",
  "generated_at": "2024-01-15T12:00:00Z",
  "goal_analysis": {
    "target_score": 85,
    "current_score": 72.5,
    "improvement_needed": 12.5,
    "achievable_probability": 0.78,
    "estimated_weeks_required": 10,
    "confidence_level": "high"
  },
  "optimized_path": {
    "path_name": "Balanced Improvement Strategy",
    "total_duration_weeks": 12,
    "weekly_study_hours": 25,
    "expected_score": 86.2,
    "success_probability": 0.82,
    "phases": [
      {
        "phase_id": 1,
        "phase_name": "Foundation Strengthening",
        "duration_weeks": 4,
        "focus_areas": ["Mathematics_Basics", "Physics_Fundamentals"],
        "weekly_hours": 20,
        "expected_improvement": "+4.2",
        "key_activities": [
          "Daily practice problems",
          "Concept review sessions",
          "Weekly mock tests"
        ]
      },
      {
        "phase_id": 2,
        "phase_name": "Advanced Problem Solving",
        "duration_weeks": 5,
        "focus_areas": ["Mathematics_Advanced", "Chemistry_Problem_Solving"],
        "weekly_hours": 25,
        "expected_improvement": "+5.1",
        "key_activities": [
          "Complex problem practice",
          "Time-bound tests",
          "Error analysis"
        ]
      },
      {
        "phase_id": 3,
        "phase_name": "Exam Preparation",
        "duration_weeks": 3,
        "focus_areas": ["Full_Syllabus_Revision", "Test_Strategy"],
        "weekly_hours": 30,
        "expected_improvement": "+3.1",
        "key_activities": [
          "Full-length mock tests",
          "Strategy refinement",
          "Weakness targeting"
        ]
      }
    ]
  },
  "subject_priorities": {
    "Physics": {
      "priority": "high",
      "current_level": 68.0,
      "target_level": 85.0,
      "improvement_needed": 17.0,
      "recommended_hours_week": 8,
      "key_topics": ["Thermodynamics", "Optics", "Modern_Physics"]
    },
    "Chemistry": {
      "priority": "medium",
      "current_level": 75.0,
      "target_level": 85.0,
      "improvement_needed": 10.0,
      "recommended_hours_week": 6,
      "key_topics": ["Organic_Chemistry", "Physical_Chemistry"]
    },
    "Mathematics": {
      "priority": "high",
      "current_level": 74.5,
      "target_level": 85.0,
      "improvement_needed": 10.5,
      "recommended_hours_week": 11,
      "key_topics": ["Calculus", "Algebra", "Coordinate_Geometry"]
    }
  },
  "alternative_paths": [
    {
      "path_name": "Intensive Mathematics Focus",
      "success_probability": 0.75,
      "duration_weeks": 10,
      "weekly_hours": 30,
      "expected_score": 84.8,
      "trade_offs": ["Higher study load", "Less focus on Chemistry"]
    }
  ],
  "adaptation_strategy": {
    "review_frequency": "weekly",
    "performance_thresholds": {
      "adjustment_trigger": 5.0,
      "improvement_threshold": 2.0,
      "decline_threshold": -1.5
    },
    "flexibility_factors": ["topic_difficulty", "learning_speed", "external_commitments"]
  }
}
```

#### Error Scenarios
- **401 Unauthorized:** Authentication required
- **404 Not Found:** Student not found or insufficient data
- **500 Internal Server Error:** Learning path optimization failed

---

### 5. Get Performance Anomaly Detection

**Endpoint:** `POST /api/advanced-analytics/anomalies/detect`

**Description:** Detect performance anomalies and unusual learning patterns that may require attention or intervention.

**Authentication:** Required (JWT token)

#### Request Example
```bash
curl -X POST "http://localhost:8000/api/advanced-analytics/anomalies/detect" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student_123",
    "analysis_period_days": 30,
    "anomaly_types": ["performance_decline", "study_pattern_change", "engagement_drop"],
    "sensitivity_level": "medium"
  }'
```

#### Request Body
- `student_id`: ID of the student (required)
- `analysis_period_days`: Period to analyze for anomalies (default: 30)
- `anomaly_types`: Types of anomalies to detect (performance_decline, study_pattern_change, engagement_drop, unusual_errors)
- `sensitivity_level`: Detection sensitivity (low, medium, high)

#### Expected Response (200 OK)
```json
{
  "success": true,
  "anomaly_id": "anom_jkl012",
  "student_id": "student_123",
  "analysis_period": 30,
  "generated_at": "2024-01-15T12:30:00Z",
  "anomalies_detected": [
    {
      "anomaly_type": "performance_decline",
      "severity": "medium",
      "detected_date": "2024-01-14T00:00:00Z",
      "description": "15% performance drop in Mathematics over last 5 days",
      "metrics": {
        "baseline_score": 78.5,
        "current_score": 66.7,
        "decline_percentage": 15.1,
        "statistical_significance": 0.032
      },
      "potential_causes": [
        "Increased difficulty level",
        "Study pattern disruption",
        "Conceptual gaps in new topics"
      ],
      "recommendations": [
        "Review recent Mathematics topics",
        "Reduce difficulty temporarily",
        "Schedule extra practice sessions"
      ],
      "urgency": "address_within_3_days"
    },
    {
      "anomaly_type": "study_pattern_change",
      "severity": "low",
      "detected_date": "2024-01-12T00:00:00Z",
      "description": "Shift from morning to evening study sessions",
      "metrics": {
        "morning_sessions_previous": 85,
        "morning_sessions_current": 30,
        "evening_sessions_previous": 15,
        "evening_sessions_current": 70
      },
      "potential_causes": [
        "Schedule changes",
        "Preference shift",
        "External commitments"
      ],
      "recommendations": [
        "Monitor effectiveness of new pattern",
        "Consider hybrid approach",
        "Evaluate performance impact"
      ],
      "urgency": "monitor"
    }
  ],
  "overall_assessment": {
    "anomaly_count": 2,
    "high_priority_anomalies": 0,
    "medium_priority_anomalies": 1,
    "low_priority_anomalies": 1,
    "overall_status": "requires_attention",
    "next_review_date": "2024-01-22T00:00:00Z"
  },
  "trend_analysis": {
    "performance_trend": "slightly_declining",
    "engagement_trend": "stable",
    "study_consistency": "decreasing",
    "risk_level": "low_to_medium"
  }
}
```

#### Error Scenarios
- **400 Bad Request:** Invalid anomaly types or parameters
- **401 Unauthorized:** Authentication required
- **404 Not Found:** Student not found or insufficient data
- **500 Internal Server Error:** Anomaly detection failed

---

### 6. Get Analytics Summary

**Endpoint:** `GET /api/advanced-analytics/summary/{student_id}`

**Description:** Get comprehensive analytics summary combining all analytics types into a unified dashboard view.

**Authentication:** Required (JWT token)

#### Request Example
```bash
curl -X GET "http://localhost:8000/api/advanced-analytics/summary/student_123?include_predictions=true&include_recommendations=true" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Query Parameters
- `student_id`: ID of the student (required)
- `include_predictions`: Include predictive analytics (default: true)
- `include_recommendations`: Include AI recommendations (default: true)
- `time_period_days`: Analysis time period (default: 30)

#### Expected Response (200 OK)
```json
{
  "success": true,
  "student_id": "student_123",
  "summary_id": "sum_mno345",
  "generated_at": "2024-01-15T13:00:00Z",
  "executive_summary": {
    "current_performance_level": "good",
    "overall_score": 72.5,
    "improvement_trend": "positive",
    "key_strengths": ["Mathematics_Problem_Solving", "Consistency"],
    "key_areas_for_improvement": ["Physics_Concepts", "Speed_Accuracy"],
    "achievement_probability": 0.78,
    "recommended_focus": "Balanced_improvement_strategy"
  },
  "performance_metrics": {
    "current_scores": {
      "Physics": 68.0,
      "Chemistry": 75.0,
      "Mathematics": 74.5
    },
    "predicted_scores": {
      "Physics": 74.5,
      "Chemistry": 77.8,
      "Mathematics": 82.6
    },
    "improvement_potential": {
      "Physics": 6.5,
      "Chemistry": 2.8,
      "Mathematics": 8.1
    }
  },
  "learning_insights": {
    "optimal_study_times": ["09:00-11:00", "19:00-21:00"],
    "learning_style": "visual_kinesthetic",
    "retention_rate": 0.68,
    "study_consistency": 0.78,
    "engagement_level": "high"
  },
  "comparative_analysis": {
    "percentile_ranking": 75.2,
    "peer_comparison": "above_average",
    "subject_standings": {
      "Physics": "above_average",
      "Chemistry": "above_average",
      "Mathematics": "above_average"
    }
  },
  "recommendations": {
    "immediate_actions": [
      "Focus on Physics conceptual understanding",
      "Increase Mathematics practice frequency"
    ],
    "strategic_initiatives": [
      "Implement spaced repetition for better retention",
      "Optimize study schedule based on peak performance times"
    ],
    "long_term_goals": [
      "Achieve 85+ target score in 12 weeks",
      "Maintain top 25% percentile ranking"
    ]
  },
  "alerts_and_anomalies": {
    "active_anomalies": 1,
    "high_priority_alerts": 0,
    "medium_priority_alerts": 1,
    "recent_trends": "Slight_performance_decline_in_Mathematics"
  },
  "next_steps": {
    "review_date": "2024-01-22T00:00:00Z",
    "focus_areas": ["Physics_Thermodynamics", "Mathematics_Calculus"],
    "recommended_actions": ["Extra_practice_sessions", "Concept_review"]
  }
}
```

#### Error Scenarios
- **401 Unauthorized:** Authentication required
- **404 Not Found:** Student not found or insufficient data
- **500 Internal Server Error:** Summary generation failed

---

## Testing Workflows

### Complete Advanced Analytics Workflow

1. **Generate Predictive Analytics**
   ```bash
   curl -X POST "/api/advanced-analytics/predictive/generate" \
     -H "Authorization: Bearer TOKEN" \
     -d '{"student_id": "student_123", "prediction_type": "performance_forecast"}'
   ```

2. **Analyze Learning Patterns**
   ```bash
   curl -X GET "/api/advanced-analytics/patterns/student_123" \
     -H "Authorization: Bearer TOKEN"
   ```

3. **Generate Comparative Analytics**
   ```bash
   curl -X POST "/api/advanced-analytics/comparative/generate" \
     -H "Authorization: Bearer TOKEN" \
     -d '{"student_id": "student_123", "comparison_groups": ["same_exam_type"]}'
   ```

4. **Get Learning Path Optimization**
   ```bash
   curl -X GET "/api/advanced-analytics/learning-path/student_123" \
     -H "Authorization: Bearer TOKEN"
   ```

5. **Detect Anomalies**
   ```bash
   curl -X POST "/api/advanced-analytics/anomalies/detect" \
     -H "Authorization: Bearer TOKEN" \
     -d '{"student_id": "student_123", "anomaly_types": ["performance_decline"]}'
   ```

6. **Get Comprehensive Summary**
   ```bash
   curl -X GET "/api/advanced-analytics/summary/student_123" \
     -H "Authorization: Bearer TOKEN"
   ```

---

## AI-Powered Analytics Features

### Predictive Modeling
- **Performance Forecasting**: ML models predict future performance
- **Risk Assessment**: Identify at-risk areas and intervention points
- **Achievement Probability**: Calculate likelihood of reaching goals
- **Trend Analysis**: Identify performance trends and patterns

### Pattern Recognition
- **Learning Style Detection**: AI identifies preferred learning methods
- **Study Habit Analysis**: Analyze optimal study times and patterns
- **Retention Modeling**: Model knowledge decay and optimal review intervals
- **Engagement Tracking**: Monitor and predict engagement levels

### Comparative Intelligence
- **Peer Benchmarking**: Compare against similar student groups
- **Percentile Rankings**: Statistical positioning analysis
- **Performance Gap Analysis**: Identify areas needing improvement
- **Competitive Analysis**: Benchmark against top performers

---

## Common Issues and Solutions

### 1. Prediction Accuracy Issues
**Problem:** Predictions seem inaccurate or unreliable
**Solution:** 
- Ensure sufficient historical data (minimum 30 days)
- Check data quality and consistency
- Verify student has consistent study patterns
- Consider adjusting prediction time horizon

### 2. Anomaly Detection False Positives
**Problem:** Too many anomaly alerts or false positives
**Solution:** 
- Adjust sensitivity level to medium or low
- Increase analysis period for better baseline
- Verify data quality and consistency
- Review anomaly types to focus on critical areas

### 3. Learning Path Not Realistic
**Problem:** Generated learning path seems too demanding
**Solution:** 
- Adjust time_available_weeks parameter
- Modify target_score to more realistic goal
- Consider alternative paths provided
- Use adaptation strategy for flexible planning

### 4. Comparative Data Issues
**Problem:** Comparative analytics showing insufficient data
**Solution:** 
- Ensure student has sufficient performance history
- Check if comparison groups are appropriate
- Verify exam type and region settings
- Consider longer analysis period

---

## AI Troubleshooting Prompt

Copy and paste this prompt into ChatGPT or Claude when encountering issues:

```
I'm testing Advanced Analytics Service in Mentor AI platform and encountering an issue.

**Endpoint:** [ENDPOINT_URL]
**HTTP Method:** [METHOD]
**Request Payload:** [REQUEST_JSON]
**Error Response:** [ERROR_RESPONSE]
**Expected Behavior:** [DESCRIPTION]

**Context:**
- The Advanced Analytics Service provides ML-powered predictive analytics and pattern recognition
- Predictions use historical performance data and statistical models
- Comparative analytics benchmark against peer groups and historical data
- Learning path optimization uses AI to create personalized study plans
- Anomaly detection identifies unusual patterns requiring attention

**Question:** Can you help me debug this issue by:
1. Analyzing the analytics generation pipeline and ML models
2. Checking if student data is sufficient for analysis type
3. Identifying common issues with predictive accuracy or pattern detection
4. Suggesting specific fixes or debugging steps

**Additional Information:**
- Student ID: [STUDENT_ID]
- Analysis Type: [PREDICTION/PATTERN/COMPARATIVE/LEARNING_PATH/ANOMALY]
- Time Period: [ANALYSIS_PERIOD_DAYS]
- [Add any relevant logs or observations]
```

---

## Related Models and Services

### Models
- `models.advanced_analytics_models.PredictiveAnalyticsRequest`
- `models.advanced_analytics_models.PredictiveAnalyticsResponse`
- `models.advanced_analytics_models.LearningPatternAnalysis`
- `models.advanced_analytics_models.ComparativeAnalytics`
- `models.advanced_analytics_models.LearningPathOptimization`
- `models.advanced_analytics_models.AnomalyDetection`
- `models.advanced_analytics_models.AnalyticsSummary`

### Services
- `services.advanced_analytics_service.AdvancedAnalyticsService`
- `services.predictive_modeling_service.PredictiveModelingService`
- `services.pattern_recognition_service.PatternRecognitionService`
- `services.comparative_analysis_service.ComparativeAnalysisService`

### Dependencies
- `services.ml_model_service.MLModelService`
- `services.analytics_data_service.AnalyticsDataService`
- `services.performance_analytics.PerformanceAnalytics`

---

## Performance Considerations

1. **ML Model Inference**: Predictive analytics take 2-5 seconds
2. **Data Processing**: Pattern analysis requires 30+ days of data
3. **Caching**: Analytics results cached for 6 hours
4. **Batch Processing**: Comparative analytics processed in batches
5. **Resource Usage**: High memory usage for complex ML models

---

## Security Notes

1. **Data Privacy**: All analytics data anonymized for comparisons
2. **Access Control**: Students can only access their own analytics
3. **Model Security**: ML models protected and version controlled
4. **Data Retention**: Analytics data retained according to privacy policies
5. **Audit Logging**: All analytics generations and retrievals are logged

---

## Testing Best Practices

1. **Data Quality**: Ensure sufficient and clean historical data
2. **Model Validation**: Test prediction accuracy with known outcomes
3. **Edge Cases**: Test with students having limited data
4. **Performance Testing**: Test with various analysis periods and complexity
5. **Integration Testing**: Verify with learning management and test systems