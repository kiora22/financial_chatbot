import os
import logging
from logging.handlers import RotatingFileHandler

from config.settings import settings

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)


def setup_logging(name: str) -> logging.Logger:
    """Set up logging configuration."""
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.getLevelName(settings.log_level))
    
    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_formatter = logging.Formatter(
        "%(levelname)s - %(message)s"
    )
    
    # Create handlers
    file_handler = RotatingFileHandler(
        filename=f"logs/{name}.log",
        maxBytes=10485760,  # 10MB
        backupCount=5,
    )
    file_handler.setLevel(logging.getLevelName(settings.log_level))
    file_handler.setFormatter(file_formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.getLevelName(settings.log_level))
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger