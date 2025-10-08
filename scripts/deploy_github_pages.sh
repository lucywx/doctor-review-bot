#!/bin/bash

# GitHub Pages 快速部署脚本
# 用于 Meta WhatsApp 商业验证

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=========================================="
echo "  GitHub Pages 部署助手"
echo "=========================================="
echo ""

# 检查是否有 git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ 未安装 Git${NC}"
    echo "请先安装 Git: brew install git"
    exit 1
fi

# 检查是否登录 GitHub
if ! git config user.name &> /dev/null; then
    echo -e "${YELLOW}⚠️  请先配置 Git${NC}"
    echo ""
    read -p "请输入你的 GitHub 用户名: " GIT_USERNAME
    read -p "请输入你的邮箱: " GIT_EMAIL

    git config --global user.name "$GIT_USERNAME"
    git config --global user.email "$GIT_EMAIL"

    echo -e "${GREEN}✅ Git 配置完成${NC}"
fi

echo ""
echo "=========================================="
echo "  创建 GitHub 仓库"
echo "=========================================="
echo ""

echo "请按照以下步骤操作:"
echo ""
echo "1. 访问: https://github.com/new"
echo "2. Repository name: doctor-review-bot"
echo "3. Description: WhatsApp Doctor Review Bot"
echo "4. 设置为: Public"
echo "5. 不要勾选任何初始化选项"
echo "6. 点击 'Create repository'"
echo ""

read -p "完成后按回车继续..."

echo ""
read -p "请输入你的 GitHub 用户名: " GITHUB_USERNAME
REPO_URL="https://github.com/$GITHUB_USERNAME/doctor-review-bot.git"

echo ""
echo -e "${GREEN}仓库 URL: $REPO_URL${NC}"
echo ""

# 初始化 Git
echo "初始化本地仓库..."

if [ ! -d ".git" ]; then
    git init
    echo -e "${GREEN}✅ Git 仓库已初始化${NC}"
fi

# 创建 .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Database
*.db
*.sqlite
*.sqlite3

# Environment
.env
.env.local
.env.production

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
logs/
*.log

# OS
.DS_Store
Thumbs.db

# Railway
.railway/

# Temporary
*.tmp
*.bak
EOF

# 添加文件
echo "添加文件到 Git..."
git add docs/index.html
git add README.md
git add .gitignore

# 提交
echo "创建初始提交..."
git commit -m "Initial commit: Add project homepage for GitHub Pages"

# 添加远程仓库
echo "连接到 GitHub..."
git remote add origin "$REPO_URL" 2>/dev/null || git remote set-url origin "$REPO_URL"

# 创建 gh-pages 分支
echo "创建 gh-pages 分支..."
git checkout -b gh-pages 2>/dev/null || git checkout gh-pages

# 复制 index.html 到根目录
cp docs/index.html index.html
git add index.html
git commit -m "Add homepage to root" 2>/dev/null || echo "No changes to commit"

# 推送
echo ""
echo -e "${YELLOW}准备推送到 GitHub...${NC}"
echo ""
echo "你可能需要输入 GitHub 凭证"
echo "如果使用 HTTPS，可能需要 Personal Access Token"
echo ""

read -p "是否继续推送？(y/n): " DO_PUSH

if [[ "$DO_PUSH" == "y" || "$DO_PUSH" == "Y" ]]; then
    git push -u origin gh-pages

    echo ""
    echo "=========================================="
    echo "  部署完成！"
    echo "=========================================="
    echo ""
    echo -e "${GREEN}✅ GitHub Pages 已部署${NC}"
    echo ""
    echo "你的网站地址:"
    echo -e "${GREEN}https://$GITHUB_USERNAME.github.io/doctor-review-bot/${NC}"
    echo ""
    echo "等待 1-2 分钟后访问，网站生效需要时间"
    echo ""
    echo "=========================================="
    echo "  在 Meta 使用这个网址"
    echo "=========================================="
    echo ""
    echo "回到 Meta 页面，在 Website 字段填入:"
    echo -e "${YELLOW}https://$GITHUB_USERNAME.github.io/doctor-review-bot/${NC}"
    echo ""
else
    echo "取消推送"
fi

echo ""
echo "=========================================="
echo "  备用方案"
echo "=========================================="
echo ""
echo "如果推送失败，可以手动操作:"
echo ""
echo "1. 访问: https://github.com/$GITHUB_USERNAME/doctor-review-bot"
echo "2. 上传 docs/index.html 文件"
echo "3. Settings → Pages → Source: gh-pages branch"
echo ""
