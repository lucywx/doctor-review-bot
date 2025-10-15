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
        Use OpenAI to extract review content from URLs

        This method uses OpenAI's web search to find reviews about the doctor
        using the URLs found by Google as search hints

        Args:
            urls: List of URL dicts from search
            doctor_name: Doctor's name

        Returns:
            Dict with extracted reviews
        """
        try:
            from src.search.openai_web_searcher import openai_web_searcher

            # Use OpenAI web search with the doctor name
            # This will search for reviews using OpenAI's web search capabilities
            search_result = await openai_web_searcher.search_doctor_reviews(
                doctor_name=doctor_name,
                specialty="",
                location="Malaysia"
            )

            reviews = search_result.get("reviews", [])
            
            # Add source information from Google search
            for review in reviews:
                review["source"] = "google_custom_search + openai_web_search"

            logger.info(f"✅ Extracted {len(reviews)} reviews using OpenAI web search")

            return {
                "reviews": reviews,
                "total_count": len(reviews),
                "source": "google_custom_search + openai_web_search"
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
