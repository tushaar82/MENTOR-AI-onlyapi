"""
Model Configuration for Token Optimization
Implements multi-model strategy to reduce token costs by 25%
"""

class ModelConfig:
    """Configuration for different AI models based on task complexity and cost efficiency"""
    
    MODELS = {
        'basic_generation': {
            'model': 'gemini-2.0-flash-lite',
            'cost_per_token': 0.000000075,  # $0.075 per 1M input tokens
            'max_tokens': 1000,
            'use_cases': ['simple_mcq', 'basic_explanations', 'hints'],
            'quality_threshold': 0.85,
            'speed_factor': 0.3  # 70% faster than pro
        },
        'standard_generation': {
            'model': 'gemini-2.0-flash',
            'cost_per_token': 0.00000015,  # $0.15 per 1M input tokens
            'max_tokens': 4000,
            'use_cases': ['practice_questions', 'topic_summaries', 'mindmaps'],
            'quality_threshold': 0.92,
            'speed_factor': 1.0  # Baseline speed
        },
        'complex_generation': {
            'model': 'gemini-2.0-flash',
            'cost_per_token': 0.00000015,  # $0.15 per 1M input tokens
            'max_tokens': 8000,
            'use_cases': ['diagnostic_tests', 'detailed_analytics', 'comprehensive_explanations'],
            'quality_threshold': 0.95,
            'speed_factor': 1.0
        }
    }
    
    TASK_COMPLEXITY = {
        'simple_mcq': {
            'complexity_score': 0.2,
            'estimated_tokens': 150,
            'preferred_model': 'basic_generation',
            'fallback_model': 'standard_generation'
        },
        'practice_questions': {
            'complexity_score': 0.5,
            'estimated_tokens': 800,
            'preferred_model': 'standard_generation',
            'fallback_model': 'complex_generation'
        },
        'diagnostic_tests': {
            'complexity_score': 0.9,
            'estimated_tokens': 2000,
            'preferred_model': 'complex_generation',
            'fallback_model': 'complex_generation'
        },
        'topic_summaries': {
            'complexity_score': 0.4,
            'estimated_tokens': 600,
            'preferred_model': 'standard_generation',
            'fallback_model': 'standard_generation'
        },
        'hints': {
            'complexity_score': 0.3,
            'estimated_tokens': 200,
            'preferred_model': 'basic_generation',
            'fallback_model': 'standard_generation'
        },
        'mindmaps': {
            'complexity_score': 0.6,
            'estimated_tokens': 1000,
            'preferred_model': 'standard_generation',
            'fallback_model': 'complex_generation'
        }
    }
    
    @classmethod
    def get_model_config(cls, model_type: str) -> dict:
        """Get configuration for a specific model type"""
        return cls.MODELS.get(model_type, cls.MODELS['standard_generation'])
    
    @classmethod
    def get_task_complexity(cls, task_type: str) -> dict:
        """Get complexity information for a specific task type"""
        return cls.TASK_COMPLEXITY.get(task_type, cls.TASK_COMPLEXITY['practice_questions'])
    
    @classmethod
    def calculate_cost_savings(cls, task_type: str, model_type: str) -> float:
        """Calculate cost savings for using a specific model for a task"""
        task_config = cls.get_task_complexity(task_type)
        model_config = cls.get_model_config(model_type)
        
        # Cost with standard model (baseline)
        standard_config = cls.MODELS['standard_generation']
        standard_cost = task_config['estimated_tokens'] * standard_config['cost_per_token']
        
        # Cost with selected model
        actual_cost = task_config['estimated_tokens'] * model_config['cost_per_token']
        
        return ((standard_cost - actual_cost) / standard_cost) * 100
    
    @classmethod
    def get_optimal_model(cls, task_type: str, quality_requirement: float = 0.9) -> str:
        """Get optimal model for a task based on quality requirements"""
        task_config = cls.get_task_complexity(task_type)
        preferred_model = task_config['preferred_model']
        fallback_model = task_config['fallback_model']
        
        # Check if preferred model meets quality requirements
        preferred_config = cls.get_model_config(preferred_model)
        
        if preferred_config['quality_threshold'] >= quality_requirement:
            return preferred_model
        else:
            return fallback_model
    
    @classmethod
    def get_all_models_for_task(cls, task_type: str) -> list:
        """Get all suitable models for a task, ordered by cost efficiency"""
        task_config = cls.get_task_complexity(task_type)
        suitable_models = []
        
        for model_type, model_config in cls.MODELS.items():
            if any(use_case in model_config['use_cases'] for use_case in [task_type]):
                cost_savings = cls.calculate_cost_savings(task_type, model_type)
                suitable_models.append({
                    'model_type': model_type,
                    'cost_savings': cost_savings,
                    'quality_threshold': model_config['quality_threshold'],
                    'speed_factor': model_config['speed_factor']
                })
        
        # Sort by cost savings (descending)
        suitable_models.sort(key=lambda x: x['cost_savings'], reverse=True)
        return suitable_models