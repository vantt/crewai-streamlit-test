# src/utils/error_handler.py
import logging
from typing import Optional, Callable
import streamlit as st
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TravelPlannerError(Exception):
    """Base exception class for Travel Planner application"""
    pass

def handle_error(error_message: str = "An error occurred", 
                log_error: bool = True) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(f"{error_message}: {str(e)}")
                st.error(f"{error_message}: {str(e)}")
                return None
        return wrapper
    return decorator

class ErrorHandler:
    @staticmethod
    def log_error(error: Exception, context: Optional[str] = None):
        """Log error with context"""
        error_message = f"{context}: {str(error)}" if context else str(error)
        logger.error(error_message)
        return error_message

    @staticmethod
    def handle_api_error(error: Exception) -> str:
        """Handle API-related errors"""
        error_message = "API Error: Please check your API key and try again."
        logger.error(f"{error_message} Details: {str(error)}")
        return error_message