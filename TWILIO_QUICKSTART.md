# 🚀 Twilio WhatsApp 快速接入指南

> 5分钟完成 Twilio WhatsApp Business API 接入

---

## ✅ 您已经完成的部分

从您的 Twilio Console 截图中，我看到您已经配置了：

- ✅ **Account SID**: `AC1ee327e499287690c7357addf217950d`
- ✅ **WhatsApp 号码**: `+14155238886`
- ✅ **Twilio Console 访问**: 已登录并可以发送消息

---

## 🎯 接下来需要做的（5分钟）

### Step 1: 运行 Twilio 配置脚本

```bash
cd /Users/lucyy/Desktop/coding/project02-docreview
./scripts/setup_twilio.sh
```

脚本会自动使用您已获取的信息，您只需要输入：
- **Auth Token** (从 Twilio Console Dashboard 获取)

### Step 2: 启动测试环境

```bash
./scripts/start_local_test.sh
```

这会：
- ✅ 启动 FastAPI 服务
- ✅ 启动 ngrok 隧道
- ✅ 显示 Webhook URL（记得复制！）

### Step 3: 配置 Twilio Webhook

1. **访问**: https://console.twilio.com/
2. **进入**: Messaging → Settings → Webhooks
3. **设置**:
   - **Webhook URL**: `https://your-ngrok-url.ngrok-free.app/webhook/whatsapp`
   - **HTTP Method**: POST
   - **Save** 保存

### Step 4: 测试连接

```bash
./scripts/test_webhook.sh
```

选择 `2` (ngrok)，脚本会自动测试所有功能。

### Step 5: 真实 WhatsApp 测试

1. **添加测试号码**: 在 WhatsApp 中添加 `+14155238886`
2. **发送消息**: `你好`
3. **应该收到**: 欢迎消息
4. **发送查询**: `李医生`
5. **应该收到**: 评价汇总

---

## 📋 配置摘要

### 已获取的信息
- **Account SID**: `your_twilio_account_sid_here` (示例)
- **WhatsApp 号码**: `+1234567890` (示例)
- **需要输入**: Auth Token

### 环境变量配置
```ini
WHATSAPP_PROVIDER=twilio
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=+14155238886
VERIFY_TOKEN=twilio_verify_token_20250108
```

---

## 🔧 Twilio vs Meta 对比

| 特性 | Twilio | Meta |
|------|--------|------|
| **设置复杂度** | ✅ 简单 | ❌ 复杂 |
| **Webhook 配置** | ✅ 直接在 Console | ❌ 需要 Meta for Developers |
| **消息格式** | ✅ 标准 HTTP POST | ❌ Facebook Graph API |
| **认证方式** | ✅ Basic Auth | ❌ Bearer Token |
| **稳定性** | ✅ 高 | ⚠️ 中等 |

---

## 💰 成本对比

### Twilio WhatsApp 定价
- **发送消息**: $0.01/条
- **接收消息**: $0.01/条
- **月度成本** (30用户, 1500次查询): ~$30

### Meta WhatsApp 定价
- **免费额度**: 每月 1000 次对话
- **超出后**: $0.005-0.01/条
- **月度成本** (30用户, 1500次查询): ~$0-5

**建议**: 初期使用 Meta（成本低），稳定后考虑 Twilio（稳定性高）

---

## 🧪 测试清单

完成接入的标志：

- [ ] 运行 `setup_twilio.sh` 成功
- [ ] 运行 `start_local_test.sh` 显示 ngrok URL
- [ ] Twilio Console Webhook 配置成功
- [ ] 运行 `test_webhook.sh` 全部通过
- [ ] WhatsApp 发送 "你好" 收到欢迎消息
- [ ] WhatsApp 发送 "李医生" 收到评价汇总

**全部 ✅ = Twilio WhatsApp 接入成功！🎉**

---

## 🆘 常见问题

### Q1: Auth Token 在哪里找？

**位置**: Twilio Console Dashboard 顶部
**步骤**:
1. 访问 https://console.twilio.com/
2. 在 Dashboard 顶部找到 "Account SID" 和 "Auth Token"
3. 点击 "Auth Token" 旁边的眼睛图标显示完整 Token

### Q2: Webhook 配置失败

**检查**:
1. ngrok 是否运行: `curl http://localhost:4040`
2. 服务是否运行: `curl http://localhost:8000/health`
3. Webhook URL 是否正确

### Q3: 收不到消息

**解决**:
1. 确认 WhatsApp 号码格式: `+14155238886`
2. 检查 Twilio 账户余额
3. 查看应用日志: `tail -f logs/app.log`

---

## 📚 相关文档

- [TWILIO_SETUP_GUIDE.md](docs/TWILIO_SETUP_GUIDE.md) - 详细配置指南
- [README.md](README.md) - 项目总览
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 命令速查

---

## 🎊 准备好了吗？

### 现在就开始：

```bash
./scripts/setup_twilio.sh
```

**预计 5 分钟后，您的 Twilio WhatsApp 机器人就能工作了！**

---

有任何问题随时查看文档或询问我！🚀
