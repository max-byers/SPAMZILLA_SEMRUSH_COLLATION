import os
import pandas as pd
import glob
from datetime import datetime
import logging
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler()])

def collate_previous_domains():
    """
    Collate all previously analyzed domain lists from the domain_analyzer/DOMAIN_LIST folder
    into a single CSV file, removing duplicates.
    """
    try:
        # Get the paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        domain_list_dir = os.path.join(parent_dir, 'domain_analyzer', 'DOMAIN_LIST')
        output_dir = os.path.join(current_dir, 'PREVIOUSLY_ANALYSED_DOMAINS')
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logging.info(f"Created directory: {output_dir}")
        
        # Get all date folders
        date_folders = [f for f in os.listdir(domain_list_dir) 
                       if os.path.isdir(os.path.join(domain_list_dir, f))]
        
        if not date_folders:
            raise FileNotFoundError("No date folders found in the DOMAIN_LIST directory")
        
        logging.info(f"Found {len(date_folders)} date folders to process")
        
        # Process each date folder
        dfs = []
        for date_folder in date_folders:
            accepted_file = os.path.join(domain_list_dir, date_folder, f'accepted_domains_list_{date_folder.replace("-", "")}.csv')
            
            if os.path.exists(accepted_file):
                try:
                    # Copy the file to the output directory
                    shutil.copy2(accepted_file, os.path.join(output_dir, os.path.basename(accepted_file)))
                    logging.info(f"Copied {accepted_file}")
                    
                    # Read the file
                    df = pd.read_csv(accepted_file)
                    logging.info(f"Successfully read {accepted_file} with {len(df)} rows")
                    dfs.append(df)
                except Exception as e:
                    logging.error(f"Error processing {accepted_file}: {str(e)}")
                    continue
        
        if not dfs:
            raise ValueError("No valid CSV files could be read")
        
        # Combine all DataFrames
        combined_df = pd.concat(dfs, ignore_index=True)
        logging.info(f"Combined DataFrame has {len(combined_df)} rows")
        
        # Remove duplicates based on domain name
        original_count = len(combined_df)
        combined_df = combined_df.drop_duplicates(subset=['domain'], keep='first')
        logging.info(f"Removed {original_count - len(combined_df)} duplicate domains")
        
        # Generate output filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(output_dir, f'collated_previous_domains_{timestamp}.csv')
        
        # Save the combined data
        combined_df.to_csv(output_file, index=False)
        logging.info(f"Successfully saved collated data to: {output_file}")
        
        # Print summary
        logging.info("\n=== Summary ===")
        logging.info(f"Total folders processed: {len(date_folders)}")
        logging.info(f"Total unique domains: {len(combined_df)}")
        logging.info(f"Output file: {output_file}")
        
        return output_file
        
    except Exception as e:
        logging.error(f"Error collating previous domains: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        collate_previous_domains()
    except Exception as e:
        logging.error(f"Script failed: {str(e)}")
        exit(1) 