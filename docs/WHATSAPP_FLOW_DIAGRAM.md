# WhatsApp API 接入流程图

> 可视化展示完整的接入和消息处理流程

---

## 📊 完整接入流程

```
┌─────────────────────────────────────────────────────────────────┐
│                     WhatsApp API 接入流程                        │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│ 1. Meta 后台 │  你的操作：创建应用、获取凭证
└──────┬───────┘
       │
       ↓
┌───────────────────────────────────────────────────────────┐
│  Meta for Developers                                      │
│  ├─ My Apps → Create App (Business)                       │
│  ├─ Add WhatsApp Product                                  │
│  └─ API Setup:                                            │
│      ├─ Phone Number ID: 109361185504724                  │
│      ├─ Temporary Access Token: EAAGm7J...               │
│      └─ Add Test Phone Number: +8613800138000            │
└───────────────────────────────────────────────────────────┘
       │
       ↓
┌──────────────┐
│ 2. 本地配置  │  运行脚本：./scripts/setup_whatsapp.sh
└──────┬───────┘
       │
       ↓
┌───────────────────────────────────────────────────────────┐
│  配置脚本做什么？                                          │
│  ├─ 交互式输入凭证                                         │
│  ├─ 备份原 .env 文件                                       │
│  ├─ 更新环境变量：                                         │
│  │   WHATSAPP_PHONE_NUMBER_ID=109361185504724           │
│  │   WHATSAPP_ACCESS_TOKEN=EAAGm7J...                   │
│  │   VERIFY_TOKEN=my_secret_verify_token_123            │
│  └─ 显示下一步提示                                         │
└───────────────────────────────────────────────────────────┘
       │
       ↓
┌──────────────┐
│ 3. 启动服务  │  运行脚本：./scripts/start_local_test.sh
└──────┬───────┘
       │
       ↓
┌───────────────────────────────────────────────────────────┐
│  启动脚本做什么？                                          │
│  ├─ 启动 FastAPI (localhost:8000)                         │
│  │   ├─ 加载 .env 配置                                    │
│  │   ├─ 连接数据库                                        │
│  │   └─ 注册 Webhook 路由                                 │
│  └─ 启动 ngrok                                            │
│      ├─ 建立隧道: localhost:8000 → 公网                   │
│      └─ 生成 URL: https://abc123.ngrok-free.app          │
└───────────────────────────────────────────────────────────┘
       │
       ↓
┌──────────────┐
│ 4. 配置回调  │  Meta 后台：Configuration → Webhook
└──────┬───────┘
       │
       ↓
┌───────────────────────────────────────────────────────────┐
│  Meta Webhook 配置                                        │
│  ├─ Callback URL:                                         │
│  │   https://abc123.ngrok-free.app/webhook/whatsapp     │
│  ├─ Verify Token:                                         │
│  │   my_secret_verify_token_123                          │
│  └─ 点击 "Verify and Save"                                │
└───────────────────────────────────────────────────────────┘
       │
       ↓
┌──────────────┐
│ 5. 验证流程  │  Meta → 你的服务器
└──────┬───────┘
       │
       ↓
┌───────────────────────────────────────────────────────────┐
│  Webhook 验证（GET 请求）                                  │
│                                                           │
│  Meta 发送:                                               │
│  GET /webhook/whatsapp?                                   │
│      hub.mode=subscribe                                   │
│      hub.verify_token=my_secret_verify_token_123         │
│      hub.challenge=RANDOM_STRING                         │
│                                                           │
│  你的服务器:                                               │
│  1. 检查 verify_token 是否匹配                            │
│  2. 返回 challenge 值                                     │
│                                                           │
│  Meta 收到:                                               │
│  ✅ 绿色勾号 = 验证成功                                    │
└───────────────────────────────────────────────────────────┘
       │
       ↓
┌──────────────┐
│ 6. 订阅事件  │  Meta 后台：勾选 messages
└──────┬───────┘
       │
       ↓
┌───────────────────────────────────────────────────────────┐
│  Webhook Fields                                           │
│  ☑️ messages  ← 必须勾选                                   │
│  ☐ message_status                                         │
│  ☐ messaging_postbacks                                    │
└───────────────────────────────────────────────────────────┘
       │
       ↓
┌──────────────┐
│ 7. 测试消息  │  运行脚本：./scripts/test_webhook.sh
└──────┬───────┘
       │
       ↓
       ✅ 接入完成！
```

---

## 🔄 消息处理流程

