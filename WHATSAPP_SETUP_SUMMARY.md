# ✅ WhatsApp API 接入工具包 - 使用说明

> 你现在有了完整的 WhatsApp 接入自动化工具包！

---

## 🎁 你获得了什么

### 1. **4 个自动化脚本**

| 脚本 | 用途 | 预计时间 |
|-----|------|---------|
| `scripts/setup_whatsapp.sh` | 交互式配置 WhatsApp 凭证 | 5 分钟 |
| `scripts/start_local_test.sh` | 一键启动本地测试环境（FastAPI + ngrok） | 2 分钟 |
| `scripts/test_webhook.sh` | 自动化测试 Webhook 配置 | 3 分钟 |
| `scripts/deploy_railway.sh` | 一键部署到 Railway 生产环境 | 10 分钟 |

### 2. **2 个详细指南**

| 文档 | 内容 |
|-----|------|
| [docs/WHATSAPP_QUICKSTART.md](docs/WHATSAPP_QUICKSTART.md) | 3 步快速接入指南（图文详解） |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | 常用命令速查表 |

### 3. **更新的 README**

[README.md](README.md) 增加了快速开始部分，直接链接到新工具。

---

## 🚀 立即开始（3 步走）

### Step 1: 在 Meta 获取凭证（5 分钟）

