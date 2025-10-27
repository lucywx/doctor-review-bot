"""
Google Places API client for fetching Google Maps reviews
"""

import httpx
import logging
from typing import Optional, Dict, List
from src.config import settings

logger = logging.getLogger(__name__)


class GooglePlacesClient:
    """Client for Google Places API to fetch reviews from Google Maps"""

    def __init__(self):
        self.api_key = settings.google_places_api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place"

        if not self.api_key or self.api_key == "not_required":
            logger.warning("Google Places API key not configured")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("Google Places API client initialized")

    async def search_doctor(self, doctor_name: str, location: str = "Malaysia") -> Optional[Dict]:
        """
        Search for a doctor on Google Maps

        Args:
            doctor_name: Name of the doctor to search
            location: Location to search in (default: Malaysia)

        Returns:
            Place details with reviews, or None if not found
        """
        if not self.enabled:
            logger.warning("Google Places API is disabled (no API key)")
            return None

        try:
            # Step 1: Search for the place
            place_id = await self._search_place(doctor_name, location)
            if not place_id:
                logger.info(f"No Google Maps place found for: {doctor_name}")
                return None

            # Step 2: Get place details with reviews
            place_details = await self._get_place_details(place_id, doctor_name)
            return place_details

        except Exception as e:
            logger.error(f"Error searching Google Places for {doctor_name}: {e}")
            return None

    async def _search_place(self, doctor_name: str, location: str) -> Optional[str]:
        """
        Search for a place and return its place_id

        Args:
            doctor_name: Name of the doctor
            location: Location to search

        Returns:
            place_id if found, None otherwise
        """
        url = f"{self.base_url}/textsearch/json"

        # Try different query formats
        queries = [
            f"Dr {doctor_name} {location}",
            f"{doctor_name} doctor {location}",
            f"{doctor_name} clinic {location}"
        ]

        async with httpx.AsyncClient(timeout=30.0) as client:
            for query in queries:
                params = {
                    "query": query,
                    "key": self.api_key,
                    "language": "en"
                }

                try:
                    response = await client.get(url, params=params)
                    data = response.json()

                    if data.get("status") == "OK" and data.get("results"):
                        place_id = data["results"][0]["place_id"]
                        logger.info(f"Found place_id for {doctor_name}: {place_id}")
                        return place_id

                except Exception as e:
                    logger.error(f"Error in place search with query '{query}': {e}")
                    continue

        return None

    async def _get_place_details(self, place_id: str, doctor_name: str) -> Optional[Dict]:
        """
        Get detailed information about a place including reviews

        Args:
            place_id: Google Maps place ID
            doctor_name: Doctor's name for filtering reviews

        Returns:
            Dictionary with place details and reviews
        """
        url = f"{self.base_url}/details/json"

        params = {
            "place_id": place_id,
            "fields": "name,rating,user_ratings_total,reviews,formatted_address,url",
            "key": self.api_key,
            "language": "en"
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                data = response.json()

                if data.get("status") == "OK":
                    result = data.get("result", {})

                    # Format the response
                    place_data = {
                        "name": result.get("name", ""),
                        "rating": result.get("rating", 0),
                        "total_reviews": result.get("user_ratings_total", 0),
                        "address": result.get("formatted_address", ""),
                        "url": result.get("url", ""),
                        "reviews": self._format_reviews(result.get("reviews", []), doctor_name)
                    }

                    logger.info(f"Retrieved {len(place_data['reviews'])} reviews from Google Maps (Total: {place_data['total_reviews']})")
                    return place_data

                else:
                    logger.warning(f"Place details request failed: {data.get('status')}")
                    return None

        except Exception as e:
            logger.error(f"Error getting place details for {place_id}: {e}")
            return None

    def _format_reviews(self, reviews: List[Dict], doctor_name: str) -> List[Dict]:
        """
        Format reviews into standardized structure with filtering

        Args:
            reviews: Raw reviews from Places API
            doctor_name: Doctor's name for filtering

        Returns:
            List of formatted review dictionaries
        """
        formatted = []
        
        # Extract key parts of doctor's name for filtering
        name_parts = doctor_name.lower().replace("dr.", "").replace("dr", "").strip().split()
        key_name = name_parts[0] if name_parts else doctor_name.lower()
        
        for review in reviews:
            review_text = review.get("text", "").lower()
            
            # Filter 1: Must mention doctor's name or be clearly about the doctor
            if not self._is_review_about_doctor(review_text, key_name, doctor_name):
                logger.debug(f"⏭️ Filtered out review not about {doctor_name}: {review_text[:50]}...")
                continue
            
            # Filter 2: Skip reviews that are mainly about clinic/hospital policies
            if self._is_clinic_policy_review(review_text):
                logger.debug(f"⏭️ Filtered out clinic policy review: {review_text[:50]}...")
                continue
            
            # Filter 3: Skip reviews that are mainly about nurses/staff (not the doctor)
            if self._is_staff_review(review_text):
                logger.debug(f"⏭️ Filtered out staff review: {review_text[:50]}...")
                continue

            formatted.append({
                "author": review.get("author_name", "Anonymous"),
                "rating": review.get("rating", 0),
                "text": review.get("text", ""),
                "time": review.get("relative_time_description", ""),
                "source": "Google Maps"
            })

        logger.info(f"📊 Filtered {len(reviews)} → {len(formatted)} reviews for {doctor_name}")
        return formatted

    def _is_review_about_doctor(self, review_text: str, key_name: str, full_name: str) -> bool:
        """
        Check if review is actually about the specific doctor
        
        Args:
            review_text: Review text in lowercase
            key_name: First name part of doctor
            full_name: Full doctor name
            
        Returns:
            True if review is about the doctor
        """
        # Must mention doctor's name or "dr" + first name
        if key_name not in review_text and "dr" not in review_text:
            return False
        
        # Check for generic doctor references that might not be specific
        generic_terms = ["the doctor", "this doctor", "doctor"]
        if any(term in review_text for term in generic_terms):
            # If only generic terms, need more context to be sure
            if len(review_text) < 50:  # Very short reviews with only generic terms are suspicious
                return False
        
        return True

    def _is_clinic_policy_review(self, review_text: str) -> bool:
        """
        Check if review is mainly about clinic/hospital policies rather than doctor
        
        Args:
            review_text: Review text in lowercase
            
        Returns:
            True if review is about clinic policies
        """
        policy_keywords = [
            "clinic does not",
            "hospital policy",
            "they do not give",
            "clinic said",
            "hospital said",
            "policy",
            "procedure",
            "system",
            "management",
            "appointment system",
            "waiting time",
            "queue"
        ]
        
        # If review contains multiple policy keywords, it's likely about policies
        policy_count = sum(1 for keyword in policy_keywords if keyword in review_text)
        return policy_count >= 2

    def _is_staff_review(self, review_text: str) -> bool:
        """
        Check if review is mainly about nurses/staff rather than doctor
        
        Args:
            review_text: Review text in lowercase
            
        Returns:
            True if review is mainly about staff
        """
        staff_keywords = [
            "nurse",
            "nurses", 
            "staff",
            "receptionist",
            "reception",
            "front desk",
            "secretary"
        ]
        
        doctor_keywords = [
            "dr",
            "doctor",
            "physician",
            "specialist"
        ]
        
        staff_count = sum(1 for keyword in staff_keywords if keyword in review_text)
        doctor_count = sum(1 for keyword in doctor_keywords if keyword in review_text)
        
        # Only filter if review is PRIMARILY about staff
        # Condition 1: Short reviews that focus mainly on staff
        if staff_count > doctor_count and len(review_text) < 80:
            return True
        
        # Condition 2: Reviews that mention staff multiple times but barely mention doctor
        # AND the review is short (likely focused only on staff)
        if staff_count >= 3 and doctor_count <= 1 and len(review_text) < 150:
            return True
            
        # Condition 3: Very short reviews that are mainly about staff complaints
        if staff_count >= 2 and doctor_count == 0 and len(review_text) < 100:
            return True
            
        return False


# Global instance
google_places_client = GooglePlacesClient()
