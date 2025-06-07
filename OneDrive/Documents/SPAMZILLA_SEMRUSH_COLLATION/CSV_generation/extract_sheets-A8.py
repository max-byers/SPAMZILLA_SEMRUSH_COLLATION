import pandas as pd
import os
from config import DEFAULT_OUTPUT_DIRECTORY, EVERYTHING_QUALITY_DIR, SUMMARY_DIR, QUALITY_BACKLINK_SETTINGS
from urllib.parse import urlparse
import tldextract
from datetime import datetime
import glob
import sys
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
        sys.exit(1)

# Define the domains for each date with their sheet numbers
domains_19_04 = {
    'absolutelyneedlepoint.com': '1',
    'community-of-joy.org': '2',
    'eaze.net': '3',
    'letmedia.org': '4',
    'madnessmusepress.com': '5',
    'mikescourtside.com': '6',
    'squareorganics.com': '7',
    'workingminds.org': '8',
    'forthebenefitofallbeings.com': '1',
    'saveourfaves.org': '2',
    'forallcares.com': '3',
    'mybloggingthing.com': '4',
    'positiveinvest.org': '5',
    'wagbpro.com': '6',
    'wrc-gh.org': '7',
    'learningdevelopmentconference.com': '8',
    'letmefail.com': '9',
    'sandbox2boardroom.com': '10',
    'stockr.net': '11',
    'sfenergywatch.org': '12'
}

domains_27_04 = [
    'visualizeyourlearning.com',
    'socialwod.com',
    'converticulture.com'
]

domains_8_05 = [
    'greatwaterfilters.com.au'
]

# Automatically find the latest *_SEMRUSH_backlinks folder
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
debug_log(f"Parent directory: {parent_dir}")

semrush_folders = sorted(glob.glob(os.path.join(parent_dir, '*_SEMRUSH_backlinks')), key=os.path.getmtime, reverse=True)
if not semrush_folders:
    raise FileNotFoundError('No *_SEMRUSH_backlinks folders found!')
semrush_dir = semrush_folders[0]
# Extract date from folder name (e.g., 17_05_SEMRUSH_backlinks -> 17_05)
date_folder = os.path.basename(semrush_dir).split('_SEMRUSH_backlinks')[0]
debug_log(f"Looking for SEMRUSH files in: {semrush_dir}")
debug_log(f"Using date folder: {date_folder}")

# Set output directories
base_output_dir = os.path.join(parent_dir, DEFAULT_OUTPUT_DIRECTORY)
everything_quality_dir = os.path.join(base_output_dir, EVERYTHING_QUALITY_DIR)
date_quality_dir = os.path.join(everything_quality_dir, date_folder)
summary_dir = os.path.join(base_output_dir, SUMMARY_DIR)

debug_log(f"Output directories:")
debug_log(f"Base output: {base_output_dir}")
debug_log(f"Everything quality: {everything_quality_dir}")
debug_log(f"Date quality: {date_quality_dir}")
debug_log(f"Summary: {summary_dir}")

# Create output directories if they don't exist
for directory in [base_output_dir, everything_quality_dir, summary_dir, date_quality_dir]:
    try:
        if not os.path.exists(directory):
            debug_log(f"Creating directory: {directory}")
            os.makedirs(directory)
            debug_log(f"Successfully created directory: {directory}")
    except Exception as e:
        debug_log(f"Error creating directory {directory}: {str(e)}")
        sys.exit(1)

def get_core_domain(url):
    """Extract the core domain from a URL, using only the main TLD"""
    try:
        # Extract domain components
        extracted = tldextract.extract(url)
        # Combine domain and core TLD only
        return f"{extracted.domain}.{extracted.suffix.split('.')[-1]}"
    except:
        return None

