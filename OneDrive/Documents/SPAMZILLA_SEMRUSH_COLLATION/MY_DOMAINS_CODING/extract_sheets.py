import pandas as pd
import os
from config import DEFAULT_OUTPUT_DIRECTORY, EVERYTHING_QUALITY_DIR, SUMMARY_DIR, QUALITY_BACKLINK_SETTINGS
from urllib.parse import urlparse
import tldextract

# Set SEMRUSH directory
semrush_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'MY_DOMAINS'))
print(f"Looking for SEMRUSH files in: {semrush_dir}")

# Set output directories
base_output_dir = os.path.dirname(os.path.abspath(__file__))
everything_quality_dir = os.path.join(base_output_dir, EVERYTHING_QUALITY_DIR)
summary_dir = os.path.join(base_output_dir, SUMMARY_DIR)

print(f"Output directories:")
print(f"Base output: {base_output_dir}")
print(f"Everything quality: {everything_quality_dir}")
print(f"Summary: {summary_dir}")

# Create output directories if they don't exist
for directory in [base_output_dir, everything_quality_dir, summary_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

DOMAIN_PRICES = {
    'iprescribeexercise.com': 150,
    'joyofenjoy.com': 315
}

def get_core_domain(url):
    """Extract the core domain from a URL, using only the main TLD"""
    try:
        # Extract domain components
        extracted = tldextract.extract(url)
        # Combine domain and core TLD only
        return f"{extracted.domain}.{extracted.suffix.split('.')[-1]}"
    except:
        return None

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

def process_csv_file(input_file, summary_data):
    """Process a CSV backlink file and append to summary data"""
    try:
        # Read the input file
        df = pd.read_csv(input_file)
        
        # Extract domain from filename (remove -backlinks and any numbers)
        domain = os.path.basename(input_file).split('-backlinks')[0]
        price = DOMAIN_PRICES.get(domain, 'PRICE')
        
        # Create everything CSV in directory
        everything_csv = os.path.join(everything_quality_dir, f'{domain}_{price}_everything.csv')
        df.to_csv(everything_csv, index=False)
        print(f"Created {everything_csv}")
        
        # Calculate everything metrics
        everything_backlinks = len(df)
        everything_domains = df['Source url'].nunique()
        everything_avg_as = df['Page ascore'].mean()
        everything_median_as = df['Page ascore'].median()
        everything_avg_ext_links = df['External links'].mean()
        everything_median_ext_links = df['External links'].median()
        
        # Apply quality filters
        quality_df = df.copy()
        quality_df = quality_df[
            (quality_df['Page ascore'] >= QUALITY_BACKLINK_SETTINGS['MIN_AUTHORITY_SCORE']) &
            (quality_df['External links'] <= QUALITY_BACKLINK_SETTINGS['MAX_EXTERNAL_LINKS'])
        ]
        
        if QUALITY_BACKLINK_SETTINGS['REQUIRE_DOFOLLOW']:
            quality_df = quality_df[~quality_df['Nofollow']]
        
        # Get one backlink per domain (with least external links)
        if not quality_df.empty:
            # Create a list to store unique domains and their best backlinks
            unique_domains = {}  # Dictionary to store domain -> best backlink mapping
            
            # Sort by external links to process lowest first
            quality_df = quality_df.sort_values('External links')
            
            # Loop through each row
            for _, row in quality_df.iterrows():
                # Extract domain from URL
                source_domain = extract_domain_from_url(row['Source url'])
                
                if source_domain:
                    # If domain not in list or current row has fewer external links
                    if source_domain not in unique_domains:
                        unique_domains[source_domain] = row
                    elif row['External links'] < unique_domains[source_domain]['External links']:
                        unique_domains[source_domain] = row
            
            # Convert the dictionary back to a DataFrame
            quality_df = pd.DataFrame(list(unique_domains.values()))
        
        # Calculate quality metrics
        quality_backlinks = len(quality_df)
        quality_domains = quality_df['Source url'].nunique()
        quality_avg_as = quality_df['Page ascore'].mean()
        quality_median_as = quality_df['Page ascore'].median()
        quality_avg_ext_links = quality_df['External links'].mean()
        quality_median_ext_links = quality_df['External links'].median()
        
        # Create quality CSV in directory
        quality_csv = os.path.join(everything_quality_dir, f'{domain}_{price}_quality.csv')
        quality_df.to_csv(quality_csv, index=False)
        print(f"Created {quality_csv}")
        
        # Add to summary data
        summary_data.append({
            'Domain name': f'{domain}-backlinks',
            'Price': price,
            'Everything backlinks': everything_backlinks,
            'Everything domains': everything_domains,
            'Everything avg AS': everything_avg_as,
            'Everything median AS': everything_median_as,
            'Everything avg ext links': everything_avg_ext_links,
            'Everything median ext links': everything_median_ext_links,
            'Quality backlinks': quality_backlinks,
            'Quality domains': quality_domains,
            'Quality avg AS': quality_avg_as,
            'Quality median AS': quality_median_as,
            'Quality avg ext links': quality_avg_ext_links,
            'Quality median ext links': quality_median_ext_links
        })
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")

# Process all CSV files in the SEMRUSH directory
if os.path.exists(semrush_dir):
    files = [f for f in os.listdir(semrush_dir) if f.endswith('.csv')]
    if files:
        print(f"\nProcessing {len(files)} CSV files...")
        summary_data = []  # Initialize summary data list
        for file in files:
            file_path = os.path.join(semrush_dir, file)
            print(f"\nProcessing: {file}")
            process_csv_file(file_path, summary_data)
        
        # Create summary CSV with all domains
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            # Round all numeric columns to 0 decimal places
            for col in summary_df.select_dtypes(include=['float', 'int']).columns:
                summary_df[col] = summary_df[col].round(0).astype('int64')
            summary_csv = os.path.join(summary_dir, 'summary.csv')
            summary_df.to_csv(summary_csv, index=False)
            print(f"\nCreated summary file with {len(summary_data)} domains: {summary_csv}")
    else:
        print(f"No CSV files found in {semrush_dir}")
else:
    print(f"Directory {semrush_dir} not found")

print("\nProcessing complete!") 