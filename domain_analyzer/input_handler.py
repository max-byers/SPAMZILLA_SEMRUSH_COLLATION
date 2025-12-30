import os
import glob
import pandas as pd
import numpy as np
from datetime import datetime
from output_handler import create_csv_files

print("Loading file_operations.py - Using most recent SEMRUSH directory")

def find_semrush_files(base_dir, semrush_dir=None):
    """
    Find the merged SEMRUSH file in the specified SEMRUSH subfolder.
    If no directory is specified, it will look for the most recent monthly folder.
    """
    if semrush_dir is None:
        # Find all monthly SEMRUSH folders
        monthly_folders = glob.glob(os.path.join(base_dir, "*_SEMRUSH_comparison"))
        if not monthly_folders:
            print("No monthly SEMRUSH folders found")
            return []
        
        # Sort by modification time (newest first)
        monthly_folders.sort(key=os.path.getmtime, reverse=True)
        semrush_dir = monthly_folders[0]
    
    print(f"Using specified SEMRUSH directory: {semrush_dir}")

    # Ensure semrush_dir is an absolute path
    if not os.path.isabs(semrush_dir):
        semrush_dir = os.path.abspath(semrush_dir)

    # First try to find the merged file
    merged_file = os.path.join(semrush_dir, "merged_file.csv")
    if os.path.exists(merged_file):
        print(f"Found merged SEMRUSH file: {merged_file}")
        return [merged_file]

    # If no merged file, try to find individual comparison files
    print(f"Looking for SEMRUSH comparison files in: {semrush_dir}")
    # Use forward slashes for the pattern to ensure cross-platform compatibility
    pattern = semrush_dir.replace(os.sep, '/') + "/*-backlinks_comparison.csv"
    print(f"Glob pattern used: {pattern}")
    comparison_files = glob.glob(pattern)
    
    if not comparison_files:
        # Try alternative pattern for backlinks files
        alt_pattern = semrush_dir.replace(os.sep, '/') + "/*-backlinks.csv"
        print(f"Alternative glob pattern used: {alt_pattern}")
        comparison_files = glob.glob(alt_pattern)
        
        # Print directory contents for debugging
        print(f"Directory contents of {semrush_dir}:")
        try:
            print(os.listdir(semrush_dir))
        except Exception as e:
            print(f"Could not list directory contents: {e}")

    if comparison_files:
        print(f"Found {len(comparison_files)} comparison files: {comparison_files}")
        return comparison_files

    print(f"No SEMRUSH files found in {semrush_dir}")
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

    # Try to find any Spamzilla export files in the SPAMZILLA_DOMAIN_EXPORTS directory
    export_dir = os.path.join(base_dir, "SPAMZILLA_DOMAIN_EXPORTS")
    export_files = glob.glob(os.path.join(export_dir, "export-*.csv"))

    if export_files:
        # Sort by modification time (newest first)
        export_files.sort(key=os.path.getmtime, reverse=True)
        print(f"Found {len(export_files)} Spamzilla export files.")
        print(f"Using the most recent: {export_files[0]}")
        return export_files[0]

    print("No Spamzilla export files found.")
    return None

