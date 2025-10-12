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

    def _generate_name_variations(self, name: str) -> str:
        """
        Simple name variation strategy:
        1. Exact match (user input)
        2. First word match (e.g., "Tang" from "Tang Boon Nee")

        Args:
            name: Doctor's name as entered by user

        Returns:
            Two variations: full name and first word
        """
        name_clean = name.strip()

        # Remove common prefixes to get base name
        base_name = name_clean
        for prefix in ["Doctor ", "Dr. ", "Dr ", "Prof. ", "Prof ", "Dato' ", "Datuk "]:
            if name_clean.startswith(prefix):
                base_name = name_clean[len(prefix):].strip()
                break

        # Strategy 1: Exact match - use full name as entered
        variations = [f'"{base_name}"']

        # Strategy 2: First word match
        first_word = base_name.split()[0] if base_name.split() else base_name
        if first_word != base_name:  # Only add if different from full name
            variations.append(f'"Dr {first_word}"')

        return ", ".join(variations)

    def _is_blacklisted_domain(self, url: str) -> bool:
        """
        Check if URL is from a known defunct/spam domain
        Fast check without HTTP requests
        """
        # Known defunct domains that redirect to spam
        blacklisted_domains = [
            "lookp.com",           # Redirects to sostalisman.net
            "sostalisman.net",     # Spam site
            "wedresearch.com",     # Often unreliable
        ]

        url_lower = url.lower()
        for domain in blacklisted_domains:
            if domain in url_lower:
                logger.warning(f"⚠️ Blacklisted domain detected: {domain} in {url}")
                return True

        return False

    async def search_doctor_reviews(
        self,
        doctor_name: str,
        specialty: str = "",
        location: str = ""
    ) -> Dict:
        """
        Simple search strategy:
        - Search for doctor name (exact + first word match)
        - Return all results found

        Args:
            doctor_name: Doctor's name as entered by user
            specialty: Ignored for now (kept for compatibility)
            location: City/hospital name in Malaysia (defaults to "Malaysia")

        Returns:
            Dict with reviews and metadata
        """
        try:
            logger.info(f"🔍 Simple search for: {doctor_name}")

            # Generate name variations (exact + first word)
            name_variations = self._generate_name_variations(doctor_name)
            logger.info(f"📝 Name variations: {name_variations}")

            # Build simple search prompt
            location_hint = f" in {location}" if location else " in Malaysia"

            search_prompt = f"""Search for patient reviews and information about doctor: {name_variations}{location_hint}

Search ALL these Malaysian sources:
1. Google Maps reviews (Malaysia)
2. Facebook (pages, groups, comments)
3. Lowyat Forum (forum.lowyat.net)
4. Cari Forum (cari.com.my)
5. Hospital websites (Gleneagles, Pantai, Prince Court, Sunway Medical)
6. Healthgrades, RateMDs
7. Medical directories and professional profiles
8. Malaysian healthcare blogs

Return JSON array (even if only 1 review found):
[{{"source":"Google Maps","snippet":"review text","author_name":"name","review_date":"2023-01-01","rating":4.5,"url":"https://..."}}]

IMPORTANT: Include ALL reviews found, even brief mentions or single reviews.
Return empty array only if absolutely nothing found: []"""

            logger.info(f"🌐 Calling OpenAI web search...")

            # Call OpenAI API
            response = await self.client.responses.create(
                model="gpt-4o-mini",
                tools=[{"type": "web_search"}],
                input=search_prompt
            )

            # Parse response
            reviews = await self._parse_openai_response(response, doctor_name)

            logger.info(f"✅ Found {len(reviews)} reviews")

            return {
                "doctor_name": doctor_name,
                "reviews": reviews,
                "source": "openai_web_search",
                "total_count": len(reviews)
            }

        except Exception as e:
            import traceback
            logger.error(f"❌ Search error: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "doctor_name": doctor_name,
                "reviews": [],
                "source": "error",
                "total_count": 0,
                "error": f"Search failed: {str(e)}"
            }

    async def _parse_openai_response(self, response, doctor_name: str) -> List[Dict]:
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

                            # CRITICAL: Validate URL format
                            # OpenAI sometimes returns descriptions instead of actual URLs
                            if not url or not url.startswith(("http://", "https://")):
                                logger.warning(f"⚠️ Skipping review from {source}: Invalid/missing URL: {url[:50] if url else 'None'}")
                                continue

                            # Step 1: Fast blacklist check (0ms)
                            if self._is_blacklisted_domain(url):
                                logger.warning(f"⚠️ Skipping review from blacklisted domain: {url}")
                                continue  # SKIP - known defunct/spam domain

                            # Collect review for batch validation
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

                    logger.info(f"✅ Parsed {len(reviews)} reviews from JSON (after blacklist)")
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


# Global instance
openai_web_searcher = OpenAIWebSearcher()