```
┌─────────────────────────────────────────────────────────────────┐
│                     用户发送消息后的处理流程                       │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│ 用户 WhatsApp│  发送消息："李医生"
└──────┬───────┘
       │
       ↓
┌───────────────────────────────────────────────────────────┐
│  WhatsApp Business API (Meta 云端)                        │
│  ├─ 接收用户消息                                           │
│  ├─ 封装为 Webhook Payload                                │
│  └─ POST 到你的 Callback URL                               │
└───────────────────────────────────────────────────────────┘
       │
       ↓  POST /webhook/whatsapp
       │
┌───────────────────────────────────────────────────────────┐
│  你的 FastAPI 服务器                                        │
│  (src/whatsapp/routes.py)                                 │
│                                                           │
│  async def receive_webhook(request):                      │
│    1. 解析 JSON body                                       │
│    2. 提取 from_number, message_text                       │
│    3. 创建异步任务处理                                      │
│    4. 立即返回 200 OK (不阻塞)                             │
└───────────────────────────────────────────────────────────┘
       │
       ↓  异步处理
       │
┌───────────────────────────────────────────────────────────┐
│  消息处理器 (src/whatsapp/handler.py)                      │
│                                                           │
│  async def process_message(from, text):                   │
│    ├─ 1. 检查用户配额 (50次/天)                            │
│    ├─ 2. 提取医生姓名                                       │
│    ├─ 3. 发送"正在搜索..."消息                              │
│    └─ 4. 调用搜索聚合器                                     │
└───────────────────────────────────────────────────────────┘
       │
       ↓
┌───────────────────────────────────────────────────────────┐
│  搜索聚合器 (src/search/aggregator.py)                     │
│                                                           │
│  async def search_doctor_reviews(doctor_name):            │
│    ├─ 1. 生成 doctor_id (hash)                            │
│    ├─ 2. 检查缓存                                          │
│    │    └─ 如果命中 → 直接返回                              │
│    ├─ 3. 并行调用搜索引擎：                                 │
│    │    ├─ Google Places API                              │
│    │    ├─ Facebook Graph API                             │
│    │    └─ Mock Searcher (开发模式)                        │
│    ├─ 4. 合并所有结果                                       │
│    └─ 5. 调用情感分析                                       │
└───────────────────────────────────────────────────────────┘
       │
       ↓
┌───────────────────────────────────────────────────────────┐
│  情感分析 (src/analysis/sentiment.py)                      │
│                                                           │
│  async def analyze_reviews(reviews):                      │
│    ├─ 1. 检查是否 Mock 模式                                │
│    ├─ 2. 批量调用 OpenAI API (10条/批)                     │
│    │    └─ GPT-4-turbo/GPT-5-mini                         │
│    ├─ 3. 解析 JSON 结果                                    │
│    └─ 4. 为每条评价添加 sentiment 字段                     │
│         (positive/negative/neutral)                       │
└───────────────────────────────────────────────────────────┘
       │
       ↓
┌───────────────────────────────────────────────────────────┐
│  缓存管理器 (src/cache/manager.py)                         │
│                                                           │
│  async def save_reviews(doctor_id, reviews):              │
│    ├─ 1. 保存到 doctors 表                                 │
│    ├─ 2. 保存到 reviews 表                                 │
│    └─ 3. 设置 TTL = 7 天                                   │
└───────────────────────────────────────────────────────────┘
       │
       ↓
┌───────────────────────────────────────────────────────────┐
│  消息格式化 (src/whatsapp/formatter.py)                    │
│                                                           │
│  def format_review_batch(batch, doctor_name, ...):        │
│    ├─ 1. 显示配额信息（首批）                               │
│    ├─ 2. 格式化评论列表：                                   │
│    │    📊 Monthly quota: 497/500 searches remaining      │
│    │                                                       │
│    │    🔍 李医生                                           │
│    │    Found 10 reviews                                   │
│    │                                                       │
│    │    1. "李医生非常专业..."                              │
│    │       📅 2024-10-15                                   │
│    │       🔗 https://...                                  │
│    │                                                       │
│    │    2. "等待时间较长..."                                │
│    │       📅 2024-10-10                                   │
│    │       🔗 https://...                                  │
│    └─ 3. 添加来源说明                                       │
└───────────────────────────────────────────────────────────┘
       │
       ↓
┌───────────────────────────────────────────────────────────┐
│  WhatsApp 客户端 (src/whatsapp/client.py)                  │
│                                                           │
│  async def send_message(to, message):                     │
│    ├─ 1. 构造 API 请求                                     │
│    │    POST https://graph.facebook.com/v18.0/          │
│    │         {phone_number_id}/messages                  │
│    ├─ 2. 设置 Authorization: Bearer {access_token}       │
│    └─ 3. 发送消息                                          │
└───────────────────────────────────────────────────────────┘
       │
       ↓
┌───────────────────────────────────────────────────────────┐
│  WhatsApp Business API                                    │
│  └─ 推送消息到用户 WhatsApp                                 │
└───────────────────────────────────────────────────────────┘
       │
       ↓
┌──────────────┐
│ 用户 WhatsApp│  收到格式化的评价汇总
└──────────────┘

总耗时：
├─ 缓存命中：< 500ms
└─ 缓存未命中：2-5s (取决于 API 响应)
```

