"""
Database migration script: SQLite to PostgreSQL
Exports data from SQLite and imports to PostgreSQL
"""

import asyncio
import aiosqlite
import asyncpg
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class DatabaseMigrator:
    """Migrate data from SQLite to PostgreSQL"""

    def __init__(self, sqlite_path: str, postgres_url: str):
        self.sqlite_path = sqlite_path
        self.postgres_url = postgres_url
        self.sqlite_conn = None
        self.postgres_pool = None

    async def connect(self):
        """Connect to both databases"""
        try:
            # Connect to SQLite
            self.sqlite_conn = await aiosqlite.connect(self.sqlite_path)
            self.sqlite_conn.row_factory = aiosqlite.Row
            logger.info(f"✅ Connected to SQLite: {self.sqlite_path}")

            # Connect to PostgreSQL
            self.postgres_pool = await asyncpg.create_pool(self.postgres_url)
            logger.info(f"✅ Connected to PostgreSQL")

        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            raise

    async def close(self):
        """Close database connections"""
        if self.sqlite_conn:
            await self.sqlite_conn.close()
        if self.postgres_pool:
            await self.postgres_pool.close()
        logger.info("🔌 Closed database connections")

    async def _count_records(self, table: str) -> tuple:
        """Count records in both databases"""
        # SQLite count
        async with self.sqlite_conn.execute(f"SELECT COUNT(*) FROM {table}") as cursor:
            sqlite_count = (await cursor.fetchone())[0]

        # PostgreSQL count
        async with self.postgres_pool.acquire() as conn:
            pg_count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")

        return sqlite_count, pg_count

    async def migrate_users(self):
        """Migrate users table"""
        logger.info("\n📋 Migrating users...")

        try:
            # Fetch from SQLite
            async with self.sqlite_conn.execute(
                "SELECT phone_number_hash, daily_query_count, quota_reset_at, created_at FROM users"
            ) as cursor:
                users = await cursor.fetchall()

            if not users:
                logger.info("  ⏭️  No users to migrate")
                return

            # Insert into PostgreSQL
            async with self.postgres_pool.acquire() as conn:
                inserted = 0
                for user in users:
                    try:
                        await conn.execute(
                            """
                            INSERT INTO users (phone_number_hash, daily_query_count, quota_reset_at, created_at)
                            VALUES ($1, $2, $3, $4)
                            ON CONFLICT (phone_number_hash) DO NOTHING
                            """,
                            user[0], user[1], user[2], user[3]
                        )
                        inserted += 1
                    except Exception as e:
                        logger.warning(f"  ⚠️  Skip duplicate user: {user[0][:8]}...")

            logger.info(f"  ✅ Migrated {inserted}/{len(users)} users")

        except Exception as e:
            logger.error(f"  ❌ Error migrating users: {e}")
            raise

    async def migrate_doctor_reviews(self):
        """Migrate doctor_reviews table"""
        logger.info("\n📋 Migrating doctor_reviews...")

        try:
            # Fetch from SQLite
            async with self.sqlite_conn.execute(
                """
                SELECT doctor_id, doctor_name, source, url, snippet, sentiment,
                       rating, hash, fetched_at, valid_until, display_policy
                FROM doctor_reviews
                """
            ) as cursor:
                reviews = await cursor.fetchall()

            if not reviews:
                logger.info("  ⏭️  No reviews to migrate")
                return

            # Insert into PostgreSQL
            async with self.postgres_pool.acquire() as conn:
                inserted = 0
                for review in reviews:
                    try:
                        await conn.execute(
                            """
                            INSERT INTO doctor_reviews (
                                doctor_id, doctor_name, source, url, snippet, sentiment,
                                rating, hash, fetched_at, valid_until, display_policy
                            )
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                            ON CONFLICT (hash) DO NOTHING
                            """,
                            *review
                        )
                        inserted += 1
                    except Exception as e:
                        logger.warning(f"  ⚠️  Skip duplicate review: {review[7][:8]}...")

            logger.info(f"  ✅ Migrated {inserted}/{len(reviews)} reviews")

        except Exception as e:
            logger.error(f"  ❌ Error migrating reviews: {e}")
            raise

    async def migrate_search_logs(self):
        """Migrate search_logs table"""
        logger.info("\n📋 Migrating search_logs...")

        try:
            # Fetch from SQLite
            async with self.sqlite_conn.execute(
                """
                SELECT user_id, doctor_name, doctor_id, location, cache_hit,
                       response_time_ms, sources_used, results_count, api_calls_count,
                       estimated_cost_usd, error_message, created_at
                FROM search_logs
                """
            ) as cursor:
                logs = await cursor.fetchall()

            if not logs:
                logger.info("  ⏭️  No logs to migrate")
                return

            # Insert into PostgreSQL
            async with self.postgres_pool.acquire() as conn:
                inserted = 0
                for log in logs:
                    try:
                        await conn.execute(
                            """
                            INSERT INTO search_logs (
                                user_id, doctor_name, doctor_id, location, cache_hit,
                                response_time_ms, sources_used, results_count, api_calls_count,
                                estimated_cost_usd, error_message, created_at
                            )
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                            """,
                            *log
                        )
                        inserted += 1
                    except Exception as e:
                        logger.warning(f"  ⚠️  Skip log entry: {e}")

            logger.info(f"  ✅ Migrated {inserted}/{len(logs)} logs")

        except Exception as e:
            logger.error(f"  ❌ Error migrating logs: {e}")
            raise

    async def verify_migration(self):
        """Verify data integrity after migration"""
        logger.info("\n🔍 Verifying migration...")

        tables = ["users", "doctor_reviews", "search_logs"]
        all_matched = True

        for table in tables:
            sqlite_count, pg_count = await self._count_records(table)
            match = "✅" if sqlite_count == pg_count else "❌"
            logger.info(f"  {match} {table}: SQLite={sqlite_count}, PostgreSQL={pg_count}")

            if sqlite_count != pg_count:
                all_matched = False

        if all_matched:
            logger.info("\n🎉 Migration verification PASSED!")
        else:
            logger.warning("\n⚠️  Migration verification FAILED - counts don't match")

        return all_matched

    async def run_migration(self):
        """Run complete migration process"""
        logger.info("🚀 Starting database migration...\n")
        start_time = datetime.now()

        try:
            await self.connect()

            # Migrate tables
            await self.migrate_users()
            await self.migrate_doctor_reviews()
            await self.migrate_search_logs()

            # Verify
            verified = await self.verify_migration()

            # Summary
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"\n⏱️  Migration completed in {elapsed:.2f}s")

            if verified:
                logger.info("✅ All data migrated successfully!")
                logger.info("\n📝 Next steps:")
                logger.info("  1. Backup your SQLite database")
                logger.info("  2. Update DATABASE_URL in .env to PostgreSQL")
                logger.info("  3. Restart your application")
                logger.info("  4. Test thoroughly before deleting SQLite file")
            else:
                logger.warning("⚠️  Please review migration results carefully")

        except Exception as e:
            logger.error(f"\n❌ Migration failed: {e}")
            raise
        finally:
            await self.close()


