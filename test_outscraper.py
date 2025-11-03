#!/usr/bin/env python3
"""
Outscraper测试脚本
用于测试Google Maps数据提取功能
"""

import os
import sys
import json
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.search.outscraper_client import OutscraperClient, OutscraperConfig

def test_outscraper():
    """测试Outscraper功能"""
    
    # 从环境变量获取API密钥
    api_key = os.getenv('OUTSCRAPER_API_KEY')
    if not api_key:
        print("❌ 请设置环境变量 OUTSCRAPER_API_KEY")
        print("   您可以在Outscraper官网注册后获取API密钥")
        return False
    
    # 创建配置
    config = OutscraperConfig(api_key=api_key)
    client = OutscraperClient(config)
    
    print("🚀 开始测试Outscraper...")
    
    # 1. 测试账户信息
    print("\n📊 获取账户信息...")
    account_info = client.get_account_info()
    if account_info:
        print(f"✅ 账户信息获取成功")
        print(f"   账户状态: {account_info.get('status', 'unknown')}")
        print(f"   余额: ${account_info.get('balance', 0)}")
    else:
        print("❌ 账户信息获取失败")
    
    # 2. 测试商家搜索
    print("\n🔍 测试商家搜索...")
    test_query = "咖啡店"
    test_location = "北京"
    
    businesses = client.search_businesses(
        query=test_query,
        location=test_location,
        limit=5
    )
    
    if businesses:
        print(f"✅ 成功找到 {len(businesses)} 个商家:")
        for i, business in enumerate(businesses, 1):
            print(f"   {i}. {business.name}")
            print(f"      地址: {business.address}")
            print(f"      评分: {business.rating}")
            print(f"      电话: {business.phone}")
            print()
    else:
        print("❌ 商家搜索失败")
        return False
    
    # 3. 测试评论获取
    print("💬 测试评论获取...")
    if businesses and businesses[0].place_id:
        reviews = client.get_business_reviews(
            place_id=businesses[0].place_id,
            limit=5
        )
        
        if reviews:
            print(f"✅ 成功获取 {len(reviews)} 条评论:")
            for i, review in enumerate(reviews, 1):
                print(f"   {i}. {review.author_name} ({review.rating}⭐)")
                print(f"      {review.text[:100]}...")
                print()
        else:
            print("❌ 评论获取失败")
    
    # 4. 测试综合搜索
    print("🔄 测试综合搜索...")
    result = client.search_with_reviews(
        query="餐厅",
        location="上海",
        business_limit=3,
        reviews_per_business=5
    )
    
    if result and 'businesses' in result:
        print(f"✅ 综合搜索成功:")
        print(f"   商家数量: {result['total_businesses']}")
        print(f"   评论数量: {result['total_reviews']}")
        print(f"   搜索查询: {result['search_query']}")
        
        # 保存结果到文件
        output_file = f"outscraper_test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            # 转换为可序列化的格式
            serializable_result = {
                'businesses': [
                    {
                        'name': b.name,
                        'address': b.address,
                        'phone': b.phone,
                        'website': b.website,
                        'rating': b.rating,
                        'reviews_count': b.reviews_count,
                        'category': b.category,
                        'latitude': b.latitude,
                        'longitude': b.longitude,
                        'place_id': b.place_id
                    } for b in result['businesses']
                ],
                'reviews': [
                    {
                        'author_name': r.author_name,
                        'rating': r.rating,
                        'text': r.text,
                        'time': r.time,
                        'helpful_votes': r.helpful_votes
                    } for r in result['reviews']
                ],
                'total_businesses': result['total_businesses'],
                'total_reviews': result['total_reviews'],
                'search_query': result['search_query'],
                'timestamp': result['timestamp']
            }
            json.dump(serializable_result, f, ensure_ascii=False, indent=2)
        
        print(f"📁 结果已保存到: {output_file}")
    else:
        print("❌ 综合搜索失败")
        return False
    
    # 5. 费用估算
    print("\n💰 费用估算...")
    cost_info = client.estimate_cost(
        business_count=10,
        reviews_per_business=20
    )
    
    print(f"   总评论数: {cost_info['total_reviews']}")
    print(f"   免费额度: {cost_info['free_reviews']}")
    print(f"   付费部分: {cost_info['paid_reviews']}")
    print(f"   预估费用: ${cost_info['estimated_cost']}")
    print(f"   套餐类型: {cost_info['tier']}")
    
    print("\n✅ Outscraper测试完成!")
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 Outscraper Google Maps API 测试工具")
    print("=" * 60)
    
    # 检查环境变量
    if not os.getenv('OUTSCRAPER_API_KEY'):
        print("\n📝 使用说明:")
        print("1. 访问 https://outscraper.com/ 注册账户")
        print("2. 获取API密钥")
        print("3. 设置环境变量:")
        print("   export OUTSCRAPER_API_KEY='your_api_key_here'")
        print("4. 重新运行此脚本")
        return
    
    # 运行测试
    success = test_outscraper()
    
    if success:
        print("\n🎉 测试成功! Outscraper已准备就绪")
    else:
        print("\n❌ 测试失败，请检查配置")

if __name__ == "__main__":
    main()
