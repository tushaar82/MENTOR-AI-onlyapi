# Interactive Study Tools API Documentation

## Overview

The Interactive Study Tools provide comprehensive AI-powered learning tools including flashcards, practice problems, interactive simulations, collaborative study sessions, gamified learning experiences, and adaptive learning paths. These tools enhance student engagement through interactive content, real-time feedback, and personalized learning experiences.

## Base URL
```
/api/interactive-tools
```

## Endpoints

### 1. Generate Flashcards

**Endpoint:** `POST /api/interactive-tools/flashcards/generate`

**Description:** Generate AI-powered flashcards for specific topics with customizable difficulty levels and learning objectives.

**Authentication:** Required (JWT token)

#### Request Example
```bash
curl -X POST "http://localhost:8000/api/interactive-tools/flashcards/generate" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student_123",
    "topic_id": "T02",
    "topic_name": "Thermodynamics",
    "subject": "Physics",
    "difficulty": "medium",
    "card_count": 20,
    "include_images": true,
    "card_types": ["concept", "formula", "example", "definition"]
  }'
```

#### Request Body
- `student_id`: ID of the student (required)
- `topic_id`: ID of the topic (required)
- `topic_name`: Name of the topic (required)
- `subject`: Subject area (required)
- `difficulty`: Difficulty level (easy, medium, hard)
- `card_count`: Number of flashcards to generate (default: 10, max: 50)
- `include_images`: Include visual content (default: true)
- `card_types`: Types of flashcards (concept, formula, example, definition)

#### Expected Response (200 OK)
```json
{
  "success": true,
  "flashcard_set_id": "flash_set_abc123",
  "student_id": "student_123",
  "topic_id": "T02",
  "generated_at": "2024-01-15T10:30:00Z",
  "flashcards": [
    {
      "card_id": "card_001",
      "front": {
        "content": "What is the First Law of Thermodynamics?",
        "type": "question",
        "image_url": "https://example.com/images/first_law_diagram.png"
      },
      "back": {
        "content": "The First Law of Thermodynamics states that energy cannot be created or destroyed, only transformed from one form to another. Mathematically: ΔU = Q - W",
        "type": "answer",
        "key_points": ["Energy conservation", "ΔU = Q - W", "Internal energy change"]
      },
      "difficulty": "medium",
      "category": "concept",
      "estimated_time": 30,
      "related_concepts": ["Energy", "Work", "Heat"]
    },
    {
      "card_id": "card_002",
      "front": {
        "content": "Calculate the work done by 2 moles of ideal gas expanding isothermally at 300K from 10L to 20L.",
        "type": "problem",
        "image_url": null
      },
      "back": {
        "content": "Solution: W = nRT ln(V₂/V₁)\nW = 2 × 8.314 × 300 × ln(20/10)\nW = 2 × 8.314 × 300 × 0.693 = 3456 J",
        "type": "solution",
        "steps": ["Identify isothermal process", "Apply formula W = nRT ln(V₂/V₁)", "Substitute values and calculate"],
        "answer": "3456 J"
      },
      "difficulty": "hard",
      "category": "example",
      "estimated_time": 120,
      "related_concepts": ["Isothermal process", "Ideal gas", "Work calculation"]
    }
  ],
  "metadata": {
    "total_cards": 20,
    "difficulty_distribution": {
      "easy": 5,
      "medium": 10,
      "hard": 5
    },
    "category_distribution": {
      "concept": 8,
      "formula": 4,
      "example": 5,
      "definition": 3
    },
    "estimated_total_time": 45,
    "spaced_repetition_schedule": {
      "initial_interval": 1,
      "growth_factor": 2.5,
      "max_interval": 30
    }
  }
}
```

#### Error Scenarios
- **400 Bad Request:** Invalid parameters or card count exceeds limit
- **401 Unauthorized:** Authentication required
- **404 Not Found:** Topic not found or invalid subject
- **500 Internal Server Error:** Flashcard generation failed

---

### 2. Start Flashcard Session

**Endpoint:** `POST /api/interactive-tools/flashcards/session/start`

**Description:** Start an interactive flashcard study session with spaced repetition algorithm.

**Authentication:** Required (JWT token)

#### Request Example
```bash
curl -X POST "http://localhost:8000/api/interactive-tools/flashcards/session/start" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student_123",
    "flashcard_set_id": "flash_set_abc123",
    "session_type": "review",
    "difficulty_filter": "all",
    "max_cards": 15,
    "time_limit_minutes": 30
  }'
```

#### Request Body
- `student_id`: ID of the student (required)
- `flashcard_set_id`: ID of flashcard set (required)
- `session_type`: Type of session (review, learning, test)
- `difficulty_filter`: Filter by difficulty (easy, medium, hard, all)
- `max_cards`: Maximum cards in session (default: 20)
- `time_limit_minutes`: Session time limit (optional)

