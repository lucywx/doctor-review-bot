"""
Facebook Graph API integration
Search for doctor reviews on Facebook public pages
"""

import httpx
import logging
from typing import List, Dict
from src.config import settings

logger = logging.getLogger(__name__)


class FacebookSearcher:
    """Search Facebook for doctor reviews (public pages only)"""

    def __init__(self):
        self.access_token = settings.facebook_access_token
        self.base_url = "https://graph.facebook.com/v18.0"

    async def search_doctor(self, doctor_name: str) -> List[Dict]:
        """
        Search for doctor pages and reviews on Facebook

        Args:
            doctor_name: Doctor's name

        Returns:
            List of review dicts
        """
        try:
            # Step 1: Search for pages
            page_id = await self._search_pages(doctor_name)

            if not page_id:
                logger.info(f"No Facebook pages found for: {doctor_name}")
                return []

            # Step 2: Get page ratings/reviews
            reviews = await self._get_page_reviews(page_id, doctor_name)

            logger.info(f"✅ Found {len(reviews)} reviews from Facebook for {doctor_name}")
            return reviews

        except Exception as e:
            logger.error(f"Error searching Facebook: {e}")
            return []

    async def _search_pages(self, doctor_name: str) -> str:
        """
        Search for Facebook pages

        Args:
            doctor_name: Doctor's name

        Returns:
            Page ID or None
        """
        try:
            url = f"{self.base_url}/pages/search"
            params = {
                "q": doctor_name,
                "type": "page",
                "fields": "id,name,about,category",
                "access_token": self.access_token,
                "limit": 5
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                pages = data.get("data", [])
                if pages:
                    # Return first matching page
                    page_id = pages[0]["id"]
                    logger.info(f"Found Facebook page: {page_id}")
                    return page_id

                return None

        except Exception as e:
            logger.error(f"Error searching Facebook pages: {e}")
            return None

    async def _get_page_reviews(self, page_id: str, doctor_name: str) -> List[Dict]:
        """
        Get reviews for a Facebook page

        Args:
            page_id: Facebook page ID
            doctor_name: Doctor's name

        Returns:
            List of formatted reviews
        """
        try:
            url = f"{self.base_url}/{page_id}/ratings"
            params = {
                "fields": "reviewer,rating,review_text,created_time,open_graph_story",
                "access_token": self.access_token,
                "limit": 50
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                ratings_data = data.get("data", [])

                # Format reviews
                reviews = []
                for item in ratings_data:
                    # Only include reviews with text
                    if item.get("review_text"):
                        reviews.append({
                            "doctor_name": doctor_name,
                            "source": "facebook",
                            "url": f"https://www.facebook.com/{page_id}",
                            "snippet": item["review_text"],
                            "rating": float(item.get("rating", 0)),
                            "review_date": item.get("created_time", "")[:10],  # ISO date
                            "author_name": item.get("reviewer", {}).get("name", "Anonymous"),
                            "sentiment": None  # Will be analyzed later
                        })

                return reviews

        except Exception as e:
            logger.error(f"Error getting Facebook page reviews: {e}")
            return []


# Global instance
facebook_searcher = FacebookSearcher()
