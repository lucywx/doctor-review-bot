#!/usr/bin/env python3
"""
检查生产环境Google Places API配置
"""

import asyncio
import httpx
import json

async def check_production_places_api():
    print("=" * 60)
    print("🔍 检查生产环境Google Places API配置")
    print("=" * 60)
    
    # 直接测试Google Places API
    api_key = "AIzaSyC0O-5Urc47Z1pF8hXpHVHAxC7NZowfjfw"
    
    print(f"🧪 直接测试Google Places API...")
    print(f"   API密钥: {api_key[:20]}...")
    
    # 测试Google Places Text Search API
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": "Dr Paul Ng Hock Oon Malaysia",
        "key": api_key,
        "language": "en"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "UNKNOWN")
                
                print(f"   ✅ API响应状态: {status}")
                
                if status == "OK":
                    results = data.get("results", [])
                    print(f"   ✅ 找到 {len(results)} 个地点")
                    
                    if results:
                        place = results[0]
                        print(f"   ✅ 第一个地点: {place.get('name', 'N/A')}")
                        print(f"   ✅ 地点ID: {place.get('place_id', 'N/A')}")
                        
                        # 测试获取详细信息
                        place_id = place.get('place_id')
                        if place_id:
                            print(f"\n🔍 测试获取地点详细信息...")
                            
                            details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                            details_params = {
                                "place_id": place_id,
                                "fields": "name,rating,user_ratings_total,reviews,formatted_address,url",
                                "key": api_key,
                                "language": "en"
                            }
                            
                            details_response = await client.get(details_url, params=details_params)
                            
                            if details_response.status_code == 200:
                                details_data = details_response.json()
                                details_status = details_data.get("status", "UNKNOWN")
                                
                                print(f"   ✅ 详细信息状态: {details_status}")
                                
                                if details_status == "OK":
                                    result = details_data.get("result", {})
                                    reviews = result.get("reviews", [])
                                    
                                    print(f"   ✅ 地点名称: {result.get('name', 'N/A')}")
                                    print(f"   ✅ 评分: {result.get('rating', 0)}/5.0")
                                    print(f"   ✅ 总评价数: {result.get('user_ratings_total', 0)}")
                                    print(f"   ✅ 获取到评价数: {len(reviews)}")
                                    
                                    if reviews:
                                        print(f"\n📋 评价示例:")
                                        for i, review in enumerate(reviews[:2], 1):
                                            print(f"   {i}. {review.get('author_name', 'Anonymous')} - {'⭐' * review.get('rating', 0)}")
                                            print(f"      {review.get('text', '')[:100]}...")
                                else:
                                    print(f"   ❌ 获取详细信息失败: {details_status}")
                            else:
                                print(f"   ❌ 获取详细信息HTTP错误: {details_response.status_code}")
                    else:
                        print(f"   ⚠️  没有找到地点")
                else:
                    print(f"   ❌ API错误: {status}")
                    if "error_message" in data:
                        print(f"   错误信息: {data['error_message']}")
            else:
                print(f"   ❌ HTTP错误: {response.status_code}")
                print(f"   响应: {response.text}")
                
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")

if __name__ == "__main__":
    asyncio.run(check_production_places_api())
