"""
简单测试 GPT-5 Responses API
"""

import asyncio
import os
from openai import AsyncOpenAI


async def main():
    api_key = os.getenv("OPENAI_API_KEY", "")

    if not api_key:
        print("❌ No API key")
        return

    client = AsyncOpenAI(api_key=api_key)

    print("🧪 测试 GPT-5 Responses API + Web Search")
    print("=" * 70)
    print()
    print("⏳ 正在搜索（可能需要 1-2 分钟）...")
    print()

    try:
        response = await client.responses.create(
            model="gpt-5",
            reasoning={"effort": "low"},
            tools=[{"type": "web_search"}],
            tool_choice="auto",
            input="Search for patient reviews about Dr Tang Boon Nee in Malaysia."
        )

        print("✅ 搜索完成！")
        print("-" * 70)
        print(response.output)
        print()
        print("=" * 70)

    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())
