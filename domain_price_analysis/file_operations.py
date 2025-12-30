import pandas as pd
import os
import glob
from datetime import datetime
from csv_operations import create_main_sheet_csv, create_rejected_sheet_csv, create_spam_test_sheet_csv

print("Loading file_operations.py - Using most recent SEMRUSH directory")

def find_semrush_files(base_dir):
    """
    Find the SEMRUSH files in the specified directory.
    """
    print(f"Looking for SEMRUSH files in: {base_dir}")
    
    # Look for files with different patterns
    patterns = [
        "*-backlinks.csv",             # Standard pattern
        "*-backlinks_comparison.csv",  # Comparison pattern
        "*-backlinks - Copy.csv"       # Copy pattern (keeping for backward compatibility)
    ]
    
    all_files = []
    for pattern in patterns:
        print(f"Searching with pattern: {pattern}")
        files = glob.glob(os.path.join(base_dir, pattern))
        print(f"Found files: {files}")
        all_files.extend(files)
    
    if all_files:
        print(f"Found {len(all_files)} SEMRUSH files")
        return all_files
    
    print(f"No SEMRUSH files found in {base_dir}")
    return []


def find_spamzilla_file(base_dir, specific_filename=None):
    """
    Find the Spamzilla export file in the given directory.

    Args:
        base_dir (str): Base directory to search in
        specific_filename (str, optional): Specific filename to look for

    Returns:
        str: Path to the Spamzilla file, or None if not found
    """
    if specific_filename:
        # Look for the specific file
        filepath = os.path.join(base_dir, specific_filename)
        if os.path.exists(filepath):
            print(f"Found specified Spamzilla file: {filepath}")
            return filepath

        print(f"Warning: Specified file '{specific_filename}' not found.")

    # Try to find any Spamzilla export files
    export_files = glob.glob(os.path.join(base_dir, "export-*.csv"))

    if export_files:
        # Sort by modification time (newest first)
        export_files.sort(key=os.path.getmtime, reverse=True)
        print(f"Found {len(export_files)} Spamzilla export files.")
        print(f"Using the most recent: {export_files[0]}")
        return export_files[0]

    print("No Spamzilla export files found.")
    return None

def process_semrush_files(semrush_files):
    """
    Process the SEMRUSH files and combine them if needed.
    """
    if not semrush_files or len(semrush_files) == 0:
        raise ValueError("No valid SEMRUSH files provided")

    try:
        # Combine all files
        print(f"Combining {len(semrush_files)} SEMRUSH files...")
        dfs = []
        for file in semrush_files:
            print(f"Reading: {os.path.basename(file)}")
            df_temp = pd.read_csv(file)
            
            # Extract domain name from filename
            domain_name = os.path.basename(file).replace('-backlinks.csv', '').replace('-backlinks - Copy.csv', '')
            
            # Add domain name as Name column
            df_temp['Name'] = domain_name
            
            # Rename Target column if it exists
            if 'Target' in df_temp.columns:
                df_temp = df_temp.rename(columns={'Target': 'Target_URL'})
            
            dfs.append(df_temp)
        
        df = pd.concat(dfs, ignore_index=True)
        print(f"Combined {len(dfs)} files into one DataFrame")

        # Ensure Name column exists
        if 'Name' not in df.columns:
            print(f"Warning: DataFrame doesn't have a 'Name' column.")
            # Try to identify a suitable domain column
            possible_domain_cols = [col for col in df.columns if
                                    any(term in col.lower() for term in ["domain", "url", "site", "target"])]
            if possible_domain_cols:
                df = df.rename(columns={possible_domain_cols[0]: "Name"})
                print(f"Renamed column '{possible_domain_cols[0]}' to 'Name'")
            else:
                print(f"Available columns: {list(df.columns)}")
                raise ValueError("Could not find a domain column in the SEMRUSH file")

        # Standardize Name column
        df['Name'] = df['Name'].astype(str).str.lower().str.strip()

        print(f"Processed SEMRUSH data with {len(df)} rows")
        print("Available columns:", df.columns.tolist())
        return df

    except Exception as e:
        print(f"Error processing SEMRUSH files: {e}")
        raise


