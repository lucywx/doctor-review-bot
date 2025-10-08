"""
Search aggregator - coordinates all search engines and caching
"""

import asyncio
import logging
from typing import List, Dict
from src.search.google_places import google_places_searcher
from src.search.facebook import facebook_searcher
from src.search.mock_searcher import mock_searcher
from src.analysis.sentiment import sentiment_analyzer
from src.cache.manager import cache_manager
from src.config import settings

logger = logging.getLogger(__name__)

# Use mock searcher if API keys are not set (development or production)
USE_MOCK = (
    settings.google_places_api_key == "your_google_api_key" or
    settings.facebook_access_token == "your_facebook_token"
)


class SearchAggregator:
    """
    Aggregates search results from multiple sources
    Handles caching and sentiment analysis
    """

    async def search_doctor_reviews(
        self,
        doctor_name: str,
        location: str = ""
    ) -> Dict:
        """
        Search for doctor reviews across all sources

        Args:
            doctor_name: Doctor's name
            location: Optional location

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

            # Step 2: Search all sources in parallel
            if USE_MOCK:
                logger.info("🧪 Using MOCK searcher (no real API keys)")
                mock_result = await mock_searcher.search_doctor(doctor_name, location)
                all_reviews = mock_result.get("reviews", [])
            else:
                logger.info("🌐 Searching all sources...")
                search_tasks = [
                    google_places_searcher.search_doctor(doctor_name, location),
                    facebook_searcher.search_doctor(doctor_name)
                ]

                results = await asyncio.gather(*search_tasks, return_exceptions=True)

                # Combine results
                all_reviews = []
                for result in results:
                    if isinstance(result, list):
                        all_reviews.extend(result)
                    elif isinstance(result, Exception):
                        logger.error(f"Search error: {result}")

            if not all_reviews:
                logger.info(f"❌ No reviews found for {doctor_name}")
                return {
                    "doctor_name": doctor_name,
                    "doctor_id": doctor_id,
                    "reviews": [],
                    "source": "fresh",
                    "total_count": 0
                }

            logger.info(f"📊 Found {len(all_reviews)} total reviews from all sources")

            # Step 3: Analyze sentiment
            logger.info("🤖 Analyzing sentiment...")
            analyzed_reviews = await sentiment_analyzer.analyze_reviews(all_reviews)

            # Step 4: Save to cache
            logger.info("💾 Saving to cache...")
            await cache_manager.save_reviews(
                doctor_id=doctor_id,
                doctor_name=doctor_name,
                reviews=analyzed_reviews,
                ttl_days=7
            )

            return {
                "doctor_name": doctor_name,
                "doctor_id": doctor_id,
                "reviews": analyzed_reviews,
                "source": "fresh",
                "total_count": len(analyzed_reviews)
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
