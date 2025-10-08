#!/bin/bash

# Twilio WhatsApp API 配置脚本
# 用于配置 Twilio WhatsApp Business API 凭证

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="/Users/lucyy/Desktop/coding/project02-docreview"
cd "$PROJECT_ROOT"

echo -e "${BLUE}🚀 Twilio WhatsApp API 配置脚本${NC}"
echo "=================================="
echo ""

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ 错误: .env 文件不存在${NC}"
    echo "请先运行: cp .env.example .env"
    exit 1
fi

# 备份原配置
if [ -f ".env" ]; then
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    echo -e "${GREEN}✅ 已备份原配置到 .env.backup.$(date +%Y%m%d_%H%M%S)${NC}"
fi

echo ""
echo -e "${YELLOW}📋 需要从 Twilio Console 获取以下信息:${NC}"
echo "1. Account SID"
echo "2. Auth Token"
echo "3. WhatsApp 号码 (格式: +1234567890)"
echo ""
echo -e "${BLUE}获取步骤:${NC}"
echo "1. 访问 https://console.twilio.com/"
echo "2. 登录你的 Twilio 账号"
echo "3. 在 Dashboard 找到 Account SID 和 Auth Token"
echo "4. 在 Messaging > Try it out > Send a WhatsApp message 找到你的 WhatsApp 号码"
echo ""

# 从图片中获取的信息
TWILIO_ACCOUNT_SID="your_twilio_account_sid_here"
TWILIO_WHATSAPP_NUMBER="+1234567890"

echo -e "${GREEN}✅ 已从 Twilio 控制台获取信息:${NC}"
echo "Account SID: $TWILIO_ACCOUNT_SID"
echo "WhatsApp 号码: $TWILIO_WHATSAPP_NUMBER"
echo ""

# 获取 Twilio Auth Token
echo -e "${YELLOW}请输入 Twilio Auth Token (从 Twilio Console Dashboard 获取):${NC}"
read -s -p "Auth Token: " TWILIO_AUTH_TOKEN
echo ""

if [ -z "$TWILIO_AUTH_TOKEN" ]; then
    echo -e "${RED}❌ Auth Token 不能为空${NC}"
    exit 1
fi

# 获取 Verify Token
echo -e "${YELLOW}请输入 Webhook Verify Token (用于验证 webhook 请求):${NC}"
read -p "Verify Token (默认: twilio_verify_token_$(date +%Y%m%d)): " VERIFY_TOKEN

if [ -z "$VERIFY_TOKEN" ]; then
    VERIFY_TOKEN="twilio_verify_token_$(date +%Y%m%d)"
fi

echo ""
echo -e "${BLUE}📝 配置摘要:${NC}"
echo "Account SID: ${TWILIO_ACCOUNT_SID:0:8}..."
echo "Auth Token: ${TWILIO_AUTH_TOKEN:0:8}..."
echo "WhatsApp 号码: $TWILIO_WHATSAPP_NUMBER"
echo "Verify Token: $VERIFY_TOKEN"
echo ""

# 确认配置
read -p "确认以上配置正确？(y/N): " CONFIRM
if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}❌ 配置已取消${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}🔄 正在更新配置文件...${NC}"

# 更新 .env 文件
sed -i '' "s/WHATSAPP_PROVIDER=.*/WHATSAPP_PROVIDER=twilio/" .env
sed -i '' "s/TWILIO_ACCOUNT_SID=.*/TWILIO_ACCOUNT_SID=$TWILIO_ACCOUNT_SID/" .env
sed -i '' "s/TWILIO_AUTH_TOKEN=.*/TWILIO_AUTH_TOKEN=$TWILIO_AUTH_TOKEN/" .env
sed -i '' "s/TWILIO_WHATSAPP_NUMBER=.*/TWILIO_WHATSAPP_NUMBER=$TWILIO_WHATSAPP_NUMBER/" .env
sed -i '' "s/VERIFY_TOKEN=.*/VERIFY_TOKEN=$VERIFY_TOKEN/" .env

echo -e "${GREEN}✅ 配置已更新！${NC}"
echo ""

echo -e "${BLUE}📋 下一步操作:${NC}"
echo "1. 启动测试环境:"
echo "   ./scripts/start_local_test.sh"
echo ""
echo "2. 配置 Twilio Webhook:"
echo "   - 访问 https://console.twilio.com/"
echo "   - 进入 Messaging > Settings > Webhooks"
echo "   - 设置 Webhook URL: https://your-ngrok-url.ngrok-free.app/webhook/whatsapp"
echo "   - 设置 HTTP Method: POST"
echo ""
echo "3. 测试连接:"
echo "   ./scripts/test_webhook.sh"
echo ""

echo -e "${GREEN}🎉 Twilio WhatsApp 配置完成！${NC}"
