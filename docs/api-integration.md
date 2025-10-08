# API 集成文档

本文档详细说明如何集成 WhatsApp、Google Places、Facebook 等 API。

---

## 1. WhatsApp Business Cloud API

### 1.1 注册与配置

#### 步骤 1：创建 Meta 开发者账号
1. 访问 [Meta for Developers](https://developers.facebook.com/)
2. 创建新应用 → 选择 "Business" 类型
3. 添加 "WhatsApp" 产品

#### 步骤 2：获取凭证
```bash
# 需要获取的信息
WHATSAPP_PHONE_NUMBER_ID=123456789      # 电话号码 ID
WHATSAPP_BUSINESS_ACCOUNT_ID=987654321  # 商业账号 ID
WHATSAPP_ACCESS_TOKEN=EAAxxxx...        # 访问令牌
VERIFY_TOKEN=your_custom_verify_token   # Webhook 验证 token（自定义）
```

#### 步骤 3：配置 Webhook
- URL: `https://your-domain.com/webhook/whatsapp`
- 验证 token: 自定义字符串（如 `my_secret_token_123`）
- 订阅字段: `messages`

### 1.2 接收消息

```python
from fastapi import FastAPI, Request, Response
import hmac
import hashlib

app = FastAPI()

VERIFY_TOKEN = "your_custom_verify_token"

@app.get("/webhook/whatsapp")
async def verify_webhook(request: Request):
    """WhatsApp webhook 验证"""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    return Response(status_code=403)

@app.post("/webhook/whatsapp")
async def receive_message(request: Request):
    """接收用户消息"""
    body = await request.json()

    # 提取消息
    try:
        entry = body["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        messages = value.get("messages", [])

        if messages:
            message = messages[0]
            from_number = message["from"]  # 用户手机号
            message_body = message["text"]["body"]  # 消息内容

            # 处理消息
            await process_user_query(from_number, message_body)

    except Exception as e:
        print(f"Error processing message: {e}")

    return {"status": "ok"}
```

### 1.3 发送消息

```python
import httpx

async def send_whatsapp_message(to: str, message: str):
    """发送 WhatsApp 消息"""
    url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        return response.json()
```

### 1.4 格式化输出模板

```python
def format_doctor_review_response(doctor_name: str, reviews: list) -> str:
    """格式化医生评价输出"""
    positive = [r for r in reviews if r["sentiment"] == "positive"]
    negative = [r for r in reviews if r["sentiment"] == "negative"]

    message = f"🔍 *{doctor_name}* 的评价汇总\n\n"

    # 正面评价
    message += "✅ *正面评价*\n"
    for i, review in enumerate(positive[:5], 1):
        source_emoji = {"google_maps": "🗺️", "facebook": "👥", "hospital_website": "🏥"}
        emoji = source_emoji.get(review["source"], "📄")
        message += f"{i}. {emoji} {review['snippet'][:100]}...\n"
        message += f"   来源: {review['url']}\n\n"

    # 负面评价
    message += "❌ *负面评价*\n"
    for i, review in enumerate(negative[:5], 1):
        emoji = source_emoji.get(review["source"], "📄")
        message += f"{i}. {emoji} {review['snippet'][:100]}...\n"
        message += f"   来源: {review['url']}\n\n"

    message += "_数据来源于公开网络，仅供参考_"
    return message
```

### 1.5 成本说明

- **免费额度**：每月 1,000 条对话免费
- **付费价格**：$0.005-0.009/条（按地区不同）
- **对话定义**：24 小时内的多条消息算 1 个对话

---

## 2. Google Places API

### 2.1 启用 API

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建项目
3. 启用 **Places API** 和 **Maps JavaScript API**
4. 创建 API 密钥

```bash
GOOGLE_PLACES_API_KEY=AIzaSyXXXXXXXXXXXXXXXXX
```

### 2.2 搜索医生

```python
import httpx

async def search_google_places(doctor_name: str, location: str = ""):
    """搜索 Google Maps 上的医生"""
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    params = {
        "query": f"{doctor_name} 医生 {location}",
        "key": GOOGLE_PLACES_API_KEY,
        "language": "zh-CN"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(base_url, params=params)
        data = response.json()

        if data["status"] == "OK":
            places = data["results"]
            return await get_place_reviews(places[0]["place_id"])
        return []

async def get_place_reviews(place_id: str):
    """获取地点详情和评论"""
    base_url = "https://maps.googleapis.com/maps/api/place/details/json"

    params = {
        "place_id": place_id,
        "fields": "name,rating,reviews,formatted_address,url",
        "key": GOOGLE_PLACES_API_KEY,
        "language": "zh-CN"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(base_url, params=params)
        data = response.json()

        if data["status"] == "OK":
            result = data["result"]
            reviews = []

            for review in result.get("reviews", []):
                reviews.append({
                    "source": "google_maps",
                    "url": result["url"],
                    "snippet": review["text"],
                    "rating": review["rating"],
                    "review_date": review["time"],  # Unix timestamp
                    "author": review["author_name"]
                })

            return reviews
        return []
```

### 2.3 成本说明

- **免费额度**：每月 $200 免费（约 28,000 次基础调用）
- **Text Search**：$32/1000 次
- **Place Details**：$17/1000 次
- **预估成本**：1,500 次搜索/月 ≈ $0（在免费额度内）

---

## 3. Facebook Graph API

### 3.1 获取访问令牌

1. 访问 [Facebook for Developers](https://developers.facebook.com/)
2. 创建应用 → 添加 "Facebook Login" 产品
3. 生成访问令牌（需要 `pages_read_engagement` 权限）

```bash
FACEBOOK_ACCESS_TOKEN=EAAxxxx...
```

### 3.2 搜索公开主页

```python
async def search_facebook_pages(doctor_name: str):
    """搜索 Facebook 公开主页"""
    base_url = "https://graph.facebook.com/v18.0/pages/search"

    params = {
        "q": doctor_name,
        "type": "page",
        "fields": "id,name,about,category,rating_count,overall_star_rating",
        "access_token": FACEBOOK_ACCESS_TOKEN
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(base_url, params=params)
        data = response.json()

        pages = data.get("data", [])
        if pages:
            return await get_page_reviews(pages[0]["id"])
        return []

async def get_page_reviews(page_id: str):
    """获取主页评论（仅限公开评论）"""
    base_url = f"https://graph.facebook.com/v18.0/{page_id}/ratings"

    params = {
        "fields": "reviewer,rating,review_text,created_time,open_graph_story",
        "access_token": FACEBOOK_ACCESS_TOKEN,
        "limit": 50
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(base_url, params=params)
        data = response.json()

        reviews = []
        for item in data.get("data", []):
            if item.get("review_text"):  # 只抓取有文字评论的
                reviews.append({
                    "source": "facebook",
                    "url": f"https://www.facebook.com/{page_id}",
                    "snippet": item["review_text"],
                    "rating": item.get("rating", 0),
                    "review_date": item["created_time"],
                    "author": item["reviewer"]["name"]
                })

        return reviews
```

### 3.3 限制说明

⚠️ **重要**：
- 只能访问**公开主页**的评论
- 无法访问私密群组或个人账号
- 需要主页管理员权限才能读取某些数据
- API 调用有速率限制（200 calls/hour/user）

### 3.4 成本说明

- **免费**：Graph API 本身免费
- **限制**：受速率限制，不收费

---

## 4. 医院官网爬虫

### 4.1 基础爬虫（Beautiful Soup）

```python
import httpx
from bs4 import BeautifulSoup

async def scrape_hospital_website(doctor_name: str, hospital_url: str):
    """爬取医院官网的医生评价"""
    search_url = f"{hospital_url}/search?q={doctor_name}"

    async with httpx.AsyncClient() as client:
        response = await client.get(search_url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # 根据网站结构调整选择器
        reviews = soup.select(".doctor-review-item")

        results = []
        for review in reviews:
            snippet = review.select_one(".review-text").get_text(strip=True)
            rating = review.select_one(".rating")
            date = review.select_one(".review-date")

            results.append({
                "source": "hospital_website",
                "url": hospital_url,
                "snippet": snippet,
                "rating": float(rating.get_text()) if rating else None,
                "review_date": date.get_text() if date else None
            })

        return results
```

### 4.2 动态网站爬虫（Selenium）

对于需要 JavaScript 渲染的网站：

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

async def scrape_dynamic_website(doctor_name: str, url: str):
    """爬取动态网站"""
    options = Options()
    options.add_argument("--headless")  # 无头模式
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        driver.implicitly_wait(5)

        # 查找评论元素
        reviews = driver.find_elements(By.CLASS_NAME, "review-item")

        results = []
        for review in reviews:
            text = review.find_element(By.CLASS_NAME, "review-text").text
            results.append({
                "source": "hospital_website",
                "url": url,
                "snippet": text
            })

        return results

    finally:
        driver.quit()
```

### 4.3 注意事项

⚠️ **爬虫合规**：
- 遵守 `robots.txt` 规则
- 设置合理的爬取频率（间隔 1-2 秒）
- 添加 User-Agent
- 仅爬取公开信息

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
```

---

## 5. OpenAI API（情感分析）

### 5.1 配置

```bash
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
```

### 5.2 情感分类

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def classify_sentiment(review_text: str) -> dict:
    """使用 GPT-4 进行情感分析"""
    prompt = f"""
请分析以下医生评价的情感倾向，分类为：positive（正面）、negative（负面）或 neutral（中性）。

评价内容：
{review_text}

请以 JSON 格式返回：
{{
  "sentiment": "positive/negative/neutral",
  "key_points": ["要点1", "要点2"],
  "confidence": 0.95
}}
"""

    response = await client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "你是一个专业的医疗评价分析助手。"},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.3
    )

    result = json.loads(response.choices[0].message.content)
    return result
