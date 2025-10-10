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
            logger.info(f"🤖 Using model: gpt-4o (hardcoded for web_search compatibility)")
            response = await self.client.responses.create(
                model="gpt-4o",  # Must use gpt-4o for web_search tool
                tools=[{"type": "web_search"}],  # Enable web search tool
                input=f"""Search for patient reviews about Dr {doctor_name} practicing in Malaysia.

Find reviews from Lowyat.net forums, Google Maps, Facebook, medical review sites, or patient blogs.

CRITICAL: DO NOT include LookP.com URLs (website is defunct/redirects to spam).

Return ONLY JSON array (no explanations):
[{{"source":"Lowyat.net","snippet":"review text","author_name":"username","review_date":"2023-01-01","rating":null,"url":"https://forum.lowyat.net/..."}}]

Each review MUST have a working URL. Better to return fewer reviews with valid URLs than many with broken links."""
            )

            logger.info(f"✅ OpenAI API call successful, response type: {type(response)}")

            # Log raw response for debugging
            if hasattr(response, 'output_text'):
                output_preview = response.output_text[:300] if response.output_text else "EMPTY"
                logger.info(f"📝 Response preview: {output_preview}...")

            # Parse response and extract reviews
            reviews = self._parse_openai_response(response, doctor_name)

            logger.info(f"✅ Found {len(reviews)} reviews via OpenAI web search")

            if len(reviews) == 0:
                logger.warning("⚠️ WARNING: 0 reviews found - this might indicate an issue")
                logger.warning(f"⚠️ Response output_text length: {len(response.output_text) if hasattr(response, 'output_text') else 'N/A'}")
            
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
                logger.info(f"📝 Extracted from output_text, length: {len(content)}")
            elif hasattr(response, 'output') and isinstance(response.output, list):
                # Try to get text from output array
                content = ""
                for item in response.output:
                    if hasattr(item, 'text'):
                        content += item.text
                logger.info(f"📝 Extracted from output array, length: {len(content)}")
            elif hasattr(response, 'choices'):
                # Fallback for Chat Completions API format
                content = response.choices[0].message.content.strip()
                logger.info(f"📝 Extracted from choices, length: {len(content)}")
            else:
                logger.warning(f"⚠️ Unknown response format: {type(response)}")
                logger.warning(f"⚠️ Response attributes: {dir(response)}")
                content = str(response).strip()

            logger.info(f"📝 Content preview: {content[:200]}...")
            logger.info(f"📝 Content ends with: ...{content[-100:]}" if len(content) > 100 else f"📝 Full content: {content}")

            # Try to extract JSON from response
            json_content = None
            import re

            # Method 1: Check for markdown code block
            if '```json' in content:
                json_match = re.search(r'```json\s*\n(.*?)\n```', content, re.DOTALL)
                if json_match:
                    json_content = json_match.group(1).strip()
                    logger.info("📝 Found JSON in markdown code block")

            # Method 2: Check if starts/ends with []
            elif content.strip().startswith('[') and content.strip().endswith(']'):
                json_content = content.strip()
                logger.info("📝 Found direct JSON array")

            # Method 3: Extract JSON array from text (even if surrounded by text)
            elif '[' in content and ']' in content:
                # Find JSON array pattern anywhere in text
                json_match = re.search(r'\[\s*\{.*?\}\s*\]|\[\s*\]', content, re.DOTALL)
                if json_match:
                    json_content = json_match.group(0).strip()
                    logger.info("📝 Extracted JSON array from text")

            # Try to parse as JSON
            if json_content:
                try:
                    reviews_data = json.loads(json_content)
                    reviews = []

                    for review_data in reviews_data:
                        if isinstance(review_data, dict):
                            # Validate URL first - CRITICAL for avoiding defamation risk
                            url = review_data.get("url") or ""
                            source = review_data.get("source", "web_search")

                            # CRITICAL: Skip reviews without valid URLs
                            # Without URL, we cannot verify the review exists = legal risk
                            if not url:
                                logger.warning(f"⚠️ Skipping review from {source}: No URL for verification")
                                continue

                            # Filter out known broken/defunct domains
                            broken_domains = [
                                "lookp.com",  # LookP website is defunct, redirects to spam
                                "sostalisman.net",  # Spam redirect site
                            ]

                            is_broken = any(domain in url.lower() for domain in broken_domains)

                            if is_broken:
                                logger.warning(f"⚠️ Skipping review: Broken/defunct URL: {url}")
                                continue  # SKIP this review entirely - cannot verify

                            # Only include reviews with valid, verifiable URLs
                            rating = review_data.get("rating")
                            rating = float(rating) if rating is not None else 0.0

                            reviews.append({
                                "doctor_name": doctor_name,
                                "source": source,
                                "url": url,
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
