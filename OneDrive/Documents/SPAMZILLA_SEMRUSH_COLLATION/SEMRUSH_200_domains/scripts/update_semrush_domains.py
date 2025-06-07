import os
import glob
import pandas as pd
from datetime import datetime
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler()])

def get_export_file():
    """Get the export file from command line argument."""
    logging.info("Starting get_export_file()")
    if len(sys.argv) < 2:
        logging.error("No file path provided as argument")
        raise FileNotFoundError("Please provide the export file path as an argument")
    export_file = sys.argv[1]
    logging.info(f"Checking file path: {export_file}")
    if not os.path.exists(export_file):
        logging.error(f"File not found: {export_file}")
        raise FileNotFoundError(f"Export file not found: {export_file}")
    logging.info(f"Found export file: {export_file}")
    return export_file

def extract_domains(export_file):
    """Extract all domains from the Spamzilla export file."""
    logging.info(f"Starting to extract domains from {export_file}")
    try:
        # Read the CSV file
        logging.info("Reading CSV file...")
        df = pd.read_csv(export_file)
        
        # Use the Name column which contains the domains
        domain_column = 'Name'
        logging.info(f"Looking for column: {domain_column}")
        
        if domain_column not in df.columns:
            logging.error(f"Column {domain_column} not found in CSV. Available columns: {df.columns.tolist()}")
            return []
        
        # Get unique domains
        domains = df[domain_column].unique()
        logging.info(f"Found {len(domains)} unique domains")
        return list(domains)
    except Exception as e:
        logging.error(f"Error reading export file {export_file}: {str(e)}")
        return []

def update_semrush_domains():
    """Update the SEMRUSH_200_domains folder with new domains."""
    logging.info("Starting update_semrush_domains()")
    try:
        # Get the specified export file
        export_file = get_export_file()
        logging.info(f"Using export file: {export_file}")
        
        # Extract all domains
        domains = extract_domains(export_file)
        if not domains:
            logging.error("No domains found in export file")
            return
        
        logging.info(f"Total unique domains found: {len(domains)}")
        
        # Create SEMRUSH_200_domains folder if it doesn't exist
        output_dir = "SEMRUSH_200_domains"
        os.makedirs(output_dir, exist_ok=True)
        logging.info(f"Using output directory: {output_dir}")
        
        # Clear existing files in the folder
        for file in os.listdir(output_dir):
            if file.startswith("domains_") and file.endswith(".txt"):
                file_path = os.path.join(output_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                        logging.info(f"Deleted existing file: {file}")
                except Exception as e:
                    logging.error(f"Error deleting {file_path}: {str(e)}")
        
        # Create text files with 200 domains each
        file_count = 1
        for i in range(0, len(domains), 200):
            chunk = domains[i:i+200]
            file_path = os.path.join(output_dir, f"domains_{file_count}.txt")
            with open(file_path, 'w') as f:
                f.write('\n'.join(chunk))
            logging.info(f"Created file {file_path} with {len(chunk)} domains")
            file_count += 1
        
        logging.info(f"Successfully created {file_count-1} files in {output_dir}")
        logging.info(f"Total domains processed: {len(domains)}")
        
    except Exception as e:
        logging.error(f"Error updating domains: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        update_semrush_domains()
    except Exception as e:
        logging.error(f"Script failed: {str(e)}")
        sys.exit(1) 