import os
import glob

# Configuration for domain export file
class Config:
    # Default path to Spamzilla domain exports directory
    DEFAULT_EXPORTS_DIR = r"C:\Users\Max Byers\OneDrive\Documents\SPAMZILLA_SEMRUSH_COLLATION\SPAMZILLA_DOMAIN_EXPORTS"
    
    # Filename slug to use (just the unique part of the filename)
    # Example: 'export-133821_2025-07-16-06-07-03'
    EXPORT_FILE_SLUG = 'export-133821_2025-12-02-22-17-10.csv'
    
    @classmethod
    def get_export_file(cls):
        """
        Get the export file path.
        
        Returns:
        - str: Full path to the export file
        """
        # If a specific file slug is set, try to find the matching file
        if cls.EXPORT_FILE_SLUG:
            # Search for files matching the slug
            matching_files = glob.glob(os.path.join(cls.DEFAULT_EXPORTS_DIR, f'{cls.EXPORT_FILE_SLUG}*.csv'))
            
            if matching_files:
                # If multiple matches, take the first one
                export_file = matching_files[0]
                print(f"Using file: {export_file}")
                return export_file
        
        # If no specific file or no match found, find the most recent file
        export_files = glob.glob(os.path.join(cls.DEFAULT_EXPORTS_DIR, 'export-*_*.csv'))
        
        if not export_files:
            raise FileNotFoundError("No export files found in the specified directory")
        
        # Return the most recently created file
        return max(export_files, key=os.path.getctime) 