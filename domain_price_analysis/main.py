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
import logging

# Import configuration
from config import BASE_DIR, SEMRUSH_DIR, SPAMZILLA_DIR, SPAMZILLA_FILE, DOMAINS_DIR, SUMMARY_FILE, OUTPUT_DIR, REQUIRED_COLUMNS

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
    """Find the latest summary file in the SUMMARY directory"""
    summary_dir = os.path.join(base_dir, 'SUMMARY')
    if not os.path.exists(summary_dir):
        print(f"Warning: SUMMARY directory not found at {summary_dir}")
        return None
        
    # Look for the specific 06_06_summary.csv file
    target_file = os.path.join(summary_dir, '06_06_summary.csv')
    if os.path.exists(target_file):
        print(f"Using summary file: {target_file}")
        return target_file
        
    # Fallback to finding the most recent summary file if the specific one isn't found
    summary_files = glob.glob(os.path.join(summary_dir, '*_summary.csv'))
    if not summary_files:
        print("Warning: No summary files found")
        return None
        
    latest_file = max(summary_files, key=os.path.getctime)
    print(f"Using summary file: {latest_file}")
    return latest_file

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

# Required columns for final output
REQUIRED_COLUMNS = [
    'Name', 'Quality domains', 'Quality backlinks', 'TF', 'CF', 'TF/CF',
    'DR', 'UR', 'DA', 'AS', 'A RD', 'M RD', 'S RD', 'IP\'S', 'Age',
    'A (BL/RD)', 'A BL', 'M BL', 'S BL', 'Everything domains',
    'Everything backlinks', 'SZ', 'Expiry', 'Source'
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
    print("\n=== DEBUGGING COLUMN MAPPINGS ===")
    for source_col, target_col in column_mapping.items():
        if source_col in df.columns:
            df[target_col] = df[source_col]
            applied_mappings[target_col] = source_col
            print(f"Mapped '{source_col}' to '{target_col}'")
            
            # Debug the mapped data
            if target_col in ['S BL', 'S RD', 'M BL', 'M RD', 'DA', 'AS', 'DR']:
                mapped_data = df[target_col]
                print(f"  {target_col} data type: {mapped_data.dtype}")
                print(f"  {target_col} non-null count: {mapped_data.notna().sum()}")
                print(f"  {target_col} sample values: {mapped_data.head(3).tolist()}")
        else:
            print(f"Source column '{source_col}' not found for target '{target_col}'")
    
    print("=== END COLUMN MAPPING DEBUG ===\n")

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
    print("\n=== DEBUGGING RATIO CALCULATIONS ===")
    print(f"Available columns: {df.columns.tolist()}")
    
    # Debug S (BL/RD) ratio calculation
    print(f"\nS (BL/RD) calculation:")
    print(f"  'S BL' in columns: {'S BL' in df.columns}")
    print(f"  'S RD' in columns: {'S RD' in df.columns}")
    
    if 'S BL' in df.columns and 'S RD' in df.columns:
        try:
            s_bl = pd.to_numeric(df['S BL'], errors='coerce').fillna(0)
            s_rd = pd.to_numeric(df['S RD'], errors='coerce').fillna(0)
            
            print(f"  S BL values (first 5): {s_bl.head().tolist()}")
            print(f"  S RD values (first 5): {s_rd.head().tolist()}")
            print(f"  S BL non-zero count: {(s_bl > 0).sum()}")
            print(f"  S RD non-zero count: {(s_rd > 0).sum()}")
            
            df['S (BL/RD)'] = np.where(s_rd > 0, s_bl / s_rd, 0)
            print(f"  Calculated S (BL/RD) values (first 5): {df['S (BL/RD)'].head().tolist()}")
            print(f"  S (BL/RD) non-zero count: {(df['S (BL/RD)'] > 0).sum()}")
            print("Calculated 'S (BL/RD)' ratio")
        except Exception as e:
            print(f"Error calculating 'S (BL/RD)': {e}")
            print(f"Exception details: {traceback.format_exc()}")
    else:
        print("  Missing required columns for S (BL/RD) calculation")

    # Debug M (BL/RD) ratio calculation
    print(f"\nM (BL/RD) calculation:")
    print(f"  'M BL' in columns: {'M BL' in df.columns}")
    print(f"  'M RD' in columns: {'M RD' in df.columns}")
    
    if 'M BL' in df.columns and 'M RD' in df.columns:
        try:
            m_bl = pd.to_numeric(df['M BL'], errors='coerce').fillna(0)
            m_rd = pd.to_numeric(df['M RD'], errors='coerce').fillna(0)
            
            print(f"  M BL values (first 5): {m_bl.head().tolist()}")
            print(f"  M RD values (first 5): {m_rd.head().tolist()}")
            print(f"  M BL non-zero count: {(m_bl > 0).sum()}")
            print(f"  M RD non-zero count: {(m_rd > 0).sum()}")
            
            df['M (BL/RD)'] = np.where(m_rd > 0, m_bl / m_rd, 0)
            print(f"  Calculated M (BL/RD) values (first 5): {df['M (BL/RD)'].head().tolist()}")
            print(f"  M (BL/RD) non-zero count: {(df['M (BL/RD)'] > 0).sum()}")
            print("Calculated 'M (BL/RD)' ratio")
        except Exception as e:
            print(f"Error calculating 'M (BL/RD)': {e}")
            print(f"Exception details: {traceback.format_exc()}")
    else:
        print("  Missing required columns for M (BL/RD) calculation")

    # Calculate Variance between authority metrics
    print(f"\n=== DEBUGGING VARIANCE CALCULATION ===")
    print(f"Required columns for variance: ['DA', 'AS', 'DR']")
    print(f"  'DA' in columns: {'DA' in df.columns}")
    print(f"  'AS' in columns: {'AS' in df.columns}")
    print(f"  'DR' in columns: {'DR' in df.columns}")
    
    if all(col in df.columns for col in ['DA', 'AS', 'DR']):
        try:
            da_values = pd.to_numeric(df['DA'], errors='coerce').fillna(0)
            as_values = pd.to_numeric(df['AS'], errors='coerce').fillna(0)
            dr_values = pd.to_numeric(df['DR'], errors='coerce').fillna(0)
            
            print(f"  DA values (first 5): {da_values.head().tolist()}")
            print(f"  AS values (first 5): {as_values.head().tolist()}")
            print(f"  DR values (first 5): {dr_values.head().tolist()}")
            print(f"  DA non-zero count: {(da_values > 0).sum()}")
            print(f"  AS non-zero count: {(as_values > 0).sum()}")
            print(f"  DR non-zero count: {(dr_values > 0).sum()}")
            
            # Calculate variance (max - min)
            max_values = np.maximum.reduce([da_values, as_values, dr_values])
            min_values = np.minimum.reduce([da_values, as_values, dr_values])
            df['Variance'] = max_values - min_values
            
            print(f"  Max values (first 5): {max_values.head().tolist()}")
            print(f"  Min values (first 5): {min_values.head().tolist()}")
            print(f"  Calculated Variance values (first 5): {df['Variance'].head().tolist()}")
            print(f"  Variance non-zero count: {(df['Variance'] > 0).sum()}")
            print("Calculated 'Variance' between DA, AS, and DR")
        except Exception as e:
            print(f"Error calculating 'Variance': {e}")
            print(f"Exception details: {traceback.format_exc()}")
    else:
        print("  Missing required columns for Variance calculation")
        missing_cols = [col for col in ['DA', 'AS', 'DR'] if col not in df.columns]
        print(f"  Missing columns: {missing_cols}")
    
    print("=== END DEBUGGING ===\n")

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

    # Debug final state of calculated columns
    print("\n=== FINAL DEBUGGING OF CALCULATED COLUMNS ===")
    calculated_columns = ['S (BL/RD)', 'M (BL/RD)', 'Variance', 'Follow %']
    for col in calculated_columns:
        if col in df.columns:
            print(f"{col}:")
            print(f"  Data type: {df[col].dtype}")
            print(f"  Non-null count: {df[col].notna().sum()}")
            print(f"  Non-zero count: {(df[col] != 0).sum() if df[col].dtype in ['float64', 'int64'] else 'N/A'}")
            print(f"  Sample values: {df[col].head(5).tolist()}")
        else:
            print(f"{col}: Column not found in final dataframe")
    
    print("=== END FINAL DEBUGGING ===\n")

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

def process_domain_data(domain, semrush_dir, spamzilla_dir, base_dir, summary_file):
    """
    Process data for a single domain from SEMRUSH and Spamzilla files.
    Returns a dictionary with the domain's metrics.
    """
    print(f"\n{'='*50}")
    print(f"Processing data for domain: {domain}")
    print(f"{'='*50}")
    
    domain_data = {
        'Name': domain,
        'Source': '',  # Will be populated from Spamzilla data
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
        'Price': '',
        'Bid': ''  # Added for manual bidding input
    }

    # Process SEMRUSH data
    print(f"\nLooking for SEMRUSH data in: {semrush_dir}")
    
    # Find all SEMRUSH comparison files
    semrush_files = glob.glob(os.path.join(semrush_dir, "*-backlinks_comparison.csv"))
    if not semrush_files:
        print("No SEMRUSH comparison files found")
    else:
        print(f"Found {len(semrush_files)} SEMRUSH comparison files")
        
        # Read and combine all SEMRUSH files
        all_semrush_data = []
        for file in semrush_files:
            try:
                df = pd.read_csv(file)
                all_semrush_data.append(df)
            except Exception as e:
                print(f"Error reading {file}: {str(e)}")
        
        if all_semrush_data:
            # Combine all data
            df_semrush = pd.concat(all_semrush_data, ignore_index=True)
            print(f"Combined SEMRUSH data shape: {df_semrush.shape}")
            print(f"SEMRUSH columns: {df_semrush.columns.tolist()}")
            
            # Find data for this domain
            domain_row = df_semrush[df_semrush['Target'] == domain]
            if not domain_row.empty:
                print(f"\nFound data for domain {domain}")
                print(f"SEMRUSH data:\n{domain_row.iloc[0]}")
                
                semrush_mapping = {
                    'AS': 'Authority Score',
                    'S RD': 'Domains',
                    'S BL': 'Backlinks',
                    'IP\'S': 'IPs',
                    'Follow %': 'Follow links'
                }
                
                print("\nMapping SEMRUSH columns:")
                for target_col, source_col in semrush_mapping.items():
                    if source_col in domain_row.columns:
                        value = domain_row[source_col].iloc[0]
                        if pd.notna(value):
                            domain_data[target_col] = value
                            print(f"✓ Mapped {source_col} to {target_col}: {value}")
                        else:
                            print(f"✗ {source_col} value is NA/empty")
                    else:
                        print(f"✗ Column {source_col} not found in SEMRUSH data")
            else:
                print(f"✗ No data found in SEMRUSH for domain {domain}")
        else:
            print("✗ No valid SEMRUSH data found")

    # Process Spamzilla data
    spamzilla_file = find_spamzilla_file(spamzilla_dir)
    if spamzilla_file:
        try:
            print(f"\nProcessing Spamzilla data from: {spamzilla_file}")
            df_spamzilla = pd.read_csv(spamzilla_file)
            print(f"Spamzilla file shape: {df_spamzilla.shape}")
            print(f"Spamzilla columns: {df_spamzilla.columns.tolist()}")
            
            domain_row = df_spamzilla[df_spamzilla['Name'] == domain]
            if not domain_row.empty:
                print(f"\nFound data for domain {domain}")
                print(f"First row of Spamzilla data:\n{domain_row.iloc[0]}")
                
                # Get the source from Spamzilla data
                if 'Source' in domain_row.columns:
                    source = domain_row['Source'].iloc[0]
                    if pd.notna(source):
                        domain_data['Source'] = source
                        print(f"✓ Set source to: {source}")
                    else:
                        print("✗ Source value is NA/empty")
                else:
                    print("✗ Source column not found in Spamzilla data")
                
                # Map columns with validation
                spamzilla_mapping = {
                    'DA': 'Moz DA',
                    'DR': 'Ahrefs DR',
                    'UR': 'Ahrefs UR',
                    'TF': 'TF',
                    'CF': 'CF',
                    'M RD': 'Majestic RD',
                    'M BL': 'Majestic BL',
                    'A RD': 'Ahrefs RD',
                    'A BL': 'Ahrefs BL',
                    'SZ': 'SZ Score',
                    'Age': 'Age',
                    'MT': 'Majestic Topics',
                    'Expiry': 'Expires'
                }
                
                print("\nMapping Spamzilla columns:")
                for target_col, source_col in spamzilla_mapping.items():
                    if source_col in domain_row.columns:
                        value = domain_row[source_col].iloc[0]
                        if pd.notna(value):  # Only update if value is not NA
                            domain_data[target_col] = value
                            print(f"✓ Mapped {source_col} to {target_col}: {value}")
                        else:
                            print(f"✗ {source_col} value is NA/empty")
                    else:
                        print(f"✗ Column {source_col} not found in Spamzilla data")
            else:
                print(f"✗ No data found in Spamzilla for domain {domain}")
        except Exception as e:
            print(f"✗ Error processing Spamzilla data: {str(e)}")

    # Use the provided summary_file directly
    if summary_file and os.path.exists(summary_file):
        try:
            print(f"\nProcessing summary data from: {summary_file}")
            df_summary = pd.read_csv(summary_file)
            print(f"Summary file shape: {df_summary.shape}")
            print(f"Summary columns: {df_summary.columns.tolist()}")
            
            # Try both with and without -backlinks suffix
            lookup_names = [f"{domain}-backlinks", domain]
            domain_row = None
            for lookup_name in lookup_names:
                domain_row = df_summary[df_summary['Domain name'] == lookup_name]
                if not domain_row.empty:
                    print(f"\nFound data for domain {lookup_name}")
                    print(f"First row of summary data:\n{domain_row.iloc[0]}")
                    break
            
            if domain_row is not None and not domain_row.empty:
                summary_mapping = {
                    'Everything backlinks': 'Everything backlinks',
                    'Everything domains': 'Everything domains',
                    'Quality backlinks': 'Quality backlinks',
                    'Quality domains': 'Quality domains'
                }
                
                print("\nMapping summary columns:")
                for target_col, source_col in summary_mapping.items():
                    if source_col in domain_row.columns:
                        value = domain_row[source_col].iloc[0]
                        if pd.notna(value):
                            domain_data[target_col] = value
                            print(f"✓ Mapped {source_col} to {target_col}: {value}")
                        else:
                            print(f"✗ {source_col} value is NA/empty")
                    else:
                        print(f"✗ Column {source_col} not found in summary data")
            else:
                print(f"✗ No data found in summary for domain {domain} (tried with and without -backlinks suffix)")
        except Exception as e:
            print(f"✗ Error processing summary data: {str(e)}")

    # Print final domain data for verification
    print(f"\nFinal data for domain {domain}:")
    for key, value in domain_data.items():
        if value:  # Only print non-empty values
            print(f"✓ {key}: {value}")

    # Calculate ratios and variance
    print(f"\n=== CALCULATING RATIOS AND VARIANCE ===")
    
    # Calculate S (BL/RD) ratio
    if domain_data['S BL'] and domain_data['S RD']:
        try:
            s_bl = float(domain_data['S BL'])
            s_rd = float(domain_data['S RD'])
            if s_rd > 0:
                domain_data['S (BL/RD)'] = round(s_bl / s_rd, 2)
                print(f"✓ Calculated S (BL/RD): {s_bl} / {s_rd} = {domain_data['S (BL/RD)']}")
            else:
                print(f"✗ S RD is 0, cannot calculate S (BL/RD) ratio")
        except (ValueError, TypeError) as e:
            print(f"✗ Error calculating S (BL/RD): {e}")
    else:
        print(f"✗ Missing S BL ({domain_data['S BL']}) or S RD ({domain_data['S RD']}) for ratio calculation")
    
    # Calculate M (BL/RD) ratio
    if domain_data['M BL'] and domain_data['M RD']:
        try:
            m_bl = float(domain_data['M BL'])
            m_rd = float(domain_data['M RD'])
            if m_rd > 0:
                domain_data['M (BL/RD)'] = round(m_bl / m_rd, 2)
                print(f"✓ Calculated M (BL/RD): {m_bl} / {m_rd} = {domain_data['M (BL/RD)']}")
            else:
                print(f"✗ M RD is 0, cannot calculate M (BL/RD) ratio")
        except (ValueError, TypeError) as e:
            print(f"✗ Error calculating M (BL/RD): {e}")
    else:
        print(f"✗ Missing M BL ({domain_data['M BL']}) or M RD ({domain_data['M RD']}) for ratio calculation")
    
    # Calculate Variance between DA, AS, and DR
    da_values = []
    if domain_data['DA']:
        try:
            da_values.append(float(domain_data['DA']))
        except (ValueError, TypeError):
            pass
    
    if domain_data['AS']:
        try:
            da_values.append(float(domain_data['AS']))
        except (ValueError, TypeError):
            pass
    
    if domain_data['DR']:
        try:
            da_values.append(float(domain_data['DR']))
        except (ValueError, TypeError):
            pass
    
    if len(da_values) >= 2:
        try:
            max_val = max(da_values)
            min_val = min(da_values)
            domain_data['Variance'] = round(max_val - min_val, 2)
            print(f"✓ Calculated Variance: max({da_values}) - min({da_values}) = {domain_data['Variance']}")
        except Exception as e:
            print(f"✗ Error calculating Variance: {e}")
    else:
        print(f"✗ Need at least 2 values from DA ({domain_data['DA']}), AS ({domain_data['AS']}), DR ({domain_data['DR']}) for variance calculation")
    
    print("=== END CALCULATIONS ===\n")

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

        # Remove columns that should not be in the final output
        columns_to_remove = [
            'Indexed', 'Drops', 'MT', 'English %', 'Potentially spam',
            'Everything avg AS', 'Everything median AS', 'Everything avg ext links', 'Everything median ext links',
            'Quality avg AS', 'Quality median AS', 'Quality avg ext links', 'Quality median ext links',
            'Follow %'
        ]
        for col in columns_to_remove:
            if col in df.columns:
                df = df.drop(col, axis=1)

        # Define the required columns with their expected order
        required_columns = [
            'Name', 'Quality domains', 'Quality backlinks', 'TF', 'CF', 'TF/CF',
            'DR', 'UR', 'DA', 'AS', 'A RD', 'M RD', 'S RD', 'IP\'S', 'Age',
            'A (BL/RD)', 'A BL', 'M BL', 'S BL', 'Everything domains',
            'Everything backlinks', 'SZ', 'Expiry', 'Source'
        ]

        # Debug: Print actual columns in the DataFrame
        print("\n=== COLUMN ORDER DEBUGGING ===")
        print("Columns in DataFrame before filtering:")
        print(df.columns.tolist())

        # Check for missing columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print("\n!!! WARNING: MISSING COLUMNS !!!")
            print("The following required columns are missing:")
            for col in missing_columns:
                print(f"  - {col}")

        # Check for unexpected columns
        unexpected_columns = [col for col in df.columns if col not in required_columns]
        if unexpected_columns:
            print("\n!!! WARNING: UNEXPECTED COLUMNS !!!")
            print("The following unexpected columns were found:")
            for col in unexpected_columns:
                print(f"  - {col}")

        # Select and order columns
        output_columns = [col for col in required_columns if col in df.columns]
        
        # Debug: Print selected columns
        print("\nColumns after filtering:")
        print(output_columns)

        # Check if the order matches the expected order
        if output_columns != required_columns[:len(output_columns)]:
            print("\n!!! WARNING: COLUMN ORDER MISMATCH !!!")
            print("Expected order:")
            for i, col in enumerate(required_columns[:len(output_columns)], 1):
                print(f"{i}. {col}")
            print("\nActual order:")
            for i, col in enumerate(output_columns, 1):
                print(f"{i}. {col}")

        # Filter DataFrame to selected columns
        df = df[output_columns]

        # Write to CSV
        df.to_csv(output_filepath, index=False)
        print(f"\nCSV file created successfully at: {output_filepath}")
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

def write_domain_names_csv(domains):
    """
    Write a CSV file containing domain names with columns for manual bidding analysis.
    
    Args:
        domains (list): List of domain names to write to CSV
    
    Returns:
        str: Path to the created CSV file or None if failed
    """
    # Get current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Set output directory for bidding strategy
    output_dir = os.path.join(BASE_DIR, "bidding_strategy")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create filename in the format [date]_bidding_analysis.csv
    output_filepath = os.path.join(output_dir, f"{current_date}_bidding_analysis.csv")

    try:
        # Create a DataFrame with domain names and additional columns for manual entry
        df = pd.DataFrame({
            'Domain': domains,
            'Project Bid': '',     # To be manually filled
            'Actual Bid': '',      # To be manually filled
            'Notes': '',           # For additional comments
            'Priority': ''         # To be manually assigned
        })
        
        # Write to CSV
        df.to_csv(output_filepath, index=False)
        
        print(f"\nBidding analysis CSV file created successfully at: {output_filepath}")
        print(f"Total domains written: {len(domains)}")
        print("Columns added for manual entry: Project Bid, Actual Bid, Notes, Priority")
        
        return output_filepath

    except Exception as e:
        print(f"Error creating bidding analysis CSV file: {e}")
        traceback.print_exc()
        return None

def main():
    logger.info("\nStarting domain price analysis script...")
    logger.info(f"BASE_DIR: {BASE_DIR}")
    logger.info(f"SPAMZILLA_DIR: {SPAMZILLA_DIR}")
    logger.info(f"SEMRUSH_DIR: {SEMRUSH_DIR}")
    logger.info(f"DOMAINS_DIR: {DOMAINS_DIR}")
    logger.info(f"SUMMARY_FILE: {SUMMARY_FILE}")
    logger.info(f"OUTPUT_DIR: {OUTPUT_DIR}")
    logger.info("\nChecking directories:")
    logger.info(f"BASE_DIR exists: {os.path.exists(BASE_DIR)}")
    logger.info(f"SPAMZILLA_DIR exists: {os.path.exists(SPAMZILLA_DIR)}")
    logger.info(f"SEMRUSH_DIR exists: {os.path.exists(SEMRUSH_DIR)}")
    logger.info(f"DOMAINS_DIR exists: {os.path.exists(DOMAINS_DIR)}")
    
    # Get domains to analyze
    domains = get_domains_from_directory(DOMAINS_DIR)
    if not domains:
        logger.error("No domains found to analyze. Exiting.")
        print("No domains found to analyze. Exiting.")
        return
    
    # Write domain names to a separate CSV
    write_domain_names_csv(domains)
    
    # Process each domain and collect results
    all_domain_data = []
    for domain in domains:
        try:
            data = process_domain_data(domain, SEMRUSH_DIR, SPAMZILLA_DIR, BASE_DIR, SUMMARY_FILE)
            all_domain_data.append(data)
        except Exception as e:
            logger.error(f"Error processing domain {domain}: {e}")
    
    # Write the output
    output_file_created = False
    output_filepath = None
    if all_domain_data:
        try:
            from datetime import datetime
            current_date = datetime.now().strftime("%Y-%m-%d")
            output_filepath = os.path.join(OUTPUT_DIR, f"{current_date}_price_analysis.csv")
            write_csv_file(all_domain_data)
            output_file_created = os.path.exists(output_filepath)
            if output_file_created:
                logger.info(f"CSV file created successfully at: {output_filepath}")
                print(f"CSV file created successfully at: {output_filepath}")
            else:
                logger.error(f"CSV file was not created at: {output_filepath}")
                print(f"CSV file was not created at: {output_filepath}")
        except Exception as e:
            logger.error(f"Error writing CSV file: {e}")
            print(f"Error writing CSV file: {e}")
    else:
        logger.warning("No data to write")
        print("No data to write")
    
    # Final check and summary
    if output_filepath:
        if os.path.exists(output_filepath):
            logger.info(f"Output file exists: {output_filepath}")
            print(f"Output file exists: {output_filepath}")
        else:
            logger.error(f"Output file does NOT exist: {output_filepath}")
            print(f"Output file does NOT exist: {output_filepath}")
    else:
        logger.warning("No output file path was set.")
        print("No output file path was set.")

if __name__ == "__main__":
    main()