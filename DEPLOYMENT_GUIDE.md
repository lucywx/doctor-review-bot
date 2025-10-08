# 🚀 部署指南

## 快速部署到 Railway（推荐）

### 前置准备

1. **获取 API 密钥**

**WhatsApp Business API：**
- 访问 [Meta for Developers](https://developers.facebook.com/)
- 创建应用 → 添加 WhatsApp 产品
- 获取：Phone Number ID, Access Token
- 设置自定义 Verify Token

**Google Places API：**
- 访问 [Google Cloud Console](https://console.cloud.google.com/)
- 启用 Places API
- 创建 API 密钥

**Facebook Graph API：**
- 使用与 WhatsApp 相同的 Meta 应用
- 获取长期访问令牌

**OpenAI API：**
- 访问 [OpenAI Platform](https://platform.openai.com/)
- 生成 API 密钥

---

### 部署步骤

#### 1. 部署到 Railway

```bash
# 安装 Railway CLI
npm install -g @railway/cli

# 登录
railway login

# 初始化项目
railway init

# 添加 PostgreSQL
railway add --database postgres

# 设置环境变量
railway variables set WHATSAPP_PHONE_NUMBER_ID="your_value"
railway variables set WHATSAPP_ACCESS_TOKEN="your_value"
railway variables set VERIFY_TOKEN="your_custom_token"
railway variables set GOOGLE_PLACES_API_KEY="your_value"
railway variables set FACEBOOK_ACCESS_TOKEN="your_value"
railway variables set OPENAI_API_KEY="your_value"
railway variables set ENVIRONMENT="production"
railway variables set DEBUG="false"

# 自动设置数据库 URL
railway variables set DATABASE_URL='${{Postgres.DATABASE_URL}}'

# 部署
railway up

# 生成公网域名
railway domain

# 初始化数据库
railway run python scripts/init_db.py
```

#### 2. 配置 WhatsApp Webhook

获得 Railway 域名后（如 `https://your-app.up.railway.app`）：

1. 访问 [Meta for Developers](https://developers.facebook.com/)
2. 进入你的应用 → WhatsApp → Configuration
3. 设置 Webhook：
   - **Callback URL**: `https://your-app.up.railway.app/webhook/whatsapp`
   - **Verify Token**: 你设置的 `VERIFY_TOKEN`
   - **Webhook Fields**: 勾选 `messages`
4. 点击 "Verify and Save"

---

## 本地开发

```bash
# 1. 克隆项目
cd project02-docreview

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API 密钥

# 5. 初始化数据库
python scripts/init_db_sqlite.py

# 6. 启动应用
python src/main.py
```

访问 http://localhost:8000/docs 查看 API 文档

---

## 环境变量说明

| 变量 | 说明 | 必需 |
|------|------|------|
| `DATABASE_URL` | 数据库连接字符串 | ✅ |
| `WHATSAPP_PHONE_NUMBER_ID` | WhatsApp 电话号码 ID | ✅ |
| `WHATSAPP_ACCESS_TOKEN` | WhatsApp 访问令牌 | ✅ |
| `VERIFY_TOKEN` | Webhook 验证令牌（自定义） | ✅ |
| `GOOGLE_PLACES_API_KEY` | Google Places API 密钥 | ✅ |
| `FACEBOOK_ACCESS_TOKEN` | Facebook 访问令牌 | ✅ |
| `OPENAI_API_KEY` | OpenAI API 密钥 | ✅ |
| `OPENAI_MODEL` | OpenAI 模型名称 | ❌ (默认 gpt-4-turbo) |
| `ENVIRONMENT` | 运行环境 | ❌ (production/development) |
| `RATE_LIMIT_PER_USER_DAILY` | 每日查询限制 | ❌ (默认 50) |

---

## 测试部署

### 1. 健康检查

```bash
curl https://your-app.up.railway.app/health
```

预期输出：
```json
{
  "status": "healthy",
  "environment": "production",
  "database": "connected"
}
```

### 2. Webhook 验证

```bash
curl "https://your-app.up.railway.app/webhook/whatsapp?hub.mode=subscribe&hub.verify_token=YOUR_TOKEN&hub.challenge=test123"
```

预期输出：`test123`

### 3. 发送测试消息

通过 WhatsApp 发送消息到你的机器人号码，测试完整流程。

---

## 监控和维护

### 查看日志

```bash
railway logs --tail
```

### 查看数据库

```bash
railway connect postgres
```

### 每日统计

访问 API 端点查看统计数据：
```bash
curl https://your-app.up.railway.app/api/stats/daily
```

---

## 成本估算

### Railway（托管平台）
- 免费额度：$5/月
- 超出后：按使用量计费

### API 调用成本（30用户，1500次/月）
- WhatsApp: $0（免费额度内）
- Google Places: $0（免费额度内）
- OpenAI: $3-5/月
- **总计**: **$3-5/月**

---

## 故障排查

### Webhook 无法连接
- 检查 Railway 应用是否正常运行
- 确认域名可访问
- 验证 Verify Token 是否匹配

### 数据库连接失败
- 检查 `DATABASE_URL` 环境变量
- 确认 PostgreSQL 服务正常
- 运行数据库初始化脚本

### API 调用失败
- 检查所有 API 密钥是否有效
- 查看日志获取详细错误信息
- 确认 API 配额未超限

---

## 扩展到更多用户

当用户增长时：

1. **升级 Railway 计划**
   - 增加 CPU/内存
   - 添加多个实例

2. **优化缓存策略**
   - 增加缓存有效期
   - 使用 Redis 共享缓存

3. **监控 API 成本**
   - 查看每日统计
   - 调整搜索策略

---

## 安全建议

- ✅ 使用 HTTPS（Railway 自动提供）
- ✅ 验证 Webhook 签名
- ✅ 限制每日查询次数
- ✅ 定期更新依赖包
- ✅ 不要将 `.env` 提交到 Git

---

## 支持

如遇问题，查看：
- Railway 日志：`railway logs`
- 应用日志：检查 `/logs` 目录
- API 文档：`https://your-app.up.railway.app/docs`
