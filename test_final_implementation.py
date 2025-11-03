#!/usr/bin/env python3
"""
测试最终实现：Responses API + gpt-5-mini + Outscraper
测试医生：Dr Tang Boon Nee（之前成功找到评价的案例）
"""

import asyncio
import os
import sys

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not installed, using system environment variables")

# 添加 src 目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.search.chatgpt_search import get_chatgpt_client
from src.search.outscraper_client import get_outscraper_client


async def test_chatgpt_responses_api():
    """测试 ChatGPT Responses API + gpt-5-mini"""
    print("\n" + "="*60)
    print("测试 1: ChatGPT Responses API + gpt-5-mini + web_search")
    print("="*60)

    doctor_name = "Dr Tang Boon Nee"
    location = "Malaysia"

    client = get_chatgpt_client()

    if not client.enabled:
        print("❌ ChatGPT client not enabled (API key not configured)")
        return

    print(f"\n🔍 搜索医生: {doctor_name}")
    print(f"📍 地点: {location}\n")

    result = await client.search_facebook_and_forums(doctor_name, location)

    print(f"\n📊 搜索结果:")
    print(f"   - 来源: {result.get('source')}")
    print(f"   - 评价数量: {result.get('total_count')}")

    if result.get('summary'):
        print(f"\n📝 总结:\n{result['summary'][:500]}...")

    if result.get('error'):
        print(f"\n❌ 错误: {result['error']}")


async def test_outscraper():
    """测试 Outscraper Google Maps 搜索"""
    print("\n" + "="*60)
    print("测试 2: Outscraper Google Maps 关键词搜索")
    print("="*60)

    doctor_name = "Dr Tang Boon Nee"
    location = "Malaysia"

    client = get_outscraper_client()

    if not client.enabled:
        print("❌ Outscraper client not enabled (API key not configured)")
        return

    print(f"\n🔍 搜索医生: {doctor_name}")
    print(f"📍 地点: {location}\n")

    result = await client.search_doctor_reviews(doctor_name, location, limit=10)

    print(f"\n📊 搜索结果:")
    print(f"   - 来源: {result.get('source')}")
    print(f"   - 评价数量: {result.get('total_count')}")

    if result.get('reviews'):
        print(f"\n📝 前 3 条评价:")
        for i, review in enumerate(result['reviews'][:3], 1):
            print(f"\n   {i}. {review.get('text', '')[:100]}...")
            print(f"      ⭐ 评分: {review.get('rating')}")
            print(f"      📍 地点: {review.get('place_name')}")
            print(f"      🔗 来源: {review.get('url')}")

    if result.get('error'):
        print(f"\n❌ 错误: {result['error']}")


async def main():
    """运行所有测试"""
    print("\n🚀 开始测试最终实现")
    print("架构: Responses API + gpt-5-mini + Outscraper")

    # 测试 ChatGPT Responses API
    await test_chatgpt_responses_api()

    # 测试 Outscraper
    await test_outscraper()

    print("\n" + "="*60)
    print("✅ 测试完成")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
