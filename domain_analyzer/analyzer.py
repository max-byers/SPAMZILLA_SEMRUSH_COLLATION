import importlib
import pandas as pd
import numpy as np
import os
import datetime
import glob
import re
import traceback
from datetime import datetime
from input_handler import find_semrush_files, process_semrush_files, find_writable_path, find_spamzilla_file
from output_handler import create_csv_files
from domain_metrics import create_processed_dataframe, determine_rejection_reasons, prepare_data_for_csv, generate_rejection_analysis
import config  # Import the new config

# Base directory is one level up from the current directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Use the manually set SEMRUSH comparison directory or fall back to automatic selection
SEMRUSH_DIR = config.SEMRUSH_COMPARISON_PATH or os.path.join(BASE_DIR, "24_08_SEMRUSH_comparison")

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

def get_newest_spamzilla_file(base_dir):
    """Get the Spamzilla export file."""
    # Check if a manual file path is set
    if config.SPAMZILLA_FILE_PATH and os.path.exists(config.SPAMZILLA_FILE_PATH):
        return config.SPAMZILLA_FILE_PATH
    
    # Check both the export directory and root directory
    export_dir = os.path.join(base_dir, "SPAMZILLA_DOMAIN_EXPORTS")
    export_files = glob.glob(os.path.join(export_dir, "export-*.csv"))
    root_files = glob.glob(os.path.join(base_dir, "export-*.csv"))
    
    # Combine and sort all files
    all_files = export_files + root_files
    if all_files:
        all_files.sort(key=os.path.getmtime, reverse=True)
        return all_files[0]
    return None

def get_previous_day_files(base_dir, current_file_date):
    """Placeholder function - no longer used."""
    return []

def load_domain_history(previous_files):
    """Placeholder function - no longer used."""
    return set()

def check_domain_history(domain_name, domain_history):
    """Placeholder function - no longer used."""
    return False

def main():
    try:
        # Find and process files
        spamzilla_file = get_newest_spamzilla_file(BASE_DIR)
        print(f"Spamzilla file selected: {spamzilla_file}")
        if not spamzilla_file:
            raise FileNotFoundError("No Spamzilla export file found")
            
        # Get current file date
        current_file_date = datetime.fromtimestamp(os.path.getmtime(spamzilla_file))
        
        # Remove previous domain history code block
        
        semrush_files = find_semrush_files(BASE_DIR, SEMRUSH_DIR)
        print(f"SEMRUSH files selected: {semrush_files}")
        
        # Process SEMRUSH data
        processed_df = process_semrush_files(spamzilla_file, semrush_files)
        print(f"Processed SEMRUSH and Spamzilla data, resulting DataFrame shape: {processed_df.shape}")
        
        # Create processed dataframe
        processed_df = create_processed_dataframe(processed_df)
        
        # Remove domain history-related column initialization
        
        # Determine rejection reasons and split data
        accepted_df, rejected_df = determine_rejection_reasons(processed_df, processed_df)
        print(f"Accepted domains: {len(accepted_df)}, Rejected domains: {len(rejected_df)}")
        
        # Prepare data for CSV files
        accepted_df, rejected_df, spam_test_df = prepare_data_for_csv(accepted_df, rejected_df)
        print(f"Prepared data for CSV files.")
        
        # Create output directory path
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DOMAIN_LIST")
        os.makedirs(output_dir, exist_ok=True)
        
        # Use current date for output
        today = datetime.now()
        timestamp = today.strftime("%Y%m%d")
        date_folder = today.strftime("%Y-%m-%d")
        
        # Create date-based folder inside the output directory
        date_output_dir = os.path.join(output_dir, date_folder)
        os.makedirs(date_output_dir, exist_ok=True)
        
        # Save only domain names for accepted domains
        accepted_domains_file = os.path.join(date_output_dir, f"accepted_domains_list_{timestamp}.csv")
        accepted_df[['Name', 'Expiry']].to_csv(accepted_domains_file, index=False)
        print(f"\nCreated domains file: {os.path.basename(accepted_domains_file)}")
        
        # Save full data for rejected domains and spam test results
        rejected_csv = os.path.join(date_output_dir, f"rejected_domains_{timestamp}.csv")
        spam_test_csv = os.path.join(date_output_dir, f"spam_test_results_{timestamp}.csv")
        
        rejected_df.to_csv(rejected_csv, index=False)
        spam_test_df.to_csv(spam_test_csv, index=False)
        
        print("\nCSV files created successfully:")
        print(f"  main_csv: {accepted_domains_file}")
        print(f"  rejected_csv: {rejected_csv}")
        print(f"  spam_test_csv: {spam_test_csv}")
        
        # Generate analysis report
        analysis_file = generate_rejection_analysis(accepted_df, rejected_df, date_output_dir, timestamp)
        print(f"\nAnalysis report generated: {analysis_file}")
        
        # Display analysis report contents
        print("\nAnalysis Report Contents:")
        print("=======================")
        with open(analysis_file, 'r') as f:
            print(f.read())
        
        # AS SCORE DISTRIBUTION (0-4)
        # =========================
        #
        # AS 0.0-0.5: 0 domains (0.00%)
        # AS 0.5-1.0: 0 domains (0.00%)
        # AS 1.0-1.5: 3 domains (0.81%)
        # AS 1.5-2.0: 0 domains (0.00%)
        # AS 2.0-2.5: 197 domains (53.10%)
        # AS 2.5-3.0: 0 domains (0.00%)
        # AS 3.0-3.5: 59 domains (15.90%)
        # AS 3.5-4.0: 112 domains (30.19%)
        #
        # Total domains with AS < 5: 371
        # Percentage of total domains: 66.73%
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("\nTraceback:")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    main()