async def main():
    """Main migration script"""
    # Configuration
    sqlite_path = "./doctor_review.db"
    postgres_url = os.getenv("DATABASE_URL_POSTGRES")

    # Validate inputs
    if not os.path.exists(sqlite_path):
        logger.error(f"❌ SQLite database not found: {sqlite_path}")
        return

    if not postgres_url or "postgresql" not in postgres_url:
        logger.error("❌ PostgreSQL URL not configured")
        logger.info("Set DATABASE_URL_POSTGRES in .env file:")
        logger.info("  DATABASE_URL_POSTGRES=postgresql://user:pass@host:5432/dbname")
        return

    # Confirm migration
    logger.info("⚠️  Database Migration: SQLite → PostgreSQL")
    logger.info(f"  Source: {sqlite_path}")
    logger.info(f"  Target: {postgres_url[:30]}...")
    logger.info("\n⚠️  Make sure you have:")
    logger.info("  1. Backed up your SQLite database")
    logger.info("  2. Initialized PostgreSQL schema (run scripts/init_db.py)")
    logger.info("  3. Tested PostgreSQL connection")

    # Run migration
    migrator = DatabaseMigrator(sqlite_path, postgres_url)
    await migrator.run_migration()


if __name__ == "__main__":
    asyncio.run(main())
