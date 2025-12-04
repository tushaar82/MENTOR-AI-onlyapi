"""
Prompt Optimizer for Token Efficiency
Creates ultra-compact prompts for basic models and optimized prompts for other models
"""

import re
import json
from typing import Dict, Any, List
from config.model_config import ModelConfig

class PromptOptimizer:
    """Optimizes prompts based on model capabilities and task requirements"""
    
    def __init__(self):
        self.model_config = ModelConfig()
        self.prompt_templates = self._load_prompt_templates()
        self.compression_rules = self._load_compression_rules()
    
    def optimize_prompt_for_model(self, prompt: str, model_type: str, task_type: str) -> str:
        """
        Optimize prompt based on model type and task
        
        Args:
            prompt: Original prompt to optimize
            model_type: Type of model (basic_generation, standard_generation, complex_generation)
            task_type: Type of task (simple_mcq, practice_questions, etc.)
            
        Returns:
            Optimized prompt string
        """
        try:
            if model_type == 'basic_generation':
                return self._create_ultra_minimal_prompt(prompt, task_type)
            elif model_type == 'standard_generation':
                return self._create_standard_prompt(prompt, task_type)
            elif model_type == 'complex_generation':
                return self._create_comprehensive_prompt(prompt, task_type)
            else:
                return prompt
                
        except Exception as e:
            print(f"Error optimizing prompt: {str(e)}")
            return prompt
    
    def _create_ultra_minimal_prompt(self, original_prompt: str, task_type: str) -> str:
        """Create ultra-minimal prompt for basic model"""
        
        # Extract essential information based on task type
        essentials = self._extract_essentials(original_prompt, task_type)
        
        # Create minimal prompt based on task type
        if task_type == 'simple_mcq':
            return f"Q:{essentials.get('topic', 'Math')} D:{essentials.get('difficulty', 'medium')} F:MCQ|4|1"
        elif task_type == 'hints':
            return f"Q:{essentials.get('topic', 'Math')} H:{essentials.get('question', '')} T:50"
        elif task_type == 'basic_explanations':
            return f"E:{essentials.get('concept', '')} L:simple T:100"
        else:
            # Generic minimal prompt
            return f"T:{essentials.get('topic', 'Math')} D:{essentials.get('difficulty', 'medium')} T:100"
    
    def _create_standard_prompt(self, original_prompt: str, task_type: str) -> str:
        """Create standard optimized prompt"""
        
        # Remove redundant information while preserving context
        essential_lines = []
        lines = original_prompt.split('\n')
        
        # Keep only essential lines based on task type
        essential_keywords = self._get_essential_keywords(task_type)
        
        for line in lines:
            if any(keyword in line for keyword in essential_keywords):
                # Compress the line
                compressed_line = self._compress_line(line)
                essential_lines.append(compressed_line)
        
        return '\n'.join(essential_lines)
    
    def _create_comprehensive_prompt(self, original_prompt: str, task_type: str) -> str:
        """Create comprehensive prompt for complex tasks"""
        
        # For complex tasks, keep most of the original prompt
        # but optimize structure and remove redundancy
        
        if task_type == 'diagnostic_tests':
            return self._optimize_diagnostic_prompt(original_prompt)
        elif task_type == 'detailed_analytics':
            return self._optimize_analytics_prompt(original_prompt)
        else:
            return self._optimize_general_prompt(original_prompt)
    
    def _extract_essentials(self, prompt: str, task_type: str) -> Dict[str, str]:
        """Extract essential information from prompt"""
        
        essentials = {}
        
        # Common patterns to extract
        patterns = {
            'topic': r'(?:Topic|Subject|Concept):\s*([^\n]+)',
            'difficulty': r'(?:Difficulty|Level|Complexity):\s*([^\n]+)',
            'question': r'(?:Question|Problem|Q):\s*([^\n]+)',
            'concept': r'(?:Concept|Topic to explain):\s*([^\n]+)',
            'format': r'(?:Format|Output format):\s*([^\n]+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                essentials[key] = match.group(1).strip()
        
        return essentials
    
    def _get_essential_keywords(self, task_type: str) -> List[str]:
        """Get essential keywords for different task types"""
        
        keyword_map = {
            'simple_mcq': ['Topic:', 'Difficulty:', 'Format:', 'Context:'],
            'practice_questions': ['Topic:', 'Difficulty:', 'Context:', 'Instructions:', 'Format:'],
            'diagnostic_tests': ['Topic:', 'Difficulty:', 'Pattern:', 'Weightage:', 'Format:'],
            'topic_summaries': ['Topic:', 'Scope:', 'Format:', 'Length:'],
            'mindmaps': ['Topic:', 'Structure:', 'Format:', 'Connections:'],
            'hints': ['Question:', 'Topic:', 'Format:'],
            'basic_explanations': ['Concept:', 'Level:', 'Format:', 'Length:']
        }
        
        return keyword_map.get(task_type, ['Topic:', 'Difficulty:', 'Format:'])
    
    def _compress_line(self, line: str) -> str:
        """Compress individual line by removing redundant words"""
        
        # Remove redundant phrases
        redundant_phrases = [
            'Please generate',
            'Create a',
            'I need you to',
            'Can you please',
            'I would like you to',
            'Your task is to'
        ]
        
        compressed = line
        for phrase in redundant_phrases:
            compressed = compressed.replace(phrase, '')
        
        # Remove extra whitespace
        compressed = re.sub(r'\s+', ' ', compressed).strip()
        
        # Abbreviate common terms
        abbreviations = {
            'question': 'Q',
            'difficulty': 'D',
            'topic': 'T',
            'format': 'F',
            'context': 'C',
            'instructions': 'I',
            'explanation': 'E',
            'solution': 'S'
        }
        
        for full, abbrev in abbreviations.items():
            compressed = re.sub(rf'\b{full}\b:', f'{abbrev}:', compressed, flags=re.IGNORECASE)
        
        return compressed
    
    def _optimize_diagnostic_prompt(self, prompt: str) -> str:
        """Optimize diagnostic test prompt"""
        
        # Extract key components
        lines = prompt.split('\n')
        optimized_lines = []
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Identify sections
            if any(keyword in line.lower() for keyword in ['exam pattern', 'weightage', 'topics']):
                current_section = line.lower()
                optimized_lines.append(line)
            elif current_section and line.startswith('-'):
                # Compress list items
                compressed_item = self._compress_list_item(line)
                optimized_lines.append(compressed_item)
            else:
                # Regular line - apply basic compression
                optimized_lines.append(self._compress_line(line))
        
        return '\n'.join(optimized_lines)
    
    def _optimize_analytics_prompt(self, prompt: str) -> str:
        """Optimize analytics prompt"""
        
        # Keep structure but reduce verbosity
        sections = {
            'performance_data': [],
            'analysis_requirements': [],
            'output_format': []
        }
        
        lines = prompt.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Categorize lines
            if any(keyword in line.lower() for keyword in ['score', 'accuracy', 'time']):
                sections['performance_data'].append(line)
            elif any(keyword in line.lower() for keyword in ['analyze', 'identify', 'recommend']):
                sections['analysis_requirements'].append(line)
            elif any(keyword in line.lower() for keyword in ['format', 'output', 'structure']):
                sections['output_format'].append(line)
        
        # Rebuild optimized prompt
        optimized_prompt = []
        for section, lines in sections.items():
            if lines:
                optimized_prompt.append(f"## {section.replace('_', ' ').title()}")
                for line in lines:
                    optimized_prompt.append(self._compress_line(line))
        
        return '\n'.join(optimized_prompt)
    
    def _optimize_general_prompt(self, prompt: str) -> str:
        """Optimize general prompt"""
        
        # Apply general optimization rules
        optimized = prompt
        
        # Remove redundant phrases
        for pattern in self.compression_rules['redundant_phrases']:
            optimized = re.sub(pattern, '', optimized, flags=re.IGNORECASE)
        
        # Compress common terms
        for full, abbrev in self.compression_rules['abbreviations'].items():
            optimized = re.sub(rf'\b{full}\b', abbrev, optimized, flags=re.IGNORECASE)
        
        # Remove extra whitespace and empty lines
        optimized = re.sub(r'\n\s*\n', '\n', optimized)
        optimized = re.sub(r'\s+', ' ', optimized)
        
        return optimized.strip()
    
    def _compress_list_item(self, line: str) -> str:
        """Compress list items"""
        
        # Remove bullet points and compress
        compressed = re.sub(r'^[-*]\s*', '', line)
        return f"- {compressed}"
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """Load prompt templates for different tasks"""
        
        return {
            'ultra_minimal_mcq': "Q:{topic} D:{difficulty} F:MCQ|4|1",
            'ultra_minimal_hint': "Q:{question} H:{topic} T:50",
            'ultra_minimal_explanation': "E:{concept} L:simple T:100",
            'standard_mcq': "Topic: {topic}\nDifficulty: {difficulty}\nFormat: MCQ with 4 options\nContext: {context}",
            'comprehensive_diagnostic': "Exam: {exam_type}\nPattern: {pattern}\nWeightage: {weightage}\nTopics: {topics}"
        }
    
    def _load_compression_rules(self) -> Dict[str, Any]:
        """Load compression rules for prompts"""
        
        return {
            'redundant_phrases': [
                r'please generate',
                r'create a',
                r'i need you to',
                r'can you please',
                r'i would like you to',
                r'your task is to',
                r'please create',
                r'generate a'
            ],
            'abbreviations': {
                'question': 'Q',
                'difficulty': 'D',
                'topic': 'T',
                'format': 'F',
                'context': 'C',
                'instructions': 'I',
                'explanation': 'E',
                'solution': 'S',
                'answer': 'A',
                'option': 'O',
                'subject': 'Subj'
            }
        }
    
    def calculate_compression_ratio(self, original_prompt: str, optimized_prompt: str) -> float:
        """Calculate compression ratio"""
        
        original_length = len(original_prompt.split())
        optimized_length = len(optimized_prompt.split())
        
        if original_length == 0:
            return 0
        
        return ((original_length - optimized_length) / original_length) * 100
    
    def validate_prompt(self, prompt: str, task_type: str) -> Dict[str, Any]:
        """Validate optimized prompt"""
        
        validation_result = {
            'is_valid': True,
            'issues': [],
            'recommendations': []
        }
        
        # Check for essential components
        essentials = self._get_essential_keywords(task_type)
        
        for essential in essentials:
            if essential not in prompt:
                validation_result['is_valid'] = False
                validation_result['issues'].append(f"Missing essential component: {essential}")
        
        # Check prompt length
        word_count = len(prompt.split())
        if word_count > 200:  # Too long for basic model
            validation_result['recommendations'].append("Consider further compression for basic model")
        elif word_count < 10:  # Too short
            validation_result['recommendations'].append("Prompt may be too short for quality output")
        
        return validation_result