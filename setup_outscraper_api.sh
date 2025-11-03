#!/bin/bash

echo "================================================"
echo "🔧 Outscraper API 设置向导"
echo "================================================"
echo ""

# 检查是否已有API key
if [ ! -z "$OUTSCRAPER_API_KEY" ]; then
    echo "✅ 环境变量 OUTSCRAPER_API_KEY 已设置"
    echo "   当前值: ${OUTSCRAPER_API_KEY:0:20}..."
    echo ""
    read -p "是否要更新？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "跳过设置"
        exit 0
    fi
fi

echo "📝 请按照以下步骤获取API Key："
echo ""
echo "1. 访问: https://outscraper.com/"
echo "2. 点击 'Sign Up' 或 'Start Free' 注册账户"
echo "3. 登录后，访问 Dashboard"
echo "4. 点击左侧菜单 'API' 或 'API Keys'"
echo "5. 复制你的API Key"
echo ""
echo "免费额度: 500条评价/月"
echo ""

# 提示用户输入API key
read -p "请粘贴你的 Outscraper API Key: " API_KEY

if [ -z "$API_KEY" ]; then
    echo "❌ 未输入API Key"
    exit 1
fi

echo ""
echo "================================================"
echo "验证API Key..."
echo "================================================"
echo ""

# 验证API key
RESPONSE=$(curl -s -w "\n%{http_code}" -H "X-API-KEY: $API_KEY" https://api.outscraper.com/account)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ API Key 有效！"
    echo ""
    echo "账户信息:"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
    echo ""

    # 添加到.env文件
    ENV_FILE=".env"
    if [ -f "$ENV_FILE" ]; then
        # 检查是否已存在
        if grep -q "OUTSCRAPER_API_KEY" "$ENV_FILE"; then
            # 更新现有的
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS
                sed -i '' "s/OUTSCRAPER_API_KEY=.*/OUTSCRAPER_API_KEY=$API_KEY/" "$ENV_FILE"
            else
                # Linux
                sed -i "s/OUTSCRAPER_API_KEY=.*/OUTSCRAPER_API_KEY=$API_KEY/" "$ENV_FILE"
            fi
            echo "✅ 已更新 .env 文件中的 OUTSCRAPER_API_KEY"
        else
            # 添加新的
            echo "" >> "$ENV_FILE"
            echo "# Outscraper API" >> "$ENV_FILE"
            echo "OUTSCRAPER_API_KEY=$API_KEY" >> "$ENV_FILE"
            echo "✅ 已添加 OUTSCRAPER_API_KEY 到 .env 文件"
        fi
    else
        # 创建新的.env文件
        echo "# Outscraper API" > "$ENV_FILE"
        echo "OUTSCRAPER_API_KEY=$API_KEY" >> "$ENV_FILE"
        echo "✅ 已创建 .env 文件并添加 OUTSCRAPER_API_KEY"
    fi

    # 设置当前shell的环境变量
    export OUTSCRAPER_API_KEY="$API_KEY"

    echo ""
    echo "================================================"
    echo "下一步:"
    echo "================================================"
    echo ""
    echo "1. 运行测试:"
    echo "   python3 test_outscraper_doctor.py"
    echo ""
    echo "2. 如果测试成功，配置Railway:"
    echo "   railway variables set OUTSCRAPER_API_KEY=\"$API_KEY\""
    echo ""
    echo "   或通过Dashboard手动添加:"
    echo "   https://railway.app/dashboard"
    echo ""
    echo "3. 部署并测试生产环境"
    echo ""

else
    echo "❌ API Key 验证失败"
    echo "HTTP状态码: $HTTP_CODE"
    echo "响应: $BODY"
    echo ""
    echo "请检查:"
    echo "1. API Key是否正确复制（没有多余空格）"
    echo "2. 账户是否已激活"
    echo "3. 网络连接是否正常"
    exit 1
fi
