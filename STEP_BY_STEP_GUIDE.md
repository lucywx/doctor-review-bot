# 🚀 WhatsApp 医生评价机器人 - 分步部署指南

> 从零开始，手把手教你部署一个完整的 WhatsApp 机器人

---

## 📍 你现在的位置

✅ **已完成**:
- 项目代码开发完成
- 本地服务器运行正常（http://localhost:8000）
- 数据库初始化成功
- Mock 模式测试通过

⏭️ **接下来要做**:
1. 获取所需的 API 密钥
2. 本地测试真实 API
3. 部署到 Railway 云平台
4. 配置 WhatsApp webhook
5. 开始使用

---

## 阶段 1️⃣: 获取 API 密钥（最重要！）

### 1.1 OpenAI API（必需 - 用于情感分析）

**步骤**:

1. **访问** [https://platform.openai.com/](https://platform.openai.com/)

2. **注册/登录** OpenAI 账号

3. **创建 API 密钥**:
   - 点击右上角头像 → "API keys"
   - 点击 "Create new secret key"
   - 命名: `doctor-review-bot`
   - 复制密钥（只显示一次！）: `sk-proj-...`

4. **充值账户** (推荐 $10):
   - 点击 "Billing" → "Add payment method"
   - 添加信用卡
   - 充值 $10（够用几个月）

5. **保存密钥**:
   ```bash
   # 在你的电脑上运行
   nano ~/.env_openai
   # 粘贴: OPENAI_API_KEY=sk-proj-xxxxx
   ```

**成本**: $3-5/月（30用户，1500次查询）

---

### 1.2 Google Places API（必需 - 用于 Google Maps 评价）

**步骤**:

1. **访问** [https://console.cloud.google.com/](https://console.cloud.google.com/)

2. **创建项目**:
   - 点击顶部项目下拉框
   - 点击 "New Project"
   - 项目名称: `doctor-review-bot`
   - 点击 "Create"

3. **启用 Places API**:
   - 在搜索框输入 "Places API"
   - 点击 "Places API"
   - 点击 "Enable"

4. **创建 API 密钥**:
   - 左侧菜单 → "Credentials"
   - 点击 "Create Credentials" → "API key"
   - 复制密钥: `AIzaSy...`

5. **限制 API 密钥**（可选但推荐）:
   - 点击刚创建的密钥
   - "API restrictions" → 选择 "Restrict key"
   - 勾选 "Places API"
   - 保存

6. **启用计费**（获取免费额度）:
   - 左侧菜单 → "Billing"
   - 添加信用卡
   - 每月 $200 免费额度

**成本**: $0/月（免费额度内）

---

### 1.3 WhatsApp Business API（必需 - 用于消息收发）

**步骤**:

1. **访问** [https://developers.facebook.com/](https://developers.facebook.com/)

2. **创建 Meta 开发者账号**:
   - 点击 "Get Started"
   - 使用 Facebook 账号登录
   - 完成验证

3. **创建应用**:
   - 点击 "My Apps" → "Create App"
   - 选择 "Business"
   - 填写信息:
     - App name: `Doctor Review Bot`
     - App contact email: 你的邮箱
   - 点击 "Create App"

4. **添加 WhatsApp 产品**:
   - 在应用仪表板，找到 "Add a Product"
   - 找到 "WhatsApp" → 点击 "Set Up"

5. **获取测试号码和令牌**:
   - 在 "API Setup" 页面:
   - **Phone Number ID**: 复制显示的号码 ID（类似 `109...`）
   - **Access Token**: 点击 "Copy"（临时令牌，24小时有效）
   - **测试号码**: 会显示一个测试用的 WhatsApp 号码

6. **添加测试收件人**:
   - 在同一页面下方 "To"
   - 点击 "Add phone number"
   - 输入你自己的 WhatsApp 号码（需要验证）

7. **获取永久令牌**（稍后部署时需要）:
   - 左侧菜单 → "App Settings" → "Basic"
   - 记下 **App ID** 和 **App Secret**
   - 后续用 Graph API 生成永久令牌

8. **创建 Verify Token**（自定义）:
   - 这是你自己设置的密码，用于验证 webhook
   - 建议: `doctor_review_bot_verify_2025`
   - 记住这个值！

**成本**: $0/月（免费，测试号码有限制）

---

### 1.4 Facebook Graph API（可选 - 用于 Facebook 评价）

**步骤**:

1. **使用与 WhatsApp 相同的 Meta 应用**

2. **生成访问令牌**:
   - 访问 [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
   - 选择你的应用
   - 点击 "Generate Access Token"
   - 选择权限: `pages_read_engagement`, `pages_read_user_content`
   - 复制令牌

3. **获取长期令牌**（可选）:
   - 使用 Access Token Tool 转换为长期令牌
   - 或稍后在代码中自动刷新

**成本**: $0/月（公开内容免费）

---

## 阶段 2️⃣: 配置本地环境（测试真实 API）

### 2.1 更新 .env 文件

现在我们有了所有 API 密钥，更新配置文件：

```bash
# 在项目目录运行
cd ~/Desktop/coding/project02-docreview
nano .env
```

**替换以下值**:

```ini
# WhatsApp Business Cloud API
WHATSAPP_PHONE_NUMBER_ID=109xxxxxxxxx  # 从 Meta 控制台复制
WHATSAPP_ACCESS_TOKEN=EAAxxxxxxxxxxxxx  # 从 Meta 控制台复制
VERIFY_TOKEN=doctor_review_bot_verify_2025  # 你自己设置的

# Google Places API
GOOGLE_PLACES_API_KEY=AIzaSyxxxxxxxxx  # 从 Google Cloud 复制

# Facebook Graph API（可选）
FACEBOOK_ACCESS_TOKEN=EAAxxxxxxxxxxxxx  # 从 Graph API Explorer 复制

# OpenAI API
OPENAI_API_KEY=sk-proj-xxxxxxxxx  # 从 OpenAI 复制
OPENAI_MODEL=gpt-4-turbo
```

保存（Ctrl+O, Enter, Ctrl+X）

---

### 2.2 重启服务测试

```bash
# 1. 停止当前运行的服务
lsof -ti:8000 | xargs kill -9

# 2. 重新启动
source venv/bin/activate
python src/main.py
```

**查看日志**，确认没有 Mock 模式提示：
- ✅ 应该看到: `Using real API keys`
- ❌ 不应该看到: `🎭 Using MOCK mode`

---

### 2.3 本地测试真实 API

**测试 1: 健康检查**
```bash
curl http://localhost:8000/health
```

**测试 2: 模拟 WhatsApp 消息**
```bash
curl -X POST http://localhost:8000/webhook/whatsapp/test \
  -H "Content-Type: application/json" \
  -d '{
    "from": "+1234567890",
    "text": "北京协和医院 张医生"
  }'
```

查看日志，应该看到：
- 🔍 调用 Google Places API
- 🤖 调用 OpenAI 分析情感
- 💾 保存到缓存
- 📤 返回格式化结果

**测试 3: 再次查询（测试缓存）**
```bash
curl -X POST http://localhost:8000/webhook/whatsapp/test \
  -H "Content-Type: application/json" \
  -d '{
    "from": "+1234567890",
    "text": "北京协和医院 张医生"
  }'
```

这次应该很快（✅ Cache hit）

---

## 阶段 3️⃣: 部署到 Railway（生产环境）

### 3.1 准备 Railway 账号

1. **访问** [https://railway.app/](https://railway.app/)

2. **注册账号**:
   - 点击 "Sign Up"
   - 使用 GitHub 账号登录（推荐）

3. **验证邮箱**:
   - 收到验证邮件 → 点击链接

4. **绑定信用卡**（获取免费额度）:
   - 账户设置 → Billing
   - 添加信用卡
   - 免费额度: $5/月

---

### 3.2 安装 Railway CLI

```bash
# macOS
brew install railway

# 或使用 npm
npm install -g @railway/cli

# 验证安装
railway --version
```

---

### 3.3 初始化项目

```bash
# 在项目目录
cd ~/Desktop/coding/project02-docreview

# 登录 Railway
railway login
# 会打开浏览器，点击授权

# 创建新项目
railway init
# 输入项目名称: doctor-review-bot
```

---

### 3.4 添加 PostgreSQL 数据库

```bash
# 添加 PostgreSQL 服务
railway add --database postgres

# 等待创建完成（约 30 秒）
```

---

### 3.5 设置环境变量

**方法 1: 使用 CLI（推荐）**

```bash
# WhatsApp 配置
railway variables set WHATSAPP_PHONE_NUMBER_ID="你的_phone_number_id"
railway variables set WHATSAPP_ACCESS_TOKEN="你的_access_token"
railway variables set VERIFY_TOKEN="doctor_review_bot_verify_2025"

# Google Places API
railway variables set GOOGLE_PLACES_API_KEY="你的_google_api_key"

# Facebook（可选）
railway variables set FACEBOOK_ACCESS_TOKEN="你的_facebook_token"

# OpenAI API
railway variables set OPENAI_API_KEY="你的_openai_key"
railway variables set OPENAI_MODEL="gpt-4-turbo"

# 环境配置
railway variables set ENVIRONMENT="production"
railway variables set DEBUG="false"

# 数据库 URL（自动从 PostgreSQL 服务获取）
railway variables set DATABASE_URL='${{Postgres.DATABASE_URL}}'
```

**方法 2: 使用网页界面**

1. 访问 [https://railway.app/dashboard](https://railway.app/dashboard)
2. 选择你的项目
3. 点击 "Variables" 标签
4. 逐个添加上述变量

---

### 3.6 部署应用

```bash
# 部署到 Railway
railway up

# 等待部署完成（约 2-3 分钟）
# 你会看到构建日志
```

**如果部署成功**，会显示:
```
✅ Deployment successful
🚀 Service is live at: https://xxx.up.railway.app
```

---

### 3.7 生成公网域名

```bash
# 生成域名
railway domain

# 会显示类似: https://doctor-review-bot-production.up.railway.app
```

**复制这个 URL**，后面配置 webhook 需要用！

---

### 3.8 初始化生产数据库

```bash
# 连接到 Railway 环境并初始化数据库
railway run python scripts/init_db.py
```

应该看到:
```
✅ Database initialized successfully!
   - Created 5 tables
```

---

### 3.9 验证部署

```bash
# 替换为你的实际域名
export RAILWAY_URL="https://你的应用.up.railway.app"

# 测试健康检查
curl $RAILWAY_URL/health
```

预期输出:
```json
{
  "status": "healthy",
  "environment": "production",
  "database": "connected"
}
```

---

## 阶段 4️⃣: 配置 WhatsApp Webhook

### 4.1 设置 Webhook URL

1. **访问** [https://developers.facebook.com/](https://developers.facebook.com/)

2. **进入你的应用** → WhatsApp → Configuration

3. **配置 Webhook**:
   - **Callback URL**: `https://你的应用.up.railway.app/webhook/whatsapp`
   - **Verify Token**: `doctor_review_bot_verify_2025`（你设置的值）

4. **点击 "Verify and Save"**

   - 如果成功，会显示绿色勾号 ✅
   - 如果失败，检查:
     - URL 是否正确
     - Verify Token 是否匹配
     - Railway 应用是否运行

5. **订阅 Webhook 字段**:
   - 勾选 `messages`
   - 点击 "Subscribe"

---

### 4.2 测试 Webhook

**方法 1: 从 Meta 控制台发送测试消息**

1. 在 WhatsApp → API Setup 页面
2. "To" 下拉框选择你的测试号码
3. "Message" 输入: `李医生`
4. 点击 "Send Message"

**方法 2: 用你的 WhatsApp 发送消息**

1. 打开你的 WhatsApp
2. 添加测试号码为联系人
3. 发送消息: `你好`
4. 应该收到欢迎消息
5. 发送: `张医生`
6. 应该收到评价汇总

---

## 阶段 5️⃣: 监控和维护

### 5.1 查看日志

```bash
# 实时查看日志
railway logs --tail

# 查看最近 100 条
railway logs --lines 100
```

---

### 5.2 查看统计数据

```bash
# 每日统计
curl $RAILWAY_URL/api/stats/daily

# 应该返回:
# {
#   "total_searches": 10,
#   "cache_hits": 6,
#   "cache_hit_rate": 60.0,
#   ...
# }
```

---

### 5.3 监控成本

**Railway 成本**:
- 登录 Railway Dashboard
- 查看 "Usage" 标签
- 月度免费额度: $5

**API 成本**:
```bash
# 查看 OpenAI 使用情况
https://platform.openai.com/usage

# 查看 Google Cloud 使用情况
https://console.cloud.google.com/billing
```

---

## 🎉 完成！你的机器人已上线

### 测试清单

- [ ] 健康检查返回 "healthy"
- [ ] Webhook 验证成功（绿色勾号）
- [ ] 发送 "你好" 收到欢迎消息
- [ ] 发送医生名字收到评价汇总
- [ ] 查看日志显示正常处理
- [ ] 统计数据正常记录

### 下一步

1. **添加更多测试用户**:
   - Meta 控制台 → WhatsApp → API Setup
   - 添加更多电话号码

2. **申请正式号码**（需要 Meta Business 验证）:
   - 提交商业验证
   - 申请正式 WhatsApp 号码
   - 升级到生产环境

3. **优化缓存策略**:
   - 根据热门医生调整 TTL
   - 监控缓存命中率

4. **添加更多功能**:
   - 医院筛选
   - 地区搜索
   - 评分排序

---

## 🆘 故障排查

### 问题 1: Webhook 验证失败

**症状**: Meta 控制台显示红色 X

**解决**:
```bash
# 1. 检查应用是否运行
curl https://你的应用.up.railway.app/health

# 2. 手动测试 webhook 验证
curl "https://你的应用.up.railway.app/webhook/whatsapp?hub.mode=subscribe&hub.verify_token=doctor_review_bot_verify_2025&hub.challenge=test123"
# 应该返回: test123

# 3. 检查 VERIFY_TOKEN 环境变量
railway variables
```

---

### 问题 2: 收不到消息

**症状**: 发送消息无响应

**解决**:
```bash
# 1. 查看日志
railway logs --tail

# 2. 检查 webhook 订阅
# Meta 控制台 → WhatsApp → Configuration
# 确认 "messages" 已勾选

# 3. 检查电话号码是否在测试列表
# Meta 控制台 → WhatsApp → API Setup → "To"
```

---

### 问题 3: API 报错

**症状**: 日志显示 API 错误

**解决**:
```bash
# 检查 API 密钥
railway variables | grep API

# 测试 OpenAI
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer 你的_OPENAI_KEY"

# 测试 Google Places
curl "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=museum&inputtype=textquery&key=你的_GOOGLE_KEY"
```

---

### 问题 4: 数据库连接失败

**症状**: 健康检查返回 "database": "disconnected"

**解决**:
```bash
# 1. 检查 PostgreSQL 服务状态
railway status

# 2. 重新初始化数据库
railway run python scripts/init_db.py

# 3. 检查 DATABASE_URL
railway variables | grep DATABASE
```

---

## 📚 参考资料

- [WhatsApp Business API 文档](https://developers.facebook.com/docs/whatsapp)
- [OpenAI API 文档](https://platform.openai.com/docs)
- [Google Places API 文档](https://developers.google.com/maps/documentation/places/web-service)
- [Railway 部署指南](https://docs.railway.app/)

---

## ❓ 需要帮助？

如果遇到问题，请提供：
1. 错误日志（`railway logs`）
2. 环境变量（隐藏敏感值）
3. 具体操作步骤

我会帮你解决！
