#!/bin/bash

echo "================================================"
echo "测试 GPT-4 过滤 Google Maps 评价"
echo "================================================"
echo ""

echo "等待 Railway 部署完成（30秒）..."
for i in {30..1}; do
    echo -ne "\r倒计时: $i 秒... "
    sleep 1
done
echo -e "\n"

echo "================================================"
echo "测试 1: 搜索 Dr. Nicholas Lim Lye Tak"
echo "================================================"
echo ""

# 清除缓存（如果有的话）
echo "Step 1: 发送搜索请求..."

# 使用 WhatsApp 发送测试（需要你的 WhatsApp 号）
# 或者直接调用 API endpoint

echo "正在通过生产环境搜索..."
echo ""

# 模拟搜索并查看日志
echo "请在 Railway Logs 中查看以下关键日志："
echo ""
echo "预期日志输出："
echo "  🗺️ Fetching Google Maps reviews via Places API..."
echo "  📍 Place: Columbia Asia Hospital Petaling Jaya (Total reviews: 5558)"
echo "  🔍 Found 5 raw Google Maps reviews"
echo "  🤖 Using GPT-4 to filter reviews about Dr. Nicholas Lim Lye Tak..."
echo "  ✅ GPT-4 filtered 5 → X reviews about Dr. Nicholas Lim Lye Tak"
echo ""
echo "或者："
echo "  ℹ️ No Google Maps reviews are actually about Dr. Nicholas Lim Lye Tak (filtered by GPT-4)"
echo ""

echo "================================================"
echo "如何验证："
echo "================================================"
echo ""
echo "方法1: 查看 Railway Logs"
echo "  1. 访问: https://railway.app/dashboard"
echo "  2. 选择 doctor-review-bot 项目"
echo "  3. 点击 Deployments"
echo "  4. 查看最新部署的 Logs"
echo ""
echo "方法2: 通过 WhatsApp 测试"
echo "  1. 发送消息到你的 WhatsApp bot: 'Dr. Nicholas Lim Lye Tak'"
echo "  2. 等待结果"
echo "  3. 检查返回的评价数量和来源"
echo ""
echo "方法3: 使用本地测试（如果有数据库访问）"
echo ""

echo "================================================"
echo "手动测试 Places API + GPT-4 过滤"
echo "================================================"
echo ""

# 测试 Places API 返回的5条评价
echo "获取 Places API 原始评价..."
echo ""

PLACE_ID="ChIJjR6RfF5JzDERv1dmkS2Bw8o"
API_KEY="AIzaSyC0O-5Urc47Z1pF8hXpHVHAxC7NZowfjfw"

REVIEWS=$(curl -s "https://maps.googleapis.com/maps/api/place/details/json?place_id=$PLACE_ID&fields=reviews&key=$API_KEY" | python3 -c "
import sys, json
data = json.load(sys.stdin)
reviews = data.get('result', {}).get('reviews', [])
for i, r in enumerate(reviews[:5], 1):
    print(f'Review {i}: {r[\"text\"][:100]}...')
")

echo "$REVIEWS"
echo ""

echo "================================================"
echo "GPT-4 应该能识别出："
echo "================================================"
echo ""
echo "✅ 哪些评价提到了 'Nicholas Lim' 或 'Dr. Lim'"
echo "❌ 哪些评价只提到了其他医生（如 Dr. Siva, Dr. Hyder）"
echo "❌ 哪些评价只是关于医院设施"
echo ""

echo "现在请通过 WhatsApp 发送 'Dr. Nicholas Lim Lye Tak' 来测试！"
echo ""
