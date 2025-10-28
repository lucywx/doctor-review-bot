#!/usr/bin/env python3
"""
测试修复后的环境变量加载
"""

import asyncio
import httpx
import json

async def test_fix():
    print("=" * 60)
    print("🔍 测试修复后的环境变量加载")
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
                print(f"GOOGLE_PLACES_API_KEY: {data.get('GOOGLE_PLACES_API_KEY')}")
                print(f"GOOGLE_SEARCH_API_KEY: {data.get('GOOGLE_SEARCH_API_KEY')}")
                
                if data.get('GOOGLE_PLACES_API_KEY'):
                    print("✅ 修复成功！GOOGLE_PLACES_API_KEY已正确加载")
                else:
                    print("❌ 修复未生效，GOOGLE_PLACES_API_KEY仍为null")
            else:
                print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 如果GOOGLE_PLACES_API_KEY不为null，说明修复成功")
    print("🎯 如果仍为null，可能需要手动重启Railway服务")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_fix())
