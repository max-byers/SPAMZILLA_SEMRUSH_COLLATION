# Configuration file for domain price analysis inputs
import os

# Base directory for all operations
BASE_DIR = r"C:/Users/Max Byers/OneDrive/Documents/SPAMZILLA_SEMRUSH_COLLATION"

# --- MANUAL INPUT SECTION ---
# Edit these variables to manually specify your source paths
# You can use either:
#   - Full absolute paths: r"C:/full/path/to/folder"
#   - Relative paths from BASE_DIR: "folder_name" or "folder/subfolder"

# SEMRUSH backlinks comparison directory
# Example: "14_09_SEMRUSH_comparison" or r"C:/full/path/to/SEMRUSH_comparison"
SEMRUSH_DIR_MANUAL = "14_09_SEMRUSH_comparison"

# Domains/backlink CSV files directory
# Example: "BACKLINK_CSV_FILES/14_09" or r"C:/full/path/to/domains"
DOMAINS_DIR_MANUAL = "BACKLINK_CSV_FILES/14_09"

# Spamzilla exports directory (preset folder - usually don't need to change)
# Example: "SPAMZILLA_DOMAIN_EXPORTS" or r"C:/full/path/to/spamzilla"
SPAMZILLA_DIR_MANUAL = "SPAMZILLA_DOMAIN_EXPORTS"

# Spamzilla export file (enter just the filename here)
# The file will be looked for in the SPAMZILLA_DIR_MANUAL folder above
# Example: "export-2024-09-14.csv"
# Note: If you need a full path, use absolute path: r"C:/full/path/to/export-2024-09-14.csv"
SPAMZILLA_FILE_MANUAL = "export-2024-09-14.csv"

# Summary file (specific file path)
# Example: "SUMMARY/06_06_summary.csv" or r"C:/full/path/to/summary.csv"
SUMMARY_FILE_MANUAL = "SUMMARY/06_06_summary.csv"

# --- END MANUAL INPUT SECTION ---

# Construct full paths from manual entries
def get_full_path(manual_path, base_dir):
    """Convert manual path to full path, handling both absolute and relative paths."""
    if os.path.isabs(manual_path):
        return manual_path
    return os.path.join(base_dir, manual_path)

# SEMRUSH directory
SEMRUSH_DIR = get_full_path(SEMRUSH_DIR_MANUAL, BASE_DIR)

# Domains directory
DOMAINS_DIR = get_full_path(DOMAINS_DIR_MANUAL, BASE_DIR)

# Spamzilla directory
SPAMZILLA_DIR = get_full_path(SPAMZILLA_DIR_MANUAL, BASE_DIR)

# Spamzilla file (combines preset directory with manual filename)
# If filename is absolute path, use it directly; otherwise combine with SPAMZILLA_DIR
if os.path.isabs(SPAMZILLA_FILE_MANUAL):
    SPAMZILLA_FILE = SPAMZILLA_FILE_MANUAL
else:
    SPAMZILLA_FILE = os.path.join(SPAMZILLA_DIR, SPAMZILLA_FILE_MANUAL)

# Summary file
if os.path.isabs(SUMMARY_FILE_MANUAL):
    SUMMARY_FILE = SUMMARY_FILE_MANUAL
else:
    SUMMARY_FILE = os.path.join(BASE_DIR, SUMMARY_FILE_MANUAL)

# Output directory for price analysis
OUTPUT_DIR = os.path.join(BASE_DIR, "output_domain_price_analysis")

# Required columns for final output
REQUIRED_COLUMNS = [
    'Name',
    'Quality domains',
    'Quality backlinks',
    'TF',
    'CF',
    'TF/CF',
    'DR',
    'UR',
    'DA',
    'AS',
    'A RD',
    'M RD',
    'S RD',
    'IP\'S',
    'Age',
    'A (BL/RD)',
    'A BL',
    'M BL',
    'S BL',
    'Everything domains',
    'Everything backlinks',
    'SZ',
    'Expiry',
    'Source'
]

# You can manually edit any of the above variables as needed. 