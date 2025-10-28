#!/usr/bin/env python3
"""
测试Pydantic Settings的环境变量优先级
"""

import os
import sys
sys.path.append('/Users/lucyy/Desktop/coding/project02-docreview')

# 设置环境变量
os.environ['GOOGLE_PLACES_API_KEY'] = 'test_env_var_value'

from src.config import settings

print("=" * 60)
print("🔍 测试Pydantic Settings环境变量优先级")
print("=" * 60)

print(f"\n📋 环境变量检查:")
print(f"os.environ['GOOGLE_PLACES_API_KEY']: {os.environ.get('GOOGLE_PLACES_API_KEY')}")
print(f"settings.google_places_api_key: {settings.google_places_api_key}")

print(f"\n🔧 Settings配置:")
print(f"env_file: {settings.model_config.get('env_file')}")
print(f"env_ignore_empty: {settings.model_config.get('env_ignore_empty')}")

print(f"\n📁 .env文件内容:")
try:
    with open('/Users/lucyy/Desktop/coding/project02-docreview/.env', 'r') as f:
        lines = f.readlines()
        for line in lines:
            if 'GOOGLE_PLACES_API_KEY' in line:
                print(f"找到: {line.strip()}")
                break
        else:
            print("❌ .env文件中没有找到GOOGLE_PLACES_API_KEY")
except Exception as e:
    print(f"❌ 无法读取.env文件: {e}")

print("\n" + "=" * 60)
print("🎯 分析:")
print("如果settings.google_places_api_key显示.env文件的值而不是环境变量值，")
print("说明.env文件优先级更高")
print("=" * 60)
