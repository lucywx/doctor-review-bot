"""
Test script for Google Places API integration
Tests fetching reviews for Dr Paul Ng Hock Oon
"""

import asyncio
import sys
from src.search.google_places import google_places_client
from src.config import settings


async def test_places_api():
    """Test Google Places API with Dr Paul Ng Hock Oon"""

    print("=" * 60)
    print("🧪 Testing Google Places API Integration")
    print("=" * 60)

    # Check if API key is configured
    if not settings.google_places_api_key or settings.google_places_api_key == "not_required":
        print("\n❌ ERROR: GOOGLE_PLACES_API_KEY not configured in .env file")
        print("\nTo configure:")
        print("1. Go to https://console.cloud.google.com/apis/credentials")
        print("2. Create a new API key (or use existing)")
        print("3. Enable 'Places API' for your project")
        print("4. Add to .env file: GOOGLE_PLACES_API_KEY=your_key_here")
        print("\nCost: $200 free/month = ~40,000 searches")
        print("After free tier: $0.005 per search (Atmosphere Data)")
        return

    print(f"\n✅ API Key configured: {settings.google_places_api_key[:20]}...")
    print(f"   Client enabled: {google_places_client.enabled}")

    # Test search
    test_doctor = "Paul Ng Hock Oon"
    print(f"\n🔍 Searching for: Dr {test_doctor}")
    print(f"   Location: Malaysia")
    print("-" * 60)

    try:
        result = await google_places_client.search_doctor(
            doctor_name=test_doctor,
            location="Malaysia"
        )

        if not result:
            print("\n❌ No results found")
            print("   This could mean:")
            print("   1. Doctor not on Google Maps")
            print("   2. API key doesn't have Places API enabled")
            print("   3. Search query needs adjustment")
            return

        # Display results
        print(f"\n✅ Found place: {result['name']}")
        print(f"   Address: {result['address']}")
        print(f"   Rating: {result['rating']}/5.0")
        print(f"   Total reviews: {result['total_reviews']}")
        print(f"   URL: {result['url']}")

        reviews = result.get("reviews", [])
        print(f"\n📊 Retrieved {len(reviews)} reviews (max 5 due to API limit)")

        if reviews:
            print("\n" + "=" * 60)
            print("REVIEWS:")
            print("=" * 60)

            for i, review in enumerate(reviews, 1):
                print(f"\n{i}. {review['author']} - {'⭐' * review['rating']}")
                print(f"   Posted: {review['time']}")
                print(f"   {review['text'][:200]}..." if len(review['text']) > 200 else f"   {review['text']}")

            print("\n" + "=" * 60)
            print(f"⚠️  NOTE: Places API limit is 5 reviews maximum")
            print(f"   Total reviews available: {result['total_reviews']}")
            print(f"   Coverage: {len(reviews)}/{result['total_reviews']} ({len(reviews)/result['total_reviews']*100:.1f}%)")
        else:
            print("\n⚠️  No reviews found (place exists but has no reviews)")

        print("\n✅ Test completed successfully!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_places_api())
