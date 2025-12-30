import os
import shutil
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_date_folders():
    """Create today's date folders for both types of backlink files."""
    today = datetime.now().strftime("%d_%m")
    
    # Create folders for both types of files
    backlinks_folder = f"{today}_SEMRUSH_backlinks"
    outgoing_domains_folder = f"{today}_SEMRUSH_outbounds"
    
    for folder in [backlinks_folder, outgoing_domains_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            logger.info(f"Created directory: {folder}")
    
    return backlinks_folder, outgoing_domains_folder

def is_file_from_today(file_path):
    """Check if a file was created today."""
    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
    return file_time.date() == datetime.now().date()

def organize_downloaded_files():
    """Main function to organize downloaded files."""
    # Source directory
    downloads_dir = r"C:\Users\Max Byers\Downloads"
    
    # Create today's folders
    backlinks_folder, outgoing_domains_folder = create_date_folders()
    
    # Track processed files
    processed_files = []
    skipped_files = []
    
    # Process each file in Downloads
    for filename in os.listdir(downloads_dir):
        if not filename.endswith('.csv'):
            continue
            
        file_path = os.path.join(downloads_dir, filename)
        
        # Skip if not created today
        if not is_file_from_today(file_path):
            continue
        
        # Determine target folder based on filename
        if filename.endswith('-backlinks.csv'):
            target_folder = backlinks_folder
        elif filename.endswith('-backlinks_outgoing_domains.csv'):
            target_folder = outgoing_domains_folder
        else:
            skipped_files.append(filename)
            continue
        
        # Move the file
        try:
            target_path = os.path.join(target_folder, filename)
            shutil.move(file_path, target_path)
            processed_files.append(filename)
            logger.info(f"Moved {filename} to {target_folder}")
        except Exception as e:
            logger.error(f"Error moving {filename}: {str(e)}")
    
    # Print summary
    logger.info("\nSummary:")
    logger.info(f"Processed {len(processed_files)} files:")
    for file in processed_files:
        logger.info(f"- {file}")
    
    if skipped_files:
        logger.info(f"\nSkipped {len(skipped_files)} files (not matching patterns):")
        for file in skipped_files:
            logger.info(f"- {file}")

if __name__ == "__main__":
    logger.info("Starting file organization process...")
    organize_downloaded_files()
    logger.info("File organization complete!") 