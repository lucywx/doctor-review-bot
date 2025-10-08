# WhatsApp Business API 快速接入指南

> 3 步完成 WhatsApp 集成，5 分钟开始测试

---

## 🎯 目标

完成 WhatsApp Business API 接入，让你的医生评价机器人能够：
- ✅ 接收用户通过 WhatsApp 发送的消息
- ✅ 自动回复查询结果
- ✅ 记录搜索日志和统计数据

---

## 📋 前置准备

### 必需账号
- [x] Meta (Facebook) 开发者账号
- [x] WhatsApp 账号（用于测试）

### 本地环境
- [x] 项目已启动（`python src/main.py`）
- [x] 安装 ngrok：`brew install ngrok`

---

## 🚀 3 步接入流程

### Step 1️⃣: 获取 WhatsApp API 凭证 (5 分钟)

#### 1.1 访问 Meta Developers

```
https://developers.facebook.com/
→ My Apps
→ Doctor Review Bot (你已创建的应用)
→ WhatsApp
→ API Setup
```

#### 1.2 复制 3 个关键信息

| 信息 | 在哪里找 | 示例 |
|-----|---------|------|
| **Phone Number ID** | "From" 下拉框下面 | `109361185504724` |
| **Temporary Access Token** | "Temporary access token" 点击复制 | `EAAGm7J1VhB4BO...` |
| **测试号码** | "Send and receive messages" 区域 | `+1 555 0100` |

#### 1.3 添加你的测试号码

1. 在同一页面下方找到 **"To"** 下拉框
2. 点击 **"Manage phone number list"**
3. 点击 **"Add phone number"**
4. 输入你的 WhatsApp 号码（格式：`+8613800138000`）
5. 去 WhatsApp 查收验证码，输入完成验证

#### 1.4 运行配置脚本

```bash
cd /Users/lucyy/Desktop/coding/project02-docreview
./scripts/setup_whatsapp.sh
```

按提示输入：
- Phone Number ID
- Access Token
- Verify Token（使用默认值即可）

---

### Step 2️⃣: 启动本地测试环境 (2 分钟)

#### 2.1 一键启动

```bash
./scripts/start_local_test.sh
```

**这个脚本会自动：**
- ✅ 启动 FastAPI 服务 (localhost:8000)
- ✅ 启动 ngrok 隧道（生成公网 URL）
- ✅ 显示实时日志

#### 2.2 复制 ngrok URL

启动后会显示：

```
==========================================
  ngrok Public URL
==========================================

https://abc123-45-67-89.ngrok-free.app

Webhook URL (复制这个):
https://abc123-45-67-89.ngrok-free.app/webhook/whatsapp
```

**⚠️ 复制带 `/webhook/whatsapp` 的完整 URL！**

---

### Step 3️⃣: 配置 Meta Webhook (3 分钟)

#### 3.1 进入 Webhook 配置页面

```
https://developers.facebook.com/
→ My Apps
→ Doctor Review Bot
→ WhatsApp
→ Configuration
```

#### 3.2 填写 Webhook 信息

| 字段 | 填入内容 |
|-----|---------|
| **Callback URL** | `https://abc123...ngrok-free.app/webhook/whatsapp` |
| **Verify token** | `my_secret_verify_token_123` (或你自定义的) |

#### 3.3 点击 "Verify and Save"

**成功标志：**
- ✅ 显示绿色勾号
- ✅ Status: Active

**如果显示红色 X：**
- 检查 ngrok 是否运行（访问 http://localhost:4040）
- 检查 Verify Token 是否完全一致
- 运行测试脚本：`./scripts/test_webhook.sh`

#### 3.4 订阅消息事件

在同一页面（Configuration）：
1. 找到 **"Webhook fields"**
2. 勾选 ☑️ **`messages`**
3. 点击 **"Subscribe"**

---

## 🎉 完成！开始测试

### 测试方式 1：命令行测试

```bash
./scripts/test_webhook.sh
```

选择测试环境，会自动测试：
- ✅ 健康检查
- ✅ Webhook 验证
- ✅ 消息处理
- ✅ 医生查询

### 测试方式 2：Meta 控制台测试

```
WhatsApp → API Setup
→ "To" 选择你的测试号码
→ "Message" 输入：你好
→ 点击 "Send Message"
```

**应该看到：**
- FastAPI 日志显示收到消息
- 测试号码收到欢迎消息

### 测试方式 3：真实 WhatsApp 测试

1. 打开 WhatsApp
2. 添加测试号码 `+1 555 0100` 为联系人
3. 发送消息：`你好`
4. 应该收到欢迎消息：

```
👋 欢迎使用医生评价查询助手！

📝 使用方法：
直接发送医生姓名，如"李医生"

⚡ 每日限额：50次查询
```

5. 发送：`李医生`
6. 应该收到评价汇总

---

## 📊 查看运行状态

### 查看实时日志

```bash
# FastAPI 日志
tail -f logs/app.log

# ngrok 控制台
open http://localhost:4040
```

