#!/bin/bash

# Railway 部署自动化脚本
# 一键部署到 Railway 生产环境

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_DIR="/Users/lucyy/Desktop/coding/project02-docreview"

echo "=========================================="
echo "  Railway 部署助手"
echo "=========================================="
echo ""

# 检查 Railway CLI
if ! command -v railway &> /dev/null; then
    echo -e "${RED}❌ 未检测到 Railway CLI${NC}"
    echo ""
    echo "安装方法:"
    echo "  brew install railway"
    echo ""
    echo "或使用 npm:"
    echo "  npm install -g @railway/cli"
    exit 1
fi

echo -e "${GREEN}✅ Railway CLI 已安装${NC}"
echo ""

# 进入项目目录
cd "$PROJECT_DIR" || exit 1

# 检查登录状态
echo "检查 Railway 登录状态..."
if ! railway whoami &> /dev/null; then
    echo -e "${YELLOW}⚠️  需要登录 Railway${NC}"
    echo ""
    read -p "是否现在登录？(y/n): " DO_LOGIN
    if [[ "$DO_LOGIN" == "y" || "$DO_LOGIN" == "Y" ]]; then
        railway login
    else
        echo "请先运行: railway login"
        exit 0
    fi
fi

echo -e "${GREEN}✅ 已登录 Railway${NC}"
echo ""

# 检查项目是否已初始化
if [ ! -f ".railway" ] && [ ! -d ".railway" ]; then
    echo -e "${YELLOW}⚠️  项目未初始化${NC}"
    echo ""
    read -p "是否创建新项目？(y/n): " CREATE_PROJECT
    if [[ "$CREATE_PROJECT" == "y" || "$CREATE_PROJECT" == "Y" ]]; then
        echo "初始化 Railway 项目..."
        railway init
    else
        exit 0
    fi
fi

# 加载本地环境变量
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ 找不到 .env 文件${NC}"
    exit 1
fi

# 检查是否配置了 WhatsApp
if grep -q "your_phone_number_id" .env; then
    echo -e "${YELLOW}⚠️  警告: WhatsApp 配置未设置${NC}"
    echo ""
    echo "请先运行配置脚本:"
    echo "  ./scripts/setup_whatsapp.sh"
    echo ""
    read -p "是否继续部署？(y/n): " CONTINUE
    if [[ "$CONTINUE" != "y" && "$CONTINUE" != "Y" ]]; then
        exit 0
    fi
fi

# 检查是否已有 PostgreSQL
echo ""
echo "=========================================="
echo "  数据库配置"
echo "=========================================="
echo ""

echo "检查 PostgreSQL 服务..."
if railway variables | grep -q "DATABASE_URL"; then
    echo -e "${GREEN}✅ PostgreSQL 已配置${NC}"
else
    echo -e "${YELLOW}⚠️  未检测到 PostgreSQL${NC}"
    echo ""
    read -p "是否添加 PostgreSQL？(y/n): " ADD_POSTGRES
    if [[ "$ADD_POSTGRES" == "y" || "$ADD_POSTGRES" == "Y" ]]; then
        echo "添加 PostgreSQL 服务..."
        railway add --database postgres
        echo "等待服务启动..."
        sleep 10
    fi
fi

# 设置环境变量
echo ""
echo "=========================================="
echo "  环境变量配置"
echo "=========================================="
echo ""

# 从 .env 读取变量
export $(grep -v '^#' .env | xargs)

echo "正在设置环境变量..."

# 必需的环境变量
REQUIRED_VARS=(
    "WHATSAPP_PHONE_NUMBER_ID"
    "WHATSAPP_ACCESS_TOKEN"
    "VERIFY_TOKEN"
    "GOOGLE_PLACES_API_KEY"
    "OPENAI_API_KEY"
    "OPENAI_MODEL"
)

for VAR in "${REQUIRED_VARS[@]}"; do
    VALUE="${!VAR}"
    if [ -z "$VALUE" ] || [[ "$VALUE" == your_* ]]; then
        echo -e "${YELLOW}⚠️  跳过未配置的变量: $VAR${NC}"
        continue
    fi

    echo "  设置 $VAR..."
    railway variables set "$VAR=$VALUE" > /dev/null 2>&1 || true
done

# 可选变量
OPTIONAL_VARS=(
    "FACEBOOK_ACCESS_TOKEN"
    "WHATSAPP_BUSINESS_ACCOUNT_ID"
)

for VAR in "${OPTIONAL_VARS[@]}"; do
    VALUE="${!VAR}"
    if [ ! -z "$VALUE" ] && [[ "$VALUE" != your_* ]]; then
        echo "  设置 $VAR..."
        railway variables set "$VAR=$VALUE" > /dev/null 2>&1 || true
    fi
done

# 生产环境配置
echo "  设置生产环境配置..."
railway variables set "ENVIRONMENT=production" > /dev/null 2>&1
railway variables set "DEBUG=false" > /dev/null 2>&1
railway variables set "LOG_LEVEL=INFO" > /dev/null 2>&1

