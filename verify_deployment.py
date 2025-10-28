#!/usr/bin/env python3
"""
验证Railway部署后的Google Places API功能
"""

import asyncio
import httpx
import json
import time

async def verify_deployment():
    print("=" * 60)
    print("🔍 验证Railway部署后的Google Places API功能")
    print("=" * 60)
    
    base_url = "https://doctor-review-bot-production.up.railway.app"
    
    # 等待服务重启
    print("⏳ 等待服务重启...")
    await asyncio.sleep(10)
    
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
    
    # 测试WhatsApp webhook
    print("\n📱 测试WhatsApp webhook搜索...")
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
                
                # 检查是否包含评价信息
                if "reviews" in str(result) or "Google Maps" in str(result):
                    print("   ✅ 搜索功能正常工作！")
                else:
                    print("   ⚠️  搜索功能可能还有问题")
            else:
                print(f"   ❌ 错误响应: {response.text}")
                
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    print("\n" + "=" * 60)
    print("📋 下一步:")
    print("1. 如果环境变量已设置，等待2-3分钟让Railway重新部署")
    print("2. 用您的真实WhatsApp号码测试搜索")
    print("3. 如果还有问题，请检查Railway日志")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(verify_deployment())
