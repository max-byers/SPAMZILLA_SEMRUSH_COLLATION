# core/__init__.py
"""
Core functionality package for backlink analysis.

This package provides the core utilities and constants
used throughout the backlink analysis application.
"""

# Import key functions from modules to expose at package level
try:
    from core.utils import sanitize_sheet_name, extract_domain_name, extract_domain_from_url, get_output_filename
    from core.constants import DATE_FORMAT, DOMAIN_COLORS, DEFAULT_COLUMN_ORDER
except ImportError as e:
    print(f"Error importing from core modules: {e}")


    # Define stub functions to prevent crashes
    def raise_import_error(func_name):
        def stub_func(*args, **kwargs):
            raise ImportError(f"Could not import {func_name}. Check module structure.")

        return stub_func


    sanitize_sheet_name = raise_import_error("sanitize_sheet_name")
    extract_domain_name = raise_import_error("extract_domain_name")
    extract_domain_from_url = raise_import_error("extract_domain_from_url")
    get_output_filename = raise_import_error("get_output_filename")

    # Default constants
    DATE_FORMAT = "%Y%m%d"
    DOMAIN_COLORS = [
        "0000FF",  # Blue
        "FF0000",  # Red
        "008000",  # Green
        "800080",  # Purple
        "FFA500",  # Orange
        "008080",  # Teal
    ]
    DEFAULT_COLUMN_ORDER = [
        "Page ascore",
        "Domain Backlinks",
        "Referring Domain",
        "Source title",
        "Anchor",
        "Source url",
    ]

# Export these functions and constants at the package level
__all__ = [
    # Utility functions
    'sanitize_sheet_name',
    'extract_domain_name',
    'extract_domain_from_url',
    'get_output_filename',

    # Constants
    'DATE_FORMAT',
    'DOMAIN_COLORS',
    'DEFAULT_COLUMN_ORDER'
]