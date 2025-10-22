#!/usr/bin/env python3
"""
诊断Railway崩溃问题的脚本
检查所有必需的环境变量和依赖
"""

import os
import sys
from src.config import Settings

def check_environment_variables():
    """检查所有必需的环境变量"""
    print("🔍 检查环境变量...")
    
    required_vars = [
        "DATABASE_URL",
        "TWILIO_ACCOUNT_SID", 
        "TWILIO_AUTH_TOKEN",
        "TWILIO_WHATSAPP_NUMBER",
        "VERIFY_TOKEN",
        "OPENAI_API_KEY",
        "ADMIN_PHONE_NUMBER"
    ]
    
    optional_vars = [
        "GOOGLE_SEARCH_API_KEY",
        "GOOGLE_SEARCH_ENGINE_ID",
        "OPENAI_MODEL",
        "ENVIRONMENT",
        "DEBUG"
    ]
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
        else:
            print(f"✅ {var}: 已设置")
    
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
        else:
            print(f"✅ {var}: 已设置")
    
    if missing_required:
        print(f"\n❌ 缺少必需的环境变量:")
        for var in missing_required:
            print(f"   - {var}")
    
    if missing_optional:
        print(f"\n⚠️  缺少可选的环境变量:")
        for var in missing_optional:
            print(f"   - {var}")
    
    return len(missing_required) == 0

def test_config_loading():
    """测试配置加载"""
    print("\n🔧 测试配置加载...")
    try:
        settings = Settings()
        print("✅ 配置加载成功")
        return True
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False

def test_database_connection():
    """测试数据库连接"""
    print("\n📊 测试数据库连接...")
    try:
        import asyncio
        from src.database import db
        
        async def test_db():
            await db.connect()
            print("✅ 数据库连接成功")
            await db.disconnect()
        
        asyncio.run(test_db())
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def main():
    print("🚀 Railway崩溃诊断工具")
    print("=" * 50)
    
    # 检查环境变量
    env_ok = check_environment_variables()
    
    # 测试配置加载
    config_ok = test_config_loading()
    
    # 测试数据库连接
    db_ok = test_database_connection()
    
    print("\n" + "=" * 50)
    print("📋 诊断结果:")
    
    if env_ok and config_ok and db_ok:
        print("✅ 所有检查通过！问题可能在其他地方")
    else:
        print("❌ 发现问题:")
        if not env_ok:
            print("   - 环境变量配置不完整")
        if not config_ok:
            print("   - 配置加载失败")
        if not db_ok:
            print("   - 数据库连接失败")
    
    print("\n💡 建议:")
    print("1. 检查Railway环境变量设置")
    print("2. 确保DATABASE_URL指向正确的PostgreSQL实例")
    print("3. 检查所有API密钥是否正确")

if __name__ == "__main__":
    main()
