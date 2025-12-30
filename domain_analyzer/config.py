import os

# Base directory is one level up from the current directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Manually specify the FULL filename for Spamzilla export
# Example: SPAMZILLA_FILE = "export-133821_2025-05-11-06-40-03_cleaned.csv"
SPAMZILLA_FILE = "export-133821_2025-12-02-22-17-10.csv"

# Manually specify the SEMRUSH comparison folder name
# This will always be in the root directory
# Example: SEMRUSH_COMPARISON_FOLDER = "25_06_SEMRUSH_comparison"
SEMRUSH_COMPARISON_FOLDER = "03_12_SEMRUSH_comparison"

# Full paths will be constructed based on the above variables
SPAMZILLA_FILE_PATH = os.path.join(BASE_DIR, "SPAMZILLA_DOMAIN_EXPORTS", SPAMZILLA_FILE) if SPAMZILLA_FILE else None
SEMRUSH_COMPARISON_PATH = os.path.join(BASE_DIR, SEMRUSH_COMPARISON_FOLDER) if SEMRUSH_COMPARISON_FOLDER else None 