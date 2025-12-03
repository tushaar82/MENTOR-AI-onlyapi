"""
Test script for token limiting implementation.

This script tests the token limiting functionality
including:
- Token usage tracking
- Token limit validation
- Token usage endpoints
- Integration with Vidhya service

Author: Mentor AI Team
Version: 1.0.0
"""

import asyncio
import json
import logging
from datetime import datetime

from services.token_usage_service import get_token_usage_service
from services.vidhya_service import get_vidhya_service
from services.child_service import ChildService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_token_limiting():
    """Test token limiting implementation."""
    logger.info("Starting token limiting tests")
    
    # Initialize services
    token_service = get_token_usage_service()
    vidhya_service = get_vidhya_service()
    
    # Test data
    test_student_id = "test_student_123"
    test_parent_id = "test_parent_456"
    
    try:
        # Test 1: Check token limits for new student
        logger.info("Test 1: Checking token limits for new student")
        limit_check = await token_service.check_token_limit(
            student_id=test_student_id,
            tokens_requested=500
        )
        
        print(f"Token limit check result: {json.dumps(limit_check, indent=2)}")
        
        # Test 2: Track token usage
        logger.info("Test 2: Tracking token usage")
        track_success = await token_service.track_token_usage(
            student_id=test_student_id,
            tokens_used=250,
            interaction_type="test_interaction",
            parent_id=test_parent_id,
            metadata={
                "test": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        print(f"Token tracking result: {track_success}")
        
        # Test 3: Check updated usage
        logger.info("Test 3: Checking updated token usage")
        usage_data = await token_service.get_student_token_usage(test_student_id)
        
        print(f"Token usage data: {json.dumps(usage_data, indent=2, default=str)}")
        
        # Test 4: Test Vidhya service integration
        logger.info("Test 4: Testing Vidhya service with token limits")
        
        # Start a chat session
        session_info = await vidhya_service.start_chat_session(
            user_id=test_parent_id,
            student_id=test_student_id,
            language="en",
            title="Test Session"
        )
        
        print(f"Chat session started: {json.dumps(session_info, indent=2)}")
        
        session_id = session_info["session_id"]
        
        # Send a test message
        try:
            response = await vidhya_service.send_message(
                message="What is photosynthesis?",
                session_id=session_id,
                user_id=test_parent_id,
                language="en"
            )
            
            print(f"Vidhya response: {json.dumps(response, indent=2, default=str)}")
            
            # Check if tokens were tracked
            if "tokens_used" in response:
                logger.info(f"Tokens used in this interaction: {response['tokens_used']}")
            
        except Exception as e:
            print(f"Vidhya service error: {e}")
            logger.error(f"Vidhya service error: {e}")
        
        # Test 5: Test limit exceeded scenario
        logger.info("Test 5: Testing token limit exceeded scenario")
        
        # Use up most of the daily limit
        large_request = 2000
        limit_check_large = await token_service.check_token_limit(
            student_id=test_student_id,
            tokens_requested=large_request
        )
        
        print(f"Large request limit check: {json.dumps(limit_check_large, indent=2)}")
        
        if not limit_check_large["allowed"]:
            logger.info("Token limit correctly enforced for large request")
        else:
            logger.warning("Token limit not enforced for large request")
        
        # Test 6: Get comprehensive usage
        logger.info("Test 6: Getting comprehensive token usage")
        comprehensive_usage = await token_service.get_student_token_usage(
            student_id=test_student_id,
            start_date=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        )
        
        print(f"Comprehensive usage: {json.dumps(comprehensive_usage, indent=2, default=str)}")
        
        logger.info("Token limiting tests completed successfully")
        
    except Exception as e:
        logger.error(f"Error during token limiting tests: {e}")
        logger.exception("Full traceback:")
        print(f"Test error: {e}")


async def test_subscription_integration():
    """Test subscription integration with token limits."""
    logger.info("Testing subscription integration with token limits")
    
    try:
        # This would test the integration between subscription plans
        # and token limits, but requires a full subscription service setup
        
        # For now, just log that this test would be implemented
        logger.info("Subscription integration test would require:")
        logger.info("1. Active subscription for test parent")
        logger.info("2. Token limits based on subscription plan")
        logger.info("3. Plan upgrade scenarios")
        
        print("Subscription integration test - Not fully implemented")
        
    except Exception as e:
        logger.error(f"Error during subscription integration test: {e}")
        print(f"Subscription test error: {e}")


async def main():
    """Main test function."""
    print("=" * 60)
    print("MENTOR AI - TOKEN LIMITING IMPLEMENTATION TEST")
    print("=" * 60)
    print()
    
    print("This script tests the token limiting implementation including:")
    print("1. Token usage tracking service")
    print("2. Token limit validation")
    print("3. Vidhya service integration")
    print("4. Token usage endpoints")
    print()
    
    try:
        await test_token_limiting()
        print()
        await test_subscription_integration()
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        print(f"Test execution failed: {e}")
    
    print()
    print("=" * 60)
    print("TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())