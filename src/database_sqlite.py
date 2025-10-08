"""
SQLite database connection module (for local development)
"""

import aiosqlite
from typing import Optional
import logging
from src.config import settings

logger = logging.getLogger(__name__)


class DatabaseSQLite:
    """SQLite database manager"""

    def __init__(self):
        self.db: Optional[aiosqlite.Connection] = None
        self.db_path = settings.database_url.replace("sqlite:///", "")

    async def connect(self):
        """Create database connection"""
        try:
            self.db = await aiosqlite.connect(self.db_path)
            self.db.row_factory = aiosqlite.Row
            logger.info(f"✅ SQLite database connected: {self.db_path}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to SQLite: {e}")
            raise

    async def disconnect(self):
        """Close database connection"""
        if self.db:
            await self.db.close()
            logger.info("SQLite database connection closed")

    async def execute(self, query: str, *args):
        """Execute a query without returning results"""
        async with self.db.execute(query, args) as cursor:
            await self.db.commit()
            return cursor.rowcount

    async def fetch(self, query: str, *args):
        """Fetch multiple rows"""
        async with self.db.execute(query, args) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def fetchrow(self, query: str, *args):
        """Fetch a single row"""
        async with self.db.execute(query, args) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def fetchval(self, query: str, *args):
        """Fetch a single value"""
        async with self.db.execute(query, args) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None


# Global database instance
db = DatabaseSQLite()