#### Expected Response (200 OK)
```json
{
  "success": true,
  "session_id": "session_def456",
  "student_id": "student_123",
  "flashcard_set_id": "flash_set_abc123",
  "started_at": "2024-01-15T11:00:00Z",
  "session_config": {
    "session_type": "review",
    "total_cards": 15,
    "time_limit_minutes": 30,
    "difficulty_distribution": {
      "easy": 3,
      "medium": 8,
      "hard": 4
    }
  },
  "first_card": {
    "card_id": "card_001",
    "front": {
      "content": "What is the First Law of Thermodynamics?",
      "type": "question",
      "image_url": "https://example.com/images/first_law_diagram.png"
    },
    "session_data": {
      "card_position": 1,
      "previous_attempts": 0,
      "difficulty_rating": "medium",
      "time_shown": "2024-01-15T11:00:05Z"
    }
  },
  "session_stats": {
    "cards_remaining": 14,
    "correct_answers": 0,
    "incorrect_answers": 0,
    "average_response_time": 0,
    "session_progress": 0.067
  }
}
```

#### Error Scenarios
- **400 Bad Request:** Invalid session parameters
- **401 Unauthorized:** Authentication required
- **404 Not Found:** Flashcard set not found
- **500 Internal Server Error:** Session creation failed

---

### 3. Submit Flashcard Response

**Endpoint:** `POST /api/interactive-tools/flashcards/session/respond`

**Description:** Submit answer for current flashcard and get next card or session results.

**Authentication:** Required (JWT token)

#### Request Example
```bash
curl -X POST "http://localhost:8000/api/interactive-tools/flashcards/session/respond" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session_def456",
    "card_id": "card_001",
    "student_id": "student_123",
    "response": "Energy cannot be created or destroyed, only transformed",
    "confidence_level": "high",
    "time_taken_seconds": 25,
    "request_hint": false
  }'
```

#### Request Body
- `session_id`: ID of the active session (required)
- `card_id`: ID of the current card (required)
- `student_id`: ID of the student (required)
- `response`: Student's answer (required)
- `confidence_level`: Confidence in answer (low, medium, high)
- `time_taken_seconds`: Time spent on this card (required)
- `request_hint`: Whether student requested hint (default: false)

#### Expected Response (200 OK)
```json
{
  "success": true,
  "session_id": "session_def456",
  "card_result": {
    "card_id": "card_001",
    "correct": true,
    "accuracy_score": 0.85,
    "feedback": "Excellent! You correctly identified the core principle of energy conservation.",
    "improvement_tips": ["Consider mentioning the mathematical form ΔU = Q - W"],
    "next_review_interval": 3,
    "mastery_level": "developing"
  },
  "next_card": {
    "card_id": "card_002",
    "front": {
      "content": "Calculate the work done by 2 moles of ideal gas expanding isothermally at 300K from 10L to 20L.",
      "type": "problem",
      "image_url": null
    },
    "session_data": {
      "card_position": 2,
      "previous_attempts": 0,
      "difficulty_rating": "hard",
      "time_shown": "2024-01-15T11:00:35Z"
    }
  },
  "updated_session_stats": {
    "cards_completed": 1,
    "cards_remaining": 14,
    "correct_answers": 1,
    "incorrect_answers": 0,
    "average_response_time": 25,
    "session_progress": 0.133,
    "current_streak": 1,
    "best_streak": 1
  },
  "session_complete": false
}
```

#### Error Scenarios
- **400 Bad Request:** Invalid session or card ID
- **401 Unauthorized:** Authentication required
- **404 Not Found:** Session or card not found
- **500 Internal Server Error:** Response processing failed

---

### 4. Generate Practice Problems

**Endpoint:** `POST /api/interactive-tools/practice/generate`

**Description:** Generate adaptive practice problems with step-by-step hints and personalized difficulty adjustment.

**Authentication:** Required (JWT token)

#### Request Example
```bash
curl -X POST "http://localhost:8000/api/interactive-tools/practice/generate" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student_123",
    "topic_id": "T02",
    "subject": "Physics",
    "problem_count": 10,
    "difficulty": "adaptive",
    "problem_types": ["numerical", "conceptual", "derivation"],
    "include_hints": true,
    "adaptive_difficulty": true
  }'
```

#### Request Body
- `student_id`: ID of the student (required)
- `topic_id`: ID of the topic (required)
- `subject`: Subject area (required)
- `problem_count`: Number of problems to generate (default: 5, max: 20)
- `difficulty`: Difficulty level (easy, medium, hard, adaptive)
- `problem_types`: Types of problems (numerical, conceptual, derivation, application)
- `include_hints`: Include step-by-step hints (default: true)
- `adaptive_difficulty`: Adjust based on performance (default: true)

