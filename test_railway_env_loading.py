#!/usr/bin/env python3
"""
测试Railway环境变量加载
"""

import asyncio
import httpx
import json

async def test_railway_env_loading():
    print("=" * 60)
    print("🔍 测试Railway环境变量加载")
    print("=" * 60)
    
    # 创建一个简单的测试请求来检查环境变量
    base_url = "https://doctor-review-bot-production.up.railway.app"
    
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
    
    # 测试搜索功能并观察日志
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
    print("📋 关键检查点:")
    print("1. 检查Railway日志中是否有: 'Google Places API client initialized'")
    print("2. 检查Railway日志中是否有: '🗺️ Fetching Google Maps reviews via Places API...'")
    print("3. 如果没有上述日志，说明环境变量未正确设置")
    print("4. 如果有日志但显示 'not configured'，说明环境变量值为空或'not_required'")
    print("=" * 60)
    
    print("\n🔧 解决步骤:")
    print("1. 访问: https://railway.app/dashboard")
    print("2. 进入项目: doctor-review-bot")
    print("3. 点击: Variables 选项卡")
    print("4. 确认 GOOGLE_PLACES_API_KEY 存在且值为: AIzaSyC0O-5Urc47Z1pF8hXpHVHAxC7NZowfjfw")
    print("5. 如果没有，添加这个环境变量")
    print("6. 等待2-3分钟让Railway重新部署")
    print("7. 重新测试搜索功能")

if __name__ == "__main__":
    asyncio.run(test_railway_env_loading())
