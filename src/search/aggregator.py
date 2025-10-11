"""
Search aggregator - uses OpenAI web search for doctor reviews
"""

import logging
from typing import List, Dict
from src.search.openai_web_searcher import openai_web_searcher
from src.cache.manager import cache_manager
from src.config import settings

logger = logging.getLogger(__name__)


class SearchAggregator:
    """
    Uses OpenAI web search to find doctor reviews
    Handles caching and sentiment analysis
    """

    async def search_doctor_reviews(
        self,
        doctor_name: str,
        location: str = "",
        specialty: str = ""
    ) -> Dict:
        """
        Search for doctor reviews using OpenAI web search

        Args:
            doctor_name: Doctor's name
            location: Optional location
            specialty: Optional medical specialty

        Returns:
            Dict with reviews and metadata
        """
        try:
            # Generate doctor ID
            doctor_id = cache_manager.generate_doctor_id(doctor_name, "", location)

            logger.info(f"🔍 Searching for: {doctor_name} (ID: {doctor_id})")

            # Step 1: Check cache
            cached_reviews = await cache_manager.get_cached_reviews(doctor_id)

            if cached_reviews:
                logger.info(f"✅ Using {len(cached_reviews)} cached reviews")
                return {
                    "doctor_name": doctor_name,
                    "doctor_id": doctor_id,
                    "reviews": cached_reviews,
                    "source": "cache",
                    "total_count": len(cached_reviews)
                }

            # Step 2: Search using OpenAI web search
            logger.info("🌐 Searching web via OpenAI...")
            search_result = await openai_web_searcher.search_doctor_reviews(
                doctor_name=doctor_name,
                specialty=specialty,
                location=location
            )

            all_reviews = search_result.get("reviews", [])

            # Step 2.5: Fallback - if no results with specialty, try without specialty
            if not all_reviews and specialty:
                logger.warning(f"⚠️ No results with specialty '{specialty}', retrying without it...")
                search_result = await openai_web_searcher.search_doctor_reviews(
                    doctor_name=doctor_name,
                    specialty="",  # Remove specialty
                    location=location
                )
                all_reviews = search_result.get("reviews", [])

                if all_reviews:
                    logger.info(f"✅ Found {len(all_reviews)} reviews without specialty filter")

            if not all_reviews:
                logger.info(f"❌ No reviews found for {doctor_name}")
                return {
                    "doctor_name": doctor_name,
                    "doctor_id": doctor_id,
                    "reviews": [],
                    "source": "fresh",
                    "total_count": 0
                }

            logger.info(f"📊 Found {len(all_reviews)} reviews from web search")

            # Step 3: Save to cache (sentiment analysis removed for speed)
            logger.info("💾 Saving to cache...")
            await cache_manager.save_reviews(
                doctor_id=doctor_id,
                doctor_name=doctor_name,
                reviews=all_reviews,
                ttl_days=7
            )

            return {
                "doctor_name": doctor_name,
                "doctor_id": doctor_id,
                "reviews": all_reviews,
                "source": "fresh",
                "total_count": len(all_reviews)
            }

        except Exception as e:
            logger.error(f"Error in search aggregator: {e}", exc_info=True)
            return {
                "doctor_name": doctor_name,
                "reviews": [],
                "error": str(e)
            }

    async def get_review_statistics(self, doctor_id: str) -> Dict:
        """
        Get statistics for cached reviews

        Args:
            doctor_id: Doctor's unique ID

        Returns:
            Statistics dict
        """
        try:
            reviews = await cache_manager.get_cached_reviews(doctor_id)

            if not reviews:
                return {"total": 0}

            positive = len([r for r in reviews if r.get("sentiment") == "positive"])
            negative = len([r for r in reviews if r.get("sentiment") == "negative"])
            neutral = len([r for r in reviews if r.get("sentiment") == "neutral"])

            return {
                "total": len(reviews),
                "positive": positive,
                "negative": negative,
                "neutral": neutral,
                "sentiment_breakdown": {
                    "positive": f"{positive/len(reviews)*100:.1f}%",
                    "negative": f"{negative/len(reviews)*100:.1f}%",
                    "neutral": f"{neutral/len(reviews)*100:.1f}%"
                }
            }

        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {"total": 0, "error": str(e)}


# Global instance
search_aggregator = SearchAggregator()
