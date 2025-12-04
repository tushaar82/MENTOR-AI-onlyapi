# Parent Resource Library API Documentation

## Overview

The Parent Resource Library provides comprehensive educational resources, parenting guides, learning strategies, and support materials for parents to effectively support their child's educational journey. It features AI-powered resource generation, personalized recommendations, community contributions, and expert-curated content.

## Base URL
```
/api/parent-resources
```

## Endpoints

### 1. Generate Educational Resource

**Endpoint:** `POST /api/parent-resources/generate`

**Description:** Generate AI-powered educational resources tailored to specific needs, subjects, and learning objectives.

**Authentication:** Required (JWT token - parent account)

#### Request Example
```bash
curl -X POST "http://localhost:8000/api/parent-resources/generate" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "parent_id": "parent_123",
    "resource_type": "guide",
    "category": "study_strategies",
    "subject": "mathematics",
    "child_age": 15,
    "learning_style": "visual",
    "specific_needs": ["exam_preparation", "motivation"],
    "language": "english",
    "difficulty_level": "intermediate"
  }'
```

#### Request Body
- `parent_id`: ID of the parent (required)
- `resource_type`: Type of resource (guide, article, video, worksheet, activity, template)
- `category`: Resource category (study_strategies, subject_specific, exam_preparation, motivation, parenting_tips, learning_disabilities, career_guidance, time_management)
- `subject`: Specific subject (optional)
- `child_age`: Age of child (required)
- `learning_style`: Child's learning style (visual, auditory, kinesthetic, reading)
- `specific_needs`: Specific needs or goals (optional)
- `language`: Resource language (default: english)
- `difficulty_level`: Content difficulty (beginner, intermediate, advanced, mixed)

#### Expected Response (200 OK)
```json
{
  "success": true,
  "resource_id": "res_abc123",
  "parent_id": "parent_123",
  "generated_at": "2024-01-15T10:30:00Z",
  "resource": {
    "title": "Effective Mathematics Study Strategies for Teenagers",
    "description": "Comprehensive guide for parents to support their teenager's mathematics learning journey",
    "resource_type": "guide",
    "category": "study_strategies",
    "subject": "mathematics",
    "age_group": "teenager",
    "difficulty_level": "intermediate",
    "language": "english",
    "content": {
      "introduction": "Mathematics can be challenging for teenagers, but with the right support and strategies, parents can play a crucial role in their success...",
      "key_strategies": [
        {
          "strategy": "Create a Dedicated Study Environment",
          "description": "Establish a quiet, well-lit space specifically for mathematics study",
          "implementation_steps": [
            "Choose a location away from distractions",
            "Ensure proper lighting and comfortable seating",
            "Organize materials and supplies",
            "Set consistent study times"
          ],
          "benefits": ["Improved focus", "Better retention", "Reduced stress"],
          "time_investment": "30 minutes setup, ongoing maintenance"
        },
        {
          "strategy": "Use Visual Learning Aids",
          "description": "Leverage visual tools to make abstract concepts concrete",
          "implementation_steps": [
            "Use graph paper for geometry problems",
            "Create color-coded formulas",
            "Utilize online visualization tools",
            "Draw diagrams for word problems"
          ],
          "benefits": ["Better conceptual understanding", "Enhanced memory", "Increased engagement"],
          "time_investment": "15-20 minutes per study session"
        }
      ],
      "common_challenges": [
        {
          "challenge": "Math Anxiety",
          "signs": ["Avoidance of math tasks", "Physical symptoms during math work", "Negative self-talk"],
          "solutions": [
            "Practice relaxation techniques",
            "Break problems into smaller steps",
            "Celebrate small successes",
            "Seek professional help if needed"
          ]
        },
        {
          "challenge": "Lack of Motivation",
          "signs": ["Procrastination", "Incomplete assignments", "Disinterest in math topics"],
          "solutions": [
            "Connect math to real-world applications",
            "Set achievable goals",
            "Use gamified learning apps",
            "Find math role models"
          ]
        }
      ],
      "parent_child_activities": [
        {
          "activity": "Math in Daily Life",
          "description": "Find and discuss mathematics in everyday situations",
          "examples": [
            "Calculate shopping discounts and sales tax",
            "Measure ingredients for cooking",
            "Plan a budget for a family outing",
            "Analyze sports statistics"
          ],
          "frequency": "2-3 times per week",
          "duration": "15-30 minutes"
        }
      ],
      "resources_and_tools": [
        {
          "tool_name": "Khan Academy",
          "description": "Free online math lessons and practice",
          "url": "https://www.khanacademy.org/math",
          "cost": "Free",
          "age_appropriateness": "All ages"
        },
        {
          "tool_name": "GeoGebra",
          "description": "Interactive geometry and algebra software",
          "url": "https://www.geogebra.org",
          "cost": "Free",
          "age_appropriateness": "12+ years"
        }
      ],
      "monitoring_progress": {
        "what_to_track": ["Homework completion", "Test scores", "Attitude changes", "Study habits"],
        "tracking_methods": ["Weekly check-ins", "Progress charts", "Teacher communication"],
        "celebration_milestones": ["Consistent effort", "Grade improvements", "Problem-solving breakthroughs"]
      }
    },
    "personalization": {
      "learning_style_adapted": true,
      "age_appropriate": true,
      "specific_needs_addressed": ["exam_preparation", "motivation"],
      "cultural_considerations": "General approach adaptable to various cultural contexts"
    },
    "metadata": {
      "word_count": 1850,
      "estimated_reading_time": "7-10 minutes",
      "content_quality_score": 8.5,
      "expert_reviewed": false,
      "last_updated": "2024-01-15T10:30:00Z"
    }
  }
}
```

