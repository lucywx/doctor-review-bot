"""
Search aggregator - uses Google Custom Search + OpenAI for doctor reviews
"""

import logging
from typing import List, Dict
from src.search.google_searcher import google_searcher
from src.search.openai_web_searcher import openai_web_searcher
from src.search.google_places import google_places_client
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

                # Use GPT-4 to analyze HTML and extract actual patient reviews
                logger.info(f"🤖 Using GPT-4 to analyze pages and extract genuine patient reviews...")
                extraction_result = await google_searcher.extract_content_with_openai(
                    urls=urls,
                    doctor_name=doctor_name
                )

                all_reviews = extraction_result.get("reviews", [])
                source = extraction_result.get("source", "google + gpt4")

                logger.info(f"✅ Extracted {len(all_reviews)} genuine patient reviews")
            else:
                logger.warning("⚠️ No URLs found via Google Search")

            # Step 3: Try Google Places API for Google Maps reviews
            if google_places_client.enabled:
                logger.info(f"🗺️ Fetching Google Maps reviews via Places API...")
                places_result = await google_places_client.search_doctor(
                    doctor_name=doctor_name,
                    location=search_location
                )

                if places_result and places_result.get("reviews"):
                    places_reviews = places_result["reviews"]

                    if places_reviews:
                        logger.info(f"📍 Place: {places_result.get('name', 'Unknown')} (Total reviews: {places_result.get('total_reviews', 0)})")
                        logger.info(f"🔍 Found {len(places_reviews)} raw Google Maps reviews")
                        logger.info(f"🤖 Using GPT-4 to filter reviews about {doctor_name}...")

                        # Use GPT-4 to intelligently filter Google Maps reviews
                        filtered_reviews = await self._filter_google_maps_reviews_with_gpt(
                            reviews=places_reviews,
                            doctor_name=doctor_name,
                            place_name=places_result.get('name', 'Unknown'),
                            google_maps_url=places_result.get("url", "")
                        )

                        if filtered_reviews:
                            logger.info(f"✅ GPT-4 filtered {len(places_reviews)} → {len(filtered_reviews)} reviews about {doctor_name}")
                            all_reviews.extend(filtered_reviews)
                            source = f"{source} + google_maps"
                        else:
                            logger.info(f"ℹ️ No Google Maps reviews are actually about {doctor_name} (filtered by GPT-4)")

                        # Add Google Maps link as a hint for users to see all reviews
                        google_maps_url = places_result.get("url", "")
                        if google_maps_url:
                            all_reviews.append({
                                "snippet": f"📍 See all {places_result.get('total_reviews', 0)} reviews on Google Maps (API shows max 5, may not include reviews mentioning {doctor_name})",
                                "url": google_maps_url,
                                "review_date": "",
                                "source": "Google Maps Link"
                            })
                            logger.info(f"Added Google Maps link for {places_result.get('total_reviews', 0)} total reviews")
                    else:
                        logger.info(f"ℹ️ No Google Maps reviews returned from Places API")
                else:
                    logger.info("ℹ️ No Google Maps place found via Places API")
            else:
                logger.info("ℹ️ Google Places API not configured, skipping Google Maps reviews")

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

    async def _filter_google_maps_reviews_with_gpt(
        self,
        reviews: List[Dict],
        doctor_name: str,
        place_name: str,
        google_maps_url: str
    ) -> List[Dict]:
        """
        Use GPT-4 to intelligently filter Google Maps reviews
        Only keep reviews that are actually about the specific doctor

        Args:
            reviews: List of raw Google Maps reviews
            doctor_name: Doctor's name
            place_name: Name of the place (hospital/clinic)
            google_maps_url: Google Maps URL

        Returns:
            List of filtered reviews that are about the doctor
        """
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)

        # Prepare reviews for analysis
        reviews_text = "\n\n".join([
            f"Review {i+1}:\n{review['text']}"
            for i, review in enumerate(reviews)
        ])

        prompt = f"""You are analyzing Google Maps reviews for {place_name}.

Your task: Identify which reviews are specifically about **{doctor_name}** (the doctor).

Reviews to analyze:
{reviews_text}

Instructions:
1. Read each review carefully
2. A review is about {doctor_name} if it:
   - Mentions the doctor's name (or clear variations like "Dr. {doctor_name.split()[0]}")
   - Describes their medical care, diagnosis, treatment, or bedside manner
   - Is clearly a patient's experience with this specific doctor

3. A review is NOT about {doctor_name} if it:
   - Only mentions other doctors' names
   - Is about hospital facilities, nurses, admin staff, or general hospital experience
   - Doesn't mention any specific doctor

Output format:
Return ONLY a JSON array of review numbers that ARE about {doctor_name}.
Example: [1, 3] or [] if none match.

Your response:"""

        try:
            response = await client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=100
            )

            result_text = response.choices[0].message.content.strip()
            logger.debug(f"GPT-4 filtering result: {result_text}")

            # Parse the result
            import json
            import re

            # Extract JSON array from response
            json_match = re.search(r'\[[\d\s,]*\]', result_text)
            if json_match:
                relevant_indices = json.loads(json_match.group())

                # Filter reviews based on GPT-4's analysis
                filtered = []
                for idx in relevant_indices:
                    if 1 <= idx <= len(reviews):
                        review = reviews[idx - 1].copy()
                        review["url"] = google_maps_url
                        review["source"] = "Google Maps"
                        filtered.append(review)

                return filtered
            else:
                logger.warning("Could not parse GPT-4 response for review filtering")
                return []

        except Exception as e:
            logger.error(f"Error using GPT-4 to filter Google Maps reviews: {e}")
            return []

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
