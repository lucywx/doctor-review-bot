# ✅ WhatsApp API 接入检查清单

> 跟着这个清单一步步操作，确保不遗漏任何步骤

---

## 📋 Phase 1: Meta 后台操作（5-10 分钟）

### ✅ Step 1.1: 进入应用
- [ ] 访问 https://developers.facebook.com/
- [ ] 点击 **"My Apps"**
- [ ] 找到并点击 **"Doctor Review Bot"**
- [ ] 左侧菜单找到 **"WhatsApp"**

### ✅ Step 1.2: 获取 Phone Number ID
- [ ] 点击 **"API Setup"**
- [ ] 找到 **"From"** 下拉框
- [ ] 在下拉框下方看到一串数字（如 `109361185504724`）
- [ ] **复制这串数字** → 记为 `Phone Number ID`

```
示例：109361185504724
你的：___________________
```

### ✅ Step 1.3: 获取 Access Token
- [ ] 在同一页面找到 **"Temporary access token"**
- [ ] 点击右侧的 **"Copy"** 按钮
- [ ] **复制 Token** → 记为 `Access Token`
- [ ] ⚠️ 注意：临时 Token 只有 24 小时有效

```
示例：EAAGm7J1VhB4BO...
你的：___________________
```

### ✅ Step 1.4: 添加测试号码
- [ ] 在同一页面往下滚动，找到 **"To"** 下拉框
- [ ] 点击 **"Manage phone number list"**
- [ ] 点击 **"Add phone number"**
- [ ] 输入你的 WhatsApp 号码（格式：`+8613800138000`）
- [ ] 去 WhatsApp 查收验证码
- [ ] 输入验证码完成验证
- [ ] ✅ 看到号码显示在列表中

### ✅ Step 1.5: 记录测试号码
- [ ] 在 "Send and receive messages" 区域
- [ ] 看到 Meta 提供的测试号码（如 `+1 555 0100`）
- [ ] **记录这个号码** → 稍后用 WhatsApp 给它发消息

```
测试号码：___________________
```

---

## 📋 Phase 2: 本地配置（2-3 分钟）

### ✅ Step 2.1: 运行配置脚本

打开终端，执行：

```bash
cd /Users/lucyy/Desktop/coding/project02-docreview
./scripts/setup_whatsapp.sh
```

- [ ] 脚本启动，显示欢迎信息
- [ ] 提示 "请输入 Phone Number ID"
- [ ] **粘贴** 刚才复制的 Phone Number ID
- [ ] 提示 "请输入 Access Token"
- [ ] **粘贴** 刚才复制的 Access Token
- [ ] 提示 "使用默认 Verify Token？"
- [ ] 输入 `y` 使用默认值
- [ ] ✅ 看到 "配置已更新！"

### ✅ Step 2.2: 验证配置

```bash
grep "WHATSAPP_PHONE_NUMBER_ID" .env
grep "WHATSAPP_ACCESS_TOKEN" .env
```

- [ ] 确认看到你输入的值（不是 `your_phone_number_id`）
- [ ] ✅ 配置成功

---

## 📋 Phase 3: 启动测试环境（2-3 分钟）

### ✅ Step 3.1: 停止当前服务（如果在运行）

```bash
lsof -ti:8000 | xargs kill -9
```

- [ ] 执行命令（如果端口未占用会显示错误，忽略即可）

### ✅ Step 3.2: 启动测试环境

```bash
./scripts/start_local_test.sh
```

- [ ] 脚本开始运行
- [ ] 看到 "✅ FastAPI 服务已启动"
- [ ] 看到 "✅ ngrok 隧道已启动"
- [ ] 看到类似这样的 URL：
  ```
  https://abc123-45-67-89.ngrok-free.app/webhook/whatsapp
  ```
- [ ] **复制完整的 Webhook URL**（包含 `/webhook/whatsapp`）
- [ ] ✅ 服务运行中（终端显示日志）

```
你的 ngrok URL：
___________________________________________
```

### ✅ Step 3.3: 保持终端运行

- [ ] **不要关闭这个终端窗口**
- [ ] 服务需要持续运行
- [ ] 可以按 `Ctrl+C` 停止查看日志，但服务会继续运行

---

## 📋 Phase 4: 配置 Meta Webhook（3-5 分钟）

### ✅ Step 4.1: 进入 Webhook 配置页面

- [ ] 回到 Meta for Developers
- [ ] 确保在 **"Doctor Review Bot"** 应用中
- [ ] 左侧菜单点击 **"WhatsApp"**
- [ ] 点击 **"Configuration"**

### ✅ Step 4.2: 配置 Callback URL

- [ ] 找到 **"Webhook"** 部分
- [ ] 找到 **"Callback URL"** 输入框
- [ ] **粘贴** 刚才复制的 ngrok URL
  ```
  https://abc123-45-67-89.ngrok-free.app/webhook/whatsapp
  ```
- [ ] ⚠️ 确保 URL 结尾是 `/webhook/whatsapp`

### ✅ Step 4.3: 配置 Verify Token

- [ ] 找到 **"Verify token"** 输入框
- [ ] 输入：`my_secret_verify_token_123`
- [ ] ⚠️ 注意：必须完全一致，区分大小写

### ✅ Step 4.4: 验证 Webhook

