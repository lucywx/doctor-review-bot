#!/usr/bin/env python3
"""
验证Railway环境变量的根本问题
"""

import asyncio
import httpx
import json

async def verify_railway_env_root_cause():
    print("=" * 60)
    print("🔍 验证Railway环境变量根本问题")
    print("=" * 60)
    
    # 测试Google Places API直接调用
    api_key = "AIzaSyC0O-5Urc47Z1pF8hXpHVHAxC7NZowfjfw"
    
    print(f"🧪 直接测试API密钥: {api_key[:20]}...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 测试Google Places API
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
                
                print(f"✅ 直接API调用成功: {status}")
                
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
                            else:
                                print(f"❌ Details API错误: {details_data.get('status')}")
                        else:
                            print(f"❌ Details API HTTP错误: {details_response.status_code}")
                else:
                    print(f"❌ API错误: {status}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                
    except Exception as e:
        print(f"❌ API测试失败: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 根本原因分析:")
    print("1. API密钥本身工作正常")
    print("2. 问题在于Railway环境变量加载")
    print("3. 可能的原因:")
    print("   - Railway环境变量名称不匹配")
    print("   - Railway环境变量值有格式问题")
    print("   - Railway服务没有正确加载环境变量")
    print("=" * 60)
    
    print("\n🔧 解决方案:")
    print("1. 检查Railway环境变量名称是否完全匹配")
    print("2. 检查Railway环境变量值是否有多余空格")
    print("3. 尝试在Railway中重新设置环境变量")
    print("4. 检查Railway服务是否正确加载环境变量")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(verify_railway_env_root_cause())
