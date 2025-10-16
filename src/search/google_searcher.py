"""
Google Custom Search API integration for finding doctor reviews
"""

import logging
import httpx
from typing import List, Dict, Optional
from src.config import settings

logger = logging.getLogger(__name__)


# Malaysia Top 50 Hospital Names for filtering official Facebook pages
# This list is used to identify and skip hospital official pages (e.g., facebook.com/sunway/)
# while allowing patient review content (e.g., facebook.com/groups/...)
MALAYSIA_HOSPITAL_NAMES = [
    # Top 10
    'sunway',                   # Sunway Medical Centre
    'gleneagles',               # Gleneagles Hospital KL
    'subangjaya',               # Subang Jaya Medical Centre
    'sjmc',                     # SJMC abbreviation
    'hkl',                      # Hospital Kuala Lumpur
    'princecourt',              # Prince Court Medical Centre
    'prince court',
    'pantai',                   # Pantai Hospital (multiple branches)
    'island hospital',          # Island Hospital Penang
    'islandhospital',

    # Top 11-20
    'kpj',                      # KPJ Healthcare (multiple branches)
    'lohguan',                  # Loh Guan Lye
    'penang adventist',         # Penang Adventist Hospital
    'adventisthospital',
    'sime darby',               # Sime Darby Medical Centre
    'sdmc',
    'tropicana',                # Tropicana Medical Centre
    'beacon',                   # Beacon Hospital
    'ipoh specialist',          # Ipoh Specialist Hospital
    'ipohspecialist',
    'normah',                   # Normah Medical Specialist Centre

    # Top 21-30
    'columbia asia',            # Columbia Asia (multiple branches)
    'columbiasia',
    'ummc',                     # University Malaya Medical Centre
    'putra',                    # Putra Specialist Hospital
    'putrajaya',                # Putrajaya Hospital
    'melaka',                   # Melaka Hospital
    'kuala lumpur',             # Hospital Kuala Lumpur
    'ampang',                   # Ampang Hospital
    'selayang',                 # Selayang Hospital
    'tung shin',                # Tung Shin Hospital
    'tungshin',

    # Top 31-40
    'mahkota',                  # Mahkota Medical Centre
    'ara damansara',            # Ara Damansara Medical Centre
    'aradamansara',
    'tawakal',                  # Hospital Tawakal
    'tuanku jaafar',            # Tuanku Ja'afar Hospital
    'tuankujaafar',
    'sultanah aminah',          # Hospital Sultanah Aminah
    'sultanahaminah',
    'tengku ampuan rahimah',    # Hospital Tengku Ampuan Rahimah
    'htar',
    'sultan ismail',            # Hospital Sultan Ismail
    'sultanismail',

    # Top 41-50
    'sultanah bahiyah',         # Hospital Sultanah Bahiyah
    'sultanahbahiyah',
    'raja permaisuri bainun',   # Hospital Raja Permaisuri Bainun
    'hrpb',
    'bainun',
    'tuanku fauziah',           # Hospital Tuanku Fauziah
    'tuankufauziah',
    'sultanah nur zahirah',     # Hospital Sultanah Nur Zahirah
    'sultanahzahirah',
    'duke',                     # Duke Medical Centre
    'thomson',                  # Thomson Hospital
    'assunta',                  # Assunta Hospital
    'damansara specialist',     # Damansara Specialist Hospital
    'damansaraspecialist'
]


