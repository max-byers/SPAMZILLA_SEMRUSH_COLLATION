import os

# Configuration for Anchor Text Analysis

# Input and Output Directories
BACKLINKS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "13_06_SEMRUSH_backlinks")
OUTPUT_DIR = os.path.join("ANCHOR_TEXT")

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'DEBUG',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'log_file': os.path.join(OUTPUT_DIR, 'anchor_text_analysis.log')
}

# Analysis Parameters
MAX_ANCHOR_TEXTS = 10  # Maximum number of top anchor texts to report per domain

# Optional: Additional configuration options
NORMALIZATION_OPTIONS = {
    'remove_html_entities': True,
    'strip_punctuation': True,
    'lowercase': True
} 