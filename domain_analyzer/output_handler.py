"""
CSV file creation utilities for generating specific CSV files.
"""

import os
import pandas as pd
from datetime import datetime

def create_csv_files(df_accepted, df_rejected, df_spam_test, output_dir=None):
    """
    Creates all CSV files for the processed data.
    
    Args:
        df_accepted (pd.DataFrame): DataFrame containing accepted domains
        df_rejected (pd.DataFrame): DataFrame containing rejected domains
        df_spam_test (pd.DataFrame): DataFrame containing spam test results
        output_dir (str): Directory to save the CSV files. If None, uses DOMAIN_LIST in current directory
        
    Returns:
        tuple: Paths to the created CSV files (main_csv, rejected_csv, spam_test_csv)
    """
    # Set default output directory if none provided
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DOMAIN_LIST")
    
    # Create base output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate timestamp and date (date only, no time)
    timestamp = datetime.now().strftime("%Y%m%d")
    date_folder = datetime.now().strftime("%Y-%m-%d")
    
    # Create date-based folder inside the output directory
    date_output_dir = os.path.join(output_dir, date_folder)
    os.makedirs(date_output_dir, exist_ok=True)
    
    # Create filenames with date only (no time)
    accepted_filename = f"accepted_domains_list_{timestamp}.csv"
    rejected_filename = f"rejected_domains_{timestamp}.csv"
    spam_test_filename = f"spam_test_results_{timestamp}.csv"
    
    # Create file paths
    accepted_path = os.path.join(date_output_dir, accepted_filename)
    rejected_path = os.path.join(date_output_dir, rejected_filename)
    spam_test_path = os.path.join(date_output_dir, spam_test_filename)
    
    # Save only domain names for accepted domains
    df_accepted[['Name', 'Expiry']].to_csv(accepted_path, index=False)
    print(f"\nCreated domains file: {accepted_filename}")
    
    # Save full data for rejected domains and spam test results
    df_rejected.to_csv(rejected_path, index=False)
    df_spam_test.to_csv(spam_test_path, index=False)
    
    print("\nCSV files created successfully:")
    print(f"  main_csv: {accepted_path}")
    print(f"  rejected_csv: {rejected_path}")
    print(f"  spam_test_csv: {spam_test_path}")
    
    return accepted_path, rejected_path, spam_test_path