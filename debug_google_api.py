"""
Debug script to see full Google Custom Search API response
"""
import asyncio
import httpx
import json
from src.config import settings

async def test_google_api():
    """Test what fields Google API returns"""

    api_key = settings.google_search_api_key
    search_engine_id = settings.google_search_engine_id

    # Search for Dr Tang Boon Nee
    query = '"Dr Tang Boon Nee" Malaysia (review OR reviews OR testimonial OR feedback OR experience)'
    site = "forum.lowyat.net"
    site_query = f"{query} site:{site}"

    params = {
        "key": api_key,
        "cx": search_engine_id,
        "q": site_query,
        "num": 3  # Just get 3 results for testing
    }

    print(f"🔍 Searching: {site_query}\n")

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get("https://www.googleapis.com/customsearch/v1", params=params)
        response.raise_for_status()
        data = response.json()

    # Print full response structure for first item
    if data.get("items"):
        print("=" * 80)
        print("FULL FIRST ITEM STRUCTURE:")
        print("=" * 80)
        print(json.dumps(data["items"][0], indent=2, ensure_ascii=False))

        print("\n" + "=" * 80)
        print("ALL AVAILABLE FIELDS IN FIRST ITEM:")
        print("=" * 80)
        for key in data["items"][0].keys():
            print(f"  - {key}")

        print("\n" + "=" * 80)
        print("SNIPPET COMPARISON:")
        print("=" * 80)
        item = data["items"][0]
        print(f"URL: {item.get('link')}")
        print(f"\nsnippet:\n{item.get('snippet')}")
        print(f"\nhtmlSnippet:\n{item.get('htmlSnippet')}")

        # Check if there are other text fields
        if 'pagemap' in item:
            print(f"\npagemap keys: {list(item['pagemap'].keys())}")

if __name__ == "__main__":
    asyncio.run(test_google_api())
