import importlib
import pandas as pd
import numpy as np
import os
import datetime
import glob
import re
import traceback
from datetime import datetime, timedelta
import sys

def find_latest_semrush_dir(base_dir):
    """
    Find the current month's SEMRUSH directory.
    """
    # Get current month name
    current_month = datetime.now().strftime("%B")
    
    # Look for directory matching the pattern Month_SEMRUSH_backlinks
    semrush_dir = os.path.join(base_dir, f"{current_month}_SEMRUSH_backlinks")
    
    if not os.path.exists(semrush_dir):
        print(f"No SEMRUSH directory found for current month: {semrush_dir}")
        return None
    
    print(f"Found SEMRUSH directory: {semrush_dir}")
    return semrush_dir

def find_latest_summary_file(base_dir):
    """
    Find the summary file for the current date in the BACKLINK_CSV_FILES/SUMMARY directory.
    """
    summary_dir = os.path.join(base_dir, "BACKLINK_CSV_FILES", "SUMMARY")
    if not os.path.exists(summary_dir):
        print(f"Summary directory not found: {summary_dir}")
        return None

    # Get current date in YYYY-MM-DD format
    current_date = datetime.now().strftime("%Y-%m-%d")
    summary_file = os.path.join(summary_dir, f"{current_date}_summary.csv")

    if not os.path.exists(summary_file):
        print(f"No summary file found for current date: {summary_file}")
        return None

    print(f"Found summary file: {summary_file}")
    return summary_file

def find_latest_semrush_comparison_dir(base_dir):
    """
    Find the most recent SEMRUSH_comparison directory.
    """
    semrush_comparison_dirs = glob.glob(os.path.join(base_dir, "*_SEMRUSH_comparison"))
    if not semrush_comparison_dirs:
        print("No SEMRUSH_comparison directories found")
        return None
    semrush_comparison_dirs.sort(key=os.path.getmtime, reverse=True)
    latest_dir = semrush_comparison_dirs[0]
    print(f"Found latest SEMRUSH_comparison directory: {latest_dir}")
    return latest_dir

try:
    # Add the parent directory to the Python path
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(parent_dir)
    print(f"Added parent directory to path: {parent_dir}")

    # Constants
    BASE_DIR = r"C:\Users\Max Byers\OneDrive\Documents\SPAMZILLA_SEMRUSH_COLLATION"
    import glob
    # Find most recent SEMRUSH directory
    semrush_dirs = glob.glob(os.path.join(BASE_DIR, "May_SEMRUSH_comparison", "*_SEMRUSH_backlinks"))
    semrush_dirs += glob.glob(os.path.join(BASE_DIR, "May_SEMRUSH_comparison", "*_SEMRUSH_comparison"))
    semrush_dirs = sorted(semrush_dirs, key=os.path.getmtime, reverse=True)
    SEMRUSH_DIR = semrush_dirs[0] if semrush_dirs else None
    # Find most recent Spamzilla file
    spamzilla_files = glob.glob(os.path.join(BASE_DIR, "SPAMZILLA_DOMAIN_EXPORTS", "export-133821_2025-*.csv"))
    spamzilla_files = sorted(spamzilla_files, key=os.path.getmtime, reverse=True)
    SPAMZILLA_FILE = os.path.basename(spamzilla_files[0]) if spamzilla_files else None
    SPAMZILLA_DIR = os.path.join(BASE_DIR, "SPAMZILLA_DOMAIN_EXPORTS")
    DOMAINS_DIR = os.path.join(BASE_DIR, "BACKLINK_CSV_FILES", "30_05")
    SUMMARY_FILE = os.path.join(BASE_DIR, "SUMMARY", "30_05_summary.csv")

    print("\nStarting domain price analysis script...")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Using BASE directory: {BASE_DIR}")
    print(f"Using SPAMZILLA directory: {SPAMZILLA_DIR}")
    print(f"Using SEMRUSH comparison directory: {SEMRUSH_DIR}")
    print(f"Using domains directory: {DOMAINS_DIR}")
    print(f"Using summary file: {SUMMARY_FILE}")
    print(f"Using Spamzilla file: {SPAMZILLA_FILE}")

    # Check if directories exist
    print("\nChecking directories:")
    print(f"BASE_DIR exists: {os.path.exists(BASE_DIR)}")
    print(f"SPAMZILLA_DIR exists: {os.path.exists(SPAMZILLA_DIR)}")
    print(f"SEMRUSH_DIR exists: {os.path.exists(SEMRUSH_DIR)}")
    print(f"DOMAINS_DIR exists: {os.path.exists(DOMAINS_DIR)}")

