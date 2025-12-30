# content_analysis/utils.py
"""
Utility functions for content analysis.
"""
import re
from core.utils import sanitize_sheet_name


def get_alpha_ordered_domains(workbook):
    """
    Get a list of all domains in the workbook, ordered alphabetically.

    Args:
        workbook: The openpyxl workbook

    Returns:
        List of domain names in alphabetical order
    """
    # Extract domain names from sheet names
    domains = set()
    for sheet_name in workbook.sheetnames:
        # Try to extract domain from sheet name (assuming format like domain_Everything)
        parts = sheet_name.split('_')
        if len(parts) >= 2 and parts[1] in ['Everything', 'Quality', 'dodgy']:
            domains.add(parts[0])

    # Sort alphabetically (case-insensitive)
    return sorted(list(domains), key=str.lower)


def get_suspicious_sheet_name(domain_name):
    """
    Get the standardized sheet name for suspicious content for a domain.

    Args:
        domain_name: Domain name

    Returns:
        Sanitized sheet name
    """
    return sanitize_sheet_name(f"{domain_name}_dodgy")


def extract_flagged_words(text):
    """
    Extract individual flagged words from a comma-separated string.

    Args:
        text: Comma-separated string of flagged words

    Returns:
        List of individual words
    """
    if not text or not isinstance(text, str):
        return []

    # Split by comma and clean up
    words = [word.strip() for word in text.split(',')]
    return [word for word in words if word]


def categorize_suspicious_content(df):
    """
    Group suspicious content by category.

    Args:
        df: DataFrame with suspicious content

    Returns:
        Dictionary mapping categories to counts
    """
    if 'Categories' not in df.columns or df.empty:
        return {}

    # Extract all categories
    all_categories = []
    for categories in df['Categories']:
        if isinstance(categories, str):
            all_categories.extend([cat.strip() for cat in categories.split(',')])

    # Count occurrences
    category_counts = {}
    for category in all_categories:
        category_counts[category] = category_counts.get(category, 0) + 1

    return category_counts


def highlight_patterns_in_text(text, patterns, style='red+bold'):
    """
    Create a formatted representation of text with patterns highlighted.
    For terminal/text display, not Excel.

    Args:
        text: Original text
        patterns: List of regex patterns or strings to highlight
        style: Style to apply ('red+bold', 'underline', etc.)

    Returns:
        Formatted string with ANSI codes for display
    """
    if not text or not patterns:
        return text

    # ANSI codes for styling
    style_codes = {
        'red': '\033[31m',
        'bold': '\033[1m',
        'red+bold': '\033[31;1m',
        'underline': '\033[4m',
        'reset': '\033[0m'
    }

    start_code = style_codes.get(style, style_codes['red+bold'])
    end_code = style_codes['reset']

    # Make a copy of the text to modify
    result = text

    # For each pattern, find matches and replace with highlighted version
    for pattern in patterns:
        try:
            regex = re.compile(pattern, re.IGNORECASE)

            # Find all matches
            matches = list(regex.finditer(result))

            # Work backwards to avoid offset issues
            for match in reversed(matches):
                start, end = match.span()
                matched_text = result[start:end]

                # Replace with highlighted version
                result = result[:start] + start_code + matched_text + end_code + result[end:]
        except:
            # If regex fails, try simple string replacement
            if pattern.lower() in result.lower():
                result = result.replace(pattern, f"{start_code}{pattern}{end_code}")

    return result