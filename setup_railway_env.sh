#!/bin/bash

# 设置Railway环境变量脚本
# 确保Google Places API等关键变量正确设置

set -e

echo "=========================================="
echo "  设置Railway环境变量"
echo "=========================================="

# 从.env文件读取变量
if [ ! -f ".env" ]; then
    echo "❌ 找不到 .env 文件"
    exit 1
fi

# 加载环境变量
set -a
source .env
set +a

echo "正在设置环境变量..."

# 必需的Google Places API变量
if [ ! -z "$GOOGLE_PLACES_API_KEY" ] && [[ "$GOOGLE_PLACES_API_KEY" != your_* ]]; then
    echo "设置 GOOGLE_PLACES_API_KEY..."
    railway variables set "GOOGLE_PLACES_API_KEY=$GOOGLE_PLACES_API_KEY" || echo "设置失败"
else
    echo "⚠️  GOOGLE_PLACES_API_KEY 未配置"
fi

# Google Search API变量
if [ ! -z "$GOOGLE_SEARCH_API_KEY" ] && [[ "$GOOGLE_SEARCH_API_KEY" != your_* ]]; then
    echo "设置 GOOGLE_SEARCH_API_KEY..."
    railway variables set "GOOGLE_SEARCH_API_KEY=$GOOGLE_SEARCH_API_KEY" || echo "设置失败"
else
    echo "⚠️  GOOGLE_SEARCH_API_KEY 未配置"
fi

if [ ! -z "$GOOGLE_SEARCH_ENGINE_ID" ] && [[ "$GOOGLE_SEARCH_ENGINE_ID" != your_* ]]; then
    echo "设置 GOOGLE_SEARCH_ENGINE_ID..."
    railway variables set "GOOGLE_SEARCH_ENGINE_ID=$GOOGLE_SEARCH_ENGINE_ID" || echo "设置失败"
else
    echo "⚠️  GOOGLE_SEARCH_ENGINE_ID 未配置"
fi

# OpenAI API变量
if [ ! -z "$OPENAI_API_KEY" ] && [[ "$OPENAI_API_KEY" != your_* ]]; then
    echo "设置 OPENAI_API_KEY..."
    railway variables set "OPENAI_API_KEY=$OPENAI_API_KEY" || echo "设置失败"
else
    echo "⚠️  OPENAI_API_KEY 未配置"
fi

# Twilio变量
if [ ! -z "$TWILIO_ACCOUNT_SID" ] && [[ "$TWILIO_ACCOUNT_SID" != your_* ]]; then
    echo "设置 TWILIO_ACCOUNT_SID..."
    railway variables set "TWILIO_ACCOUNT_SID=$TWILIO_ACCOUNT_SID" || echo "设置失败"
else
    echo "⚠️  TWILIO_ACCOUNT_SID 未配置"
fi

if [ ! -z "$TWILIO_AUTH_TOKEN" ] && [[ "$TWILIO_AUTH_TOKEN" != your_* ]]; then
    echo "设置 TWILIO_AUTH_TOKEN..."
    railway variables set "TWILIO_AUTH_TOKEN=$TWILIO_AUTH_TOKEN" || echo "设置失败"
else
    echo "⚠️  TWILIO_AUTH_TOKEN 未配置"
fi

if [ ! -z "$TWILIO_WHATSAPP_NUMBER" ] && [[ "$TWILIO_WHATSAPP_NUMBER" != your_* ]]; then
    echo "设置 TWILIO_WHATSAPP_NUMBER..."
    railway variables set "TWILIO_WHATSAPP_NUMBER=$TWILIO_WHATSAPP_NUMBER" || echo "设置失败"
else
    echo "⚠️  TWILIO_WHATSAPP_NUMBER 未配置"
fi

if [ ! -z "$VERIFY_TOKEN" ] && [[ "$VERIFY_TOKEN" != your_* ]]; then
    echo "设置 VERIFY_TOKEN..."
    railway variables set "VERIFY_TOKEN=$VERIFY_TOKEN" || echo "设置失败"
else
    echo "⚠️  VERIFY_TOKEN 未配置"
fi

# 数据库URL
echo "设置 DATABASE_URL..."
railway variables set 'DATABASE_URL=${{Postgres.DATABASE_URL}}' || echo "设置失败"

# 生产环境配置
echo "设置生产环境配置..."
railway variables set "ENVIRONMENT=production" || echo "设置失败"
railway variables set "DEBUG=false" || echo "设置失败"
railway variables set "LOG_LEVEL=INFO" || echo "设置失败"

echo ""
echo "✅ 环境变量设置完成"
echo ""
echo "请等待几分钟让Railway重新部署，然后测试服务"
