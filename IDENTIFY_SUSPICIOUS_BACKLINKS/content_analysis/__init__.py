# content_analysis/__init__.py
"""
Content analysis package for backlink data.

This package provides tools for analyzing backlink content,
detecting suspicious keywords, and generating reports.
"""

# Import key functions from modules to expose at package level
try:
    from content_analysis.detection import find_keywords_in_text, analyze_content
    from content_analysis.reporting import add_content_analysis_sheet, add_dodgy_domain_sheet
    from content_analysis.utils import get_alpha_ordered_domains, categorize_suspicious_content
except ImportError as e:
    print(f"Error importing from content_analysis modules: {e}")


    # Define stub functions to prevent crashes
    def raise_import_error(func_name):
        def stub_func(*args, **kwargs):
            raise ImportError(f"Could not import {func_name}. Check module structure.")

        return stub_func


    find_keywords_in_text = raise_import_error("find_keywords_in_text")
    analyze_content = raise_import_error("analyze_content")
    add_content_analysis_sheet = raise_import_error("add_content_analysis_sheet")
    add_dodgy_domain_sheet = raise_import_error("add_dodgy_domain_sheet")
    get_alpha_ordered_domains = raise_import_error("get_alpha_ordered_domains")
    categorize_suspicious_content = raise_import_error("categorize_suspicious_content")

# Export these functions at the package level
__all__ = [
    # Detection functions
    'find_keywords_in_text',
    'analyze_content',

    # Reporting functions
    'add_content_analysis_sheet',
    'add_dodgy_domain_sheet',

    # Utility functions
    'get_alpha_ordered_domains',
    'categorize_suspicious_content'
]