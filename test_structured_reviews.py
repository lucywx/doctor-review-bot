#!/usr/bin/env python3
"""
测试结构化评价提取
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.search.chatgpt_search import get_chatgpt_client

async def test_structured_extraction():
    print("🔍 测试结构化评价提取...")
    print("="*80)

    client = get_chatgpt_client()

    if not client.enabled:
        print("❌ ChatGPT client not enabled")
        return

    doctor_name = "Dr Tang Boon Nee"
    location = "Malaysia"

    print(f"🔍 搜索: {doctor_name} in {location}\n")

    result = await client.search_facebook_and_forums(doctor_name, location)

    print("\n" + "="*80)
    print("📊 搜索结果:")
    print("="*80)
    print(f"来源: {result.get('source')}")
    print(f"评价数量: {result.get('total_count')}")
    print(f"Citations: {len(result.get('citations', []))}")

    if result.get('reviews'):
        print(f"\n📝 提取的结构化评价 ({len(result['reviews'])} 条):")
        print("="*80)
        for i, review in enumerate(result['reviews'], 1):
            print(f"\n{i}. 【{review.get('place_name', 'Unknown')}】")
            print(f"   患者: {review.get('author_name', 'Anonymous')}")
            print(f"   日期: {review.get('review_date', 'Unknown')}")
            print(f"   评分: {'⭐' * review.get('rating', 0) if review.get('rating') else 'N/A'}")
            print(f"   内容: {review.get('text', '')[:200]}...")
            print(f"   链接: {review.get('url', 'N/A')}")

    if result.get('summary'):
        print(f"\n📄 原始总结:")
        print("="*80)
        print(result['summary'][:500])
        if len(result['summary']) > 500:
            print(f"\n... (总共 {len(result['summary'])} 字符)")

    if result.get('citations'):
        print(f"\n📚 引用来源:")
        print("="*80)
        for i, citation in enumerate(result['citations'], 1):
            print(f"  {i}. {citation.get('title')}")
            print(f"     {citation.get('url')}")

    print("\n" + "="*80)
    print("✅ 测试完成！")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_structured_extraction())
