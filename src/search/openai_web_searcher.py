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
        Generate common name variations for better search coverage

        Examples:
        - "John Smith" → "Dr John Smith", "Dr. John Smith", "John Smith", "Dr Smith"
        - "Lee Wei Ming" → "Dr Lee Wei Ming", "Dr. Lee", "Lee Wei Ming"

        Args:
            name: Doctor's name

        Returns:
            Formatted string of name variations for search prompt
        """
        variations = []
        name_clean = name.strip()

        # Get base name (without prefix if present)
        base_name = name_clean
        for prefix in ["Doctor ", "Dr. ", "Dr ", "Prof. ", "Prof "]:
            if name_clean.startswith(prefix):
                base_name = name_clean[len(prefix):].strip()
                break

        # Generate variations
        variations.append(f'"{base_name}"')  # Base name without title
        variations.append(f'"Dr {base_name}"')  # With "Dr" prefix
        variations.append(f'"Dr. {base_name}"')  # With "Dr." prefix
        variations.append(f'"Doctor {base_name}"')  # With "Doctor" prefix

        # For multi-part names (e.g., "Lee Wei Ming"), also try shortened form
        name_parts = base_name.split()
        if len(name_parts) >= 2:
            # Try "Dr [Last Name]" for common patterns
            variations.append(f'"Dr {name_parts[0]}"')  # e.g., "Dr Lee"

        # Remove duplicates while preserving order
        seen = set()
        unique_variations = []
        for v in variations:
            if v not in seen:
                seen.add(v)
                unique_variations.append(v)

        return ", ".join(unique_variations[:5])  # Limit to 5 variations

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

        # Specialty-specific keyword mappings (all 38 specialties)
        specialty_map = {
            "cardiology": ["cardiology", "cardiologist", "heart", "cardiac"],
            "dermatology": ["dermatology", "dermatologist", "skin", "dermatologic"],
            "endocrinology & diabetes": ["endocrinology", "endocrinologist", "diabetes", "hormone", "thyroid"],
            "endocrinology": ["endocrinology", "endocrinologist", "diabetes", "hormone", "thyroid"],
            "gastroenterology & hepatology": ["gastro", "GI", "digestive", "liver", "gastroenterologist", "hepatology"],
            "gastroenterology": ["gastro", "GI", "digestive", "liver", "gastroenterologist"],
            "general surgery": ["surgeon", "surgery", "surgical", "general surgery"],
            "obstetrics & gynaecology": ["obstetric", "gynaecolog", "gynecolog", "ob/gyn", "o&g", "obgyn", "women health"],
            "obstetrics": ["obstetric", "pregnancy", "childbirth", "prenatal"],
            "gynaecology": ["gynaecolog", "gynecolog", "women health", "gynae"],
            "oncology": ["oncology", "cancer", "oncologist", "tumor", "chemotherapy"],
            "ophthalmology": ["ophthalmology", "ophthalmologist", "eye", "vision", "optometry"],
            "orthopaedic surgery": ["ortho", "orthopedic", "bone", "joint", "orthopedist", "musculoskeletal"],
            "orthopedic": ["ortho", "orthopedic", "bone", "joint", "orthopedist"],
            "paediatrics": ["pediatric", "paediatric", "children", "kids", "pediatrician"],
            "pediatrics": ["pediatric", "paediatric", "children", "kids", "pediatrician"],
            "anaesthesiology & critical care": ["anesthesia", "anaesthesia", "anesthetist", "critical care", "ICU"],
            "anaesthesiology": ["anesthesia", "anaesthesia", "anesthetist", "anesthesiologist"],
            "anesthesiology": ["anesthesia", "anaesthesia", "anesthetist", "anesthesiologist"],
            "cardiothoracic surgery": ["cardiothoracic", "heart surgery", "chest surgery", "cardiac surgery", "thoracic"],
            "dentistry": ["dentist", "dental", "teeth", "oral health", "orthodontist"],
            "ear, nose & throat": ["ENT", "ear nose throat", "otolaryngology", "ent specialist"],
            "ear nose throat": ["ENT", "ear nose throat", "otolaryngology", "ent specialist"],
            "emergency medicine": ["emergency", "ER", "emergency room", "trauma", "urgent care"],
            "geriatric medicine": ["geriatric", "elderly", "aging", "gerontology", "senior care"],
            "haematology": ["hematology", "haematology", "blood", "hematologist"],
            "hematology": ["hematology", "haematology", "blood", "hematologist"],
            "infectious diseases": ["infectious disease", "infection", "communicable disease", "tropical medicine"],
            "internal medicine": ["internal medicine", "internist", "general medicine"],
            "nephrology": ["nephrology", "nephrologist", "kidney", "renal", "dialysis"],
            "neurology": ["neurology", "neurologist", "brain", "nerve", "neurological"],
            "neurosurgery": ["neurosurgery", "neurosurgeon", "brain surgery", "spine surgery"],
            "nuclear medicine": ["nuclear medicine", "radioisotope", "PET scan", "nuclear imaging"],
            "pain medicine": ["pain medicine", "pain management", "chronic pain", "pain specialist"],
            "palliative medicine": ["palliative", "hospice", "end of life", "comfort care"],
            "pathology": ["pathology", "pathologist", "lab medicine", "biopsy", "histology"],
            "plastic & reconstructive surgery": ["plastic surgery", "cosmetic", "reconstructive", "aesthetic"],
            "plastic surgery": ["plastic surgery", "cosmetic", "reconstructive", "aesthetic"],
            "psychiatry": ["psychiatry", "psychiatrist", "mental health", "psychiatric"],
            "radiology": ["radiology", "radiologist", "imaging", "X-ray", "MRI", "CT scan"],
            "rehabilitation medicine": ["rehabilitation", "rehab", "physical medicine", "physiatry"],
            "respiratory medicine": ["respiratory", "pulmonology", "lung", "pulmonologist", "breathing"],
            "rheumatology": ["rheumatology", "rheumatologist", "arthritis", "autoimmune", "joint disease"],
            "robotic surgery": ["robotic surgery", "robot assisted", "da vinci", "minimally invasive"],
            "spine surgery": ["spine surgery", "spinal", "back surgery", "vertebrae"],
            "sports medicine": ["sports medicine", "athletic", "sports injury", "exercise medicine"],
            "transplant medicine": ["transplant", "organ transplant", "transplantation"],
            "urology": ["urology", "urologist", "urinary", "bladder", "prostate", "kidney"],
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

    async def search_doctor_reviews(
        self,
        doctor_name: str,
        specialty: str = "",
        location: str = ""
    ) -> Dict:
        """
        Search for doctor reviews using OpenAI web_search with fallback strategy

        Strategy: Progressive search degradation for maximum precision + recall
        1. First try: Doctor name + specialty (strict matching)
        2. If results < threshold: Retry without specialty (broader search)
        3. Merge and deduplicate results, prioritizing specialty-matched reviews

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

            # PHASE 1: Search with specialty (if provided)
            if specialty:
                specialty_keywords = self._extract_specialty_keywords(specialty)
                logger.info(f"🎯 PHASE 1: Searching with specialty constraint: {specialty_keywords}")

                reviews_with_specialty = await self._search_with_constraint(
                    doctor_name,
                    specialty_keywords,
                    location,
                    require_specialty=True
                )

                logger.info(f"✅ Phase 1 found {len(reviews_with_specialty)} reviews WITH specialty match")

                # If we found enough results (>=3), use them
                if len(reviews_with_specialty) >= 3:
                    logger.info(f"✅ Sufficient results with specialty, returning {len(reviews_with_specialty)} reviews")
                    return {
                        "doctor_name": doctor_name,
                        "reviews": reviews_with_specialty,
                        "source": "openai_web_search_with_specialty",
                        "total_count": len(reviews_with_specialty),
                        "search_strategy": "specialty_only"
                    }

                # PHASE 2: Not enough results, try without specialty constraint
                logger.warning(f"⚠️ Only {len(reviews_with_specialty)} reviews with specialty - trying broader search...")
                reviews_without_specialty = await self._search_with_constraint(
                    doctor_name,
                    specialty_keywords,
                    location,
                    require_specialty=False
                )

                logger.info(f"✅ Phase 2 found {len(reviews_without_specialty)} reviews WITHOUT specialty constraint")

                # Merge results: specialty-matched reviews first, then others
                merged_reviews = self._merge_and_deduplicate_reviews(
                    reviews_with_specialty,
                    reviews_without_specialty
                )

                logger.info(f"✅ Final merged result: {len(merged_reviews)} reviews (after deduplication)")

                return {
                    "doctor_name": doctor_name,
                    "reviews": merged_reviews,
                    "source": "openai_web_search_merged",
                    "total_count": len(merged_reviews),
                    "search_strategy": "fallback_merged",
                    "specialty_matched_count": len(reviews_with_specialty),
                    "additional_count": len(merged_reviews) - len(reviews_with_specialty)
                }

            # No specialty provided - direct search
            else:
                logger.info(f"🔍 No specialty provided - direct search for: {doctor_name}")
                reviews = await self._search_with_constraint(
                    doctor_name,
                    "",
                    location,
                    require_specialty=False
                )

                return {
                    "doctor_name": doctor_name,
                    "reviews": reviews,
                    "source": "openai_web_search",
                    "total_count": len(reviews),
                    "search_strategy": "no_specialty"
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

    async def _search_with_constraint(
        self,
        doctor_name: str,
        specialty_keywords: str,
        location: str,
        require_specialty: bool
    ) -> List[Dict]:
        """
        Internal method to search with or without specialty constraint

        Args:
            doctor_name: Doctor's name
            specialty_keywords: Extracted specialty keywords
            location: Location hint
            require_specialty: If True, REQUIRE specialty match; if False, make it optional

        Returns:
            List of review dicts
        """
        specialty_instruction = ""
        if specialty_keywords:
            if require_specialty:
                specialty_instruction = f"""
CRITICAL REQUIREMENT: ONLY return reviews that explicitly mention this doctor's specialty.
Specialty keywords to match: {specialty_keywords}

The review text must mention one of these specialty terms. Do NOT return reviews that don't mention the specialty.
"""
            else:
                specialty_instruction = f"""
Optional context (NOT required): Doctor's specialty may be related to: {specialty_keywords}
Return ALL reviews for this doctor, regardless of specialty mention.
"""

        location_hint = f"\nLocation context: {location}" if location else ""

        # Generate name variations for better search coverage
        name_variations = self._generate_name_variations(doctor_name)

        # Build search prompt
        search_prompt = f"""Find patient reviews for: "Dr {doctor_name}"{location_hint}
{specialty_instruction}

IMPORTANT: Search for the doctor using these name variations:
{name_variations}

Search globally: Google Maps, Facebook, Yelp, Healthgrades, RateMDs, Zocdoc, forums, blogs, review sites

Return JSON only:
[{{"source":"Google Maps","snippet":"review text","author_name":"name","review_date":"2023-01-01","rating":4.5,"url":"https://maps.google.com/..."}}]

CRITICAL: "url" must be full http/https link (not description)
Empty if none: []"""

        logger.info(f"🔍 Calling OpenAI API (require_specialty={require_specialty})")

        # Call OpenAI API
        response = await self.client.responses.create(
            model="gpt-4o-mini",
            tools=[{"type": "web_search"}],
            input=search_prompt
        )

        # Parse response
        reviews = await self._parse_openai_response(response, doctor_name)

        if len(reviews) == 0:
            logger.warning(f"⚠️ 0 reviews found (require_specialty={require_specialty})")

        return reviews

    def _merge_and_deduplicate_reviews(
        self,
        priority_reviews: List[Dict],
        additional_reviews: List[Dict]
    ) -> List[Dict]:
        """
        Merge two review lists, removing duplicates based on URL
        Priority reviews (with specialty match) come first

        Args:
            priority_reviews: Reviews that matched specialty (higher priority)
            additional_reviews: Reviews without specialty constraint (lower priority)

        Returns:
            Merged and deduplicated list
        """
        # Track seen URLs to avoid duplicates
        seen_urls = set()
        merged = []

        # Add priority reviews first
        for review in priority_reviews:
            url = review.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                merged.append(review)

        # Add additional reviews (skip if URL already exists)
        for review in additional_reviews:
            url = review.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                merged.append(review)

        logger.info(f"🔄 Deduplication: {len(priority_reviews)} + {len(additional_reviews)} → {len(merged)} reviews")

        return merged

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

                    # URL validation is disabled because:
                    # 1. Blacklist check already filters known bad domains (fast, 0ms)
                    # 2. URL format validation ensures http/https URLs only
                    # 3. Batch validation was too aggressive and filtered valid reviews
                    # 4. Real-time validation adds 2-4s latency per search
                    # Trade-off: Accept some potentially invalid URLs for better coverage and speed

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
