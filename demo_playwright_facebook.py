"""
演示：使用 Playwright 抓取 Facebook 动态内容

安装：
pip install playwright
playwright install chromium

运行：
python demo_playwright_facebook.py
"""

import asyncio
from playwright.async_api import async_playwright


async def scrape_facebook_comments(url: str):
    """
    使用 Playwright 抓取 Facebook 评论

    这个示例展示了如何：
    1. 启动浏览器
    2. 访问动态页面
    3. 等待内容加载
    4. 执行 JavaScript
    5. 提取内容
    """

    print(f"正在抓取: {url}\n")

    async with async_playwright() as p:
        # 1. 启动浏览器（headless=True 表示后台运行）
        print("1. 启动 Chrome 浏览器...")
        browser = await p.chromium.launch(
            headless=False,  # 设为 False 可以看到浏览器窗口
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage'
            ]
        )

        # 2. 创建新页面
        print("2. 创建新页面...")
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )

        page = await context.new_page()

        # 3. 删除 webdriver 标记（避免被检测）
        print("3. 设置反检测...")
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false
            });
        """)

        # 4. 访问 Facebook URL
        print(f"4. 访问 URL: {url}")
        try:
            await page.goto(url, wait_until='networkidle', timeout=30000)
        except:
            print("   ⚠️ 页面加载超时，继续尝试...")
            pass

        # 5. 等待页面加载
        print("5. 等待内容加载...")
        await asyncio.sleep(5)

        # 6. 滚动加载更多内容
        print("6. 滚动页面加载更多评论...")
        for i in range(3):
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(2)
            print(f"   滚动 {i+1}/3")

        # 7. 提取页面文本内容
        print("7. 提取页面内容...")

        # 方法 A：提取所有文本（简单但不精确）
        all_text = await page.evaluate('() => document.body.innerText')

        # 方法 B：尝试找到评论元素（精确但可能失败）
        selectors = [
            '[role="article"]',  # 通用文章元素
            '[data-testid*="comment"]',  # 评论元素
            'div[dir="auto"]',  # 文本容器
        ]

        comments = []
        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                if elements:
                    print(f"   ✅ 找到 {len(elements)} 个元素（选择器: {selector}）")
                    for el in elements[:10]:  # 只取前 10 个
                        text = await el.inner_text()
                        if text and len(text) > 20:
                            comments.append(text)
                    break
            except:
                continue

        # 8. 截图（可选，用于调试）
        screenshot_path = "/tmp/facebook_screenshot.png"
        await page.screenshot(path=screenshot_path)
        print(f"8. 截图已保存: {screenshot_path}")

        # 9. 关闭浏览器
        await browser.close()
        print("9. 浏览器已关闭\n")

        # 10. 返回结果
        return {
            "all_text": all_text[:1000],  # 前 1000 字符
            "comments": comments[:5],  # 前 5 条评论
            "total_length": len(all_text)
        }


async def filter_doctor_mentions(text: str, doctor_name: str):
    """
    简单的文本过滤：找出提到医生名字的段落
    """
    paragraphs = text.split('\n')
    relevant = []

    for para in paragraphs:
        if doctor_name.lower() in para.lower():
            if 20 < len(para) < 500:  # 长度合理
                relevant.append(para.strip())

    return relevant


async def main():
    """主函数"""

    print("=" * 70)
    print("Playwright Facebook 抓取演示")
    print("=" * 70)
    print()

    # 测试 URL
    url = "https://www.facebook.com/ColumbiaAsiaHospitalPetalingJaya/posts/1298529398952280"
    doctor_name = "Dr. Paul Ngalap Ayu"

    # 抓取内容
    result = await scrape_facebook_comments(url)

    # 显示结果
    print("=" * 70)
    print("抓取结果")
    print("=" * 70)
    print()

    print(f"总文本长度: {result['total_length']} 字符")
    print()

    print("提取的文本片段（前 1000 字符）:")
    print("-" * 70)
    print(result['all_text'])
    print("-" * 70)
    print()

    if result['comments']:
        print(f"找到 {len(result['comments'])} 条可能的评论:")
        for i, comment in enumerate(result['comments'], 1):
            print(f"{i}. {comment[:100]}...")
        print()

    # 过滤相关评论
    print(f"搜索提到 '{doctor_name}' 的内容:")
    print("-" * 70)
    relevant = await filter_doctor_mentions(result['all_text'], doctor_name)

    if relevant:
        for i, para in enumerate(relevant, 1):
            print(f"{i}. {para}")
            print()
    else:
        print("❌ 没有找到提到医生名字的内容")
        print()

    print("=" * 70)
    print("演示完成")
    print("=" * 70)
    print()
    print("注意事项:")
    print("1. Facebook 可能需要登录才能看到完整内容")
    print("2. Facebook 可能检测并阻止爬虫")
    print("3. 页面结构经常变化，选择器可能失效")
    print("4. 建议使用 ChatGPT API 代替自己爬取")


if __name__ == "__main__":
    # 运行
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n\n错误: {e}")