#### Error Scenarios
- **400 Bad Request:** Invalid parameters or missing required fields
- **401 Unauthorized:** Authentication required
- **403 Forbidden:** Not authorized to generate resources
- **500 Internal Server Error:** Resource generation failed

---

### 2. Search Resources

**Endpoint:** `POST /api/parent-resources/search`

**Description:** Search the resource library with AI-powered filtering and personalized recommendations.

**Authentication:** Required (JWT token - parent account)

#### Request Example
```bash
curl -X POST "http://localhost:8000/api/parent-resources/search" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "parent_id": "parent_123",
    "query": "helping with physics homework",
    "filters": {
      "resource_type": ["guide", "video"],
      "category": "subject_specific",
      "subject": "physics",
      "age_group": "teenager",
      "difficulty_level": "intermediate"
    },
    "sort_by": "relevance",
    "limit": 20,
    "include_personalized": true
  }'
```

#### Request Body
- `parent_id`: ID of the parent (required)
- `query`: Search query (required)
- `filters`: Search filters (optional)
- `sort_by`: Sort criteria (relevance, popularity, rating, date_created, effectiveness)
- `limit`: Maximum results (default: 10, max: 50)
- `include_personalized`: Include personalized recommendations (default: true)

#### Expected Response (200 OK)
```json
{
  "success": true,
  "search_id": "search_def456",
  "parent_id": "parent_123",
  "searched_at": "2024-01-15T11:00:00Z",
  "query": "helping with physics homework",
  "results": [
    {
      "resource_id": "res_ghi789",
      "title": "Parent's Guide to Physics Homework Support",
      "description": "Strategies and techniques for parents to help with physics homework",
      "resource_type": "guide",
      "category": "subject_specific",
      "subject": "physics",
      "age_group": "teenager",
      "difficulty_level": "intermediate",
      "language": "english",
      "quality_score": 9.2,
      "effectiveness_rating": 4.5,
      "usage_count": 342,
      "user_ratings": {
        "average": 4.3,
        "total_ratings": 28
      },
      "personalization_match": 0.87,
      "relevance_score": 0.94,
      "created_at": "2024-01-10T14:30:00Z",
      "updated_at": "2024-01-14T09:15:00Z",
      "tags": ["homework", "physics", "parent_support", "teenagers"],
      "preview": {
        "key_points": [
          "Understanding physics concepts yourself",
          "Creating effective study routines",
          "Using everyday examples to explain physics"
        ],
        "estimated_reading_time": "5-7 minutes"
      }
    },
    {
      "resource_id": "res_jkl012",
      "title": "Physics Experiments at Home",
      "description": "Simple physics experiments parents can do with children at home",
      "resource_type": "video",
      "category": "subject_specific",
      "subject": "physics",
      "age_group": "teenager",
      "difficulty_level": "beginner",
      "language": "english",
      "quality_score": 8.8,
      "effectiveness_rating": 4.7,
      "usage_count": 256,
      "user_ratings": {
        "average": 4.6,
        "total_ratings": 19
      },
      "personalization_match": 0.72,
      "relevance_score": 0.89,
      "created_at": "2024-01-08T16:45:00Z",
      "updated_at": "2024-01-12T11:20:00Z",
      "tags": ["experiments", "hands_on", "physics", "parent_child"],
      "preview": {
        "duration": "12:30",
        "experiments_count": 5,
        "materials_needed": "Common household items"
      }
    }
  ],
  "search_metadata": {
    "total_found": 47,
    "returned": 20,
    "has_more": true,
    "next_cursor": "cursor_abc123",
    "search_time_ms": 245,
    "personalization_applied": true,
    "quality_filtered": true,
    "recommendations": [
      "Try searching for 'physics study strategies' for more comprehensive results",
      "Consider resources with video content for visual demonstrations"
    ]
  },
  "personalized_suggestions": [
    {
      "suggestion": "Based on your child's interest in astronomy, consider 'Physics of Space' resources",
      "reason": "Previous searches show interest in space-related topics",
      "confidence": 0.78
    }
  ]
}
```

