#!/bin/bash

# WhatsApp API 配置助手
# 交互式引导设置 WhatsApp Business API 凭证

set -e

echo "=========================================="
echo "  WhatsApp Business API 配置助手"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查 .env 文件
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ 错误: 找不到 .env 文件${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 请准备好以下信息（从 Meta Developers 获取）:${NC}"
echo ""
echo "访问: https://developers.facebook.com/"
echo "进入: My Apps → Doctor Review Bot → WhatsApp → API Setup"
echo ""

# 获取 Phone Number ID
echo "----------------------------------------"
echo -e "${YELLOW}1️⃣  Phone Number ID${NC}"
echo "   在哪里找: 'From' 下拉框下面显示"
echo "   示例: 109361185504724"
echo ""
read -p "请输入 Phone Number ID: " PHONE_NUMBER_ID

if [ -z "$PHONE_NUMBER_ID" ]; then
    echo -e "${RED}❌ Phone Number ID 不能为空${NC}"
    exit 1
fi

# 获取 Access Token
echo ""
echo "----------------------------------------"
echo -e "${YELLOW}2️⃣  Temporary Access Token${NC}"
echo "   在哪里找: 'Temporary access token' 区域，点击复制"
echo "   示例: EAAGm7J1VhB4BO..."
echo "   注意: 临时令牌 24 小时有效"
echo ""
read -p "请输入 Access Token: " ACCESS_TOKEN

if [ -z "$ACCESS_TOKEN" ]; then
    echo -e "${RED}❌ Access Token 不能为空${NC}"
    exit 1
fi

# Verify Token (用户自定义)
echo ""
echo "----------------------------------------"
echo -e "${YELLOW}3️⃣  Verify Token (自定义密码)${NC}"
echo "   这是你自己设置的密码，用于验证 Webhook"
echo "   当前值: my_secret_verify_token_123"
echo ""
read -p "使用默认值？(y/n, 默认 y): " USE_DEFAULT_VERIFY

VERIFY_TOKEN="my_secret_verify_token_123"
if [[ "$USE_DEFAULT_VERIFY" == "n" || "$USE_DEFAULT_VERIFY" == "N" ]]; then
    read -p "请输入自定义 Verify Token: " CUSTOM_VERIFY_TOKEN
    if [ ! -z "$CUSTOM_VERIFY_TOKEN" ]; then
        VERIFY_TOKEN="$CUSTOM_VERIFY_TOKEN"
    fi
fi

# 更新 .env 文件
echo ""
echo "----------------------------------------"
echo -e "${GREEN}✅ 正在更新配置...${NC}"

# 备份原文件
cp "$ENV_FILE" "${ENV_FILE}.backup"
echo "   已备份原配置到: ${ENV_FILE}.backup"

# 使用 sed 更新配置
sed -i.tmp "s|WHATSAPP_PHONE_NUMBER_ID=.*|WHATSAPP_PHONE_NUMBER_ID=$PHONE_NUMBER_ID|" "$ENV_FILE"
sed -i.tmp "s|WHATSAPP_ACCESS_TOKEN=.*|WHATSAPP_ACCESS_TOKEN=$ACCESS_TOKEN|" "$ENV_FILE"
sed -i.tmp "s|VERIFY_TOKEN=.*|VERIFY_TOKEN=$VERIFY_TOKEN|" "$ENV_FILE"

# 删除临时文件
rm -f "${ENV_FILE}.tmp"

echo -e "${GREEN}✅ 配置已更新！${NC}"
echo ""

# 显示配置摘要
echo "=========================================="
echo "  配置摘要"
echo "=========================================="
echo ""
echo "Phone Number ID: ${PHONE_NUMBER_ID:0:10}..."
echo "Access Token: ${ACCESS_TOKEN:0:20}..."
echo "Verify Token: $VERIFY_TOKEN"
echo ""

# 下一步提示
echo "=========================================="
echo "  下一步操作"
echo "=========================================="
echo ""
echo -e "${GREEN}1. 启动本地测试:${NC}"
echo "   ./scripts/start_local_test.sh"
echo ""
echo -e "${GREEN}2. 配置 Meta Webhook (需要 ngrok URL):${NC}"
echo "   - 访问: https://developers.facebook.com/"
echo "   - 进入: Doctor Review Bot → WhatsApp → Configuration"
echo "   - Callback URL: https://your-ngrok-url.ngrok-free.app/webhook/whatsapp"
echo "   - Verify Token: $VERIFY_TOKEN"
echo ""
echo -e "${GREEN}3. 测试 Webhook:${NC}"
echo "   ./scripts/test_webhook.sh"
echo ""
echo -e "${YELLOW}⚠️  注意: Temporary Access Token 24小时后会过期${NC}"
echo ""