- [ ] 点击 **"Verify and Save"** 按钮
- [ ] 等待几秒...
- [ ] ✅ 看到 **绿色勾号** ✓
- [ ] ✅ Status 显示 **"Active"**

**如果显示红色 X：**
- [ ] 检查 ngrok 是否运行（访问 http://localhost:4040）
- [ ] 检查 Verify Token 是否完全一致
- [ ] 查看终端日志是否有错误
- [ ] 运行测试脚本：`./scripts/test_webhook.sh`

### ✅ Step 4.5: 订阅消息事件

- [ ] 在同一页面往下滚动
- [ ] 找到 **"Webhook fields"** 部分
- [ ] 找到 **"messages"** 选项
- [ ] **勾选** ☑️ **messages**
- [ ] 点击 **"Subscribe"** 或 **"Save"**
- [ ] ✅ 确认已勾选

---

## 📋 Phase 5: 测试接入（5 分钟）

### ✅ Step 5.1: 自动化测试

打开新终端窗口：

```bash
cd /Users/lucyy/Desktop/coding/project02-docreview
./scripts/test_webhook.sh
```

- [ ] 选择 `2` (ngrok)
- [ ] 脚本自动检测 ngrok URL
- [ ] 测试 1: 健康检查
  - [ ] ✅ 显示 "healthy"
- [ ] 测试 2: Webhook 验证
  - [ ] ✅ 返回 challenge 值
- [ ] 测试 3: 测试消息
  - [ ] ✅ 状态 "ok"
- [ ] 测试 4: 医生查询
  - [ ] ✅ 处理成功

### ✅ Step 5.2: Meta 控制台测试

- [ ] 回到 Meta → WhatsApp → **API Setup**
- [ ] 找到 **"To"** 下拉框
- [ ] 选择你添加的测试号码
- [ ] 在 **"Message"** 输入框输入：`你好`
- [ ] 点击 **"Send Message"**
- [ ] 查看终端日志，应该看到：
  ```
  📨 Received message from ...
  ```
- [ ] ✅ 日志显示消息已处理

### ✅ Step 5.3: 真实 WhatsApp 测试

- [ ] 打开你的 WhatsApp 应用
- [ ] 添加测试号码为联系人（如 `+1 555 0100`）
- [ ] 发送消息：`你好`
- [ ] 等待几秒...
- [ ] ✅ 收到机器人回复的欢迎消息

### ✅ Step 5.4: 医生查询测试

- [ ] 继续在 WhatsApp 中发送：`李医生`
- [ ] 等待几秒...
- [ ] ✅ 收到评价汇总信息
- [ ] ✅ 信息格式正确（正面/负面评价分类）
- [ ] ✅ 显示来源标签

---

## 🎉 完成检查

### ✅ 最终验证

- [ ] Webhook 验证显示绿色勾号
- [ ] messages 事件已订阅
- [ ] 自动化测试全部通过
- [ ] WhatsApp 能收到欢迎消息
- [ ] WhatsApp 能收到医生评价汇总
- [ ] 终端日志显示正常处理流程

### ✅ 功能测试

测试以下命令，确保都能正常回复：

| 发送内容 | 预期回复 |
|---------|---------|
| `你好` | ✅ 欢迎消息 |
| `hello` | ✅ 欢迎消息 |
| `帮助` | ✅ 欢迎消息 |
| `李医生` | ✅ 评价汇总（正面/负面分类） |
| `张医生` | ✅ 评价汇总 |
| `随便输入` | ✅ 无效输入提示 |

---

## 📊 接入完成！

### 当前状态
- ✅ WhatsApp API 已配置
- ✅ Webhook 已验证
- ✅ 本地服务运行中
- ✅ ngrok 隧道正常
- ✅ 消息处理正常
- ✅ AI 分析功能正常

### 下一步（可选）

#### 选项 1: 继续本地测试
- 保持当前状态，继续测试各种功能
- 添加更多测试用户
- 调整配置优化性能

#### 选项 2: 部署到生产环境
```bash
./scripts/deploy_railway.sh
```

---

## 🆘 遇到问题？

### 常见问题速查

**Q1: Webhook 验证失败（红色 X）**
```bash
# 测试本地服务
curl http://localhost:8000/health

# 测试 ngrok
open http://localhost:4040

# 手动验证
curl "http://localhost:8000/webhook/whatsapp?hub.mode=subscribe&hub.verify_token=my_secret_verify_token_123&hub.challenge=test"
```

**Q2: 收不到消息**
- 检查 messages 是否已勾选
- 检查手机号是否在测试列表
- 查看终端日志
- 检查 ngrok 控制台（http://localhost:4040）

**Q3: ngrok URL 变化**
- 免费版每次重启会变化
- 需要重新配置 Meta Webhook
- 建议注册 ngrok 获取固定域名

**Q4: Access Token 过期**
- 临时 Token 24 小时有效
- 重新运行 `./scripts/setup_whatsapp.sh`
- 或在 Meta 后台重新复制

---

## 📝 记录信息

记录以下信息以备后用：

```
配置日期：2025-10-08
Phone Number ID：___________________
测试号码：___________________
ngrok URL：___________________
Verify Token：my_secret_verify_token_123

笔记：
_______________________________________
_______________________________________
_______________________________________
```

---

**完成时间：__________**

**操作者签字：__________**

🎊 恭喜！你的 WhatsApp 医生评价机器人已经成功上线！