#### Expected Response (200 OK)
```json
{
  "success": true,
  "practice_set_id": "practice_set_ghi789",
  "student_id": "student_123",
  "topic_id": "T02",
  "generated_at": "2024-01-15T12:00:00Z",
  "problems": [
    {
      "problem_id": "prob_001",
      "type": "numerical",
      "difficulty": "medium",
      "question": "A gas undergoes an isothermal expansion from 5L to 15L at 300K. If the initial pressure is 2 atm, calculate the work done by the gas.",
      "given_data": [
        "Initial volume (V₁) = 5L",
        "Final volume (V₂) = 15L",
        "Temperature (T) = 300K",
        "Initial pressure (P₁) = 2 atm"
      ],
      "hints": [
        {
          "level": 1,
          "hint": "For isothermal process, use W = nRT ln(V₂/V₁)"
        },
        {
          "level": 2,
          "hint": "First find the number of moles using PV = nRT"
        },
        {
          "level": 3,
          "hint": "n = P₁V₁/RT = (2 atm × 5L)/(0.0821 L·atm/mol·K × 300K)"
        }
      ],
      "solution": {
        "steps": [
          "Calculate moles: n = P₁V₁/RT = (2 × 5)/(0.0821 × 300) = 0.406 mol",
          "Apply isothermal work formula: W = nRT ln(V₂/V₁)",
          "Calculate: W = 0.406 × 8.314 × 300 × ln(15/5) = 1120 J"
        ],
        "final_answer": "1120 J",
        "units": "Joules",
        "significant_figures": 3
      },
      "estimated_time": 180,
      "points": 10,
      "concepts_tested": ["Isothermal process", "Work calculation", "Ideal gas law"]
    },
    {
      "problem_id": "prob_002",
      "type": "conceptual",
      "difficulty": "easy",
      "question": "Explain why the temperature of an ideal gas remains constant during an isothermal expansion, even though the gas does work.",
      "expected_points": [
        "Heat energy flows into the system from surroundings",
        "Internal energy of ideal gas depends only on temperature",
        "Work done by gas equals heat absorbed (ΔU = Q - W = 0)",
        "Temperature remains constant as internal energy is unchanged"
      ],
      "solution": {
        "explanation": "In an isothermal expansion, the gas does work on the surroundings. According to the First Law (ΔU = Q - W), for ΔU = 0 (constant temperature), Q must equal W. Heat flows from the surroundings to the gas, exactly compensating for the work done, keeping the temperature constant.",
        "key_concepts": ["First Law of Thermodynamics", "Internal energy", "Heat-work equivalence"]
      },
      "estimated_time": 120,
      "points": 5,
      "concepts_tested": ["First Law", "Internal energy", "Isothermal process"]
    }
  ],
  "metadata": {
    "total_problems": 10,
    "difficulty_distribution": {
      "easy": 3,
      "medium": 5,
      "hard": 2
    },
    "type_distribution": {
      "numerical": 5,
      "conceptual": 3,
      "derivation": 2
    },
    "estimated_total_time": 45,
    "total_points": 75,
    "adaptive_algorithm": "bayesian_difficulty_adjustment"
  }
}
```

#### Error Scenarios
- **400 Bad Request:** Invalid parameters or problem count exceeds limit
- **401 Unauthorized:** Authentication required
- **404 Not Found:** Topic not found or invalid subject
- **500 Internal Server Error:** Practice problem generation failed

---

### 5. Start Practice Session

**Endpoint:** `POST /api/interactive-tools/practice/session/start`

**Description:** Start an adaptive practice session with real-time difficulty adjustment and performance tracking.

**Authentication:** Required (JWT token)

#### Request Example
```bash
curl -X POST "http://localhost:8000/api/interactive-tools/practice/session/start" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student_123",
    "practice_set_id": "practice_set_ghi789",
    "session_mode": "adaptive",
    "target_accuracy": 0.75,
    "time_limit_minutes": 45
  }'
```

#### Request Body
- `student_id`: ID of the student (required)
- `practice_set_id`: ID of practice set (required)
- `session_mode`: Session mode (adaptive, fixed, timed)
- `target_accuracy`: Target accuracy for adaptation (default: 0.75)
- `time_limit_minutes`: Session time limit (optional)

#### Expected Response (200 OK)
```json
{
  "success": true,
  "session_id": "practice_session_jkl012",
  "student_id": "student_123",
  "practice_set_id": "practice_set_ghi789",
  "started_at": "2024-01-15T13:00:00Z",
  "session_config": {
    "session_mode": "adaptive",
    "target_accuracy": 0.75,
    "time_limit_minutes": 45,
    "adaptive_parameters": {
      "difficulty_adjustment_factor": 0.1,
      "performance_window": 3,
      "min_difficulty": 0.3,
      "max_difficulty": 0.9
    }
  },
  "first_problem": {
    "problem_id": "prob_001",
    "type": "numerical",
    "difficulty": "medium",
    "question": "A gas undergoes an isothermal expansion from 5L to 15L at 300K. If the initial pressure is 2 atm, calculate the work done by the gas.",
    "given_data": [
      "Initial volume (V₁) = 5L",
      "Final volume (V₂) = 15L",
      "Temperature (T) = 300K",
      "Initial pressure (P₁) = 2 atm"
    ],
    "session_data": {
      "problem_position": 1,
      "time_started": "2024-01-15T13:00:05Z",
      "hints_used": 0,
      "attempts": 0
    }
  },
  "session_stats": {
    "problems_remaining": 9,
    "correct_answers": 0,
    "incorrect_answers": 0,
    "current_accuracy": 0,
    "average_difficulty": 0.5,
    "session_progress": 0.1
  }
}
```

