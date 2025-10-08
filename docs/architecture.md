# 系统架构设计文档

## 1. 系统概述

Doctor Review Aggregation Bot 是一个基于 WhatsApp 的智能医生评价搜索系统，采用**多引擎实时聚合 + 智能缓存**的混合架构。

---

## 2. 架构设计原则

- **成本优先**：通过缓存最小化 API 调用
- **响应快速**：缓存命中 < 500ms，实时搜索 < 10s
- **可扩展性**：模块化设计，便于添加新数据源
- **合规性**：仅抓取公开数据，遵守各平台 ToS

---

## 3. 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户层                                │
│                   WhatsApp 客户端                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     接入层 (Gateway)                         │
│              WhatsApp Business Cloud API                     │
│                 - Webhook 接收消息                           │
│                 - 发送格式化回复                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   应用层 (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  消息处理模块 (Message Handler)                      │  │
│  │  - 解析用户输入                                       │  │
│  │  - 提取医生姓名                                       │  │
│  │  - 调用搜索引擎                                       │  │
│  │  - 格式化输出                                         │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                        │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  缓存管理模块 (Cache Manager)                        │  │
│  │  - 查询缓存数据库                                     │  │
│  │  - 检查缓存有效性 (valid_until)                      │  │
│  │  - 计算缓存命中率                                     │  │
│  └──────────────┬───────────────┬───────────────────────┘  │
│                 │ 缓存未命中    │ 缓存命中                  │
│                 ▼               ▼                            │
│  ┌──────────────────────┐  ┌──────────────────────────┐   │
│  │ 搜索聚合模块          │  │ 直接返回缓存结果         │   │
│  │ (Search Aggregator)   │  │                          │   │
│  └──────────────────────┘  └──────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   数据聚合层                                 │
│  ┌───────────────┐  ┌───────────────┐  ┌────────────────┐ │
│  │ Google Places │  │ Facebook Graph│  │ Web Scraper    │ │
│  │ API Module    │  │ API Module    │  │ (医院官网)     │ │
│  │               │  │               │  │                │ │
│  │ - 搜索医生    │  │ - 公开主页    │  │ - BeautifulSoup│ │
│  │ - 获取评分    │  │ - 公开群组    │  │ - Selenium     │ │
│  │ - 拉取评论    │  │ - 评论抓取    │  │ - 智能解析     │ │
│  └───────────────┘  └───────────────┘  └────────────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   AI 分析层                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  OpenAI GPT-4-turbo-mini                             │  │
│  │  - 情感分类（正面/负面/中性）                        │  │
│  │  - 提取关键信息                                       │  │
│  │  - 生成摘要                                           │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   存储层                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  PostgreSQL Database                                 │  │
│  │                                                       │  │
│  │  - doctor_reviews (缓存表)                           │  │
│  │  - search_logs (搜索日志)                            │  │
│  │  - user_sessions (用户会话)                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. 核心模块详解

### 4.1 消息处理模块 (Message Handler)

**职责**：
- 接收 WhatsApp webhook 请求
- 验证消息合法性
- 解析用户输入（医生姓名、地区等）
- 协调缓存和搜索模块
- 格式化输出结果

**流程**：
```python
def handle_message(message):
    # 1. 提取医生姓名
    doctor_name = extract_doctor_name(message)

    # 2. 查询缓存
    cached_result = cache_manager.get(doctor_name)
    if cached_result and is_valid(cached_result):
        return format_response(cached_result)

    # 3. 实时搜索
    search_results = search_aggregator.search(doctor_name)

    # 4. AI 分析
    analyzed_results = ai_analyzer.classify(search_results)

    # 5. 存入缓存
    cache_manager.save(doctor_name, analyzed_results)

    # 6. 返回结果
    return format_response(analyzed_results)
```

---

### 4.2 缓存管理模块 (Cache Manager)

**缓存策略**：
- **热数据**：7 天有效期（热门医生）
- **冷数据**：3 天有效期（普通医生）
- **失效策略**：超过 valid_until 自动失效

**缓存命中率目标**：
- 初期：40-50%
- 稳定期：60-70%

**实现逻辑**：
```python
def get_cached_review(doctor_id):
    result = db.query(
        "SELECT * FROM doctor_reviews WHERE doctor_id = %s AND valid_until > NOW()",
        (doctor_id,)
    )
    return result if result else None
```

---

### 4.3 搜索聚合模块 (Search Aggregator)

**并行搜索架构**：

```python
async def search_all_sources(doctor_name):
    tasks = [
        search_google_places(doctor_name),
        search_facebook(doctor_name),
        scrape_hospital_websites(doctor_name)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return merge_results(results)
```

**数据源优先级**：
1. Google Places（最可靠）
2. Facebook 公开页面
3. 医院官网

---

### 4.4 AI 分析模块 (AI Analyzer)

**任务**：
- 情感分类（正面/负面/中性）
- 提取核心观点
- 过滤垃圾评论

**Prompt 设计**：
```python
CLASSIFICATION_PROMPT = """
请分析以下医生评价，分类为：正面、负面或中性。

评价内容：{review_text}

输出格式：
{
  "sentiment": "positive/negative/neutral",
  "key_points": ["要点1", "要点2"],
  "confidence": 0.95
}
"""
```

---

## 5. 数据流图

### 5.1 缓存命中场景

```
用户输入 "张医生"
    ↓
查询缓存数据库
    ↓
找到有效缓存（valid_until > now）
    ↓
直接返回结果（< 500ms）
```

### 5.2 缓存未命中场景

```
用户输入 "李医生"
    ↓
查询缓存数据库
    ↓
缓存不存在/已过期
    ↓
并行调用 3 个搜索引擎
    ↓
汇总原始数据（10-50 条评论）
    ↓
调用 OpenAI 分析
    ↓
存入缓存（设置 valid_until）
    ↓
返回格式化结果（< 10s）
```

---

## 6. 性能指标

| 指标 | 目标值 |
|------|--------|
| 缓存命中响应时间 | < 500ms |
| 实时搜索响应时间 | < 10s |
| 并发处理能力 | 10 请求/秒 |
| 缓存命中率 | > 60% |
| API 错误率 | < 1% |

---

## 7. 容错设计

### 7.1 API 失败降级策略

```python
def search_with_fallback(doctor_name):
    try:
        return search_google_places(doctor_name)
    except GoogleAPIError:
        try:
            return search_facebook(doctor_name)
        except FacebookAPIError:
            return {"error": "所有搜索引擎暂时不可用"}
```

### 7.2 超时控制

- 单个 API 调用：5s 超时
- 总搜索时间：15s 超时
- AI 分析：10s 超时

---

## 8. 安全设计

### 8.1 访问控制

- WhatsApp webhook 签名验证
- 白名单用户机制（初期 30 人）
- 每用户每日查询限制（50 次）

### 8.2 数据脱敏

- 评论中的个人联系方式自动脱敏
- 不存储用户手机号
- 日志定期清理（30 天）

---

## 9. 监控与日志

### 9.1 关键指标监控

- API 调用次数和成本
- 缓存命中率
- 平均响应时间
- 错误率统计

### 9.2 日志记录

```python
# 搜索日志
{
  "timestamp": "2025-10-08T10:30:00Z",
  "user_id": "user_123",
  "doctor_name": "张医生",
  "cache_hit": false,
  "response_time_ms": 8500,
  "sources_used": ["google_places", "facebook"],
  "api_cost_usd": 0.015
}
```

---

## 10. 扩展性设计

### 10.1 添加新数据源

模块化设计允许快速接入新平台：

```python
# 新增数据源只需实现接口
class NewSourceSearcher(BaseSearcher):
    async def search(self, doctor_name):
        # 实现搜索逻辑
        pass
```

### 10.2 水平扩展

- 使用 Redis 共享缓存
- 多实例部署 + 负载均衡
- 数据库读写分离

---

## 11. 技术选型理由

| 组件 | 选型 | 理由 |
|------|------|------|
| Web 框架 | FastAPI | 异步支持、性能好、开发快 |
| 数据库 | PostgreSQL | 免费、稳定、支持复杂查询 |
| AI 模型 | GPT-4-turbo-mini | 性价比高、中文友好 |
| 部署平台 | Railway/Render | 免费额度、自动部署 |
| 消息平台 | WhatsApp Cloud API | 官方、稳定、免费额度充足 |

---

## 12. 版本规划

### v1.0（MVP）
- WhatsApp 基础交互
- Google Places 搜索
- 简单缓存机制
- 基础情感分类

### v2.0（增强版）
- Facebook 数据源
- 医院官网爬虫
- 高级缓存策略
- 多维度分析

### v3.0（未来）
- 多语言支持
- 语音输入
- 图表可视化
- 订阅提醒功能
