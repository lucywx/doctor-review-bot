"""
Search aggregator - uses Google Custom Search + OpenAI for doctor reviews
"""

import logging
from typing import List, Dict
from src.search.google_searcher import google_searcher
from src.search.openai_web_searcher import openai_web_searcher
from src.cache.manager import cache_manager
from src.config import settings

logger = logging.getLogger(__name__)


class SearchAggregator:
    """
    Uses Google Custom Search to find URLs, then OpenAI to extract reviews
    Falls back to OpenAI web search if Google is not configured
    Handles caching and sentiment analysis
    """

    async def search_doctor_reviews(
        self,
        doctor_name: str,
        location: str = "",
        specialty: str = ""
    ) -> Dict:
        """
        Search for doctor reviews using Google Custom Search ONLY

        Strategy:
        1. Check cache first
        2. Use Google Custom Search to find relevant URLs and extract snippets
        3. Google search results provide snippets that work as reviews

        Args:
            doctor_name: Doctor's name
            location: City/hospital name in Malaysia (defaults to "Malaysia" if empty)
            specialty: Optional medical specialty (not used, kept for compatibility)

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

            # Step 2: Use Google Custom Search ONLY
            search_location = location or "Malaysia"
            all_reviews = []
            source = "google_custom_search"

            if not settings.google_search_api_key or not settings.google_search_engine_id:
                logger.error("❌ Google Search API not configured! Please add credentials to .env")
                return {
                    "doctor_name": doctor_name,
                    "doctor_id": doctor_id,
                    "reviews": [],
                    "source": "error",
                    "total_count": 0,
                    "error": "Google Search API not configured"
                }

            logger.info(f"🔍 Using Google Custom Search to find reviews...")

            # Find URLs using Google
            google_result = await google_searcher.search_doctor_reviews(
                doctor_name=doctor_name,
                specialty=specialty,
                location=search_location
            )

            urls = google_result.get("urls", [])

            if urls:
                logger.info(f"📍 Found {len(urls)} URLs from Google Search")

                # Use Google search snippets directly as reviews
                # No need to call OpenAI - saves cost and time
                all_reviews = []
                for url_data in urls:
                    # Extract snippet from Google search result
                    snippet = url_data.get("snippet", "")
                    if snippet and len(snippet) > 20:  # Filter out very short snippets
                        all_reviews.append({
                            "snippet": snippet,
                            "url": url_data.get("url", ""),
                            "source": url_data.get("source", "google_custom_search"),
                            "review_date": "",  # Google results don't include dates
                            "sentiment": None
                        })

                logger.info(f"✅ Extracted {len(all_reviews)} reviews from Google search results")
            else:
                logger.warning("⚠️ No results found via Google Search")

            # NOTE: OpenAI web_search code is preserved below but not used
            # Uncomment if you want to use OpenAI as fallback
            #
            # if not all_reviews:
            #     logger.info(f"🌐 Falling back to OpenAI web search...")
            #     search_result = await openai_web_searcher.search_doctor_reviews(
            #         doctor_name=doctor_name,
            #         specialty=specialty,
            #         location=search_location
            #     )
            #     all_reviews = search_result.get("reviews", [])
            #     source = "openai_web_search"

            if not all_reviews:
                logger.info(f"❌ No reviews found for {doctor_name}")
                return {
                    "doctor_name": doctor_name,
                    "doctor_id": doctor_id,
                    "reviews": [],
                    "source": source,
                    "total_count": 0
                }

            logger.info(f"📊 Found {len(all_reviews)} reviews total")

            # Step 4: Save to cache (sentiment analysis removed for speed)
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
                "source": source,
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