except Exception as e:
    print(f"Error during initialization: {e}")
    traceback.print_exc()

# Required columns for final output
REQUIRED_COLUMNS = [
    'Name', 'Source', 'Potentially spam', 'DA', 'AS', 'DR', 'UR', 'TF', 'CF',
    'S RD', 'M RD', 'A RD', 'S BL', 'M BL', 'A BL', 'IP\'S', 'SZ', 'Variance',
    'Follow %', 'S (BL/RD)', 'M (BL/RD)', 'Age', 'Indexed', 'Drops', 'MT',
    'English %', 'Expiry'
]

# Prohibited topics for spam checking
PROHIBITED_TOPICS = [
    'adult', 'porn', 'xxx', 'sex', 'erotic', 'escort', 'dating', 'mature',
    'casino', 'gambling', 'bet', 'poker', 'slots', 'lottery', 'wager', 'bingo',
    'pharmacy', 'drug', 'pill', 'medication', 'prescription', 'med', 'pharma',
    'viagra', 'cialis', 'supplement', 'weight loss',
    'hack', 'crack', 'keygen', 'warez', 'torrent', 'pirate', 'bootleg',
    'counterfeit', 'fake', 'replica', 'piracy', 'cheat',
    'politic', 'racism', 'extremist', 'partisan', 'supremacist', 'terrorist',
    'propaganda', 'conspiracy', 'radical'
]

# Import functions from modules
from file_operations import find_semrush_files, process_semrush_files, find_writable_path, find_spamzilla_file, create_csv_files, read_domains_from_file
from data_processing import create_processed_dataframe, determine_rejection_reasons, prepare_data_for_csv
from backlink_collation import process_backlink_data

def find_semrush_files(base_dir):
    """
    Find the SEMRUSH files in the specified directory.
    """
    print(f"Looking for SEMRUSH files in: {base_dir}")
    
    # Look for files with different patterns
    patterns = [
        "*-backlinks_comparison.csv",  # Comparison files
        "*-backlinks.csv",             # Backlinks files
        "*-backlinks - Copy.csv"       # Copy pattern
    ]
    
    all_files = []
    
    # Look in the specified directory
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
        # Combine all comparison files
        print(f"Combining {len(semrush_files)} SEMRUSH comparison files...")
        dfs = []
        for file in semrush_files:
            print(f"Reading: {os.path.basename(file)}")
            df = pd.read_csv(file)
            
            # Extract domain name from filename if Target column is missing
            if 'Target' not in df.columns:
                domain = os.path.basename(file).split('-backlinks_comparison.csv')[0]
                df['Target'] = domain
                print(f"Added Target column with domain: {domain}")
            
            # Ensure all required columns exist
            required_cols = ['Target', 'Authority Score', 'Backlinks', 'Domains', 'IPs', 'Follow links', 'Nofollow links']
            for col in required_cols:
                if col not in df.columns:
                    df[col] = np.nan
                    print(f"Added missing column: {col}")
            
            dfs.append(df)
        
        df = pd.concat(dfs, ignore_index=True)
        print(f"Combined {len(dfs)} files into one DataFrame")

        # Standardize Target column
        df['Target'] = df['Target'].astype(str).str.lower().str.strip()

        # Convert numeric columns to appropriate types
        numeric_cols = ['Authority Score', 'Backlinks', 'Domains', 'IPs', 'Follow links', 'Nofollow links']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                print(f"Converted {col} to numeric type")

        print(f"Processed SEMRUSH data with {len(df)} unique domains")
        return df

    except Exception as e:
        print(f"Error processing SEMRUSH files: {e}")
        raise

def find_writable_path():
    """
    Find a path where we can write the CSV files.
    Returns a tuple of (path, description)
    """
    # Generate filename with current date
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

    # Try to create directory and write a test file in each location
    for path, description in possible_paths:
        try:
            # Create the directory if it doesn't exist
            if not os.path.exists(path):
                os.makedirs(path)

            # Test if we can write to this directory
            test_file = os.path.join(path, ".write_test")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)

            # If we get here, we found a writable path
            return path, description
        except:
            continue

    # If all else fails, use a backup directory in current directory
    backup_path = os.path.join(os.getcwd(), f"{base_dirname}_backup")
    try:
        if not os.path.exists(backup_path):
            os.makedirs(backup_path)
        return backup_path, "current directory with backup name"
    except:
        return os.getcwd(), "current directory"

def create_processed_dataframe(df_merged):
    """
    Process the merged dataframe to create the final dataframe with all metrics.
    """
    print(f"Merged dataframe has {len(df_merged)} rows and {len(df_merged.columns)} columns")
    print("Column names in merged data:", df_merged.columns.tolist())

    # Debug SEMRUSH data mapping
    print("\nDebug SEMRUSH data mapping:")
    semrush_cols = [col for col in df_merged.columns if 'SEM' in col]
    print(f"SEMRUSH columns in merged data: {semrush_cols}")

    # Create a copy to avoid modifying the original
    df = df_merged.copy()

    # Standardize domain name column
    if 'name' in df.columns:
        df = df.rename(columns={'name': 'Name'})
        print("Renamed 'name' column to 'Name'")
    elif 'Name' not in df.columns and 'Target' in df.columns:
        df['Name'] = df['Target']
        print("Created 'Name' column from 'Target' column")

    # Map source data columns to expected columns
    column_mapping = {
        'Source': 'Source',
        'Moz DA': 'DA',
        'Authority Score': 'AS',  # From SEMRUSH comparison
        'Ahrefs DR': 'DR',
        'Ahrefs UR': 'UR',
        'TF': 'TF',
        'CF': 'CF',
        'Domains': 'S RD',  # From SEMRUSH comparison
        'Majestic RD': 'M RD',
        'Ahrefs RD': 'A RD',
        'Backlinks': 'S BL',  # From SEMRUSH comparison
        'Majestic BL': 'M BL',
        'Ahrefs BL': 'A BL',
        'IPs': 'IP\'S',  # From SEMRUSH comparison
        'SZ Score': 'SZ',
        'Age': 'Age',
        'Google Index': 'Indexed',
        'Majestic Topics': 'MT',
        'Follow links': 'Follow %',
        'Expires': 'Expiry'
    }

    # Create a dictionary to track what mappings were applied
    applied_mappings = {}

    # Apply column mappings where source columns exist
    for source_col, target_col in column_mapping.items():
        if source_col in df.columns:
            df[target_col] = df[source_col]
            applied_mappings[target_col] = source_col
            print(f"Mapped '{source_col}' to '{target_col}'")

    # Calculate Follow % if we have the necessary columns
    if 'Follow links' in df.columns and 'Nofollow links' in df.columns:
        try:
            follow = pd.to_numeric(df['Follow links'], errors='coerce').fillna(0)
            nofollow = pd.to_numeric(df['Nofollow links'], errors='coerce').fillna(0)
            total = follow + nofollow
            df['Follow %'] = np.where(total > 0, follow / total, 0)
            print("Calculated 'Follow %' from 'Follow links' and 'Nofollow links'")
        except Exception as e:
            print(f"Error calculating 'Follow %': {e}")

    # Calculate S (BL/RD) and M (BL/RD) ratios
    if 'S BL' in df.columns and 'S RD' in df.columns:
        try:
            s_bl = pd.to_numeric(df['S BL'], errors='coerce').fillna(0)
            s_rd = pd.to_numeric(df['S RD'], errors='coerce').fillna(0)
            df['S (BL/RD)'] = np.where(s_rd > 0, s_bl / s_rd, 0)
            print("Calculated 'S (BL/RD)' ratio")
        except Exception as e:
            print(f"Error calculating 'S (BL/RD)': {e}")

    if 'M BL' in df.columns and 'M RD' in df.columns:
        try:
            m_bl = pd.to_numeric(df['M BL'], errors='coerce').fillna(0)
            m_rd = pd.to_numeric(df['M RD'], errors='coerce').fillna(0)
            df['M (BL/RD)'] = np.where(m_rd > 0, m_bl / m_rd, 0)
            print("Calculated 'M (BL/RD)' ratio")
        except Exception as e:
            print(f"Error calculating 'M (BL/RD)': {e}")

    # Calculate Variance between authority metrics
    if all(col in df.columns for col in ['DA', 'AS', 'DR']):
        try:
            da_values = pd.to_numeric(df['DA'], errors='coerce').fillna(0)
            as_values = pd.to_numeric(df['AS'], errors='coerce').fillna(0)
            dr_values = pd.to_numeric(df['DR'], errors='coerce').fillna(0)
            df['Variance'] = np.maximum.reduce([da_values, as_values, dr_values]) - np.minimum.reduce(
                [da_values, as_values, dr_values])
            print("Calculated 'Variance' between DA, AS, and DR")
        except Exception as e:
            print(f"Error calculating 'Variance': {e}")

    # Initialize potential spam column
    df['Potentially spam'] = ''

    # Check Majestic Topics for prohibited topics
    if 'MT' in df.columns:
        df['MT'] = df['MT'].fillna('').astype(str)
        for index, row in df.iterrows():
            mt_content = row['MT'].lower()
            found_topics = []

            for topic in PROHIBITED_TOPICS:
                if re.search(r'\b' + re.escape(topic) + r'\b', mt_content):
                    found_topics.append(topic)

            if found_topics:
                df.at[index, 'Potentially spam'] += f"Questionable Majestic topics: {', '.join(found_topics)}. "

    # Check name for potential personal names
    df['Name'] = df['Name'].fillna('').astype(str)
    name_pattern = r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'
    for index, row in df.iterrows():
        domain = row['Name'].lower()
        cleaned_domain = re.sub(r'\.(com|net|org|io|co|us|uk|de|fr|info|biz|xyz|site|online)$', '', domain)
        parts = re.split(r'[-_.]', cleaned_domain)
        if any(re.search(name_pattern, part, re.IGNORECASE) for part in parts):
            df.at[index, 'Potentially spam'] += "Possible personal name in domain. "

    # Check for age
    if 'Age' in df.columns:
        try:
            age_values = pd.to_numeric(df['Age'], errors='coerce')
            for index, age in enumerate(age_values):
                if not pd.isna(age) and age < 0.5:
                    df.at[index, 'Potentially spam'] += f"Very new domain (Age: {age} years). "
        except Exception as e:
            print(f"Error processing Age column: {e}")

    # Check for high spam scores
    if 'SZ' in df.columns:
        try:
            sz_values = pd.to_numeric(df['SZ'], errors='coerce')
            for index, sz in enumerate(sz_values):
                if not pd.isna(sz) and sz > 20:
                    df.at[index, 'Potentially spam'] += f"High spam score (SZ: {sz}). "
        except Exception as e:
            print(f"Error processing SZ column: {e}")

    # Check for large discrepancies between metrics
    if 'Variance' in df.columns:
        try:
            variance_values = pd.to_numeric(df['Variance'], errors='coerce')
            for index, variance in enumerate(variance_values):
                if not pd.isna(variance) and variance > 40:
                    df.at[index, 'Potentially spam'] += f"High variance between metrics ({variance}). "
        except Exception as e:
            print(f"Error processing Variance: {e}")

    # Process expiry dates
    if 'Expiry' in df.columns:
        try:
            df['Expiry'] = pd.to_datetime(df['Expiry'], errors='coerce')
            mask = ~df['Expiry'].isna()
            if any(mask):
                df.loc[mask, 'Expiry'] = df.loc[mask, 'Expiry'] + pd.Timedelta(hours=10)
            print("Added 10 hours to Expiry dates")
        except Exception as e:
            print(f"Error processing Expiry dates: {e}")

    # Trim trailing spaces from Potentially spam column
    df['Potentially spam'] = df['Potentially spam'].str.strip()

    # Print out mappings that were applied
    print("\nActual column mappings applied:")
    for target, source in applied_mappings.items():
        print(f"  {source} → {target}")

    # Create missing columns but keep existing ones as they are
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            print(f"Creating missing column: {col}")
            df[col] = ''

    # Print info about the processed dataframe
    print(f"\nProcessed dataframe has {len(df)} rows")
    print("Column types after processing:")
    for col in REQUIRED_COLUMNS:
        if col in df.columns:
            print(f"  {col}: {df[col].dtype}")

    # Return DataFrame with columns in specified order
    return df[REQUIRED_COLUMNS]

def determine_rejection_reasons(df_final, df_all):
    """
    Determine which domains should be rejected and track the reasons.
    """
    print("========================================")
    print("DETERMINE_REJECTION_REASONS FUNCTION CALLED")
    print(f"Received dataframe with {len(df_final)} rows")
    print("========================================")

    # Make a copy to avoid modifying the original
    df = df_final.copy()

    # Initialize rejection tracking
    df['Reason'] = ''

    # Process AS column for rejection
    if 'AS' in df.columns:
        try:
            as_values = pd.to_numeric(df['AS'], errors='coerce').fillna(0)
            mask = as_values < 5
            df.loc[mask, 'Reason'] += "Low Authority Score (AS<5). "
            print(f"Found {mask.sum()} domains with AS < 5")
        except Exception as e:
            print(f"Error checking AS values: {e}")

    # Process SZ column for rejection
    if 'SZ' in df.columns:
        try:
            sz_values = pd.to_numeric(df['SZ'], errors='coerce').fillna(0)
            mask = sz_values > 30
            df.loc[mask, 'Reason'] += "High Spam Score (SZ>30). "
            print(f"Found {mask.sum()} domains with SZ > 30")
        except Exception as e:
            print(f"Error checking SZ values: {e}")

    # Check for prohibited topics in MT
    if 'MT' in df.columns:
        strictly_prohibited = [
            'adult', 'porn', 'xxx', 'sex', 'erotic', 'escort',
            'casino', 'gambling', 'bet', 'poker',
            'viagra', 'cialis', 'pharmacy',
            'warez', 'crack', 'keygen', 'torrent', 'pirate',
            'terrorist', 'extremist', 'supremacist'
        ]

        prohibited_count = 0
        for index, row in df.iterrows():
            mt_content = str(row['MT']).lower()
            found_topics = []

            for topic in strictly_prohibited:
                if re.search(r'\b' + re.escape(topic) + r'\b', mt_content):
                    found_topics.append(topic)

            if found_topics:
                df.at[index, 'Reason'] += f"Prohibited topics: {', '.join(found_topics)}. "
                prohibited_count += 1

        print(f"Found {prohibited_count} domains with prohibited topics")

    # Check for very new domains
    if 'Age' in df.columns:
        try:
            age_values = pd.to_numeric(df['Age'], errors='coerce')
            mask = age_values < 0.25
            df.loc[mask, 'Reason'] += "Extremely new domain (<3 months). "
            print(f"Found {mask.sum()} domains with Age < 0.25 years")
        except Exception as e:
            print(f"Error checking Age values: {e}")

    # Trim trailing spaces from Reason column
    df['Reason'] = df['Reason'].str.strip()

    # Separate accepted and rejected domains
    df_accepted = df[df['Reason'] == ''].copy()
    df_rejected = df[df['Reason'] != ''].copy()

    print(f"\nAccepted domains: {len(df_accepted)}")
    print(f"Rejected domains: {len(df_rejected)}")

    return df_accepted, df_rejected

def write_excel_file(df_final, df_rejected, df_domains, df_auctions):
    """
    Writes the processed data to CSV files in the output_domain_price_analysis directory.
    Returns True if successful, False otherwise.
    """
    # Get current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Set output directory and filepaths
    output_dir = os.path.join(BASE_DIR, "output_domain_price_analysis")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    accepted_filepath = os.path.join(output_dir, f"{current_date}_price_analysis.csv")
    rejected_filepath = os.path.join(output_dir, f"{current_date}_rejected_domains.csv")

    try:
        # Format data before writing
        for df in [df_final, df_rejected]:
            # Convert numeric columns to appropriate format
            numeric_cols = ['DA', 'AS', 'DR', 'UR', 'TF', 'CF', 'S RD', 'M RD', 'A RD', 
                          'S BL', 'M BL', 'A BL', 'IP\'S', 'SZ', 'Variance', 'Follow %', 
                          'S (BL/RD)', 'M (BL/RD)', 'Age']
            
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').round(2)
            
            # Format percentage columns
            if 'Follow %' in df.columns:
                df['Follow %'] = df['Follow %'].apply(lambda x: f"{x:.2%}" if pd.notnull(x) else '')
            
            # Format date column
            if 'Expiry' in df.columns:
                df['Expiry'] = pd.to_datetime(df['Expiry'], errors='coerce').dt.strftime('%Y-%m-%d')
            
            # Fill NaN values with empty strings for string columns
            string_cols = ['Name', 'Source', 'Potentially spam', 'MT', 'Indexed', 'Drops']
            for col in string_cols:
                if col in df.columns:
                    df[col] = df[col].fillna('')

        # Write accepted domains to CSV
        df_final.to_csv(accepted_filepath, index=False)
        print(f"Accepted domains CSV file created successfully at: {accepted_filepath}")

        # Write rejected domains to CSV
        df_rejected.to_csv(rejected_filepath, index=False)
        print(f"Rejected domains CSV file created successfully at: {rejected_filepath}")

        return True

    except Exception as e:
        print(f"Error creating CSV files: {e}")
        traceback.print_exc()
        return False

