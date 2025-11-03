# 动态页面爬取技术指南

## 问题：如何搜索动态页面（例如 Facebook 评论）？

动态页面的内容通过 JavaScript 加载，普通 HTTP 请求无法获取。

---

## 技术方案对比

| 方案 | 难度 | 成本 | 可靠性 | 适用场景 |
|------|------|------|--------|---------|
| **Playwright/Selenium** | 🟡 中等 | 💰 中等 | ⭐⭐⭐⭐ | 通用，最可靠 |
| **Puppeteer** | 🟡 中等 | 💰 中等 | ⭐⭐⭐⭐ | Node.js 项目 |
| **API 逆向工程** | 🔴 困难 | 💰 低 | ⭐⭐ | 特定网站 |
| **第三方服务** | 🟢 简单 | 💰💰 高 | ⭐⭐⭐ | 快速实现 |
| **ChatGPT API** | 🟢 简单 | 💰💰 高 | ⭐⭐⭐⭐⭐ | 最简单 |

---

## 方案 1：Playwright（Python）⭐⭐⭐⭐⭐ 推荐

### 什么是 Playwright？

Playwright 是微软开发的浏览器自动化工具，可以：
- 运行真实的 Chrome/Firefox 浏览器
- 执行 JavaScript
- 等待动态内容加载
- 截图、点击、滚动等操作

### 安装

```bash
pip install playwright
playwright install chromium
```

### 代码示例：抓取 Facebook 评论

```python
from playwright.async_api import async_playwright
import asyncio

async def scrape_facebook_comments(url: str):
    """
    使用 Playwright 抓取 Facebook 评论
    """
    async with async_playwright() as p:
        # 1. 启动浏览器（headless=True 表示后台运行）
        browser = await p.chromium.launch(headless=True)

        # 2. 创建新页面
        page = await browser.new_page()

        # 3. 访问 Facebook URL
        await page.goto(url, wait_until='networkidle')

        # 4. 等待评论加载（可能需要滚动）
        await page.wait_for_selector('[data-testid="UFI2Comment/root_depth_0"]', timeout=10000)

        # 5. 滚动加载更多评论
        for _ in range(3):  # 滚动 3 次
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(2)  # 等待加载

        # 6. 提取评论内容
        comments = await page.evaluate('''
            () => {
                const commentElements = document.querySelectorAll('[data-testid="UFI2Comment/root_depth_0"]');
                return Array.from(commentElements).map(el => ({
                    text: el.innerText,
                    author: el.querySelector('[data-testid="UFI2CommentsCount/sentenceWithCommentCount"]')?.innerText || ''
                }));
            }
        ''')

        # 7. 关闭浏览器
        await browser.close()

        return comments

# 使用
url = "https://www.facebook.com/ColumbiaAsiaHospitalPetalingJaya/posts/1298529398952280"
comments = await scrape_facebook_comments(url)

for comment in comments:
    print(f"作者: {comment['author']}")
    print(f"内容: {comment['text']}")
    print()
```

### 优点

- ✅ 可以抓取任何动态内容
- ✅ 执行 JavaScript，看到真实内容
- ✅ 可以模拟滚动、点击等操作
- ✅ 支持 Chrome/Firefox/Safari

### 缺点

- ❌ 需要运行浏览器（占用资源）
- ❌ 速度较慢（每次 5-10 秒）
- ❌ Facebook 可能检测并阻止（需要处理）

### 成本

```
Railway 服务器（需要更多资源）:
- Hobby: $10/月（可能不够）
- Pro: $20/月（推荐）

每次抓取时间：5-10 秒
并发限制：建议 2-3 个浏览器实例
```

---

## 方案 2：Selenium（Python）⭐⭐⭐⭐

### 什么是 Selenium？

Selenium 是老牌的浏览器自动化工具，功能类似 Playwright。

### 安装

```bash
pip install selenium
# 还需要下载 ChromeDriver
```

