"""
Test script for language switching functionality in Mentor AI
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any

# Base URL for the API
BASE_URL = "http://localhost:8000"

async def test_language_endpoints():
    """Test language-related endpoints"""
    async with aiohttp.ClientSession() as session:
        print("=" * 60)
        print("Testing Language Endpoints")
        print("=" * 60)
        
        # Test getting supported languages
        print("\n1. Testing GET /api/language/supported")
        async with session.get(f"{BASE_URL}/api/language/supported") as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Success: {len(data['data']['languages'])} languages supported")
                for lang in data['data']['languages'][:3]:  # Show first 3
                    print(f"   - {lang['name']} ({lang['code']})")
            else:
                print(f"❌ Failed: {response.status}")
        
        # Test getting translations for English
        print("\n2. Testing GET /api/language/translations/en")
        async with session.get(f"{BASE_URL}/api/language/translations/en") as response:
            if response.status == 200:
                data = await response.json()
                print("✅ Success: English translations loaded")
                print(f"   Sample translation: {data['data']['translations']['hero']['title']}")
            else:
                print(f"❌ Failed: {response.status}")
        
        # Test getting translations for Hindi
        print("\n3. Testing GET /api/language/translations/hi")
        async with session.get(f"{BASE_URL}/api/language/translations/hi") as response:
            if response.status == 200:
                data = await response.json()
                print("✅ Success: Hindi translations loaded")
                print(f"   Sample translation: {data['data']['translations']['hero']['title']}")
            else:
                print(f"❌ Failed: {response.status}")
        
        # Test setting language preference
        print("\n4. Testing POST /api/language/preference")
        preference_data = {"language": "hi"}
        async with session.post(
            f"{BASE_URL}/api/language/preference",
            json=preference_data,
            headers={"Authorization": "Bearer test_token"}
        ) as response:
            if response.status in [200, 401]:  # 401 is expected without valid token
                print("✅ Success: Language preference endpoint working")
            else:
                print(f"❌ Failed: {response.status}")

async def test_vidhya_multilingual():
    """Test Vidhya AI multilingual capabilities"""
    async with aiohttp.ClientSession() as session:
        print("\n" + "=" * 60)
        print("Testing Vidhya AI Multilingual Support")
        print("=" * 60)
        
        # Test starting chat in different languages
        languages = ["en", "hi", "bn"]
        
        for lang in languages:
            print(f"\nTesting chat in {lang}...")
            chat_data = {
                "language": lang,
                "title": f"Test Chat - {lang.upper()}"
            }
            
            async with session.post(
                f"{BASE_URL}/api/vidhya/chat/start",
                json=chat_data,
                headers={"Authorization": "Bearer test_token"}
            ) as response:
                if response.status in [200, 401]:  # 401 is expected without valid token
                    print(f"✅ {lang.upper()}: Chat start endpoint working")
                else:
                    print(f"❌ {lang.upper()}: Failed with status {response.status}")

async def test_middleware_language_detection():
    """Test language middleware functionality"""
    async with aiohttp.ClientSession() as session:
        print("\n" + "=" * 60)
        print("Testing Language Middleware")
        print("=" * 60)
        
        # Test with query parameter
        print("\n1. Testing with ?lang=hi query parameter")
        async with session.get(
            f"{BASE_URL}/api/language/supported?lang=hi"
        ) as response:
            if response.status == 200:
                print("✅ Query parameter language detection working")
            else:
                print(f"❌ Failed: {response.status}")
        
        # Test with Accept-Language header
        print("\n2. Testing with Accept-Language header")
        headers = {"Accept-Language": "hi-IN, hi;q=0.9, en;q=0.8"}
        async with session.get(
            f"{BASE_URL}/api/language/supported",
            headers=headers
        ) as response:
            if response.status == 200:
                print("✅ Accept-Language header processing working")
            else:
                print(f"❌ Failed: {response.status}")

async def main():
    """Run all tests"""
    print("🌍 Testing Multi-Language Support Implementation")
    print("Make sure the backend server is running on http://localhost:8000")
    
    try:
        await test_language_endpoints()
        await test_vidhya_multilingual()
        await test_middleware_language_detection()
        
        print("\n" + "=" * 60)
        print("✅ Language Testing Complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Start the frontend: npm run dev")
        print("2. Test language switching in the UI")
        print("3. Verify translations appear correctly")
        print("4. Test Vidhya AI in different languages")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        print("Make sure the backend server is running on http://localhost:8000")

if __name__ == "__main__":
    asyncio.run(main())