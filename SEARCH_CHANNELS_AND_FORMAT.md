# 搜索渠道和输出格式说明

## 📊 搜索渠道优先级

### 1️⃣ 缓存（第一优先级）
- **来源**: PostgreSQL 数据库
- **优先级**: 最高
- **TTL**: 7 天（热门医生）/ 3 天（冷门医生）
- **命中率**: 热门医生 ~90%，冷门医生 ~30%

### 2️⃣ Outscraper - Google Maps 评价（第二优先级）
- **来源**: Google Maps 评价
- **搜索方式**: 关键词搜索（`reviewsQuery` 参数）
- **覆盖范围**: 所有包含医生名字的 Google Maps 评价
- **数量限制**: 20 条/次
- **成本**: ~$0.02/次搜索
- **特点**:
  - ✅ 结构化数据（评分、日期、作者）
  - ✅ 关键词精准过滤
  - ✅ 高质量评价

### 3️⃣ ChatGPT-4o-mini Web Search（第三优先级）
- **来源**: Facebook 评论 + 论坛讨论
- **搜索方式**: OpenAI Web Search API
- **覆盖范围**:
  - Facebook 帖子和评论区
  - 马来西亚医疗论坛（Lowyat, Cari 等）
  - 其他患者讨论平台
- **数量限制**: 5-10 条/次
- **成本**: ~$0.001/次搜索（极低）
- **特点**:
  - ✅ 可以访问动态内容（Facebook）
  - ✅ 智能提取和总结
  - ⚠️ 需要 OpenAI API 支持 web_search_preview

---

## 📋 标准输出格式

所有搜索渠道统一使用以下格式：

### 评价对象格式

```json
{
  "text": "患者的完整评价内容",
  "rating": 5,
  "author_name": "患者姓名",
  "review_date": "2024-01-15",
  "url": "https://maps.google.com/...",
  "source": "google_maps",
  "place_name": "Hospital Name"
}
```

### 字段说明

| 字段 | 类型 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| `text` | string | ✅ | 评价内容 | "Dr. Nicholas is very professional..." |
| `rating` | int/null | ⚪ | 评分（1-5分）| 5 |
| `author_name` | string | ⚪ | 患者姓名 | "John Doe" |
| `review_date` | string | ⚪ | 发布日期（YYYY-MM-DD）| "2024-01-15" |
| `url` | string | ⚪ | 评价链接 | "https://..." |
| `source` | string | ✅ | 数据来源 | "google_maps" / "facebook" / "forum" |
| `place_name` | string | ⚪ | 地点名称（仅 Google Maps）| "KPJ Healthcare" |

### 数据来源标识

| source 值 | 说明 | 来自哪个模块 |
|-----------|------|-------------|
| `google_maps` | Google Maps 评价 | Outscraper |
| `facebook` | Facebook 评论 | ChatGPT |
| `forum` | 论坛讨论 | ChatGPT |
| `chatgpt_web_search` | ChatGPT 搜索（未分类）| ChatGPT |

---

## 🔄 完整搜索流程

```
1. 用户请求: "Dr. Nicholas Lim Lye Tak"
         ↓
2. 生成 doctor_id: md5(normalize("nicholas lim lye tak"))
         ↓
3. 检查缓存
   ├─ 命中 → 直接返回缓存结果 ✅
   └─ 未命中 → 继续执行搜索
         ↓
4. Outscraper 搜索（并行）
   ├─ 搜索 "Dr. Nicholas Lim Lye Tak Malaysia"
   ├─ 使用 reviewsQuery="Dr. Nicholas Lim Lye Tak"
   └─ 返回: 10 条 Google Maps 评价
         ↓
5. ChatGPT 搜索（并行）
   ├─ 搜索 "Dr. Nicholas Lim Lye Tak Malaysia patient reviews Facebook forum"
   ├─ 使用 web_search_preview 工具
   └─ 返回: 3 条 Facebook/论坛评价
         ↓
6. 合并结果
   ├─ 去重（基于 text + source）
   ├─ 按来源分组统计
   └─ 总计: 13 条评价
         ↓
7. 缓存结果（TTL: 7天）
         ↓
8. 返回用户
```

