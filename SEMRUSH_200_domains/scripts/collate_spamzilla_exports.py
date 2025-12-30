import os
import pandas as pd
import glob
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler()])

def collate_spamzilla_exports():
    """
    Collate all Spamzilla export files from the SPAMZILLA_DOMAIN_EXPORTS folder
    into a single CSV file, removing duplicates.
    """
    try:
        # Get the path to the SPAMZILLA_DOMAIN_EXPORTS folder
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        exports_dir = os.path.join(parent_dir, 'SPAMZILLA_DOMAIN_EXPORTS')
        
        if not os.path.exists(exports_dir):
            raise FileNotFoundError(f"SPAMZILLA_DOMAIN_EXPORTS directory not found at: {exports_dir}")
        
        # Get all CSV files in the directory
        csv_files = glob.glob(os.path.join(exports_dir, '*.csv'))
        
        if not csv_files:
            raise FileNotFoundError("No CSV files found in the SPAMZILLA_DOMAIN_EXPORTS directory")
        
        logging.info(f"Found {len(csv_files)} CSV files to process")
        
        # Read and combine all CSV files
        dfs = []
        for file in csv_files:
            try:
                df = pd.read_csv(file)
                logging.info(f"Successfully read {file} with {len(df)} rows")
                dfs.append(df)
            except Exception as e:
                logging.error(f"Error reading {file}: {str(e)}")
                continue
        
        if not dfs:
            raise ValueError("No valid CSV files could be read")
        
        # Combine all DataFrames
        combined_df = pd.concat(dfs, ignore_index=True)
        logging.info(f"Combined DataFrame has {len(combined_df)} rows")
        
        # Remove duplicates based on domain name
        original_count = len(combined_df)
        combined_df = combined_df.drop_duplicates(subset=['Name'], keep='first')
        logging.info(f"Removed {original_count - len(combined_df)} duplicate domains")
        
        # Generate output filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(current_dir, f'collated_spamzilla_exports_{timestamp}.csv')
        
        # Save the combined data
        combined_df.to_csv(output_file, index=False)
        logging.info(f"Successfully saved collated data to: {output_file}")
        
        # Print summary
        logging.info("\n=== Summary ===")
        logging.info(f"Total files processed: {len(csv_files)}")
        logging.info(f"Total unique domains: {len(combined_df)}")
        logging.info(f"Output file: {output_file}")
        
        return output_file
        
    except Exception as e:
        logging.error(f"Error collating Spamzilla exports: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        collate_spamzilla_exports()
    except Exception as e:
        logging.error(f"Script failed: {str(e)}")
        exit(1) 