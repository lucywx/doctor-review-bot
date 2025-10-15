"""
User quota management
"""

import hashlib
import logging
from datetime import date
from typing import Optional
from src.database import db
from src.config import settings

logger = logging.getLogger(__name__)


class UserQuotaManager:
    """Manage user daily search quotas"""

    def __init__(self):
        self.daily_quota = settings.rate_limit_per_user_daily

    async def check_and_update_quota(self, user_id: str) -> dict:
        """
        Check if user has remaining quota and update usage

        Args:
            user_id: User's identifier (phone number hash)

        Returns:
            Dict with quota status
        """
        try:
            # Get or create user session
            user = await self._get_or_create_user(user_id)

            # Check if quota needs reset (new day)
            today = date.today()
            if user["quota_reset_at"] != today.isoformat():
                await self._reset_daily_quota(user_id)
                user["today_usage"] = 0

            # Check quota
            if user["today_usage"] >= user["daily_quota"]:
                return {
                    "allowed": False,
                    "remaining": 0,
                    "quota": user["daily_quota"],
                    "used": user["today_usage"]
                }

            # Update usage
            await self._increment_usage(user_id)

            return {
                "allowed": True,
                "remaining": user["daily_quota"] - user["today_usage"] - 1,
                "quota": user["daily_quota"],
                "used": user["today_usage"] + 1
            }

        except Exception as e:
            logger.error(f"Error checking quota: {e}")
            # Allow by default on error
            return {"allowed": True, "error": str(e)}

    async def _get_or_create_user(self, user_id: str) -> dict:
        """Get user or create new one"""
        # Try to get existing user
        query = "SELECT * FROM user_sessions WHERE user_id = $1"
        user = await db.fetchrow(query, user_id)

        if user:
            return user

        # Create new user
        phone_hash = self._hash_phone(user_id)
        query = """
            INSERT INTO user_sessions (
                user_id, phone_number_hash, is_active, role,
                daily_quota, today_usage, total_searches,
                first_seen_at, last_active_at, quota_reset_at
            ) VALUES ($1, $2, true, 'user', $3, 0, 0, NOW(), NOW(), CURRENT_DATE)
        """

        await db.execute(query, user_id, phone_hash, self.daily_quota)

        # Fetch newly created user
        user = await db.fetchrow("SELECT * FROM user_sessions WHERE user_id = $1", user_id)
        logger.info(f"✅ Created new user: {user_id}")
        return user

    async def _reset_daily_quota(self, user_id: str):
        """Reset user's daily quota"""
        query = """
            UPDATE user_sessions
            SET today_usage = 0,
                quota_reset_at = CURRENT_DATE,
                last_active_at = NOW()
            WHERE user_id = $1
        """
        await db.execute(query, user_id)
        logger.info(f"🔄 Reset quota for user: {user_id}")

    async def _increment_usage(self, user_id: str):
        """Increment user's usage count"""
        query = """
            UPDATE user_sessions
            SET today_usage = today_usage + 1,
                total_searches = total_searches + 1,
                last_active_at = NOW()
            WHERE user_id = $1
        """
        await db.execute(query, user_id)

    def _hash_phone(self, phone: str) -> str:
        """Hash phone number for privacy"""
        return hashlib.sha256(phone.encode()).hexdigest()

    async def get_user_stats(self, user_id: str) -> dict:
        """Get user statistics"""
        try:
            query = "SELECT * FROM user_sessions WHERE user_id = $1"
            user = await db.fetchrow(query, user_id)

            if not user:
                return {}

            return {
                "total_searches": user["total_searches"],
                "today_usage": user["today_usage"],
                "daily_quota": user["daily_quota"],
                "remaining": user["daily_quota"] - user["today_usage"],
                "first_seen": user["first_seen_at"],
                "last_active": user["last_active_at"]
            }

        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {}


# Global instance
user_quota_manager = UserQuotaManager()
