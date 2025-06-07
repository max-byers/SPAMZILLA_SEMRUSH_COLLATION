import os
import pandas as pd
from datetime import datetime
import logging

def collate_all_accepted_domains():
    """
    Collate all accepted domain list CSV files in the current directory into a single CSV file, removing duplicates.
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[logging.StreamHandler()])
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_files = [f for f in os.listdir(current_dir) if f.endswith('.csv')]
        if not csv_files:
            raise FileNotFoundError("No CSV files found in the current directory.")
        logging.info(f"Found {len(csv_files)} CSV files to process.")
        dfs = []
        for file in csv_files:
            try:
                df = pd.read_csv(os.path.join(current_dir, file))
                logging.info(f"Read {file} with {len(df)} rows.")
                dfs.append(df)
            except Exception as e:
                logging.error(f"Error reading {file}: {str(e)}")
                continue
        if not dfs:
            raise ValueError("No valid CSV files could be read.")
        combined_df = pd.concat(dfs, ignore_index=True)
        logging.info(f"Combined DataFrame has {len(combined_df)} rows.")
        # Try to deduplicate by 'domain' column, fallback to first column if not present
        if 'domain' in combined_df.columns:
            dedup_col = 'domain'
        else:
            dedup_col = combined_df.columns[0]
        original_count = len(combined_df)
        combined_df = combined_df.drop_duplicates(subset=[dedup_col], keep='first')
        logging.info(f"Removed {original_count - len(combined_df)} duplicate domains.")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(current_dir, f'collated_all_accepted_domains_{timestamp}.csv')
        combined_df.to_csv(output_file, index=False)
        logging.info(f"Successfully saved collated data to: {output_file}")
        logging.info(f"Total unique domains: {len(combined_df)}")
        return output_file
    except Exception as e:
        logging.error(f"Error collating accepted domains: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        collate_all_accepted_domains()
    except Exception as e:
        logging.error(f"Script failed: {str(e)}")
        exit(1) 