# core/constants.py
"""
Constants used throughout the backlink analysis tool.
"""
# Date format for file naming
DATE_FORMAT = "%Y%m%d"

# Color palette for domain rotation (6 colors)
DOMAIN_COLORS = [
    "0000FF",  # Blue
    "FF0000",  # Red
    "008000",  # Green
    "800080",  # Purple
    "FFA500",  # Orange
    "008080",  # Teal
]

# Default column order - updated to include Domain Backlinks column
DEFAULT_COLUMN_ORDER = [
    "Page ascore",
    "Domain Backlinks",
    "Referring Domain",
    "Source title",
    "Anchor",
    "Source url",
    # Additional columns will follow in their original order
]