"""
测试特定医生的搜索结果
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.search.aggregator import search_aggregator


async def test_doctor(doctor_name: str, location: str = "Malaysia"):
    """测试搜索特定医生"""

    print("=" * 70)
    print(f"🔍 搜索医生: {doctor_name}")
    print("=" * 70)
    print()

    # 执行搜索
    result = await search_aggregator.search_doctor_reviews(
        doctor_name=doctor_name,
        location=location
    )

    # 显示结果
    print(f"医生ID: {result.get('doctor_id', 'N/A')}")
    print(f"总评价数: {result.get('total_count', 0)}")
    print(f"  - Google Maps: {result.get('google_maps_count', 0)} 条")
    print(f"  - Facebook/论坛: {result.get('facebook_forums_count', 0)} 条")
    print()

    # ChatGPT 总结
    if result.get('chatgpt_summary'):
        print("📝 ChatGPT 总结:")
        print(f"   {result['chatgpt_summary']}")
        print()

    # 显示评价详情
    reviews = result.get('reviews', [])
    if reviews:
        print(f"📋 评价列表（共 {len(reviews)} 条）:")
        print("-" * 70)
        for i, review in enumerate(reviews, 1):
            print(f"\n{i}. 来源: {review.get('source', 'unknown')}")
            print(f"   评分: {review.get('rating', 'N/A')}")
            print(f"   作者: {review.get('author_name', 'N/A')}")
            print(f"   日期: {review.get('review_date', 'N/A')}")
            print(f"   内容: {review.get('text', '')[:200]}...")
            if review.get('url'):
                print(f"   链接: {review['url']}")
            if review.get('place_name'):
                print(f"   地点: {review['place_name']}")
    else:
        print("⚠️ 未找到评价")

    print()
    print("=" * 70)
    print()

    return result


async def main():
    """主函数"""

    print()
    print("🧪 测试特定医生搜索")
    print()

    # 测试 Dr Tang Boon Nee
    await test_doctor("Dr Tang Boon Nee", "Malaysia")


if __name__ == "__main__":
    asyncio.run(main())
