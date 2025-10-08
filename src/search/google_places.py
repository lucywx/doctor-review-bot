"""
Google Places API integration
Search for doctor reviews on Google Maps
"""

import httpx
import logging
from typing import List, Dict, Optional
from datetime import datetime
from src.config import settings

logger = logging.getLogger(__name__)


class GooglePlacesSearcher:
    """Search Google Places/Maps for doctor reviews"""

    def __init__(self):
        self.api_key = settings.google_places_api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place"

    async def search_doctor(self, doctor_name: str, location: str = "") -> List[Dict]:
        """
        Search for a doctor on Google Places

        Args:
            doctor_name: Doctor's name
            location: Optional location to narrow search

        Returns:
            List of review dicts
        """
        try:
            # Step 1: Text search to find the place
            place_id = await self._find_place(doctor_name, location)

            if not place_id:
                logger.info(f"No Google Places results for: {doctor_name}")
                return []

            # Step 2: Get place details including reviews
            reviews = await self._get_place_reviews(place_id, doctor_name)

            logger.info(f"✅ Found {len(reviews)} reviews from Google Maps for {doctor_name}")
            return reviews

        except Exception as e:
            logger.error(f"Error searching Google Places: {e}")
            return []

    async def _find_place(self, doctor_name: str, location: str = "") -> Optional[str]:
        """
        Find place ID for a doctor

        Args:
            doctor_name: Doctor's name
            location: Optional location

        Returns:
            Place ID or None
        """
        try:
            # Build search query
            query = f"{doctor_name} 医生 {location}".strip()

            url = f"{self.base_url}/textsearch/json"
            params = {
                "query": query,
                "key": self.api_key,
                "language": "zh-CN",
                "type": "doctor"
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if data["status"] == "OK" and data.get("results"):
                    place_id = data["results"][0]["place_id"]
                    logger.info(f"Found place_id: {place_id}")
                    return place_id

                return None

        except Exception as e:
            logger.error(f"Error finding place: {e}")
            return None

    async def _get_place_reviews(self, place_id: str, doctor_name: str) -> List[Dict]:
        """
        Get reviews for a place

        Args:
            place_id: Google Place ID
            doctor_name: Doctor's name

        Returns:
            List of formatted reviews
        """
        try:
            url = f"{self.base_url}/details/json"
            params = {
                "place_id": place_id,
                "fields": "name,rating,reviews,formatted_address,url,user_ratings_total",
                "key": self.api_key,
                "language": "zh-CN"
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if data["status"] != "OK":
                    return []

                result = data.get("result", {})
                reviews_data = result.get("reviews", [])

                # Format reviews
                reviews = []
                for review in reviews_data:
                    reviews.append({
                        "doctor_name": doctor_name,
                        "source": "google_maps",
                        "url": result.get("url", ""),
                        "snippet": review.get("text", ""),
                        "rating": float(review.get("rating", 0)),
                        "review_date": self._parse_timestamp(review.get("time")),
                        "author_name": review.get("author_name", "Anonymous"),
                        "sentiment": None  # Will be analyzed later
                    })

                return reviews

        except Exception as e:
            logger.error(f"Error getting place reviews: {e}")
            return []

    def _parse_timestamp(self, timestamp: Optional[int]) -> Optional[str]:
        """Convert Unix timestamp to ISO date string"""
        if timestamp:
            try:
                dt = datetime.fromtimestamp(timestamp)
                return dt.strftime("%Y-%m-%d")
            except:
                pass
        return None


# Global instance
google_places_searcher = GooglePlacesSearcher()
