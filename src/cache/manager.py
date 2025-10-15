"""
Cache manager for doctor reviews
Handles caching logic to minimize API calls
"""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from src.database import db
from src.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages cached doctor review data"""

    def __init__(self):
        self.default_ttl_days = settings.cache_default_ttl_days
        self.hot_ttl_days = settings.cache_hot_doctor_ttl_days
        self.cold_ttl_days = settings.cache_cold_doctor_ttl_days

    async def get_cached_reviews(self, doctor_id: str) -> Optional[List[Dict]]:
        """
        Get cached reviews for a doctor

        Args:
            doctor_id: Doctor's unique identifier

        Returns:
            List of cached reviews or None if not found/expired
        """
        try:
            query = """
                SELECT
                    snippet, sentiment, source, url, rating,
                    review_date, author_name, metadata
                FROM doctor_reviews
                WHERE doctor_id = $1
                  AND valid_until > NOW()
                  AND display_policy != 'hidden'
                ORDER BY
                    CASE sentiment
                        WHEN 'positive' THEN 1
                        WHEN 'neutral' THEN 2
                        WHEN 'negative' THEN 3
                    END,
                    rating DESC,
                    review_date DESC
            """

            reviews = await db.fetch(query, doctor_id)

            if reviews:
                logger.info(f"✅ Cache hit for doctor_id: {doctor_id}, found {len(reviews)} reviews")
                return reviews
            else:
                logger.info(f"❌ Cache miss for doctor_id: {doctor_id}")
                return None

        except Exception as e:
            logger.error(f"Error fetching cached reviews: {e}")
            return None

    async def save_reviews(
        self,
        doctor_id: str,
        doctor_name: str,
        reviews: List[Dict],
        ttl_days: Optional[int] = None
    ) -> int:
        """
        Save reviews to cache

        Args:
            doctor_id: Doctor's unique identifier
            doctor_name: Doctor's name
            reviews: List of review dicts
            ttl_days: Time-to-live in days (optional)

        Returns:
            Number of reviews saved
        """
        if not reviews:
            return 0

        if ttl_days is None:
            ttl_days = self.default_ttl_days

        try:
            saved_count = 0
            valid_until = datetime.now() + timedelta(days=ttl_days)

            for review in reviews:
                # Generate unique hash
                content = f"{review.get('url', '')}|{review.get('snippet', '')}"
                hash_value = hashlib.sha256(content.encode()).hexdigest()

                # Insert or ignore if duplicate (PostgreSQL: ON CONFLICT DO NOTHING)
                query = """
                    INSERT INTO doctor_reviews (
                        doctor_id, doctor_name, doctor_specialty, hospital_name, location,
                        source, url, snippet, sentiment, rating, review_date, author_name,
                        hash, fetched_at, valid_until, display_policy, metadata
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, NOW(), $14, 'normal', $15)
                    ON CONFLICT (hash) DO NOTHING
                """

                # Convert empty strings to None for database fields
                review_date = review.get("review_date")
                if review_date == "":
                    review_date = None

                result = await db.execute(
                    query,
                    doctor_id,
                    doctor_name,
                    review.get("doctor_specialty"),
                    review.get("hospital_name"),
                    review.get("location"),
                    review.get("source"),
                    review.get("url"),
                    review.get("snippet"),
                    review.get("sentiment"),
                    review.get("rating"),
                    review_date,  # Use None instead of empty string
                    review.get("author_name"),
                    hash_value,
                    valid_until.isoformat(),
                    None  # metadata as JSON
                )

                # PostgreSQL execute returns command tag (e.g., "INSERT 0 1")
                # Check if insertion was successful
                if "INSERT" in result:
                    saved_count += 1

            logger.info(f"💾 Saved {saved_count}/{len(reviews)} reviews to cache for {doctor_name}")
            return saved_count

        except Exception as e:
            logger.error(f"Error saving reviews to cache: {e}")
            return 0

    async def check_cache_status(self, doctor_id: str) -> Dict:
        """
        Check cache status for a doctor

        Args:
            doctor_id: Doctor's unique identifier

        Returns:
            Dict with cache statistics
        """
        try:
            query = """
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN valid_until > NOW() THEN 1 ELSE 0 END) as valid,
                    MAX(fetched_at) as last_fetched
                FROM doctor_reviews
                WHERE doctor_id = $1
            """

            result = await db.fetchrow(query, doctor_id)

            return {
                "total_cached": result["total"] if result else 0,
                "valid_count": result["valid"] if result else 0,
                "last_fetched": result["last_fetched"] if result else None,
                "cache_valid": (result["valid"] if result else 0) > 0
            }

        except Exception as e:
            logger.error(f"Error checking cache status: {e}")
            return {"cache_valid": False}

    def generate_doctor_id(self, name: str, hospital: str = "", location: str = "") -> str:
        """
        Generate a unique doctor ID from name and optional identifiers

        Normalizes doctor names to ensure consistent cache hits:
        - Removes common prefixes (Dr., Dr, Doctor, Prof., Prof)
        - Converts to lowercase
        - Removes extra whitespace
        - This ensures "Dr. Smith", "Dr Smith", and "Smith" all map to same ID

        Args:
            name: Doctor's name
            hospital: Hospital name (optional)
            location: Location (optional)

        Returns:
            Unique doctor ID (MD5 hash)
        """
        # Normalize name for consistent cache hits
        normalized_name = name.strip().lower()

        # Remove common prefixes
        prefixes = ["doctor ", "dr. ", "dr ", "prof. ", "prof "]
        for prefix in prefixes:
            if normalized_name.startswith(prefix):
                normalized_name = normalized_name[len(prefix):].strip()
                break

        # Remove extra whitespace
        normalized_name = " ".join(normalized_name.split())

        # Normalize hospital and location
        normalized_hospital = hospital.strip().lower() if hospital else ""
        normalized_location = location.strip().lower() if location else ""

        identifier = f"{normalized_name}|{normalized_hospital}|{normalized_location}"
        return hashlib.md5(identifier.encode()).hexdigest()

    async def cleanup_expired_cache(self) -> int:
        """
        Clean up expired cache entries (older than 30 days)

        Returns:
            Number of deleted entries
        """
        try:
            query = """
                DELETE FROM doctor_reviews
                WHERE valid_until < NOW() - INTERVAL '30 days'
            """

            result = await db.execute(query)
            logger.info(f"🧹 Cleaned up {result} expired cache entries")
            return result

        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
            return 0


# Global cache manager instance
cache_manager = CacheManager()