---

## 🔍 数据流详解

### 1️⃣ Webhook Payload 示例

**用户发送 "李医生"，Meta 推送：**

```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "15550100",
              "phone_number_id": "109361185504724"
            },
            "contacts": [
              {
                "profile": {
                  "name": "Lucy"
                },
                "wa_id": "8613800138000"
              }
            ],
            "messages": [
              {
                "from": "8613800138000",
                "id": "wamid.xxx",
                "timestamp": "1696800000",
                "text": {
                  "body": "李医生"
                },
                "type": "text"
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}
```

### 2️⃣ 搜索结果示例

**从多个来源聚合：**

```json
[
  {
    "text": "李医生非常专业，态度很好，诊断准确",
    "source": "google_maps",
    "source_url": "https://maps.google.com/...",
    "rating": 5,
    "date": "2025-09-15"
  },
  {
    "text": "等待时间较长，但医生很耐心",
    "source": "facebook",
    "source_url": "https://facebook.com/...",
    "date": "2025-09-20"
  }
]
```

### 3️⃣ 情感分析结果

**OpenAI 分析后：**

```json
[
  {
    "text": "李医生非常专业，态度很好，诊断准确",
    "source": "google_maps",
    "source_url": "https://maps.google.com/...",
    "sentiment": "positive",  ← 新增字段
    "rating": 5,
    "date": "2025-09-15"
  },
  {
    "text": "等待时间较长，但医生很耐心",
    "source": "facebook",
    "source_url": "https://facebook.com/...",
    "sentiment": "neutral",  ← 新增字段
    "date": "2025-09-20"
  }
]
```

### 4️⃣ 返回给用户的消息

```
📊 李医生 - 评价汇总

✅ 正面评价 (1条)
1. 李医生非常专业，态度很好，诊断准确
   🗺️ Google Maps
   🔗 https://maps.google.com/...
   📅 2025-09-15

⚖️ 中性评价 (1条)
2. 等待时间较长，但医生很耐心
   👥 Facebook
   🔗 https://facebook.com/...
   📅 2025-09-20

💡 提示：信息来自公开评价，仅供参考
```

---

## 🛠️ 关键组件职责

### FastAPI 路由层
```python
# src/whatsapp/routes.py

@router.get("/whatsapp")    # Webhook 验证
@router.post("/whatsapp")   # 接收消息
@router.post("/whatsapp/test")  # 测试端点
```

### 消息处理层
```python
# src/whatsapp/handler.py

class MessageHandler:
    - 配额检查
    - 命令识别
    - 调用搜索
    - 日志记录
```

### 搜索聚合层
```python
# src/search/aggregator.py

class SearchAggregator:
    - 缓存检查
    - 并行搜索
    - 结果合并
    - 情感分析
```

### 情感分析层
```python
# src/analysis/sentiment.py

class SentimentAnalyzer:
    - OpenAI API 调用
    - 批量处理
    - Mock 模式
```

### 缓存管理层
```python
# src/cache/manager.py

class CacheManager:
    - 生成 doctor_id
    - 读取缓存
    - 保存结果
    - TTL 管理
```

---

## ⏱️ 性能指标

| 场景 | 响应时间 | API 调用 | 成本 |
|------|---------|---------|------|
| 缓存命中 | < 500ms | 0 | $0 |
| 首次查询 | 2-5s | Google + OpenAI | ~$0.01 |
| 热门医生 | < 1s | 0 | $0 |
| Mock 模式 | < 300ms | 0 | $0 |

---

## 🔐 安全检查点

```
用户输入 → 配额检查 → 输入清洗 → 业务处理
                ↓           ↓          ↓
            限流保护    SQL注入防护  异常捕获
```

---

这个流程图帮助你理解：
1. ✅ 如何从零开始接入 WhatsApp API
2. ✅ 消息是如何从用户到达你的服务器
3. ✅ 你的代码如何处理和响应消息
4. ✅ 每个组件的职责和数据流向

参考此图进行调试和优化！🚀
