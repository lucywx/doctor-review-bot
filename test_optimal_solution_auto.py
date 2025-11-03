"""
自动测试最优方案 - Outscraper + ChatGPT-4o-mini
非交互式版本，自动运行所有测试

运行：
python test_optimal_solution_auto.py
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.search.aggregator import search_aggregator


async def test_components():
    """测试各个组件"""

    print("=" * 70)
    print("测试各个组件")
    print("=" * 70)
    print()

    # 测试 Outscraper
    print("1. 测试 Outscraper")
    print("-" * 70)

    from src.search.outscraper_client import get_outscraper_client

    outscraper = get_outscraper_client()
    print(f"Outscraper 状态: {'✅ 已启用' if outscraper.enabled else '❌ 未配置'}")

    if outscraper.enabled:
        result = await outscraper.search_doctor_reviews(
            doctor_name="Dr. Nicholas Lim",
            location="Malaysia",
            limit=5
        )
        print(f"测试搜索结果: {result.get('total_count', 0)} 条评价")
    else:
        print("⚠️ Outscraper API key 未配置")
        print("   请在 .env 文件中设置 OUTSCRAPER_API_KEY")

    print()

    # 测试 ChatGPT
    print("2. 测试 ChatGPT")
    print("-" * 70)

    from src.search.chatgpt_search import get_chatgpt_client

    chatgpt = get_chatgpt_client()
    print(f"ChatGPT 状态: {'✅ 已启用' if chatgpt.enabled else '❌ 未配置'}")

    if chatgpt.enabled:
        print("正在搜索 Facebook 和论坛评价...")
        result = await chatgpt.search_facebook_and_forums(
            doctor_name="Dr. Nicholas Lim",
            location="Malaysia"
        )
        print(f"测试搜索结果: {result.get('total_count', 0)} 条评价")
        if result.get('summary'):
            print(f"总结: {result['summary']}")
    else:
        print("⚠️ OpenAI API key 未配置")
        print("   请在 .env 文件中设置 OPENAI_API_KEY")

    print()


async def test_search():
    """测试搜索功能"""

    print("=" * 70)
    print("测试最优方案：Outscraper + ChatGPT-4o-mini")
    print("=" * 70)
    print()

    # 测试医生
    test_doctors = [
        "Dr. Nicholas Lim Lye Tak",
    ]

    for doctor_name in test_doctors:
        print("-" * 70)
        print(f"测试医生: {doctor_name}")
        print("-" * 70)
        print()

        # 执行搜索
        result = await search_aggregator.search_doctor_reviews(
            doctor_name=doctor_name,
            location="Malaysia"
        )

        # 显示结果
        print(f"医生ID: {result.get('doctor_id', 'N/A')}")
        print(f"总评价数: {result.get('total_count', 0)}")
        print(f"  - Google Maps: {result.get('google_maps_count', 0)} 条")
        print(f"  - Facebook/论坛: {result.get('facebook_forums_count', 0)} 条")
        print()

        # ChatGPT 总结
        if result.get('chatgpt_summary'):
            print(f"ChatGPT 总结: {result['chatgpt_summary']}")
            print()

        # 显示评价
        reviews = result.get('reviews', [])
        if reviews:
            print(f"评价列表（共 {len(reviews)} 条）:")
            for i, review in enumerate(reviews[:5], 1):  # 只显示前 5 条
                print(f"\n{i}. 来源: {review.get('source', 'unknown')}")
                print(f"   评分: {review.get('rating', 'N/A')}")
                print(f"   内容: {review.get('text', '')[:200]}...")
                if review.get('place_name'):
                    print(f"   地点: {review['place_name']}")
        else:
            print("⚠️ 未找到评价")

        print()
        print()


async def main():
    """主函数"""

    print()
    print("🚀 最优方案自动测试脚本")
    print()

    # 检查环境变量
    print("检查环境变量...")
    print("-" * 70)

    openai_key = os.getenv("OPENAI_API_KEY", "")
    outscraper_key = os.getenv("OUTSCRAPER_API_KEY", "")

    if openai_key and openai_key != "your_openai_api_key_here":
        print("✅ OPENAI_API_KEY 已设置")
    else:
        print("❌ OPENAI_API_KEY 未设置")

    if outscraper_key and outscraper_key != "your_outscraper_api_key_here":
        print("✅ OUTSCRAPER_API_KEY 已设置")
    else:
        print("❌ OUTSCRAPER_API_KEY 未设置")

    print()

    # 运行测试
    print("开始运行测试...")
    print()

    # 测试各个组件
    await test_components()
    print()
    print()

    # 测试完整搜索流程
    await test_search()

    print()
    print("=" * 70)
    print("测试完成！")
    print("=" * 70)
    print()


if __name__ == "__main__":
    asyncio.run(main())
