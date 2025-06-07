# content_analysis/detection.py
"""
Functions for detecting suspicious content in backlink data.
"""
import re
import pandas as pd

# Import our keywords
try:
    from content_analysis.keywords import SUSPICIOUS_KEYWORDS
except ImportError:
    # Provide a fallback in case import fails
    SUSPICIOUS_KEYWORDS = {
        'Adult': [r'\bxxx\b', r'\bporn\b', r'\badult\b', r'\bsex\b'],
        'Gambling': [r'\bcasino\b', r'\bpoker\b', r'\bbet\b', r'\bbetting\b'],
        'Pharmaceuticals': [r'\bpharmacy\b', r'\bdrug\b', r'\bprescription\b'],
        'Crypto Scams': [r'\bcrypto\b', r'\bbitcoin\b'],
        'General Scams': [r'\bmake\s+money\s+fast\b', r'\bget\s+rich\s+quick\b']
    }


def find_keywords_in_text(text, suspicious_keywords=None):
    """
    Find suspicious keywords in a text using regex patterns.

    Args:
        text: String to search in
        suspicious_keywords: Dictionary of keyword categories and regex patterns

    Returns:
        List of tuples (keyword, category, match_position)
    """
    if not text or not isinstance(text, str):
        return []

    if suspicious_keywords is None:
        suspicious_keywords = SUSPICIOUS_KEYWORDS

    found_matches = []

    for category, patterns in suspicious_keywords.items():
        for pattern in patterns:
            # Use regex to find all matches
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Get the actual matched text from the source
                matched_word = text[match.start():match.end()]
                found_matches.append((matched_word, category, match.start()))

    # Sort by position in text
    found_matches.sort(key=lambda x: x[2])
    return found_matches


def analyze_content(df, suspicious_keywords=None, domain_name=None):
    """
    Analyze dataframe content for suspicious keywords.

    Args:
        df: DataFrame with backlink data
        suspicious_keywords: Dictionary of keyword categories and regex patterns
        domain_name: Name of the domain being analyzed

    Returns:
        DataFrame with flagged content
    """
    if suspicious_keywords is None:
        suspicious_keywords = SUSPICIOUS_KEYWORDS

    # Initialize results
    results = []

    # Check each column that might contain suspicious content
    columns_to_check = ['Anchor', 'Source title', 'Source url', 'Referring Domain']

    # Process each row
    for idx, row in df.iterrows():
        row_number = idx + 1  # +1 because df is 0-indexed but Excel rows start at 1
        referring_domain = row['Referring Domain'] if 'Referring Domain' in df.columns else "Unknown"
        source_url = row['Source url'] if 'Source url' in df.columns else ""
        anchor = row['Anchor'] if 'Anchor' in df.columns else ""
        source_title = row['Source title'] if 'Source title' in df.columns else ""
        external_links = row['External links'] if 'External links' in df.columns else None

        # Container for this row's flagged words
        found_keywords = []
        found_categories = set()
        found_locations = []

        # Check each column for suspicious content
        for column in columns_to_check:
            if column not in df.columns:
                continue

            text = str(row[column]) if pd.notna(row[column]) else ""

            if not text:
                continue

            # Find all keywords in this text
            matches = find_keywords_in_text(text, suspicious_keywords)
            for keyword, category, _ in matches:
                found_keywords.append(keyword)
                found_categories.add(category)
                found_locations.append(column)

        # If we found any suspicious keywords, add to results
        if found_keywords:
            results.append({
                'Domain': domain_name,
                'Referring Domain': referring_domain,
                'Flagged Word(s)': ', '.join(found_keywords),
                'Categories': ', '.join(found_categories),
                'Amount': len(found_keywords),
                'Row Number': row_number,
                'Source URL': source_url,
                'Anchor': anchor,
                'Title': source_title,
                'External Links': external_links,
                'Location': ', '.join(found_locations)
            })

    # Convert to DataFrame
    if results:
        results_df = pd.DataFrame(results)
        # Reorder columns as requested
        column_order = ['Domain', 'Flagged Word(s)', 'Categories', 'Amount',
                        'Source URL', 'Anchor', 'Title', 'Referring Domain',
                        'External Links', 'Location', 'Row Number']
        # Ensure all columns exist
        for col in column_order:
            if col not in results_df.columns:
                results_df[col] = ""
        return results_df[column_order]
    else:
        # Return empty DataFrame with the correct columns
        return pd.DataFrame(columns=['Domain', 'Flagged Word(s)', 'Categories', 'Amount',
                                     'Source URL', 'Anchor', 'Title', 'Referring Domain',
                                     'External Links', 'Location', 'Row Number'])


def get_suspicious_ratio(df, domain_name=None):
    """
    Calculate the ratio of suspicious content in a DataFrame.

    Args:
        df: DataFrame with backlink data
        domain_name: Name of the domain being analyzed

    Returns:
        Dictionary with suspicious metrics
    """
    # Get suspicious content
    suspicious_df = analyze_content(df, domain_name=domain_name)

    # Calculate metrics
    total_backlinks = len(df)
    suspicious_backlinks = len(suspicious_df)
    suspicious_domains = suspicious_df['Referring Domain'].nunique() if not suspicious_df.empty else 0
    total_domains = df['Referring Domain'].nunique() if 'Referring Domain' in df.columns else 0

    # Calculate ratios
    backlink_ratio = round(suspicious_backlinks / max(1, total_backlinks), 3)
    domain_ratio = round(suspicious_domains / max(1, total_domains), 3)

    return {
        'domain_name': domain_name,
        'total_backlinks': total_backlinks,
        'suspicious_backlinks': suspicious_backlinks,
        'total_domains': total_domains,
        'suspicious_domains': suspicious_domains,
        'backlink_ratio': backlink_ratio,
        'domain_ratio': domain_ratio
    }


def highlight_suspicious_words_in_text(text, keywords):
    """
    Mark specific suspicious keywords in text for better visibility.

    Args:
        text: The text to analyze
        keywords: List of suspicious keywords to highlight

    Returns:
        Text with keywords marked for highlighting
    """
    if not text or not keywords:
        return text

    result = text
    # Convert to lowercase for case-insensitive matching
    text_lower = text.lower()

    # Process each keyword and mark it
    for keyword in keywords:
        keyword_lower = keyword.lower()
        if keyword_lower in text_lower:
            # Find all occurrences of the keyword
            start_idx = 0
            while True:
                idx = text_lower.find(keyword_lower, start_idx)
                if idx == -1:
                    break

                # Extract the actual case-sensitive version of the keyword from original text
                actual_keyword = text[idx:idx + len(keyword)]

                # Mark it with special tags (can be later interpreted by Excel formatting)
                marked_keyword = f"<mark>{actual_keyword}</mark>"

                # Replace in the result
                result = result[:idx] + marked_keyword + result[idx + len(keyword):]

                # Update search start position and adjust for the inserted tags
                start_idx = idx + len(marked_keyword)

                # Also update lowercase text for future searches
                text_lower = text_lower[:idx] + " " * len(keyword) + text_lower[idx + len(keyword):]

    return result