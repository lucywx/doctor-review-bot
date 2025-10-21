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
    """Manage user monthly search quotas"""

    def __init__(self):
        self.monthly_quota = settings.rate_limit_per_user_monthly

    async def check_and_update_quota(self, user_id: str) -> dict:
        """
        Check if user has remaining monthly quota and update usage

        Args:
            user_id: User's identifier (phone number hash)

        Returns:
            Dict with quota status including remaining searches
        """
        try:
            # Get or create user session
            user = await self._get_or_create_user(user_id)

            # Check if quota needs reset (new month - first day of month)
            from datetime import datetime
            today = date.today()
            reset_at = datetime.fromisoformat(user["quota_reset_at"]).date() if isinstance(user["quota_reset_at"], str) else user["quota_reset_at"]

            # Reset if it's a new month
            if today.month != reset_at.month or today.year != reset_at.year:
                await self._reset_monthly_quota(user_id)
                user["today_usage"] = 0

            # Check quota
            monthly_quota = user.get("daily_quota", self.monthly_quota)  # daily_quota field stores monthly quota now
            current_usage = user["today_usage"]

            if current_usage >= monthly_quota:
                return {
                    "allowed": False,
                    "remaining": 0,
                    "quota": monthly_quota,
                    "used": current_usage
                }

            # Update usage
            await self._increment_usage(user_id)

            return {
                "allowed": True,
                "remaining": monthly_quota - current_usage - 1,
                "quota": monthly_quota,
                "used": current_usage + 1
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

        # Determine quota based on user type
        from src.config import settings
        is_admin = (user_id == settings.admin_phone_number)
        quota = settings.rate_limit_admin_monthly if is_admin else self.monthly_quota
        role = 'admin' if is_admin else 'user'

        # Create new user with appropriate settings
        phone_hash = self._hash_phone(user_id)
        query = """
            INSERT INTO user_sessions (
                user_id, phone_number_hash, is_active, role,
                daily_quota, today_usage, total_searches,
                first_seen_at, last_active_at, quota_reset_at
            ) VALUES ($1, $2, true, $3, $4, 0, 0, NOW(), NOW(), CURRENT_DATE)
        """

        await db.execute(query, user_id, phone_hash, role, quota)

        # Fetch newly created user
        user = await db.fetchrow("SELECT * FROM user_sessions WHERE user_id = $1", user_id)
        logger.info(f"✅ Created new user: {user_id} (role: {role}, monthly quota: {quota})")
        return user

    async def _reset_monthly_quota(self, user_id: str):
        """Reset user's monthly quota"""
        query = """
            UPDATE user_sessions
            SET today_usage = 0,
                quota_reset_at = CURRENT_DATE,
                last_active_at = NOW()
            WHERE user_id = $1
        """
        await db.execute(query, user_id)
        logger.info(f"🔄 Reset monthly quota for user: {user_id}")

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

            monthly_quota = user.get("daily_quota", 50)  # daily_quota field stores monthly quota
            monthly_usage = user["today_usage"]  # today_usage stores monthly usage

            return {
                "total_searches": user["total_searches"],
                "monthly_usage": monthly_usage,
                "monthly_quota": monthly_quota,
                "remaining": monthly_quota - monthly_usage,
                "first_seen": user["first_seen_at"],
                "last_active": user["last_active_at"],
                "role": user.get("role", "user")
            }

        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {}


# Global instance
user_quota_manager = UserQuotaManager()
