#!/bin/bash

# 使用你提供的API key设置到Railway

API_KEY="AIzaSyC0O-5Urc47Z1pF8hXpHVHAxC7NZowfjfw"

echo "================================================"
echo "设置 GOOGLE_PLACES_API_KEY 到 Railway"
echo "================================================"
echo ""
echo "API Key: ${API_KEY:0:25}..."
echo ""

# 方法1: 使用railway CLI
echo "正在设置环境变量..."
railway variables set GOOGLE_PLACES_API_KEY="$API_KEY"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Railway CLI 设置成功！"
    echo ""
    echo "等待20秒让Railway自动重新部署..."

    for i in {20..1}; do
        echo -ne "\r倒计时: $i 秒... "
        sleep 1
    done
    echo ""
    echo ""

    echo "验证设置是否生效..."
    echo ""

    RESPONSE=$(curl -s "https://doctor-review-bot-production.up.railway.app/env-check")

    echo "$RESPONSE" | python3 -m json.tool
    echo ""

    # 检查是否成功
    ENABLED=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('places_client_enabled', False))")

    if [ "$ENABLED" = "True" ]; then
        echo "✅✅✅ Places API 已成功启用！"
    else
        echo "❌ Places API 仍未启用，请查看上面的详细信息"
        echo ""
        echo "如果 GOOGLE_PLACES_API_KEY_raw_env 仍然是 null，请："
        echo "1. 访问 Railway Dashboard: https://railway.app/dashboard"
        echo "2. 选择 doctor-review-bot 项目"
        echo "3. 确认 Variables 中有 GOOGLE_PLACES_API_KEY"
        echo "4. 手动触发 Redeploy"
    fi
else
    echo ""
    echo "❌ Railway CLI 设置失败"
    echo ""
    echo "请手动设置："
    echo "1. 访问: https://railway.app/dashboard"
    echo "2. 选择项目: doctor-review-bot"
    echo "3. 选择正确的服务（可能有多个服务）"
    echo "4. 点击 Variables 标签"
    echo "5. 点击 'New Variable'"
    echo "6. 添加:"
    echo "   名称: GOOGLE_PLACES_API_KEY"
    echo "   值: $API_KEY"
    echo "7. 保存后会自动触发重新部署"
fi
