#!/usr/bin/env python3
"""
CSV Collation Script for SEMRUSH Comparison Files
This script collates multiple CSV files from a directory into a single comprehensive CSV file.
"""

import pandas as pd
import os
import glob
from pathlib import Path
import argparse
from typing import List, Optional

def collate_csv_files(input_directory: str, output_file: str, file_pattern: str = "*.csv") -> None:
    """
    Collate multiple CSV files from a directory into a single CSV file.
    
    Args:
        input_directory (str): Path to the directory containing CSV files
        output_file (str): Path for the output collated CSV file
        file_pattern (str): Pattern to match CSV files (default: "*.csv")
    """
    try:
        # Get all CSV files in the directory
        csv_files = glob.glob(os.path.join(input_directory, file_pattern))
        
        if not csv_files:
            print(f"No CSV files found in {input_directory} with pattern {file_pattern}")
            return
        
        print(f"Found {len(csv_files)} CSV files to collate:")
        for file in csv_files:
            print(f"  - {os.path.basename(file)}")
        
        # List to store all dataframes
        dataframes = []
        
        # Read each CSV file and add a source column
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                # Add a source column to identify which file the data came from
                df['Source_File'] = os.path.basename(csv_file)
                dataframes.append(df)
                print(f"Successfully read {len(df)} rows from {os.path.basename(csv_file)}")
            except Exception as e:
                print(f"Error reading {csv_file}: {str(e)}")
                continue
        
        if not dataframes:
            print("No valid CSV files could be read.")
            return
        
        # Combine all dataframes
        print("\nCombining dataframes...")
        combined_df = pd.concat(dataframes, ignore_index=True)
        
        # Remove duplicates if any (optional)
        initial_rows = len(combined_df)
        combined_df = combined_df.drop_duplicates()
        final_rows = len(combined_df)
        
        if initial_rows != final_rows:
            print(f"Removed {initial_rows - final_rows} duplicate rows")
        
        # Save the combined dataframe
        combined_df.to_csv(output_file, index=False)
        
        print(f"\nCollation complete!")
        print(f"Total rows in collated file: {len(combined_df)}")
        print(f"Output saved to: {output_file}")
        
        # Display summary statistics
        print(f"\nSummary by source file:")
        source_counts = combined_df['Source_File'].value_counts()
        for source, count in source_counts.items():
            print(f"  {source}: {count} rows")
        
        # Display column information
        print(f"\nColumns in collated file:")
        for i, col in enumerate(combined_df.columns, 1):
            print(f"  {i:2d}. {col}")
            
    except Exception as e:
        print(f"Error during collation: {str(e)}")

def main():
    """Main function to handle command line arguments and execute collation."""
    parser = argparse.ArgumentParser(description="Collate CSV files from a directory")
    parser.add_argument("input_dir", help="Input directory containing CSV files")
    parser.add_argument("-o", "--output", help="Output CSV file path", 
                       default="collated_output.csv")
    parser.add_argument("-p", "--pattern", help="File pattern to match", 
                       default="*.csv")
    
    args = parser.parse_args()
    
    # Check if input directory exists
    if not os.path.exists(args.input_dir):
        print(f"Error: Input directory '{args.input_dir}' does not exist.")
        return
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Execute collation
    collate_csv_files(args.input_dir, args.output, args.pattern)

if __name__ == "__main__":
    # If no command line arguments provided, use default values for the 06_09 folder
    import sys
    if len(sys.argv) == 1:
        print("No arguments provided. Using default values for 06_09_SEMRUSH_comparison folder:")
        input_dir = "06_09_SEMRUSH_comparison"
        output_file = "06_09_SEMRUSH_comparison_collated.csv"
        
        if os.path.exists(input_dir):
            collate_csv_files(input_dir, output_file)
        else:
            print(f"Default directory '{input_dir}' not found.")
            print("Please provide the correct input directory as an argument.")
            print("Usage: python collate_csv_files.py <input_directory> [-o output_file]")
    else:
        main()













