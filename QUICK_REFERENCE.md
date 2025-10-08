# 🚀 快速参考手册

> 常用命令和操作速查表

---

## 📦 一键脚本

### WhatsApp 接入

```bash
# 1. 配置 WhatsApp API 凭证
./scripts/setup_whatsapp.sh

# 2. 启动本地测试（FastAPI + ngrok）
./scripts/start_local_test.sh

# 3. 测试 Webhook 连接
./scripts/test_webhook.sh

# 4. 部署到 Railway（生产环境）
./scripts/deploy_railway.sh
```

---

## 🛠️ 常用命令

### 本地开发

```bash
# 启动服务
source venv/bin/activate
python src/main.py

# 后台启动
nohup python src/main.py > logs/app.log 2>&1 &

# 停止服务
lsof -ti:8000 | xargs kill -9
```

### 查看日志

```bash
# 实时查看日志
tail -f logs/app.log

# 查看最近 100 行
tail -100 logs/app.log

# 过滤特定内容
tail -f logs/app.log | grep "ERROR"
```

### 测试端点

```bash
# 健康检查
curl http://localhost:8000/health

# 测试 Webhook 验证
curl "http://localhost:8000/webhook/whatsapp?hub.mode=subscribe&hub.verify_token=my_secret_verify_token_123&hub.challenge=test"

# 模拟消息
curl -X POST http://localhost:8000/webhook/whatsapp/test \
  -H "Content-Type: application/json" \
  -d '{"from": "+123", "message": "李医生"}'

# 查看统计
curl http://localhost:8000/api/stats/daily | python3 -m json.tool
```

---

## 🌐 ngrok 相关

```bash
# 启动 ngrok
ngrok http 8000

# 查看 ngrok 控制台
open http://localhost:4040

# 获取 ngrok URL
curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"https://[^"]*'

# 停止 ngrok
pkill ngrok
```

---

## 🚂 Railway 相关

```bash
# 登录
railway login

# 初始化项目
railway init

# 查看环境变量
railway variables

# 设置环境变量
railway variables set KEY=value

# 部署
railway up

# 查看日志
railway logs --tail

# 查看状态
railway status

# 生成域名
railway domain

# 运行命令（在生产环境）
railway run python scripts/init_db.py
```

---

## 📋 Meta Developers 配置

### Webhook 配置路径

```
https://developers.facebook.com/
→ My Apps
→ Doctor Review Bot
→ WhatsApp
→ Configuration
```

### 必填信息

| 字段 | 值 |
|-----|---|
| Callback URL | `https://your-ngrok-url.ngrok-free.app/webhook/whatsapp` |
| Verify token | `my_secret_verify_token_123` |
| Webhook fields | ☑️ `messages` |

### API Setup 路径

```
https://developers.facebook.com/
→ My Apps
→ Doctor Review Bot
→ WhatsApp
→ API Setup
```

### 需要复制的信息

- Phone Number ID
- Temporary Access Token
- 测试号码（添加你的 WhatsApp）

---

## 🗄️ 数据库操作

### 初始化数据库

```bash
# SQLite（本地）
python scripts/init_db_sqlite.py

# PostgreSQL（生产）
python scripts/init_db.py

# Railway 环境
railway run python scripts/init_db.py
```

### 查看数据

```bash
# SQLite
sqlite3 doctor_review.db

# 查看表
.tables

# 查看搜索日志
SELECT * FROM search_logs ORDER BY created_at DESC LIMIT 10;

# 查看用户配额
SELECT * FROM user_quotas;

# 退出
.quit
```

---

## 🧪 测试和调试

### Mock 模式

保持 `.env` 中以下值为占位符，自动启用 Mock：

```ini
WHATSAPP_ACCESS_TOKEN=your_access_token
GOOGLE_PLACES_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key
```

### 查看 Mock 状态

启动服务时日志会显示：
```
🧪 Using MOCK mode
🧪 Using MOCK searcher
🧪 Using MOCK sentiment analyzer
```

