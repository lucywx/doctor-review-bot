"""
ChatGPT Search - 用于搜索 Facebook 和论坛评价

使用 Responses API + gpt-5-mini + web_search 工具
这是 OpenAI 的新一代 Agentic API，支持实时网络搜索
"""

from openai import AsyncOpenAI
from typing import Dict, List
import logging
import os
import json

logger = logging.getLogger(__name__)


class ChatGPTSearchClient:
    """ChatGPT Search 客户端 - 使用 Responses API + gpt-5-mini + web_search"""

    def __init__(self, api_key: str = None):
        """
        初始化 ChatGPT 客户端

        Args:
            api_key: OpenAI API key
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")

        if not self.api_key or self.api_key == "your_openai_api_key_here":
            logger.warning("OpenAI API key not configured")
            self.enabled = False
            self.client = None
        else:
            self.enabled = True
            self.client = AsyncOpenAI(api_key=self.api_key)
            logger.info("✅ ChatGPT Responses API + gpt-5-mini initialized (实时网络搜索)")

    async def search_facebook_and_forums(
        self,
        doctor_name: str,
        location: str = "Malaysia"
    ) -> Dict:
        """
        使用 ChatGPT web search 搜索 Facebook 和论坛评价

        使用 OpenAI 的 web_search_preview 工具进行实时网络搜索

        Args:
            doctor_name: 医生名字
            location: 地点

        Returns:
            {
                "reviews": [
                    {
                        "text": "评价内容",
                        "source": "来源",
                        "url": "链接",
                        "author_name": "患者姓名",
                        "review_date": "发布日期",
                        "rating": "评分"
                    }
                ],
                "summary": "...",
                "total_count": 5,
                "source": "chatgpt_web_search"
            }
        """
        if not self.enabled:
            logger.warning("ChatGPT search not enabled")
            return {
                "reviews": [],
                "summary": "",
                "total_count": 0,
                "error": "OpenAI API key not configured"
            }

        try:
            logger.info(f"🔍 ChatGPT Responses API 实时网络搜索: {doctor_name} in {location}")

            # 使用 Responses API + gpt-5-mini + web_search 工具
            response = await self.client.responses.create(
                model="gpt-5-mini",  # ⭐ 使用 gpt-5-mini（成本优化）
                tools=[{"type": "web_search"}],  # ⭐ 启用 web_search 工具
                input=f"""Search for patient reviews about {doctor_name} in {location}.

Focus on:
1. Facebook pages and posts mentioning {doctor_name}
2. Medical forums and discussion boards
3. Patient review sites and community platforms
4. Health forums and parenting websites

For each review you find, extract:
- The review text
- Author name (if available)
- Date (if available)
- Source website name
- Source URL
- Rating (if available)

Provide specific patient experiences and testimonials."""
            )

            # 解析 Responses API 的输出
            reviews = []
            summary_parts = []
            citations = []

            logger.info(f"📦 Response type: {type(response)}")

            # Responses API 返回的 output 是一个列表
            # 包含 reasoning items, web_search_call items, 和最终的 message
            if hasattr(response, 'output') and isinstance(response.output, list):
                logger.info(f"📝 Output items count: {len(response.output)}")

                # 遍历 output 列表，找到 type='message' 的项目
                for item in response.output:
                    if hasattr(item, 'type'):
                        logger.info(f"  - Item type: {item.type}")

                        # 记录搜索查询
                        if item.type == 'web_search_call' and hasattr(item, 'action'):
                            if hasattr(item.action, 'query'):
                                logger.info(f"    🔍 Search query: {item.action.query}")

                        # 提取最终消息内容
                        if item.type == 'message' and hasattr(item, 'content'):
                            for content_block in item.content:
                                # 文本内容
                                if hasattr(content_block, 'text'):
                                    summary_parts.append(content_block.text)
                                    logger.info(f"  ✅ Found text content: {len(content_block.text)} chars")

                                    # 检查是否有 annotations (引用/链接)
                                    if hasattr(content_block, 'annotations'):
                                        for annotation in content_block.annotations:
                                            if hasattr(annotation, 'url'):
                                                citations.append({
                                                    'url': annotation.url,
                                                    'title': getattr(annotation, 'title', 'Unknown')
                                                })
                                                logger.info(f"  🔗 Citation: {annotation.title}")

            # 合并总结
            full_summary = "\n\n".join(summary_parts) if summary_parts else "No results found"

            logger.info(f"✅ ChatGPT Responses API 搜索完成")
            logger.info(f"📝 返回文本总结 ({len(summary_parts)} 部分)")
            logger.info(f"📚 Citations: {len(citations)} sources")

            return {
                "reviews": reviews,  # 暂时返回空列表，因为需要从文本中手动解析
                "summary": full_summary,
                "total_count": len(reviews),
                "source": "chatgpt_responses_api",
                "citations": citations,  # 引用来源列表
                "raw_response": full_summary
            }

        except Exception as e:
            logger.error(f"❌ ChatGPT Responses API 搜索失败: {e}")
            logger.exception(e)  # 打印完整堆栈跟踪
            return {
                "reviews": [],
                "summary": f"搜索失败: {str(e)}",
                "total_count": 0,
                "error": str(e)
            }


# 创建全局实例（懒加载）
_chatgpt_client = None

def get_chatgpt_client(api_key: str = None) -> ChatGPTSearchClient:
    """获取 ChatGPT 客户端实例"""
    global _chatgpt_client

    if _chatgpt_client is None:
        _chatgpt_client = ChatGPTSearchClient(api_key=api_key)

    return _chatgpt_client
