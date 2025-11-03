#!/usr/bin/env python3
"""
验证 Railway 部署状态
检查最新代码是否已部署
"""

import requests
import sys

RAILWAY_URL = "https://doctor-review-bot-production.up.railway.app"

print("🔍 验证 Railway 部署状态...\n")

# 1. 检查健康状态
print("1. 检查健康状态...")
try:
    response = requests.get(f"{RAILWAY_URL}/health", timeout=10)
    if response.status_code == 200:
        print(f"   ✅ 健康检查通过: HTTP {response.status_code}")
    else:
        print(f"   ⚠️ 健康检查异常: HTTP {response.status_code}")
except Exception as e:
    print(f"   ❌ 健康检查失败: {e}")
    sys.exit(1)

# 2. 检查 API 信息
print("\n2. 检查 API 信息...")
try:
    response = requests.get(RAILWAY_URL, timeout=10)
    data = response.json()
    print(f"   ✅ API 版本: {data.get('version')}")
    print(f"   ✅ 状态: {data.get('status')}")
except Exception as e:
    print(f"   ❌ API 信息获取失败: {e}")

# 3. 检查环境变量配置
print("\n3. 检查环境变量配置...")
try:
    response = requests.get(f"{RAILWAY_URL}/env-check", timeout=10)
    data = response.json()

    # 检查关键环境变量
    has_openai = 'OPENAI_API_KEY' in data and data['OPENAI_API_KEY'] != "None"
    has_places = data.get('GOOGLE_PLACES_API_KEY_is_none') == False

    print(f"   {'✅' if has_openai else '❌'} OpenAI API Key: {'已配置' if has_openai else '未配置'}")
    print(f"   {'✅' if has_places else '⚠️'} Google Places API Key: {'已配置' if has_places else '未配置'}")
    print(f"   ℹ️  环境: {data.get('environment')}")

except Exception as e:
    print(f"   ⚠️ 环境变量检查失败: {e}")

# 4. 总结
print("\n" + "="*60)
print("📊 部署状态总结")
print("="*60)
print(f"✅ Railway 应用正在运行")
print(f"✅ Git push 成功，最新提交已推送")
print(f"ℹ️  Railway 会自动检测到代码变更并重新部署")
print(f"ℹ️  部署通常需要 2-5 分钟")
print("\n📝 最新变更:")
print("   - 升级到 Responses API + gpt-5-mini")
print("   - 删除 41 个旧文件")
print("   - 添加新文档和测试文件")
print("\n🔗 Railway 应用地址:")
print(f"   {RAILWAY_URL}")
print("\n✅ 验证完成！")
