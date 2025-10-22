"""
Update admin user quota to 500/month
"""

import asyncio
import asyncpg
from src.config import settings

async def update_admin_quota():
    """Update admin user's quota to 500/month"""

    # Connect to database
    conn = await asyncpg.connect(settings.database_url)

    try:
        # Get admin phone number from settings
        admin_phone = settings.admin_phone_number
        print(f"Admin phone number: {admin_phone}")

        # Check current quota
        user = await conn.fetchrow(
            "SELECT user_id, daily_quota, today_usage, role FROM user_sessions WHERE user_id = $1",
            admin_phone
        )

        if not user:
            print(f"❌ Admin user not found: {admin_phone}")
            return

        print(f"Current quota: {user['daily_quota']}")
        print(f"Current usage: {user['today_usage']}")
        print(f"Current role: {user['role']}")

        # Update to admin quota (500/month)
        await conn.execute(
            """
            UPDATE user_sessions
            SET daily_quota = $1, role = 'admin'
            WHERE user_id = $2
            """,
            settings.rate_limit_admin_monthly,  # 500
            admin_phone
        )

        # Verify update
        updated_user = await conn.fetchrow(
            "SELECT user_id, daily_quota, today_usage, role FROM user_sessions WHERE user_id = $1",
            admin_phone
        )

        print(f"\n✅ Updated admin quota:")
        print(f"New quota: {updated_user['daily_quota']}")
        print(f"Usage: {updated_user['today_usage']}")
        print(f"Role: {updated_user['role']}")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(update_admin_quota())
