# smart_quiz_api/utils/logger.py

import logging
import sys
from typing import Optional
from pathlib import Path

# Configure logging
def setup_logger(
    name: str = "smart_quiz",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """Setup a logger with console and optional file output."""
    
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(format_string)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(format_string)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

# Create default logger
logger = setup_logger()

# Quiz-specific logging functions
def log_quiz_generation(user_id: str, quiz_type: str, source_url: Optional[str] = None):
    """Log quiz generation events."""
    logger.info(f"🎯 Quiz Generation - User: {user_id}, Type: {quiz_type}, Source: {source_url or 'manual'}")

def log_quiz_completion(user_id: str, quiz_id: int, score: float, duration: Optional[float] = None):
    """Log quiz completion events."""
    duration_str = f", Duration: {duration:.2f}s" if duration else ""
    logger.info(f"✅ Quiz Completed - User: {user_id}, Quiz: {quiz_id}, Score: {score:.1f}%{duration_str}")

def log_user_activity(user_id: str, activity: str, details: Optional[dict[str, str]] = None):
    """Log user activity events."""
    details_str = f" - {details}" if details else ""
    logger.info(f"👤 User Activity - User: {user_id}, Activity: {activity}{details_str}")

def log_system_health(service: str, status: str, response_time: Optional[float] = None):
    """Log system health checks."""
    time_str = f" ({response_time:.2f}ms)" if response_time else ""
    logger.info(f"🏥 Health Check - Service: {service}, Status: {status}{time_str}")

def log_error(error: Exception, context: Optional[str] = None, user_id: Optional[str] = None):
    """Log errors with context."""
    context_str = f" [{context}]" if context else ""
    user_str = f" (User: {user_id})" if user_id else ""
    logger.error(f"❌ Error{context_str}{user_str}: {str(error)}", exc_info=True) 

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(name)s: %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger 