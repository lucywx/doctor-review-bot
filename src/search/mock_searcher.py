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
                "snippet": f"{doctor_name}态度很好，诊断准确，医术精湛，强烈推荐！",
                "rating": 5.0,
                "review_date": "2025-09-15",
                "author_name": "患者A",
                "sentiment": None
            },
            {
                "doctor_name": doctor_name,
                "source": "google_maps",
                "url": f"https://maps.google.com/mock/{doctor_name}",
                "snippet": f"在{doctor_name}这里看病很放心，专业水平高，对患者很负责",
                "rating": 4.5,
                "review_date": "2025-09-10",
                "author_name": "患者B",
                "sentiment": None
            },
            {
                "doctor_name": doctor_name,
                "source": "facebook",
                "url": f"https://facebook.com/mock/{doctor_name}",
                "snippet": f"{doctor_name}医生经验丰富，耐心解答问题，治疗效果很好",
                "rating": 5.0,
                "review_date": "2025-08-28",
                "author_name": "患者C",
                "sentiment": None
            },
            {
                "doctor_name": doctor_name,
                "source": "google_maps",
                "url": f"https://maps.google.com/mock/{doctor_name}",
                "snippet": f"等待时间比较长，但{doctor_name}很认真负责，值得等待",
                "rating": 4.0,
                "review_date": "2025-08-20",
                "author_name": "患者D",
                "sentiment": None
            },
            {
                "doctor_name": doctor_name,
                "source": "hospital_website",
                "url": f"https://hospital.com/doctors/{doctor_name}",
                "snippet": f"{doctor_name}服务态度一般，沟通不够充分，希望改进",
                "rating": 2.5,
                "review_date": "2025-08-05",
                "author_name": "患者E",
                "sentiment": None
            },
            {
                "doctor_name": doctor_name,
                "source": "facebook",
                "url": f"https://facebook.com/mock/{doctor_name}",
                "snippet": f"对{doctor_name}的诊断不太满意，感觉不够细致",
                "rating": 2.0,
                "review_date": "2025-07-15",
                "author_name": "患者F",
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
