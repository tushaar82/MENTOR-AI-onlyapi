"""
Intelligent Model Router for Token Optimization
Automatically selects optimal AI model based on task complexity and cost efficiency
"""

import logging
from typing import Dict, Any, Optional
from config.model_config import ModelConfig
from utils.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

class ModelRouter:
    """Intelligent router for selecting optimal AI models based on task requirements"""
    
    def __init__(self):
        self.model_config = ModelConfig()
        self.gemini_client = GeminiClient()
        self.usage_stats = {}
        self.performance_cache = {}
        
    def select_model(self, task_type: str, complexity: str = 'medium', 
                   quality_requirement: float = 0.9, token_estimate: int = None) -> Dict[str, Any]:
        """
        Select optimal model for a given task
        
        Args:
            task_type: Type of task (simple_mcq, practice_questions, etc.)
            complexity: Complexity level (easy, medium, hard)
            quality_requirement: Minimum quality threshold (0.0-1.0)
            token_estimate: Estimated token count for the task
            
        Returns:
            Dictionary containing model configuration and metadata
        """
        try:
            # Get task complexity information
            task_config = self.model_config.get_task_complexity(task_type)
            
            # Adjust quality requirement based on complexity
            if complexity == 'easy':
                adjusted_quality = min(quality_requirement, 0.85)
            elif complexity == 'hard':
                adjusted_quality = max(quality_requirement, 0.95)
            else:
                adjusted_quality = quality_requirement
            
            # Get optimal model
            optimal_model_type = self.model_config.get_optimal_model(task_type, adjusted_quality)
            model_config = self.model_config.get_model_config(optimal_model_type)
            
            # Calculate cost savings
            cost_savings = self.model_config.calculate_cost_savings(task_type, optimal_model_type)
            
            result = {
                'model_type': optimal_model_type,
                'model_name': model_config['model'],
                'cost_per_token': model_config['cost_per_token'],
                'max_tokens': model_config['max_tokens'],
                'quality_threshold': model_config['quality_threshold'],
                'speed_factor': model_config['speed_factor'],
                'cost_savings_percent': cost_savings,
                'estimated_cost': task_config['estimated_tokens'] * model_config['cost_per_token'],
                'task_complexity': task_config['complexity_score']
            }
            
            # Log selection for analytics
            self._log_model_selection(task_type, optimal_model_type, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error selecting model for task {task_type}: {str(e)}")
            # Fallback to standard model
            return self.model_config.get_model_config('standard_generation')
    
    def generate_with_optimal_model(self, prompt: str, task_type: str, 
                                 complexity: str = 'medium', **kwargs) -> Dict[str, Any]:
        """
        Generate content using the optimal model for the task
        
        Args:
            prompt: The prompt to send to the model
            task_type: Type of task being performed
            complexity: Complexity level of the task
            **kwargs: Additional parameters for generation
            
        Returns:
            Dictionary containing generated content and metadata
        """
        try:
            # Select optimal model
            model_selection = self.select_model(task_type, complexity)
            
            # Optimize prompt for the selected model
            optimized_prompt = self._optimize_prompt_for_model(prompt, model_selection)
            
            # Generate content
            generation_params = {
                'model': model_selection['model_name'],
                'prompt': optimized_prompt,
                'max_tokens': model_selection['max_tokens'],
                'temperature': self._get_temperature_for_task(task_type, complexity),
                **kwargs
            }
            
            # Call the model
            response_content = self.gemini_client.generate_content(
                prompt=generation_params['prompt'],
                temperature=generation_params['temperature'],
                max_output_tokens=generation_params['max_tokens'],
                **{k: v for k, v in generation_params.items() if k not in ['prompt', 'temperature', 'max_tokens']}
            )
            
            # Create response dictionary with expected structure
            response = {
                'content': response_content,
                'tokens_used': len(response_content.split()) * 1.3,  # Rough estimate
                'generation_time': 0.5  # Placeholder
            }
            
            # Track usage
            self._track_usage(task_type, model_selection, response)
            
            return {
                'content': response['content'],
                'tokens_used': response.get('tokens_used', 0),
                'model_used': model_selection['model_type'],
                'cost_incurred': response.get('tokens_used', 0) * model_selection['cost_per_token'],
                'cost_savings': model_selection['cost_savings_percent'],
                'quality_score': self._assess_quality(response, task_type),
                'generation_time': response.get('generation_time', 0)
            }
            
        except Exception as e:
            logger.error(f"Error generating with optimal model: {str(e)}")
            # Fallback to standard generation
            return self._fallback_generation(prompt, task_type, **kwargs)
    
    def _optimize_prompt_for_model(self, prompt: str, model_selection: Dict[str, Any]) -> str:
        """Optimize prompt based on the selected model's capabilities"""
        model_type = model_selection['model_type']
        
        if model_type == 'basic_generation':
            # Ultra-compact prompts for basic model
            return self._create_ultra_minimal_prompt(prompt)
        elif model_type == 'standard_generation':
            # Standard optimized prompts
            return self._create_standard_prompt(prompt)
        elif model_type == 'complex_generation':
            # Full-featured prompts for complex tasks
            return self._create_comprehensive_prompt(prompt)
        else:
            return prompt
    
    def _create_ultra_minimal_prompt(self, original_prompt: str) -> str:
        """Create ultra-minimal prompt for basic model"""
        # Extract essential information
        lines = original_prompt.split('\n')
        essentials = {}
        
        for line in lines:
            if line.startswith('Topic:'):
                essentials['topic'] = line.replace('Topic:', '').strip()
            elif line.startswith('Difficulty:'):
                essentials['difficulty'] = line.replace('Difficulty:', '').strip()
            elif line.startswith('Format:'):
                essentials['format'] = line.replace('Format:', '').strip()
        
        # Create minimal prompt
        minimal_prompt = f"Q:{essentials.get('topic', 'Unknown')} "
        minimal_prompt += f"D:{essentials.get('difficulty', 'medium')} "
        minimal_prompt += f"F:{essentials.get('format', 'MCQ|4|1')} "
        minimal_prompt += "Tokens:50"
        
        return minimal_prompt
    
    def _create_standard_prompt(self, original_prompt: str) -> str:
        """Create standard optimized prompt"""
        # Remove redundant information while preserving context
        lines = original_prompt.split('\n')
        essential_lines = []
        
        for line in lines:
            if any(keyword in line for keyword in ['Topic:', 'Difficulty:', 'Format:', 'Context:', 'Instructions:']):
                essential_lines.append(line)
        
        return '\n'.join(essential_lines)
    
    def _create_comprehensive_prompt(self, original_prompt: str) -> str:
        """Create comprehensive prompt for complex tasks"""
        # Return original prompt for complex tasks
        return original_prompt
    
    def _get_temperature_for_task(self, task_type: str, complexity: str) -> float:
        """Get appropriate temperature for task and complexity"""
        base_temps = {
            'simple_mcq': 0.1,
            'practice_questions': 0.3,
            'diagnostic_tests': 0.2,
            'topic_summaries': 0.4,
            'mindmaps': 0.5
        }
        
        base_temp = base_temps.get(task_type, 0.3)
        
        # Adjust based on complexity
        if complexity == 'easy':
            return base_temp * 0.8
        elif complexity == 'hard':
            return base_temp * 1.2
        else:
            return base_temp
    
    def _assess_quality(self, response: Dict[str, Any], task_type: str) -> float:
        """Assess quality of generated content"""
        # Simple quality assessment based on response characteristics
        content = response.get('content', '')
        
        # Basic quality metrics
        if task_type == 'simple_mcq':
            # Check if it's a valid MCQ
            has_options = any(option in content for option in ['A)', 'B)', 'C)', 'D)'])
            has_question = '?' in content or '.' in content[:100]
            return 0.9 if (has_options and has_question) else 0.6
        
        elif task_type == 'practice_questions':
            # Check content length and structure
            word_count = len(content.split())
            has_explanation = 'Explanation:' in content or 'Solution:' in content
            quality_score = min(word_count / 100, 1.0) * 0.7
            if has_explanation:
                quality_score += 0.3
            return min(quality_score, 1.0)
        
        else:
            # Default quality assessment
            return 0.8
    
    def _track_usage(self, task_type: str, model_selection: Dict[str, Any], response: Dict[str, Any]):
        """Track model usage for analytics"""
        model_type = model_selection['model_type']
        
        if model_type not in self.usage_stats:
            self.usage_stats[model_type] = {
                'usage_count': 0,
                'total_tokens': 0,
                'total_cost': 0,
                'average_quality': 0,
                'tasks': []
            }
        
        stats = self.usage_stats[model_type]
        stats['usage_count'] += 1
        stats['total_tokens'] += response.get('tokens_used', 0)
        stats['total_cost'] += response.get('tokens_used', 0) * model_selection['cost_per_token']
        stats['tasks'].append({
            'task_type': task_type,
            'tokens_used': response.get('tokens_used', 0),
            'quality_score': self._assess_quality(response, task_type)
        })
        
        # Calculate average quality
        total_quality = sum(task['quality_score'] for task in stats['tasks'])
        stats['average_quality'] = total_quality / len(stats['tasks'])
    
    def _log_model_selection(self, task_type: str, model_type: str, selection_data: Dict[str, Any]):
        """Log model selection for analytics"""
        logger.info(f"Model Selection - Task: {task_type}, Model: {model_type}, "
                   f"Savings: {selection_data['cost_savings_percent']:.1f}%, "
                   f"Quality: {selection_data['quality_threshold']}")
    
    def _fallback_generation(self, prompt: str, task_type: str, **kwargs) -> Dict[str, Any]:
        """Fallback generation using standard model"""
        try:
            standard_config = self.model_config.get_model_config('standard_generation')
            response_content = self.gemini_client.generate_content(
                prompt=prompt,
                max_output_tokens=standard_config['max_tokens'],
                **{k: v for k, v in kwargs.items() if k != 'model'}
            )
            
            return {
                'content': response_content,
                'tokens_used': len(response_content.split()) * 1.3,  # Rough estimate
                'model_used': 'standard_generation_fallback',
                'cost_incurred': len(response_content.split()) * 1.3 * standard_config['cost_per_token'],
                'cost_savings': 0,
                'quality_score': 0.8,
                'generation_time': 0.5  # Placeholder
            }
            
        except Exception as e:
            logger.error(f"Fallback generation failed: {str(e)}")
            raise Exception("All generation methods failed")
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get usage statistics for all models"""
        total_cost = sum(stats['total_cost'] for stats in self.usage_stats.values())
        total_tokens = sum(stats['total_tokens'] for stats in self.usage_stats.values())
        
        return {
            'model_usage': self.usage_stats,
            'total_cost': total_cost,
            'total_tokens': total_tokens,
            'average_cost_per_token': total_cost / total_tokens if total_tokens > 0 else 0,
            'model_distribution': {
                model_type: stats['usage_count'] 
                for model_type, stats in self.usage_stats.items()
            }
        }