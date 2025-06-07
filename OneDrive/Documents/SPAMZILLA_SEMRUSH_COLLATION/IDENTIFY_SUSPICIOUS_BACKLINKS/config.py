# config.py
"""
Configuration settings for the backlink analysis application.

This module contains all the configuration settings for the application,
including feature flags, quality settings, and more.
"""

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

# File paths
DEFAULT_OUTPUT_DIRECTORY = 'output'  # Default directory for output files