#### Error Scenarios
- **400 Bad Request:** Invalid session parameters
- **401 Unauthorized:** Authentication required
- **404 Not Found:** Practice set not found
- **500 Internal Server Error:** Session creation failed

---

### 6. Submit Practice Answer

**Endpoint:** `POST /api/interactive-tools/practice/session/submit`

**Description:** Submit answer for current practice problem and get feedback with next problem or session results.

**Authentication:** Required (JWT token)

#### Request Example
```bash
curl -X POST "http://localhost:8000/api/interactive-tools/practice/session/submit" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "practice_session_jkl012",
    "problem_id": "prob_001",
    "student_id": "student_123",
    "answer": "1120 J",
    "time_taken_seconds": 165,
    "hints_used": [1],
    "confidence_level": "medium"
  }'
```

#### Request Body
- `session_id`: ID of the active session (required)
- `problem_id`: ID of the current problem (required)
- `student_id`: ID of the student (required)
- `answer`: Student's answer (required)
- `time_taken_seconds`: Time spent on this problem (required)
- `hints_used`: List of hint levels used (optional)
- `confidence_level`: Confidence in answer (low, medium, high)

#### Expected Response (200 OK)
```json
{
  "success": true,
  "session_id": "practice_session_jkl012",
  "problem_result": {
    "problem_id": "prob_001",
    "correct": true,
    "accuracy_score": 0.95,
    "points_earned": 10,
    "feedback": "Excellent work! You correctly applied the isothermal work formula.",
    "detailed_feedback": {
      "strengths": ["Correct formula application", "Accurate calculation"],
      "improvements": ["Consider showing intermediate steps for clarity"],
      "next_steps": ["Try similar problems with different initial conditions"]
    },
    "solution_revealed": {
      "steps": [
        "Calculate moles: n = P₁V₁/RT = (2 × 5)/(0.0821 × 300) = 0.406 mol",
        "Apply isothermal work formula: W = nRT ln(V₂/V₁)",
        "Calculate: W = 0.406 × 8.314 × 300 × ln(15/5) = 1120 J"
      ],
      "final_answer": "1120 J"
    },
    "learning_insights": {
      "mastery_level": "proficient",
      "concepts_mastered": ["Isothermal work calculation"],
      "concepts_needing_practice": [],
      "recommended_next_difficulty": "hard"
    }
  },
  "next_problem": {
    "problem_id": "prob_002",
    "type": "conceptual",
    "difficulty": "easy",
    "question": "Explain why the temperature of an ideal gas remains constant during an isothermal expansion, even though the gas does work.",
    "session_data": {
      "problem_position": 2,
      "time_started": "2024-01-15T13:03:00Z",
      "hints_used": 0,
      "attempts": 0
    }
  },
  "updated_session_stats": {
    "problems_completed": 1,
    "problems_remaining": 9,
    "correct_answers": 1,
    "incorrect_answers": 0,
    "current_accuracy": 1.0,
    "average_difficulty": 0.55,
    "total_points": 10,
    "session_progress": 0.2,
    "adaptive_adjustment": {
      "difficulty_increased": true,
      "new_difficulty_level": 0.6,
      "adjustment_reason": "High accuracy on medium difficulty"
    }
  },
  "session_complete": false
}
```

#### Error Scenarios
- **400 Bad Request:** Invalid session or problem ID
- **401 Unauthorized:** Authentication required
- **404 Not Found:** Session or problem not found
- **500 Internal Server Error:** Answer processing failed

---

### 7. Generate Interactive Simulation

**Endpoint:** `POST /api/interactive-tools/simulations/generate`

**Description:** Generate interactive physics/chemistry/mathematics simulations with real-time parameter adjustment and visualization.

**Authentication:** Required (JWT token)

#### Request Example
```bash
curl -X POST "http://localhost:8000/api/interactive-tools/simulations/generate" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student_123",
    "topic_id": "T02",
    "simulation_type": "thermodynamics_process",
    "complexity": "medium",
    "interactive_elements": ["parameter_sliders", "real_time_graphs", "step_by_step"],
    "learning_objectives": ["understand_isothermal_process", "analyze_work_calculation"]
  }'
```

#### Request Body
- `student_id`: ID of the student (required)
- `topic_id`: ID of the topic (required)
- `simulation_type`: Type of simulation (thermodynamics_process, wave_motion, chemical_reaction, geometry_visualization)
- `complexity`: Simulation complexity (basic, medium, advanced)
- `interactive_elements`: Interactive features to include
- `learning_objectives`: Specific learning goals for the simulation

