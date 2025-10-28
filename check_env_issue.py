#!/usr/bin/env python3
"""
检查Railway环境变量读取问题
"""

import os
import sys
sys.path.append('/Users/lucyy/Desktop/coding/project02-docreview')

from src.config import settings

print("=" * 60)
print("🔍 检查Railway环境变量读取")
print("=" * 60)

print(f"\n📋 环境变量检查:")
print(f"GOOGLE_PLACES_API_KEY (os.environ): {os.environ.get('GOOGLE_PLACES_API_KEY', 'NOT_SET')}")
print(f"GOOGLE_PLACES_API_KEY (settings): {settings.google_places_api_key}")

print(f"\n🔧 Settings配置:")
print(f"env_file: {settings.model_config.get('env_file')}")
print(f"case_sensitive: {settings.model_config.get('case_sensitive')}")

print(f"\n📁 .env文件内容:")
try:
    with open('/Users/lucyy/Desktop/coding/project02-docreview/.env', 'r') as f:
        content = f.read()
        if 'GOOGLE_PLACES_API_KEY' in content:
            print("✅ .env文件包含GOOGLE_PLACES_API_KEY")
        else:
            print("❌ .env文件不包含GOOGLE_PLACES_API_KEY")
except Exception as e:
    print(f"❌ 无法读取.env文件: {e}")

print("\n" + "=" * 60)
print("🎯 问题分析:")
print("1. Railway环境变量可能被.env文件覆盖")
print("2. 或者Railway环境变量没有正确设置")
print("3. 需要检查Railway Dashboard中的变量设置")
print("=" * 60)
