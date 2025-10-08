#!/bin/bash

# 本地测试环境一键启动脚本
# 同时启动 FastAPI 服务和 ngrok 隧道

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
echo "  WhatsApp Bot 本地测试启动器"
echo "=========================================="
echo ""

# 检查项目目录
cd "$PROJECT_DIR" || {
    echo -e "${RED}❌ 无法进入项目目录: $PROJECT_DIR${NC}"
    exit 1
}

# 检查 .env 配置
if grep -q "WHATSAPP_PROVIDER=twilio" .env; then
    # 检查 Twilio 配置
    if grep -q "your_twilio_auth_token_here" .env; then
        echo -e "${YELLOW}⚠️  警告: Twilio 配置未完成${NC}"
        echo ""
        echo "请先运行配置脚本:"
        echo "  ./scripts/setup_twilio.sh"
        echo ""
        read -p "是否继续（将使用 Mock 模式）？(y/n): " CONTINUE
        if [[ "$CONTINUE" != "y" && "$CONTINUE" != "Y" ]]; then
            exit 0
        fi
    else
        echo -e "${GREEN}✅ Twilio 配置已设置${NC}"
    fi
elif grep -q "WHATSAPP_PROVIDER=meta" .env || grep -q "WHATSAPP_PHONE_NUMBER_ID" .env; then
    # 检查 Meta 配置
    if grep -q "your_phone_number_id" .env; then
        echo -e "${YELLOW}⚠️  警告: Meta WhatsApp 配置未设置${NC}"
        echo ""
        echo "请先运行配置脚本:"
        echo "  ./scripts/setup_whatsapp.sh"
        echo ""
        read -p "是否继续（将使用 Mock 模式）？(y/n): " CONTINUE
        if [[ "$CONTINUE" != "y" && "$CONTINUE" != "Y" ]]; then
            exit 0
        fi
    else
        echo -e "${GREEN}✅ Meta WhatsApp 配置已设置${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  警告: WhatsApp 配置未设置${NC}"
    echo ""
    echo "请先运行配置脚本:"
    echo "  ./scripts/setup_twilio.sh  (推荐)"
    echo "  ./scripts/setup_whatsapp.sh  (Meta)"
    echo ""
    read -p "是否继续（将使用 Mock 模式）？(y/n): " CONTINUE
    if [[ "$CONTINUE" != "y" && "$CONTINUE" != "Y" ]]; then
        exit 0
    fi
fi

# 检查端口占用
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  端口 $PORT 已被占用${NC}"
    read -p "是否终止占用进程？(y/n): " KILL_PROCESS
    if [[ "$KILL_PROCESS" == "y" || "$KILL_PROCESS" == "Y" ]]; then
        echo "正在终止进程..."
        lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
        sleep 2
    else
        echo "请手动终止占用进程后重试"
        exit 1
    fi
fi

# 检查 ngrok
if ! command -v ngrok &> /dev/null; then
    echo -e "${YELLOW}⚠️  未检测到 ngrok${NC}"
    echo ""
    echo "安装 ngrok:"
    echo "  brew install ngrok"
    echo ""
    read -p "是否继续（不启动 ngrok）？(y/n): " SKIP_NGROK
    if [[ "$SKIP_NGROK" != "y" && "$SKIP_NGROK" != "Y" ]]; then
        exit 0
    fi
    USE_NGROK=false
else
    USE_NGROK=true
fi

# 激活虚拟环境
if [ -d "venv" ]; then
    echo -e "${GREEN}✅ 激活虚拟环境...${NC}"
    source venv/bin/activate
else
    echo -e "${RED}❌ 找不到虚拟环境${NC}"
    exit 1
fi

# 创建日志目录
mkdir -p logs

# 启动 FastAPI 服务
echo ""
echo -e "${GREEN}🚀 启动 FastAPI 服务...${NC}"
echo "   端口: $PORT"
echo "   日志: logs/app.log"
echo ""

# 后台启动
nohup python src/main.py > logs/app.log 2>&1 &
APP_PID=$!
echo $APP_PID > logs/app.pid

# 等待服务启动
echo "等待服务启动..."
sleep 3

# 检查服务状态
if ! curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
    echo -e "${RED}❌ FastAPI 服务启动失败${NC}"
    echo "查看日志: tail -f logs/app.log"
    exit 1
fi

echo -e "${GREEN}✅ FastAPI 服务已启动 (PID: $APP_PID)${NC}"

# 启动 ngrok
if [ "$USE_NGROK" = true ]; then
    echo ""
    echo -e "${GREEN}🌐 启动 ngrok 隧道...${NC}"

    # 后台启动 ngrok
    nohup ngrok http $PORT > logs/ngrok.log 2>&1 &
    NGROK_PID=$!
    echo $NGROK_PID > logs/ngrok.pid

    # 等待 ngrok 启动
    sleep 3

    # 获取 ngrok URL
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"https://[^"]*' | grep -o 'https://[^"]*' | head -1)

    if [ -z "$NGROK_URL" ]; then
        echo -e "${YELLOW}⚠️  无法获取 ngrok URL，请手动访问 http://localhost:4040${NC}"
    else
        echo -e "${GREEN}✅ ngrok 隧道已启动 (PID: $NGROK_PID)${NC}"
        echo ""
        echo "=========================================="
        echo -e "  ${BLUE}ngrok Public URL${NC}"
        echo "=========================================="
        echo ""
        echo -e "${GREEN}$NGROK_URL${NC}"
        echo ""
        echo "Webhook URL (复制这个):"
        echo -e "${YELLOW}$NGROK_URL/webhook/whatsapp${NC}"
        echo ""
    fi
fi

# 显示状态
echo "=========================================="
echo "  服务状态"
echo "=========================================="
echo ""
echo -e "${GREEN}✅ FastAPI:${NC} http://localhost:$PORT"
echo -e "${GREEN}✅ API 文档:${NC} http://localhost:$PORT/docs"
if [ "$USE_NGROK" = true ]; then
    echo -e "${GREEN}✅ ngrok 控制台:${NC} http://localhost:4040"
fi
echo ""

# 显示下一步
echo "=========================================="
echo "  下一步操作"
echo "=========================================="
echo ""
echo -e "${BLUE}1. 配置 Meta Webhook:${NC}"
echo "   - 访问: https://developers.facebook.com/"
echo "   - 进入: Doctor Review Bot → WhatsApp → Configuration"
echo "   - Callback URL: $NGROK_URL/webhook/whatsapp"
echo "   - Verify Token: (从 .env 中查看)"
echo ""
echo -e "${BLUE}2. 测试 Webhook:${NC}"
echo "   ./scripts/test_webhook.sh"
echo ""
echo -e "${BLUE}3. 查看日志:${NC}"
echo "   tail -f logs/app.log"
echo ""
echo -e "${BLUE}4. 停止服务:${NC}"
echo "   kill $APP_PID"
if [ "$USE_NGROK" = true ]; then
    echo "   kill $NGROK_PID"
fi
echo ""

# 保持终端打开，实时显示日志
echo "=========================================="
echo "  实时日志 (Ctrl+C 停止查看，服务继续运行)"
echo "=========================================="
echo ""

sleep 2
tail -f logs/app.log
