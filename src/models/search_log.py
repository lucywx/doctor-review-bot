"""
Search log recording for analytics and cost tracking
"""

import logging
import json
from datetime import datetime
from typing import Optional, List
from src.database import db

logger = logging.getLogger(__name__)


class SearchLogger:
    """Log search queries for analytics"""

    async def log_search(
        self,
        user_id: str,
        doctor_name: str,
        doctor_id: str,
        cache_hit: bool,
        response_time_ms: int,
        sources_used: List[str],
        results_count: int,
        api_calls_count: int = 0,
        estimated_cost_usd: float = 0.0,
        error_message: Optional[str] = None
    ):
        """
        Log a search query

        Args:
            user_id: User identifier
            doctor_name: Doctor's name
            doctor_id: Doctor's ID
            cache_hit: Whether cache was hit
            response_time_ms: Response time in milliseconds
            sources_used: List of data sources used
            results_count: Number of results returned
            api_calls_count: Number of API calls made
            estimated_cost_usd: Estimated cost in USD
            error_message: Error message if any
        """
        try:
            query = """
                INSERT INTO search_logs (
                    user_id, doctor_name, doctor_id, location,
                    cache_hit, response_time_ms, sources_used, results_count,
                    api_calls_count, estimated_cost_usd, error_message,
                    created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW())
            """

            # Convert sources list to JSON string
            sources_json = json.dumps(sources_used)

            await db.execute(
                query,
                user_id,
                doctor_name,
                doctor_id,
                None,  # location
                cache_hit,  # PostgreSQL uses boolean
                response_time_ms,
                sources_json,
                results_count,
                api_calls_count,
                estimated_cost_usd,
                error_message
            )

            logger.info(f"📝 Logged search: {doctor_name} (cache_hit={cache_hit}, time={response_time_ms}ms)")

        except Exception as e:
            logger.error(f"Error logging search: {e}")

    async def get_user_search_history(self, user_id: str, limit: int = 10) -> List[dict]:
        """Get user's recent search history"""
        try:
            query = """
                SELECT doctor_name, cache_hit, response_time_ms, results_count, created_at
                FROM search_logs
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT $2
            """

            results = await db.fetch(query, user_id, limit)
            return results

        except Exception as e:
            logger.error(f"Error getting search history: {e}")
            return []

    async def get_daily_stats(self) -> dict:
        """Get today's statistics"""
        try:
            query = """
                SELECT
                    COUNT(*) as total_searches,
                    SUM(CASE WHEN cache_hit = true THEN 1 ELSE 0 END) as cache_hits,
                    AVG(response_time_ms) as avg_response_time,
                    SUM(estimated_cost_usd) as total_cost,
                    SUM(api_calls_count) as total_api_calls
                FROM search_logs
                WHERE DATE(created_at) = CURRENT_DATE
            """

            result = await db.fetchrow(query)

            if result:
                return {
                    "total_searches": result["total_searches"] or 0,
                    "cache_hits": result["cache_hits"] or 0,
                    "cache_hit_rate": (result["cache_hits"] or 0) / max(result["total_searches"] or 1, 1) * 100,
                    "avg_response_time_ms": result["avg_response_time"] or 0,
                    "total_cost_usd": result["total_cost"] or 0,
                    "total_api_calls": result["total_api_calls"] or 0
                }

            return {}

        except Exception as e:
            logger.error(f"Error getting daily stats: {e}")
            return {}

    async def get_popular_doctors(self, limit: int = 10) -> List[dict]:
        """Get most searched doctors"""
        try:
            query = """
                SELECT
                    doctor_name,
                    COUNT(*) as search_count,
                    MAX(created_at) as last_searched
                FROM search_logs
                WHERE DATE(created_at) >= CURRENT_DATE - INTERVAL '7 days'
                GROUP BY doctor_name
                ORDER BY search_count DESC
                LIMIT $1
            """

            results = await db.fetch(query, limit)
            return results

        except Exception as e:
            logger.error(f"Error getting popular doctors: {e}")
            return []


# Global instance
search_logger = SearchLogger()
