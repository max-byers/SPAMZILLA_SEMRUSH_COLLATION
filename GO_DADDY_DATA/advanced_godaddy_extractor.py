import os
import shutil
from datetime import datetime
from pathlib import Path

class AdvancedGoDaddyExtractor:
    def __init__(self):
        # Get the Downloads folder path
        self.downloads_path = Path.home() / "Downloads"
        self.output_folder = Path("GO_DADDY_DATA") / "output"
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        # Current date for file naming
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        
    def find_domain_files(self):
        """Find domain files in Downloads folder with specific naming patterns from last 24 hours"""
        domain_files = []
        
        # Calculate the cutoff time (24 hours ago)
        from datetime import timedelta
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        # Look for all files
        all_files = list(self.downloads_path.glob("*"))
        
        # Filter for files with the specific naming patterns and created in last 24 hours
        for file in all_files:
            if file.is_file():  # Only process files, not directories
                filename = file.name
                # Check if filename matches the pattern: godaddy_did_win.csv or godaddy_did_not_win.csv
                if (filename == 'godaddy_did_win.csv' or 
                    filename == 'godaddy_did_not_win.csv'):
                    # Check if file was created or modified in the last 24 hours
                    file_stat = file.stat()
                    file_modified_time = datetime.fromtimestamp(file_stat.st_mtime)
                    file_created_time = datetime.fromtimestamp(file_stat.st_ctime)
                    
                    # Use the more recent of creation or modification time
                    file_time = max(file_created_time, file_modified_time)
                    
                    if file_time >= cutoff_time:
                        domain_files.append(file)
                        print(f"Found recent file: {filename} (modified: {file_time.strftime('%Y-%m-%d %H:%M:%S')})")
                    else:
                        print(f"Skipping old file: {filename} (modified: {file_time.strftime('%Y-%m-%d %H:%M:%S')})")
        
        return domain_files
    
    def copy_files_to_output(self, domain_files):
        """Copy the found files to the output folder with date prefix"""
        copied_files = []
        
        for file_path in domain_files:
            # Create new filename with date prefix
            if file_path.name == 'godaddy_did_win.csv':
                new_filename = f"{self.current_date}_godaddy_did_win.csv"
            elif file_path.name == 'godaddy_did_not_win.csv':
                new_filename = f"{self.current_date}_godaddy_did_not_win.csv"
            else:
                continue
            
            output_file = self.output_folder / new_filename
            
            # Copy the file
            shutil.copy2(file_path, output_file)
            copied_files.append(output_file)
            print(f"Copied {file_path.name} to {output_file}")
        
        return copied_files
    
    def process_files(self):
        """Main method to process all domain files automatically"""
        print("=== GoDaddy Domain Extractor ===")
        print(f"Searching for domain files in: {self.downloads_path}")
        
        domain_files = self.find_domain_files()
        
        if not domain_files:
            print("No files found in Downloads folder.")
            return
        
        print(f"Found {len(domain_files)} files in Downloads:")
        for file in domain_files:
            print(f"  - {file.name}")
        
        # Copy files to output folder
        copied_files = self.copy_files_to_output(domain_files)
        
        print(f"\n=== Summary ===")
        print(f"Total files processed: {len(domain_files)}")
        print(f"Files copied to output: {len(copied_files)}")
        for file in copied_files:
            print(f"  - {file.name}")

def main():
    extractor = AdvancedGoDaddyExtractor()
    extractor.process_files()

if __name__ == "__main__":
    main() 