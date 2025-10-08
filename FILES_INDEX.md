# 📁 项目文件索引

> 快速找到你需要的文件

---

## 🚀 快速开始

| 文件 | 用途 | 何时使用 |
|-----|------|---------|
| **[START_HERE.md](START_HERE.md)** | 总览和快速启动 | 🌟 **从这里开始！** |
| **[TEST_RESULTS.md](TEST_RESULTS.md)** | 测试报告 | 查看系统状态 |

---

## 📖 用户文档

### WhatsApp 接入相关

| 文件 | 大小 | 内容 | 适用场景 |
|-----|------|------|---------|
| [docs/WHATSAPP_QUICKSTART.md](docs/WHATSAPP_QUICKSTART.md) | 8.0KB | 3 步快速接入指南 | 第一次接入 |
| [WHATSAPP_SETUP_SUMMARY.md](WHATSAPP_SETUP_SUMMARY.md) | 12KB | 工具包详解 | 了解脚本原理 |
| [docs/WHATSAPP_FLOW_DIAGRAM.md](docs/WHATSAPP_FLOW_DIAGRAM.md) | 21KB | 可视化流程图 | 理解数据流 |

### 通用参考

| 文件 | 内容 | 适用场景 |
|-----|------|---------|
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | 命令速查表 | 日常使用 |
| [README.md](README.md) | 项目总览 | 了解项目 |
| [STEP_BY_STEP_GUIDE.md](STEP_BY_STEP_GUIDE.md) | 完整部署指南 | 详细步骤 |
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | Railway 部署 | 生产部署 |
| [TESTING.md](TESTING.md) | 测试指南 | 运行测试 |

### 技术文档

| 文件 | 内容 |
|-----|------|
| [docs/architecture.md](docs/architecture.md) | 系统架构设计 |
| [docs/database.md](docs/database.md) | 数据库设计 |
| [docs/api-integration.md](docs/api-integration.md) | API 集成详情 |
| [docs/deployment.md](docs/deployment.md) | 部署文档 |
| [docs/timeline-and-budget.md](docs/timeline-and-budget.md) | 时间线和预算 |

---

## 🔧 自动化脚本

| 脚本 | 大小 | 用途 | 命令 |
|-----|------|------|------|
| [scripts/setup_whatsapp.sh](scripts/setup_whatsapp.sh) | 3.7KB | 配置 WhatsApp 凭证 | `./scripts/setup_whatsapp.sh` |
| [scripts/start_local_test.sh](scripts/start_local_test.sh) | 5.0KB | 启动本地测试环境 | `./scripts/start_local_test.sh` |
| [scripts/test_webhook.sh](scripts/test_webhook.sh) | 5.4KB | 测试 Webhook 配置 | `./scripts/test_webhook.sh` |
| [scripts/deploy_railway.sh](scripts/deploy_railway.sh) | 7.9KB | 部署到 Railway | `./scripts/deploy_railway.sh` |

### 数据库脚本

| 脚本 | 用途 |
|-----|------|
| [scripts/init_db_sqlite.py](scripts/init_db_sqlite.py) | 初始化 SQLite（本地） |
| [scripts/init_db.py](scripts/init_db.py) | 初始化 PostgreSQL（生产） |
| [scripts/migrate_to_postgres.py](scripts/migrate_to_postgres.py) | 迁移到 PostgreSQL |

---

## 💻 源代码

### 核心模块

```
src/
├── main.py                    # FastAPI 入口
├── config.py                  # 配置管理
├── database.py                # PostgreSQL 数据库
├── database_sqlite.py         # SQLite 数据库
│
├── whatsapp/                  # WhatsApp 集成
│   ├── routes.py             # Webhook 路由
│   ├── handler.py            # 消息处理器
│   ├── client.py             # API 客户端
│   ├── client_mock.py        # Mock 客户端
│   ├── formatter.py          # 消息格式化
│   └── models.py             # 数据模型
│
├── search/                    # 搜索引擎
│   ├── aggregator.py         # 搜索聚合器
│   ├── google_places.py      # Google Places API
│   ├── facebook.py           # Facebook Graph API
│   └── mock_searcher.py      # Mock 搜索器
│
├── analysis/                  # AI 分析
│   └── sentiment.py          # 情感分析
│
├── cache/                     # 缓存管理
│   └── manager.py            # 缓存管理器
│
├── models/                    # 数据模型
│   ├── user.py               # 用户配额管理
│   └── search_log.py         # 搜索日志
│
└── utils/                     # 工具函数
    ├── logger.py             # 日志配置
    └── error_handler.py      # 异常处理
```