#### Expected Response (200 OK)
```json
{
  "success": true,
  "simulation_id": "sim_mno345",
  "student_id": "student_123",
  "topic_id": "T02",
  "generated_at": "2024-01-15T14:00:00Z",
  "simulation_config": {
    "title": "Interactive Thermodynamic Process Simulator",
    "type": "thermodynamics_process",
    "complexity": "medium",
    "estimated_duration": 25,
    "learning_objectives": [
      "understand_isothermal_process",
      "analyze_work_calculation",
      "visualize_pv_diagrams"
    ]
  },
  "interactive_elements": {
    "parameter_controls": [
      {
        "parameter": "initial_pressure",
        "type": "slider",
        "min": 0.5,
        "max": 5.0,
        "default": 2.0,
        "unit": "atm",
        "description": "Initial gas pressure"
      },
      {
        "parameter": "initial_volume",
        "type": "slider",
        "min": 1.0,
        "max": 20.0,
        "default": 5.0,
        "unit": "L",
        "description": "Initial gas volume"
      },
      {
        "parameter": "temperature",
        "type": "slider",
        "min": 200,
        "max": 400,
        "default": 300,
        "unit": "K",
        "description": "Gas temperature"
      },
      {
        "parameter": "process_type",
        "type": "dropdown",
        "options": ["isothermal", "adiabatic", "isobaric", "isochoric"],
        "default": "isothermal",
        "description": "Type of thermodynamic process"
      }
    ],
    "visualizations": [
      {
        "type": "pv_diagram",
        "title": "Pressure-Volume Diagram",
        "real_time": true,
        "interactive": true
      },
      {
        "type": "work_calculation",
        "title": "Work Done Calculation",
        "real_time": true,
        "show_steps": true
      },
      {
        "type": "gas_animation",
        "title": "Gas Particle Animation",
        "real_time": true,
        "speed_control": true
      }
    ],
    "learning_tools": [
      {
        "type": "step_by_step_guide",
        "title": "Process Steps",
        "interactive": true
      },
      {
        "type": "formula_explanation",
        "title": "Formula Derivation",
        "expandable": true
      }
    ]
  },
  "simulation_data": {
    "initial_state": {
      "pressure": 2.0,
      "volume": 5.0,
      "temperature": 300,
      "moles": 0.406
    },
    "process_equations": {
      "isothermal": "PV = constant",
      "adiabatic": "PV^γ = constant",
      "isobaric": "P = constant",
      "isochoric": "V = constant"
    },
    "work_formulas": {
      "isothermal": "W = nRT ln(V₂/V₁)",
      "adiabatic": "W = (P₁V₁ - P₂V₂)/(γ-1)",
      "isobaric": "W = P(V₂ - V₁)",
      "isochoric": "W = 0"
    }
  },
  "assessment_criteria": [
    {
      "criterion": "correct_process_identification",
      "weight": 0.3,
      "description": "Identify correct thermodynamic process"
    },
    {
      "criterion": "parameter_adjustment",
      "weight": 0.4,
      "description": "Adjust parameters to achieve desired outcome"
    },
    {
      "criterion": "calculation_accuracy",
      "weight": 0.3,
      "description": "Calculate work done correctly"
    }
  ],
  "embed_code": "<iframe src='https://simulations.mentorai.com/sim_mno345' width='800' height='600'></iframe>",
  "api_endpoint": "/api/interactive-tools/simulations/sim_mno345/interact"
}
```

#### Error Scenarios
- **400 Bad Request:** Invalid simulation parameters
- **401 Unauthorized:** Authentication required
- **404 Not Found:** Topic not found or simulation type invalid
- **500 Internal Server Error:** Simulation generation failed

---

### 8. Interact with Simulation

**Endpoint:** `POST /api/interactive-tools/simulations/{simulation_id}/interact`

**Description:** Send interaction data to simulation and receive updated state and feedback.

**Authentication:** Required (JWT token)

#### Request Example
```bash
curl -X POST "http://localhost:8000/api/interactive-tools/simulations/sim_mno345/interact" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student_123",
    "interaction_type": "parameter_change",
    "parameters": {
      "initial_pressure": 3.0,
      "final_volume": 15.0,
      "process_type": "isothermal"
    },
    "request_calculation": true,
    "timestamp": "2024-01-15T14:05:00Z"
  }'
```

