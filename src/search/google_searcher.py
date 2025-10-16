"""
Google Custom Search API integration for finding doctor reviews
"""

import logging
import httpx
from typing import List, Dict, Optional
from src.config import settings

logger = logging.getLogger(__name__)


class GoogleSearcher:
    """Search using Google Custom Search API"""

    def __init__(self):
        self.api_key = settings.google_search_api_key
        self.search_engine_id = settings.google_search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"

        # Target sites for doctor reviews
        self.target_sites = [
            "facebook.com",
            "forum.lowyat.net",
            "cari.com.my",
            "maps.google.com",
            "google.com/maps",
            "aestheticsadvisor.com",
            "whatclinic.com"
        ]

    async def search_doctor_reviews(
        self,
        doctor_name: str,
        specialty: str = "",
        location: str = ""
    ) -> Dict:
        """
        Search for doctor reviews using Google Custom Search

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

            # Search across target sites
            urls = []
            for site in self.target_sites:
                site_urls = await self._search_site(query, site)
                urls.extend(site_urls)

                # Limit total URLs
                if len(urls) >= 30:
                    break

            logger.info(f"🔍 Google Search found {len(urls)} URLs for: {doctor_name}")

            return {
                "source": "google_custom_search",
                "urls": urls,
                "total_count": len(urls),
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

        # Add review keywords
        query_parts.append("(review OR reviews OR testimonial OR feedback OR experience)")

        return " ".join(query_parts)

    async def _search_site(self, query: str, site: str, num_results: int = 10) -> List[Dict]:
        """
        Search a specific site

        Args:
            query: Search query
            site: Site to search (e.g., "facebook.com")
            num_results: Number of results to fetch

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
            failed_urls = []

            # Track processing time to avoid timeout
            start_time = time.time()
            max_processing_time = 25  # seconds (leave 5 seconds buffer for WhatsApp timeout)

            # Process URLs - try GPT-4 extraction first
            for url_dict in urls[:15]:  # Process up to 15 URLs
                # Check if we're approaching timeout
                elapsed = time.time() - start_time
                if elapsed > max_processing_time:
                    logger.warning(f"⏱️ Timeout approaching ({elapsed:.1f}s), stopping extraction")
                    # Continue with fallback for remaining URLs
                    failed_urls.extend(urls[len(all_reviews):])
                    break
                url = url_dict.get("url", "")
                google_snippet = url_dict.get("snippet", "")

                if not url:
                    continue

                # Skip Facebook official hospital pages
                # Pattern: facebook.com/hospitalname/ (where hospitalname contains medical keywords)
                url_lower = url.lower()
                if 'facebook.com/' in url_lower:
                    # Extract the path after facebook.com/
                    parts = url_lower.split('facebook.com/')
                    if len(parts) > 1:
                        path = parts[1].split('/')[0].split('?')[0]  # Get first segment, remove query params

                        # Check if path contains specific hospital names (Malaysia major hospitals)
                        hospital_names = [
                            'gleneagles',           # Gleneagles Hospital
                            'pantai',               # Pantai Hospital
                            'sunway',               # Sunway Medical Centre
                            'subangjaya',           # Subang Jaya Medical Centre
                            'sjmc',                 # Subang Jaya Medical Centre abbreviation
                            'sdmc',                 # Sime Darby Medical Centre
                            'prince court',         # Prince Court Medical Centre
                            'princecourt',
                            'mncc',                 # Malaysia National Cancer Council
                            'ummc',                 # University Malaya Medical Centre
                            'kpj',                  # KPJ Healthcare
                            'tmc',                  # TMC (Tropicana Medical Centre)
                            'columbiasia',          # Columbia Asia Hospital
                            'adventist',            # Adventist Hospital
                            'tung shin',            # Tung Shin Hospital
                            'tungshin'
                        ]

                        # If path contains hospital name, it's likely an official page
                        if any(name in path for name in hospital_names):
                            # Exception: groups are OK (even if hospital-related)
                            if path != 'groups':
                                logger.info(f"⏭️ Skipping Facebook official hospital page: {url[:70]}...")
                                failed_urls.append(url_dict)
                                continue

                try:
                    # Fetch HTML content with shorter timeout
                    async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
                        response = await client.get(url)

                        if response.status_code != 200:
                            logger.warning(f"❌ HTTP {response.status_code} for {url}")
                            failed_urls.append(url_dict)
                            continue

                        html_content = response.text[:30000]  # Limit to 30k chars (balance between content and speed)

                    # Use GPT-4 to extract ONLY genuine patient reviews
                    extraction_prompt = f"""Analyze this webpage and extract ONLY genuine patient reviews about {doctor_name}.

Rules:
- ONLY include actual patient experiences and reviews
- EXCLUDE doctor bios, introductions, and professional descriptions
- EXCLUDE hospital promotional content
- EXCLUDE "About the doctor" sections
- EXCLUDE directory listings and contact information

For each genuine patient review found, extract:
1. The full review text (patient's words)
2. Date (if available, in YYYY-MM-DD format)
3. Author name (if available)

URL: {url}

HTML Content:
{html_content}

Return a JSON object with this EXACT structure:
{{
  "reviews": [
    {{
      "snippet": "Full patient review text here",
      "review_date": "YYYY-MM-DD or empty string",
      "author_name": "Name or empty string",
      "url": "{url}"
    }}
  ]
}}

If NO genuine patient reviews are found, return: {{"reviews": []}}"""

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
                        # Add source metadata
                        for review in reviews:
                            review["source"] = "google_custom_search + gpt4_extraction"
                            review["url"] = url  # Ensure URL is present

                        all_reviews.extend(reviews)
                        logger.info(f"📄 Extracted {len(reviews)} reviews from {url}")
                    else:
                        # GPT-4 found no reviews - mark for fallback
                        logger.warning(f"⚠️ GPT-4 found no reviews in {url}")
                        failed_urls.append(url_dict)

                except Exception as e:
                    logger.warning(f"❌ Failed to extract from {url}: {e}")
                    failed_urls.append(url_dict)
                    continue

            # Fallback: Use Google snippets if GPT-4 extraction yielded few results
            if len(all_reviews) < 5 and failed_urls:
                logger.info(f"🔄 Using fallback: Google snippets for {len(failed_urls)} URLs")

                for url_dict in failed_urls[:10]:  # Use up to 10 snippets as fallback
                    snippet = url_dict.get("snippet", "")
                    url = url_dict.get("url", "")

                    if snippet and len(snippet) > 20:  # Only use meaningful snippets
                        all_reviews.append({
                            "snippet": snippet,
                            "url": url,
                            "review_date": "",
                            "author_name": "",
                            "source": "google_snippet"
                        })

                logger.info(f"📋 Added {len(failed_urls[:10])} Google snippets as fallback")

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
