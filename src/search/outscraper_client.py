"""
Outscraper Google Maps API 客户端
支持关键词搜索 Google Maps 评价
"""

import asyncio
import httpx
import time
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class OutscraperClient:
    """Outscraper API 客户端 - 简化版，专注于医生评价搜索"""

    def __init__(self, api_key: str):
        """
        初始化 Outscraper 客户端

        Args:
            api_key: Outscraper API key
        """
        self.api_key = api_key
        self.base_url = "https://api.app.outscraper.com"

        if not api_key or api_key == "your_outscraper_api_key":
            logger.warning("Outscraper API key not configured")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("✅ Outscraper client initialized")

    async def search_doctor_reviews(
        self,
        doctor_name: str,
        location: str = "Malaysia",
        limit: int = 20
    ) -> Dict:
        """
        搜索医生的 Google Maps 评价（关键词搜索）⭐

        这是核心功能：直接搜索包含医生名字的评价

        Args:
            doctor_name: 医生名字（例如 "Dr. Nicholas Lim"）
            location: 地点（默认 Malaysia）
            limit: 最多返回多少条评价

        Returns:
            {
                "reviews": [...],  # 评价列表
                "total_count": 10,  # 找到的评价数量
                "source": "outscraper_keyword_search"
            }
        """
        if not self.enabled:
            logger.warning("Outscraper not enabled")
            return {"reviews": [], "total_count": 0, "error": "API key not configured"}

        try:
            # 构建搜索查询
            query = f"{doctor_name} {location}"

            logger.info(f"🔍 Outscraper 关键词搜索: {doctor_name}")

            # Outscraper API endpoint for Google Maps Reviews
            url = f"{self.base_url}/maps/reviews-v3"

            params = {
                "query": query,
                "reviewsLimit": limit,  # 最多抓取多少条评价
                "reviewsQuery": doctor_name,  # ⭐ 关键词过滤：只返回包含医生名字的评价
                "language": "en",
                "region": "MY",  # Malaysia
                "async": False  # 同步请求
            }

            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }

            # 发送请求
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(url, params=params, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    reviews = self._parse_reviews(data, doctor_name)

                    logger.info(f"✅ Outscraper 找到 {len(reviews)} 条包含 '{doctor_name}' 的评价")

                    return {
                        "reviews": reviews,
                        "total_count": len(reviews),
                        "source": "outscraper_keyword_search",
                        "query": query
                    }

                elif response.status_code == 401:
                    logger.error("❌ Outscraper API key 无效")
                    return {"reviews": [], "total_count": 0, "error": "Invalid API key"}

                elif response.status_code == 429:
                    logger.error("❌ Outscraper API 请求过于频繁")
                    return {"reviews": [], "total_count": 0, "error": "Rate limit exceeded"}

                else:
                    logger.error(f"❌ Outscraper API 错误: {response.status_code}")
                    return {"reviews": [], "total_count": 0, "error": f"HTTP {response.status_code}"}

        except Exception as e:
            logger.error(f"❌ Outscraper 搜索失败: {e}")
            return {"reviews": [], "total_count": 0, "error": str(e)}

    def _parse_reviews(self, data: Dict, doctor_name: str) -> List[Dict]:
        """
        解析 Outscraper API 响应

        Args:
            data: API 响应数据
            doctor_name: 医生名字（用于记录）

        Returns:
            评价列表
        """
        reviews = []

        try:
            # Outscraper 返回格式：
            # {
            #   "data": [
            #     {
            #       "name": "Hospital Name",
            #       "reviews_data": [
            #         {
            #           "author_title": "John Doe",
            #           "review_text": "Dr. Nicholas is great...",
            #           "review_rating": 5,
            #           "review_datetime_utc": "2024-01-15",
            #           ...
            #         }
            #       ]
            #     }
            #   ]
            # }

            if "data" not in data:
                return reviews

            for place in data.get("data", []):
                place_name = place.get("name", "Unknown Place")
                place_url = place.get("google_maps_url", "")

                for review in place.get("reviews_data", []):
                    review_text = review.get("review_text", "")

                    # Outscraper 的 reviewsQuery 参数已经帮我们过滤了
                    # 但我们再检查一下确保包含医生名字
                    if doctor_name.lower() in review_text.lower():
                        # 标准化字段名，与 ChatGPT 搜索保持一致
                        reviews.append({
                            "text": review_text,                                    # 评价内容
                            "rating": review.get("review_rating", 0),              # 评分
                            "author_name": review.get("author_title", "Anonymous"), # 患者姓名
                            "review_date": review.get("review_datetime_utc", ""),  # 发布日期
                            "place_name": place_name,                               # 地点名称
                            "url": place_url,                                       # 评价链接
                            "source": "google_maps"                                 # 来源
                        })

        except Exception as e:
            logger.error(f"解析 Outscraper 响应失败: {e}")

        return reviews


# 创建全局实例（懒加载）
_outscraper_client = None

def get_outscraper_client(api_key: str = None) -> OutscraperClient:
    """获取 Outscraper 客户端实例"""
    global _outscraper_client

    if _outscraper_client is None:
        import os
        key = api_key or os.getenv("OUTSCRAPER_API_KEY", "")
        _outscraper_client = OutscraperClient(api_key=key)

    return _outscraper_client