class GoogleSearcher:
    """Search using Google Custom Search API"""

    def __init__(self):
        self.api_key = settings.google_search_api_key
        self.search_engine_id = settings.google_search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"

        # Priority sites: High-quality review platforms (searched first, results boosted)
        # These sites consistently have genuine patient reviews and discussions
        self.priority_sites = [
            "forum.lowyat.net",      # Malaysia's largest tech/general forum - active medical discussions
            "cari.com.my",           # Popular Malaysian community forum
            "facebook.com",          # Social media - groups and posts
            "linkedin.com",          # Professional network - formal complaints
            "google.com/maps",       # Google Maps reviews
            "maps.google.com",       # Google Maps reviews (alternate domain)
        ]

        # Blacklist: Sites to exclude from search results
        # These sites typically don't contain genuine patient reviews
        self.excluded_sites = [
            # Doctor directory sites (listing/promotional content only)
            "aestheticsadvisor.com",
            "whatclinic.com",
            "vaidam.com",
            "medsurgeindia.com",
            "medifee.com",
            "practo.com",
            "onedaymd.com",          # Medical directory/listing site
            "scribd.com",             # Document sharing (often just lists)
            "theasianparent.com",     # Parenting forum (low-quality, generic discussions)
            "medisata.com",          # Indonesian doctor directory
            "tripmedis.id",          # Indonesian medical tourism directory
            "kinderasia.com",        # Doctor directory/booking
            "pantangplus.com",       # Hospital package promotional site
            "berobatkemelaka.com",   # Indonesian medical tourism site

            # Hospital official websites (not patient reviews)
            "sunway.com.my",
            "gleneagles.com.my",
            "sjmc.com.my",
            "columbiaasiahospitals.com",
            "pantai.com.my",
        ]

    async def search_doctor_reviews(
        self,
        doctor_name: str,
        specialty: str = "",
        location: str = ""
    ) -> Dict:
        """
        Search for doctor reviews using hybrid strategy:
        1. Priority sites search (high-quality platforms like Lowyat, Cari)
        2. Web-wide search (discover new platforms)
        3. Merge and deduplicate
        4. Blacklist filtering

        This ensures we get best results from known platforms while not missing new ones

        Args:
            doctor_name: Doctor's name
            specialty: Doctor's specialty (optional)
            location: Location/city (optional)

        Returns:
            Dict with search results
        """
        try:
            if not self.api_key or not self.search_engine_id:
                logger.warning("Google Search API credentials not configured")
                return {
                    "source": "google_custom_search",
                    "urls": [],
                    "total_count": 0,
                    "error": "API credentials not configured"
                }

            # Build search query
            query = self._build_query(doctor_name, specialty, location)

            # Phase 1: Search priority sites (get ~15 results, ~2-3 per site)
            priority_urls = []
            for site in self.priority_sites:
                site_results = await self._search_site(query, site, num_results=3)
                priority_urls.extend(site_results)

            logger.info(f"📌 Priority sites search: {len(priority_urls)} URLs from {len(self.priority_sites)} sites")

            # Phase 2: Web-wide search (get remaining results to reach ~30 total)
            remaining_needed = max(30 - len(priority_urls), 10)  # Get at least 10 from web
            web_urls = await self._search_web(query, num_results=remaining_needed)

            logger.info(f"🌐 Web-wide search: {len(web_urls)} URLs")

            # Merge and deduplicate (priority URLs come first)
            seen_urls = set()
            all_urls = []

            # Add priority URLs first (these rank higher)
            for url_dict in priority_urls:
                url = url_dict.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_urls.append(url_dict)

            # Add web URLs (only if not already seen)
            for url_dict in web_urls:
                url = url_dict.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_urls.append(url_dict)

            # Filter out blacklisted sites
            filtered_urls = []
            for url_dict in all_urls:
                url = url_dict.get("url", "")

                # Check if URL contains any blacklisted domain
                is_blacklisted = any(excluded in url.lower() for excluded in self.excluded_sites)

                if not is_blacklisted:
                    filtered_urls.append(url_dict)
                else:
                    logger.debug(f"⏭️ Filtered blacklisted site: {url[:60]}...")

            logger.info(f"🔍 Final results: {len(filtered_urls)} URLs ({len(priority_urls)} priority + {len(web_urls)} web, {len(all_urls) - len(filtered_urls)} filtered)")

            return {
                "source": "google_custom_search",
                "urls": filtered_urls,
                "total_count": len(filtered_urls),
                "query": query
            }

        except Exception as e:
            logger.error(f"Google Search error: {e}")
            return {
                "source": "google_custom_search",
                "urls": [],
                "total_count": 0,
                "error": str(e)
            }

    def _build_query(self, doctor_name: str, specialty: str, location: str) -> str:
        """Build search query"""
        query_parts = [f'"{doctor_name}"']

        if specialty:
            query_parts.append(specialty)

        if location:
            query_parts.append(location)
        else:
            query_parts.append("Malaysia")

        # Add review keywords - include negative keywords to catch complaints and lawsuits
        # This ensures we find both positive and negative patient experiences
        query_parts.append("(review OR reviews OR testimonial OR feedback OR experience OR complaint OR lawsuit OR sued OR malpractice OR negligence)")

        return " ".join(query_parts)

    async def _search_site(self, query: str, site: str, num_results: int = 3) -> List[Dict]:
        """
        Search a specific site (for priority site targeting)

        Args:
            query: Search query
            site: Site to search (e.g., "forum.lowyat.net")
            num_results: Number of results to fetch (default 3)

        Returns:
            List of URL dicts with metadata
        """
        try:
            # Add site restriction to query
            site_query = f"{query} site:{site}"

            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": site_query,
                "num": min(num_results, 10)  # Max 10 per request
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()

            # Extract URLs and metadata
            urls = []
            for item in data.get("items", []):
                urls.append({
                    "url": item.get("link"),
                    "title": item.get("title"),
                    "snippet": item.get("snippet"),
                    "source": site
                })

            logger.debug(f"Found {len(urls)} results from {site}")
            return urls

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.warning(f"Google API rate limit exceeded")
            else:
                logger.error(f"HTTP error searching {site}: {e}")
            return []

        except Exception as e:
            logger.error(f"Error searching {site}: {e}")
            return []

    async def _search_web(self, query: str, num_results: int = 30) -> List[Dict]:
        """
        Search entire web (no site restriction)

        Args:
            query: Search query
            num_results: Number of results to fetch (max 30)

        Returns:
            List of URL dicts with metadata
        """
        try:
            # Search entire web (no site: restriction)
            # Google API allows max 10 results per request, so we need multiple requests
            all_urls = []

            # Make up to 3 requests to get 30 results (10 per request)
            for start_index in range(1, min(num_results, 30) + 1, 10):
                params = {
                    "key": self.api_key,
                    "cx": self.search_engine_id,
                    "q": query,
                    "num": 10,
                    "start": start_index  # Pagination: 1, 11, 21
                }

                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(self.base_url, params=params)
                    response.raise_for_status()
                    data = response.json()

                # Extract URLs and metadata
                items = data.get("items", [])
                if not items:
                    break  # No more results

                for item in items:
                    all_urls.append({
                        "url": item.get("link"),
                        "title": item.get("title"),
                        "snippet": item.get("snippet"),
                        "source": "web"
                    })

                # If we got fewer than 10 results, there are no more pages
                if len(items) < 10:
                    break

            logger.debug(f"Found {len(all_urls)} results from web search")
            return all_urls

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.warning(f"Google API rate limit exceeded")
            else:
                logger.error(f"HTTP error in web search: {e}")
            return []

        except Exception as e:
            logger.error(f"Error in web search: {e}")
            return []

    async def extract_content_with_openai(self, urls: List[Dict], doctor_name: str) -> Dict:
        """
        Scrape URLs and use GPT-4 to extract genuine patient reviews from HTML content

        Strategy:
        1. Try to fetch HTML and use GPT-4 to extract patient reviews
        2. Fallback: If GPT-4 extraction fails or finds nothing, use Google's snippet

        Args:
            urls: List of URL dicts from Google search (includes url, title, snippet)
            doctor_name: Doctor's name

        Returns:
            Dict with extracted reviews
        """
        try:
            from openai import AsyncOpenAI
            import json
            import asyncio
            import time

            openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
            all_reviews = []
            failed_to_fetch_urls = []  # URLs that failed to fetch (HTTP errors, timeout, etc.)
            gpt4_found_no_reviews = []  # URLs that GPT-4 analyzed but found no reviews
            verified_working_urls = set()  # URLs we successfully accessed (HTTP 200)

            # Track processing time to avoid timeout
            start_time = time.time()
            max_processing_time = 25  # seconds (leave 5 seconds buffer for WhatsApp timeout)

            # Process URLs - try GPT-4 extraction first
            for url_dict in urls[:15]:  # Process up to 15 URLs
                # Check if we're approaching timeout
                elapsed = time.time() - start_time
                if elapsed > max_processing_time:
                    logger.warning(f"⏱️ Timeout approaching ({elapsed:.1f}s), stopping extraction")
                    # Mark remaining URLs as failed to fetch (didn't have time to try)
                    failed_to_fetch_urls.extend(urls[len(all_reviews):])
                    break
                url = url_dict.get("url", "")
                google_snippet = url_dict.get("snippet", "")

                if not url:
                    continue

                # Skip Facebook official hospital pages
                url_lower = url.lower()
                if 'facebook.com/' in url_lower:
                    # Extract the path after facebook.com/
                    parts = url_lower.split('facebook.com/')
                    if len(parts) > 1:
                        path = parts[1].split('/')[0].split('?')[0]  # Get first segment, remove query params

                        # If path contains hospital name, it's likely an official page
                        if any(name in path for name in MALAYSIA_HOSPITAL_NAMES):
                            # Exception: groups are OK (even if hospital-related)
                            if path != 'groups':
                                logger.info(f"⏭️ Skipping Facebook official hospital page: {url[:70]}...")
                                # Don't use fallback for hospital official pages
                                continue

                try:
                    # Fetch HTML content with shorter timeout
                    async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
                        response = await client.get(url)

                        if response.status_code != 200:
                            logger.warning(f"❌ HTTP {response.status_code} for {url}")
                            failed_to_fetch_urls.append(url_dict)
                            continue

                        # Mark this URL as working (successfully accessed)
                        verified_working_urls.add(url)
                        html_content = response.text[:30000]  # Limit to 30k chars (balance between content and speed)

                    # Use GPT-4 to extract ONLY genuine patient reviews
                    extraction_prompt = f"""Analyze this webpage and extract ONLY genuine patient reviews about {doctor_name}.

Rules:
- ONLY include actual patient experiences and reviews ABOUT {doctor_name}
- EXCLUDE doctor bios, introductions, and professional descriptions
- EXCLUDE hospital promotional content
- EXCLUDE "About the doctor" sections
- EXCLUDE directory listings and contact information
- EXCLUDE reviews about OTHER doctors (not {doctor_name})

IMPORTANT: Each review snippet MUST mention "{doctor_name}" or clearly reference this specific doctor.
If a review talks about a different doctor, DO NOT include it.

For each genuine patient review found about {doctor_name}, extract:
1. The full review text that mentions {doctor_name} (patient's words)
2. Date (if available, in YYYY-MM-DD format)
3. Author name (if available)

URL: {url}

HTML Content:
{html_content}

Return a JSON object with this EXACT structure:
{{
  "reviews": [
    {{
      "snippet": "Full patient review text here that mentions {doctor_name}",
      "review_date": "YYYY-MM-DD or empty string",
      "author_name": "Name or empty string",
      "url": "{url}"
    }}
  ]
}}

If NO genuine patient reviews about {doctor_name} are found, return: {{"reviews": []}}"""

                    # Call GPT-4 for analysis
                    completion = await openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are an expert at extracting genuine patient reviews from webpages. You distinguish between patient reviews and doctor information."},
                            {"role": "user", "content": extraction_prompt}
                        ],
                        temperature=0.1,
                        response_format={"type": "json_object"}
                    )

                    # Parse response
                    content = completion.choices[0].message.content
                    result = json.loads(content)
                    reviews = result.get("reviews", [])

                    if reviews:
                        # Filter reviews to ensure they mention the doctor's name
                        # Extract key name parts (handle "Dr Tang Boon Nee" → check for "tang")
                        name_parts = doctor_name.lower().replace("dr.", "").replace("dr", "").strip().split()
                        # Use last name (usually first word after removing "Dr")
                        key_name = name_parts[0] if name_parts else doctor_name.lower()

                        relevant_reviews = []
                        for review in reviews:
                            snippet = review.get("snippet", "").lower()
                            # Check if snippet mentions the key name
                            if key_name in snippet:
                                review["source"] = "google_custom_search + gpt4_extraction"
                                review["url"] = url  # Ensure URL is present
                                relevant_reviews.append(review)
                            else:
                                logger.debug(f"⏭️ Filtered out review without '{key_name}': {snippet[:50]}...")

                        if relevant_reviews:
                            all_reviews.extend(relevant_reviews)
                            logger.info(f"📄 Extracted {len(relevant_reviews)}/{len(reviews)} relevant reviews from {url}")
                        else:
                            # GPT-4 extracted reviews but none mention doctor name
                            logger.warning(f"⚠️ GPT-4 extracted {len(reviews)} reviews but none mention '{doctor_name}'")
                            gpt4_found_no_reviews.append(url_dict)
                    else:
                        # GPT-4 analyzed the page and found no patient reviews
                        # Trust GPT-4's judgment - don't use fallback for these
                        logger.info(f"✓ GPT-4 verified no patient reviews in {url}")
                        gpt4_found_no_reviews.append(url_dict)

                except Exception as e:
                    logger.warning(f"❌ Failed to extract from {url}: {e}")
                    failed_to_fetch_urls.append(url_dict)
                    continue

            # Fallback: Use Google snippets ONLY for URLs we couldn't fetch
            # Do NOT use fallback for URLs that GPT-4 successfully analyzed (trust GPT-4's judgment)
            if len(all_reviews) < 5 and failed_to_fetch_urls:
                logger.info(f"🔄 Fallback: Using Google snippets for {len(failed_to_fetch_urls)} URLs we couldn't fetch")
                logger.info(f"ℹ️  Not using fallback for {len(gpt4_found_no_reviews)} URLs where GPT-4 found no reviews (trusting GPT-4)")

                # Extract key name for filtering (same logic as GPT-4 extraction)
                name_parts = doctor_name.lower().replace("dr.", "").replace("dr", "").strip().split()
                key_name = name_parts[0] if name_parts else doctor_name.lower()

                fallback_added = 0
                for url_dict in failed_to_fetch_urls[:10]:  # Use up to 10 snippets as fallback
                    snippet = url_dict.get("snippet", "")
                    url = url_dict.get("url", "")

                    # For failed_to_fetch URLs, we can't verify the URL works
                    # So we ONLY use the Google snippet text, and EXCLUDE the URL from results
                    # This way users see the snippet but can't click broken links

                    # Skip Facebook official hospital pages (same logic as GPT-4 extraction)
                    url_lower = url.lower()
                    if 'facebook.com/' in url_lower:
                        parts = url_lower.split('facebook.com/')
                        if len(parts) > 1:
                            path = parts[1].split('/')[0].split('?')[0]
                            if any(name in path for name in MALAYSIA_HOSPITAL_NAMES):
                                if path != 'groups':
                                    logger.debug(f"⏭️ Fallback: Skipping Facebook hospital page: {url[:70]}...")
                                    continue

                    # Filter: Only use snippets that mention the doctor's name
                    if snippet and len(snippet) > 20:  # Only use meaningful snippets
                        snippet_lower = snippet.lower()

                        # Skip directory listings and non-review content
                        skip_patterns = [
                            'address:',           # Address listings
                            'jalan ss',           # Malaysian address
                            'selangor, malaysia', # Location info
                            'google ...',         # Google ellipsis (directory listing)
                            'internal:',          # Staff listings
                            'assoc. prof.',       # Academic listings
                            'fke.postgraduate',   # Academic pages
                            'aestheticsadvisor',  # Directory site
                            'professional registration', # Doctor bio pages
                            'lulusan',            # Indonesian doctor directory (educational background)
                            'pakar program',      # Doctor specialty programs
                            'dokter spesialis',   # Indonesian (specialist doctor)
                            'adalah dokter',      # Indonesian (is a doctor)
                            'doctor registration', # Registration pages
                            'years of experience', # Bio pages
                            'graduated from',     # Educational background
                            'tak pernah jumpa',   # Malay: never met (not a real review)
                            'never met',          # English: never met
                            'consultation hours', # Doctor directory info
                            'office hours',
                            'bilik:',             # Malay: room number (directory info)
                            'phone:',
                            'extension no',
                        ]

                        if any(pattern in snippet_lower for pattern in skip_patterns):
                            logger.debug(f"⏭️ Fallback: Skipping directory/bio content: {snippet[:50]}...")
                            continue

                        # CRITICAL: Check if snippet contains actual review language
                        # Only accept snippets that show patient experiences, not just doctor mentions
                        review_indicators = [
                            # Malay/Indonesian review keywords
                            'saya',              # I (first person - indicates patient experience)
                            'aku',               # I (informal)
                            'recommended',       # Recommendation
                            'recommend',
                            'sangat bagus',      # Very good
                            'doktor tu',         # That doctor (informal discussion)
                            'pengalaman',        # Experience (when combined with first person)

                            # English review keywords
                            'went to',           # Patient action
                            'visited',
                            'my experience',
                            'i went',
                            'saw dr',
                            'he/she was',
                            'very good',
                            'excellent',
                            'terrible',
                            'complaint',
                            'helped me',
                        ]

                        # Check if snippet contains at least one review indicator
                        has_review_language = any(indicator in snippet_lower for indicator in review_indicators)

                        if not has_review_language:
                            logger.debug(f"⏭️ Fallback: Skipping non-review snippet (no patient experience language): {snippet[:50]}...")
                            continue

                        if key_name in snippet_lower:
                            # Try to extract date from snippet text
                            import re
                            from datetime import datetime

                            extracted_date = ""
                            # Pattern 1: "Nov 17, 2020" or "Jun 23, 2020"
                            date_match = re.search(r'([A-Z][a-z]{2})\s+(\d{1,2}),\s+(\d{4})', snippet)
                            if date_match:
                                try:
                                    month_str = date_match.group(1)
                                    day = date_match.group(2)
                                    year = date_match.group(3)
                                    # Parse date
                                    parsed_date = datetime.strptime(f"{month_str} {day} {year}", "%b %d %Y")
                                    extracted_date = parsed_date.strftime("%Y-%m-%d")
                                except ValueError:
                                    pass

                            # Pattern 2: "2013-08-21" (YYYY-MM-DD already formatted)
                            if not extracted_date:
                                date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', snippet)
                                if date_match:
                                    extracted_date = date_match.group(0)

                            all_reviews.append({
                                "snippet": snippet,
                                "url": "",  # Don't include URL since we couldn't verify it works
                                "review_date": extracted_date,
                                "author_name": "",
                                "source": "google_snippet_unverified"
                            })
                            fallback_added += 1
                        else:
                            logger.debug(f"⏭️ Filtered out fallback snippet without '{key_name}': {snippet[:50]}...")

                logger.info(f"📋 Added {fallback_added} relevant Google snippets as fallback (filtered from {len(failed_to_fetch_urls[:10])})")

            logger.info(f"✅ Total: {len(all_reviews)} reviews (GPT-4 + fallback)")

            return {
                "reviews": all_reviews,
                "total_count": len(all_reviews),
                "source": "google_custom_search + gpt4_extraction"
            }

        except Exception as e:
            logger.error(f"Error extracting content with OpenAI: {e}")
            return {
                "reviews": [],
                "total_count": 0,
                "error": str(e)
            }


# Global instance
google_searcher = GoogleSearcher()
