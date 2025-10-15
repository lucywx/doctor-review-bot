# Google Custom Search API 设置指南

## 为什么使用 Google Custom Search?

OpenAI web_search 的局限性:
- ❌ 只返回 5-10 条结果
- ❌ 无法控制搜索哪些网站
- ❌ 结果质量不稳定（优先医学目录，忽略社交媒体和论坛）

Google Custom Search 的优势:
- ✅ 可以指定搜索特定网站（Facebook, Lowyat, Cari论坛等）
- ✅ 返回更多相关结果
- ✅ 更好的控制和可预测性
- ✅ 结合 OpenAI 提取内容，发挥两者优势

## 设置步骤

### 1. 获取 Google API Key

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建或选择一个项目
3. 启用 "Custom Search API"
   - 在搜索栏搜索 "Custom Search API"
   - 点击 "Enable" 启用 API
4. 创建凭据
   - 左侧菜单 → "Credentials" (凭据)
   - 点击 "Create Credentials" → "API Key"
   - 复制生成的 API Key

### 2. 创建搜索引擎

1. 访问 [Google Programmable Search Engine](https://programmablesearchengine.google.com/)
2. 点击 "Add" 创建新的搜索引擎
3. 配置:
   - **Sites to search**: 选择 "Search the entire web"
   - **Name**: Doctor Review Search (或任意名称)
4. 创建后，点击 "Customize" → "Setup"
5. 在 "Search engine ID" 下找到你的搜索引擎 ID (类似 `abc123def456`)

### 3. 配置项目

将 API Key 和 Search Engine ID 添加到 `.env` 文件:

```env
# Google Custom Search API
GOOGLE_SEARCH_API_KEY=your_actual_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
```

### 4. 测试配置

运行测试脚本:

```bash
python test_google_search.py
```

预期输出:
```
✅ Google API Key configured
✅ Search Engine ID: abc123def456
🔍 Found 15 URLs from Google Search
✅ Extracted 8 reviews via OpenAI
```

## 工作原理

新的搜索流程:

```
1. 用户输入医生名字
   ↓
2. 检查缓存
   ↓
3. Google Custom Search 查找相关 URLs
   - 搜索 Facebook, Lowyat, Cari, Google Maps 等
   - 返回 20-30 个相关网页链接
   ↓
4. OpenAI 从 URLs 中提取评价内容
   - 访问每个 URL
   - 提取原始评价文本
   - 返回结构化数据
   ↓
5. 保存到缓存
   ↓
6. 返回给用户
```

## 费用

### Google Custom Search API
- **免费额度**: 100 次查询/天
- **付费**: $5 / 1000 次额外查询
- 预计成本: 如果每天 50 次搜索，完全免费

### OpenAI (内容提取)
- 使用 GPT-4 或 GPT-3.5 提取内容
- 预计成本: $0.01-0.02 每次搜索

## 备用方案

如果没有配置 Google API，系统会自动退回到 OpenAI web_search:

```python
if settings.google_search_api_key and settings.google_search_engine_id:
    # 使用 Google Custom Search
else:
    # 退回到 OpenAI web_search
```

## 相关文件

- `src/search/google_searcher.py` - Google 搜索实现
- `src/search/aggregator.py` - 搜索聚合器（协调 Google + OpenAI）
- `src/config.py` - 配置管理
- `test_google_search.py` - 测试脚本

## 故障排除

### Error: "API key not configured"
→ 检查 `.env` 文件是否正确配置 `GOOGLE_SEARCH_API_KEY`

### Error: "Search engine ID not configured"
→ 检查 `.env` 文件是否正确配置 `GOOGLE_SEARCH_ENGINE_ID`

### Error: 429 Rate Limit
→ 超过免费额度 (100次/天)，等待明天重置或升级到付费计划

### No results found
→ 医生名字可能拼写不正确，或该医生确实没有在线评价
