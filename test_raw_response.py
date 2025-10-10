#!/usr/bin/env python3
"""Check what OpenAI actually returns (raw response)"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openai import AsyncOpenAI
from src.config import settings

async def test():
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    print("Testing OpenAI Responses API - RAW OUTPUT")
    print("=" * 80)

    response = await client.responses.create(
        model="gpt-4o",
        tools=[{"type": "web_search"}],
        input="""Search for REAL patient reviews about Dr Tang Boon Nee (practicing in Malaysia).

SEARCH SOURCES (in priority order):
1. Medical Review Platforms:
   - LookP.com (Malaysia doctor reviews)
   - MediSata.com
   - TalkHealthAsia
   - Google Maps Malaysia

2. Social Media (PUBLIC posts only):
   - Facebook (clinic pages, public posts, community groups)
   - Instagram (public clinic accounts)

3. Forums & Communities:
   - Lowyat.net (Malaysia local forum - PRIORITY)
   - Reddit Malaysia
   - BabyCenter Malaysia (for ob/gyn, pediatrics)

4. Patient Blogs/Personal Experiences:
   - Search: "Dr Tang Boon Nee experience blog"
   - Personal blogs sharing medical journey
   - Medium/Blogspot posts about treatment experience

EXCLUDE:
✗ Editorial content from health websites (not patient reviews)
✗ Promotional articles
✗ News articles about the doctor
✗ Medical advice articles

OUTPUT REQUIREMENTS (CRITICAL - SYSTEM WILL FAIL IF NOT FOLLOWED):
1. Return ONLY the JSON array - nothing else
2. NO introductions (do not write "Here are the reviews...")
3. NO explanations after the JSON
4. NO citations or footnotes
5. NO markdown code blocks (do not wrap in ```)
6. Start response with [ and end with ]

Format: [{{"source":"LookP","snippet":"review text","rating":null,"author_name":"Name","review_date":"2023-01-01","url":"https://..."}}]
Empty: []"""
    )

    print("\n📦 RESPONSE OBJECT:")
    print(f"Type: {type(response)}")
    print(f"Dir: {[x for x in dir(response) if not x.startswith('_')]}")

    print("\n📝 OUTPUT_TEXT:")
    output = response.output_text
    print(f"Length: {len(output)} characters")
    print("\n" + "=" * 80)
    print(output)
    print("=" * 80)

    # Check if there's citation info
    if hasattr(response, 'output'):
        print("\n📚 OUTPUT ARRAY:")
        for i, item in enumerate(response.output):
            print(f"\nItem {i}: {type(item)}")
            print(f"Attributes: {[x for x in dir(item) if not x.startswith('_')]}")
            if hasattr(item, 'text'):
                print(f"Text: {item.text[:200]}...")
            if hasattr(item, 'citations'):
                print(f"Citations: {item.citations}")

if __name__ == "__main__":
    asyncio.run(test())