访问 [https://developers.facebook.com/](https://developers.facebook.com/)：

```
My Apps → Doctor Review Bot → WhatsApp → API Setup
```

需要复制：
- ✅ Phone Number ID（在 "From" 下拉框下方）
- ✅ Temporary Access Token（点击复制按钮）
- ✅ 添加你的 WhatsApp 号码到测试列表

### Step 2: 运行配置脚本（2 分钟）

```bash
cd /Users/lucyy/Desktop/coding/project02-docreview
./scripts/setup_whatsapp.sh
```

按提示输入刚才复制的信息，脚本会自动：
- 更新 `.env` 文件
- 备份原配置
- 显示下一步操作

### Step 3: 启动测试环境（2 分钟）

```bash
./scripts/start_local_test.sh
```

脚本会自动：
- 启动 FastAPI 服务
- 启动 ngrok 隧道
- 显示 Webhook URL
- 实时显示日志

**复制显示的 ngrok URL！**

---

## 📋 配置 Meta Webhook（3 分钟）

访问：
```
https://developers.facebook.com/
→ My Apps
→ Doctor Review Bot
→ WhatsApp
→ Configuration
```

填入：
- **Callback URL**: `https://your-ngrok-url.ngrok-free.app/webhook/whatsapp`
- **Verify token**: `my_secret_verify_token_123`

点击 **"Verify and Save"**，看到 ✅ 绿色勾号即成功！

勾选：
- ☑️ **messages** (在 Webhook fields 下)

---

## 🧪 测试接入（2 分钟）

### 方法 1：自动化测试

```bash
./scripts/test_webhook.sh
```

选择测试环境（本地/ngrok/Railway），脚本会自动测试 4 个场景：
- ✅ 健康检查
- ✅ Webhook 验证
- ✅ 消息处理
- ✅ 医生查询

### 方法 2：真实 WhatsApp 测试

1. 打开 WhatsApp
2. 向测试号码发送：`你好`
3. 应该收到欢迎消息
4. 发送：`李医生`
5. 应该收到评价汇总

---

## 🎯 整个流程总结

```
┌─────────────────────────────────────────┐
│  1. Meta 获取凭证 (5 分钟)              │
│     - Phone Number ID                   │
│     - Access Token                      │
│     - 添加测试号码                      │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│  2. 运行配置脚本 (2 分钟)               │
│     ./scripts/setup_whatsapp.sh         │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│  3. 启动测试环境 (2 分钟)               │
│     ./scripts/start_local_test.sh       │
│     → 复制 ngrok URL                    │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│  4. 配置 Meta Webhook (3 分钟)          │
│     - Callback URL: ngrok URL           │
│     - Verify Token: 脚本提示的值        │
│     - 勾选 messages                     │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│  5. 测试接入 (2 分钟)                   │
│     ./scripts/test_webhook.sh           │
│     或用真实 WhatsApp 发消息            │
└────────────┬────────────────────────────┘
             ↓
         ✅ 完成！
```

**总耗时：约 15 分钟**

---

## 🚂 部署到生产环境（可选）

本地测试成功后，一键部署到 Railway：

```bash
./scripts/deploy_railway.sh
```

脚本会自动：
- ✅ 检查 Railway CLI
- ✅ 登录验证
- ✅ 添加 PostgreSQL
- ✅ 设置所有环境变量
- ✅ 部署应用
- ✅ 生成永久域名
- ✅ 初始化数据库
- ✅ 健康检查

部署完成后，用 Railway 域名更新 Meta Webhook 配置即可。

---

## 📊 脚本功能对比

| 功能 | setup_whatsapp | start_local_test | test_webhook | deploy_railway |
|-----|----------------|------------------|--------------|----------------|
| 配置 API 凭证 | ✅ | - | - | - |
| 启动 FastAPI | - | ✅ | - | - |
| 启动 ngrok | - | ✅ | - | - |
| 测试健康检查 | - | - | ✅ | ✅ |
| 测试 Webhook | - | - | ✅ | - |
| 部署到云端 | - | - | - | ✅ |
| 初始化数据库 | - | - | - | ✅ |

---

## 🔍 脚本细节说明

### `setup_whatsapp.sh` 做了什么？

1. **验证环境**
   - 检查 `.env` 文件存在
   - 显示帮助信息

2. **交互式输入**
   - 引导你输入 Phone Number ID
   - 引导你输入 Access Token
   - 可选自定义 Verify Token

3. **自动更新配置**
   - 备份原 `.env` 到 `.env.backup`
   - 使用 `sed` 精确替换配置项
   - 显示配置摘要

4. **下一步提示**
   - 告诉你运行哪个脚本
   - 提示 Meta 配置步骤

### `start_local_test.sh` 做了什么？

1. **环境检查**
   - 检查项目目录
   - 检查 WhatsApp 配置（可选跳过使用 Mock）
   - 检查端口占用（可选自动终止）
   - 检查 ngrok 安装

2. **启动服务**
   - 激活虚拟环境
   - 后台启动 FastAPI（PID 保存到 logs/app.pid）
   - 等待服务就绪
   - 健康检查验证

3. **启动 ngrok**
   - 后台启动 ngrok（PID 保存到 logs/ngrok.pid）
   - 自动获取公网 URL
   - 显示 Webhook URL

4. **实时日志**
   - 显示服务状态
   - 显示下一步操作
   - 尾随显示日志（Ctrl+C 停止查看，服务继续运行）

### `test_webhook.sh` 做了什么？

1. **选择环境**
   - 本地 (localhost:8000)
   - ngrok（自动检测或手动输入）
   - Railway（输入生产域名）

2. **自动化测试**
   - **测试 1**: 健康检查 (`/health`)
   - **测试 2**: Webhook 验证（GET 请求）
   - **测试 3**: 模拟消息（测试端点）
   - **测试 4**: 医生查询（完整流程）

3. **结果报告**
   - 显示每个测试的结果（✅/❌）
   - 提供故障排查提示
   - 显示下一步操作

### `deploy_railway.sh` 做了什么？

1. **前置检查**
   - 检查 Railway CLI 安装
   - 检查登录状态
   - 检查项目初始化
   - 检查 WhatsApp 配置

2. **数据库配置**
   - 检查 PostgreSQL 服务
   - 可选添加 PostgreSQL

3. **环境变量设置**
   - 从 `.env` 读取所有变量
   - 批量设置到 Railway
   - 跳过未配置的变量
   - 设置生产环境配置

4. **部署**
   - 运行 `railway up`
   - 生成域名
   - 初始化数据库
   - 健康检查

5. **完成提示**
   - 显示域名和 Webhook URL
   - 提供下一步操作指引
   - 保存域名到 `.railway_domain`

---

## 🛡️ 安全特性

所有脚本都内置了安全检查：

- ✅ **备份保护**：修改配置前自动备份
- ✅ **验证检查**：输入不能为空
- ✅ **确认提示**：关键操作前需要确认
- ✅ **错误处理**：遇到错误自动中止
- ✅ **日志记录**：所有操作都有日志

---

## 📝 日志文件说明

脚本运行会生成以下日志：

```
logs/
├── app.log          # FastAPI 应用日志
├── ngrok.log        # ngrok 隧道日志
├── app.pid          # FastAPI 进程 ID
└── ngrok.pid        # ngrok 进程 ID
```

停止服务：
```bash
# 停止 FastAPI
kill $(cat logs/app.pid)

# 停止 ngrok
kill $(cat logs/ngrok.pid)

# 或一键停止所有
lsof -ti:8000 | xargs kill -9 && pkill ngrok
```

---

## 🆘 常见问题速查

### Q1: 脚本报错 "Permission denied"

```bash
chmod +x scripts/*.sh
```

### Q2: ngrok URL 每次都变化怎么办？

**临时方案**：注册 ngrok 免费账号，获取固定域名

**推荐方案**：部署到 Railway，永久域名

### Q3: Temporary Access Token 过期了

重新运行：
```bash
./scripts/setup_whatsapp.sh
```

输入新的 Token，然后重启服务。

### Q4: 想切换到生产 API

修改 `.env` 中的 API Key（去掉 `your_` 占位符），重启服务即可。

### Q5: Railway 部署失败

查看错误日志：
```bash
railway logs --tail
```

常见原因：
- 环境变量未设置
- PostgreSQL 服务未启动
- 代码有语法错误

---

## 🎓 学习路径

1. **第 1 天**：理解 WhatsApp API 流程
   - 阅读 [WHATSAPP_QUICKSTART.md](docs/WHATSAPP_QUICKSTART.md)
   - 运行 `setup_whatsapp.sh`
   - 本地测试成功

2. **第 2 天**：熟悉项目代码
   - 查看 [src/whatsapp/handler.py](src/whatsapp/handler.py)
   - 查看 [src/search/aggregator.py](src/search/aggregator.py)
   - 修改欢迎消息试试

3. **第 3 天**：部署到生产环境
   - 运行 `deploy_railway.sh`
   - 配置生产 Webhook
   - 添加更多测试用户

4. **第 4 天**：优化和监控
   - 查看日志分析
   - 调整缓存策略
   - 监控 API 成本

---

## 📚 相关资源

### 官方文档

- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)
- [OpenAI API](https://platform.openai.com/docs)
- [Google Places API](https://developers.google.com/maps/documentation/places)
- [Railway Docs](https://docs.railway.app/)

### 项目文档

- [README.md](README.md) - 项目总览
- [WHATSAPP_QUICKSTART.md](docs/WHATSAPP_QUICKSTART.md) - 快速接入
- [STEP_BY_STEP_GUIDE.md](STEP_BY_STEP_GUIDE.md) - 完整指南
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 命令速查
- [TESTING.md](TESTING.md) - 测试指南

---

## ✅ 验收清单

完成 WhatsApp 接入的标志：

- [ ] 运行 `setup_whatsapp.sh` 成功
- [ ] 运行 `start_local_test.sh` 成功显示 ngrok URL
- [ ] Meta Webhook 验证显示绿色勾号
- [ ] `messages` 事件已订阅
- [ ] 运行 `test_webhook.sh` 全部通过
- [ ] WhatsApp 发送 "你好" 收到欢迎消息
- [ ] WhatsApp 发送 "李医生" 收到评价汇总
- [ ] 日志显示完整处理流程（搜索→分析→缓存→返回）

**全部 ✅ = 接入成功！可以部署到生产环境了！**

---

## 🎉 下一步

接入成功后，你可以：

1. **添加更多功能**
   - 医院筛选
   - 地区搜索
   - 评分排序

2. **优化性能**
   - 调整缓存策略
   - 批量处理优化
   - 添加 Redis

3. **扩展用户**
   - 添加更多测试用户
   - 申请正式 WhatsApp 号码
   - 提交 Meta 商业验证

4. **监控运营**
   - 设置告警
   - 成本监控
   - 用户行为分析

---

**恭喜！你现在拥有了一套完整的 WhatsApp 接入工具链！🎊**

如有问题，查看 [QUICK_REFERENCE.md](QUICK_REFERENCE.md) 或项目文档。
