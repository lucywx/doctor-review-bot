#!/usr/bin/env python3
"""
验证Railway环境变量设置
"""

import asyncio
import httpx
import json
import time

async def verify_railway_env():
    print("=" * 60)
    print("🔍 验证Railway环境变量设置")
    print("=" * 60)
    
    base_url = "https://doctor-review-bot-production.up.railway.app"
    
    # 等待Railway重新部署
    print("⏳ 等待Railway重新部署...")
    await asyncio.sleep(30)
    
    # 测试健康检查
    print("\n🏥 测试健康检查...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/health")
            
            if response.status_code == 200:
                health = response.json()
                print(f"   ✅ 健康状态: {health['status']}")
                print(f"   ✅ 环境: {health['environment']}")
            else:
                print(f"   ❌ 健康检查失败: {response.status_code}")
                return
                
    except Exception as e:
        print(f"   ❌ 健康检查失败: {e}")
        return
    
    # 测试搜索功能
    print("\n🔍 测试搜索功能...")
    test_data = {
        "message": "Dr Paul Ng Hock Oon",
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
    print("1. 确保GOOGLE_PLACES_API_KEY已添加到Railway Variables")
    print("2. 等待2-3分钟让Railway重新部署")
    print("3. 用真实WhatsApp号码测试")
    print("4. 查看Railway日志确认Google Places API被调用")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(verify_railway_env())