### 代码示例

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_with_selenium(url: str):
    """
    使用 Selenium 抓取 Facebook 评论
    """
    # 1. 配置浏览器选项
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 后台运行
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # 2. 启动浏览器
    driver = webdriver.Chrome(options=options)

    try:
        # 3. 访问页面
        driver.get(url)

        # 4. 等待评论加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[role="article"]'))
        )

        # 5. 滚动加载更多
        for _ in range(3):
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(2)

        # 6. 提取评论
        comment_elements = driver.find_elements(By.CSS_SELECTOR, '[role="article"]')
        comments = []

        for el in comment_elements:
            text = el.text
            if text:
                comments.append({'text': text})

        return comments

    finally:
        # 7. 关闭浏览器
        driver.quit()

# 使用
url = "https://www.facebook.com/..."
comments = scrape_with_selenium(url)
```

### Playwright vs Selenium

| 特性 | Playwright | Selenium |
|------|-----------|----------|
| 速度 | ⭐⭐⭐⭐⭐ 更快 | ⭐⭐⭐ 较慢 |
| API 设计 | ⭐⭐⭐⭐⭐ 现代 | ⭐⭐⭐ 传统 |
| 异步支持 | ✅ 原生支持 | ❌ 需要额外配置 |
| 安装复杂度 | ⭐⭐⭐⭐⭐ 简单 | ⭐⭐⭐ 需要 driver |

**推荐**：用 Playwright（更现代、更快）

---

## 方案 3：API 逆向工程 ⭐⭐

### 原理

很多网站的动态内容通过 API 加载。如果能找到 API 端点，直接调用 API 更快。

### 步骤

```
1. 打开浏览器开发者工具（F12）
2. 访问 Facebook 帖子
3. 查看 Network 标签
4. 找到评论的 API 请求（例如 /api/graphql）
5. 分析请求参数和响应格式
6. 用 Python 模拟相同的请求
```

### 示例（假设找到了 API）

```python
import httpx

async def fetch_facebook_comments_api(post_id: str):
    """
    直接调用 Facebook API（需要逆向找到端点）
    """
    url = "https://www.facebook.com/api/graphql"

    # 需要的参数（通过浏览器抓包获得）
    params = {
        "doc_id": "123456789",  # GraphQL 查询 ID
        "variables": {
            "postID": post_id,
            "count": 50
        }
    }

    headers = {
        "User-Agent": "Mozilla/5.0...",
        "Cookie": "session_token=...",  # 可能需要登录
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=params, headers=headers)
        data = response.json()

        # 解析 API 响应
        comments = data['data']['node']['comments']['edges']
        return comments
```

### 优点

- ✅ 速度快（直接 API 调用）
- ✅ 资源占用少（不需要浏览器）
- ✅ 可以批量获取

### 缺点

- ❌ 需要逆向工程（很难）
- ❌ API 可能随时变化
- ❌ 可能需要登录凭证
- ❌ 违反服务条款风险

---

## 方案 4：第三方爬虫服务 ⭐⭐⭐

### 服务选项

#### Apify（推荐）

- 专业的爬虫平台
- 有现成的 Facebook Scraper
- 定价：$49/月起

```python
from apify_client import ApifyClient

client = ApifyClient('your_api_token')

# 运行 Facebook Comments Scraper
run = client.actor("apify/facebook-comments-scraper").call(
    run_input={
        "startUrls": [
            "https://www.facebook.com/ColumbiaAsiaHospitalPetalingJaya/posts/1298529398952280"
        ],
        "maxComments": 100
    }
)

# 获取结果
comments = client.dataset(run["defaultDatasetId"]).list_items().items
```

#### Bright Data（原 Luminati）

- 企业级爬虫服务
- 提供浏览器 API
- 定价：$500/月起（贵）

#### ScrapingBee

- 浏览器自动化 API
- 处理 JavaScript 渲染
- 定价：$49/月（1000 次请求）

```python
import requests

response = requests.get(
    url='https://app.scrapingbee.com/api/v1/',
    params={
        'api_key': 'YOUR_API_KEY',
        'url': 'https://www.facebook.com/...',
        'render_js': 'true',  # 执行 JavaScript
        'wait': 5000  # 等待 5 秒
    }
)

html = response.text
# 用 BeautifulSoup 解析
```

### 优点

- ✅ 开箱即用，不需要维护基础设施
- ✅ 处理反爬措施（代理、User-Agent 轮换）
- ✅ 可靠性高

### 缺点

- ❌ 成本高（$49-500/月）
- ❌ 依赖第三方服务

---

## 方案 5：ChatGPT API（最简单）⭐⭐⭐⭐⭐

### 原理

OpenAI 的 ChatGPT 已经内置了 Web Browser Tool，可以直接访问动态网页。

### 代码示例

```python
from openai import AsyncOpenAI

