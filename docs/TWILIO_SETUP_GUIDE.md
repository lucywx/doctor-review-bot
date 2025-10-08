# 📱 Twilio WhatsApp 接入指南

> 使用 Twilio WhatsApp Business API 快速接入医生评价机器人

---

## 🎯 快速开始（5分钟完成）

### Step 1: 配置 Twilio 凭证

```bash
cd /Users/lucyy/Desktop/coding/project02-docreview
./scripts/setup_twilio.sh
```

脚本会自动使用您已获取的信息：
- ✅ Account SID: `your_twilio_account_sid_here`
- ✅ WhatsApp 号码: `+1234567890`
- ⏳ 只需输入 Auth Token

### Step 2: 启动测试环境

```bash
./scripts/start_local_test.sh
```

### Step 3: 配置 Twilio Webhook

1. **访问 Twilio Console**: https://console.twilio.com/
2. **进入 Messaging**: Messaging > Settings > Webhooks
3. **配置 Webhook**:
   - **Webhook URL**: `https://your-ngrok-url.ngrok-free.app/webhook/whatsapp`
   - **HTTP Method**: POST
   - **Save** 保存配置

### Step 4: 测试连接

```bash
./scripts/test_webhook.sh
```

---

## 📋 详细配置步骤

### 1. Twilio Console 配置

#### 获取必要信息

从您的 Twilio Console 中获取：

| 信息 | 位置 | 示例值 |
|------|------|--------|
| Account SID | Dashboard 顶部 | `AC1234567890abcdef1234567890abcdef` |
| Auth Token | Dashboard 顶部 (点击显示) | `your_auth_token_here` |
| WhatsApp 号码 | Messaging > Try it out | `+14155238886` |

#### 配置 Webhook

1. **进入 Webhook 设置**:
   ```
   Twilio Console → Messaging → Settings → Webhooks
   ```

2. **设置 Webhook URL**:
   ```
   https://your-ngrok-url.ngrok-free.app/webhook/whatsapp
   ```

3. **选择 HTTP 方法**: POST

4. **保存配置**

### 2. 本地环境配置

#### 复制环境变量文件

```bash
cp env.example .env
```

#### 运行配置脚本

```bash
./scripts/setup_twilio.sh
```

脚本会引导您：
- 输入 Twilio Auth Token
- 设置 Webhook Verify Token
- 自动更新 `.env` 文件

### 3. 启动服务

```bash
./scripts/start_local_test.sh
```

脚本会：
- ✅ 启动 FastAPI 服务
- ✅ 启动 ngrok 隧道
- ✅ 显示 Webhook URL
- ✅ 显示实时日志

### 4. 测试功能

#### 自动化测试

```bash
./scripts/test_webhook.sh
```

选择 `2` (ngrok)，脚本会测试：
- ✅ 健康检查
- ✅ Webhook 验证
- ✅ 消息处理
- ✅ 医生查询

#### 真实 WhatsApp 测试

1. **添加测试号码**: 在 WhatsApp 中添加 `+14155238886`
2. **发送消息**: `你好`
3. **应该收到**: 欢迎消息
4. **发送查询**: `李医生`
5. **应该收到**: 评价汇总

---

## 🔧 Twilio 与 Meta 的区别

| 特性 | Twilio | Meta |
|------|--------|------|
| **设置复杂度** | 简单 | 复杂 |
| **Webhook 配置** | 直接在 Console | 需要 Meta for Developers |
| **消息格式** | 标准 HTTP POST | Facebook Graph API |
| **认证方式** | Basic Auth | Bearer Token |
| **成本** | 按消息计费 | 免费额度 + 按消息计费 |
| **稳定性** | 高 | 中等 |

---

## 📊 成本估算

### Twilio WhatsApp 定价

| 地区 | 发送消息 | 接收消息 |
|------|---------|---------|
| 美国 | $0.005/条 | $0.005/条 |
| 中国 | $0.01/条 | $0.01/条 |
| 其他地区 | $0.01/条 | $0.01/条 |

### 月度成本估算（30用户，1500次查询）

