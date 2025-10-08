"""
Enhanced logging configuration with structured logging
"""

import logging
import sys
from datetime import datetime
from typing import Optional
from src.config import settings


class ColoredFormatter(logging.Formatter):
    """Colored log formatter for console output"""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        # Add color to level name
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"

        return super().format(record)


class StructuredLogger:
    """Enhanced logger with structured logging support"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def _log_with_context(self, level: int, message: str, **context):
        """Log with additional context"""
        if context:
            context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
            message = f"{message} | {context_str}"
        self.logger.log(level, message)

    def debug(self, message: str, **context):
        self._log_with_context(logging.DEBUG, message, **context)

    def info(self, message: str, **context):
        self._log_with_context(logging.INFO, message, **context)

    def warning(self, message: str, **context):
        self._log_with_context(logging.WARNING, message, **context)

    def error(self, message: str, **context):
        self._log_with_context(logging.ERROR, message, **context)

    def critical(self, message: str, **context):
        self._log_with_context(logging.CRITICAL, message, **context)


def setup_logging():
    """Configure application-wide logging"""

    # Get log level from settings
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Set formatter
    if settings.environment == "development":
        # Colored output for development
        formatter = ColoredFormatter(
            '%(levelname)-8s | %(name)-20s | %(message)s'
        )
    else:
        # JSON-like format for production (easier for log aggregation)
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"🚀 Logging initialized | level={settings.log_level.upper()} | env={settings.environment}")


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance"""
    return StructuredLogger(name)
