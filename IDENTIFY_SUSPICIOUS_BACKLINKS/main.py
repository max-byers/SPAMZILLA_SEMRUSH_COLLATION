# main.py
import sys
import os
import logging
import traceback
from datetime import datetime

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import glob
from core.utils import extract_domain_name, get_output_filename
from core.file_operations import read_backlink_file

# Import from new module structure with corrected import paths
try:
    # Use the package-level imports instead of trying to import from specific modules
    from excel_utils import create_workbook, add_summary_to_sheet
    from content_analysis import add_content_analysis_sheet, analyze_content  # Updated import
except ImportError as e:
    logger.error(f"Error importing required modules: {e}")
    # If the package-level imports fail, we'll define simple stub functions
    def create_workbook():
        from openpyxl import Workbook
        return Workbook()

    def add_summary_to_sheet(*args, **kwargs):
        logger.warning("Using fallback add_summary_to_sheet function")
        return None

    def add_content_analysis_sheet(*args, **kwargs):
        logger.warning("Using fallback add_content_analysis_sheet function")
        return None, {}, {}

from file_processor import process_backlink_file, get_domain_everything_df

# Import configuration
try:
    from config import FEATURES
except ImportError:
    logger.warning("Config file not found, using default features")
    # Default features if config not available
    FEATURES = {
        'SORT_DOMAINS_BY_SIZE': True,
        'GROUP_SIMILAR_BACKLINKS': True,
        'ADD_HYPERLINKS': True,
        'USE_DOMAIN_SPACING': True,
        'ENABLE_CONTENT_ANALYSIS': True,
        'VALIDATE_REQUIRED_COLUMNS': True,
        'ENABLE_LOGGING': True
    }


def count_domain_backlinks(file_path):
    """Count the number of backlinks per domain in a file"""
    try:
        logger.info(f"Counting backlinks for file: {file_path}")
        # Read the file
        df = read_backlink_file(file_path)
        if df is None:
            logger.warning(f"No data found in file: {file_path}")
            return {}

        # Standardize column names
        from utils import standardize_semrush_columns
        df = standardize_semrush_columns(df)

        # Extract domain from source URL
        from core.utils import extract_domain_from_url
        domain_col = 'Source url'
        if domain_col in df.columns:
            domains = df[domain_col].apply(extract_domain_from_url)
            domain_counts = domains.value_counts().to_dict()
            logger.info(f"Found {len(domain_counts)} unique domains in {file_path}")
            return domain_counts
        logger.warning(f"Source URL column not found in {file_path}")
        return {}
    except Exception as e:
        logger.error(f"Error counting domain backlinks in {file_path}: {e}")
        logger.error("Traceback:", exc_info=True)
        return {}


def validate_path(path):
    """Validate that the path exists and is either a file or directory"""
    if not os.path.exists(path):
        logger.error(f"Path does not exist: {path}")
        return False
        
    if not (os.path.isfile(path) or os.path.isdir(path)):
        logger.error(f"Path is neither a file nor a directory: {path}")
        return False
        
    return True


