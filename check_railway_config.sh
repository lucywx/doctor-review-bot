#!/bin/bash

echo "=================================="
echo "Railway 配置检查脚本"
echo "=================================="
echo ""

# 检查健康状态
echo "1️⃣ 检查应用健康状态..."
curl -s "https://doctor-review-bot-production.up.railway.app/health" | python3 -m json.tool
echo ""

# 检查最新部署
echo "2️⃣ 检查本地 Git 状态..."
CURRENT_COMMIT=$(git rev-parse --short HEAD)
echo "   本地 commit: $CURRENT_COMMIT"
echo ""

# 提示用户检查 Railway
echo "3️⃣ 请在 Railway 检查以下内容："
echo ""
echo "   访问: https://railway.app/"
echo "   进入项目: doctor-review-bot"
echo ""
echo "   ✅ 检查 Deployments 选项卡："
echo "      - 最新部署的 commit 应该是: $CURRENT_COMMIT"
echo "      - 状态应该是: SUCCESS (绿色)"
echo "      - 点击查看日志，搜索错误关键词"
echo ""
echo "   ✅ 检查 Variables 选项卡："
echo "      必须有这两个变量："
echo "      - GOOGLE_SEARCH_API_KEY (39 字符)"
echo "      - GOOGLE_SEARCH_ENGINE_ID (451baeb0bffe64a5e)"
echo ""
echo "   ✅ 查看日志中的错误："
echo "      - 点击最新的 Deployment"
echo "      - 点击 'View Logs'"
echo "      - 搜索: 'Error', 'Exception', 'Google'"
echo "      - 将错误信息复制给我"
echo ""
echo "=================================="
echo ""
echo "📋 需要添加的环境变量："
echo ""
echo "GOOGLE_SEARCH_API_KEY=AIzaSyC0O-5Urc47Z1pF8hXpHVHAxC7NZowfjfw"
echo "GOOGLE_SEARCH_ENGINE_ID=451baeb0bffe64a5e"
echo ""
echo "=================================="