async def search_with_chatgpt(doctor_name: str, facebook_url: str = None):
    """
    使用 ChatGPT 搜索医生评价（包括 Facebook 评论）
    """
    client = AsyncOpenAI(api_key='your_api_key')

    if facebook_url:
        # 指定 URL
        prompt = f"访问这个 Facebook 帖子并提取关于 {doctor_name} 的患者评价：{facebook_url}"
    else:
        # 让 ChatGPT 自己搜索
        prompt = f"搜索 {doctor_name} 在马来西亚的患者评价，包括 Facebook、Google Maps、论坛"

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": prompt
        }]
        # ChatGPT 会自动使用 web search + web browser
    )

    return response.choices[0].message.content

# 使用
result = await search_with_chatgpt(
    doctor_name="Dr. Paul Ngalap Ayu",
    facebook_url="https://www.facebook.com/ColumbiaAsiaHospitalPetalingJaya/posts/1298529398952280"
)

print(result)
# ChatGPT 会返回：
# "在这个 Facebook 帖子中，找到了 3 条关于 Dr. Paul 的评价：
# 1. 患者A说：Dr. Paul 很专业...
# 2. 患者B说：Dr. Paul 帮我治好了...
# 3. ..."
```

### 优点

- ✅✅✅ 最简单（几行代码）
- ✅ 不需要维护浏览器基础设施
- ✅ 可靠性高（OpenAI 维护）
- ✅ 可以搜索 + 抓取 + 分析一步完成

### 缺点

- ❌ 成本较高（GPT-4o: ~$0.04/次）
- ❌ 依赖 OpenAI

### 成本

```
每次搜索：
- Input: ~5,000 tokens
- Output: ~3,000 tokens
- 成本：$0.0125 + $0.03 = $0.0425

月成本（1,500次）：
1,500 × $0.0425 = $63.75/月
```

---

## Facebook 特殊挑战

### 挑战 1：登录墙

很多 Facebook 内容需要登录才能查看。

**解决方案**：

```python
# Playwright 登录 Facebook
async def login_facebook(page):
    await page.goto('https://www.facebook.com/login')
    await page.fill('input[name="email"]', 'your_email@example.com')
    await page.fill('input[name="pass"]', 'your_password')
    await page.click('button[name="login"]')
    await page.wait_for_url('https://www.facebook.com/', timeout=10000)

    # 保存 cookies
    cookies = await page.context.cookies()
    return cookies
