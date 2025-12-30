import os
import sys
import logging

# Add the parent directory to Python path to import local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ANCHOR_TEXT.anchor_text_analysis import analyze_anchor_texts
from ANCHOR_TEXT.config import (
    BACKLINKS_DIR, 
    OUTPUT_DIR, 
    LOGGING_CONFIG, 
    MAX_ANCHOR_TEXTS
)

def setup_logging():
    """Configure logging based on config settings"""
    # Ensure UTF-8 encoding for logging
    logging.getLogger().handlers.clear()  # Clear any existing handlers
    
    # Create console handler with UTF-8 encoding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, LOGGING_CONFIG['level']))
    console_handler.setFormatter(logging.Formatter(LOGGING_CONFIG['format']))
    
    # Create file handler with UTF-8 encoding
    file_handler = logging.FileHandler(LOGGING_CONFIG['log_file'], encoding='utf-8')
    file_handler.setLevel(getattr(logging, LOGGING_CONFIG['level']))
    file_handler.setFormatter(logging.Formatter(LOGGING_CONFIG['format']))
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, LOGGING_CONFIG['level']),
        handlers=[console_handler, file_handler]
    )

def main():
    """Main entry point for anchor text analysis"""
    try:
        # Ensure output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Setup logging
        setup_logging()
        
        # Log start of analysis
        logging.info("Starting Anchor Text Analysis")
        logging.info(f"Backlinks Directory: {BACKLINKS_DIR}")
        logging.info(f"Output Directory: {OUTPUT_DIR}")
        
        # Run the analysis
        analyze_anchor_texts()
        
        logging.info("Anchor Text Analysis completed successfully")
    
    except Exception as e:
        logging.error(f"An error occurred during analysis: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 