# core/utils.py
"""
Core utility functions for backlink analysis.

This module contains essential utility functions for the
backlink analysis application.
"""
import os
import re
from datetime import datetime
from urllib.parse import urlparse
import logging

# Import from core constants
try:
    from core.constants import DATE_FORMAT
except ImportError:
    # Default date format if import fails
    DATE_FORMAT = "%Y%m%d"


def sanitize_sheet_name(name):
    """
    Sanitize a name to be valid as an Excel sheet name.

    Args:
        name: The name to sanitize

    Returns:
        A sanitized name valid for Excel sheets
    """
    # Remove invalid characters
    sanitized = re.sub(r'[\\/*\[\]:?]', '_', str(name))

    # Excel sheet names are limited to 31 characters
    if len(sanitized) > 31:
        sanitized = sanitized[:31]

    return sanitized


def extract_domain_name(file_path):
    """
    Extract domain name from file path with enhanced error handling and logging.
    
    Args:
        file_path: Path to a file
        
    Returns:
        Extracted domain name or None if extraction fails
    """
    try:
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        # Get the filename without extension
        filename = os.path.basename(file_path)
        filename = os.path.splitext(filename)[0]
        logger.info(f"Processing filename: {filename}")
        
        # Common patterns for domain extraction
        patterns = [
            r'backlinks-(.*?)-',      # backlinks-domain-
            r'backlink-(.*?)-',       # backlink-domain-
            r'-(.*?)-backlinks',      # -domain-backlinks
            r'-(.*?)-backlink',       # -domain-backlink
            r'^(.*?)-backlinks',      # domain-backlinks
            r'^(.*?)-backlink',       # domain-backlink
            r'backlinks_(.*?)_',      # backlinks_domain_
            r'backlink_(.*?)_',       # backlink_domain_
            r'_(.*?)_backlinks',      # _domain_backlinks
            r'_(.*?)_backlink',       # _domain_backlink
            r'^(.*?)_backlinks',      # domain_backlinks
            r'^(.*?)_backlink'        # domain_backlink
        ]
        
        # Try each pattern
        for pattern in patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                domain = match.group(1)
                # Clean up the domain
                domain = domain.strip('-_').lower()
                logger.info(f"Successfully extracted domain using pattern '{pattern}': {domain}")
                return domain
        
        # Fallback 1: Try to extract domain from URL-like patterns
        url_patterns = [
            r'https?://([^/]+)',      # http://domain.com
            r'www\.([^/]+)',          # www.domain.com
            r'([a-zA-Z0-9-]+\.[a-zA-Z]{2,})'  # domain.com
        ]
        
        for pattern in url_patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                domain = match.group(1)
                domain = domain.strip('-_').lower()
                logger.info(f"Successfully extracted domain using URL pattern: {domain}")
                return domain
        
        # Fallback 2: Use the first part of the filename
        domain = filename.split('_')[0].split('-')[0].strip().lower()
        logger.info(f"Using filename as domain (fallback): {domain}")
        return domain
        
    except Exception as e:
        logger.error(f"Error extracting domain from {file_path}: {str(e)}")
        logger.error("Traceback:", exc_info=True)
        return None


def extract_domain_from_url(url):
    """
    Extract domain name from a URL.

    Args:
        url: URL to extract domain from

    Returns:
        Domain name (without www)
    """
    if not url or not isinstance(url, str):
        return ""

    try:
        # Parse the URL
        parsed_url = urlparse(url)

        # Get the network location (hostname)
        domain = parsed_url.netloc

        # Remove www prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]

        return domain
    except:
        # If there's an error parsing, return empty string
        return ""


def get_output_filename(base_directory):
    """
    Generate a standardized output filename with the current date.

    Args:
        base_directory: Directory where the file should be saved

    Returns:
        Full path to the output file
    """
    # Create the filename with current date
    current_date = datetime.now().strftime(DATE_FORMAT)
    filename = f"Backlink_Analysis_{current_date}.xlsx"

    # If base_directory is empty, use current directory
    if not base_directory:
        base_directory = os.getcwd()

    # Ensure the base directory exists
    if not os.path.exists(base_directory):
        os.makedirs(base_directory)

    return os.path.join(base_directory, filename)


def standardize_semrush_columns(df):
    """Standardize column names to ensure consistency"""
    if df is None or df.empty:
        return df
        
    # Create a mapping of possible column names to our standard names
    column_map = {
        'Source URL': 'Source url',
        'Source Url': 'Source url',
        'Source': 'Source url',
        'Page AS': 'Page ascore',
        'Page Authority Score': 'Page ascore',
        'Authority Score': 'Page ascore',
        'AS': 'Page ascore',
        'Target': 'Target url',
        'Target Url': 'Target url',
        'Target URL': 'Target url',
        'Title': 'Source title',
        'Source Title': 'Source title',
        'FirstSeen': 'First seen',
        'First Seen': 'First seen',
        'LastSeen': 'Last seen',
        'Last Seen': 'Last seen',
        'ExtBacklinks': 'External links',
        'External Links': 'External links',
        'External backlinks': 'External links',
        'NoFollow': 'Nofollow',
        'No Follow': 'Nofollow',
        'SiteWide': 'Sitewide',
        'Site Wide': 'Sitewide',
        'Lost Link': 'Lost link',
        'LostLink': 'Lost link'
    }
    
    # Rename columns that match our mapping
    df = df.rename(columns=column_map)
    return df


def analyze_last_seen_dates(df):
    """Analyze the last seen dates of backlinks"""
    import pandas as pd
    from datetime import datetime, timedelta
    
    if 'Last seen' not in df.columns:
        return {}
        
    try:
        # Convert Last seen to datetime
        df['Last seen'] = pd.to_datetime(df['Last seen'])
        
        # Get current time
        now = datetime.now()
        
        # Define time periods
        time_periods = {
            'Last 24 hours': timedelta(days=1),
            'Last 7 days': timedelta(days=7),
            'Last 30 days': timedelta(days=30),
            'Last 90 days': timedelta(days=90),
            'Over 90 days': timedelta(days=float('inf'))
        }
        
        # Count links in each time period
        results = {}
        for period_name, period_delta in time_periods.items():
            if period_name == 'Over 90 days':
                count = len(df[df['Last seen'] < (now - timedelta(days=90))])
            else:
                count = len(df[df['Last seen'] > (now - period_delta)])
            results[period_name] = count
            
        return results
    except Exception as e:
        print(f"Error analyzing last seen dates: {e}")
        return {}