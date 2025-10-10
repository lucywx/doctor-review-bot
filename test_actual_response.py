#!/usr/bin/env python3
"""Test actual OpenAI response to diagnose the 0 results issue"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.search.openai_web_searcher import openai_web_searcher

async def test_search():
    print("=" * 80)
    print("Testing OpenAI Web Search with actual code")
    print("=" * 80)

    doctor_name = "Tang Boon Nee"
    print(f"\n🔍 Searching for: {doctor_name}\n")

    result = await openai_web_searcher.search_doctor_reviews(
        doctor_name=doctor_name,
        specialty="",
        location=""
    )

    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"Total reviews found: {result['total_count']}")
    print(f"Source: {result['source']}")

    if 'error' in result:
        print(f"\n❌ Error: {result['error']}")

    if result['reviews']:
        print(f"\n✅ Found {len(result['reviews'])} reviews:\n")
        for i, review in enumerate(result['reviews'], 1):
            print(f"{i}. {review['source']}")
            print(f"   Snippet: {review['snippet'][:100]}...")
            print(f"   Author: {review.get('author_name', 'N/A')}")
            print(f"   Date: {review.get('review_date', 'N/A')}")
            print(f"   Rating: {review.get('rating', 'N/A')}")
            print(f"   URL: {review.get('url', 'N/A')}")
            print()
    else:
        print("\n❌ No reviews found")

    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_search())
