#!/usr/bin/env python3
"""
详细调试Railway环境变量问题
"""

import asyncio
import httpx
import json

async def debug_railway_env():
    print("=" * 60)
    print("🔍 详细调试Railway环境变量问题")
    print("=" * 60)
    
    base_url = "https://doctor-review-bot-production.up.railway.app"
    
    # 测试多个端点
    endpoints = [
        "/",
        "/health", 
        "/env-check"
    ]
    
    for endpoint in endpoints:
        print(f"\n📱 测试端点: {endpoint}")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{base_url}{endpoint}")
                print(f"   状态码: {response.status_code}")
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"   响应: {json.dumps(data, indent=2)}")
                    except:
                        print(f"   响应: {response.text}")
                else:
                    print(f"   错误: {response.text}")
        except Exception as e:
            print(f"   请求失败: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 如果/env-check返回404，说明代码还没有部署")
    print("🎯 如果/env-check返回200但GOOGLE_PLACES_API_KEY为null，说明Railway环境变量问题")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(debug_railway_env())