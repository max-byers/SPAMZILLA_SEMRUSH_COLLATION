"""
Utilities Module

This module provides utility functions for logging, error handling,
and common operations for the Spamzilla CSV Transformer.
"""

import os
import sys
import logging
from datetime import datetime

# Configure logging
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Set up logger
logger = logging.getLogger('spamzilla_transformer')
logger.setLevel(LOG_LEVEL)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
logger.addHandler(console_handler)


# Add file handler
def setup_file_logging(log_file='spamzilla_transformer.log'):
    """
    Set up logging to a file in addition to console.

    Args:
        log_file (str): Path to the log file
    """
    try:
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Set up file handler
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
        logger.addHandler(file_handler)

        logger.info(f"Logging to file: {log_file}")
    except Exception as e:
        logger.warning(f"Failed to set up file logging: {str(e)}")


# Logging functions
def log_info(message):
    """Log an info message"""
    logger.info(message)


def log_warning(message):
    """Log a warning message"""
    logger.warning(message)


def log_error(message):
    """Log an error message"""
    logger.error(message)


def log_debug(message):
    """Log a debug message"""
    logger.debug(message)


# File handling utilities
def get_file_info(file_path):
    """
    Get information about a file.

    Args:
        file_path (str): Path to the file

    Returns:
        dict: Dictionary with file information
    """
    if not os.path.exists(file_path):
        return {'exists': False, 'error': 'File not found'}

    try:
        stats = os.stat(file_path)
        return {
            'exists': True,
            'size': stats.st_size,
            'created': datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
            'modified': datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {'exists': True, 'error': str(e)}


def is_valid_file(file_path, min_size=1):
    """
    Check if a file exists and has minimum size.

    Args:
        file_path (str): Path to the file
        min_size (int): Minimum file size in bytes

    Returns:
        bool: True if valid, False otherwise
    """
    if not os.path.exists(file_path):
        return False

    if os.path.getsize(file_path) < min_size:
        return False

    return True


# Exception handling
def safe_execute(func, *args, **kwargs):
    """
    Safely execute a function and catch any exceptions.

    Args:
        func: Function to execute
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        tuple: (result, error) - result is None if an error occurred
    """
    try:
        result = func(*args, **kwargs)
        return result, None
    except Exception as e:
        log_error(f"Error executing {func.__name__}: {str(e)}")
        return None, e


# String utilities
def is_empty_or_whitespace(text):
    """
    Check if a string is None, empty, or contains only whitespace.

    Args:
        text: String to check

    Returns:
        bool: True if empty or whitespace, False otherwise
    """
    return text is None or (isinstance(text, str) and text.strip() == '') 