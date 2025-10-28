#!/usr/bin/env python3
"""
检查Railway环境变量配置
通过创建一个简单的测试端点来检查环境变量
"""

import asyncio
import httpx
import json

async def check_railway_env_vars():
    print("=" * 60)
    print("🔍 检查Railway环境变量配置")
    print("=" * 60)
    
    base_url = "https://doctor-review-bot-production.up.railway.app"
    
    # 测试不同的端点
    endpoints = [
        "/health",
        "/docs", 
        "/"
    ]
    
    for endpoint in endpoints:
        print(f"\n📡 测试端点: {endpoint}")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{base_url}{endpoint}")
                print(f"   状态码: {response.status_code}")
                
                if response.status_code == 200:
                    if endpoint == "/health":
                        data = response.json()
                        print(f"   ✅ 健康状态: {data.get('status', 'unknown')}")
                        print(f"   ✅ 环境: {data.get('environment', 'unknown')}")
                        print(f"   ✅ 数据库: {data.get('database', 'unknown')}")
                else:
                    print(f"   ❌ 错误: {response.text[:100]}...")
                    
        except Exception as e:
            print(f"   ❌ 请求失败: {e}")
    
    # 检查Railway部署状态
    print(f"\n🚀 检查Railway部署状态:")
    print("请访问: https://railway.app/dashboard")
    print("进入项目: doctor-review-bot")
    print("检查:")
    print("1. Deployments选项卡 - 最新部署是否成功")
    print("2. Variables选项卡 - GOOGLE_PLACES_API_KEY是否存在")
    print("3. Logs选项卡 - 查看是否有环境变量相关错误")
    
    print(f"\n🔧 手动检查步骤:")
    print("1. 确认GOOGLE_PLACES_API_KEY变量名完全正确")
    print("2. 确认变量值: AIzaSyC0O-5Urc47Z1pF8hXpHVHAxC7NZowfjfw")
    print("3. 尝试删除并重新添加环境变量")
    print("4. 手动重启Railway服务")
    
    print(f"\n📋 如果问题仍然存在:")
    print("1. 检查Railway日志中的错误信息")
    print("2. 确认代码中环境变量的读取方式")
    print("3. 可能需要重新部署整个项目")

if __name__ == "__main__":
    asyncio.run(check_railway_env_vars())
