"""
Test script for Google Custom Search API integration
"""

import asyncio
from src.config import settings
from src.search.google_searcher import google_searcher


async def test_google_search():
    print("=" * 60)
    print("GOOGLE CUSTOM SEARCH TEST")
    print("=" * 60)

    # Check configuration
    print("\n1️⃣ Checking configuration...")
    if settings.google_search_api_key and settings.google_search_engine_id:
        print(f"   ✅ Google API Key configured (length: {len(settings.google_search_api_key)})")
        print(f"   ✅ Search Engine ID: {settings.google_search_engine_id}")
    else:
        print("   ❌ Google Search API not configured")
        print("\n   Please add to your .env file:")
        print("   GOOGLE_SEARCH_API_KEY=your_api_key_here")
        print("   GOOGLE_SEARCH_ENGINE_ID=your_engine_id_here")
        return False

    # Test search
    print("\n2️⃣ Testing Google Custom Search...")
    print("   Searching for: Dr Tang Boon Nee")

    try:
        result = await google_searcher.search_doctor_reviews(
            doctor_name="Dr Tang Boon Nee",
            specialty="",
            location="Malaysia"
        )

        print(f"\n   Results:")
        print(f"   - Total URLs found: {result.get('total_count', 0)}")
        print(f"   - Source: {result.get('source')}")

        if result.get('error'):
            print(f"   ❌ Error: {result.get('error')}")
            return False

        urls = result.get('urls', [])
        if urls:
            print(f"\n   First 5 URLs:")
            for i, url_data in enumerate(urls[:5], 1):
                print(f"   {i}. {url_data.get('source')}: {url_data.get('url')}")
                print(f"      Title: {url_data.get('title', 'N/A')[:60]}...")

            # Test content extraction
            print("\n3️⃣ Testing review extraction with OpenAI...")
            extraction_result = await google_searcher.extract_content_with_openai(
                urls=urls[:5],  # Test with first 5 URLs
                doctor_name="Dr Tang Boon Nee"
            )

            reviews = extraction_result.get('reviews', [])
            print(f"\n   Extracted {len(reviews)} reviews")

            if reviews:
                print(f"\n   First review:")
                first_review = reviews[0]
                print(f"   - Snippet: {first_review.get('snippet', '')[:100]}...")
                print(f"   - Date: {first_review.get('review_date', 'N/A')}")
                print(f"   - URL: {first_review.get('url', 'N/A')}")
            else:
                print("   ⚠️ No reviews extracted (URLs might not have reviews)")
        else:
            print("   ⚠️ No URLs found")

        print("\n" + "=" * 60)
        print("✅ TEST COMPLETED")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n   ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_google_search())
    exit(0 if success else 1)
