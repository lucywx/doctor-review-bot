#!/usr/bin/env python3
"""
详细诊断Railway环境变量问题
"""

import asyncio
import httpx
import json
import os

async def diagnose_railway_env():
    print("=" * 60)
    print("🔍 详细诊断Railway环境变量问题")
    print("=" * 60)
    
    # 检查本地环境变量
    print("\n📋 本地环境变量检查:")
    print("-" * 40)
    
    local_vars = [
        "GOOGLE_PLACES_API_KEY",
        "GOOGLE_SEARCH_API_KEY", 
        "GOOGLE_SEARCH_ENGINE_ID",
        "OPENAI_API_KEY"
    ]
    
    for var in local_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:20]}...")
        else:
            print(f"❌ {var}: 未设置")
    
    # 测试生产环境配置
    print("\n🌐 测试生产环境配置:")
    print("-" * 40)
    
    base_url = "https://doctor-review-bot-production.up.railway.app"
    
    # 创建一个测试端点来检查环境变量
    test_data = {
        "action": "check_env",
        "message": "Dr Paul Ng Hock Oon"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/webhook/whatsapp/test",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"响应: {json.dumps(result, indent=2)}")
            else:
                print(f"错误响应: {response.text}")
                
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 直接测试Google Places API
    print("\n🧪 直接测试Google Places API:")
    print("-" * 40)
    
    api_key = "AIzaSyC0O-5Urc47Z1pF8hXpHVHAxC7NZowfjfw"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 测试Text Search
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                "query": "Dr Paul Ng Hock Oon Malaysia",
                "key": api_key,
                "language": "en"
            }
            
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "UNKNOWN")
                
                print(f"✅ API状态: {status}")
                
                if status == "OK":
                    results = data.get("results", [])
                    print(f"✅ 找到 {len(results)} 个地点")
                    
                    if results:
                        place = results[0]
                        place_id = place.get("place_id")
                        
                        # 测试Details API
                        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                        details_params = {
                            "place_id": place_id,
                            "fields": "name,rating,user_ratings_total,reviews",
                            "key": api_key,
                            "language": "en"
                        }
                        
                        details_response = await client.get(details_url, params=details_params)
                        
                        if details_response.status_code == 200:
                            details_data = details_response.json()
                            if details_data.get("status") == "OK":
                                result = details_data.get("result", {})
                                reviews = result.get("reviews", [])
                                print(f"✅ 获取到 {len(reviews)} 条评价")
                                print(f"✅ 总评价数: {result.get('user_ratings_total', 0)}")
                            else:
                                print(f"❌ Details API错误: {details_data.get('status')}")
                        else:
                            print(f"❌ Details API HTTP错误: {details_response.status_code}")
                else:
                    print(f"❌ API错误: {status}")
                    if "error_message" in data:
                        print(f"   错误信息: {data['error_message']}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                
    except Exception as e:
        print(f"❌ API测试失败: {e}")
    
    print("\n" + "=" * 60)
    print("🔧 可能的解决方案:")
    print("1. 检查Railway Variables中GOOGLE_PLACES_API_KEY是否正确设置")
    print("2. 确保变量名完全匹配: GOOGLE_PLACES_API_KEY")
    print("3. 等待更长时间让Railway重新部署")
    print("4. 检查Railway日志中是否有环境变量加载错误")
    print("5. 尝试手动重启Railway服务")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(diagnose_railway_env())
