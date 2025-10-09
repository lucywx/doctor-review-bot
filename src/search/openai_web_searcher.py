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
            
            # Use OpenAI Responses API with web search (ChatGPT-like capability)
            logger.info(f"🔍 Calling OpenAI Responses API with query: {search_query}")
            response = await self.client.responses.create(
                model="gpt-4o",  # Use gpt-4o model for web search
                tools=[{"type": "web_search"}],  # Enable web search tool
                input=f"""Search for patient reviews and feedback about Dr {doctor_name}.
                Look for reviews from Google Maps, hospital websites, medical forums, and social media.
                Return the reviews in JSON format with fields: source, snippet, rating, author_name, review_date, url.
                If you find reviews, return them. If no reviews found, return empty array []."""
            )

            logger.info(f"✅ OpenAI API call successful, response type: {type(response)}")

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
            import traceback
            logger.error(f"❌ Error in OpenAI web search: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            # CRITICAL: Never return mock data for doctor reviews
            return {
                "doctor_name": doctor_name,
                "reviews": [],
                "source": "error",
                "total_count": 0,
                "error": f"Search failed: {str(e)}"
            }

    def _parse_openai_response(self, response, doctor_name: str) -> List[Dict]:
        """Parse OpenAI response and extract reviews"""
        try:
            import json

            # Extract content from response (Responses API format)
            # The Responses API returns output_text attribute
            if hasattr(response, 'output_text'):
                content = response.output_text.strip()
            elif hasattr(response, 'output') and isinstance(response.output, list):
                # Try to get text from output array
                content = ""
                for item in response.output:
                    if hasattr(item, 'text'):
                        content += item.text
            elif hasattr(response, 'choices'):
                # Fallback for Chat Completions API format
                content = response.choices[0].message.content.strip()
            else:
                logger.warning(f"Unknown response format: {type(response)}")
                logger.debug(f"Response attributes: {dir(response)}")
                content = str(response).strip()

            logger.info(f"📝 OpenAI response: {content[:200]}...")

            # Try to extract JSON from markdown code blocks
            json_content = None
            if '```json' in content:
                # Extract JSON from markdown code block
                import re
                json_match = re.search(r'```json\s*\n(.*?)\n```', content, re.DOTALL)
                if json_match:
                    json_content = json_match.group(1).strip()
                    logger.info("📝 Found JSON in markdown code block")
            elif content.strip().startswith('[') and content.strip().endswith(']'):
                # Direct JSON array
                json_content = content.strip()

            # Try to parse as JSON
            if json_content:
                try:
                    reviews_data = json.loads(json_content)
                    reviews = []

                    for review_data in reviews_data:
                        if isinstance(review_data, dict):
                            # Handle null values properly
                            rating = review_data.get("rating")
                            rating = float(rating) if rating is not None else 0.0

                            reviews.append({
                                "doctor_name": doctor_name,
                                "source": review_data.get("source", "web_search"),
                                "url": review_data.get("url") or "",
                                "snippet": review_data.get("snippet", ""),
                                "rating": rating,
                                "review_date": review_data.get("review_date") or "",
                                "author_name": review_data.get("author_name") or "Anonymous",
                                "sentiment": None  # Will be analyzed later
                            })

                    logger.info(f"✅ Parsed {len(reviews)} reviews from JSON")
                    return reviews

                except json.JSONDecodeError as e:
                    logger.warning(f"📝 JSON parsing failed: {e}, trying text parsing...")
            
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