```
发送消息: 1500 × $0.01 = $15
接收消息: 1500 × $0.01 = $15
总计: $30/月
```

**注意**: 这比 Meta 的免费额度要高，但 Twilio 提供更稳定的服务。

---

## 🚀 生产部署

### 部署到 Railway

```bash
./scripts/deploy_railway.sh
```

### 更新 Twilio Webhook

部署完成后，更新 Twilio Console 中的 Webhook URL：

```
https://your-app.up.railway.app/webhook/whatsapp
```

---

## 🧪 测试场景

### 1. 基础功能测试

| 发送内容 | 预期回复 |
|---------|---------|
| `你好` | ✅ 欢迎消息 |
| `hello` | ✅ 欢迎消息 |
| `帮助` | ✅ 使用说明 |
| `李医生` | ✅ 评价汇总 |
| `张医生` | ✅ 评价汇总 |

### 2. 错误处理测试

| 发送内容 | 预期回复 |
|---------|---------|
| `123` | ✅ 无效输入提示 |
| `@#$%` | ✅ 无效输入提示 |
| 空消息 | ✅ 无效输入提示 |

### 3. 性能测试

```bash
python tests/test_performance.py
```

预期结果：
- 响应时间 < 100ms
- 并发处理 10+ 用户
- 缓存命中率 > 60%

---

## 🆘 故障排查

### 问题 1: Webhook 无法连接

**症状**: Twilio Console 显示 Webhook 失败

**解决**:
```bash
# 1. 检查服务状态
curl http://localhost:8000/health

# 2. 检查 ngrok 状态
curl http://localhost:4040

# 3. 手动测试 Webhook
curl -X POST https://your-ngrok-url.ngrok-free.app/webhook/whatsapp \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:+1234567890&Body=test"
```

### 问题 2: 收不到消息

**症状**: 发送消息无响应

**解决**:
1. 检查 Twilio Console 中的 Webhook 配置
2. 确认 ngrok URL 正确
3. 查看应用日志: `tail -f logs/app.log`
4. 检查 Twilio 账户余额

### 问题 3: 认证失败

**症状**: 日志显示 "Authentication failed"

**解决**:
```bash
# 检查环境变量
grep TWILIO .env

# 重新运行配置脚本
./scripts/setup_twilio.sh
```

### 问题 4: 消息格式错误

**症状**: Twilio API 返回 400 错误

**解决**:
1. 检查电话号码格式（必须包含国家代码）
2. 确认消息内容不为空
3. 检查 Twilio 账户权限

---

## 📚 相关资源

### Twilio 官方文档

- [Twilio WhatsApp API](https://www.twilio.com/docs/whatsapp)
- [Webhook 配置](https://www.twilio.com/docs/messaging/webhooks)
- [消息格式](https://www.twilio.com/docs/messaging/whatsapp)

### 项目文档

- [README.md](../README.md) - 项目总览
- [QUICK_REFERENCE.md](../QUICK_REFERENCE.md) - 命令速查
- [TESTING.md](../TESTING.md) - 测试指南

---

## ✅ 验收清单

完成 Twilio WhatsApp 接入的标志：

- [ ] 运行 `setup_twilio.sh` 成功
- [ ] 运行 `start_local_test.sh` 显示 ngrok URL
- [ ] Twilio Console Webhook 配置成功
- [ ] 运行 `test_webhook.sh` 全部通过
- [ ] WhatsApp 发送 "你好" 收到欢迎消息
- [ ] WhatsApp 发送 "李医生" 收到评价汇总
- [ ] 日志显示 Twilio 消息发送成功

**全部 ✅ = Twilio WhatsApp 接入成功！🎉**

---

## 🎊 下一步

接入成功后，您可以：

1. **监控使用情况**: 查看 Twilio Console 中的使用统计
2. **优化成本**: 调整缓存策略，减少 API 调用
3. **扩展功能**: 添加更多消息类型和模板
4. **部署生产**: 使用 Railway 部署到生产环境

**预计完成时间**: 5-10 分钟