#### Error Scenarios
- **400 Bad Request:** Invalid search parameters
- **401 Unauthorized:** Authentication required
- **500 Internal Server Error:** Search processing failed

---

### 3. Get Resource Details

**Endpoint:** `GET /api/parent-resources/{resource_id}`

**Description:** Get detailed information about a specific resource including full content and related resources.

**Authentication:** Required (JWT token - parent account)

#### Request Example
```bash
curl -X GET "http://localhost:8000/api/parent-resources/res_ghi789?include_related=true&include_reviews=true" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Query Parameters
- `resource_id`: ID of the resource (required)
- `include_related`: Include related resources (default: true)
- `include_reviews`: Include user reviews (default: true)

#### Expected Response (200 OK)
```json
{
  "success": true,
  "resource_id": "res_ghi789",
  "retrieved_at": "2024-01-15T11:30:00Z",
  "resource": {
    "title": "Parent's Guide to Physics Homework Support",
    "description": "Comprehensive strategies for parents to effectively support their children with physics homework",
    "resource_type": "guide",
    "category": "subject_specific",
    "subject": "physics",
    "age_group": "teenager",
    "difficulty_level": "intermediate",
    "language": "english",
    "content": {
      "introduction": "Physics can be intimidating for both students and parents. This guide provides practical strategies...",
      "sections": [
        {
          "section_id": 1,
          "title": "Understanding Physics Basics",
          "content": "Before helping your child, it's important to have a basic understanding of key physics concepts...",
          "key_concepts": ["Forces and motion", "Energy and momentum", "Waves and optics"],
          "parent_friendly_explanations": [
            "Force is simply a push or pull",
            "Energy is the ability to do work",
            "Waves are disturbances that transfer energy"
          ]
        },
        {
          "section_id": 2,
          "title": "Creating a Supportive Environment",
          "content": "The right environment can make homework time more productive and less stressful...",
          "environmental_factors": [
            "Quiet, well-lit study space",
            "Access to necessary materials",
            "Minimal distractions",
            "Positive attitude toward physics"
          ]
        }
      ],
      "practical_strategies": [
        {
          "strategy": "Ask Guiding Questions",
          "description": "Instead of giving answers, guide your child through problem-solving",
          "examples": [
            "What information do we know from the problem?",
            "What formula might help here?",
            "Does this answer make sense?"
          ]
        }
      ],
      "common_mistakes": [
        {
          "mistake": "Doing the homework for the child",
          "consequence": "Child doesn't learn problem-solving skills",
          "alternative": "Guide through the process step by step"
        }
      ]
    },
    "interactive_elements": [
      {
        "type": "checklist",
        "title": "Homework Support Checklist",
        "items": [
          "Review the assignment together",
          "Break down complex problems",
          "Provide guidance, not answers",
          "Celebrate effort and progress"
        ]
      },
      {
        "type": "template",
        "title": "Problem-Solving Template",
        "content": "1. Identify given information\n2. Determine what to find\n3. Choose appropriate formula\n4. Solve step by step\n5. Check the answer"
      }
    ],
    "assessment_tools": [
      {
        "tool_name": "Understanding Check",
        "description": "Quick questions to assess child's understanding",
        "questions": [
          "Can you explain this concept in your own words?",
          "How would you apply this to a real-life situation?",
          "What part is most confusing?"
        ]
      }
    ]
  },
  "metadata": {
    "author": "Dr. Sarah Johnson, Physics Education Specialist",
    "created_at": "2024-01-10T14:30:00Z",
    "updated_at": "2024-01-14T09:15:00Z",
    "word_count": 2200,
    "estimated_reading_time": "8-12 minutes",
    "content_quality_score": 9.2,
    "expert_reviewed": true,
    "last_reviewed": "2024-01-12T16:45:00Z",
    "version": "2.1"
  },
  "usage_stats": {
    "total_views": 1847,
    "unique_parents": 892,
    "average_time_spent": "9.5 minutes",
    "completion_rate": 0.78,
    "bookmark_count": 234,
    "share_count": 156
  },
  "effectiveness_data": {
    "average_rating": 4.3,
    "total_ratings": 28,
    "effectiveness_score": 4.5,
    "parent_testimonials": [
      {
        "parent_id": "parent_456",
        "testimonial": "This guide transformed homework time from stressful to productive!",
        "rating": 5,
        "date": "2024-01-12T10:30:00Z"
      }
    ],
    "measured_outcomes": {
      "homework_completion_improvement": 0.35,
      "parent_confidence_increase": 0.42,
      "child_understanding_improvement": 0.28
    }
  },
  "related_resources": [
    {
      "resource_id": "res_mno345",
      "title": "Physics Experiments for Family Learning",
      "relationship": "complementary",
      "relevance_score": 0.85
    },
    {
      "resource_id": "res_pqr678",
      "title": "Math-Physics Connection Guide",
      "relationship": "related_subject",
      "relevance_score": 0.72
    }
  ],
  "reviews": [
    {
      "review_id": "rev_stu901",
      "parent_id": "parent_789",
      "rating": 5,
      "title": "Exactly what I needed!",
      "comment": "Clear, practical advice that I could implement immediately. My child's attitude toward physics has improved dramatically.",
      "helpful_count": 12,
      "created_at": "2024-01-13T14:20:00Z"
    }
  ]
}
```

#### Error Scenarios
- **401 Unauthorized:** Authentication required
- **404 Not Found:** Resource not found
- **500 Internal Server Error:** Resource retrieval failed

---

### 4. Rate Resource

**Endpoint:** `POST /api/parent-resources/{resource_id}/rate`

**Description:** Rate and review a resource, providing feedback for quality improvement and community benefit.

**Authentication:** Required (JWT token - parent account)

#### Request Example
```bash
curl -X POST "http://localhost:8000/api/parent-resources/res_ghi789/rate" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "parent_id": "parent_123",
    "rating": 4,
    "title": "Very helpful guide",
    "comment": "The strategies were practical and easy to implement. My child is now more confident with physics homework.",
    "effectiveness_score": 4,
    "would_recommend": true,
    "used_with_child_age": 15,
    "implementation_difficulty": "easy",
    "tags": ["practical", "easy_to_implement", "effective"]
  }'
