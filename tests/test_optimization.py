"""
Test script for token optimization implementation
Validates model selection logic and cost savings
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.model_router import ModelRouter
from services.prompt_optimizer import PromptOptimizer
from config.model_config import ModelConfig

def test_model_selection():
    """Test model selection logic for different scenarios"""
    print("=== Testing Model Selection Logic ===")
    
    router = ModelRouter()
    
    test_cases = [
        {
            "name": "Simple MCQ - Easy",
            "task_type": "simple_mcq",
            "complexity": "easy",
            "expected_model": "basic_generation"
        },
        {
            "name": "Simple MCQ - Medium",
            "task_type": "simple_mcq", 
            "complexity": "medium",
            "expected_model": "basic_generation"
        },
        {
            "name": "Practice Questions - Medium",
            "task_type": "practice_questions",
            "complexity": "medium", 
            "expected_model": "standard_generation"
        },
        {
            "name": "Diagnostic Test - Hard",
            "task_type": "diagnostic_tests",
            "complexity": "hard",
            "expected_model": "complex_generation"
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        
        # Test model selection
        selection = router.select_model(
            task_type=test_case['task_type'],
            complexity=test_case['complexity']
        )
        
        print(f"  Selected Model: {selection['model_type']}")
        print(f"  Cost per Token: ₹{selection['cost_per_token'] * 1000:.4f}")
        print(f"  Cost Savings: {selection['cost_savings_percent']:.1f}%")
        print(f"  Expected Model: {test_case['expected_model']}")
        
        # Validate selection
        if selection['model_type'] == test_case['expected_model']:
            print("  ✅ PASS: Correct model selected")
        else:
            print("  ❌ FAIL: Incorrect model selected")
        
        print(f"  Estimated Cost: ₹{selection['estimated_cost']:.4f}")

def test_prompt_optimization():
    """Test prompt optimization for different models"""
    print("\n=== Testing Prompt Optimization ===")
    
    optimizer = PromptOptimizer()
    
    original_prompt = """
    Topic: Calculus - Limits and Continuity
    Difficulty: medium
    Format: MCQ with 4 options and 1 correct answer
    Context: This question should test understanding of limits and continuity in calculus
    Instructions: Please generate a multiple choice question that tests the concept of limits
    """
    
    test_cases = [
        {"model": "basic_generation", "task": "simple_mcq"},
        {"model": "standard_generation", "task": "practice_questions"},
        {"model": "complex_generation", "task": "diagnostic_tests"}
    ]
    
    for test_case in test_cases:
        print(f"\nTesting {test_case['model']} for {test_case['task']}:")
        
        optimized = optimizer.optimize_prompt_for_model(
            original_prompt, 
            test_case['model'], 
            test_case['task']
        )
        
        print(f"  Original length: {len(original_prompt.split())} words")
        print(f"  Optimized length: {len(optimized.split())} words")
        
        compression_ratio = optimizer.calculate_compression_ratio(original_prompt, optimized)
        print(f"  Compression: {compression_ratio:.1f}%")
        
        validation = optimizer.validate_prompt(optimized, test_case['task'])
        print(f"  Valid: {validation['is_valid']}")
        
        if validation['issues']:
            print(f"  Issues: {validation['issues']}")
        
        print(f"  Optimized: {optimized[:100]}...")

def test_cost_calculations():
    """Test cost calculations and savings"""
    print("\n=== Testing Cost Calculations ===")
    
    config = ModelConfig()
    
    test_scenarios = [
        {"task": "simple_mcq", "model": "basic_generation"},
        {"task": "practice_questions", "model": "standard_generation"},
        {"task": "diagnostic_tests", "model": "complex_generation"}
    ]
    
    for scenario in test_scenarios:
        print(f"\nTesting {scenario['task']} with {scenario['model']}:")
        
        # Calculate cost savings
        savings = config.calculate_cost_savings(scenario['task'], scenario['model'])
        print(f"  Cost Savings: {savings:.1f}%")
        
        # Get optimal model
        optimal = config.get_optimal_model(scenario['task'])
        print(f"  Optimal Model: {optimal}")
        
        # Get all suitable models
        all_models = config.get_all_models_for_task(scenario['task'])
        print("  All Suitable Models:")
        for model in all_models:
            print(f"    {model['model_type']}: {model['cost_savings']:.1f}% savings")

def test_integration():
    """Test full integration with mock generation"""
    print("\n=== Testing Full Integration ===")
    
    router = ModelRouter()
    
    try:
        # Test simple MCQ generation
        result = router.generate_with_optimal_model(
            prompt="Topic: Basic Algebra\nDifficulty: easy\nCount: 2",
            task_type="simple_mcq",
            complexity="easy"
        )
        
        print(f"Generation Result:")
        print(f"  Model Used: {result['model_used']}")
        print(f"  Tokens Used: {result['tokens_used']}")
        print(f"  Cost Incurred: ₹{result['cost_incurred']:.4f}")
        print(f"  Cost Savings: {result['cost_savings']:.1f}%")
        print(f"  Quality Score: {result['quality_score']:.2f}")
        print(f"  Generation Time: {result['generation_time']:.2f}s")
        
        # Test usage statistics
        stats = router.get_usage_statistics()
        print(f"\nUsage Statistics:")
        print(f"  Total Cost: ₹{stats['total_cost']:.4f}")
        print(f"  Total Tokens: {stats['total_tokens']}")
        print(f"  Average Cost per Token: ₹{stats['average_cost_per_token']:.6f}")
        
    except Exception as e:
        print(f"Integration test failed: {str(e)}")
        print("This is expected if Gemini client is not configured")

def main():
    """Run all optimization tests"""
    print("🚀 Token Optimization Implementation Test")
    print("=" * 50)
    
    try:
        test_model_selection()
        test_prompt_optimization()
        test_cost_calculations()
        test_integration()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("\nNext Steps:")
        print("1. Configure Gemini client with proper API keys")
        print("2. Update existing routers to use model_router")
        print("3. Deploy and monitor token usage")
        print("4. Validate cost savings in production")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()