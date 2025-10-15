# ⚠️ Railway 环境变量配置

## 问题原因
本地测试找到 17 条评价，但 Railway 上找不到任何评价。

**原因**: Railway 没有配置 Google Custom Search API 密钥！

---

## 🔧 解决方法：添加环境变量到 Railway

### 步骤 1: 打开 Railway 项目
1. 访问 https://railway.app/
2. 进入你的 `doctor-review-bot` 项目
3. 点击项目 → **Variables** 选项卡

### 步骤 2: 添加 Google API 环境变量

添加这两个变量：

```
变量名: GOOGLE_SEARCH_API_KEY
变量值: (粘贴你的 Google API Key)

变量名: GOOGLE_SEARCH_ENGINE_ID
变量值: 451baeb0bffe64a5e (你的搜索引擎 ID)
```

### 步骤 3: 重新部署
点击 **Deploy** 或等待自动重新部署（约 1-2 分钟）

---

## 📋 需要添加的完整环境变量列表

确保 Railway 上有这些环境变量：

### ✅ 必需的变量
- `DATABASE_URL` - PostgreSQL 连接（Railway 自动提供）
- `OPENAI_API_KEY` - OpenAI API 密钥
- `TWILIO_ACCOUNT_SID` - Twilio 账户 SID
- `TWILIO_AUTH_TOKEN` - Twilio 认证令牌
- `TWILIO_WHATSAPP_NUMBER` - Twilio WhatsApp 号码
- `VERIFY_TOKEN` - Webhook 验证令牌
- `ADMIN_PHONE_NUMBER` - 管理员电话
- **`GOOGLE_SEARCH_API_KEY`** ⚠️ **新增 - 必需！**
- **`GOOGLE_SEARCH_ENGINE_ID`** ⚠️ **新增 - 必需！**

### ⚙️ 可选的变量
- `OPENAI_MODEL` - 默认 `gpt-4-turbo`
- `RATE_LIMIT_PER_USER_DAILY` - 默认 `50`
- `CACHE_DEFAULT_TTL_DAYS` - 默认 `7`

---

## 🔍 如何找到你的 Google API 密钥

### API Key
从你的 `.env` 文件中复制：
```bash
cat .env | grep GOOGLE_SEARCH_API_KEY
```

### Search Engine ID
从你的 `.env` 文件中复制：
```bash
cat .env | grep GOOGLE_SEARCH_ENGINE_ID
```

---

## ✅ 验证配置成功

部署完成后，在 WhatsApp 测试：
1. 发送: `Dr Tang Boon Nee`
2. 预期结果: 应该返回 **17 条评价**（包括 Facebook）

---

## 🐛 如果还是不工作

查看 Railway 日志：
1. Railway 项目 → **Deployments**
2. 点击最新部署
3. 查看日志，搜索关键词：
   - `Google Search API not configured`
   - `Error`
   - `google_search_api_key`

如果看到 "Google Search API not configured"，说明环境变量没有正确配置。
