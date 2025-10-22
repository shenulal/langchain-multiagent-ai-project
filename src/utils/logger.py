"""
Logging configuration for the application
"""

import os
import sys
from loguru import logger
from typing import Optional

def setup_logger(log_level: Optional[str] = None) -> logger:
    """
    Setup and configure the logger
    
    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    # Remove default handler
    logger.remove()
    
    # Get log level from environment or use provided level
    level = log_level or os.getenv("LOG_LEVEL", "INFO")
    
    # Add console handler with custom format
    logger.add(
        sys.stdout,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        colorize=True
    )
    
    # Add file handler for persistent logging
    logger.add(
        "logs/app.log",
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="10 MB",
        retention="7 days",
        compression="zip"
    )
    
    return logger
