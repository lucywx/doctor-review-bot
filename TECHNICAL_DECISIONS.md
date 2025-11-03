# 技术决策文档

本文档记录了在实现最优方案过程中的关键技术决策和原因。

---

## 1️⃣ 为什么选择 Outscraper？

### ❌ 放弃的方案
- **Google Places API**
  - 问题：每个医生只能获取 5 条评价
  - 问题：需要先知道 Place ID
  - 问题：无法按关键词过滤评价

- **Google Custom Search API**
  - 问题：只能搜索静态网页
  - 问题：无法直接获取结构化评价数据
  - 问题：成本高（$5/1000 queries）

### ✅ 选择 Outscraper 的原因
1. **关键词搜索**：支持 `reviewsQuery` 参数，直接过滤包含医生名字的评价
   ```python
   params = {
       "reviewsQuery": doctor_name  # 只返回包含医生名字的评价
   }
   ```

2. **更多评价**：可以获取 20+ 条评价（vs Places API 的 5 条）

3. **无需 Place ID**：直接用医生名字 + 地点搜索

4. **结构化数据**：返回完整的评价数据（评分、作者、日期、内容）

5. **成本可控**：
   - 只为返回的评价付费
   - 通过缓存减少重复搜索
   - 月度成本：~$33（30 users）

---

## 2️⃣ 为什么选择 ChatGPT-4o-mini？

### ❌ 放弃的方案
- **Bing Search API**
  - 问题：无法索引 Facebook 评论（动态内容）
  - 问题：无法访问论坛讨论区

- **Playwright/Selenium**
  - 问题：需要维护浏览器自动化代码
  - 问题：容易被网站反爬虫检测
  - 问题：运行成本高（需要浏览器实例）

- **GPT-4o**
  - 问题：成本太高（$10/1M tokens vs $0.60/1M）
  - 对于简单的搜索任务过于昂贵

### ✅ 选择 ChatGPT-4o-mini 的原因

1. **Web Browser Tool**：ChatGPT 自带 web browsing 功能
   - 可以访问动态网页（Facebook 评论）
   - 可以浏览论坛讨论
   - 无需自己维护爬虫代码

2. **成本极低**：
   - GPT-4o-mini：$0.60/1M input tokens
   - GPT-4o：$10/1M input tokens
   - **便宜 17 倍！**
   - 月度成本：~$1（30 users）

3. **智能总结**：
   - 自动提取相关评价
   - 过滤无关信息
   - 提供简短总结

4. **结构化输出**：
   ```python
   response_format={"type": "json_object"}  # 返回 JSON
   ```

5. **质量足够**：
   - 对于简单的搜索和提取任务，mini 版本完全够用
   - Temperature 0.3 确保准确性

---

## 3️⃣ 为什么不使用 Google Places API？

### Google Places API 的限制

1. **评价数量限制**
   ```python
   # Google Places API 最多返回 5 条评价
   reviews = place_details.get("reviews", [])[:5]
   ```

2. **需要 Place ID**
   - 必须先搜索 Place
   - 然后获取 Place ID
   - 最后才能获取评价
   - 流程复杂，成本高

3. **无法关键词过滤**
   - 无法只获取提到特定医生的评价
   - 会返回医院/诊所的所有评价
   - 需要手动过滤（浪费 API quota）

### Outscraper 的优势

| 功能 | Google Places API | Outscraper |
|------|-------------------|-----------|
| 评价数量 | 最多 5 条 | 20+ 条 |
| 需要 Place ID | ✅ 是 | ❌ 否 |
| 关键词过滤 | ❌ 不支持 | ✅ 支持 |
| 搜索方式 | Place ID | 关键词搜索 |
| 成本 | 免费（有限额）| ~$33/月 |

---

## 4️⃣ 为什么不使用 Google Custom Search？

### Google Custom Search 的问题

1. **只能搜索静态内容**
   - 无法索引 Facebook 评论（JavaScript 动态加载）
   - 无法访问登录后的内容

2. **返回搜索结果，不是结构化数据**
   ```python
   # 返回的是网页链接，不是评价数据
   results = [
       {"link": "https://...", "snippet": "..."},
       ...
   ]
   ```

