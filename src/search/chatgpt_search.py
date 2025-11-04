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
            # 注：虽然较慢（90-120秒），但搜索质量最好
            response = await self.client.responses.create(
                model="gpt-5-mini",  # ⭐ 使用 gpt-5-mini
                tools=[{"type": "web_search"}],  # ⭐ 启用 web_search 工具
                reasoning={"effort": "low"},  # ⭐ 降低思考强度，可能减少搜索次数
                input=f"""Find patient reviews about {doctor_name} in {location}.

Search these specific sites:
- forum.lowyat.net
- motherhood.com.my
- theasianparent.com
- babycenter.com

Limit your search to 2-3 queries maximum. Focus on quality over quantity.

For each review found, provide:
- Review text (patient's actual words)
- Author name
- Date
- Source URL

Return specific patient testimonials only."""
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

            # 步骤 2：如果找到了内容，解析为结构化评价
            if full_summary and full_summary != "No results found" and len(full_summary) > 100:
                logger.info("🔄 解析文本总结为结构化评价...")
                structured_reviews = await self._parse_summary_to_reviews(
                    full_summary, citations, doctor_name
                )
                reviews.extend(structured_reviews)
                logger.info(f"✅ 提取了 {len(structured_reviews)} 条结构化评价")

            return {
                "reviews": reviews,
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

    async def _parse_summary_to_reviews(
        self,
        summary: str,
        citations: List[Dict],
        doctor_name: str
    ) -> List[Dict]:
        """
        将搜索总结解析为结构化评价列表

        Args:
            summary: Responses API 返回的文本总结
            citations: 引用来源列表
            doctor_name: 医生名字

        Returns:
            结构化评价列表
        """
        try:
            # 使用 gpt-4o-mini 解析文本为结构化数据（便宜且快速）
            parse_response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的评价信息提取助手。从搜索结果中提取患者评价，返回JSON格式。"
                    },
                    {
                        "role": "user",
                        "content": f"""从以下关于 {doctor_name} 的搜索结果中提取患者评价信息。

搜索结果：
{summary}

引用来源：
{json.dumps(citations, ensure_ascii=False, indent=2)}

请提取所有提到的患者评价，返回JSON格式：
{{
  "reviews": [
    {{
      "author_name": "患者姓名（如果提到）或 'Anonymous'",
      "review_date": "评价日期（YYYY-MM-DD格式，如果提到）或空字符串",
      "text": "评价内容（患者的原话或总结）",
      "rating": 评分（1-5，如果提到）或 0,
      "source": "来源网站名称",
      "url": "评价链接（从引用来源中匹配）"
    }}
  ]
}}

注意：
1. 提取所有明确的患者评价和体验
2. text 字段应该是患者的原话或体验描述
3. 如果同一来源有多条评价，分别提取
4. url 需要从引用来源列表中匹配对应的链接
5. 如果是论坛讨论，提取具体的评价内容，不要只说"有讨论"
"""
                    }
                ]
            )

            # 解析返回的 JSON
            result_text = parse_response.choices[0].message.content
            result_json = json.loads(result_text)

            parsed_reviews = result_json.get("reviews", [])

            # 标准化格式，添加 source 标识
            standardized_reviews = []
            for review in parsed_reviews:
                standardized_reviews.append({
                    "text": review.get("text", ""),
                    "rating": review.get("rating", 0),
                    "author_name": review.get("author_name", "Anonymous"),
                    "review_date": review.get("review_date", ""),
                    "url": review.get("url", ""),
                    "source": "facebook_forum",  # 来源标识
                    "place_name": review.get("source", "Community Review")
                })

            return standardized_reviews

        except Exception as e:
            logger.error(f"❌ 解析文本总结失败: {e}")
            return []


# 创建全局实例（懒加载）
_chatgpt_client = None

def get_chatgpt_client(api_key: str = None) -> ChatGPTSearchClient:
    """获取 ChatGPT 客户端实例"""
    global _chatgpt_client

    if _chatgpt_client is None:
        _chatgpt_client = ChatGPTSearchClient(api_key=api_key)

    return _chatgpt_client
