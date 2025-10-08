"""
Quick test script to verify OpenAI API connection
"""
import asyncio
from src.analysis.sentiment import sentiment_analyzer

async def test_openai():
    print("🧪 Testing OpenAI API connection...\n")

    # Test reviews
    test_reviews = [
        {
            "snippet": "李医生非常专业，态度很好，耐心解答问题",
            "source": "test",
            "url": "test"
        },
        {
            "snippet": "等待时间太长，医生态度不好",
            "source": "test",
            "url": "test"
        }
    ]

    try:
        # Analyze sentiment
        print("📊 Analyzing sentiment...\n")
        analyzed = await sentiment_analyzer.analyze_reviews(test_reviews)

        # Display results
        for i, review in enumerate(analyzed, 1):
            sentiment = review.get("sentiment", "unknown")
            snippet = review.get("snippet", "")[:50]

            emoji = "✅" if sentiment == "positive" else "❌" if sentiment == "negative" else "⚪"
            print(f"{emoji} Review {i}: {sentiment}")
            print(f"   Text: {snippet}...")
            print()

        print("🎉 OpenAI API is working correctly!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nPossible issues:")
        print("  1. Invalid API key")
        print("  2. Insufficient credits")
        print("  3. Network connection problem")
        return False

if __name__ == "__main__":
    asyncio.run(test_openai())
