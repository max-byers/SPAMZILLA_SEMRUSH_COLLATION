import pandas as pd
import os
from config import DEFAULT_OUTPUT_DIRECTORY, EVERYTHING_QUALITY_DIR, SUMMARY_DIR, QUALITY_BACKLINK_SETTINGS, SEMRUSH_BACKLINK_FOLDER
from urllib.parse import urlparse
import glob
import argparse

# Add debug logging
def debug_log(message):
    print(f"[DEBUG] {message}")

def ensure_directory_exists(directory):
    """Create directory if it doesn't exist"""
    try:
        if not os.path.exists(directory):
            debug_log(f"Creating directory: {directory}")
            os.makedirs(directory)
            debug_log(f"Successfully created directory: {directory}")
    except Exception as e:
        debug_log(f"Error creating directory {directory}: {str(e)}")
        exit(1)

def extract_domain_from_url(url):
    """Extract domain name from URL, stopping at first semantic sign"""
    try:
        # Parse the URL
        parsed = urlparse(url)
        # Get the netloc (domain part)
        domain = parsed.netloc
        
        # Remove www. if present
        if domain.startswith('www.'):
            domain = domain[4:]
            
        # Find the last period before the TLD
        parts = domain.split('.')
        if len(parts) >= 2:
            # Get the core domain (everything before the TLD)
            core_domain = parts[-2]
            # Get the TLD
            tld = parts[-1]
            return f"{core_domain}.{tld}"
        return domain
    except:
        return None

def process_csv_file(input_file, date_quality_dir, summary_data, leftout_domains):
    """Process a CSV backlink file and append to summary data"""
    try:
        # Skip comparison files
        if 'comparison' in input_file.lower():
            debug_log(f"Skipping comparison file: {input_file}")
            return

        debug_log(f"Processing file: {input_file}")
        # Read the input file
        df = pd.read_csv(input_file)
        debug_log(f"Successfully read CSV with {len(df)} rows")
        
        # Extract domain from filename (remove -backlinks and any numbers)
        domain = os.path.basename(input_file).split('-backlinks')[0]
        debug_log(f"Processing domain: {domain}")
        
        # Calculate everything metrics
        everything_backlinks = len(df)
        
        # Handle different column name variations
        source_url_col = None
        for col in ['Source url', 'Source URL', 'Source_url', 'source_url']:
            if col in df.columns:
                source_url_col = col
                break
                
        if source_url_col is None:
            debug_log(f"Warning: Could not find source URL column in {input_file}")
            everything_domains = 0
        else:
            everything_domains = df[source_url_col].nunique()
        
        # Apply quality filters
        quality_df = df.copy()
        
        # Handle different column name variations for quality filters
        ascore_col = None
        for col in ['Page ascore', 'Page Ascore', 'Page_ascore', 'page_ascore']:
            if col in df.columns:
                ascore_col = col
                break
                
        ext_links_col = None
        for col in ['External links', 'External Links', 'External_links', 'external_links']:
            if col in df.columns:
                ext_links_col = col
                break
                
        nofollow_col = None
        for col in ['Nofollow', 'nofollow', 'No Follow', 'no_follow']:
            if col in df.columns:
                nofollow_col = col
                break
        
        if ascore_col and ext_links_col:
            quality_df = quality_df[
                (quality_df[ascore_col] >= QUALITY_BACKLINK_SETTINGS['MIN_AUTHORITY_SCORE']) &
                (quality_df[ext_links_col] <= QUALITY_BACKLINK_SETTINGS['MAX_EXTERNAL_LINKS'])
            ]
            
            if nofollow_col and QUALITY_BACKLINK_SETTINGS['REQUIRE_DOFOLLOW']:
                quality_df = quality_df[~quality_df[nofollow_col]]
        
        # Calculate quality backlinks BEFORE deduplication (total number of quality backlinks)
        quality_backlinks = len(quality_df)
        
        # Get one backlink per domain (with least external links)
        if not quality_df.empty and source_url_col and ext_links_col:
            # Create a list to store unique domains and their best backlinks
            unique_domains = {}  # Dictionary to store domain -> best backlink mapping
            
            # Sort by external links to process lowest first
            quality_df = quality_df.sort_values(ext_links_col)
            
            # Loop through each row
            for _, row in quality_df.iterrows():
                # Extract domain from URL
                source_domain = extract_domain_from_url(row[source_url_col])
                
                if source_domain:
                    # If domain not in list or current row has fewer external links
                    if source_domain not in unique_domains:
                        unique_domains[source_domain] = row
                    elif row[ext_links_col] < unique_domains[source_domain][ext_links_col]:
                        unique_domains[source_domain] = row
            
            # Convert the dictionary back to a DataFrame
            quality_df = pd.DataFrame(list(unique_domains.values()))
        
        # Calculate quality domains AFTER deduplication (number of unique referring domains)
        quality_domains = quality_df[source_url_col].nunique() if source_url_col and not quality_df.empty else 0
        
        # Only create output files and add to summary if there are more than 10 quality backlinks
        if quality_backlinks > 10:
            # Create everything CSV in date-based directory
            everything_csv = os.path.join(date_quality_dir, f'{domain}_everything.csv')
            debug_log(f"Creating everything CSV: {everything_csv}")
            df.to_csv(everything_csv, index=False)
            debug_log(f"Successfully created everything CSV")
            
            # Create quality CSV in date-based directory
            quality_csv = os.path.join(date_quality_dir, f'{domain}_quality.csv')
            debug_log(f"Creating quality CSV: {quality_csv}")
            quality_df.to_csv(quality_csv, index=False)
            debug_log(f"Successfully created quality CSV")
            
            # Add to summary data
            summary_data.append({
                'Domain name': f'{domain}-backlinks',
                'Everything backlinks': everything_backlinks,
                'Everything domains': everything_domains,
                'Quality backlinks': quality_backlinks,
                'Quality domains': quality_domains
            })
            debug_log(f"Added summary data for {domain}")
        else:
            debug_log(f"Skipping {domain} as it has only {quality_backlinks} quality backlinks (minimum required: 11)")
            leftout_domains.append(f"{domain} - Quality backlinks: {quality_backlinks}")
        
    except Exception as e:
        debug_log(f"Error processing file {input_file}: {str(e)}")
        return