def process_files(input_path, output_path=None):
    """
    Process Semrush Excel and CSV files, either from a directory or a single file.
    """
    logger.info("Starting Semrush backlink analysis...")

    # Validate input path
    if not validate_path(input_path):
        logger.error(f"Invalid input path: {input_path}")
        return None

    # If no output file path is provided, generate one based on date
    if output_path is None:
        output_path = get_output_filename(os.path.dirname(input_path))
        logger.info(f"Generated output path: {output_path}")

    try:
        # Create a new workbook for the collated data
        workbook = create_workbook()
        logger.info("Created new workbook")

        # Store domain data for content analysis
        domain_data_dict = {}

        # Get files to process
        if os.path.isdir(input_path):
            # Process all files in directory
            all_files = []
            for ext in ['*.xlsx', '*.xls', '*.csv']:
                file_glob = os.path.join(input_path, ext)
                logger.info(f"Searching for files matching pattern: {file_glob}")
                found_files = glob.glob(file_glob)
                logger.info(f"Found {len(found_files)} files matching {ext}")
                all_files.extend(found_files)
        else:
            # Process single file
            all_files = [input_path]

        if not all_files:
            logger.error(f"No Excel or CSV files found in {input_path}")
            return None

        logger.info(f"Found {len(all_files)} files to process")
        logger.info(f"Files to process: {all_files}")

        # Track processed and failed files
        processed_files = []
        failed_files = []

        # Process each file
        for file_path in all_files:
            try:
                # Extract domain name from file path
                domain = extract_domain_from_file_path(file_path)
                if not domain:
                    logger.warning(f"Could not extract domain from {file_path}")
                    failed_files.append((file_path, "Could not extract domain"))
                    continue

                logger.info(f"Processing file {file_path} for domain {domain}")
                # Process the file
                success, _, _ = process_backlink_file(workbook, file_path, domain, None)
                if success:
                    logger.info(f"Successfully processed {file_path}")
                    processed_files.append(file_path)
                else:
                    logger.error(f"Failed to process {file_path}")
                    failed_files.append((file_path, "Processing failed"))

            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}")
                logger.error("Traceback: %s", traceback.format_exc())
                failed_files.append((file_path, str(e)))
                continue

        # Log summary
        logger.info(f"Successfully processed {len(processed_files)} files")
        if failed_files:
            logger.warning(f"Failed to process {len(failed_files)} files:")
            for file_path, error in failed_files:
                logger.warning(f"  - {file_path}: {error}")

        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Created output directory: {output_dir}")

        # Save the workbook
        workbook.save(output_path)
        logger.info(f"Saved workbook to {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error in process_files: {str(e)}")
        logger.error("Traceback: %s", traceback.format_exc())
        return None


def extract_domain_from_file_path(file_path):
    """Extract domain name from a file path"""
    import os
    # Get the filename without extension
    filename = os.path.basename(file_path)
    # Remove the -backlinks part and any numbers in parentheses
    domain = filename.split('-backlinks')[0].split(' (')[0]
    return domain


def get_output_filename(base_dir):
    """Generate an output filename based on the current date"""
    timestamp = datetime.now().strftime("%Y%m%d")
    # Use the IDENTIFY_SUSPICIOUS_BACKLINKS directory for output
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SUSPICIOUS_BACKLINKS_OUTPUT")
    return os.path.join(output_dir, f"Backlink_Analysis_{timestamp}.xlsx")


def find_latest_semrush_folder():
    """Find the configured SEMRUSH folder in the workspace"""
    try:
        # Import configuration
        from config import SEMRUSH_FOLDER_NAME, BASE_DIRECTORIES
        
        # Get parent directory path
        parent_dir = BASE_DIRECTORIES['PROJECT_ROOT']
        
        # Build full path to the configured folder
        full_path = os.path.join(parent_dir, SEMRUSH_FOLDER_NAME)
        
        print(f"Parent Directory: {parent_dir}")
        logger.info(f"Parent Directory: {parent_dir}")
        print(f"Checking folder: {full_path}")
        logger.info(f"Checking configured SEMRUSH folder: {full_path}")
        
        # Check if the folder exists
        if not os.path.isdir(full_path):
            logger.error(f"Configured SEMRUSH folder does not exist: {full_path}")
            print(f"ERROR: Folder does not exist: {full_path}")
            return None
        
        # Additional check for date-specific subfolders
        date_dirs = [d for d in os.listdir(full_path) 
                     if os.path.isdir(os.path.join(full_path, d)) 
                     and d.endswith('_SEMRUSH_backlinks')]
        
        if date_dirs:
            # Sort by modification time (most recent first)
            date_dirs.sort(key=lambda x: os.path.getmtime(os.path.join(full_path, x)), reverse=True)
            latest_dir = os.path.join(full_path, date_dirs[0])
            print(f"Selected folder: {latest_dir}")
            logger.info(f"Using configured SEMRUSH folder: {latest_dir}")
            return latest_dir
        
        # If no date-specific subfolders, use the folder itself
        print(f"Selected folder: {full_path}")
        logger.info(f"Using configured SEMRUSH folder: {full_path}")
        return full_path
        
    except ImportError:
        logger.error("Could not import configuration file")
        return None
    except Exception as e:
        logger.error(f"Error finding SEMRUSH folder: {e}")
        return None


if __name__ == "__main__":
    # Use the configured SEMRUSH backlinks folder
    input_path = find_latest_semrush_folder()
    if input_path:
        output_path = process_files(input_path)
        if output_path:
            print(f"Analysis complete. Output saved to: {output_path}")
        else:
            print("Analysis failed. Check the logs for details.")
    else:
        print("Could not find a suitable input folder for analysis.")