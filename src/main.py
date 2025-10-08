"""
Main FastAPI application entry point
Doctor Review Aggregation WhatsApp Bot
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from src.config import settings

# Choose database based on environment
if settings.environment == "production":
    from src.database import db
else:
    from src.database_sqlite import db
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
        # Connect to database
        await db.connect()
        logger.info("✅ Database connected")

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("👋 Shutting down Doctor Review Bot...")
    await db.disconnect()
    logger.info("✅ Cleanup completed")


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
