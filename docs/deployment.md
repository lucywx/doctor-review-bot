# 部署与配置文档

本文档详细说明如何将 Doctor Review Bot 部署到生产环境。

---

## 1. 部署架构

```
┌──────────────────────────────────────────────┐
│  Meta (WhatsApp Business Cloud API)         │
│  - Webhook 接收/发送消息                     │
└────────────────┬─────────────────────────────┘
                 │ HTTPS
                 ▼
┌──────────────────────────────────────────────┐
│  Railway / Render / Heroku                   │
│  ┌────────────────────────────────────────┐  │
│  │  FastAPI 应用 (Docker 容器)           │  │
│  │  - Port 8000                           │  │
│  │  - Gunicorn + Uvicorn Workers          │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │  PostgreSQL 数据库                     │  │
│  │  - 内置托管 / Supabase                 │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
                 │
                 ▼
    外部 API（Google、Facebook、OpenAI）
```

---

## 2. 推荐部署平台

### 2.1 Railway（推荐）

**优势**：
- ✅ 免费 $5/月额度
- ✅ 自动部署（Git Push）
- ✅ 内置 PostgreSQL
- ✅ 简单配置

**成本**：
- 免费额度：$5/月
- 超出后：按使用量计费

### 2.2 Render

**优势**：
- ✅ 免费静态站点
- ✅ PostgreSQL 免费版（90 天限制）
- ✅ 自动 HTTPS

**成本**：
- Web Service：免费（有限制）
- 付费：$7/月

### 2.3 Heroku

**优势**：
- ✅ 成熟稳定
- ✅ 丰富插件

**成本**：
- Eco Dyno：$5/月
- PostgreSQL：$0-9/月

---

## 3. Railway 部署步骤（详细）

### 步骤 1：准备项目文件

#### 3.1 创建 `Dockerfile`

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 3.2 创建 `requirements.txt`

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
httpx==0.26.0
asyncpg==0.29.0
sqlalchemy==2.0.25
python-dotenv==1.0.0
openai==1.10.0
beautifulsoup4==4.12.3
pydantic==2.5.3
pydantic-settings==2.1.0
```

#### 3.3 创建 `railway.json`

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 步骤 2：Railway 配置

1. **登录 Railway**
   - 访问 [railway.app](https://railway.app)
   - 使用 GitHub 登录

2. **创建新项目**
   ```bash
   # 方式 1：Web 界面
   New Project → Deploy from GitHub repo → 选择仓库

   # 方式 2：CLI
   npm install -g @railway/cli
   railway login
   railway init
   railway up
   ```

3. **添加 PostgreSQL**
   ```
   New → Database → PostgreSQL
   ```

4. **配置环境变量**
   - 进入项目 → Variables
   - 添加以下变量：

   ```bash
   # Database (Railway 自动生成)
   DATABASE_URL=${{Postgres.DATABASE_URL}}

   # WhatsApp
   WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
   WHATSAPP_ACCESS_TOKEN=your_access_token
   VERIFY_TOKEN=your_verify_token

   # Google
   GOOGLE_PLACES_API_KEY=your_google_api_key

   # Facebook
   FACEBOOK_ACCESS_TOKEN=your_facebook_token

   # OpenAI
   OPENAI_API_KEY=your_openai_key

   # App Settings
   ENVIRONMENT=production
   DEBUG=false
   ```

5. **生成公网域名**
   ```
   Settings → Networking → Generate Domain
   ```
   获得类似：`https://your-app.up.railway.app`

### 步骤 3：配置 WhatsApp Webhook

