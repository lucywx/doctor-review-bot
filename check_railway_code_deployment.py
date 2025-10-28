#!/usr/bin/env python3
"""
检查Railway是否真的加载了Google Places API代码
"""

import asyncio
import httpx
import json

async def check_railway_code_deployment():
    print("=" * 60)
    print("🔍 检查Railway代码部署情况")
    print("=" * 60)
    
    base_url = "https://doctor-review-bot-production.up.railway.app"
    
    # 检查服务启动日志
    print("\n🚀 检查服务启动日志...")
    print("请检查Railway日志中是否有以下信息:")
    print("1. 'Google Places API client initialized'")
    print("2. 'Google Places API key not configured'")
    print("3. 任何关于Google Places API的日志")
    
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
    print("🔍 可能的问题:")
    print("1. Railway没有部署最新的代码")
    print("2. Railway环境变量没有正确加载")
    print("3. 代码中的环境变量读取有问题")
    print("4. Railway服务配置有问题")
    print("=" * 60)
    
    print("\n🔧 调试步骤:")
    print("1. 检查Railway Deployments选项卡:")
    print("   - 最新部署的commit是否匹配: 97c1ce4")
    print("   - 部署状态是否为SUCCESS")
    print("")
    print("2. 检查Railway Logs选项卡:")
    print("   - 查看服务启动日志")
    print("   - 查找Google Places API相关日志")
    print("")
    print("3. 检查Railway Variables选项卡:")
    print("   - 确认GOOGLE_PLACES_API_KEY存在")
    print("   - 确认值为: AIzaSyC0O-5Urc47Z1pF8hXpHVHAxC7NZowfjfw")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(check_railway_code_deployment())