```

**风险**：
- ❌ 违反 Facebook 服务条款
- ❌ 账号可能被封禁

### 挑战 2：反爬虫检测

Facebook 会检测并阻止爬虫。

**解决方案**：

```python
# 使用 Playwright 的隐身模式
async def scrape_with_stealth(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )

        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ...',
            viewport={'width': 1920, 'height': 1080},
            locale='en-US'
        )

        page = await context.new_page()

        # 删除 webdriver 标记
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false
            });
        """)

        await page.goto(url)
        # ... 抓取内容
```

### 挑战 3：动态选择器

Facebook 的 HTML 结构经常变化。

**解决方案**：

```python
# 使用多个备选选择器
selectors = [
    '[data-testid="UFI2Comment/root_depth_0"]',  # 选择器 1
    '[role="article"]',  # 选择器 2
    '.comment-content',  # 选择器 3
]

for selector in selectors:
    try:
        elements = await page.query_selector_all(selector)
        if elements:
            break
    except:
        continue
```

---

## 完整实现示例

### 集成到项目中

```python
# src/search/facebook_scraper.py

from playwright.async_api import async_playwright
import asyncio
import logging

logger = logging.getLogger(__name__)

class FacebookScraper:
    """使用 Playwright 抓取 Facebook 评论"""

    def __init__(self):
        self.enabled = True

    async def scrape_post_comments(self, url: str, doctor_name: str, max_comments: int = 50):
        """
        抓取 Facebook 帖子的评论

        Args:
            url: Facebook 帖子 URL
            doctor_name: 医生名字（用于过滤相关评论）
            max_comments: 最多抓取评论数

        Returns:
            List of comments
        """
        try:
            async with async_playwright() as p:
                # 启动浏览器
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                # 访问页面
                logger.info(f"正在访问 Facebook: {url}")
                await page.goto(url, wait_until='networkidle', timeout=30000)

                # 等待内容加载
                await asyncio.sleep(3)

                # 滚动加载更多评论
                for i in range(3):
                    await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    await asyncio.sleep(2)
                    logger.info(f"滚动加载 {i+1}/3")

                # 提取所有文本内容
                content = await page.evaluate('() => document.body.innerText')

                await browser.close()

                # 用简单的文本分析提取相关评论
                comments = self._extract_relevant_comments(content, doctor_name)

                logger.info(f"找到 {len(comments)} 条相关评论")
                return comments[:max_comments]

        except Exception as e:
            logger.error(f"Facebook 抓取失败: {e}")
            return []

    def _extract_relevant_comments(self, content: str, doctor_name: str):
        """简单的文本过滤"""
        lines = content.split('\n')
        comments = []

        for line in lines:
            # 如果这行提到医生名字
            if doctor_name.lower() in line.lower():
                # 并且长度合理（可能是评论）
                if 20 < len(line) < 500:
                    comments.append({
                        'text': line,
                        'source': 'facebook'
                    })

        return comments

# 使用
facebook_scraper = FacebookScraper()
```

### 集成到搜索聚合器

```python
# src/search/aggregator.py

async def search_doctor_reviews(doctor_name: str):
    """完整的搜索流程"""

    # 1. Outscraper - Google Maps（关键词搜索）
    logger.info("🗺️ 搜索 Google Maps 评价...")
    google_maps_reviews = await outscraper_client.google_maps_reviews(
        query=f"{doctor_name} Malaysia",
        reviews_query=doctor_name,
        limit=20
    )

    # 2. Google Custom Search - 论坛
    logger.info("📋 搜索论坛评价...")
    forum_urls = await google_searcher.search_doctor_reviews(
        doctor_name=doctor_name,
        location="Malaysia"
    )

    # 3. Facebook（可选，如果用户提供了 URL）
    facebook_reviews = []
    if known_facebook_url:
        logger.info("📘 抓取 Facebook 评价...")
        facebook_reviews = await facebook_scraper.scrape_post_comments(
            url=known_facebook_url,
            doctor_name=doctor_name
        )

    # 4. 合并所有结果
    return {
        "google_maps": google_maps_reviews,
        "forums": forum_urls,
        "facebook": facebook_reviews,
        "total_count": len(google_maps_reviews) + len(facebook_reviews)
    }
```

---

## 成本对比（30用户，1,500次/月）

| 方案 | 月成本 | 说明 |
|------|--------|------|
| Outscraper 关键词搜索 | $45 | Google Maps only |
| + Playwright (自建) | $45 + $20 = $65 | 需要 Pro 服务器 |
| + Apify | $45 + $49 = $94 | 第三方服务 |
| + ChatGPT API | $45 + $64 = $109 | 最简单 |

---

## 最终建议

### 如果要实现 Facebook 评论抓取

**推荐方案：ChatGPT API** ⭐⭐⭐⭐⭐

理由：
1. ✅ 最简单（几行代码）
2. ✅ 不需要维护浏览器基础设施
3. ✅ OpenAI 处理所有反爬措施
4. ✅ 成本可接受（$109/月 = $3.63/用户/月）

**如果预算紧张：Playwright 自建**

理由：
1. ✅ 成本较低（$65/月）
2. ⚠️ 需要处理反爬措施
3. ⚠️ 需要维护代码（Facebook 结构变化）

### 但最重要的问题

**是否真的需要 Facebook 评论？**

- Google Maps 评价已经很全面（通过 Outscraper 关键词搜索）
- Facebook 评论数量较少
- 技术复杂度和成本显著增加

**建议**：
1. 先只做 Google Maps（$45/月）
2. 测试用户反馈
3. 如果用户强烈需要 Facebook → 再加上 ChatGPT API

---

**文档创建时间**：2025-10-30
**结论**：动态页面抓取技术可行，但建议从 Google Maps 开始，按需添加 Facebook
