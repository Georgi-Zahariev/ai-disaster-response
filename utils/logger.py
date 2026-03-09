"""
File: logger.py
Purpose: Configure application-wide logging with consistent format and levels
Inputs: LOG_LEVEL from configuration
Outputs: Configured logger instances
Dependencies: logging, config
Used By: All modules
"""

import logging
import sys
from config import Config


def setup_logger(name: str) -> logging.Logger:
    """
    Set up a logger with consistent formatting.
    
    Args:
        name: Logger name (typically __name__ of the calling module)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    # Avoid duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


# Default logger
logger = setup_logger(__name__)