def process_semrush_files(spamzilla_file, semrush_files):
    """
    Process the Spamzilla and SEMRUSH files and combine them.
    
    Args:
        spamzilla_file (str): Path to the Spamzilla export file
        semrush_files (list): List of paths to SEMRUSH comparison files
        
    Returns:
        pd.DataFrame: Combined and processed DataFrame
    """
    if not spamzilla_file:
        raise ValueError("No valid Spamzilla file provided")
    if not semrush_files or len(semrush_files) == 0:
        raise ValueError("No valid SEMRUSH files provided")

    try:
        # Read Spamzilla file
        df_spamzilla = pd.read_csv(spamzilla_file)
        
        # Fix column misalignment issue: "Out Domains External" column causes shift
        # The columns after "Out Domains External" are shifted left by 1:
        # - Out Domains External contains Date Added data (dates)
        # - Date Added contains Price data (prices with $)
        # - Price contains Expires data (dates with times)
        # - Expires is empty
        # We need to shift right: Expires <- Price, Price <- Date Added, Date Added <- Out Domains External
        if 'Out Domains External' in df_spamzilla.columns and 'Expires' in df_spamzilla.columns:
            # Store original values before shifting
            out_domains_values = df_spamzilla['Out Domains External'].copy()
            date_added_values = df_spamzilla['Date Added'].copy() if 'Date Added' in df_spamzilla.columns else pd.Series(index=df_spamzilla.index, dtype=object)
            price_values = df_spamzilla['Price'].copy() if 'Price' in df_spamzilla.columns else pd.Series(index=df_spamzilla.index, dtype=object)
            
            # Shift values to the right (each column gets value from previous column):
            # 1. Date Added gets Out Domains External's value
            if 'Date Added' in df_spamzilla.columns:
                df_spamzilla['Date Added'] = out_domains_values.copy()
            
            # 2. Price gets Date Added's value  
            if 'Price' in df_spamzilla.columns:
                df_spamzilla['Price'] = date_added_values.copy()
            
            # 3. Expires gets Price's value (this is the expiry date!)
            df_spamzilla['Expires'] = price_values.copy()
            
            # 4. Clear Out Domains External since it had misaligned data
            df_spamzilla['Out Domains External'] = ''
            
            # Verify the fix
            expires_count = df_spamzilla['Expires'].notna().sum()
            print(f"Fixed column misalignment: shifted columns after 'Out Domains External' to correct positions")
            print(f"  Expires column now has {expires_count} non-empty values (expiry dates from Price column)")
        
        # Process SEMRUSH files
        # If we have a merged file, use it directly
        if len(semrush_files) == 1 and "merged_file.csv" in semrush_files[0]:
            print(f"Reading merged SEMRUSH file: {os.path.basename(semrush_files[0])}")
            df_semrush = pd.read_csv(semrush_files[0])
        else:
            # Otherwise, combine all comparison files
            print(f"Combining {len(semrush_files)} SEMRUSH comparison files...")
            dfs = []
            for file in semrush_files:
                print(f"Reading: {os.path.basename(file)}")
                df = pd.read_csv(file)
                dfs.append(df)
            df_semrush = pd.concat(dfs, ignore_index=True)
            print(f"Combined {len(dfs)} files into one DataFrame")

        # Ensure Target column exists in SEMRUSH data
        if 'Target' not in df_semrush.columns:
            print(f"Warning: SEMRUSH file doesn't have a 'Target' column.")
            # Try to identify a suitable domain column
            possible_domain_cols = [col for col in df_semrush.columns if
                                    any(term in col.lower() for term in ["domain", "url", "site", "name"])]
            if possible_domain_cols:
                df_semrush = df_semrush.rename(columns={possible_domain_cols[0]: "Target"})
                print(f"Renamed column '{possible_domain_cols[0]}' to 'Target'")
            else:
                print(f"Available columns: {list(df_semrush.columns)}")
                raise ValueError("Could not find a domain column in the SEMRUSH file")

        # Standardize Target column
        df_semrush['Target'] = df_semrush['Target'].astype(str).str.lower().str.strip()
        
        # Merge dataframes
        df_merged = pd.merge(
            df_spamzilla,
            df_semrush,
            left_on='Name',
            right_on='Target',
            how='left'
        )

        print(f"Processed and merged data with {len(df_merged)} rows")
        return df_merged

    except Exception as e:
        print(f"Error processing files: {e}")
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
    Creates all CSV files for the processed data.
    
    Args:
        df_main (pd.DataFrame): DataFrame containing accepted domains
        df_rejected (pd.DataFrame): DataFrame containing rejected domains
        df_spam_test (pd.DataFrame): DataFrame containing spam test results
        output_dir (str): Directory to save the CSV files
        
    Returns:
        tuple: Paths to the created CSV files (main_csv, rejected_csv, spam_test_csv)
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\nCreating CSV files in: {output_dir} (current directory)")
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create CSV files
    main_csv = create_csv_files(df_main, output_dir, timestamp)
    rejected_csv = create_csv_files(df_rejected, output_dir, timestamp)
    spam_test_csv = create_csv_files(df_spam_test, output_dir, timestamp)
    
    print("\nCSV files created successfully:")
    print(f"  main_csv: {main_csv}")
    print(f"  rejected_csv: {rejected_csv}")
    print(f"  spam_test_csv: {spam_test_csv}")
    
    return main_csv, rejected_csv, spam_test_csv