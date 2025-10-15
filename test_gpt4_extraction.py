"""
Test GPT-4 extraction from a real Lowyat forum page
"""
import asyncio
import httpx
from openai import AsyncOpenAI
import json
import os

async def test_extraction():
    # Fetch the page
    url = "https://forum.lowyat.net/topic/1598645/all"
    doctor_name = "Tang Boon Nee"

    print(f"🔍 Testing extraction from: {url}")

    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        response = await client.get(url)
        html_content = response.text[:15000]

    print(f"📄 HTML length: {len(html_content)}")
    print(f"📝 First 500 chars:\n{html_content[:500]}\n")

    # Check if doctor name appears in HTML
    if doctor_name.lower() in html_content.lower():
        print(f"✅ Doctor name '{doctor_name}' found in HTML")
    else:
        print(f"❌ Doctor name '{doctor_name}' NOT found in HTML")

    # Test GPT-4 extraction
    openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    extraction_prompt = f"""Analyze this webpage and extract ONLY genuine patient reviews about {doctor_name}.

Rules:
- ONLY include actual patient experiences and reviews
- EXCLUDE doctor bios, introductions, and professional descriptions
- EXCLUDE hospital promotional content
- EXCLUDE "About the doctor" sections
- EXCLUDE directory listings and contact information

For each genuine patient review found, extract:
1. The full review text (patient's words)
2. Date (if available, in YYYY-MM-DD format)
3. Author name (if available)

URL: {url}

HTML Content:
{html_content}

Return a JSON object with this EXACT structure:
{{
  "reviews": [
    {{
      "snippet": "Full patient review text here",
      "review_date": "YYYY-MM-DD or empty string",
      "author_name": "Name or empty string",
      "url": "{url}"
    }}
  ]
}}

If NO genuine patient reviews are found, return: {{"reviews": []}}"""

    print("🤖 Calling GPT-4...")
    completion = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert at extracting genuine patient reviews from webpages. You distinguish between patient reviews and doctor information."},
            {"role": "user", "content": extraction_prompt}
        ],
        temperature=0.1,
        response_format={"type": "json_object"}
    )

    content = completion.choices[0].message.content
    result = json.loads(content)

    print(f"\n📊 GPT-4 Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    reviews = result.get("reviews", [])
    print(f"\n✅ Found {len(reviews)} reviews")

if __name__ == "__main__":
    asyncio.run(test_extraction())
