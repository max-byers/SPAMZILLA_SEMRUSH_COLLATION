import os

# Base directory for Spamzilla exports
SPAM_EXPORTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'SPAM_EXPORTS')

# Configuration for input file
class SpamzillaConfig:
    # Default input file name (can be overridden)
    INPUT_FILE = 'Check_domains_results.2026-01-04 04_22.csv'

    @classmethod
    def get_input_file_path(cls):
        """
        Get the full path to the input file.
        
        Returns:
            str: Full path to the input file
        """
        return os.path.join(SPAM_EXPORTS_DIR, cls.INPUT_FILE)

    @classmethod
    def list_available_files(cls):
        """
        List all available CSV files in the SPAM_EXPORTS directory.
        
        Returns:
            list: List of CSV filenames
        """
        try:
            return [f for f in os.listdir(SPAM_EXPORTS_DIR) if f.endswith('.csv')]
        except Exception as e:
            print(f"Error listing files: {e}")
            return []

    @classmethod
    def set_input_file(cls, filename):
        """
        Set the input file name.
        
        Args:
            filename (str): Name of the CSV file to use
        """
        # Ensure .csv extension
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        # Validate the file exists
        file_path = os.path.join(SPAM_EXPORTS_DIR, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        cls.INPUT_FILE = filename
        print(f"Input file set to: {filename}") 