```

#### Request Body
- `parent_id`: ID of the parent (required)
- `rating`: Overall rating (1-5) (required)
- `title`: Review title (optional)
- `comment`: Detailed review (optional)
- `effectiveness_score**: Effectiveness rating (1-5) (optional)
- `would_recommend`: Would recommend to others (default: true)
- `used_with_child_age`: Age of child when used (optional)
- `implementation_difficulty**: How easy to implement (easy, medium, hard)
- `tags**: User-defined tags (optional)

#### Expected Response (200 OK)
```json
{
  "success": true,
  "review_id": "rev_xyz789",
  "resource_id": "res_ghi789",
  "parent_id": "parent_123",
  "submitted_at": "2024-01-15T12:00:00Z",
  "review": {
    "rating": 4,
    "title": "Very helpful guide",
    "comment": "The strategies were practical and easy to implement. My child is now more confident with physics homework.",
    "effectiveness_score": 4,
    "would_recommend": true,
    "used_with_child_age": 15,
    "implementation_difficulty": "easy",
    "tags": ["practical", "easy_to_implement", "effective"],
    "verified_purchase": false,
    "helpful_count": 0
  },
  "updated_resource_stats": {
    "average_rating": 4.32,
    "total_ratings": 29,
    "average_effectiveness": 4.45,
    "recommendation_percentage": 0.93,
    "implementation_difficulty_distribution": {
      "easy": 0.65,
      "medium": 0.30,
      "hard": 0.05
    }
  },
  "impact_analysis": {
    "rating_impact": "+0.02",
    "trend_direction": "positive",
    "community_value": "high",
    "quality_indicator": "improving"
  }
}
```

#### Error Scenarios
- **400 Bad Request:** Invalid rating or review data
- **401 Unauthorized:** Authentication required
- **404 Not Found:** Resource not found
- **409 Conflict:** Review already exists
- **500 Internal Server Error:** Rating submission failed

---

### 5. Get Personalized Recommendations

**Endpoint:** `GET /api/parent-resources/recommendations/{parent_id}`

**Description:** Get AI-powered personalized resource recommendations based on parent profile, child's needs, and usage patterns.

**Authentication:** Required (JWT token - parent account)