# 数据库 URL（从 PostgreSQL 服务获取）
echo "  设置数据库连接..."
railway variables set 'DATABASE_URL=${{Postgres.DATABASE_URL}}' > /dev/null 2>&1

echo -e "${GREEN}✅ 环境变量配置完成${NC}"

# 部署
echo ""
echo "=========================================="
echo "  开始部署"
echo "=========================================="
echo ""

read -p "是否开始部署到 Railway？(y/n): " DO_DEPLOY
if [[ "$DO_DEPLOY" != "y" && "$DO_DEPLOY" != "Y" ]]; then
    echo "取消部署"
    exit 0
fi

echo "正在部署..."
railway up

echo ""
echo -e "${GREEN}✅ 部署完成！${NC}"

# 生成域名
echo ""
echo "=========================================="
echo "  配置域名"
echo "=========================================="
echo ""

# 检查是否已有域名
DOMAIN=$(railway domain 2>&1)
if echo "$DOMAIN" | grep -q "https://"; then
    echo -e "${GREEN}✅ 域名已配置${NC}"
    echo ""
    echo "$DOMAIN"
else
    echo "生成新域名..."
    railway domain
fi

# 获取域名
sleep 2
RAILWAY_DOMAIN=$(railway domain 2>&1 | grep -o "https://[^[:space:]]*" | head -1)

if [ -z "$RAILWAY_DOMAIN" ]; then
    echo -e "${YELLOW}⚠️  无法自动获取域名${NC}"
    echo "请运行: railway domain"
    RAILWAY_DOMAIN="https://your-app.up.railway.app"
fi

echo ""
echo "=========================================="
echo "  部署信息"
echo "=========================================="
echo ""
echo -e "${BLUE}Railway 域名:${NC} $RAILWAY_DOMAIN"
echo -e "${BLUE}Webhook URL:${NC} $RAILWAY_DOMAIN/webhook/whatsapp"
echo -e "${BLUE}API 文档:${NC} $RAILWAY_DOMAIN/docs"
echo ""

# 初始化数据库
echo "=========================================="
echo "  初始化数据库"
echo "=========================================="
echo ""

read -p "是否初始化生产数据库？(y/n): " INIT_DB
if [[ "$INIT_DB" == "y" || "$INIT_DB" == "Y" ]]; then
    echo "正在初始化数据库..."
    railway run python scripts/init_db.py
    echo -e "${GREEN}✅ 数据库初始化完成${NC}"
fi

# 健康检查
echo ""
echo "=========================================="
echo "  健康检查"
echo "=========================================="
echo ""

echo "等待服务启动..."
sleep 10

echo "测试健康检查端点..."
HEALTH_CHECK=$(curl -s "$RAILWAY_DOMAIN/health" || echo "ERROR")

if echo "$HEALTH_CHECK" | grep -q "healthy"; then
    echo -e "${GREEN}✅ 服务运行正常${NC}"
    echo ""
    echo "$HEALTH_CHECK" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_CHECK"
else
    echo -e "${YELLOW}⚠️  服务可能还在启动中${NC}"
    echo "请稍后访问: $RAILWAY_DOMAIN/health"
fi

# 下一步指引
echo ""
echo "=========================================="
echo "  下一步操作"
echo "=========================================="
echo ""
echo -e "${BLUE}1. 更新 Meta Webhook 配置:${NC}"
echo "   - 访问: https://developers.facebook.com/"
echo "   - 进入: Doctor Review Bot → WhatsApp → Configuration"
echo "   - Callback URL: $RAILWAY_DOMAIN/webhook/whatsapp"
echo "   - Verify Token: (使用 .env 中的值)"
echo "   - 点击 'Verify and Save'"
echo ""
echo -e "${BLUE}2. 测试生产环境:${NC}"
echo "   ./scripts/test_webhook.sh"
echo "   (选择选项 3: Railway)"
echo ""
echo -e "${BLUE}3. 查看日志:${NC}"
echo "   railway logs --tail"
echo ""
echo -e "${BLUE}4. 查看统计:${NC}"
echo "   curl $RAILWAY_DOMAIN/api/stats/daily"
echo ""
echo -e "${BLUE}5. 监控服务:${NC}"
echo "   访问 Railway Dashboard"
echo "   https://railway.app/dashboard"
echo ""

# 保存部署信息
echo "$RAILWAY_DOMAIN" > .railway_domain
echo -e "${GREEN}✅ 域名已保存到 .railway_domain${NC}"
echo ""

echo "=========================================="
echo "  部署完成！🎉"
echo "=========================================="
echo ""
echo "服务地址: $RAILWAY_DOMAIN"
echo "Webhook URL: $RAILWAY_DOMAIN/webhook/whatsapp"
echo ""
echo "查看日志: railway logs --tail"
echo "查看状态: railway status"
echo ""