def find_domains_to_analyze(base_dir):
    """
    Find domains to analyze from the most recent BACKLINK_CSV_FILES summary.
    Returns a list of domain names.
    """
    summary_dir = os.path.join(base_dir, "BACKLINK_CSV_FILES", "SUMMARY")
    if not os.path.exists(summary_dir):
        print(f"Summary directory not found: {summary_dir}")
        return []
    
    # Find all summary files
    summary_files = glob.glob(os.path.join(summary_dir, "*_summary.csv"))
    if not summary_files:
        print("No summary files found")
        return []
    
    # Sort files by modification time (newest first)
    summary_files.sort(key=os.path.getmtime, reverse=True)
    latest_summary = summary_files[0]
    
    print(f"Using most recent summary file: {os.path.basename(latest_summary)}")
    
    try:
        # Read the summary file
        df = pd.read_csv(latest_summary)
        
        # Extract domain names (remove -backlinks suffix if present)
        domains = df['Domain name'].str.replace('-backlinks', '').tolist()
        
        print(f"Found {len(domains)} domains to analyze: {', '.join(domains)}")
        return domains
    except Exception as e:
        print(f"Error reading summary file: {e}")
        return []

def process_domain_data(domain, semrush_dir, spamzilla_dir, base_dir):
    """
    Process data for a single domain from SEMRUSH and Spamzilla files.
    Returns a dictionary with the domain's metrics.
    """
    domain_data = {
        'Name': domain,
        'Source': 'GoDaddy Auctions',
        'Potentially spam': '',
        'DA': '',
        'AS': '',
        'DR': '',
        'UR': '',
        'TF': '',
        'CF': '',
        'S RD': '',
        'M RD': '',
        'A RD': '',
        'S BL': '',
        'M BL': '',
        'A BL': '',
        'IP\'S': '',
        'SZ': '',
        'Variance': '',
        'Follow %': '',
        'S (BL/RD)': '',
        'M (BL/RD)': '',
        'Age': '',
        'Indexed': '',
        'Drops': '',
        'MT': '',
        'English %': '',
        'Expiry': '',
        'Everything backlinks': '',
        'Everything domains': '',
        'Quality backlinks': '',
        'Quality domains': '',
        'Price': ''
    }
    
    # Process SEMRUSH data
    semrush_file = os.path.join(semrush_dir, f"{domain}-backlinks_comparison.csv")
    if os.path.exists(semrush_file):
        try:
            df_semrush = pd.read_csv(semrush_file)
            if not df_semrush.empty:
                # Map SEMRUSH data to domain_data
                domain_data.update({
                    'AS': df_semrush.get('Authority Score', [''])[0],
                    'S RD': df_semrush.get('Domains', [''])[0],
                    'S BL': df_semrush.get('Backlinks', [''])[0],
                    'IP\'S': df_semrush.get('IPs', [''])[0],
                    'Follow %': df_semrush.get('Follow links', [''])[0]
                })
        except Exception as e:
            print(f"Error processing SEMRUSH data for {domain}: {e}")
    
    # Process Spamzilla data
    spamzilla_file = find_spamzilla_file(spamzilla_dir)
    if spamzilla_file:
        try:
            df_spamzilla = pd.read_csv(spamzilla_file)
            domain_row = df_spamzilla[df_spamzilla['Name'] == domain]
            if not domain_row.empty:
                # Map Spamzilla data to domain_data
                domain_data.update({
                    'DA': domain_row.get('Moz DA', [''])[0],
                    'DR': domain_row.get('Ahrefs DR', [''])[0],
                    'UR': domain_row.get('Ahrefs UR', [''])[0],
                    'TF': domain_row.get('TF', [''])[0],
                    'CF': domain_row.get('CF', [''])[0],
                    'M RD': domain_row.get('Majestic RD', [''])[0],
                    'M BL': domain_row.get('Majestic BL', [''])[0],
                    'A RD': domain_row.get('Ahrefs RD', [''])[0],
                    'A BL': domain_row.get('Ahrefs BL', [''])[0],
                    'SZ': domain_row.get('SZ Score', [''])[0],
                    'Age': domain_row.get('Age', [''])[0],
                    'MT': domain_row.get('Majestic Topics', [''])[0],
                    'Expiry': domain_row.get('Expires', [''])[0]
                })
        except Exception as e:
            print(f"Error processing Spamzilla data for {domain}: {e}")
    
    # Get summary data
    current_date = datetime.now().strftime("%d_%m")
    summary_file = os.path.join(base_dir, "BACKLINK_CSV_FILES", "SUMMARY", f"{current_date}_summary.csv")
    if os.path.exists(summary_file):
        try:
            df_summary = pd.read_csv(summary_file)
            domain_row = df_summary[df_summary['Domain name'].str.replace('-backlinks', '') == domain]
            if not domain_row.empty:
                domain_data.update({
                    'Everything backlinks': domain_row.get('Everything backlinks', [''])[0],
                    'Everything domains': domain_row.get('Everything domains', [''])[0],
                    'Quality backlinks': domain_row.get('Quality backlinks', [''])[0],
                    'Quality domains': domain_row.get('Quality domains', [''])[0]
                })
        except Exception as e:
            print(f"Error processing summary data for {domain}: {e}")
    
    return domain_data

