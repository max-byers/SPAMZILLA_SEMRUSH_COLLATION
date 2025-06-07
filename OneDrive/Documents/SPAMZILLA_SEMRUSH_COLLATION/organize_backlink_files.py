import os
import shutil
import pandas as pd
from pathlib import Path
import argparse

def process_input_files(input_folder, output_folder):
    # Create output directory if it doesn't exist
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Process each file in input folder
    input_path = Path(input_folder)
    for file in input_path.glob('*.csv'):
        # Copy file to output folder
        shutil.copy2(str(file), str(output_path / file.name))
        print(f"Processed: {file.name}")

def organize_files_by_price():
    # Define paths
    base_dir = Path('BACKLINK_CSV_FILES')
    price_analysis_file = 'output_domain_price_analysis/collated_price_analysis.csv'
    source_dirs = [base_dir / 'EVERYTHING_QUALITY', base_dir / 'NO_PRICE_EVERYTHING_QUALITY']
    price_dir = base_dir / 'PRICE_EVERYTHING_QUALITY'
    no_price_dir = base_dir / 'NO_PRICE_EVERYTHING_QUALITY'

    # Create directories if they don't exist
    price_dir.mkdir(exist_ok=True)
    no_price_dir.mkdir(exist_ok=True)

    # Read price analysis CSV
    df = pd.read_csv(price_analysis_file)

    # Create a dictionary of domain to price mapping
    domain_prices = {}
    for _, row in df.iterrows():
        domain = row['Name']
        price = row['Price']
        if pd.notna(price) and price > 0:
            domain_prices[domain] = price

    # Process files from both source directories
    for source_dir in source_dirs:
        if not source_dir.exists():
            continue
            
        # Get list of files in source directory
        files = list(source_dir.glob('*.csv'))

        # Process each file
        for file in files:
            domain = file.stem.split('_')[0]  # Get domain from filename
            domain = domain.replace('-backlinks', '')  # Handle files with -backlinks suffix
            
            if domain in domain_prices:
                # File has a price
                price = domain_prices[domain]
                new_filename = f"{domain}_{price}_{file.name}"
                destination = price_dir / new_filename
            else:
                # File has no price
                destination = no_price_dir / file.name
            
            # Move file to appropriate directory
            shutil.move(str(file), str(destination))

    # Sort files in price directory by price (descending)
    price_files = list(price_dir.glob('*.csv'))
    price_files.sort(key=lambda x: float(x.stem.split('_')[1]), reverse=True)

    print("File organization complete!")
    print(f"Files with prices moved to: {price_dir}")
    print(f"Files without prices moved to: {no_price_dir}")

def main():
    parser = argparse.ArgumentParser(description='Process and organize backlink files')
    parser.add_argument('--input_folder', required=True, help='Input folder containing SEMRUSH backlink files')
    parser.add_argument('--output_folder', required=True, help='Output folder for processed files')
    args = parser.parse_args()

    # First process input files
    process_input_files(args.input_folder, args.output_folder)
    
    # Then organize files by price
    organize_files_by_price()

if __name__ == "__main__":
    main() 