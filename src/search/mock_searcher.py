"""
Mock searcher for testing without real API keys
"""

import logging
from typing import List, Dict
import random

logger = logging.getLogger(__name__)


class MockSearcher:
    """Mock searcher that generates fake reviews for testing"""

    async def search_doctor(self, doctor_name: str, location: str = "") -> Dict:
        """
        Generate mock search results

        Args:
            doctor_name: Doctor's name
            location: Optional location

        Returns:
            Dict with mock reviews
        """
        logger.info(f"🧪 [MOCK] Searching for: {doctor_name}")

        # Generate mock reviews
        mock_reviews = [
            {
                "doctor_name": doctor_name,
                "source": "google_maps",
                "url": f"https://maps.google.com/mock/{doctor_name}",
                "snippet": f"{doctor_name} has excellent bedside manner, accurate diagnosis, and superb medical skills. Highly recommended!",
                "rating": 5.0,
                "review_date": "2025-09-15",
                "author_name": "Patient A",
                "sentiment": None
            },
            {
                "doctor_name": doctor_name,
                "source": "google_maps",
                "url": f"https://maps.google.com/mock/{doctor_name}",
                "snippet": f"Very confident in {doctor_name}'s care, high professional level, very responsible to patients",
                "rating": 4.5,
                "review_date": "2025-09-10",
                "author_name": "Patient B",
                "sentiment": None
            },
            {
                "doctor_name": doctor_name,
                "source": "facebook",
                "url": f"https://facebook.com/mock/{doctor_name}",
                "snippet": f"Dr. {doctor_name} is very experienced, patiently answers questions, excellent treatment results",
                "rating": 5.0,
                "review_date": "2025-08-28",
                "author_name": "Patient C",
                "sentiment": None
            },
            {
                "doctor_name": doctor_name,
                "source": "google_maps",
                "url": f"https://maps.google.com/mock/{doctor_name}",
                "snippet": f"Wait time is a bit long, but {doctor_name} is very conscientious and responsible, worth the wait",
                "rating": 4.0,
                "review_date": "2025-08-20",
                "author_name": "Patient D",
                "sentiment": None
            },
            {
                "doctor_name": doctor_name,
                "source": "hospital_website",
                "url": f"https://hospital.com/doctors/{doctor_name}",
                "snippet": f"{doctor_name} service attitude is average, communication not sufficient, hope for improvement",
                "rating": 2.5,
                "review_date": "2025-08-05",
                "author_name": "Patient E",
                "sentiment": None
            },
            {
                "doctor_name": doctor_name,
                "source": "facebook",
                "url": f"https://facebook.com/mock/{doctor_name}",
                "snippet": f"Not very satisfied with {doctor_name}'s diagnosis, feels not detailed enough",
                "rating": 2.0,
                "review_date": "2025-07-15",
                "author_name": "Patient F",
                "sentiment": None
            }
        ]

        # Randomly select 4-6 reviews
        num_reviews = random.randint(4, 6)
        selected_reviews = random.sample(mock_reviews, num_reviews)

        logger.info(f"✅ [MOCK] Generated {len(selected_reviews)} mock reviews")

        return {
            "doctor_name": doctor_name,
            "reviews": selected_reviews,
            "source": "mock",
            "total_count": len(selected_reviews)
        }


# Global mock searcher
mock_searcher = MockSearcher()
