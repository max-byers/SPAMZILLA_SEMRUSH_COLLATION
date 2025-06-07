# excel_utils/__init__.py
"""
Excel utility package for backlink analysis.

This package provides a set of utilities for creating, formatting, and
manipulating Excel workbooks for backlink analysis.
"""

# Import key functions from modules to expose at package level
try:
    # Direct imports from modules with corrected file names
    from excel_utils.core import create_workbook, create_table, auto_adjust_cells
    from excel_utils.formatting import add_title_only, add_black_divider_column
    from excel_utils.navigating import add_navigation_links, add_navigation_between_dodgy_sheets
    from excel_utils.dataframe import add_df_to_worksheet, highlight_suspicious_content, \
        add_external_links_to_dodgy_sheet
    from excel_utils.summary import add_summary_to_sheet, add_suspicious_content_summary
except ImportError as e:
    print(f"Error importing from excel_utils modules: {e}")

    # No need for fallback imports if we've fixed the structure
    # Define stub functions to prevent crashes, but they'll raise errors if called
    def raise_import_error(func_name):
        def stub_func(*args, **kwargs):
            raise ImportError(f"Could not import {func_name}. Check module structure.")
        return stub_func

    create_workbook = raise_import_error("create_workbook")
    create_table = raise_import_error("create_table")
    auto_adjust_cells = raise_import_error("auto_adjust_cells")
    add_title_only = raise_import_error("add_title_only")
    add_black_divider_column = raise_import_error("add_black_divider_column")
    add_navigation_links = raise_import_error("add_navigation_links")
    add_navigation_between_dodgy_sheets = raise_import_error("add_navigation_between_dodgy_sheets")
    add_df_to_worksheet = raise_import_error("add_df_to_worksheet")
    highlight_suspicious_content = raise_import_error("highlight_suspicious_content")
    add_external_links_to_dodgy_sheet = raise_import_error("add_external_links_to_dodgy_sheet")
    add_summary_to_sheet = raise_import_error("add_summary_to_sheet")
    add_suspicious_content_summary = raise_import_error("add_suspicious_content_summary")

# Export these functions at the package level
__all__ = [
    # Core functions
    'create_workbook',
    'create_table',
    'auto_adjust_cells',

    # Formatting functions
    'add_title_only',
    'add_black_divider_column',

    # Navigation functions
    'add_navigation_links',
    'add_navigation_between_dodgy_sheets',

    # DataFrame functions
    'add_df_to_worksheet',
    'highlight_suspicious_content',
    'add_external_links_to_dodgy_sheet',

    # Summary functions
    'add_summary_to_sheet',
    'add_suspicious_content_summary'
]