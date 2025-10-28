#!/usr/bin/env python3
"""
测试生产环境配置
检查Google Places API等关键环境变量
"""

import os
import asyncio
import httpx
from src.config import settings

async def test_production_env():
    print("=" * 60)
    print("🔍 测试生产环境配置")
    print("=" * 60)
    
    # 检查关键环境变量
    print("\n📋 环境变量检查:")
    print("-" * 40)
    
    # Google Places API
    google_places_key = getattr(settings, 'google_places_api_key', None)
    if google_places_key and google_places_key != "not_required":
        print(f"✅ GOOGLE_PLACES_API_KEY: {google_places_key[:20]}...")
    else:
        print("❌ GOOGLE_PLACES_API_KEY: 未配置")
    
    # Google Search API
    google_search_key = getattr(settings, 'google_search_api_key', None)
    if google_search_key:
        print(f"✅ GOOGLE_SEARCH_API_KEY: {google_search_key[:20]}...")
    else:
        print("❌ GOOGLE_SEARCH_API_KEY: 未配置")
    
    google_search_engine = getattr(settings, 'google_search_engine_id', None)
    if google_search_engine:
        print(f"✅ GOOGLE_SEARCH_ENGINE_ID: {google_search_engine}")
    else:
        print("❌ GOOGLE_SEARCH_ENGINE_ID: 未配置")
    
    # OpenAI API
    openai_key = getattr(settings, 'openai_api_key', None)
    if openai_key:
        print(f"✅ OPENAI_API_KEY: {openai_key[:20]}...")
    else:
        print("❌ OPENAI_API_KEY: 未配置")
    
    # Twilio配置
    twilio_sid = getattr(settings, 'twilio_account_sid', None)
    if twilio_sid:
        print(f"✅ TWILIO_ACCOUNT_SID: {twilio_sid[:20]}...")
    else:
        print("❌ TWILIO_ACCOUNT_SID: 未配置")
    
    # 测试Google Places API
    print("\n🧪 测试Google Places API:")
    print("-" * 40)
    
    if google_places_key and google_places_key != "not_required":
        try:
            from src.search.google_places import google_places_client
            
            print(f"Google Places客户端启用状态: {google_places_client.enabled}")
            
            if google_places_client.enabled:
                print("正在测试Google Places API...")
                result = await google_places_client.search_doctor(
                    doctor_name="Paul Ng Hock Oon",
                    location="Malaysia"
                )
                
                if result:
                    reviews = result.get("reviews", [])
                    print(f"✅ 找到 {len(reviews)} 条评价")
                    print(f"   总评价数: {result.get('total_reviews', 0)}")
                    print(f"   评分: {result.get('rating', 0)}/5.0")
                else:
                    print("❌ 未找到评价")
            else:
                print("❌ Google Places客户端未启用")
                
        except Exception as e:
            print(f"❌ Google Places API测试失败: {e}")
    else:
        print("❌ Google Places API密钥未配置，跳过测试")
    
    # 测试搜索聚合器
    print("\n🔍 测试搜索聚合器:")
    print("-" * 40)
    
    try:
        from src.search.aggregator import search_aggregator
        
        print("正在测试搜索聚合器...")
        result = await search_aggregator.search_doctor_reviews(
            doctor_name="Paul Ng Hock Oon",
            location="Malaysia"
        )
        
        reviews = result.get("reviews", [])
        source = result.get("source", "unknown")
        
        print(f"✅ 搜索完成")
        print(f"   来源: {source}")
        print(f"   评价数: {len(reviews)}")
        
        if reviews:
            print("   评价来源分布:")
            sources = {}
            for review in reviews:
                review_source = review.get("source", "unknown")
                sources[review_source] = sources.get(review_source, 0) + 1
            
            for source_name, count in sources.items():
                print(f"     {source_name}: {count}条")
        else:
            print("❌ 未找到任何评价")
            
    except Exception as e:
        print(f"❌ 搜索聚合器测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_production_env())
