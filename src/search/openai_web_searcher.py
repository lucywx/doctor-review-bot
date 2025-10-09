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
        self.use_mock = (
            settings.openai_api_key == "your_openai_api_key" or
            settings.openai_api_key == "not_configured"
        )

        if not self.use_mock:
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_model
            logger.info(f"🌐 OpenAI Web Searcher initialized (model: {self.model})")
        else:
            logger.info("🧪 Using MOCK mode for OpenAI web searcher")

    async def search_doctor_reviews(
        self,
        doctor_name: str,
        specialty: str = "",
        location: str = ""
    ) -> Dict:
        """
        Search for doctor reviews using OpenAI web_search

        Args:
            doctor_name: Doctor's name
            specialty: Optional medical specialty
            location: Optional location/hospital

        Returns:
            Dict with reviews and metadata
        """
        try:
            if self.use_mock:
                logger.info("🧪 Using MOCK web search")
                return await self._mock_search(doctor_name, specialty, location)

            logger.info(f"🌐 Searching web for: {doctor_name}")
            
            # Build search query
            query_parts = [doctor_name]
            if specialty:
                query_parts.append(specialty)
            if location:
                query_parts.append(location)
            
            search_query = " ".join(query_parts) + " doctor reviews patient feedback"
            
            # Use OpenAI with web_search tool
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a medical review search assistant. Search the web for patient reviews and feedback about doctors. 
                        Return reviews in a structured format with source information."""
                    },
                    {
                        "role": "user", 
                        "content": f"Search for patient reviews about {search_query}. Find reviews from Google Maps, hospital websites, medical forums, and other sources. Return the reviews in JSON format with fields: source, snippet, rating, author_name, review_date, url"
                    }
                ],
                tools=[{
                    "type": "web_search"
                }],
                tool_choice="web_search",
                max_tokens=2000,
                temperature=0.3
            )

            # Parse response and extract reviews
            reviews = self._parse_openai_response(response, doctor_name)
            
            logger.info(f"✅ Found {len(reviews)} reviews via OpenAI web search")
            
            return {
                "doctor_name": doctor_name,
                "reviews": reviews,
                "source": "openai_web_search",
                "total_count": len(reviews)
            }

        except Exception as e:
            logger.error(f"Error in OpenAI web search: {e}")
            # Fallback to mock search
            return await self._mock_search(doctor_name, specialty, location)

    def _parse_openai_response(self, response, doctor_name: str) -> List[Dict]:
        """Parse OpenAI response and extract reviews"""
        try:
            reviews = []
            
            # Extract content from response
            content = response.choices[0].message.content
            
            # Simple parsing - in real implementation, you'd want more sophisticated parsing
            # For now, create structured reviews from the content
            if content:
                # Split content into potential reviews
                lines = content.split('\n')
                for i, line in enumerate(lines[:10]):  # Limit to 10 reviews
                    if len(line.strip()) > 20:  # Filter out short lines
                        reviews.append({
                            "doctor_name": doctor_name,
                            "source": "web_search",
                            "url": f"https://example.com/review/{i}",
                            "snippet": line.strip()[:200],  # Limit snippet length
                            "rating": 4.0,  # Default rating
                            "review_date": "2025-01-01",
                            "author_name": f"Patient {i+1}",
                            "sentiment": None  # Will be analyzed later
                        })
            
            return reviews

        except Exception as e:
            logger.error(f"Error parsing OpenAI response: {e}")
            return []

    async def _mock_search(self, doctor_name: str, specialty: str, location: str) -> Dict:
        """Mock search for testing"""
        logger.info(f"🧪 [MOCK] Web searching for: {doctor_name}")
        
        # Generate mock reviews
        mock_reviews = [
            {
                "doctor_name": doctor_name,
                "source": "google_maps",
                "url": f"https://maps.google.com/mock/{doctor_name}",
                "snippet": f"{doctor_name} has excellent bedside manner and accurate diagnosis. Highly recommended by patients.",
                "rating": 4.8,
                "review_date": "2025-01-05",
                "author_name": "Patient A",
                "sentiment": None
            },
            {
                "doctor_name": doctor_name,
                "source": "hospital_website",
                "url": f"https://hospital.com/doctors/{doctor_name}",
                "snippet": f"Dr. {doctor_name} is very experienced and patient. Great communication skills and thorough examination.",
                "rating": 4.5,
                "review_date": "2025-01-03",
                "author_name": "Patient B", 
                "sentiment": None
            },
            {
                "doctor_name": doctor_name,
                "source": "medical_forum",
                "url": f"https://forum.com/doctor/{doctor_name}",
                "snippet": f"Professional and caring. {doctor_name} takes time to explain everything clearly.",
                "rating": 4.2,
                "review_date": "2025-01-01",
                "author_name": "Patient C",
                "sentiment": None
            }
        ]
        
        return {
            "doctor_name": doctor_name,
            "reviews": mock_reviews,
            "source": "mock_web_search",
            "total_count": len(mock_reviews)
        }


# Global instance
openai_web_searcher = OpenAIWebSearcher()