1. 访问 [Meta for Developers](https://developers.facebook.com/)
2. 进入你的 WhatsApp 应用
3. 配置 Webhook：
   - Callback URL: `https://your-app.up.railway.app/webhook/whatsapp`
   - Verify Token: 与环境变量中的 `VERIFY_TOKEN` 一致
   - Webhook Fields: 勾选 `messages`

### 步骤 4：初始化数据库

```bash
# 方式 1：Railway CLI
railway run python scripts/init_db.py

# 方式 2：Railway Shell
railway shell
python scripts/init_db.py
```

`scripts/init_db.py`：

```python
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def init_database():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))

    # 读取并执行 SQL 文件
    with open("sql/schema.sql", "r") as f:
        sql = f.read()
        await conn.execute(sql)

    print("✅ Database initialized successfully")
    await conn.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_database())
```

---

## 4. Docker 本地测试

### 4.1 创建 `docker-compose.yml`

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/doctor_review
      - WHATSAPP_PHONE_NUMBER_ID=${WHATSAPP_PHONE_NUMBER_ID}
      - WHATSAPP_ACCESS_TOKEN=${WHATSAPP_ACCESS_TOKEN}
      - GOOGLE_PLACES_API_KEY=${GOOGLE_PLACES_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
    volumes:
      - ./src:/app/src

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=doctor_review
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 4.2 启动容器

```bash
# 启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

---

## 5. 环境变量管理

### 5.1 `.env` 文件（本地开发）

```bash
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/doctor_review
WHATSAPP_PHONE_NUMBER_ID=123456789
WHATSAPP_ACCESS_TOKEN=EAAxxxx...
VERIFY_TOKEN=my_secret_token
GOOGLE_PLACES_API_KEY=AIzaxxxx
FACEBOOK_ACCESS_TOKEN=EAAyyyy
OPENAI_API_KEY=sk-xxxx
ENVIRONMENT=development
DEBUG=true
```

### 5.2 配置加载

```python
# src/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str

    # WhatsApp
    whatsapp_phone_number_id: str
    whatsapp_access_token: str
    verify_token: str

    # APIs
    google_places_api_key: str
    facebook_access_token: str
    openai_api_key: str

    # App
    environment: str = "development"
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 6. 生产环境优化

### 6.1 使用 Gunicorn + Uvicorn

```bash
# 安装
pip install gunicorn

# 启动命令（Dockerfile 中）
CMD ["gunicorn", "src.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000"]
```

### 6.2 日志配置

```python
# src/logging_config.py
import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log")
        ]
    )

# src/main.py
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)
```

### 6.3 健康检查端点

```python
@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 检查数据库连接
        await db.execute("SELECT 1")
        return {"status": "healthy", "database": "ok"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 500
```

---

## 7. 数据库备份

### 7.1 自动备份脚本

```bash
#!/bin/bash
# backup.sh

# 从 Railway 获取数据库 URL
DATABASE_URL=$(railway variables get DATABASE_URL)

# 备份文件名
BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"

# 导出数据库
pg_dump $DATABASE_URL > $BACKUP_FILE

# 上传到云存储（可选）
# aws s3 cp $BACKUP_FILE s3://your-bucket/backups/

echo "✅ Backup completed: $BACKUP_FILE"
```

### 7.2 定时备份（Cron）

```bash
# 每天凌晨 2 点备份
0 2 * * * /path/to/backup.sh
```

---

## 8. 监控与告警

### 8.1 使用 Railway 内置监控

- CPU 使用率
- 内存使用率
- 请求响应时间

### 8.2 应用级监控（Sentry）

```bash
pip install sentry-sdk[fastapi]
```

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your_sentry_dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1
)
```

### 8.3 日志聚合（Logtail）

```bash
pip install logtail-python
```

```python
from logtail import LogtailHandler
import logging

handler = LogtailHandler(source_token="your_token")
logger = logging.getLogger(__name__)
logger.addHandler(handler)
```

---

## 9. 安全配置

### 9.1 HTTPS 强制

Railway 自动提供 HTTPS，无需额外配置。

### 9.2 环境变量加密

使用 Railway Secrets（自动加密）。

### 9.3 速率限制

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/webhook/whatsapp")
@limiter.limit("10/minute")
async def webhook(request: Request):
    # ...
    pass
```

---

## 10. CI/CD 配置

### 10.1 GitHub Actions

`.github/workflows/deploy.yml`：

```yaml
name: Deploy to Railway

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Railway CLI
        run: npm install -g @railway/cli

      - name: Deploy to Railway
        run: railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

### 10.2 自动测试

```yaml
# 在 deploy 前添加测试步骤
- name: Run Tests
  run: |
    pip install -r requirements.txt
    pytest tests/
```

---

## 11. 性能优化

### 11.1 连接池配置

```python
# src/database.py
from asyncpg import create_pool

pool = await create_pool(
    dsn=settings.database_url,
    min_size=5,
    max_size=20,
    command_timeout=60
)
```

### 11.2 缓存层（Redis）

```bash
# Railway 添加 Redis
New → Database → Redis
```

```python
import aioredis

redis = await aioredis.from_url(
    os.getenv("REDIS_URL"),
    encoding="utf-8",
    decode_responses=True
)

# 缓存查询结果
await redis.setex(f"doctor:{doctor_id}", 3600, json.dumps(data))
```

---

## 12. 常见问题排查

### 12.1 Webhook 无响应

```bash
# 检查日志
railway logs

# 测试 webhook 连通性
curl https://your-app.up.railway.app/health
```

### 12.2 数据库连接失败

```bash
# 检查 DATABASE_URL
railway variables

# 手动连接测试
railway connect postgres
```

### 12.3 API 调用失败

```python
# 添加详细错误日志
logger.error(f"API call failed: {e}", exc_info=True)
```

---

## 13. 扩展部署

### 13.1 水平扩展

```bash
# Railway 增加实例
Settings → Scale → Replicas: 2
```

### 13.2 负载均衡

Railway 自动提供负载均衡。

---

## 14. 部署检查清单

部署前确认：

- [ ] 所有环境变量已配置
- [ ] Webhook URL 已在 Meta 后台配置
- [ ] 数据库表已创建
- [ ] SSL 证书有效（Railway 自动）
- [ ] 健康检查通过
- [ ] API 密钥有效
- [ ] 日志记录正常
- [ ] 测试消息发送成功

---

## 15. 快速部署命令汇总

```bash
# 1. 初始化 Railway 项目
railway login
railway init
railway link

# 2. 添加 PostgreSQL
railway add --database postgres

# 3. 设置环境变量
railway variables set WHATSAPP_ACCESS_TOKEN=xxx
railway variables set GOOGLE_PLACES_API_KEY=xxx
railway variables set OPENAI_API_KEY=xxx

# 4. 部署
railway up

# 5. 初始化数据库
railway run python scripts/init_db.py

# 6. 查看日志
railway logs --tail

# 7. 打开应用
railway open
```

---

完成以上步骤后，你的 WhatsApp Bot 就上线了！🎉
