"""
Main FastAPI application entry point
Doctor Review Aggregation WhatsApp Bot
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from src.config import settings
# Enhanced logging and error handling
from src.utils.logger import setup_logging, get_logger
from src.utils.error_handler import register_error_handlers

# Configure logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting Doctor Review Bot...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")

    try:
        # Always use PostgreSQL
        from src.database import db
        logger.info("📊 Using PostgreSQL database")

        # Connect to database
        await db.connect()
        logger.info("✅ Database connected")

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("👋 Shutting down Doctor Review Bot...")
    try:
        await db.disconnect()
        logger.info("✅ Cleanup completed")
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")


# Create FastAPI app
app = FastAPI(
    title="Doctor Review Aggregation Bot",
    description="WhatsApp bot for aggregating doctor reviews from multiple sources",
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan
)

# Register error handlers
register_error_handlers(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===========================================
# Health Check Endpoint
# ===========================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Doctor Review Aggregation Bot API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Always use PostgreSQL
        from src.database import db

        # Check database connection
        await db.fetchval("SELECT 1")

        return {
            "status": "healthy",
            "environment": settings.environment,
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }, 500


@app.get("/env-check")
async def env_check():
    """Environment variables check endpoint"""
    import os
    from src.search.google_places import google_places_client

    raw_env = os.getenv("GOOGLE_PLACES_API_KEY")

    return {
        "GOOGLE_PLACES_API_KEY_raw_env": raw_env,
        "GOOGLE_PLACES_API_KEY_settings": settings.google_places_api_key,
        "GOOGLE_PLACES_API_KEY_is_none": settings.google_places_api_key is None,
        "GOOGLE_PLACES_API_KEY_length": len(settings.google_places_api_key) if settings.google_places_api_key else 0,
        "places_client_enabled": google_places_client.enabled,
        "places_client_api_key": google_places_client.api_key[:10] + "..." if google_places_client.api_key else None,
        "GOOGLE_SEARCH_API_KEY": settings.google_search_api_key,
        "GOOGLE_SEARCH_ENGINE_ID": settings.google_search_engine_id,
        "OPENAI_API_KEY": settings.openai_api_key[:10] + "..." if settings.openai_api_key else None,
        "environment": settings.environment
    }


# ===========================================
# Import routers
# ===========================================

from src.whatsapp.routes import router as whatsapp_router

app.include_router(whatsapp_router, prefix="/webhook", tags=["WhatsApp"])


if __name__ == "__main__":
    import uvicorn
    import os

    # Handle Railway's PORT environment variable
    port = 8000
    if 'PORT' in os.environ:
        try:
            port = int(os.environ['PORT'])
        except ValueError:
            port = 8000
    else:
        port = settings.port

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
