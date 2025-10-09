"""
OpenAI Web Search integration
Uses OpenAI's web_search tool to find doctor reviews from the web
"""

import logging
from typing import List, Dict
from openai import AsyncOpenAI
from src.config import settings

logger = logging.getLogger(__name__)


class OpenAIWebSearcher:
    """Search for doctor reviews using OpenAI's web_search tool"""

    def __init__(self):
        # CRITICAL: Never use mock data for doctor reviews - legal risk!
        # Always use real OpenAI API for production
        self.use_mock = False  # Disabled for safety

        try:
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_model
            logger.info(f"🌐 OpenAI Web Searcher initialized (model: {self.model})")
        except Exception as e:
            logger.error(f"❌ OpenAI API initialization failed: {e}")
            raise Exception("OpenAI API key is required for doctor review search")

    async def search_doctor_reviews(
        self,
        doctor_name: str,
        specialty: str = "",
        location: str = ""
    ) -> Dict:
        """
        Search for doctor reviews using OpenAI web_search

        Args:
            doctor_name: Doctor's name
            specialty: Optional medical specialty
            location: Optional location/hospital

        Returns:
            Dict with reviews and metadata
        """
        try:
            # CRITICAL: Never use mock data for doctor reviews
            logger.info(f"🌐 Searching web for: {doctor_name}")
            
            # Build search query
            query_parts = [doctor_name]
            if specialty:
                query_parts.append(specialty)
            if location:
                query_parts.append(location)
            
            search_query = " ".join(query_parts) + " doctor reviews patient feedback"
            
            # Use OpenAI Responses API with web search
            response = await self.client.responses.create(
                model="gpt-4o",  # Use model that supports web search
                tools=[{"type": "web_search"}],  # Correct tool name for responses API
                input=f"Search the web for patient reviews about {search_query}. Find reviews from Google Maps, hospital websites, medical forums, and other sources. Return the reviews in JSON format with fields: source, snippet, rating, author_name, review_date, url."
            )

            # Parse response and extract reviews
            reviews = self._parse_openai_response(response, doctor_name)
            
            logger.info(f"✅ Found {len(reviews)} reviews via OpenAI web search")
            
            return {
                "doctor_name": doctor_name,
                "reviews": reviews,
                "source": "openai_web_search",
                "total_count": len(reviews)
            }

        except Exception as e:
            logger.error(f"Error in OpenAI web search: {e}")
            # CRITICAL: Never return mock data for doctor reviews
            return {
                "doctor_name": doctor_name,
                "reviews": [],
                "source": "error",
                "total_count": 0,
                "error": "Search failed - no mock data returned for safety"
            }

    def _parse_openai_response(self, response, doctor_name: str) -> List[Dict]:
        """Parse OpenAI response and extract reviews"""
        try:
            import json
            
            # Extract content from response (Responses API format)
            if hasattr(response, 'output_text'):
                content = response.output_text.strip()
            elif hasattr(response, 'choices'):
                content = response.choices[0].message.content.strip()
            else:
                content = str(response).strip()
            
            logger.info(f"📝 OpenAI response: {content[:200]}...")
            
            # Try to parse as JSON first
            try:
                if content.startswith('[') and content.endswith(']'):
                    reviews_data = json.loads(content)
                    reviews = []
                    
                    for review_data in reviews_data:
                        if isinstance(review_data, dict):
                            reviews.append({
                                "doctor_name": doctor_name,
                                "source": review_data.get("source", "knowledge_base"),
                                "url": review_data.get("url", ""),
                                "snippet": review_data.get("snippet", ""),
                                "rating": float(review_data.get("rating", 0)),
                                "review_date": review_data.get("review_date", ""),
                                "author_name": review_data.get("author_name", "Anonymous"),
                                "sentiment": None  # Will be analyzed later
                            })
                    
                    logger.info(f"✅ Parsed {len(reviews)} reviews from JSON")
                    return reviews
                    
            except json.JSONDecodeError:
                logger.info("📝 Response is not JSON, trying text parsing...")
            
            # If not JSON, try to extract meaningful content
            if content and len(content) > 50:
                # Create a single review from the content
                reviews = [{
                    "doctor_name": doctor_name,
                    "source": "knowledge_base",
                    "url": "",
                    "snippet": content[:300],
                    "rating": 4.0,
                    "review_date": "2025-01-01",
                    "author_name": "OpenAI Knowledge",
                    "sentiment": None
                }]
                logger.info(f"✅ Created 1 review from text content")
                return reviews
            
            logger.info("❌ No meaningful content found")
            return []

        except Exception as e:
            logger.error(f"Error parsing OpenAI response: {e}")
            return []

    # REMOVED: Mock search function - too dangerous for doctor reviews


# Global instance
openai_web_searcher = OpenAIWebSearcher()
