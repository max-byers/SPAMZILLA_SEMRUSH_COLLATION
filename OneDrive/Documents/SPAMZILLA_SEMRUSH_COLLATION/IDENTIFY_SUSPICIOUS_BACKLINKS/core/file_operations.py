# core/file_operations.py
"""
Core file operations for reading and processing backlink files.
"""
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def read_backlink_file(file_path):
    """
    Read a backlink file (CSV or Excel) and perform initial processing.

    Args:
        file_path: Path to the file

    Returns:
        Processed DataFrame or None if file couldn't be read
    """
    try:
        # Read the file based on extension
        if file_path.lower().endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        logger.info(f"Loaded data with {len(df)} rows from {file_path}")

        # Remove any translation-related columns
        from utils import remove_translation_references
        df = remove_translation_references(df)

        return df
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        logger.error("Traceback:", exc_info=True)
        return None 