def find_writable_path():
    """
    Find a path where we can write the CSV files.
    Returns a tuple of (path, description)
    """
    # Generate directory name with current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    base_dirname = f"{current_date}_SEO_data"

    # Try different possible paths
    possible_paths = [
        # Current directory
        (os.path.join(os.getcwd(), base_dirname), "current directory"),

        # Desktop paths (handle both standard and OneDrive)
        (os.path.join(os.path.expanduser("~"), "Desktop", base_dirname), "Desktop"),
        (os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", base_dirname), "OneDrive Desktop"),

        # Documents folder
        (os.path.join(os.path.expanduser("~"), "Documents", base_dirname), "Documents folder"),
        (os.path.join(os.path.expanduser("~"), "OneDrive", "Documents", base_dirname), "OneDrive Documents"),

        # Temp directory as last resort
        (os.path.join(os.environ.get("TEMP", os.getcwd()), base_dirname), "temporary folder")
    ]

    # Try to create a directory in each location
    for path, description in possible_paths:
        try:
            # Test if we can create and write to this directory
            os.makedirs(path, exist_ok=True)
            test_file = os.path.join(path, ".write_test")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)

            # If we get here, we found a writable path
            return path, description
        except:
            continue

    # If all else fails, use a backup directory in current directory
    backup_path = os.path.join(os.getcwd(), f"{current_date}_SEO_data_backup")
    os.makedirs(backup_path, exist_ok=True)
    return backup_path, "current directory with backup name"

def create_csv_files(df_main, df_rejected, df_spam_test, output_dir):
    """
    Creates CSV files for all sheets.
    
    Args:
        df_main (pd.DataFrame): DataFrame for the main sheet
        df_rejected (pd.DataFrame): DataFrame for the rejected sheet
        df_spam_test (pd.DataFrame): DataFrame for the spam test sheet
        output_dir (str): Directory to save the CSV files
        
    Returns:
        dict: Dictionary containing paths to created CSV files
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create CSV files
    main_csv = create_main_sheet_csv(df_main, output_dir, timestamp)
    rejected_csv = create_rejected_sheet_csv(df_rejected, output_dir, timestamp)
    spam_test_csv = create_spam_test_sheet_csv(df_spam_test, output_dir, timestamp)
    
    return {
        'main_csv': main_csv,
        'rejected_csv': rejected_csv,
        'spam_test_csv': spam_test_csv
    }

def extract_domains_from_quality_folder():
    """
    Extract domain names from the most recent date folder in EVERYTHING_QUALITY.
    
    Returns:
        list: List of domain names
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    quality_dir = os.path.join(base_dir, "BACKLINK_CSV_FILES", "EVERYTHING_QUALITY")
    
    # Find all date folders
    date_folders = [d for d in os.listdir(quality_dir) if os.path.isdir(os.path.join(quality_dir, d))]
    if not date_folders:
        raise ValueError("No date folders found in EVERYTHING_QUALITY directory")
    
    # Sort date folders and get the most recent one
    date_folders.sort(reverse=True)
    latest_date_folder = date_folders[0]
    latest_folder_path = os.path.join(quality_dir, latest_date_folder)
    
    # Get all CSV files in the latest date folder
    csv_files = [f for f in os.listdir(latest_folder_path) if f.endswith('_quality.csv')]
    
    # Extract domain names from filenames
    domains = []
    for file in csv_files:
        domain = file.replace('_quality.csv', '')
        domains.append(domain)
    
    print(f"Found {len(domains)} domains in {latest_date_folder} folder:")
    for domain in domains:
        print(f"- {domain}")
    
    return domains

def read_domains_from_file(file_path=None):
    """
    Read domains from either a text file or extract them from the EVERYTHING_QUALITY folder.
    
    Args:
        file_path (str, optional): Path to the text file containing domains
        
    Returns:
        list: List of domains
    """
    if file_path and os.path.exists(file_path):
        # Read from text file if provided and exists
        with open(file_path, 'r') as f:
            domains = [line.strip() for line in f if line.strip()]
        print(f"Read {len(domains)} domains from file: {file_path}")
        return domains
    else:
        # Extract domains from EVERYTHING_QUALITY folder
        return extract_domains_from_quality_folder()