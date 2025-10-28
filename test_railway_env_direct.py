#!/usr/bin/env python3
"""
直接测试Railway环境变量
"""

import asyncio
import httpx
import json

async def test_railway_env():
    print("=" * 60)
    print("🔍 直接测试Railway环境变量")
    print("=" * 60)
    
    base_url = "https://doctor-review-bot-production.up.railway.app"
    
    # 测试环境变量端点
    print("\n📱 测试环境变量端点...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{base_url}/env-check")
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"GOOGLE_PLACES_API_KEY: {data.get('GOOGLE_PLACES_API_KEY', 'NOT_FOUND')}")
                print(f"GOOGLE_SEARCH_API_KEY: {data.get('GOOGLE_SEARCH_API_KEY', 'NOT_FOUND')}")
                print(f"GOOGLE_SEARCH_ENGINE_ID: {data.get('GOOGLE_SEARCH_ENGINE_ID', 'NOT_FOUND')}")
            else:
                print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 如果环境变量显示为None或NOT_FOUND，说明Railway没有正确设置")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_railway_env())