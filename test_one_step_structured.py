#!/usr/bin/env python3
"""
测试：能否让 Responses API 直接返回结构化数据
模仿 ChatGPT 网页版的行为
"""

import asyncio
import os
from openai import AsyncOpenAI

async def test_one_step():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found")
        return

    client = AsyncOpenAI(api_key=api_key)

    print("🔍 测试：能否一步获得结构化数据")
    print("="*80)

    # 尝试用非常明确的 prompt
    response = await client.responses.create(
        model="gpt-5-mini",
        tools=[{"type": "web_search"}],
        input="""Search for patient reviews about Dr Tang Boon Nee in Malaysia.

IMPORTANT: After searching, please format your response as a structured list. For each review you find, provide:

1. Patient name (or "Anonymous")
2. Review date (YYYY-MM-DD format)
3. Review content (the actual patient comment)
4. Rating (1-5 stars if mentioned)
5. Source website name
6. Source URL

Format each review clearly with these labels so I can parse it programmatically.

Example format:
---
REVIEW 1:
- Patient: Anonymous
- Date: 2019-05-15
- Rating: 4/5
- Content: "Waiting time is long but she is quite friendly and caring"
- Source: Lowyat Forum
- URL: https://forum.lowyat.net/...
---

Please search and return reviews in this exact format."""
    )

    # 提取文本
    if hasattr(response, 'output') and isinstance(response.output, list):
        for item in response.output:
            if hasattr(item, 'type') and item.type == 'message':
                if hasattr(item, 'content'):
                    for content_block in item.content:
                        if hasattr(content_block, 'text'):
                            print("\n📝 Responses API 返回:")
                            print("="*80)
                            print(content_block.text)
                            print("="*80)

    print("\n✅ 测试完成")
    print("\n💡 分析：")
    print("   如果返回的是结构化格式（如上述 REVIEW 1, REVIEW 2...）")
    print("   那我们可以用简单的正则表达式解析，不需要第二次 API 调用")
    print("   如果返回的还是自然语言段落，那还是需要两步法")

if __name__ == "__main__":
    asyncio.run(test_one_step())
