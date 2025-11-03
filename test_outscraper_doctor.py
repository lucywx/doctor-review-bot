#!/usr/bin/env python3
"""
测试Outscraper能否从Google Maps找到医生的评价
"""
import os
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.search.outscraper_client import OutscraperClient, OutscraperConfig

def test_doctor_reviews():
    """测试搜索医生评价"""

    api_key = os.getenv('OUTSCRAPER_API_KEY')
    if not api_key:
        print("❌ 请设置环境变量 OUTSCRAPER_API_KEY")
        return

    config = OutscraperConfig(api_key=api_key)
    client = OutscraperClient(config)

    print("=" * 60)
    print("🔍 测试：搜索 Dr. Nicholas Lim Lye Tak 的 Google Maps 评价")
    print("=" * 60)

    # 测试1：搜索医生的诊所/医院
    print("\n📍 步骤1: 搜索医生所在的医院...")
    doctor_name = "Dr. Nicholas Lim Lye Tak"
    location = "Petaling Jaya, Malaysia"

    businesses = client.search_businesses(
        query=f"{doctor_name}",
        location=location,
        limit=5,
        language="en"
    )

    if not businesses:
        print("❌ 未找到相关医院/诊所")
        return

    print(f"✅ 找到 {len(businesses)} 个地点:")
    for i, business in enumerate(businesses, 1):
        print(f"\n{i}. {business.name}")
        print(f"   地址: {business.address}")
        print(f"   评分: {business.rating} ({business.reviews_count} 条评价)")
        print(f"   Place ID: {business.place_id}")

    # 测试2：获取第一个地点的所有评价
    print("\n" + "=" * 60)
    print("📝 步骤2: 获取医院的评价...")
    print("=" * 60)

    target_business = businesses[0]
    print(f"\n正在获取 {target_business.name} 的评价...")

    # 获取较多评价（比如100条）
    all_reviews = client.get_business_reviews(
        place_id=target_business.place_id,
        limit=100,  # 获取100条评价
        language="en"
    )

    if not all_reviews:
        print("❌ 未获取到评价")
        return

    print(f"✅ 获取到 {len(all_reviews)} 条评价")

    # 测试3：在评价中搜索提到医生名字的
    print("\n" + "=" * 60)
    print(f"🔍 步骤3: 过滤提到 '{doctor_name}' 的评价...")
    print("=" * 60)

    # 提取医生名字的关键词
    keywords = ["nicholas", "lim", "dr. lim", "dr lim", "dr nicholas"]

    relevant_reviews = []
    for review in all_reviews:
        text_lower = review.text.lower()
        if any(keyword in text_lower for keyword in keywords):
            relevant_reviews.append(review)

    print(f"\n✅ 找到 {len(relevant_reviews)} 条提到医生的评价:")
    print(f"   (从 {len(all_reviews)} 条总评价中筛选)")

    if relevant_reviews:
        print("\n相关评价内容:")
        for i, review in enumerate(relevant_reviews[:5], 1):  # 只显示前5条
            print(f"\n{i}. {review.author_name} ({review.rating}⭐)")
            print(f"   时间: {review.time}")
            print(f"   内容: {review.text[:200]}...")
            print("-" * 60)

        # 保存结果
        output_file = "doctor_reviews_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            result = {
                'doctor_name': doctor_name,
                'hospital': target_business.name,
                'total_reviews_fetched': len(all_reviews),
                'relevant_reviews_found': len(relevant_reviews),
                'reviews': [
                    {
                        'author': r.author_name,
                        'rating': r.rating,
                        'text': r.text,
                        'time': r.time
                    } for r in relevant_reviews
                ]
            }
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\n📁 完整结果已保存到: {output_file}")
    else:
        print("\n⚠️ 在前100条评价中未找到提到医生的评价")
        print("   可能需要：")
        print("   1. 增加获取的评价数量 (limit > 100)")
        print("   2. 调整搜索关键词")
        print("   3. 搜索其他相关地点")

    # 测试4：费用估算
    print("\n" + "=" * 60)
    print("💰 费用估算")
    print("=" * 60)

    # 如果要获取500条评价
    cost_info = client.estimate_cost(
        business_count=1,
        reviews_per_business=500
    )

    print(f"\n获取500条评价的费用:")
    print(f"   总评价数: {cost_info['total_reviews']}")
    print(f"   免费额度: {cost_info['free_reviews']}")
    print(f"   需付费: {cost_info['paid_reviews']} 条")
    print(f"   预估费用: ${cost_info['estimated_cost']}")
    print(f"   套餐: {cost_info['tier']}")

    print("\n✅ 测试完成!")
    print("\n💡 建议:")
    if relevant_reviews:
        print(f"   - Outscraper 成功找到了 {len(relevant_reviews)} 条相关评价")
        print("   - 可以集成到生产环境")
    else:
        print("   - 需要调整搜索策略或增加评价获取数量")
        print("   - 或搜索医生的其他工作地点")

if __name__ == "__main__":
    test_doctor_reviews()