#### Request Body
- `student_id`: ID of the student (required)
- `interaction_type`: Type of interaction (parameter_change, question, reset, complete)
- `parameters`: Updated parameter values
- `request_calculation**: Request calculation results (default: true)
- `timestamp`: Interaction timestamp (required)

#### Expected Response (200 OK)
```json
{
  "success": true,
  "simulation_id": "sim_mno345",
  "student_id": "student_123",
  "interaction_id": "int_pqr678",
  "timestamp": "2024-01-15T14:05:00Z",
  "updated_state": {
    "current_parameters": {
      "initial_pressure": 3.0,
      "initial_volume": 5.0,
      "final_volume": 15.0,
      "temperature": 300,
      "process_type": "isothermal"
    },
    "calculated_values": {
      "final_pressure": 1.0,
      "work_done": 1345.2,
      "heat_absorbed": 1345.2,
      "internal_energy_change": 0
    },
    "visualization_data": {
      "pv_diagram": {
        "points": [
          {"x": 5.0, "y": 3.0},
          {"x": 15.0, "y": 1.0}
        ],
        "curve_type": "hyperbolic"
      },
      "work_area": {
        "highlighted": true,
        "area_value": 1345.2,
        "color": "#4CAF50"
      }
    }
  },
  "feedback": {
    "correctness": "correct",
    "explanation": "Correctly identified isothermal process. Work calculation is accurate.",
    "learning_insights": [
      "Pressure decreased as volume increased (Boyle's Law)",
      "Work done equals area under P-V curve",
      "Temperature remained constant throughout process"
    ],
    "suggestions": [
      "Try changing to adiabatic process to see the difference",
      "Experiment with different volume ratios"
    ]
  },
  "progress_tracking": {
    "interactions_count": 3,
    "correct_adjustments": 2,
    "learning_objectives_progress": {
      "understand_isothermal_process": 0.8,
      "analyze_work_calculation": 0.9,
      "visualize_pv_diagrams": 0.7
    },
    "mastery_level": "developing"
  },
  "next_steps": {
    "recommended_action": "try_different_process_type",
    "suggested_parameters": {
      "process_type": "adiabatic",
      "initial_pressure": 2.5,
      "volume_ratio": 3
    }
  }
}
```

#### Error Scenarios
- **400 Bad Request:** Invalid interaction parameters
- **401 Unauthorized:** Authentication required
- **404 Not Found:** Simulation not found
- **500 Internal Server Error:** Interaction processing failed

---

### 9. Start Collaborative Study Session

**Endpoint:** `POST /api/interactive-tools/collaborative/session/start`

**Description:** Start a collaborative study session with real-time interaction, shared whiteboard, and group problem solving.

**Authentication:** Required (JWT token)

#### Request Example
```bash
curl -X POST "http://localhost:8000/api/interactive-tools/collaborative/session/start" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "host_student_id": "student_123",
    "topic_id": "T02",
    "session_name": "Thermodynamics Study Group",
    "max_participants": 4,
    "session_duration_minutes": 60,
    "features": ["whiteboard", "voice_chat", "screen_share", "problems"],
    "access_type": "public"
  }'
```

#### Request Body
- `host_student_id`: ID of the host student (required)
- `topic_id`: ID of the topic (required)
- `session_name`: Name of the study session (required)
- `max_participants`: Maximum number of participants (default: 6)
- `session_duration_minutes`: Session duration (default: 60)
- `features`: Features to enable (whiteboard, voice_chat, screen_share, problems)
- `access_type`: Access type (public, private, invite_only)

#### Expected Response (200 OK)
```json
{
  "success": true,
  "session_id": "collab_session_stu901",
  "host_student_id": "student_123",
  "session_name": "Thermodynamics Study Group",
  "created_at": "2024-01-15T15:00:00Z",
  "session_config": {
    "topic_id": "T02",
    "topic_name": "Thermodynamics",
    "max_participants": 4,
    "current_participants": 1,
    "session_duration_minutes": 60,
    "access_type": "public",
    "features_enabled": {
      "whiteboard": true,
      "voice_chat": true,
      "screen_share": true,
      "collaborative_problems": true
    }
  },
  "host_info": {
    "student_id": "student_123",
    "name": "John Doe",
    "role": "host",
    "permissions": ["manage_participants", "control_features", "end_session"]
  },
  "session_links": {
    "join_url": "https://study.mentorai.com/join/collab_session_stu901",
    "share_url": "https://study.mentorai.com/share/collab_session_stu901",
    "websocket_url": "wss://realtime.mentorai.com/collab/collab_session_stu901"
  },
  "initial_state": {
    "whiteboard_data": {
      "canvas_id": "wb_abc123",
      "elements": [],
      "background": "grid"
    },
    "shared_problems": [],
    "chat_history": [],
    "participant_states": {
      "student_123": {
        "joined_at": "2024-01-15T15:00:00Z",
        "audio_enabled": false,
        "screen_sharing": false
      }
    }
  },
  "session_status": "active",
  "expires_at": "2024-01-15T16:00:00Z"
}
```

#### Error Scenarios
- **400 Bad Request:** Invalid session configuration
- **401 Unauthorized:** Authentication required
- **403 Forbidden:** Student not allowed to host sessions
- **500 Internal Server Error:** Session creation failed

---

### 10. Join Collaborative Session

**Endpoint:** `POST /api/interactive-tools/collaborative/session/join`

**Description:** Join an existing collaborative study session.

**Authentication:** Required (JWT token)

#### Request Example
```bash
curl -X POST "http://localhost:8000/api/interactive-tools/collaborative/session/join" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student_456",
    "session_id": "collab_session_stu901",
    "join_code": null,
    "features_requested": ["whiteboard", "voice_chat"]
  }'