### 常见日志标记

| 标记 | 含义 |
|-----|------|
| 🚀 | 服务启动 |
| 📬 | 收到 webhook |
| 🔍 | 开始搜索 |
| ✅ | 操作成功 |
| ❌ | 错误 |
| 🎭 | Mock 模式 |
| 🤖 | AI 分析 |
| 💾 | 缓存操作 |

---

## ⚠️ 故障排查

### 问题 1: 端口占用

```bash
# 查看占用端口的进程
lsof -ti:8000

# 终止进程
lsof -ti:8000 | xargs kill -9
```

### 问题 2: Webhook 验证失败

```bash
# 1. 检查服务状态
curl http://localhost:8000/health

# 2. 检查 ngrok 状态
curl http://localhost:4040

# 3. 手动测试验证
curl "http://localhost:8000/webhook/whatsapp?hub.mode=subscribe&hub.verify_token=my_secret_verify_token_123&hub.challenge=test123"

# 4. 查看日志
tail -f logs/app.log | grep "Webhook"
```

### 问题 3: API 调用失败

```bash
# 测试 OpenAI API
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# 测试 Google Places API
curl "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=hospital&inputtype=textquery&key=$GOOGLE_PLACES_API_KEY"
```

### 问题 4: 数据库连接失败

```bash
# 检查数据库文件
ls -lh doctor_review.db

# 重新初始化
rm doctor_review.db
python scripts/init_db_sqlite.py
```

---

## 📊 监控命令

### 系统资源

```bash
# CPU 和内存占用
top | grep python

# 磁盘使用
df -h

# 日志文件大小
ls -lh logs/
```

### 应用监控

```bash
# 实时请求监控
tail -f logs/app.log | grep "📬"

# 错误监控
tail -f logs/app.log | grep "❌"

# 性能监控
tail -f logs/app.log | grep "response_time"
```

---

## 🔑 环境变量速查

### 必需变量

```ini
# WhatsApp
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_ACCESS_TOKEN=
VERIFY_TOKEN=

# Google
GOOGLE_PLACES_API_KEY=

# OpenAI
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4-turbo

# 数据库
DATABASE_URL=sqlite:///./doctor_review.db
```

### 可选变量

```ini
# Facebook
FACEBOOK_ACCESS_TOKEN=

# 应用配置
ENVIRONMENT=development
DEBUG=true
PORT=8000

# 缓存
CACHE_DEFAULT_TTL_DAYS=7

# 限流
RATE_LIMIT_PER_USER_DAILY=50
```

---

## 📚 文档索引

| 文档 | 用途 |
|-----|------|
| [README.md](README.md) | 项目总览 |
| [WHATSAPP_QUICKSTART.md](docs/WHATSAPP_QUICKSTART.md) | WhatsApp 快速接入 |
| [STEP_BY_STEP_GUIDE.md](STEP_BY_STEP_GUIDE.md) | 完整部署指南 |
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | Railway 部署详解 |
| [TESTING.md](TESTING.md) | 测试指南 |
| [docs/architecture.md](docs/architecture.md) | 系统架构 |
| [docs/api-integration.md](docs/api-integration.md) | API 集成详情 |
| [docs/database.md](docs/database.md) | 数据库设计 |

---

## 🆘 快速支持

### 常见问题

1. **Webhook 验证失败** → 检查 Verify Token 是否匹配
2. **收不到消息** → 确认 `messages` 已订阅
3. **API 调用失败** → 检查 API Key 是否有效
4. **端口占用** → `lsof -ti:8000 | xargs kill -9`
5. **ngrok URL 变化** → 重新配置 Meta Webhook

### 日志关键词搜索

```bash
# 查找错误
grep -r "ERROR" logs/

# 查找特定功能
grep -r "search_doctor" logs/

# 查找时间范围
grep "2025-10-08" logs/app.log
```

---

**提示：** 将此文档添加到浏览器书签，方便随时查阅！