#### Request Example
```bash
curl -X GET "http://localhost:8000/api/parent-resources/recommendations/parent_123?limit=15&include_reasoning=true&category=all" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Query Parameters
- `parent_id`: ID of the parent (required)
- `limit`: Maximum recommendations (default: 10, max: 25)
- `include_reasoning`: Include AI reasoning (default: true)
- `category`: Filter by category (all, study_strategies, subject_specific, etc.)

#### Expected Response (200 OK)
```json
{
  "success": true,
  "parent_id": "parent_123",
  "recommendation_id": "rec_abc123",
  "generated_at": "2024-01-15T13:00:00Z",
  "recommendations": [
    {
      "resource_id": "res_def456",
      "title": "Supporting Teenager's Study Independence",
      "description": "Guide for parents to foster independent study habits in teenagers",
      "resource_type": "guide",
      "category": "study_strategies",
      "recommendation_score": 0.92,
      "confidence_level": "high",
      "personalization_reasoning": {
        "primary_factors": [
          {
            "factor": "child_age_appropriate",
            "weight": 0.35,
            "explanation": "Your child is 15, entering the age where independence becomes crucial"
          },
          {
            "factor": "previous_engagement",
            "weight": 0.25,
            "explanation": "You've shown interest in study strategy resources"
          },
          {
            "factor": "effectiveness_correlation",
            "weight": 0.20,
            "explanation": "Similar parents found this resource highly effective"
          }
        ],
        "secondary_factors": [
          {
            "factor": "learning_style_match",
            "weight": 0.15,
            "explanation": "Matches your child's visual learning preference"
          },
          {
            "factor": "time_availability",
            "weight": 0.05,
            "explanation": "Fits your available time for implementation"
          }
        ],
        "overall_match_score": 0.92,
        "explanation": "This resource is highly recommended because it addresses your teenager's developmental stage and matches your previous engagement patterns with study strategy content"
      },
      "resource_preview": {
        "key_benefits": [
          "Builds independent study skills",
          "Reduces parent-child conflicts over homework",
          "Improves long-term academic success"
        ],
        "implementation_time": "2-3 weeks to see results",
        "difficulty": "medium"
      }
    },
    {
      "resource_id": "res_ghi789",
      "title": "Physics Homework Support Strategies",
      "description": "Practical techniques for helping with physics homework",
      "resource_type": "guide",
      "category": "subject_specific",
      "subject": "physics",
      "recommendation_score": 0.87,
      "confidence_level": "high",
      "personalization_reasoning": {
        "primary_factors": [
          {
            "factor": "subject_relevance",
            "weight": 0.40,
            "explanation": "Your child recently struggled with physics homework"
          },
          {
            "factor": "timeliness",
            "weight": 0.30,
            "explanation": "Current physics challenges require immediate support"
          }
        ],
        "explanation": "Recommended due to recent physics homework difficulties and high relevance to current academic needs"
      },
      "resource_preview": {
        "key_benefits": [
          "Immediate applicability",
          "Reduces homework stress",
          "Improves physics understanding"
        ],
        "implementation_time": "Immediate",
        "difficulty": "easy"
      }
    }
  ],
  "recommendation_metadata": {
    "total_recommendations": 12,
    "algorithm_version": "v3.2",
    "data_freshness": "2024-01-15T00:00:00Z",
    "personalization_factors_used": [
      "child_profile",
      "parent_preferences",
      "usage_history",
      "effectiveness_data",
      "peer_similarity"
    ],
    "confidence_distribution": {
      "high": 8,
      "medium": 3,
      "low": 1
    }
  },
  "improvement_suggestions": [
    {
      "suggestion": "Complete your child's learning profile",
      "benefit": "More accurate personalized recommendations",
      "time_required": "5 minutes"
    },
    {
      "suggestion": "Rate resources you've used",
      "benefit": "Improve recommendation algorithm accuracy",
      "time_required": "2 minutes per resource"
    }
  ]
}
```

#### Error Scenarios
- **401 Unauthorized:** Authentication required
- **404 Not Found:** Parent profile not found
- **500 Internal Server Error:** Recommendation generation failed

---

### 6. Create Custom Resource Collection

**Endpoint:** `POST /api/parent-resources/collections/create`

**Description:** Create a custom collection of resources for easy access and organization.

**Authentication:** Required (JWT token - parent account)

#### Request Example
```bash
curl -X POST "http://localhost:8000/api/parent-resources/collections/create" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "parent_id": "parent_123",
    "collection_name": "Mathematics Support Resources",
    "description": "Collection of resources for supporting my child with mathematics learning",
    "visibility": "private",
    "tags": ["mathematics", "homework_support", "middle_school"],
    "resource_ids": ["res_def456", "res_ghi789", "res_jkl012"]
  }'