def write_csv_file(domains_data):
    """
    Writes the processed data to a CSV file in the output_domain_price_analysis directory.
    """
    # Get current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Set output directory and filepath
    output_dir = os.path.join(BASE_DIR, "output_domain_price_analysis")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_filepath = os.path.join(output_dir, f"{current_date}_price_analysis.csv")

    try:
        # Convert list of dictionaries to DataFrame
        df = pd.DataFrame(domains_data)
        
        # Write to CSV
        df.to_csv(output_filepath, index=False)
        print(f"CSV file created successfully at: {output_filepath}")
        return True

    except Exception as e:
        print(f"Error creating CSV file: {e}")
        traceback.print_exc()
        return False

def get_domains_from_directory(directory):
    """
    Get unique domain names (with TLD) from files in the specified directory.
    """
    print(f"Looking for domain files in: {directory}")
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return []
    files = glob.glob(os.path.join(directory, "*"))
    domains = set()
    for file in files:
        filename = os.path.basename(file)
        # Remove _everything or _quality and .csv
        domain = re.sub(r'_(everything|quality)\.csv$', '', filename)
        domains.add(domain.lower())
    print(f"Found {len(domains)} unique domains (with TLD): {', '.join(sorted(domains))}")
    return sorted(list(domains))

def main():
    """
    Main function to process domain data and generate analysis.
    """
    try:
        # Get domains to analyze
        domains = get_domains_from_directory(DOMAINS_DIR)
        if not domains:
            print("No domains found to analyze. Exiting.")
            return

        # Extract base domains (before first dot)
        base_domains = set([d.split('.')[0].lower() for d in domains])
        print(f"Base domains for partial match: {sorted(base_domains)}")

        # Find SEMRUSH files
        semrush_files = find_semrush_files(SEMRUSH_DIR)
        if not semrush_files:
            print("No SEMRUSH files found. Exiting.")
            return

        # Find Spamzilla file
        spamzilla_file = find_spamzilla_file(SPAMZILLA_DIR, SPAMZILLA_FILE)
        if not spamzilla_file:
            print("No Spamzilla file found. Exiting.")
            return

        # Process SEMRUSH files
        semrush_df = process_semrush_files(semrush_files)
        print(f"\nProcessed SEMRUSH data with {len(semrush_df)} rows")

        # Read Spamzilla data
        spamzilla_df = pd.read_csv(spamzilla_file)
        print(f"\nRead Spamzilla data with {len(spamzilla_df)} rows")

        # Add base domain columns for partial matching
        semrush_df['base_domain'] = semrush_df['Target'].astype(str).str.split('.').str[0].str.lower()
        spamzilla_df['base_domain'] = spamzilla_df['Name'].astype(str).str.split('.').str[0].str.lower()

        # Filter data to only include base domains we want to analyze
        semrush_df = semrush_df[semrush_df['base_domain'].isin(base_domains)]
        spamzilla_df = spamzilla_df[spamzilla_df['base_domain'].isin(base_domains)]

        print(f"Filtered SEMRUSH data: {len(semrush_df)} rows")
        print(f"Filtered Spamzilla data: {len(spamzilla_df)} rows")

        # Merge data (on full domain name, but only for those with matching base domain)
        merged_df = pd.merge(
            semrush_df,
            spamzilla_df,
            left_on='Target',
            right_on='Name',
            how='outer'
        )
        print(f"\nMerged data has {len(merged_df)} rows")

        # Process the merged data
        processed_df = create_processed_dataframe(merged_df)
        print(f"\nProcessed data has {len(processed_df)} rows")

        # Create output directory
        output_dir = os.path.join(BASE_DIR, "output_domain_price_analysis")
        os.makedirs(output_dir, exist_ok=True)

        # Generate output filename with current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        output_file = os.path.join(output_dir, f"{current_date}_price_analysis.csv")

        # Save to CSV
        processed_df.to_csv(output_file, index=False)
        print(f"\nSaved analysis to: {output_file}")

    except Exception as e:
        print(f"Error in main function: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()