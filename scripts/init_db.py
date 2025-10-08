"""
Database initialization script
Run this to set up the database schema
"""

import asyncio
import asyncpg
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings


async def init_database():
    """Initialize database with schema"""
    print("🔧 Initializing database...")
    print(f"Database URL: {settings.database_url.split('@')[1]}")  # Hide password

    try:
        # Connect to database
        conn = await asyncpg.connect(settings.database_url)
        print("✅ Connected to database")

        # Read and execute schema file
        schema_file = Path(__file__).parent.parent / "sql" / "01_schema.sql"

        if not schema_file.exists():
            print(f"❌ Schema file not found: {schema_file}")
            return

        with open(schema_file, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        print("📝 Executing schema SQL...")
        await conn.execute(schema_sql)
        print("✅ Database schema created successfully")

        # Verify tables
        tables = await conn.fetch("""
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)

        print(f"\n📊 Created tables ({len(tables)}):")
        for table in tables:
            print(f"  - {table['tablename']}")

        await conn.close()
        print("\n✅ Database initialization completed!")

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(init_database())