---

## 🗄️ 配置文件

| 文件 | 用途 |
|-----|------|
| [.env](.env) | 环境变量（本地） |
| [.env.example](.env.example) | 环境变量模板 |
| [.env.production](.env.production) | 生产环境配置 |
| [requirements.txt](requirements.txt) | Python 依赖 |
| [Dockerfile](Dockerfile) | Docker 配置 |
| [docker-compose.yml](docker-compose.yml) | Docker Compose |
| [railway.json](railway.json) | Railway 配置 |

---

## 🧪 测试文件

| 文件 | 用途 |
|-----|------|
| [test_openai.py](test_openai.py) | 测试 OpenAI API |
| [test_real_sentiment.py](test_real_sentiment.py) | 测试情感分析 |
| [test_api_key.py](test_api_key.py) | 测试 API Key |
| [test_gpt5_fixed.py](test_gpt5_fixed.py) | 测试 GPT-5 |
| [test_webhook.json](test_webhook.json) | Webhook 测试数据 |
| [tests/test_performance.py](tests/test_performance.py) | 性能测试 |

---

## 📊 使用场景索引

### 场景 1：第一次接入 WhatsApp

```
1. START_HERE.md              # 了解概况
2. docs/WHATSAPP_QUICKSTART.md # 跟着操作
3. scripts/setup_whatsapp.sh   # 配置凭证
4. scripts/start_local_test.sh # 启动测试
5. scripts/test_webhook.sh     # 验证接入
```

### 场景 2：遇到问题需要排查

```
1. QUICK_REFERENCE.md          # 查找常见问题
2. logs/app.log                # 查看日志
3. TEST_RESULTS.md             # 对比测试结果
4. docs/WHATSAPP_FLOW_DIAGRAM.md # 理解流程
```

### 场景 3：准备部署到生产

```
1. DEPLOYMENT_GUIDE.md         # 了解部署流程
2. scripts/deploy_railway.sh   # 一键部署
3. STEP_BY_STEP_GUIDE.md       # 详细步骤
```

### 场景 4：想修改代码

```
1. docs/architecture.md        # 了解架构
2. src/whatsapp/handler.py     # 消息处理逻辑
3. src/search/aggregator.py    # 搜索逻辑
4. src/analysis/sentiment.py   # AI 分析逻辑
```

### 场景 5：查看统计数据

```
1. curl http://localhost:8000/api/stats/daily
2. sqlite3 doctor_review.db
   SELECT * FROM search_logs ORDER BY created_at DESC;
```

---

## 🔍 快速搜索

### 按关键词查找文件

**WhatsApp 相关**:
- `grep -r "whatsapp" --include="*.md"`

**API 相关**:
- `grep -r "api" --include="*.py"`

**配置相关**:
- `ls -la | grep -E "\.(env|json|yml)"`

**脚本相关**:
- `ls -la scripts/*.sh`

---

## 📈 文件大小统计

```bash
# 文档总大小
du -sh docs/

# 脚本总大小
du -sh scripts/

# 源代码总大小
du -sh src/

# 项目总大小（不含 venv）
du -sh --exclude=venv .
```

---

## 🌟 推荐阅读路径

### 新手路径
```
START_HERE.md
  ↓
WHATSAPP_QUICKSTART.md
  ↓
QUICK_REFERENCE.md
  ↓
开始操作
```

### 深入路径
```
README.md
  ↓
WHATSAPP_FLOW_DIAGRAM.md
  ↓
architecture.md
  ↓
源代码
```

### 运维路径
```
DEPLOYMENT_GUIDE.md
  ↓
deploy_railway.sh
  ↓
QUICK_REFERENCE.md (监控部分)
```

---

## 📋 文件更新记录

| 日期 | 更新内容 |
|------|---------|
| 2025-10-08 21:30 | 创建 WhatsApp 接入工具包 |
| 2025-10-08 21:30 | 创建所有脚本和文档 |
| 2025-10-08 21:30 | 完成测试验证 |

---

**提示**: 将此文件加入书签，方便快速查找！
