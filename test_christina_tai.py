"""
Test script to see what URLs Google returns for Dr Christina Tai Fook Min
"""
import asyncio
import httpx
import json
from src.config import settings

async def test_christina_tai():
    """Test what URLs Google API returns for Dr Christina Tai"""

    api_key = settings.google_search_api_key
    search_engine_id = settings.google_search_engine_id

    # Search query (same as bot uses)
    query = '"Dr Christina Tai Fook Min" Malaysia (review OR reviews OR testimonial OR feedback OR experience OR complaint OR lawsuit OR sued OR malpractice OR negligence)'

    params = {
        "key": api_key,
        "cx": search_engine_id,
        "q": query,
        "num": 10
    }

    print(f"🔍 Searching: {query}\n")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get("https://www.googleapis.com/customsearch/v1", params=params)
        response.raise_for_status()
        data = response.json()

    items = data.get("items", [])

    if not items:
        print("❌ No results found!")
        return

    print(f"Found {len(items)} results\n")
    print("=" * 80)

    for i, item in enumerate(items, 1):
        url = item.get("link", "")
        title = item.get("title", "")
        snippet = item.get("snippet", "")

        print(f"\n{i}. {title}")
        print(f"   URL: {url}")
        print(f"   Snippet: {snippet[:100]}...")
        print(f"   URL Length: {len(url)} chars")

        # Check if URL works
        if "linkedin.com" in url:
            print(f"   🔗 LinkedIn URL detected!")

if __name__ == "__main__":
    asyncio.run(test_christina_tai())