def main():
    try:
        # Set up argument parser
        parser = argparse.ArgumentParser(description='Process SEMRUSH backlink files')
        parser.add_argument('--input_dir', help='Input directory containing SEMRUSH backlink files (if not provided, uses SEMRUSH_BACKLINK_FOLDER from config.py)')
        parser.add_argument('--output_dir', help='Output directory for processed files (if not provided, uses DEFAULT_OUTPUT_DIRECTORY from config.py)')
        args = parser.parse_args()

        # Use config value if not provided as argument
        input_dir = os.path.abspath(args.input_dir) if args.input_dir else os.path.abspath(SEMRUSH_BACKLINK_FOLDER)
        output_dir = os.path.abspath(args.output_dir) if args.output_dir else os.path.abspath(DEFAULT_OUTPUT_DIRECTORY)
        
        # Extract date from input directory name
        date_folder = os.path.basename(input_dir).split('_SEMRUSH_backlinks')[0]
        debug_log(f"Using date folder: {date_folder}")

        # Set up output directories
        date_quality_dir = os.path.join(output_dir, date_folder)
        summary_dir = os.path.join(os.path.dirname(output_dir), 'SUMMARY')
        text_files_dir = os.path.join(summary_dir, 'text_files')

        # Create all necessary directories
        for directory in [date_quality_dir, summary_dir, text_files_dir]:
            ensure_directory_exists(directory)

        # Get all CSV files in the input directory
        csv_files = glob.glob(os.path.join(input_dir, '*.csv'))
        debug_log(f"Found {len(csv_files)} CSV files to process")
        
        if not csv_files:
            debug_log("No CSV files found to process!")
            return
        
        summary_data = []
        leftout_domains = []
        
        # Process each CSV file
        for csv_file in csv_files:
            debug_log(f"\nProcessing: {os.path.basename(csv_file)}")
            process_csv_file(csv_file, date_quality_dir, summary_data, leftout_domains)
        
        # Create summary CSV
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            summary_csv = os.path.join(summary_dir, f'{date_folder}_summary.csv')
            debug_log(f"Creating summary file: {summary_csv}")
            summary_df.to_csv(summary_csv, index=False)
            debug_log(f"Successfully created summary file with {len(summary_data)} domains")
        
        # Create text file for left out domains
        if leftout_domains:
            leftout_file = os.path.join(text_files_dir, f'{date_folder}_domains_leftout.txt')
            debug_log(f"Creating left out domains file: {leftout_file}")
            with open(leftout_file, 'w') as f:
                f.write('\n'.join(leftout_domains))
            debug_log(f"Successfully created left out domains file with {len(leftout_domains)} domains")
        
        debug_log("\nProcessing complete!")
        
    except Exception as e:
        debug_log(f"Error in main process: {str(e)}")
        raise

if __name__ == "__main__":
    main() 