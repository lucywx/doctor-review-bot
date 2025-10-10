import asyncio
from openai import AsyncOpenAI
from src.config import settings

async def test():
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    print("Testing current prompt...")
    response = await client.responses.create(
        model='gpt-4o',
        tools=[{'type': 'web_search'}],
        input="""Search for patient reviews and feedback about Dr Tang Boon Nee.
                Look for reviews from Google Maps, hospital websites, medical forums, and social media.
                Return the reviews in JSON format with fields: source, snippet, rating, author_name, review_date, url.
                If you find reviews, return them. If no reviews found, return empty array []."""
    )

    text = response.output_text
    print(f"Response length: {len(text)}")
    print(f"\nFirst 500 chars:\n{text[:500]}")
    print("\n...")
    print(f"\nLast 500 chars:\n{text[-500:]}")

    # Check JSON
    if '```json' in text:
        print("\n✅ Found JSON markdown block")
        import re
        match = re.search(r'```json\s*\n(.*?)\n```', text, re.DOTALL)
        if match:
            json_text = match.group(1)
            print(f"Extracted JSON length: {len(json_text)}")
            print(f"First 200 chars: {json_text[:200]}")
    else:
        print("\n❌ No JSON markdown found")

if __name__ == "__main__":
    asyncio.run(test())