```

#### Request Body
- `student_id`: ID of the joining student (required)
- `session_id`: ID of the session to join (required)
- `join_code`: Optional join code for private sessions
- `features_requested`: Features student wants to use

#### Expected Response (200 OK)
```json
{
  "success": true,
  "session_id": "collab_session_stu901",
  "student_id": "student_456",
  "joined_at": "2024-01-15T15:05:00Z",
  "session_info": {
    "session_name": "Thermodynamics Study Group",
    "topic_id": "T02",
    "topic_name": "Thermodynamics",
    "host_id": "student_123",
    "host_name": "John Doe",
    "participants_count": 2,
    "max_participants": 4,
    "session_duration_minutes": 60,
    "time_remaining_minutes": 55
  },
  "participant_info": {
    "student_id": "student_456",
    "name": "Jane Smith",
    "role": "participant",
    "permissions": ["use_whiteboard", "send_messages", "share_screen"],
    "features_enabled": {
      "whiteboard": true,
      "voice_chat": true,
      "screen_share": true,
      "collaborative_problems": true
    }
  },
  "session_state": {
    "whiteboard_data": {
      "canvas_id": "wb_abc123",
      "elements": [
        {
          "id": "elem_001",
          "type": "text",
          "content": "First Law: ΔU = Q - W",
          "position": {"x": 100, "y": 100},
          "author": "student_123"
        }
      ],
      "background": "grid"
    },
    "shared_problems": [
      {
        "problem_id": "prob_001",
        "question": "Calculate work done in isothermal expansion...",
        "added_by": "student_123",
        "added_at": "2024-01-15T15:02:00Z"
      }
    ],
    "chat_history": [
      {
        "message_id": "msg_001",
        "sender_id": "student_123",
        "sender_name": "John Doe",
        "message": "Welcome everyone! Let's start with isothermal processes.",
        "timestamp": "2024-01-15T15:01:00Z"
      }
    ],
    "participant_states": {
      "student_123": {
        "joined_at": "2024-01-15T15:00:00Z",
        "audio_enabled": false,
        "screen_sharing": false
      },
      "student_456": {
        "joined_at": "2024-01-15T15:05:00Z",
        "audio_enabled": false,
        "screen_sharing": false
      }
    }
  },
  "connection_info": {
    "websocket_url": "wss://realtime.mentorai.com/collab/collab_session_stu901",
    "session_token": "token_xyz789",
    "expires_at": "2024-01-15T16:00:00Z"
  }
}
```

#### Error Scenarios
- **400 Bad Request:** Invalid session or student ID
- **401 Unauthorized:** Authentication required
- **404 Not Found:** Session not found
- **409 Conflict:** Session full or student already joined
- **500 Internal Server Error:** Join processing failed

---

## Testing Workflows

### Complete Interactive Study Tools Workflow

1. **Generate Flashcards**
   ```bash
   curl -X POST "/api/interactive-tools/flashcards/generate" \
     -H "Authorization: Bearer TOKEN" \
     -d '{"student_id": "student_123", "topic_id": "T02", "card_count": 20}'
   ```

2. **Start Flashcard Session**
   ```bash
   curl -X POST "/api/interactive-tools/flashcards/session/start" \
     -H "Authorization: Bearer TOKEN" \
     -d '{"student_id": "student_123", "flashcard_set_id": "flash_set_abc123"}'
   ```

3. **Submit Flashcard Responses**
   ```bash
   curl -X POST "/api/interactive-tools/flashcards/session/respond" \
     -H "Authorization: Bearer TOKEN" \
     -d '{"session_id": "session_def456", "card_id": "card_001", "response": "..."}'
   ```

4. **Generate Practice Problems**
   ```bash
   curl -X POST "/api/interactive-tools/practice/generate" \
     -H "Authorization: Bearer TOKEN" \
     -d '{"student_id": "student_123", "topic_id": "T02", "problem_count": 10}'
   ```

5. **Start Practice Session**
   ```bash
   curl -X POST "/api/interactive-tools/practice/session/start" \
     -H "Authorization: Bearer TOKEN" \
     -d '{"student_id": "student_123", "practice_set_id": "practice_set_ghi789"}'
   ```

6. **Submit Practice Answers**
   ```bash
   curl -X POST "/api/interactive-tools/practice/session/submit" \
     -H "Authorization: Bearer TOKEN" \
     -d '{"session_id": "practice_session_jkl012", "problem_id": "prob_001", "answer": "..."}'
   ```

7. **Generate Simulation**
   ```bash
   curl -X POST "/api/interactive-tools/simulations/generate" \
     -H "Authorization: Bearer TOKEN" \
     -d '{"student_id": "student_123", "topic_id": "T02", "simulation_type": "thermodynamics_process"}'
   ```

8. **Interact with Simulation**
   ```bash
   curl -X POST "/api/interactive-tools/simulations/sim_mno345/interact" \
     -H "Authorization: Bearer TOKEN" \
     -d '{"student_id": "student_123", "interaction_type": "parameter_change"}'
   ```

9. **Start Collaborative Session**
   ```bash
   curl -X POST "/api/interactive-tools/collaborative/session/start" \
     -H "Authorization: Bearer TOKEN" \
     -d '{"host_student_id": "student_123", "topic_id": "T02", "session_name": "Study Group"}'
   ```

10. **Join Collaborative Session**
    ```bash
    curl -X POST "/api/interactive-tools/collaborative/session/join" \
      -H "Authorization: Bearer TOKEN" \
      -d '{"student_id": "student_456", "session_id": "collab_session_stu901"}'
    ```

---

## AI-Powered Interactive Features

### Adaptive Learning
- **Difficulty Adjustment**: Real-time difficulty based on performance
- **Personalized Content**: AI-generated content tailored to learning style
- **Spaced Repetition**: Optimized review intervals for memory retention
- **Learning Path Optimization**: AI-optimized sequence of activities

### Intelligent Feedback
- **Step-by-Step Hints**: Progressive hint system
- **Detailed Explanations**: Context-aware feedback
- **Error Analysis**: Identify and correct misconceptions
- **Performance Insights**: Real-time learning analytics

### Collaborative Intelligence
- **Smart Grouping**: AI-powered student matching
- **Role Assignment**: Optimal role distribution in groups
- **Conflict Resolution**: AI-mediated discussion guidance
- **Progress Tracking**: Group and individual analytics

---

## Common Issues and Solutions

### 1. Flashcard Generation Issues
**Problem:** Flashcards not generating or poor quality
**Solution:** 
- Check topic_id exists and is valid
- Verify subject and topic name match
- Reduce card_count if generation is failing
- Ensure sufficient content exists for the topic

### 2. Practice Session Adaptation Problems
**Problem:** Difficulty not adjusting properly
**Solution:** 
- Ensure adaptive_difficulty is enabled
- Check target_accuracy is reasonable (0.6-0.9)
- Verify sufficient problems completed for adaptation
- Review performance_window parameter

### 3. Simulation Loading Issues
**Problem:** Simulations not loading or interacting
**Solution:** 
- Check browser compatibility and WebGL support
- Verify simulation_type is valid
- Ensure interactive_elements are supported
- Check network connectivity for real-time features

### 4. Collaborative Session Connection Problems
**Problem:** Cannot join or connect to collaborative sessions
**Solution:** 
- Verify WebSocket connectivity
- Check if session is full
- Ensure student has permission to join
- Validate session hasn't expired

---

## AI Troubleshooting Prompt

Copy and paste this prompt into ChatGPT or Claude when encountering issues:

```
I'm testing Interactive Study Tools in Mentor AI platform and encountering an issue.

