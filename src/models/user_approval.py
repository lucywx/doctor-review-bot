"""
User approval system
Manages whitelist and admin notifications
"""

import logging
import aiosqlite
from src.config import settings

logger = logging.getLogger(__name__)


class UserApprovalManager:
    """Manages user approval and whitelist"""

    async def _get_db(self):
        """Get database connection"""
        db_path = settings.database_url.replace("sqlite:///", "").replace("./", "")
        return await aiosqlite.connect(db_path)

    async def is_user_approved(self, phone_number: str) -> bool:
        """Check if user is approved"""
        # Admin is always approved
        if phone_number == settings.admin_phone_number:
            return True

        # If approval not required, everyone is approved
        if not settings.require_approval:
            return True

        # Check database
        db = await self._get_db()
        try:
            cursor = await db.execute(
                "SELECT approved FROM user_whitelist WHERE phone_number = ?",
                (phone_number,)
            )
            row = await cursor.fetchone()

            if row:
                return bool(row[0])

            # New user - create pending entry
            await db.execute(
                "INSERT INTO user_whitelist (phone_number, approved, requested_at) VALUES (?, 0, CURRENT_TIMESTAMP)",
                (phone_number,)
            )
            await db.commit()
            logger.info(f"🆕 New user pending approval: {phone_number}")
            return False
        finally:
            await db.close()

    async def approve_user(self, phone_number: str) -> bool:
        """Approve a user"""
        try:
            db = await self._get_db()
            try:
                await db.execute(
                    """INSERT INTO user_whitelist (phone_number, approved, approved_at)
                       VALUES (?, 1, CURRENT_TIMESTAMP)
                       ON CONFLICT(phone_number) DO UPDATE SET approved = 1, approved_at = CURRENT_TIMESTAMP""",
                    (phone_number,)
                )
                await db.commit()
                logger.info(f"✅ User approved: {phone_number}")
                return True
            finally:
                await db.close()
        except Exception as e:
            logger.error(f"❌ Error approving user: {e}")
            return False

    async def reject_user(self, phone_number: str) -> bool:
        """Reject a user"""
        try:
            db = await self._get_db()
            try:
                await db.execute("DELETE FROM user_whitelist WHERE phone_number = ?", (phone_number,))
                await db.commit()
                logger.info(f"❌ User rejected: {phone_number}")
                return True
            finally:
                await db.close()
        except Exception as e:
            logger.error(f"❌ Error rejecting user: {e}")
            return False

    async def get_pending_users(self) -> list:
        """Get list of users pending approval"""
        try:
            db = await self._get_db()
            try:
                cursor = await db.execute(
                    "SELECT phone_number, requested_at FROM user_whitelist WHERE approved = 0 ORDER BY requested_at DESC"
                )
                rows = await cursor.fetchall()
                return [{"phone_number": row[0], "requested_at": row[1]} for row in rows]
            finally:
                await db.close()
        except Exception as e:
            logger.error(f"❌ Error getting pending users: {e}")
            return []

    async def send_admin_notification(self, new_user_phone: str, first_message: str):
        """Send notification to admin"""
        try:
            from src.whatsapp.client_mock import whatsapp_client

            notification = f"""🔔 *New User Request*

📱 Phone: {new_user_phone}
💬 First message: "{first_message}"

To approve: `approve {new_user_phone}`
To reject: `reject {new_user_phone}`"""

            await whatsapp_client.send_message(settings.admin_phone_number, notification)
            logger.info(f"📤 Admin notification sent for {new_user_phone}")
        except Exception as e:
            logger.error(f"❌ Error sending admin notification: {e}")


# Global instance
user_approval_manager = UserApprovalManager()
