#!/usr/bin/env python3
"""
Test search WITHOUT specialty for Tang Boon Nee
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.search.aggregator import search_aggregator

async def test_no_specialty():
    print("=" * 80)
    print("TEST: Search WITHOUT Specialty")
    print("=" * 80)

    doctor_name = "Tang Boon Nee"

    print(f"\n🔍 Searching for: {doctor_name}")
    print(f"   Specialty: (none)")
    print(f"   Location: Malaysia (auto-added)\n")

    print("🚀 Starting search...\n")

    # Search without specialty
    result = await search_aggregator.search_doctor_reviews(
        doctor_name=doctor_name,
        specialty=""  # No specialty
    )

    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)

    print(f"\nTotal reviews found: {result.get('total_count', 0)}")
    print(f"Source: {result.get('source', 'unknown')}")
    print(f"Search strategy: {result.get('search_strategy', 'N/A')}")

    if 'error' in result:
        print(f"\n❌ Error: {result['error']}")

    reviews = result.get('reviews', [])
    if reviews:
        print(f"\n✅ Found {len(reviews)} reviews:\n")
        for i, review in enumerate(reviews[:10], 1):  # Show first 10
            print(f"\n{i}. Source: {review.get('source', 'unknown')}")
            snippet = review.get('snippet', 'No snippet')[:200]
            print(f"   Snippet: {snippet}...")
            print(f"   Rating: {review.get('rating', 'N/A')}")
            print(f"   Date: {review.get('review_date', 'N/A')}")
            print(f"   Author: {review.get('author_name', 'N/A')}")
            url = review.get('url', 'N/A')
            print(f"   URL: {url}")

        if len(reviews) > 10:
            print(f"\n   ... and {len(reviews) - 10} more reviews")
    else:
        print("\n❌ No reviews found")

    print("\n" + "=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_no_specialty())
