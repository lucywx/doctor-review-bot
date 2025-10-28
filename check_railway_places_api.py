#!/usr/bin/env python3
"""
检查Railway是否真的加载了Google Places API环境变量
通过分析日志来判断
"""

import asyncio
import httpx
import json
import time

async def check_railway_places_api():
    print("=" * 60)
    print("🔍 检查Railway Google Places API环境变量加载")
    print("=" * 60)
    
    base_url = "https://doctor-review-bot-production.up.railway.app"
    
    # 测试搜索功能
    print("\n📱 测试搜索功能...")
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
    print("3. 如果没有上述日志，说明环境变量虽然设置了，但Railway服务没有重新加载")
    print("=" * 60)
    
    print("\n🔧 可能的解决方案:")
    print("1. 手动重启Railway服务:")
    print("   - 访问: https://railway.app/dashboard")
    print("   - 进入项目: doctor-review-bot")
    print("   - 点击: Settings 选项卡")
    print("   - 找到: Restart Service 按钮")
    print("   - 点击重启服务")
    print("")
    print("2. 或者等待更长时间让Railway自动重新部署")
    print("")
    print("3. 检查Railway日志:")
    print("   - 点击: Logs 选项卡")
    print("   - 查看是否有环境变量加载错误")
    print("   - 查看是否有Google Places API初始化日志")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(check_railway_places_api())
