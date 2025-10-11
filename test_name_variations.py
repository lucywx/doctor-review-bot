#!/usr/bin/env python3
"""
Test different name variations for Tang Boon Nee
Compare search results with different capitalizations
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.search.aggregator import search_aggregator

async def test_name_variation(name, test_number):
    print("\n" + "=" * 80)
    print(f"TEST {test_number}: {name}")
    print("=" * 80)

    result = await search_aggregator.search_doctor_reviews(
        doctor_name=name,
        specialty=""  # No specialty
    )

    print(f"\n📊 Results for '{name}':")
    print(f"   Total reviews: {result.get('total_count', 0)}")
    print(f"   Source: {result.get('source', 'unknown')}")

    reviews = result.get('reviews', [])
    if reviews:
        print(f"\n   ✅ Found {len(reviews)} reviews:")
        for i, review in enumerate(reviews, 1):
            print(f"\n   {i}. [{review.get('source', 'unknown')}]")
            snippet = review.get('snippet', 'No snippet')[:150]
            print(f"      {snippet}...")
            print(f"      URL: {review.get('url', 'N/A')[:80]}")
    else:
        print(f"\n   ❌ No reviews found")

async def main():
    print("=" * 80)
    print("COMPARING NAME VARIATIONS")
    print("Testing OpenAI search with different capitalizations")
    print("=" * 80)

    # Test 3 variations
    names = [
        "tang boon nee",
        "Tang Boon Nee",
        "Dr Tang Boon Nee"
    ]

    for i, name in enumerate(names, 1):
        await test_name_variation(name, i)
        await asyncio.sleep(2)  # Small delay between tests

    print("\n" + "=" * 80)
    print("COMPARISON COMPLETE")
    print("=" * 80)
    print("\nSummary:")
    print("Test 1: tang boon nee (lowercase)")
    print("Test 2: Tang Boon Nee (proper case)")
    print("Test 3: Dr Tang Boon Nee (with title)")
    print("\nCheck which format returned the most reviews.")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
