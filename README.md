# Doctor Review Aggregation WhatsApp Bot

## 项目概述

一个基于 WhatsApp 的智能医生评价聚合机器人，帮助用户快速搜索和汇总全网医生评价信息。

### 核心功能

- 🔍 **多源搜索**：聚合 Google Maps、Facebook、医院官网等公开评价
- 🤖 **智能分类**：AI 自动将评价分为正面/负面，并标注来源
- ⚡ **缓存优化**：智能缓存机制，降低 API 调用成本
- 💬 **WhatsApp 交互**：通过 WhatsApp 即可查询，无需安装应用

### 使用流程

1. 用户通过 WhatsApp 发送医生姓名
2. Bot 搜索全网公开评价数据
3. AI 分析并分类为正面/负面评价
4. 返回格式化结果，标注每条评价的来源

---

## 技术架构

### 技术栈

- **后端**：Python 3.10+ / FastAPI
- **数据库**：PostgreSQL（缓存层）
- **AI 分析**：OpenAI GPT-4-turbo-mini
- **消息平台**：WhatsApp Business Cloud API
- **搜索引擎**：
  - Google Places API（Google Maps 评价）
  - Facebook Graph API（公开主页/群组）
  - Web Scraping（医院官网公开页面）

### 系统组件

```
用户 WhatsApp
    ↓
WhatsApp Business API
    ↓
FastAPI 后端服务
    ↓
┌─────────────┴─────────────┐
│                           │
缓存数据库 (PostgreSQL)    多引擎搜索聚合
    ↓                       ↓
返回缓存结果          实时调用 API
                            ↓
                      OpenAI 情感分析
                            ↓
                      存入缓存 + 返回结果
```

---

## 项目规模

### 初期目标

- **用户数**：30 人
- **日搜索量**：50 次
- **月搜索量**：1,500 次

### 成本预算（月度）

| 项目 | 费用 (USD) |
|------|-----------|
| WhatsApp Business API | $0（免费额度） |
| Google Places API | $0（免费额度 $200/月） |
| Facebook Graph API | $0（公开内容免费） |
| OpenAI API | $3-5 |
| 数据库托管 | $0-5（免费层） |
| 云服务器 | $5-10 |
| **总计** | **$15-25/月** |

---

## 开发计划

### 开发时间线（AI 辅助）

| 阶段 | 时间 | 任务 |
|------|------|------|
| **Day 1** | 4-6h | API 注册 + 后端框架搭建 + WhatsApp 集成 |
| **Day 2** | 3-4h | 多引擎搜索聚合 + 缓存逻辑 |
| **Day 3** | 2-3h | AI 情感分析 + 输出格式化 |
| **Day 4** | 2-3h | 测试 + 部署上线 |

**总计：2-3 天（12-16 小时）**

---

## 项目结构

```
project02-docreview/
├── README.md                 # 项目概述
├── docs/                     # 文档目录
│   ├── architecture.md       # 系统架构设计
│   ├── database.md           # 数据库设计
│   ├── api-integration.md    # API 集成指南
│   └── deployment.md         # 部署文档
├── src/                      # 源代码
│   ├── main.py              # 主入口
│   ├── whatsapp/            # WhatsApp 模块
│   ├── search/              # 搜索聚合模块
│   ├── analysis/            # AI 分析模块
│   ├── cache/               # 缓存模块
│   └── models/              # 数据模型
├── config/                   # 配置文件
├── tests/                    # 测试文件
└── requirements.txt          # 依赖列表
```

---

## 🚀 快速开始

### ⚡ 3 步完成 WhatsApp 接入（推荐）

如果你已经创建了 Meta 应用，想快速接入 WhatsApp API：

```bash
# 1. 配置 WhatsApp 凭证（5分钟）
./scripts/setup_whatsapp.sh

# 2. 启动本地测试环境（2分钟）
./scripts/start_local_test.sh

# 3. 测试 Webhook（3分钟）
./scripts/test_webhook.sh
```

**详细步骤见：** [WhatsApp 快速接入指南](docs/WHATSAPP_QUICKSTART.md)

---

### 📋 前置准备

**1. 获取 API 密钥**

