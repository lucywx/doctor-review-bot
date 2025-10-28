#!/usr/bin/env python3
"""
测试生产环境搜索功能
模拟真实的WhatsApp请求
"""

import asyncio
import httpx
import json

async def test_production_search():
    print("=" * 60)
    print("🔍 测试生产环境搜索功能")
    print("=" * 60)
    
    # 测试搜索API端点
    base_url = "https://doctor-review-bot-production.up.railway.app"
    
    # 模拟WhatsApp webhook请求
    test_data = {
        "message": "Dr Paul Ng Hock Oon",
        "from": "+60123456789"  # 使用马来西亚格式
    }
    
    print(f"📱 测试WhatsApp webhook...")
    print(f"   消息: {test_data['message']}")
    print(f"   发送者: {test_data['from']}")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
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
    
    # 测试健康检查
    print(f"\n🏥 测试健康检查...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/health")
            
            if response.status_code == 200:
                health = response.json()
                print(f"   ✅ 健康状态: {health['status']}")
                print(f"   ✅ 环境: {health['environment']}")
                print(f"   ✅ 数据库: {health['database']}")
            else:
                print(f"   ❌ 健康检查失败: {response.status_code}")
                
    except Exception as e:
        print(f"   ❌ 健康检查失败: {e}")
    
    # 测试API文档
    print(f"\n📚 测试API文档...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/docs")
            
            if response.status_code == 200:
                print(f"   ✅ API文档可访问")
            else:
                print(f"   ❌ API文档不可访问: {response.status_code}")
                
    except Exception as e:
        print(f"   ❌ API文档测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_production_search())