def process_domains(input_file, domains):
    """Process domains from a specific file (CSV or Excel)"""
    summary_data = []
    
    for domain in domains:
        try:
            # Read the input file (CSV or Excel)
            if input_file.endswith('.csv'):
                df = pd.read_csv(input_file)
            else:
                df = pd.read_excel(input_file)
            
            # Create everything CSV
            everything_csv = os.path.join(date_quality_dir, f'{domain}_everything.csv')
            df.to_csv(everything_csv, index=False)
            print(f"Created {everything_csv}")
            
            # Create quality CSV
            quality_csv = os.path.join(date_quality_dir, f'{domain}_quality.csv')
            df.to_csv(quality_csv, index=False)
            print(f"Created {quality_csv}")
            
            # Store metrics for summary after creating files
            try:
                everything_backlinks = len(df)
                everything_domains = df['Source URL'].nunique()
                quality_backlinks = len(df)
                quality_domains = df['Source URL'].nunique()
            except KeyError as e:
                print(f"Warning: Could not calculate metrics for {domain}: {str(e)}")
                everything_backlinks = len(df)
                everything_domains = 0
                quality_backlinks = len(df)
                quality_domains = 0
            
        except Exception as e:
            print(f"Error processing file for {domain}: {str(e)}")
            everything_backlinks = 0
            everything_domains = 0
            quality_backlinks = 0
            quality_domains = 0
            
        # Add to summary data
        summary_data.append({
            'Domain name': f'{domain}-backlinks',
            'Everything backlinks': everything_backlinks,
            'Everything domains': everything_domains,
            'Quality backlinks': quality_backlinks,
            'Quality domains': quality_domains
        })
    
    # Create summary CSV
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        # Use date_folder for the summary file name
        summary_csv = os.path.join(summary_dir, f'{date_folder}_summary.csv')
        summary_df.to_csv(summary_csv, index=False)
        print(f"Created summary file: {summary_csv}")

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

def process_csv_file(input_file, date_quality_dir, summary_data):
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
        
        # Calculate quality metrics
        quality_backlinks = len(quality_df)
        quality_domains = quality_df[source_url_col].nunique() if source_url_col and not quality_df.empty else 0
        
        # Only create output files and add to summary if there are more than 5 quality backlinks
        if quality_backlinks > 5:
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
            debug_log(f"Skipping {domain} as it has only {quality_backlinks} quality backlinks (minimum required: 6)")
        
    except Exception as e:
        debug_log(f"Error processing file {input_file}: {str(e)}")
        return

def main():
    try:
        # Set up argument parser
        parser = argparse.ArgumentParser(description='Process SEMRUSH backlink files')
        parser.add_argument('input_dir', help='Input directory containing SEMRUSH backlink files')
        parser.add_argument('output_dir', help='Output directory for processed files')
        args = parser.parse_args()

        # Convert paths to absolute paths
        input_dir = os.path.abspath(args.input_dir)
        output_dir = os.path.abspath(args.output_dir)
        
        # Extract date from input directory name
        date_folder = os.path.basename(input_dir).split('_SEMRUSH_backlinks')[0]
        debug_log(f"Using date folder: {date_folder}")

        # Set up output directories
        date_quality_dir = os.path.join(output_dir, date_folder)
        summary_dir = os.path.join(os.path.dirname(output_dir), 'SUMMARY')

        # Create all necessary directories
        for directory in [date_quality_dir, summary_dir]:
            ensure_directory_exists(directory)

        # Get all CSV files in the input directory
        csv_files = glob.glob(os.path.join(input_dir, '*.csv'))
        debug_log(f"Found {len(csv_files)} CSV files to process")
        
        if not csv_files:
            debug_log("No CSV files found to process!")
            return
        
        summary_data = []
        
        # Process each CSV file
        for csv_file in csv_files:
            debug_log(f"\nProcessing: {os.path.basename(csv_file)}")
            process_csv_file(csv_file, date_quality_dir, summary_data)
        
        # Create summary CSV
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            summary_csv = os.path.join(summary_dir, f'{date_folder}_summary.csv')
            debug_log(f"Creating summary file: {summary_csv}")
            summary_df.to_csv(summary_csv, index=False)
            debug_log(f"Successfully created summary file with {len(summary_data)} domains")
        
        debug_log("\nProcessing complete!")
        
    except Exception as e:
        debug_log(f"Error in main process: {str(e)}")
        raise

if __name__ == "__main__":
    main() 