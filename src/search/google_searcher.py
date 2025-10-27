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
        # COST OPTIMIZATION: Reduced from 6 to 3 sites to save API calls
        # These sites consistently have genuine patient reviews and discussions
        self.priority_sites = [
            "forum.lowyat.net",      # Malaysia's largest tech/general forum - active medical discussions
            "cari.com.my",           # Popular Malaysian community forum
            "facebook.com",          # Facebook pages and groups (hospital pages, patient groups)
        ]

        # Note: google.com/maps removed because Google Custom Search cannot index it
        # To get Google Maps reviews, we need to use Google Places API instead

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
                # Google Maps gets more results (most reliable source)
                num_results = 5 if site == "google.com/maps" else 3
                site_results = await self._search_site(query, site, num_results=num_results)
                priority_urls.extend(site_results)

            logger.info(f"📌 Priority sites search: {len(priority_urls)} URLs from {len(self.priority_sites)} sites")

            # Phase 2: Web-wide search (COST OPTIMIZATION: reduced from 30 to 10 results = 1 API call instead of 3)
            remaining_needed = max(10 - len(priority_urls), 5)  # Get at least 5 from web
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

            # Log all URLs BEFORE blacklist filtering
            logger.info(f"📋 All {len(all_urls)} URLs from Google (BEFORE blacklist filtering):")
            for i, url_dict in enumerate(all_urls, 1):
                url = url_dict.get("url", "")
                source = url_dict.get("source", "unknown")
                logger.info(f"  {i}. [{source}] {url}")

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

            # Log all URLs for debugging
            logger.info(f"📋 All {len(filtered_urls)} URLs after filtering:")
            for i, url_dict in enumerate(filtered_urls, 1):
                url = url_dict.get("url", "")
                source = url_dict.get("source", "unknown")
                logger.info(f"  {i}. [{source}] {url}")

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

        # Broad keywords to catch all types of patient content
        # OR logic = match ANY of these keywords (more keywords = more matches)
        query_parts.append("(review OR reviews OR testimonial OR feedback OR experience OR complaint OR lawsuit OR sued OR malpractice OR negligence OR doctor OR clinic OR patient OR hospital OR medical OR treatment)")

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

            # For Google Maps, also try broader search if specific search fails
            # This helps when doctor names are very long or have multiple variations
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

    async def _process_single_url(self, url_dict: Dict, doctor_name: str, openai_client) -> List[Dict]:
        """
        Process a single URL: fetch HTML and extract reviews with GPT-4

        Args:
            url_dict: URL dictionary with url, title, snippet
            doctor_name: Doctor's name
            openai_client: OpenAI async client

        Returns:
            List of extracted reviews (empty if none found)
        """
        import json

        url = url_dict.get("url", "")
        if not url:
            return []

        # Skip Facebook official hospital pages
        url_lower = url.lower()
        if 'facebook.com/' in url_lower:
            parts = url_lower.split('facebook.com/')
            if len(parts) > 1:
                path = parts[1].split('/')[0].split('?')[0]
                if any(name in path for name in MALAYSIA_HOSPITAL_NAMES):
                    if path != 'groups':
                        logger.info(f"⏭️ Skipping Facebook official hospital page: {url[:70]}...")
                        return []

        try:
            # Fetch HTML content with shorter timeout
            async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
                response = await client.get(url)

                if response.status_code != 200:
                    logger.warning(f"❌ HTTP {response.status_code} for {url}")
                    return []

                html_content = response.text[:30000]

                # Check for common error page indicators
                html_lower = html_content.lower()
                error_indicators = [
                    # 404 - Page not found
                    "page not found",
                    "404 error",
                    "page doesn't exist",
                    "page you're looking for",
                    "can't seem to find",
                    "this page isn't available",
                    "sorry, this page isn't available",
                    "the requested url was not found",

                    # 403 - Forbidden
                    "access denied",
                    "403 forbidden",
                    "permission denied",
                    "you don't have permission",

                    # 500 - Server errors
                    "internal server error",
                    "500 error",
                    "something went wrong",

                    # Login/Auth required
                    "please log in to continue",
                    "sign in required",
                    "login required",
                    "you must be logged in",

                    # Content deleted/removed
                    "has been deleted",
                    "has been removed",
                    "content no longer available",
                    "post has been deleted",

                    # Rate limiting
                    "too many requests",
                    "rate limit exceeded",
                    "you've been temporarily blocked"
                ]

                if any(indicator in html_lower for indicator in error_indicators):
                    logger.info(f"⏭️ Detected error page: {url[:70]}...")
                    return []

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
                name_parts = doctor_name.lower().replace("dr.", "").replace("dr", "").strip().split()
                key_name = name_parts[0] if name_parts else doctor_name.lower()

                relevant_reviews = []
                for review in reviews:
                    snippet = review.get("snippet", "").lower()
                    if key_name in snippet:
                        review["source"] = "google_custom_search + gpt4_extraction"
                        review["url"] = url
                        relevant_reviews.append(review)
                    else:
                        logger.debug(f"⏭️ Filtered out review without '{key_name}': {snippet[:50]}...")

                if relevant_reviews:
                    logger.info(f"📄 Extracted {len(relevant_reviews)}/{len(reviews)} relevant reviews from {url}")
                    return relevant_reviews
                else:
                    logger.debug(f"⏭️ GPT-4 extracted {len(reviews)} reviews but none mention '{doctor_name}'")
                    return []
            else:
                logger.debug(f"⏭️ GPT-4 verified no patient reviews in {url}")
                return []

        except Exception as e:
            logger.warning(f"❌ Failed to extract from {url}: {e}")
            return []

    async def extract_content_with_openai(self, urls: List[Dict], doctor_name: str) -> Dict:
        """
        Scrape URLs and use GPT-4 to extract genuine patient reviews from HTML content

        NEW STRATEGY: Concurrent processing with asyncio.gather
        - Process multiple URLs in parallel
        - Respect 25-second timeout
        - Process up to 10 URLs concurrently

        Args:
            urls: List of URL dicts from Google search (includes url, title, snippet)
            doctor_name: Doctor's name

        Returns:
            Dict with extracted reviews
        """
        try:
            from openai import AsyncOpenAI
            import asyncio
            import time

            openai_client = AsyncOpenAI(api_key=settings.openai_api_key)

            # Track processing time to avoid timeout
            start_time = time.time()
            max_processing_time = 25  # seconds (leave 5 seconds buffer for WhatsApp timeout)

            # Process URLs concurrently (increased to 10 URLs for better coverage)
            tasks = []
            for url_dict in urls[:10]:  # Limit to 10 URLs for concurrent processing
                task = self._process_single_url(url_dict, doctor_name, openai_client)
                tasks.append(task)

            # Execute all tasks concurrently with timeout
            logger.info(f"🚀 Processing {len(tasks)} URLs concurrently...")

            try:
                results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=max_processing_time
                )
            except asyncio.TimeoutError:
                logger.warning(f"⏱️ Timeout ({max_processing_time}s) reached during concurrent processing")
                results = []  # Will return empty results if timeout

            # Aggregate all reviews from concurrent tasks
            all_reviews = []
            successful_urls = 0
            failed_urls = 0

            for result in results:
                if isinstance(result, list):  # Successful result
                    all_reviews.extend(result)
                    if result:  # Non-empty result
                        successful_urls += 1
                elif isinstance(result, Exception):  # Task failed
                    logger.warning(f"Task failed with exception: {result}")
                    failed_urls += 1

            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            logger.info(f"⏱️ Processing completed in {elapsed_time:.1f}s")
            logger.info(f"📊 Results: {successful_urls} URLs with reviews, {failed_urls} failed")
            logger.info(f"✅ Total: {len(all_reviews)} reviews extracted by GPT-4")

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
