# config.py
"""
Configuration settings for the backlink analysis application.

This module contains all the configuration settings for the application,
including quality settings and more.
"""

# Quality backlink filter settings
QUALITY_BACKLINK_SETTINGS = {
    'MIN_AUTHORITY_SCORE': 5,  # Minimum authority score for quality links
    'MAX_EXTERNAL_LINKS': 200,  # Maximum external links for quality links
    'REQUIRE_DOFOLLOW': True  # Require links to be dofollow
}

# Debug settings
DEBUG = {
    'VERBOSE_LOGGING': True  # Show detailed logs
}

# File paths
DEFAULT_OUTPUT_DIRECTORY = 'BACKLINK_CSV_FILES'
EVERYTHING_QUALITY_DIR = 'EVERYTHING_QUALITY'
SUMMARY_DIR = 'SUMMARY'

# SEMRUSH backlink folder (edit this to the folder you want to analyze)
SEMRUSH_BACKLINK_FOLDER = '11_11_SEMRUSH_backlinks'