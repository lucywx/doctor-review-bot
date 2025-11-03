#!/bin/bash

# Outscraper快速启动脚本
echo "🚀 Outscraper Google Maps API 快速启动"
echo "=================================="

# 检查环境变量
if [ -z "$OUTSCRAPER_API_KEY" ]; then
    echo "❌ 请先设置环境变量 OUTSCRAPER_API_KEY"
    echo ""
    echo "📝 使用步骤:"
    echo "1. 访问 https://outscraper.com/ 注册账户"
    echo "2. 获取API密钥"
    echo "3. 设置环境变量:"
    echo "   export OUTSCRAPER_API_KEY='your_api_key_here'"
    echo "4. 重新运行此脚本"
    echo ""
    echo "💡 或者创建 .env 文件并添加:"
    echo "   OUTSCRAPER_API_KEY=your_api_key_here"
    exit 1
fi

echo "✅ API密钥已设置"
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

echo "✅ Python环境检查通过"
echo ""

# 安装依赖
echo "📦 安装依赖包..."
pip3 install requests python-dotenv

# 运行测试
echo "🧪 运行Outscraper测试..."
python3 test_outscraper.py

echo ""
echo "🎉 完成! 现在您可以在项目中使用Outscraper了"
echo ""
echo "📚 更多信息请查看:"
echo "   - OUTSCRAPER_GUIDE.md"
echo "   - src/search/outscraper_client.py"
