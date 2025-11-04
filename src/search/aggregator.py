"""
搜索聚合器 - 最优方案
整合 Outscraper（Google Maps）+ ChatGPT（Facebook/论坛）
"""

import logging
from typing import Dict, List
from src.search.outscraper_client import get_outscraper_client
from src.search.chatgpt_search import get_chatgpt_client
from src.cache.manager import cache_manager

logger = logging.getLogger(__name__)


class SearchAggregator:
    """
    搜索聚合器 - 简化版

    数据源：
    1. Outscraper（关键词搜索 Google Maps 评价）
    2. ChatGPT（web search Facebook 和论坛）
    """

    def __init__(self):
        """初始化搜索聚合器"""
        self.outscraper_client = get_outscraper_client()
        self.chatgpt_client = get_chatgpt_client()

        logger.info("🚀 搜索聚合器已初始化（最优方案）")
        logger.info(f"  - Outscraper: {'✅ 已启用' if self.outscraper_client.enabled else '❌ 未配置'}")
        logger.info(f"  - ChatGPT: {'✅ 已启用' if self.chatgpt_client.enabled else '❌ 未配置'}")

    async def search_doctor_reviews(
        self,
        doctor_name: str,
        location: str = "Malaysia",
        specialty: str = ""
    ) -> Dict:
        """
        搜索医生评价（最优方案）

        流程：
        1. 检查缓存
        2. Outscraper：搜索 Google Maps 评价（关键词搜索）
        3. ChatGPT：搜索 Facebook + 论坛（web search）
        4. 合并结果
        5. 缓存结果

        Args:
            doctor_name: 医生名字
            location: 地点（默认 Malaysia）
            specialty: 专科（可选，暂未使用）

        Returns:
            {
                "doctor_name": "Dr. Nicholas Lim",
                "doctor_id": "...",
                "reviews": [...],
                "google_maps_count": 5,
                "facebook_forums_count": 3,
                "total_count": 8,
                "sources": ["outscraper", "chatgpt"],
                "chatgpt_summary": "..."
            }
        """
        try:
            # 生成医生 ID
            doctor_id = cache_manager.generate_doctor_id(doctor_name, specialty, location)

            logger.info(f"🔍 搜索医生评价: {doctor_name} ({doctor_id})")

            # 步骤 1：检查缓存（如果数据库可用）
            try:
                cached_reviews = await cache_manager.get_cached_reviews(doctor_id)

                if cached_reviews:
                    logger.info(f"✅ 使用缓存结果：{len(cached_reviews)} 条评价")
                    return {
                        "doctor_name": doctor_name,
                        "doctor_id": doctor_id,
                        "reviews": cached_reviews,
                        "source": "cache",
                        "total_count": len(cached_reviews)
                    }
            except Exception as cache_error:
                logger.warning(f"⚠️ 缓存检查失败（可能数据库未初始化）: {cache_error}")

            # 步骤 2：Outscraper - Google Maps 评价（关键词搜索）
            all_reviews = []
            google_maps_count = 0
            facebook_forums_count = 0
            chatgpt_summary = ""

            if self.outscraper_client.enabled:
                logger.info(f"📍 Outscraper 关键词搜索...")

                outscraper_result = await self.outscraper_client.search_doctor_reviews(
                    doctor_name=doctor_name,
                    location=location,
                    limit=20  # 最多 20 条评价
                )

                outscraper_reviews = outscraper_result.get("reviews", [])
                google_maps_count = len(outscraper_reviews)

                if outscraper_reviews:
                    logger.info(f"✅ Outscraper 找到 {google_maps_count} 条 Google Maps 评价")
                    all_reviews.extend(outscraper_reviews)
                else:
                    logger.warning("⚠️ Outscraper 未找到评价")
            else:
                logger.warning("⚠️ Outscraper 未配置，跳过 Google Maps 搜索")

            # 步骤 3：ChatGPT - Facebook + 论坛
            if self.chatgpt_client.enabled:
                logger.info(f"🤖 ChatGPT 搜索 Facebook 和论坛...")

                chatgpt_result = await self.chatgpt_client.search_facebook_and_forums(
                    doctor_name=doctor_name,
                    location=location
                )

                chatgpt_reviews = chatgpt_result.get("reviews", [])
                chatgpt_summary = chatgpt_result.get("summary", "")
                chatgpt_citations = chatgpt_result.get("citations", [])
                facebook_forums_count = len(chatgpt_reviews)

                # Responses API 返回 summary 和 citations，而不是结构化的 reviews
                # 检查是否有实质内容（summary 或 citations）
                has_content = (
                    chatgpt_summary and chatgpt_summary != "No results found" and len(chatgpt_summary) > 50
                ) or len(chatgpt_citations) > 0

                if chatgpt_reviews:
                    logger.info(f"✅ ChatGPT 找到 {facebook_forums_count} 条 Facebook/论坛评价")
                    all_reviews.extend(chatgpt_reviews)
                elif has_content:
                    logger.info(f"✅ ChatGPT 找到患者评价信息（{len(chatgpt_citations)} 个来源）")
                    # 即使没有结构化 reviews，也记录找到了内容
                else:
                    logger.warning("⚠️ ChatGPT 未找到评价")
            else:
                logger.warning("⚠️ ChatGPT 未配置，跳过 Facebook/论坛搜索")

            # 步骤 4：合并结果
            total_count = len(all_reviews)

            # 检查是否有任何有价值的内容（结构化评价或 ChatGPT summary）
            has_chatgpt_content = chatgpt_summary and chatgpt_summary != "No results found" and len(chatgpt_summary) > 50

            if total_count == 0 and not has_chatgpt_content:
                logger.warning(f"❌ 未找到 {doctor_name} 的评价")
                return {
                    "doctor_name": doctor_name,
                    "doctor_id": doctor_id,
                    "reviews": [],
                    "google_maps_count": 0,
                    "facebook_forums_count": 0,
                    "total_count": 0,
                    "chatgpt_summary": chatgpt_summary if 'chatgpt_summary' in locals() else "",
                    "chatgpt_citations": chatgpt_citations if 'chatgpt_citations' in locals() else [],
                    "message": "未找到评价，建议尝试不同的医生名字拼写"
                }

            logger.info(f"✅ 搜索完成：共 {total_count} 条评价（Google Maps: {google_maps_count}, Facebook/论坛: {facebook_forums_count}）")

            # 步骤 5：缓存结果（如果数据库可用）
            try:
                await cache_manager.save_reviews(doctor_id, doctor_name, all_reviews)
            except Exception as cache_error:
                logger.warning(f"⚠️ 缓存保存失败（可能数据库未初始化）: {cache_error}")

            # 返回结果
            result_message = f"找到 {total_count} 条评价"
            if total_count == 0 and has_chatgpt_content:
                result_message = f"找到患者评价信息（来自 {len(chatgpt_citations)} 个来源）"

            return {
                "doctor_name": doctor_name,
                "doctor_id": doctor_id,
                "reviews": all_reviews,
                "google_maps_count": google_maps_count,
                "facebook_forums_count": facebook_forums_count,
                "total_count": total_count,
                "sources": ["outscraper", "chatgpt"],
                "chatgpt_summary": chatgpt_summary if 'chatgpt_summary' in locals() else "",
                "chatgpt_citations": chatgpt_citations if 'chatgpt_citations' in locals() else [],
                "message": result_message
            }

        except Exception as e:
            logger.error(f"❌ 搜索失败: {e}")
            return {
                "doctor_name": doctor_name,
                "reviews": [],
                "total_count": 0,
                "error": str(e)
            }


# 创建全局实例
search_aggregator = SearchAggregator()
