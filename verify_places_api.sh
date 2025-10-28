#!/bin/bash

echo "================================================"
echo "验证 Places API 是否已启用"
echo "================================================"
echo ""

echo "等待Railway部署完成（30秒）..."
for i in {30..1}; do
    echo -ne "\r倒计时: $i 秒... "
    sleep 1
done
echo ""
echo ""

echo "检查 /env-check endpoint..."
echo ""

RESPONSE=$(curl -s "https://doctor-review-bot-production.up.railway.app/env-check")

echo "$RESPONSE" | python3 -m json.tool
echo ""
echo "================================================"

# 提取关键信息
RAW_ENV=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('GOOGLE_PLACES_API_KEY_raw_env', 'null'))" 2>/dev/null)
ENABLED=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('places_client_enabled', False))" 2>/dev/null)

echo "关键指标："
echo "  - GOOGLE_PLACES_API_KEY_raw_env: $RAW_ENV"
echo "  - places_client_enabled: $ENABLED"
echo ""

if [ "$ENABLED" = "True" ]; then
    echo "✅✅✅ Places API 已成功启用！"
    echo ""
    echo "现在你可以搜索医生，系统会自动从Google Maps获取评价了！"
else
    echo "❌ Places API 仍未启用"
    echo ""
    if [ "$RAW_ENV" = "null" ] || [ "$RAW_ENV" = "None" ]; then
        echo "问题：环境变量仍然是 null"
        echo ""
        echo "可能的原因："
        echo "1. Railway还在部署中，请再等待1-2分钟"
        echo "2. 没有点击 'Deploy' 按钮应用更改"
        echo "3. 部署失败，请检查 Railway Logs"
    else
        echo "环境变量已加载: ${RAW_ENV:0:20}..."
        echo "但 Places API client 仍未启用，请检查日志"
    fi
fi

echo ""
echo "================================================"
