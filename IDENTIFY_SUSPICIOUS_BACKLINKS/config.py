# config.py
"""
Configuration settings for the backlink analysis application.

This module contains all the configuration settings for the application,
including feature flags, input/output paths, and more.
"""

import os

# ============================================================================
# CHANGE THIS VARIABLE TO THE FOLDER NAME YOU WANT TO USE
# ============================================================================
# Update this folder name each time you want to process a different SEMRUSH folder
SEMRUSH_FOLDER_NAME = '11_11_SEMRUSH_backlinks'

# ============================================================================
# Base directory configuration
# ============================================================================
BASE_DIRECTORIES = {
    'PROJECT_ROOT': os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'BACKLINKS_ROOT': os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'BACKLINK_CSV_FILES'),
    'OUTPUT_ROOT': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'SUSPICIOUS_BACKLINKS_OUTPUT')
}

# ============================================================================
# Input paths for SEMRUSH backlink folders
# ============================================================================
INPUT_PATHS = {
    # Specific file patterns to look for
    'FILE_PATTERNS': {
        'BACKLINKS': '*-backlinks.csv',
        'COMPARISONS': '*-backlinks_comparison.csv',
        'OUTBOUND_DOMAINS': '*-backlinks_outgoing_domains.csv'
    },
    'DOMAINS_LIST_FILE': 'input_domains.txt'
}

# Feature flags to control application behavior
FEATURES = {
    # Core features
    'SORT_DOMAINS_BY_SIZE': True,  # Sort domains by backlink count
    'GROUP_SIMILAR_BACKLINKS': True,  # Group similar backlinks together
    'ADD_HYPERLINKS': True,  # Add hyperlinks to URLs
    'USE_DOMAIN_SPACING': True,  # Add visual spacing between domains
    'HIGHLIGHT_LOST_LINKS': True,  # Highlight lost links in sheets
    'ROTATING_DOMAIN_COLORS': True,  # Use rotating colors for domains

    # Data organization
    'REORDER_COLUMNS': True,  # Reorder columns in standard format
    'SORT_BY_DOMAIN_COUNT': True,  # Sort by domain backlink count

    # Other features - all translation features disabled
    'ENABLE_TRANSLATION': False,  # Translation capability disabled
    'TRANSLATE_TITLES': False,  # Don't translate titles
    'TRANSLATE_ANCHORS': False,  # Don't translate anchors
    'CACHE_TRANSLATIONS': False,  # Don't cache translations
}

# Quality backlink filter settings
QUALITY_BACKLINK_SETTINGS = {
    'MIN_AUTHORITY_SCORE': 5,  # Minimum authority score for quality links
    'MAX_EXTERNAL_LINKS': 200,  # Maximum external links for quality links
    'REQUIRE_DOFOLLOW': True  # Require links to be dofollow
}

# Spammy backlink filter settings
SPAMMY_BACKLINK_SETTINGS = {
    'MAX_AUTHORITY_SCORE': 5,  # Maximum authority score for spammy links
    'MIN_EXTERNAL_LINKS': 200  # Minimum external links for spammy links
}

# Debug settings
DEBUG = {
    'VERBOSE_LOGGING': True,  # Show detailed logs
    'PROFILE_PERFORMANCE': False  # Don't profile performance
}