**Endpoint:** [ENDPOINT_URL]
**HTTP Method:** [METHOD]
**Request Payload:** [REQUEST_JSON]
**Error Response:** [ERROR_RESPONSE]
**Expected Behavior:** [DESCRIPTION]

**Context:**
- Interactive Study Tools provide AI-powered learning experiences
- Flashcards use spaced repetition algorithms
- Practice problems feature adaptive difficulty adjustment
- Simulations offer real-time parameter manipulation
- Collaborative sessions support real-time interaction
- Content generation uses Gemini AI with educational context

**Question:** Can you help me debug this issue by:
1. Analyzing the interactive tool generation request
2. Checking if content parameters are appropriate
3. Identifying common issues with AI content generation
4. Suggesting specific fixes or debugging steps

**Additional Information:**
- Tool Type: [FLASHCARDS/PRACTICE/SIMULATION/COLLABORATIVE]
- Student ID: [STUDENT_ID]
- Topic ID: [TOPIC_ID]
- Session ID: [SESSION_ID_IF_APPLICABLE]
- [Add any relevant logs or observations]
```

---

## Related Models and Services

### Models
- `models.interactive_tools_models.FlashcardSet`
- `models.interactive_tools_models.FlashcardSession`
- `models.interactive_tools_models.PracticeSet`
- `models.interactive_tools_models.PracticeSession`
- `models.interactive_tools_models.Simulation`
- `models.interactive_tools_models.CollaborativeSession`

### Services
- `services.flashcard_service.FlashcardService`
- `services.practice_problem_service.PracticeProblemService`
- `services.simulation_service.SimulationService`
- `services.collaborative_service.CollaborativeService`

### Dependencies
- `services.gemini_service.GeminiService`
- `services.adaptive_learning_service.AdaptiveLearningService`
- `services.realtime_service.RealtimeService`

---

## Performance Considerations

1. **Content Generation**: AI generation takes 3-8 seconds per request
2. **Session Management**: Real-time sessions require WebSocket connections
3. **Simulation Rendering**: Complex simulations may need GPU acceleration
4. **Collaborative Features**: Bandwidth requirements for video/screen sharing
5. **Caching**: Generated content cached for 24 hours

---

## Security Notes

1. **Session Security**: All sessions use token-based authentication
2. **Content Filtering**: AI-generated content is filtered and validated
3. **Collaboration Privacy**: Private sessions require join codes
4. **Data Encryption**: Real-time communications encrypted end-to-end
5. **Access Control**: Students can only access their own sessions

---

## Testing Best Practices

1. **Content Quality**: Validate AI-generated content for accuracy
2. **Session Lifecycle**: Test complete session from start to end
3. **Adaptation Logic**: Verify difficulty adjustment works correctly
4. **Real-time Features**: Test WebSocket connectivity and latency
5. **Collaborative Functions**: Test multi-user interactions simultaneously