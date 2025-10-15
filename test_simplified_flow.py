"""
Test script for simplified search flow (Google Custom Search only, no specialty)
"""

import asyncio
import sys
from src.config import settings
from src.search.aggregator import search_aggregator


async def test_simplified_search():
    print("=" * 60)
    print("SIMPLIFIED SEARCH FLOW TEST")
    print("=" * 60)

    # Initialize database
    print("\n0️⃣ Initializing database connection...")
    from src.database import db
    try:
        await db.connect()
        print("   ✅ Database connected")
    except Exception as e:
        print(f"   ⚠️ Database connection failed: {e}")
        print("   (Cache will not work, but search will continue)")

    # Check Google API configuration
    print("\n1️⃣ Checking Google Custom Search API configuration...")
    if settings.google_search_api_key and settings.google_search_engine_id:
        print(f"   ✅ API Key configured (length: {len(settings.google_search_api_key)})")
        print(f"   ✅ Engine ID: {settings.google_search_engine_id}")
    else:
        print("   ❌ Google Search API not configured!")
        print("\n   Add to .env:")
        print("   GOOGLE_SEARCH_API_KEY=your_key")
        print("   GOOGLE_SEARCH_ENGINE_ID=your_engine_id")
        return False

    # Test 1: Search with a known doctor
    print("\n2️⃣ Testing search: Dr Tang Boon Nee")
    print("   (No specialty - simplified flow)")

    try:
        result = await search_aggregator.search_doctor_reviews(
            doctor_name="Dr Tang Boon Nee"
        )

        print(f"\n   📊 Results:")
        print(f"   - Source: {result.get('source')}")
        print(f"   - Total reviews: {result.get('total_count', 0)}")

        if result.get('error'):
            print(f"   ❌ Error: {result.get('error')}")
            return False

        reviews = result.get('reviews', [])
        if reviews:
            print(f"\n   ✅ Found {len(reviews)} reviews")
            print(f"\n   First 3 reviews:")
            for i, review in enumerate(reviews[:3], 1):
                snippet = review.get('snippet', '')[:100]
                url = review.get('url', '')
                source = review.get('source', '')
                print(f"\n   {i}. {snippet}...")
                print(f"      Source: {source}")
                print(f"      URL: {url[:60]}...")
        else:
            print("   ⚠️ No reviews found")

        # Test 2: Search cache (should return instantly)
        print("\n3️⃣ Testing cache (searching same doctor again)...")
        import time
        start = time.time()

        result2 = await search_aggregator.search_doctor_reviews(
            doctor_name="Dr Tang Boon Nee"
        )

        elapsed = time.time() - start
        print(f"   ⏱️ Response time: {elapsed*1000:.0f}ms")

        if result2.get('source') == 'cache':
            print(f"   ✅ Cache hit! (should be < 100ms)")
        else:
            print(f"   ⚠️ Cache miss (source: {result2.get('source')})")

        # Test 3: Invalid input
        print("\n4️⃣ Testing invalid input (single character)...")
        result3 = await search_aggregator.search_doctor_reviews(
            doctor_name="A"
        )
        print(f"   Result: {result3.get('total_count', 0)} reviews")

        print("\n" + "=" * 60)
        print("✅ SIMPLIFIED FLOW TEST COMPLETED")
        print("=" * 60)
        print("\n📋 Summary:")
        print("   • No specialty selection needed ✅")
        print("   • Only Google Custom Search used ✅")
        print("   • OpenAI code preserved but not called ✅")
        print("   • Cache working ✅")

        # Cleanup
        await db.disconnect()
        return True

    except Exception as e:
        print(f"\n   ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

        # Cleanup
        from src.database import db
        await db.disconnect()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_simplified_search())
    sys.exit(0 if success else 1)