| API | 用途 | 获取地址 | 必需 |
|-----|------|----------|------|
| WhatsApp Business Cloud API | 消息收发 | [Meta for Developers](https://developers.facebook.com/) | ✅ |
| OpenAI API | 情感分析 | [OpenAI Platform](https://platform.openai.com/) | ✅ |
| Google Places API | Google Maps 评价 | [Google Cloud Console](https://console.cloud.google.com/) | ✅ |
| Facebook Access Token | Facebook 评价 | Meta 应用中获取 | ✅ |

**2. 系统要求**

- Python 3.10+
- SQLite 3（开发环境）或 PostgreSQL 14+（生产环境）

---

### 本地开发

#### 1. 环境配置

```bash
# 克隆项目
cd project02-docreview

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

#### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API 密钥：

```ini
# WhatsApp Business API
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_ACCESS_TOKEN=your_access_token
VERIFY_TOKEN=your_custom_token  # 自定义，用于 webhook 验证

# Google Places API
GOOGLE_PLACES_API_KEY=your_google_api_key

# Facebook Graph API
FACEBOOK_ACCESS_TOKEN=your_facebook_token

# OpenAI API
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4-turbo

# 数据库（本地开发用 SQLite）
DATABASE_URL=sqlite:///./doctor_review.db

# 应用配置
ENVIRONMENT=development
DEBUG=true
```

#### 3. 初始化数据库

```bash
# SQLite（本地开发）
python scripts/init_db_sqlite.py

# PostgreSQL（生产环境）
python scripts/init_db.py
```

成功后显示：
```
✅ Database initialized successfully!
   - Created 5 tables
```

#### 4. 启动应用

```bash
# 开发模式（自动重载）
python src/main.py

# 或使用 uvicorn
uvicorn src.main:app --reload
```

访问：
- **API 文档**：http://localhost:8000/docs
- **健康检查**：http://localhost:8000/health

---

### Mock 模式测试（无需真实 API）

如果还没有 API 密钥，可以使用 Mock 模式测试完整流程：

1. **保持 `.env` 中的占位符值不变**（`your_openai_api_key` 等）
2. **启动应用**
3. **测试 WhatsApp webhook**：

```bash
# 测试消息处理
curl -X POST http://localhost:8000/webhook/whatsapp/test \
  -H "Content-Type: application/json" \
  -d '{
    "from": "+1234567890",
    "text": "李医生"
  }'
```

Mock 模式会：
- ✅ 生成模拟的医生评价（4-6条）
- ✅ 使用关键词进行情感分类
- ✅ 测试缓存功能
- ✅ 记录搜索日志

---

### 配置 WhatsApp Webhook

**开发环境（使用 ngrok）**

```bash
# 安装 ngrok
brew install ngrok  # macOS
# 或访问 https://ngrok.com/download

# 启动隧道
ngrok http 8000
```

获得公网 URL（如 `https://abc123.ngrok.io`）后：

1. 访问 [Meta for Developers](https://developers.facebook.com/)
2. 进入你的应用 → WhatsApp → Configuration
3. 设置 Webhook：
   - **Callback URL**: `https://abc123.ngrok.io/webhook/whatsapp`
   - **Verify Token**: 你在 `.env` 中设置的 `VERIFY_TOKEN`
   - **Webhook Fields**: 勾选 `messages`
4. 点击 "Verify and Save"

**验证 webhook**：
```bash
curl "http://localhost:8000/webhook/whatsapp?hub.mode=subscribe&hub.verify_token=YOUR_TOKEN&hub.challenge=test123"
# 应返回：test123
```

---

### 使用示例

**通过 WhatsApp 发送消息：**

```
你: 李医生
Bot: 🔍 正在搜索 李医生 的评价信息...

Bot:
📊 李医生 - 评价汇总

✅ 正面评价 (2条)
1. 李医生非常专业，态度很好...
   🗺️ Google Maps
   🔗 https://maps.google.com/...

❌ 负面评价 (1条)
2. 等待时间较长...
   👥 Facebook
   🔗 https://facebook.com/...

💡 提示：信息来自公开评价，仅供参考
```

**查询配额：**
```
你: 你好
Bot: 👋 欢迎使用医生评价查询助手！

📝 使用方法：
直接发送医生姓名，如"李医生"

⚡ 每日限额：50次查询
```

---

### API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/webhook/whatsapp` | GET | Webhook 验证 |
| `/webhook/whatsapp` | POST | 接收消息 |
| `/webhook/whatsapp/test` | POST | 测试端点 |
| `/api/stats/daily` | GET | 每日统计 |
| `/docs` | GET | API 文档 |

**查看统计数据：**
```bash
curl http://localhost:8000/api/stats/daily
```

返回：
```json
{
  "total_searches": 15,
  "cache_hits": 10,
  "cache_hit_rate": 66.7,
  "avg_response_time_ms": 1250,
  "total_cost_usd": 0.05,
  "total_api_calls": 12
}
```

---

### 常见问题

**Q: 端口 8000 被占用**
```bash
# 查找并终止占用端口的进程
lsof -ti:8000 | xargs kill -9
```

**Q: 数据库连接失败**
- 检查 `DATABASE_URL` 格式
- SQLite: `sqlite:///./doctor_review.db`
- PostgreSQL: `postgresql://user:pass@host:5432/dbname`

**Q: Mock 模式未激活**
- 确保 `.env` 中保留占位符值（如 `your_openai_api_key`）
- 查看日志确认：`🎭 Using MOCK mode`

**Q: WhatsApp 消息收不到**
- 检查 webhook URL 是否正确配置
- 验证 `VERIFY_TOKEN` 是否匹配
- 查看应用日志：`railway logs --tail`（生产环境）

---

### 下一步

- 🚀 **快速接入 WhatsApp**: [docs/WHATSAPP_QUICKSTART.md](./docs/WHATSAPP_QUICKSTART.md) - 3步完成接入
- 📦 **工具包使用说明**: [WHATSAPP_SETUP_SUMMARY.md](./WHATSAPP_SETUP_SUMMARY.md) - 脚本详解
- ⚡ **命令速查**: [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - 常用命令
- 📖 **完整部署指南**: [STEP_BY_STEP_GUIDE.md](./STEP_BY_STEP_GUIDE.md) - 详细步骤
- 🏗️ **系统架构**: [docs/architecture.md](./docs/architecture.md) - 技术细节
- 🗄️ **数据库设计**: [docs/database.md](./docs/database.md) - 数据模型

---

## 法律与合规

⚠️ **重要提示**：

1. **数据来源合规**：仅抓取公开可访问的信息
2. **隐私保护**：遵守 GDPR 和当地个人信息保护法
3. **医疗信息免责**：需添加免责声明，信息仅供参考
4. **平台服务条款**：遵守 Google、Facebook 的 API 使用政策

---

## 联系方式

- 项目负责人：Lucy
- 创建日期：2025-10-08
