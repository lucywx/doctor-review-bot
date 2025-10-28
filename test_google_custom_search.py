#!/usr/bin/env python3
"""
验证Google Custom Search API是否正常工作
"""

import asyncio
import httpx
import json

async def test_google_custom_search():
    print("=" * 60)
    print("🔍 验证Google Custom Search API")
    print("=" * 60)
    
    # 测试Railway中的Google Custom Search API
    base_url = "https://doctor-review-bot-production.up.railway.app"
    
    # 测试搜索功能
    print("\n📱 测试搜索功能...")
    test_data = {
        "message": "Dr Paul Ng Hock Oon",  # 使用一个没有缓存的医生
        "from": "+60123456789"
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print("   发送搜索请求...")
            response = await client.post(
                f"{base_url}/webhook/whatsapp/test",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ 响应: {json.dumps(result, indent=2)}")
            else:
                print(f"   ❌ 错误响应: {response.text}")
                
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    print("\n" + "=" * 60)
    print("📋 检查要点:")
    print("1. 查看Railway日志中是否有:")
    print("   - 'Google Custom Search API' 相关日志")
    print("   - 'Found X URLs from Google Search'")
    print("   - 'Using Google Custom Search to find reviews'")
    print("")
    print("2. 如果没有上述日志，说明Google Custom Search API没有工作")
    print("3. 如果只有缓存结果，说明Google Custom Search API没有工作")
    print("=" * 60)
    
    print("\n🔧 验证方法:")
    print("1. 用真实WhatsApp号码搜索一个没有缓存的医生")
    print("2. 查看Railway日志")
    print("3. 检查是否有Google Custom Search相关的日志")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_google_custom_search())