### 查看统计数据

```bash
curl http://localhost:8000/api/stats/daily
```

返回：
```json
{
  "total_searches": 5,
  "cache_hits": 2,
  "cache_hit_rate": 40.0,
  "avg_response_time_ms": 1200
}
```

---

## 🆘 常见问题

### Q1: Webhook 验证失败（红色 X）

**检查清单：**

```bash
# 1. 测试服务是否运行
curl http://localhost:8000/health

# 2. 测试 ngrok 是否正常
curl https://your-ngrok-url.ngrok-free.app/health

# 3. 手动测试 Webhook 验证
curl "https://your-ngrok-url.ngrok-free.app/webhook/whatsapp?hub.mode=subscribe&hub.verify_token=my_secret_verify_token_123&hub.challenge=test123"
# 应返回: test123

# 4. 运行自动测试
./scripts/test_webhook.sh
```

**常见原因：**
- ❌ Verify Token 拼写错误（大小写敏感）
- ❌ ngrok 未启动或 URL 变化
- ❌ FastAPI 服务未运行

---

### Q2: 发送消息无响应

**检查清单：**

1. **确认 Webhook Fields 已勾选 `messages`**
   ```
   Meta → WhatsApp → Configuration → Webhook fields
   ```

2. **查看 FastAPI 日志**
   ```bash
   tail -f logs/app.log
   # 应该看到: 📬 Received webhook: {...}
   ```

3. **查看 ngrok 日志**
   ```
   访问 http://localhost:4040
   查看 "HTTP Requests" 是否有收到请求
   ```

4. **确认手机号在测试列表**
   ```
   Meta → WhatsApp → API Setup → "To"
   检查你的号码是否已添加并验证
   ```

---

### Q3: Access Token 过期

**症状：** 日志显示 `401 Unauthorized`

**原因：** Temporary Access Token 只有 24 小时有效

**解决：**
1. 访问 Meta → WhatsApp → API Setup
2. 复制新的 Temporary Access Token
3. 重新运行配置脚本：
   ```bash
   ./scripts/setup_whatsapp.sh
   ```
4. 重启服务：
   ```bash
   ./scripts/start_local_test.sh
   ```

**长期方案：** 生成永久 Token（见部署文档）

---

### Q4: ngrok URL 频繁变化

**问题：** 每次重启 ngrok，URL 都会变化，需要重新配置 Webhook

**免费方案：**
- 注册 ngrok 账号
- 获取固定域名（免费账号支持 1 个）
- 修改启动脚本使用固定域名

**推荐方案：** 部署到 Railway（永久域名）

---

## 🚀 下一步：部署到生产环境

本地测试成功后，建议部署到 Railway：

```bash
./scripts/deploy_railway.sh
```

**优势：**
- ✅ 固定域名（无需频繁更新 Webhook）
- ✅ 24/7 运行
- ✅ 免费额度 $5/月
- ✅ 自动重启和监控

详见：[Railway 部署指南](../DEPLOYMENT_GUIDE.md)

---

## 📚 相关文档

- [完整部署指南](../STEP_BY_STEP_GUIDE.md)
- [API 集成文档](./api-integration.md)
- [数据库设计](./database.md)
- [系统架构](./architecture.md)

---

## ✅ 验收清单

本地测试完成标志：

- [ ] 配置脚本运行成功
- [ ] ngrok 隧道启动并显示 URL
- [ ] Meta Webhook 验证成功（绿色勾号）
- [ ] `messages` 事件已订阅
- [ ] 命令行测试通过（`test_webhook.sh`）
- [ ] Meta 控制台发送消息成功
- [ ] 真实 WhatsApp 发送消息收到回复
- [ ] 发送医生姓名收到评价汇总
- [ ] 日志显示正常处理流程

全部通过 ✅ = 可以部署到生产环境！

---

## 💡 小贴士

### 开发调试技巧

```bash
# 实时查看所有请求
tail -f logs/app.log | grep "📬 Received"

# 查看情感分析结果
tail -f logs/app.log | grep "🤖 Analyzing"

# 查看缓存命中
tail -f logs/app.log | grep "✅ Using.*cached"
```

### Mock 模式测试

如果还没有 OpenAI API Key，可以使用 Mock 模式：
- 保持 `.env` 中 `OPENAI_API_KEY=your_openai_api_key`
- 启动服务会自动检测并使用 Mock
- 日志显示：`🧪 Using MOCK mode`

---

## 🆘 需要帮助？

如果遇到问题：

1. **查看日志**
   ```bash
   tail -f logs/app.log
   ```

2. **运行健康检查**
   ```bash
   curl http://localhost:8000/health
   ```

3. **运行自动测试**
   ```bash
   ./scripts/test_webhook.sh
   ```

4. **联系支持**
   - 提供错误日志
   - 说明复现步骤
   - 附上配置信息（隐藏敏感值）

---

**祝你接入成功！🎉**