---

## 📦 API 响应格式

### 成功响应

```json
{
  "doctor_name": "Dr. Nicholas Lim Lye Tak",
  "doctor_id": "a4cca908841befde3ad045195b92e321",
  "reviews": [
    {
      "text": "Dr. Nicholas is very professional and caring...",
      "rating": 5,
      "author_name": "John Doe",
      "review_date": "2024-01-15",
      "url": "https://maps.google.com/...",
      "source": "google_maps",
      "place_name": "KPJ Specialist Hospital"
    },
    {
      "text": "Had a great experience with Dr. Nicholas...",
      "rating": null,
      "author_name": "Sarah Lee",
      "review_date": "2024-02-20",
      "url": "https://facebook.com/...",
      "source": "facebook",
      "place_name": null
    }
  ],
  "total_count": 13,
  "google_maps_count": 10,
  "facebook_forums_count": 3,
  "chatgpt_summary": "Dr. Nicholas Lim is well-regarded for his professionalism and patient care. Most reviews are positive.",
  "source": "aggregated",
  "cached": false
}
```

### 缓存命中响应

```json
{
  "doctor_name": "Dr. Nicholas Lim Lye Tak",
  "doctor_id": "a4cca908841befde3ad045195b92e321",
  "reviews": [...],
  "total_count": 13,
  "source": "cache",
  "cached": true
}
```

### 无结果响应

```json
{
  "doctor_name": "Dr. Unknown Doctor",
  "doctor_id": "...",
  "reviews": [],
  "total_count": 0,
  "google_maps_count": 0,
  "facebook_forums_count": 0,
  "message": "未找到评价，建议尝试不同的医生名字拼写"
}
```

### 错误响应

```json
{
  "doctor_name": "Dr. Nicholas Lim",
  "reviews": [],
  "total_count": 0,
  "error": "Outscraper API rate limit exceeded",
  "error_details": {
    "outscraper": "Rate limit exceeded",
    "chatgpt": "Success (3 reviews)"
  }
}
```

---

## ⚙️ 配置参数

### Outscraper 配置

```python
# src/search/outscraper_client.py

OUTSCRAPER_CONFIG = {
    "reviewsLimit": 20,           # 每次搜索最多返回 20 条评价
    "language": "en",             # 英文评价
    "region": "MY",               # 马来西亚地区
    "reviewsQuery": doctor_name   # 关键词过滤（核心功能）
}
```

### ChatGPT 配置

```python
# src/search/chatgpt_search.py

CHATGPT_CONFIG = {
    "model": "gpt-4o-mini",              # 使用 mini 版本（便宜 17 倍）
    "temperature": 0.3,                  # 降低随机性
    "search_context_size": "medium",     # 搜索范围：medium
    "tools": [
        {
            "type": "web_search_preview"  # 启用 web 搜索
        }
    ]
}
```

### 缓存配置

```python
# .env

CACHE_DEFAULT_TTL_DAYS=7         # 默认缓存 7 天
CACHE_HOT_DOCTOR_TTL_DAYS=7      # 热门医生缓存 7 天
CACHE_COLD_DOCTOR_TTL_DAYS=3     # 冷门医生缓存 3 天
```

---

## 🔧 字段映射表

不同数据源的原始字段如何映射到标准格式：

### Outscraper → 标准格式

| Outscraper 字段 | 标准字段 | 转换 |
|----------------|---------|------|
| `review_text` | `text` | 直接映射 |
| `review_rating` | `rating` | 直接映射（1-5） |
| `author_title` | `author_name` | 直接映射 |
| `review_datetime_utc` | `review_date` | 直接映射（YYYY-MM-DD） |
| `google_maps_url` | `url` | 来自 place 对象 |
| - | `source` | 固定值 "google_maps" |
| `name` (place) | `place_name` | 来自 place 对象 |

