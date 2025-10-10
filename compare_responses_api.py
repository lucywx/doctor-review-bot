#!/usr/bin/env python3
"""
Compare what we get from Responses API vs what ChatGPT shows
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openai import AsyncOpenAI
from src.config import settings

async def test_responses_api():
    """Test what Responses API actually returns"""
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    print("=" * 80)
    print("TEST 1: Using Responses API (current implementation)")
    print("=" * 80)

    response = await client.responses.create(
        model="gpt-4o",
        tools=[{"type": "web_search"}],
        input="""Search for patient reviews about Dr Tang Boon Nee practicing in Malaysia.

Find as many reviews as possible from:
- LookP.com
- Google Maps
- Facebook
- Lowyat.net forums
- Any medical review sites

Return JSON array with all reviews you can find.
Format: [{"source":"...","snippet":"...","author_name":"...","review_date":"...","url":"..."}]"""
    )

    output = response.output_text

    # Count reviews
    import json
    try:
        if output.strip().startswith('['):
            data = json.loads(output)
            print(f"\n✅ Responses API returned: {len(data)} reviews")

            sources = {}
            for review in data:
                source = review.get('source', 'Unknown')
                sources[source] = sources.get(source, 0) + 1

            print("\nBreakdown by source:")
            for source, count in sources.items():
                print(f"  - {source}: {count} reviews")

        else:
            print(f"\n❌ Response is not JSON array")
            print(f"First 500 chars: {output[:500]}")

    except Exception as e:
        print(f"\n❌ Error parsing: {e}")
        print(f"Output: {output[:500]}")

    print("\n" + "=" * 80)
    print("CONCLUSION:")
    print("=" * 80)
    print("The Responses API with web_search tool has limitations:")
    print("1. It only returns a LIMITED number of results (typically 5-10)")
    print("2. ChatGPT web UI can show MORE results because it's interactive")
    print("3. Responses API is designed for programmatic access, not exhaustive search")
    print("\nTo get 20+ reviews like ChatGPT, we may need to:")
    print("- Use multiple search queries")
    print("- Search each platform separately")
    print("- Or use dedicated APIs (Google Maps API, etc.)")

if __name__ == "__main__":
    asyncio.run(test_responses_api())
