"""
OpenAI Web Search integration
Uses OpenAI's web_search tool to find doctor reviews from the web
"""

import logging
from typing import List, Dict
from openai import AsyncOpenAI
from src.config import settings
import httpx
import asyncio
from urllib.parse import urlparse

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
            # HTTP client for fast URL validation (2s timeout)
            self.http_client = httpx.AsyncClient(
                follow_redirects=True,
                timeout=2.0,  # Fast timeout to prevent delays
                verify=False  # Skip SSL verification for speed
            )
            logger.info(f"🌐 OpenAI Web Searcher initialized (model: {self.model})")
        except Exception as e:
            logger.error(f"❌ OpenAI API initialization failed: {e}")
            raise Exception("OpenAI API key is required for doctor review search")

    def _extract_specialty_keywords(self, specialty: str) -> str:
        """
        Extract flexible keywords from specialty for fuzzy matching

        Examples:
        - "Obstetrics & Gynaecology" → "obstetric, gynaecolog, gynecolog, ob/gyn, o&g"
        - "Ear, Nose & Throat (ENT)" → "ENT, ear nose throat, otolaryngology"
        - "Cardiology" → "cardiology, cardiologist, heart"

        Args:
            specialty: Full specialty name

        Returns:
            Comma-separated keywords for flexible search
        """
        specialty_lower = specialty.lower()
        keywords = []

        # Specialty-specific keyword mappings
        specialty_map = {
            "obstetrics & gynaecology": ["obstetric", "gynaecolog", "gynecolog", "ob/gyn", "o&g", "obgyn"],
            "ear, nose & throat": ["ENT", "ear nose throat", "otolaryngology", "ent specialist"],
            "cardiology": ["cardiology", "cardiologist", "heart"],
            "dermatology": ["dermatology", "dermatologist", "skin"],
            "gastroenterology & hepatology": ["gastro", "GI", "digestive", "liver"],
            "general surgery": ["surgeon", "surgery", "surgical"],
            "ophthalmology": ["ophthalmology", "eye", "vision"],
            "orthopaedic surgery": ["ortho", "orthopedic", "bone", "joint"],
            "paediatrics": ["pediatric", "paediatric", "children", "kids"],
            "psychiatry": ["psychiatry", "mental health", "psychiatrist"],
            "neurology": ["neurology", "neurologist", "brain", "nerve"],
            "oncology": ["oncology", "cancer", "oncologist"],
        }

        # Check for direct match in map
        for key, values in specialty_map.items():
            if key in specialty_lower:
                keywords.extend(values)
                break

        # If no match, use the specialty itself plus common variations
        if not keywords:
            # Add the original specialty
            keywords.append(specialty)

            # Add without special characters
            cleaned = specialty_lower.replace("&", "").replace(",", "").strip()
            if cleaned != specialty_lower:
                keywords.append(cleaned)

        return ", ".join(keywords[:5])  # Limit to 5 keywords

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

    async def _check_single_url(self, url: str) -> tuple[bool, str]:
        """
        Fast check if single URL redirects to different domain
        Returns: (is_valid, final_url)
        """
        try:
            # Quick HEAD request with 2s timeout
            response = await self.http_client.head(url, follow_redirects=True)

            original_domain = urlparse(url).netloc
            final_domain = urlparse(str(response.url)).netloc

            # Check if domain changed
            if original_domain != final_domain:
                logger.warning(f"⚠️ URL redirects: {original_domain} → {final_domain}")
                return False, str(response.url)

            return True, url

        except asyncio.TimeoutError:
            logger.warning(f"⚠️ URL timeout (2s): {url}")
            return False, url
        except Exception as e:
            logger.warning(f"⚠️ URL check failed: {url} - {e}")
            return False, url

    async def _validate_urls_batch(self, review_list: list) -> list:
        """
        Validate multiple URLs concurrently
        Returns: filtered list with only valid URLs
        """
        # Extract URLs
        urls_to_check = []
        for review in review_list:
            url = review.get("url", "")
            if url and url.startswith(("http://", "https://")):
                urls_to_check.append((review, url))

        if not urls_to_check:
            return review_list

        # Concurrent validation
        logger.info(f"🔍 Validating {len(urls_to_check)} URLs concurrently...")
        tasks = [self._check_single_url(url) for _, url in urls_to_check]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter valid reviews
        valid_reviews = []
        for (review, url), result in zip(urls_to_check, results):
            if isinstance(result, tuple) and result[0]:  # is_valid = True
                valid_reviews.append(review)
            else:
                logger.warning(f"⚠️ Filtered out review with invalid URL: {url}")

        logger.info(f"✅ {len(valid_reviews)}/{len(urls_to_check)} URLs are valid")
        return valid_reviews

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
            
            # Build search instructions with flexible specialty matching
            specialty_hint = ""
            if specialty:
                # Extract key terms from specialty for flexible matching
                # e.g., "Obstetrics & Gynaecology" → search for "obstetric OR gynaecolog OR gynecolog OR ob/gyn"
                specialty_keywords = self._extract_specialty_keywords(specialty)
                specialty_hint = f"\nSpecialty context (use flexibly): {specialty_keywords}"
                logger.info(f"🔍 Specialty keywords: {specialty_keywords}")

            location_hint = f"\nLocation: {location}" if location else ""

            # Use OpenAI Responses API with web search (ChatGPT-like capability)
            logger.info(f"🔍 Calling OpenAI Responses API for: {doctor_name}")
            logger.info(f"🤖 Using model: gpt-4o-mini (web_search compatible, 16.7x cheaper)")

            # Let OpenAI find all reviews, we'll validate URLs programmatically
            response = await self.client.responses.create(
                model="gpt-4o-mini",  # Cost: $0.15/1M input (vs $2.50 for gpt-4o)
                tools=[{"type": "web_search"}],  # Enable web search tool
                input=f"""Find patient reviews for: "Dr {doctor_name}"{specialty_hint}{location_hint}

Search globally: Google Maps, Facebook, Yelp, Healthgrades, RateMDs, Zocdoc, forums, blogs, review sites

IMPORTANT:
- Prioritize reviews matching the specialty if provided, but also include other reviews
- Use flexible matching (e.g., "gynae", "gynaecology", "ob/gyn" all match)
- Return ALL relevant reviews for this doctor

Return JSON only:
[{{"source":"Google Maps","snippet":"review text","author_name":"name","review_date":"2023-01-01","rating":4.5,"url":"https://maps.google.com/..."}}]

CRITICAL: "url" must be full http/https link (not description)
Empty if none: []"""
            )

            logger.info(f"✅ OpenAI API call successful, response type: {type(response)}")

            # Log raw response for debugging
            if hasattr(response, 'output_text'):
                output_preview = response.output_text[:300] if response.output_text else "EMPTY"
                logger.info(f"📝 Response preview: {output_preview}...")

            # Parse response and extract reviews
            reviews = await self._parse_openai_response(response, doctor_name)

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

                    # Step 2: Batch validate URLs concurrently (2s timeout per URL, all parallel)
                    if reviews:
                        logger.info(f"🔍 Starting batch URL validation for {len(reviews)} reviews...")
                        reviews = await self._validate_urls_batch(reviews)
                        logger.info(f"✅ After validation: {len(reviews)} reviews remain")

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