```

#### Request Body
- `parent_id`: ID of the parent (required)
- `collection_name`: Name of the collection (required)
- `description`: Collection description (optional)
- `visibility`: Collection visibility (private, shared, public)
- `tags`: Collection tags (optional)
- `resource_ids`: List of resource IDs to include (optional)

#### Expected Response (200 OK)
```json
{
  "success": true,
  "collection_id": "coll_mno345",
  "parent_id": "parent_123",
  "created_at": "2024-01-15T14:00:00Z",
  "collection": {
    "name": "Mathematics Support Resources",
    "description": "Collection of resources for supporting my child with mathematics learning",
    "visibility": "private",
    "tags": ["mathematics", "homework_support", "middle_school"],
    "resources": [
      {
        "resource_id": "res_def456",
        "title": "Supporting Teenager's Study Independence",
        "added_at": "2024-01-15T14:00:00Z",
        "custom_notes": "Great for building independence"
      },
      {
        "resource_id": "res_ghi789",
        "title": "Physics Homework Support Strategies",
        "added_at": "2024-01-15T14:00:00Z",
        "custom_notes": "Helpful for current physics challenges"
      },
      {
        "resource_id": "res_jkl012",
        "title": "Math Problem-Solving Techniques",
        "added_at": "2024-01-15T14:00:00Z",
        "custom_notes": "Excellent step-by-step approach"
      }
    ],
    "metadata": {
      "total_resources": 3,
      "total_reading_time": "25-35 minutes",
      "average_rating": 4.4,
      "collection_quality_score": 8.7,
      "last_updated": "2024-01-15T14:00:00Z"
    }
  },
  "sharing_info": {
    "share_url": null,
    "share_code": null,
    "can_share": true,
    "sharing_permissions": ["view", "comment"]
  }
}
```

#### Error Scenarios
- **400 Bad Request:** Invalid collection data
- **401 Unauthorized:** Authentication required
- **403 Forbidden:** Not authorized to create collections
- **500 Internal Server Error:** Collection creation failed

---

### 7. Get Community Resources

**Endpoint:** `GET /api/parent-resources/community`

**Description:** Get community-contributed resources, expert-curated content, and trending materials.

**Authentication:** Required (JWT token - parent account)

#### Request Example
```bash
curl -X GET "http://localhost:8000/api/parent-resources/community?sort=trending&category=all&limit=20&include_expert_curated=true" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Query Parameters
- `sort`: Sort criteria (trending, newest, highest_rated, most_discussed)
- `category`: Filter by category (all, study_strategies, subject_specific, etc.)
- `limit`: Maximum results (default: 10, max: 50)
- `include_expert_curated`: Include expert-curated content (default: true)

#### Expected Response (200 OK)
```json
{
  "success": true,
  "retrieved_at": "2024-01-15T15:00:00Z",
  "community_resources": [
    {
      "resource_id": "res_pqr678",
      "title": "Creative Ways to Teach Algebra at Home",
      "description": "Innovative methods for making algebra concepts understandable",
      "resource_type": "guide",
      "category": "subject_specific",
      "subject": "mathematics",
      "author": {
        "parent_id": "parent_456",
        "name": "Emily Rodriguez",
        "verified": true,
        "contribution_count": 12,
        "average_rating": 4.6
      },
      "community_stats": {
        "views": 1234,
        "downloads": 567,
        "ratings": 34,
        "average_rating": 4.7,
        "comments": 23,
        "shares": 89,
        "trending_score": 8.9
      },
      "expert_validation": {
        "curated": true,
        "expert": "Dr. Michael Chen, Mathematics Education",
        "review": "Excellent practical approach with strong pedagogical foundation",
        "expert_rating": 4.8
      },
      "created_at": "2024-01-12T10:30:00Z",
      "updated_at": "2024-01-14T16:45:00Z"
    },
    {
      "resource_id": "res_stu901",
      "title": "Managing Screen Time During Study Hours",
      "description": "Strategies for balancing technology use and focused study time",
      "resource_type": "article",
      "category": "time_management",
      "author": {
        "parent_id": "parent_789",
        "name": "David Thompson",
        "verified": false,
        "contribution_count": 5,
        "average_rating": 4.2
      },
      "community_stats": {
        "views": 892,
        "downloads": 234,
        "ratings": 18,
        "average_rating": 4.1,
        "comments": 15,
        "shares": 45,
        "trending_score": 7.8
      },
      "expert_validation": {
        "curated": false,
        "pending_review": true
      },
      "created_at": "2024-01-10T14:20:00Z",
      "updated_at": "2024-01-13T09:15:00Z"
    }
  ],
  "expert_curated_section": {
    "title": "Expert Picks of the Week",
    "curator": "Dr. Sarah Johnson, Child Psychology",
    "resources": [
      {
        "resource_id": "res_vwx234",
        "title": "Building Resilience in Young Learners",
        "expert_comment": "Evidence-based strategies that show remarkable effectiveness",
        "expert_rating": 4.9
      }
    ]
  },
  "trending_topics": [
    {
      "topic": "homework_motivation",
      "resource_count": 23,
      "growth_percentage": 45.2,
      "average_rating": 4.3
    },
    {
      "topic": "exam_stress_management",
      "resource_count": 18,
      "growth_percentage": 38.7,
      "average_rating": 4.5
    }
  ],
  "community_stats": {
    "total_resources": 1847,
    "active_contributors": 234,
    "expert_curated": 156,
    "average_quality_score": 7.8,
    "community_growth_rate": 0.12
  }
}
```

#### Error Scenarios
- **401 Unauthorized:** Authentication required
- **500 Internal Server Error:** Community data retrieval failed

---

### 8. Submit Resource to Community

**Endpoint:** `POST /api/parent-resources/community/submit`

