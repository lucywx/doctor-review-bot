"""
Diagnostic script to identify the error
"""

import asyncio
import sys
from src.config import settings
from src.database import db
from src.search.aggregator import search_aggregator


async def diagnose():
    print("=" * 60)
    print("DIAGNOSTIC TOOL")
    print("=" * 60)

    # Check 1: Environment variables
    print("\n1️⃣ Checking environment variables...")

    print(f"   DATABASE_URL: {'✅ Set' if settings.database_url else '❌ Missing'}")
    print(f"   OPENAI_API_KEY: {'✅ Set' if settings.openai_api_key else '❌ Missing'}")
    print(f"   GOOGLE_SEARCH_API_KEY: {'✅ Set' if settings.google_search_api_key else '❌ Missing'}")
    print(f"   GOOGLE_SEARCH_ENGINE_ID: {'✅ Set' if settings.google_search_engine_id else '❌ Missing'}")

    if settings.google_search_api_key:
        print(f"      API Key length: {len(settings.google_search_api_key)}")
    if settings.google_search_engine_id:
        print(f"      Engine ID: {settings.google_search_engine_id}")

    # Check 2: Database connection
    print("\n2️⃣ Testing database connection...")
    try:
        await db.connect()
        result = await db.fetchval("SELECT 1")
        print(f"   ✅ Database connected (result: {result})")
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False

    # Check 3: Google Search API
    print("\n3️⃣ Testing Google Custom Search API...")
    try:
        from src.search.google_searcher import google_searcher

        result = await google_searcher.search_doctor_reviews(
            doctor_name="Dr Tang Boon Nee",
            specialty="",
            location="Malaysia"
        )

        if result.get('error'):
            print(f"   ❌ Google Search error: {result.get('error')}")
            return False

        urls = result.get('urls', [])
        print(f"   ✅ Google Search working! Found {len(urls)} URLs")

        if urls:
            print(f"      First URL: {urls[0].get('url', '')[:60]}...")

    except Exception as e:
        print(f"   ❌ Google Search exception: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Check 4: Full search flow
    print("\n4️⃣ Testing full search aggregator...")
    try:
        result = await search_aggregator.search_doctor_reviews(
            doctor_name="Dr Tang Boon Nee"
        )

        if result.get('error'):
            print(f"   ❌ Aggregator error: {result.get('error')}")
            return False

        reviews = result.get('reviews', [])
        source = result.get('source', '')

        print(f"   ✅ Search completed!")
        print(f"      Source: {source}")
        print(f"      Reviews: {len(reviews)}")

        if reviews:
            print(f"      First review snippet: {reviews[0].get('snippet', '')[:80]}...")

    except Exception as e:
        print(f"   ❌ Aggregator exception: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Check 5: Message formatting
    print("\n5️⃣ Testing message formatting...")
    try:
        from src.whatsapp.formatter import format_review_batch

        # Test batch formatting (current implementation)
        message = format_review_batch(
            batch=reviews[:5] if reviews else [],
            start_num=1,
            doctor_name="Dr Tang Boon Nee",
            total_count=len(reviews),
            filtered_count=0,
            remaining=50,
            quota=50
        )
        print(f"   ✅ Message formatted successfully")
        print(f"      Message length: {len(message)} characters")
        print(f"      First 100 chars: {message[:100]}...")

    except Exception as e:
        print(f"   ❌ Formatting exception: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("✅ ALL CHECKS PASSED")
    print("=" * 60)

    # Cleanup
    await db.disconnect()
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(diagnose())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