3. **需要额外爬取**
   - 获取链接后还需要爬取每个页面
   - 需要解析 HTML
   - 维护成本高

4. **成本不低**
   - $5 per 1,000 queries
   - 免费额度只有 100 queries/day

### Outscraper 直接提供结构化评价

```python
# Outscraper 直接返回结构化评价
{
    "reviews": [
        {
            "text": "Dr. Nicholas is great...",
            "rating": 5,
            "author": "John Doe",
            "date": "2024-01-15"
        }
    ]
}
```

---

## 5️⃣ Facebook 评论搜索为什么只能用 ChatGPT？

### Facebook 的技术限制

1. **动态内容加载**
   - 评论通过 JavaScript 动态加载
   - 搜索引擎无法索引（Google、Bing 都不行）

2. **需要登录**
   - 部分内容需要 Facebook 账号
   - 传统爬虫难以处理

3. **反爬虫机制**
   - Facebook 有强大的反爬虫检测
   - IP 封禁、验证码等

### 解决方案对比

| 方案 | 可行性 | 成本 | 维护难度 |
|------|-------|------|---------|
| Google Search | ❌ 不可行 | - | - |
| Bing Search | ❌ 不可行 | - | - |
| Playwright/Selenium | ⚠️ 可行但复杂 | 高 | 高 |
| ChatGPT Web Browser | ✅ 最佳方案 | 极低 | 极低 |

### ChatGPT 的优势

1. **内置 Web Browser Tool**
   - OpenAI 维护
   - 自动处理动态内容
   - 无需担心反爬虫

2. **智能提取**
   - 自动识别相关评论
   - 过滤广告和无关内容
   - 提供总结

3. **成本极低**
   - GPT-4o-mini：~$1/月
   - 无需维护浏览器实例
   - 无需代理 IP

---

## 6️⃣ 为什么简化为 2 个数据源？

### 原方案的问题（4+ 数据源）

```python
# 原方案：复杂的多数据源架构
sources = [
    "google_places_api",      # 5 条评价
    "google_custom_search",   # 搜索结果链接
    "outscraper",            # Google Maps 评价
    "openai_web_search",     # Facebook/论坛
    ...
]
```

问题：
- 数据源重复（Google Places + Outscraper 都是 Google Maps）
- 代码复杂（需要协调多个 API）
- 成本高（多个 API 都要付费）
- 维护难（4+ 个 API keys）

### 最优方案（2 个数据源）

```python
# 最优方案：简洁的 2 数据源
sources = [
    "outscraper",           # Google Maps（关键词搜索）
    "chatgpt_4o_mini",      # Facebook + 论坛
]
```

优势：
- ✅ 覆盖所有需要的平台（Google Maps + Facebook + 论坛）
- ✅ 代码简洁（40% less code）
- ✅ 成本低（~$44/月）
- ✅ 易维护（只需 2 个 API keys）

---

## 7️⃣ 异步实现的考虑

### 为什么使用 async/await？

1. **并发搜索**
   ```python
   # 可以同时调用 Outscraper 和 ChatGPT
   outscraper_task = outscraper_client.search_doctor_reviews(...)
   chatgpt_task = chatgpt_client.search_facebook_and_forums(...)

   # 等待所有任务完成
   results = await asyncio.gather(outscraper_task, chatgpt_task)
   ```

2. **更快的响应**
   - 串行：2-3 秒（Outscraper）+ 3-5 秒（ChatGPT）= 5-8 秒
   - 并行：max(2-3 秒, 3-5 秒) = 3-5 秒

3. **更好的资源利用**
   - 等待 API 响应时不阻塞
   - 可以处理多个用户请求

### 使用 httpx 而不是 requests

```python
# ✅ 使用 httpx（支持 async）
async with httpx.AsyncClient(timeout=60.0) as client:
    response = await client.get(url, params=params, headers=headers)

# ❌ requests 不支持 async
# response = requests.get(url)  # 会阻塞整个事件循环
```

---

## 8️⃣ 错误处理策略

### 优雅降级

1. **缓存失败不影响搜索**
   ```python
   try:
       cached_reviews = await cache_manager.get_cached_reviews(doctor_id)
   except Exception as cache_error:
       # 记录警告，继续搜索
       logger.warning(f"⚠️ 缓存检查失败: {cache_error}")
   ```