```

### 5.3 批量分析优化

```python
async def batch_classify(reviews: list) -> list:
    """批量分析多条评论"""
    # 合并多条评论减少 API 调用
    combined_text = "\n---\n".join([f"评论{i+1}：{r['snippet']}"
                                     for i, r in enumerate(reviews)])

    prompt = f"""
请分析以下 {len(reviews)} 条医生评价，分别标注情感倾向。

{combined_text}

返回 JSON 数组格式：
[
  {{"id": 1, "sentiment": "positive", "key_points": [...]}},
  {{"id": 2, "sentiment": "negative", "key_points": [...]}}
]
"""

    response = await client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)
```

### 5.4 成本优化

- 使用 **gpt-4-turbo** 而非 gpt-4：成本降低 50%
- 使用 **gpt-3.5-turbo**：成本降低 90%（准确率略降）
- 批量处理：减少 API 调用次数

**成本对比**（每 1,500 次分析）：

| 模型 | 输入价格 | 输出价格 | 月成本（预估） |
|------|----------|----------|----------------|
| GPT-4-turbo | $10/1M tokens | $30/1M tokens | $3-5 |
| GPT-3.5-turbo | $0.5/1M tokens | $1.5/1M tokens | $0.5-1 |

---

## 6. 完整搜索流程示例

```python
async def search_doctor_reviews(doctor_name: str, location: str = "") -> dict:
    """聚合所有数据源搜索医生评价"""

    # 并发搜索所有数据源
    tasks = [
        search_google_places(doctor_name, location),
        search_facebook_pages(doctor_name),
        scrape_hospital_website(doctor_name, "https://example-hospital.com")
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 合并结果
    all_reviews = []
    for result in results:
        if isinstance(result, list):
            all_reviews.extend(result)

    # AI 分析
    analyzed = await batch_classify(all_reviews)

    # 组合数据
    for i, review in enumerate(all_reviews):
        review["sentiment"] = analyzed[i]["sentiment"]
        review["key_points"] = analyzed[i]["key_points"]

    return {
        "doctor_name": doctor_name,
        "total_reviews": len(all_reviews),
        "reviews": all_reviews
    }
```

---

## 7. API 错误处理

```python
async def safe_api_call(func, *args, **kwargs):
    """带重试的 API 调用"""
    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except httpx.TimeoutException:
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                raise
        except Exception as e:
            logger.error(f"API call failed: {e}")
            return []
```

---

## 8. 环境变量配置示例

创建 `.env` 文件：

```bash
# WhatsApp
WHATSAPP_PHONE_NUMBER_ID=123456789
WHATSAPP_ACCESS_TOKEN=EAAxxxx...
VERIFY_TOKEN=my_secret_token_123

# Google
GOOGLE_PLACES_API_KEY=AIzaSyXXXXXX

# Facebook
FACEBOOK_ACCESS_TOKEN=EAAyyyy...

# OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxx

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/doctor_review_db

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

---

## 9. 测试工具

### 9.1 WhatsApp 测试

使用 Meta 提供的测试号码：
```bash
curl -X POST "https://graph.facebook.com/v18.0/YOUR_PHONE_ID/messages" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "YOUR_TEST_NUMBER",
    "type": "text",
    "text": {"body": "测试消息"}
  }'
```

### 9.2 API 集成测试

```python
import pytest

@pytest.mark.asyncio
async def test_google_places_search():
    results = await search_google_places("张医生", "北京")
    assert len(results) > 0
    assert results[0]["source"] == "google_maps"

@pytest.mark.asyncio
async def test_sentiment_analysis():
    review = {"snippet": "医生态度很好，专业"}
    result = await classify_sentiment(review["snippet"])
    assert result["sentiment"] == "positive"
```

---

## 10. API 配额监控

```python
# 记录 API 使用情况
api_usage = {
    "google_places": 0,
    "facebook": 0,
    "openai_tokens": 0
}

async def track_api_call(service: str, cost: float = 0):
    """记录 API 调用"""
    api_usage[service] += 1

    # 存入数据库
    await db.execute(
        "INSERT INTO api_usage_logs (service, cost, timestamp) VALUES ($1, $2, NOW())",
        service, cost
    )
```
