"""
Test script for OpenAI web search functionality
"""
import asyncio
import sys
from src.search.openai_web_searcher import openai_web_searcher

async def test_web_search():
    print("🧪 Testing OpenAI Web Search...\n")

    # Test with a well-known doctor name
    doctor_name = "张文宏"  # Famous Chinese doctor
    specialty = "传染病"
    location = "上海"

    print(f"🔍 Searching for: {doctor_name}")
    print(f"   Specialty: {specialty}")
    print(f"   Location: {location}\n")

    try:
        # Perform search
        result = await openai_web_searcher.search_doctor_reviews(
            doctor_name=doctor_name,
            specialty=specialty,
            location=location
        )

        # Display results
        print(f"✅ Search completed!")
        print(f"   Source: {result.get('source')}")
        print(f"   Total reviews: {result.get('total_count')}")

        if result.get('error'):
            print(f"   ⚠️ Error: {result.get('error')}")

        print("\n📋 Reviews found:")
        reviews = result.get('reviews', [])

        if not reviews:
            print("   ❌ No reviews found")
            return False

        for i, review in enumerate(reviews[:3], 1):  # Show first 3
            print(f"\n   Review {i}:")
            print(f"   Source: {review.get('source')}")
            print(f"   Snippet: {review.get('snippet')[:100]}...")
            print(f"   URL: {review.get('url')}")

        print("\n🎉 Web search is working!")
        return True

    except Exception as e:
        import traceback
        print(f"❌ Error: {e}")
        print(f"\nTraceback:\n{traceback.format_exc()}")
        print("\nPossible issues:")
        print("  1. Invalid OpenAI API key")
        print("  2. Model 'gpt-4o' not available")
        print("  3. Web search tool not enabled")
        print("  4. Network connection problem")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_web_search())
    sys.exit(0 if success else 1)
