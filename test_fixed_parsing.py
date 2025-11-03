#!/usr/bin/env python3
"""
测试修复后的响应解析
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.search.chatgpt_search import get_chatgpt_client

async def test_fixed_parsing():
    print("🔍 测试修复后的 Responses API 解析...")
    print("="*60)

    client = get_chatgpt_client()

    if not client.enabled:
        print("❌ ChatGPT client not enabled")
        return

    doctor_name = "Dr Tang Boon Nee"
    location = "Malaysia"

    print(f"🔍 搜索: {doctor_name} in {location}\n")

    result = await client.search_facebook_and_forums(doctor_name, location)

    print("\n" + "="*60)
    print("📊 搜索结果:")
    print("="*60)
    print(f"来源: {result.get('source')}")
    print(f"评价数量: {result.get('total_count')}")
    print(f"Citations: {len(result.get('citations', []))}")

    if result.get('citations'):
        print("\n📚 引用来源:")
        for i, citation in enumerate(result.get('citations', []), 1):
            print(f"  {i}. {citation.get('title')}")
            print(f"     {citation.get('url')}")

    if result.get('summary'):
        print(f"\n📝 总结:")
        print(result['summary'][:1000])
        if len(result['summary']) > 1000:
            print(f"\n... (总共 {len(result['summary'])} 字符)")

    print("\n✅ 测试完成！")

if __name__ == "__main__":
    asyncio.run(test_fixed_parsing())
