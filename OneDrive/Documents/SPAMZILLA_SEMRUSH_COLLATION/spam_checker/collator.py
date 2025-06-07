"""
CSV Collator Module

This module handles collating multiple CSV files from date-based folders
into a single consolidated file.
"""

import os
import pandas as pd
from datetime import datetime
from utils import log_info, log_error, log_warning

# Define output directory
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)


def find_date_folders(base_path='.'):
    """
    Find all folders matching the pattern '[date]_spam_checker'
    
    Args:
        base_path (str): Base directory to search in
        
    Returns:
        list: List of folder paths matching the pattern
    """
    try:
        print(f"Searching in directory: {base_path}")
        folders = []
        for item in os.listdir(base_path):
            if os.path.isdir(item) and '_spam_checker' in item:
                try:
                    # Try to parse the date part to ensure it's a valid date folder
                    date_str = item.split('_spam_checker')[0]
                    print(f"Found folder: {item}")
                    folders.append(item)
                except ValueError:
                    print(f"Skipping invalid folder: {item}")
                    continue
        return sorted(folders)
    except Exception as e:
        print(f"Error finding date folders: {str(e)}")
        return []


def collate_csv_files(folder_path, output_path):
    """
    Collate all CSV files in a given folder into a single output file
    
    Args:
        folder_path (str): Path to the folder containing CSV files
        output_path (str): Path where the collated file should be saved
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"\nProcessing folder: {folder_path}")
        # Get all CSV files in the folder
        csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
        print(f"Found {len(csv_files)} CSV files")
        
        if not csv_files:
            print(f"No CSV files found in {folder_path}")
            return False
            
        # Read and concatenate all CSV files
        dfs = []
        for csv_file in csv_files:
            file_path = os.path.join(folder_path, csv_file)
            try:
                print(f"Reading file: {csv_file}")
                df = pd.read_csv(file_path)
                dfs.append(df)
                print(f"Successfully read {csv_file}")
            except Exception as e:
                print(f"Error reading {csv_file}: {str(e)}")
                continue
        
        if not dfs:
            print("No valid CSV files could be read")
            return False
            
        # Concatenate all dataframes
        print("Combining dataframes...")
        combined_df = pd.concat(dfs, ignore_index=True)
        
        # If output_path is just a filename, put it in the output directory
        if os.path.dirname(output_path) == '':
            output_path = os.path.join(OUTPUT_DIR, output_path)
            
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Write the combined dataframe to CSV
        print(f"Writing to {output_path}")
        combined_df.to_csv(output_path, index=False)
        print(f"Successfully collated {len(dfs)} files into {output_path}")
        return True
        
    except Exception as e:
        print(f"Error collating files: {str(e)}")
        return False


def process_all_folders(base_path='.'):
    """
    Process all date-based folders and create collated files for each
    
    Args:
        base_path (str): Base directory to search in
    """
    print("Starting folder processing...")
    folders = find_date_folders(base_path)
    
    if not folders:
        print("No valid date folders found")
        return
        
    for folder in folders:
        date_str = folder.split('_spam_checker')[0]
        output_filename = f"{date_str}_collated.csv"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        print(f"\nProcessing folder: {folder}")
        if collate_csv_files(folder, output_path):
            print(f"Successfully created collated file: {output_filename}")
        else:
            print(f"Failed to create collated file for {folder}")


def collate_spam_files(input_dir='SPAM_EXPORTS', date_str=None):
    """
    Collate all CSV files from a specific date in the SPAM_EXPORTS directory
    
    Args:
        input_dir (str): Directory containing the spam export files
        date_str (str): Date string to filter files (format: YYYY-MM-DD)
    """
    try:
        print(f"Processing files from {input_dir}")
        
        # Get all CSV files in the directory
        csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
        
        # Filter files by date if specified
        if date_str:
            csv_files = [f for f in csv_files if date_str in f]
            
        print(f"Found {len(csv_files)} CSV files")
        
        if not csv_files:
            print(f"No CSV files found in {input_dir}")
            return False
            
        # Read and concatenate all CSV files
        dfs = []
        for csv_file in csv_files:
            file_path = os.path.join(input_dir, csv_file)
            try:
                print(f"Reading file: {csv_file}")
                df = pd.read_csv(file_path)
                dfs.append(df)
                print(f"Successfully read {csv_file}")
            except Exception as e:
                print(f"Error reading {csv_file}: {str(e)}")
                continue
        
        if not dfs:
            print("No valid CSV files could be read")
            return False
            
        # Concatenate all dataframes
        print("Combining dataframes...")
        combined_df = pd.concat(dfs, ignore_index=True)
        
        # Generate output filename with current date
        output_filename = f"spam_collated_{datetime.now().strftime('%Y%m%d')}.csv"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
            
        # Write the combined dataframe to CSV
        print(f"Writing to {output_path}")
        combined_df.to_csv(output_path, index=False)
        print(f"Successfully collated {len(dfs)} files into {output_path}")
        return True
        
    except Exception as e:
        print(f"Error collating files: {str(e)}")
        return False


if __name__ == "__main__":
    # Use today's date
    today = datetime.now().strftime('%Y-%m-%d')
    collate_spam_files(date_str=today) 