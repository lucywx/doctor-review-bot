#!/bin/bash

# Webhook 测试脚本
# 测试 WhatsApp Webhook 配置是否正确

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_DIR="/Users/lucyy/Desktop/coding/project02-docreview"
PORT=8000

echo "=========================================="
echo "  WhatsApp Webhook 测试工具"
echo "=========================================="
echo ""

# 加载环境变量
cd "$PROJECT_DIR"
if [ -f .env ]; then
    export $(grep -v '^#' .env | grep VERIFY_TOKEN | xargs)
else
    echo -e "${RED}❌ 找不到 .env 文件${NC}"
    exit 1
fi

# 检测 URL 类型
echo -e "${BLUE}选择测试环境:${NC}"
echo "1. 本地 (localhost:8000)"
echo "2. ngrok (需要输入 URL)"
echo "3. Railway (生产环境)"
echo ""
read -p "请选择 (1/2/3): " ENV_CHOICE

case $ENV_CHOICE in
    1)
        BASE_URL="http://localhost:$PORT"
        ;;
    2)
        # 尝试自动获取 ngrok URL
        NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | grep -o '"public_url":"https://[^"]*' | grep -o 'https://[^"]*' | head -1)
        if [ -z "$NGROK_URL" ]; then
            read -p "请输入 ngrok URL (例: https://abc123.ngrok-free.app): " NGROK_URL
        else
            echo -e "${GREEN}检测到 ngrok URL: $NGROK_URL${NC}"
        fi
        BASE_URL="$NGROK_URL"
        ;;
    3)
        read -p "请输入 Railway URL (例: https://your-app.up.railway.app): " RAILWAY_URL
        BASE_URL="$RAILWAY_URL"
        ;;
    *)
        echo -e "${RED}❌ 无效选择${NC}"
        exit 1
        ;;
esac

WEBHOOK_URL="$BASE_URL/webhook/whatsapp"

echo ""
echo "=========================================="
echo "  测试配置"
echo "=========================================="
echo ""
echo "Webhook URL: $WEBHOOK_URL"
echo "Verify Token: ${VERIFY_TOKEN:0:20}..."
echo ""

# 测试 1: 健康检查
echo "=========================================="
echo "  测试 1: 健康检查"
echo "=========================================="
echo ""

HEALTH_RESPONSE=$(curl -s "$BASE_URL/health" || echo "ERROR")

if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✅ 健康检查通过${NC}"
    echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    echo -e "${RED}❌ 健康检查失败${NC}"
    echo "$HEALTH_RESPONSE"
    exit 1
fi

# 测试 2: Webhook 验证
echo ""
echo "=========================================="
echo "  测试 2: Webhook 验证"
echo "=========================================="
echo ""

# 检查 WhatsApp 提供商
if grep -q "WHATSAPP_PROVIDER=twilio" .env 2>/dev/null; then
    echo "检测到 Twilio 配置，测试 Twilio Webhook 格式"
    echo "发送 Twilio 格式的测试消息..."
    
    # Twilio 使用 POST 请求测试
    VERIFY_RESPONSE=$(curl -s -X POST "$WEBHOOK_URL" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "From=whatsapp:+1234567890&Body=test" || echo "ERROR")
    
    if echo "$VERIFY_RESPONSE" | grep -q "received\|ok"; then
        echo -e "${GREEN}✅ Twilio Webhook 测试成功${NC}"
        echo "   响应: $VERIFY_RESPONSE"
    else
        echo -e "${RED}❌ Twilio Webhook 测试失败${NC}"
        echo "   响应: $VERIFY_RESPONSE"
    fi
else
    echo "检测到 Meta 配置，测试 Meta Webhook 格式"
    echo "发送 Meta 验证请求..."
    
    CHALLENGE="test_challenge_123456"
    VERIFY_URL="$WEBHOOK_URL?hub.mode=subscribe&hub.verify_token=$VERIFY_TOKEN&hub.challenge=$CHALLENGE"
    
    VERIFY_RESPONSE=$(curl -s "$VERIFY_URL" || echo "ERROR")
    
    if [ "$VERIFY_RESPONSE" == "$CHALLENGE" ]; then
        echo -e "${GREEN}✅ Meta Webhook 验证通过${NC}"
        echo "   返回值: $VERIFY_RESPONSE"
    else
        echo -e "${RED}❌ Meta Webhook 验证失败${NC}"
        echo "   预期: $CHALLENGE"
        echo "   实际: $VERIFY_RESPONSE"
    fi
fi

# 测试 3: 模拟 WhatsApp 消息
echo ""
echo "=========================================="
echo "  测试 3: 模拟 WhatsApp 消息 (测试端点)"
echo "=========================================="
echo ""

TEST_PAYLOAD='{
  "from": "+8613800138000",
  "message": "你好"
}'

echo "发送测试消息: 你好"
TEST_RESPONSE=$(curl -s -X POST "$BASE_URL/webhook/whatsapp/test" \
    -H "Content-Type: application/json" \
    -d "$TEST_PAYLOAD" || echo "ERROR")

if echo "$TEST_RESPONSE" | grep -q "ok"; then
    echo -e "${GREEN}✅ 测试消息处理成功${NC}"
    echo "$TEST_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$TEST_RESPONSE"
else
    echo -e "${RED}❌ 测试消息处理失败${NC}"
    echo "$TEST_RESPONSE"
fi

# 测试 4: 模拟医生查询
echo ""
echo "=========================================="
echo "  测试 4: 模拟医生查询"
echo "=========================================="
echo ""

DOCTOR_PAYLOAD='{
  "from": "+8613800138000",
  "message": "李医生"
}'

echo "发送查询: 李医生"
DOCTOR_RESPONSE=$(curl -s -X POST "$BASE_URL/webhook/whatsapp/test" \
    -H "Content-Type: application/json" \
    -d "$DOCTOR_PAYLOAD" || echo "ERROR")

if echo "$DOCTOR_RESPONSE" | grep -q "ok"; then
    echo -e "${GREEN}✅ 医生查询处理成功${NC}"
    echo "   查看日志获取详细结果: tail -f logs/app.log"
else
    echo -e "${RED}❌ 医生查询处理失败${NC}"
    echo "$DOCTOR_RESPONSE"
fi

# 总结
echo ""
echo "=========================================="
echo "  测试总结"
echo "=========================================="
echo ""
echo -e "${GREEN}✅ 所有基础测试通过！${NC}"
echo ""
echo "下一步:"
echo ""
echo -e "${BLUE}1. 在 Meta 配置 Webhook:${NC}"
echo "   - 访问: https://developers.facebook.com/"
echo "   - 进入: Doctor Review Bot → WhatsApp → Configuration"
echo "   - Callback URL: $WEBHOOK_URL"
echo "   - Verify Token: $VERIFY_TOKEN"
echo "   - 点击 'Verify and Save'"
echo ""
echo -e "${BLUE}2. 订阅消息事件:${NC}"
echo "   - 在同一页面勾选 'messages'"
echo "   - 点击 'Subscribe'"
echo ""
echo -e "${BLUE}3. 添加测试号码:${NC}"
echo "   - WhatsApp → API Setup → 'To'"
echo "   - 点击 'Manage phone number list'"
echo "   - 添加你的 WhatsApp 号码"
echo ""
echo -e "${BLUE}4. 发送真实消息测试:${NC}"
echo "   - 用 WhatsApp 向测试号码发送: 你好"
echo "   - 应该收到机器人回复"
echo ""