### ChatGPT → 标准格式

| ChatGPT 返回字段 | 标准字段 | 转换 |
|-----------------|---------|------|
| `text` | `text` | 直接映射 |
| `rating` | `rating` | 直接映射（可能为 null） |
| `author_name` / `author` | `author_name` | 优先使用 author_name |
| `review_date` | `review_date` | 直接映射（YYYY-MM-DD） |
| `url` | `url` | 直接映射 |
| `source` | `source` | 直接映射（如 "facebook", "forum"） |
| - | `place_name` | null（不适用） |

---

## 📊 统计字段说明

完整响应中包含的统计信息：

```json
{
  "total_count": 13,               // 总评价数
  "google_maps_count": 10,         // Google Maps 评价数
  "facebook_forums_count": 3,      // Facebook + 论坛评价数
  "chatgpt_summary": "...",        // ChatGPT 生成的总结
  "source": "aggregated",          // 数据来源标识
  "cached": false                  // 是否来自缓存
}
```

---

## 🎯 使用示例

### Python 代码示例

```python
from src.search.aggregator import search_aggregator

# 搜索医生评价
result = await search_aggregator.search_doctor_reviews(
    doctor_name="Dr. Nicholas Lim Lye Tak",
    location="Malaysia"
)

# 访问结果
print(f"找到 {result['total_count']} 条评价")
print(f"  - Google Maps: {result['google_maps_count']} 条")
print(f"  - Facebook/论坛: {result['facebook_forums_count']} 条")

# 遍历评价
for review in result['reviews']:
    print(f"\n来源: {review['source']}")
    print(f"评分: {review['rating']}")
    print(f"作者: {review['author_name']}")
    print(f"日期: {review['review_date']}")
    print(f"内容: {review['text'][:100]}...")
    print(f"链接: {review['url']}")
```

### 输出示例

```
找到 13 条评价
  - Google Maps: 10 条
  - Facebook/论坛: 3 条

来源: google_maps
评分: 5
作者: John Doe
日期: 2024-01-15
内容: Dr. Nicholas is very professional and caring. He took time to explain everything...
链接: https://maps.google.com/...

来源: facebook
评分: None
作者: Sarah Lee
日期: 2024-02-20
内容: Had a great experience with Dr. Nicholas at KPJ. Highly recommended!
链接: https://facebook.com/...
```

---

## ⚠️ 重要注意事项

### 1. ChatGPT Web Search 限制

**当前状态**: OpenAI 的 `web_search_preview` API 可能需要特定权限或 API 版本。

如果 `responses.create` API 不可用，代码会自动降级到普通 `chat.completions`，此时：
- ❌ 无法进行实时网络搜索
- ⚠️ 只能返回 ChatGPT 训练数据中的信息
- 📅 信息可能已过时

**解决方案**:
1. 确认 OpenAI API 账号支持 web search
2. 或者集成第三方搜索 API（Bing Search API, Google Custom Search）

### 2. 数据质量

不同渠道的数据质量：

| 渠道 | 结构化程度 | 完整性 | 可靠性 |
|------|-----------|-------|-------|
| **Google Maps** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Facebook** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **论坛** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |

### 3. 成本控制

- ✅ 使用缓存可节省 70-90% API 成本
- ✅ GPT-4o-mini 比 GPT-4o 便宜 17 倍
- ✅ Outscraper 关键词搜索避免无效 API 调用

---

## 📚 相关文档

- [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) - 实现总结
- [TECHNICAL_DECISIONS.md](./TECHNICAL_DECISIONS.md) - 技术决策
- [README.md](./README.md) - 项目概述

---

**更新日期**: 2025-10-31
**版本**: 1.0