**Description:** Submit a resource to share with the community, including expert review process.

**Authentication:** Required (JWT token - parent account)

#### Request Example
```bash
curl -X POST "http://localhost:8000/api/parent-resources/community/submit" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "parent_id": "parent_123",
    "resource": {
      "title": "Math Games for Family Game Night",
      "description": "Educational math games that make learning fun for the whole family",
      "resource_type": "activity",
      "category": "study_strategies",
      "subject": "mathematics",
      "age_group": "mixed",
      "difficulty_level": "beginner",
      "language": "english",
      "content": {
        "introduction": "Making mathematics fun through family games...",
        "materials_needed": ["Dice", "Playing cards", "Paper", "Pencils"],
        "games": [
          {
            "name": "Math Bingo",
            "description": "Bingo game with math problems",
            "players": "2-6",
            "age_range": "7-12",
            "skills_practiced": ["Addition", "Subtraction", "Multiplication"]
          }
        ]
      },
      "estimated_preparation_time": "15 minutes",
      "estimated_activity_time": "30-45 minutes",
      "learning_objectives": ["Practice basic math skills", "Make learning fun", "Family bonding"]
    },
    "submission_notes": "These games have been very effective with my own children",
    "request_expert_review": true
  }'
```

#### Request Body
- `parent_id`: ID of the parent (required)
- `resource`: Complete resource object (required)
- `submission_notes`: Notes for reviewers (optional)
- `request_expert_review`: Request expert review (default: true)

#### Expected Response (200 OK)
```json
{
  "success": true,
  "submission_id": "sub_yza567",
  "parent_id": "parent_123",
  "submitted_at": "2024-01-15T16:00:00Z",
  "submission": {
    "resource_id": "res_pending_123",
    "title": "Math Games for Family Game Night",
    "status": "pending_review",
    "review_queue_position": 12,
    "estimated_review_time": "3-5 business days",
    "submission_type": "community_contribution",
    "expert_review_requested": true
  },
  "review_process": {
    "steps": [
      {
        "step": 1,
        "name": "Content Quality Check",
        "description": "Verify content meets quality standards",
        "estimated_time": "1 day"
      },
      {
        "step": 2,
        "name": "Educational Value Assessment",
        "description": "Evaluate learning effectiveness",
        "estimated_time": "2 days"
      },
      {
        "step": 3,
        "name": "Expert Review",
        "description": "Subject matter expert evaluation",
        "estimated_time": "1-2 days"
      }
    ],
    "review_criteria": [
      "Educational value",
      "Age appropriateness",
      "Clarity and organization",
      "Practical applicability",
      "Originality"
    ]
  },
  "notification_settings": {
    "email_updates": true,
    "status_changes": true,
    "review_completion": true,
    "publication": true
  }
}
```

#### Error Scenarios
- **400 Bad Request:** Invalid resource data or missing required fields
- **401 Unauthorized:** Authentication required
- **403 Forbidden:** Not authorized to submit resources
- **500 Internal Server Error:** Submission processing failed

---

## Testing Workflows

### Complete Parent Resource Library Workflow

1. **Generate Personalized Resource**
   ```bash
   curl -X POST "/api/parent-resources/generate" \
     -H "Authorization: Bearer TOKEN" \
     -d '{"parent_id": "parent_123", "resource_type": "guide", "category": "study_strategies"}'
   ```

2. **Search for Resources**
   ```bash
   curl -X POST "/api/parent-resources/search" \
     -H "Authorization: Bearer TOKEN" \
     -d '{"parent_id": "parent_123", "query": "homework help"}'
   ```

3. **Get Resource Details**
   ```bash
   curl -X GET "/api/parent-resources/res_ghi789" \
     -H "Authorization: Bearer TOKEN"
   ```

4. **Rate Resource**
   ```bash
   curl -X POST "/api/parent-resources/res_ghi789/rate" \
     -H "Authorization: Bearer TOKEN" \
     -d '{"parent_id": "parent_123", "rating": 4, "comment": "Very helpful"}'
   ```

5. **Get Personalized Recommendations**
   ```bash
   curl -X GET "/api/parent-resources/recommendations/parent_123" \
     -H "Authorization: Bearer TOKEN"
   ```

6. **Create Resource Collection**
   ```bash
   curl -X POST "/api/parent-resources/collections/create" \
     -H "Authorization: Bearer TOKEN" \
     -d '{"parent_id": "parent_123", "collection_name": "Math Support"}'
   ```

7. **Get Community Resources**
   ```bash
   curl -X GET "/api/parent-resources/community?sort=trending" \
     -H "Authorization: Bearer TOKEN"
   ```

8. **Submit Resource to Community**
   ```bash
   curl -X POST "/api/parent-resources/community/submit" \
     -H "Authorization: Bearer TOKEN" \
     -d '{"parent_id": "parent_123", "resource": {...}}'
   ```