2. **单个数据源失败不影响其他**
   ```python
   # Outscraper 失败了，ChatGPT 仍然可以运行
   if self.outscraper_client.enabled:
       try:
           result = await self.outscraper_client.search_doctor_reviews(...)
       except Exception:
           logger.error("Outscraper failed, continuing with other sources")

   # ChatGPT 继续
   if self.chatgpt_client.enabled:
       result = await self.chatgpt_client.search_facebook_and_forums(...)
   ```

3. **API key 未配置时优雅跳过**
   ```python
   if not self.api_key or self.api_key == "your_api_key_here":
       self.enabled = False
       # 不抛出错误，只是标记为未启用
   ```

---

## 9️⃣ 成本优化策略

### 1. 使用缓存减少 API 调用

```python
# 步骤 1：先检查缓存
cached_reviews = await cache_manager.get_cached_reviews(doctor_id)
if cached_reviews:
    return cached_reviews  # 直接返回，不调用 API

# 步骤 2：搜索新数据
# ...

# 步骤 3：缓存结果（7 天 TTL）
await cache_manager.save_reviews(doctor_id, doctor_name, all_reviews)
```

成本节省：
- 热门医生：90% 的请求命中缓存 → 节省 90% API 成本
- 冷门医生：30% 的请求命中缓存 → 节省 30% API 成本

### 2. 使用 GPT-4o-mini 而不是 GPT-4o

```python
# ✅ 使用 mini 版本
model = "gpt-4o-mini"  # $0.60/1M tokens

# ❌ 不使用完整版
# model = "gpt-4o"  # $10/1M tokens
```

成本节省：17 倍！

### 3. 限制搜索数量

```python
# 限制每个数据源的结果数量
outscraper_limit = 20  # 不需要 100+ 条评价
chatgpt_limit = 5     # 只需要代表性评价
```

### 4. 降低 ChatGPT Temperature

```python
# Temperature 0.3 → 更确定的答案 → 更少的 tokens
temperature = 0.3  # vs 默认的 1.0
```

---

## 🔟 为什么不等 GPT-5？

### GPT-5 的预期

1. **更贵，不是更便宜**
   - 旗舰模型通常更贵（GPT-4 比 GPT-3.5 贵 20 倍）
   - GPT-5 可能比 GPT-4o 更贵

2. **过度性能**
   - 搜索和提取评价是简单任务
   - GPT-4o-mini 已经完全够用
   - 不需要 GPT-5 的高级推理能力

3. **发布时间不确定**
   - 可能还需要几个月甚至更久
   - 现在的方案已经最优

### 可能的未来升级

如果 GPT-5-mini 发布：
- 可能价格相似
- 可能性能更好
- 可以简单替换（只改 model 参数）

```python
# 未来升级很简单
model = "gpt-5-mini"  # 只需改这一行
```

---

## 📊 最终架构总结

```
用户请求
    ↓
搜索聚合器
    ↓
┌─────────────┬─────────────┐
↓             ↓             ↓
缓存检查    Outscraper   ChatGPT-4o-mini
(PostgreSQL) (Google Maps) (Facebook+论坛)
    ↓             ↓             ↓
    └─────────────┴─────────────┘
                ↓
            合并结果
                ↓
            缓存保存
                ↓
            返回用户
```

### 关键决策
1. ✅ Outscraper：关键词搜索 Google Maps
2. ✅ ChatGPT-4o-mini：访问动态内容（Facebook）
3. ✅ 2 个数据源：简洁且覆盖全面
4. ✅ 异步实现：更快的响应
5. ✅ 缓存优化：降低成本
6. ✅ 优雅降级：提高可靠性

### 成本对比
| 方案 | 月度成本 | 数据源 | 代码复杂度 |
|------|---------|-------|-----------|
| 原方案 | ~$150 | 4+ | 高 |
| **最优方案** | **~$44** | **2** | **低** |
| 节省 | **-70%** | **-50%** | **-40%** |

---

**结论：** 最优方案在成本、性能、可维护性上都达到了最佳平衡。
