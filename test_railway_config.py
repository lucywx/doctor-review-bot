"""
Test script to diagnose Railway configuration issues
"""
import asyncio
import sys

async def test_config():
    print("=" * 60)
    print("RAILWAY CONFIGURATION DIAGNOSTIC")
    print("=" * 60)

    # Test 1: Load config
    print("\n1️⃣ Testing configuration loading...")
    try:
        from src.config import settings
        print(f"   ✅ Config loaded successfully")
        print(f"   Environment: {settings.environment}")
        print(f"   OpenAI Model: {settings.openai_model}")
        print(f"   Database: {settings.database_url[:30]}...")

        # Check API key
        key = settings.openai_api_key
        print(f"   OpenAI Key length: {len(key)}")
        print(f"   Key starts with: {key[:15]}")
        print(f"   Key ends with: ...{key[-10:]}")

        # Check for spaces
        if ' ' in key:
            print(f"   ❌ WARNING: API key contains SPACES! This will cause authentication errors!")
            print(f"   Space count: {key.count(' ')}")
        else:
            print(f"   ✅ API key format looks good (no spaces)")

    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

    # Test 2: Test OpenAI connection
    print("\n2️⃣ Testing OpenAI API connection...")
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.openai_api_key)

        # Simple test call
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'OK'"}],
            max_tokens=5
        )

        print(f"   ✅ OpenAI API is working!")
        print(f"   Response: {response.choices[0].message.content}")

    except Exception as e:
        print(f"   ❌ OpenAI API failed: {e}")
        return False

    # Test 3: Test web search
    print("\n3️⃣ Testing OpenAI web search...")
    try:
        from src.search.openai_web_searcher import openai_web_searcher

        result = await openai_web_searcher.search_doctor_reviews(
            doctor_name="Test Doctor",
            specialty="",
            location=""
        )

        print(f"   ✅ Web search executed")
        print(f"   Source: {result.get('source')}")
        print(f"   Reviews found: {result.get('total_count', 0)}")

        if result.get('error'):
            print(f"   ⚠️ Search error: {result.get('error')}")

    except Exception as e:
        print(f"   ❌ Web search failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 4: Test database
    print("\n4️⃣ Testing database connection...")
    try:
        from src.database import db

        await db.connect()
        result = await db.fetchval("SELECT 1")
        await db.disconnect()

        print(f"   ✅ Database connection working (PostgreSQL)")

    except Exception as e:
        print(f"   ❌ Database failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = asyncio.run(test_config())
    sys.exit(0 if success else 1)
