"""
SQLite database initialization script
"""

import asyncio
import aiosqlite
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings


async def init_database():
    """Initialize SQLite database with schema"""
    print("🔧 Initializing SQLite database...")

    db_path = settings.database_url.replace("sqlite:///", "")
    print(f"Database path: {db_path}")

    try:
        # Connect to database (will create file if not exists)
        conn = await aiosqlite.connect(db_path)
        print("✅ Connected to SQLite database")

        # Read and execute schema file
        schema_file = Path(__file__).parent.parent / "sql" / "01_schema_sqlite.sql"

        if not schema_file.exists():
            print(f"❌ Schema file not found: {schema_file}")
            return

        with open(schema_file, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        print("📝 Executing schema SQL...")
        await conn.executescript(schema_sql)
        await conn.commit()
        print("✅ Database schema created successfully")

        # Verify tables
        cursor = await conn.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table'
            ORDER BY name
        """)
        tables = await cursor.fetchall()

        print(f"\n📊 Created tables ({len(tables)}):")
        for table in tables:
            print(f"  - {table[0]}")

        await conn.close()
        print("\n✅ SQLite database initialization completed!")

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(init_database())