---

## AI-Powered Features

### Personalization Engine
- **Learning Style Adaptation**: Content adapted to child's learning preferences
- **Age-Appropriate Content**: AI ensures content matches developmental stage
- **Interest-Based Recommendations**: Resources matched to child's interests
- **Effectiveness Prediction**: AI predicts resource effectiveness for specific situations

### Content Generation
- **Context-Aware Generation**: Resources consider family context and constraints
- **Multi-Language Support**: Content generation in multiple languages
- **Cultural Sensitivity**: AI adapts content to cultural contexts
- **Expert Knowledge Integration**: Incorporates educational best practices

### Quality Assurance
- **Automated Content Review**: AI checks for quality and appropriateness
- **Expert Validation**: Human expert review for high-stakes content
- **Community Feedback Integration**: Learning from user ratings and comments
- **Continuous Improvement**: AI models improve with usage data

---

## Common Issues and Solutions

### 1. Resource Generation Quality Issues
**Problem:** Generated resources don't meet expectations
**Solution:** 
- Provide more specific parameters in generation request
- Include detailed child profile information
- Specify exact needs and constraints
- Try different resource types or categories

### 2. Search Not Finding Relevant Resources
**Problem:** Search results not relevant to needs
**Solution:** 
- Use more specific search terms
- Adjust filters to narrow results
- Include specific subjects or age groups
- Try broader categories and then refine

### 3. Recommendations Not Accurate
**Problem:** Personalized recommendations not matching needs
**Solution:** 
- Complete detailed child profile
- Rate resources you've used to improve algorithm
- Update preferences and constraints
- Provide feedback on recommendation quality

### 4. Community Submission Rejected
**Problem:** Resource submission not approved
**Solution:** 
- Review submission criteria carefully
- Ensure content is original and valuable
- Check for age appropriateness and educational value
- Follow formatting and content guidelines

---

## AI Troubleshooting Prompt

Copy and paste this prompt into ChatGPT or Claude when encountering issues:

```
I'm testing Parent Resource Library in Mentor AI platform and encountering an issue.

**Endpoint:** [ENDPOINT_URL]
**HTTP Method:** [METHOD]
**Request Payload:** [REQUEST_JSON]
**Error Response:** [ERROR_RESPONSE]
**Expected Behavior:** [DESCRIPTION]

**Context:**
- Parent Resource Library provides AI-generated educational content for parents
- Personalization engine adapts to child's learning profile and needs
- Community features allow sharing and expert validation
- Content generation uses Gemini AI with educational expertise
- Quality assurance combines AI review with human expert validation

**Question:** Can you help me debug this issue by:
1. Analyzing the resource generation or retrieval request
2. Checking if personalization parameters are appropriate
3. Identifying common issues with AI content generation for parenting
4. Suggesting specific fixes or debugging steps

**Additional Information:**
- Parent ID: [PARENT_ID]
- Child Age: [CHILD_AGE]
- Resource Type: [RESOURCE_TYPE]
- Category: [CATEGORY]
- [Add any relevant logs or observations]
```

---

## Related Models and Services

### Models
- `models.parent_resource_models.Resource`
- `models.parent_resource_models.ResourceCollection`
- `models.parent_resource_models.ResourceReview`
- `models.parent_resource_models.PersonalizedRecommendation`
- `models.parent_resource_models.CommunityResource`

### Services
- `services.parent_resource_service.ParentResourceService`
- `services.content_generation_service.ContentGenerationService`
- `services.personalization_service.PersonalizationService`
- `services.community_service.CommunityService`

### Dependencies
- `services.gemini_service.GeminiService`
- `services.expert_review_service.ExpertReviewService`
- `services.quality_assurance_service.QualityAssuranceService`

---

## Performance Considerations

1. **Content Generation**: AI generation takes 5-10 seconds for comprehensive resources
2. **Search Performance**: Advanced AI search with personalization takes 2-3 seconds
3. **Recommendation Engine**: Personalization processing takes 1-2 seconds
4. **Community Features**: Real-time updates and notifications
5. **Caching**: Resources cached for 24 hours, recommendations for 6 hours

---

## Security Notes

1. **Content Moderation**: All community submissions undergo review
2. **Privacy Protection**: Child data anonymized for personalization
3. **Access Control**: Parents can only access their own data and collections
4. **Content Filtering**: AI filters inappropriate or harmful content
5. **Expert Verification**: Critical content requires expert validation

---

## Testing Best Practices

1. **Content Quality**: Validate AI-generated content for accuracy and appropriateness
2. **Personalization Testing**: Test with various child profiles and needs
3. **Search Functionality**: Test search with different queries and filters
4. **Community Features**: Test submission, review, and sharing workflows
5. **Performance Testing**: Test with high load and concurrent users