import os
import glob
import pandas as pd
from datetime import datetime, timedelta
import sys
import logging
from pathlib import Path
import time
import argparse

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler()])

# Define directory structure
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
REPORTS_DIR = os.path.join(ROOT_DIR, 'reports')
DOMAINS_DIR = os.path.join(ROOT_DIR, 'domains')
DATA_DIR = os.path.join(ROOT_DIR, 'data')

# Create output directories if they don't exist
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(DOMAINS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Dodgy keywords dictionary
DODGY_KEYWORDS = {
    'Adult': [
        'xxx', 'porn', 'adult', 'sex', 'escort', 'dating', 'nude', 'naked', 'viagra', 'cialis'
    ],
    'Gambling': [
        'bet', 'casino', 'poker', 'lotto', 'lottery', 'bingo', 'jackpot', 'gamble', 'wager', 'bookie', 'slot'
    ],
    'Pharmaceutical': [
        'pharmacy', 'drug', 'prescription', 'medication', 'pill', 'tablet', 'capsule', 'antibiotic', 'painkiller', 'supplement'
    ]
}

def verify_output_files(output_dir, dodgy_domains):
    """Verify that output files don't contain any dodgy domains."""
    logging.info("\n=== Starting Output Verification ===")
    total_domains_in_files = 0
    dodgy_domains_found = 0
    
    for file in os.listdir(DOMAINS_DIR):
        if file.startswith("domains_") and file.endswith(".txt"):
            file_path = os.path.join(DOMAINS_DIR, file)
            with open(file_path, 'r') as f:
                domains = f.read().splitlines()
                total_domains_in_files += len(domains)
                
                # Check for any dodgy domains
                for domain in domains:
                    if domain.lower() in dodgy_domains:
                        dodgy_domains_found += 1
                        logging.error(f"Found dodgy domain in {file}: {domain}")
    
    logging.info(f"Verification Results:")
    logging.info(f"Total domains in output files: {total_domains_in_files}")
    logging.info(f"Dodgy domains found in output: {dodgy_domains_found}")
    logging.info("=== Verification Complete ===\n")
    
    return dodgy_domains_found == 0

def parse_date(date_str):
    """Parse date string in format DD/MM."""
    try:
        day, month = map(int, date_str.split('/'))
        current_year = datetime.now().year
        return datetime(current_year, month, day)
    except ValueError as e:
        logging.error(f"Invalid date format: {date_str}. Expected format: DD/MM")
        raise

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

def get_latest_collated_file():
    """Get the most recent collated Spamzilla exports file."""
    collated_files = glob.glob(os.path.join(DATA_DIR, 'collated_spamzilla_exports_*.csv'))
    if not collated_files:
        logging.warning("No collated Spamzilla exports file found")
        return None
    return max(collated_files, key=os.path.getctime)

def get_previously_sold_domains():
    """Get set of domains that were previously sold from the collated file."""
    collated_file = get_latest_collated_file()
    if not collated_file:
        return set()
    
    try:
        df = pd.read_csv(collated_file)
        return set(df['Name'].str.lower())
    except Exception as e:
        logging.error(f"Error reading collated file: {str(e)}")
        return set()

def analyze_domains(df):
    """Analyze domains for dodgy keywords."""
    logging.info("Starting domain analysis")
    start_time = time.time()
    
    total_domains = len(df)
    unsuitable_domains = 0
    category_matches = {k: 0 for k in DODGY_KEYWORDS}
    detailed_results = []

    for _, row in df.iterrows():
        domain = str(row['Name']).lower()
        matched_keywords = []
        matched_categories = set()
        
        for category, keywords in DODGY_KEYWORDS.items():
            for word in keywords:
                if word in domain:
                    matched_keywords.append(word)
                    matched_categories.add(category)
        
        if matched_keywords:
            unsuitable_domains += 1
            for category in matched_categories:
                category_matches[category] += 1
            detailed_results.append({
                'domain': domain,
                'matched_keywords': ', '.join(matched_keywords),
                'matched_categories': ', '.join(matched_categories)
            })

    end_time = time.time()
    analysis_time = end_time - start_time
    
    logging.info(f"Analysis completed in {analysis_time:.2f} seconds")
    logging.info(f"Processed {total_domains} domains at {total_domains/analysis_time:.2f} domains/second")

    return {
        'total_domains': total_domains,
        'unsuitable_domains': unsuitable_domains,
        'category_matches': category_matches,
        'detailed_results': detailed_results
    }

def generate_report(results, output_dir, df, start_date, end_date):
    """Generate a report of the analysis."""
    date_str = datetime.now().strftime('%Y-%m-%d')
    report_file = os.path.join(REPORTS_DIR, f"{date_str}_domain_analysis_report.txt")
    
    # Get today's date and calculate dates for next 7 days
    today = datetime.now().date()
    next_week = today + timedelta(days=7)
    
    # Count domains expiring each day in the next week
    daily_expiry_counts = {}
    for i in range(8):  # Include today and next 7 days
        check_date = today + timedelta(days=i)
        daily_expiry_counts[check_date] = 0
    
    # Count clean domains expiring each day
    dodgy_domains = {entry['domain'] for entry in results['detailed_results']}
    
    # Count domains with excessive drops
    excessive_drops_count = 0
    for _, row in df.iterrows():
        domain = str(row['Name']).lower()
        sz_drops = row['SZ Drops']
        if not pd.isna(sz_drops) and sz_drops > 2:
            excessive_drops_count += 1
    
    # Get previously sold domains
    previously_sold_domains = get_previously_sold_domains()
    previously_sold_count = sum(1 for _, row in df.iterrows() if str(row['Name']).lower() in previously_sold_domains)
    
    # Count domains by auction source
    auction_sources = df['Source'].value_counts()
    
    # Count previously sold domains by auction source
    previously_sold_sources = df[df['Name'].str.lower().isin(previously_sold_domains)]['Source'].value_counts()
    
    # Count previously sold domains by expiration date
    previously_sold_expiry = df[df['Name'].str.lower().isin(previously_sold_domains)]['Expires'].dt.date.value_counts().sort_index()
    
    # Get clean domains (those that will be in text files)
    clean_domains = []
    outside_date_range_count = 0
    age_drop_exclusion_count = 0
    
    for _, row in df.iterrows():
        domain = str(row['Name']).lower()
        sz_drops = row['SZ Drops']
        expiry_date = row['Expires']
        age = row['Age']
        
        # Check if domain is clean (not dodgy)
        is_clean = domain not in dodgy_domains
        
        # Check if expiry_date is valid
        if pd.isnull(expiry_date):
            continue
        
        # Create date objects for comparison
        expiry_date_obj = expiry_date.date()
        # Swap day and month for comparison
        start_date_obj = datetime(2025, start_date.day, start_date.month).date()
        end_date_obj = datetime(2025, end_date.day, end_date.month).date()
        
        # Check if domain expires within the specified date range (inclusive)
        expires_in_range = start_date_obj <= expiry_date_obj <= end_date_obj
        
        # Check SZ Drops criteria
        sz_drops_ok = pd.isna(sz_drops) or sz_drops <= 2
        
        # Check Age/Drop ratio exclusion
        age_drop_exclude = False
        if not pd.isna(age) and not pd.isna(sz_drops) and sz_drops != 0:
            try:
                ratio = float(age) / float(sz_drops)
                if ratio <= 2:
                    age_drop_exclude = True
            except Exception:
                pass
        
        # Remove previously_sold exclusion
        if is_clean and expires_in_range and sz_drops_ok and not age_drop_exclude:
            clean_domains.append({'Name': row['Name'], 'Expires': row['Expires']})
        elif is_clean and sz_drops_ok and not expires_in_range:
            outside_date_range_count += 1
        elif is_clean and expires_in_range and sz_drops_ok and age_drop_exclude:
            age_drop_exclusion_count += 1
    
    # Get expiration date range for clean domains
    clean_domains_df = pd.DataFrame(clean_domains)
    if not clean_domains_df.empty and 'Expires' in clean_domains_df.columns:
        clean_domains_expiry = clean_domains_df['Expires'].dt.date.value_counts().sort_index()
    else:
        clean_domains_expiry = pd.Series(dtype=int)
    
    for _, row in df.iterrows():
        domain = str(row['Name']).lower()
        if domain not in dodgy_domains:
            expiry_date = row['Expires'].date()
            if today <= expiry_date <= next_week:
                daily_expiry_counts[expiry_date] += 1
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"Domain Analysis Report - {date_str}\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Total Domains Analyzed: {results['total_domains']}\n")
        f.write(f"Unsuitable Domains: {results['unsuitable_domains']}\n")
        f.write(f"Percentage Unsuitable: {(results['unsuitable_domains'] / results['total_domains'] * 100):.2f}%\n")
        f.write(f"Domains with Excessive Drops (>2): {excessive_drops_count}\n")
        f.write(f"Percentage with Excessive Drops: {(excessive_drops_count / results['total_domains'] * 100):.2f}%\n")
        f.write(f"Previously Sold Domains: {previously_sold_count}\n")
        f.write(f"Percentage Previously Sold: {(previously_sold_count / results['total_domains'] * 100):.2f}%\n")
        if start_date is not None and end_date is not None:
            f.write(f"Domains Outside Date Range ({start_date.strftime('%d/%m')} - {end_date.strftime('%d/%m')}): {outside_date_range_count}\n")
            f.write(f"Percentage Outside Date Range: {(outside_date_range_count / results['total_domains'] * 100):.2f}%\n\n")
        else:
            f.write(f"Domains Outside Date Range: {outside_date_range_count}\n")
            f.write(f"Percentage Outside Date Range: {(outside_date_range_count / results['total_domains'] * 100):.2f}%\n\n")
        
        f.write("Category Breakdown:\n")
        for category, count in results['category_matches'].items():
            f.write(f"{category}: {count} domains\n")
        
        f.write("\nDaily Expiration Breakdown (Next 7 Days):\n")
        f.write("-" * 50 + "\n")
        for date, count in sorted(daily_expiry_counts.items()):
            f.write(f"{date}: {count} domains\n")
        
        # Add detailed breakdown of excluded domains
        f.write("\nDetailed Domain Exclusion Breakdown:\n")
        f.write("-" * 50 + "\n")
        f.write(f"1. Dodgy Keywords: {results['unsuitable_domains']} domains\n")
        f.write(f"2. Excessive Drops: {excessive_drops_count} domains\n")
        f.write(f"3. Previously Sold: {previously_sold_count} domains\n")
        f.write(f"4. Outside Date Range: {outside_date_range_count} domains\n")
        f.write(f"5. Age/Drop Ratio <= 2: {age_drop_exclusion_count} domains\n")
        f.write(f"6. Clean Domains Available: {len(df) - results['unsuitable_domains'] - excessive_drops_count - previously_sold_count - outside_date_range_count - age_drop_exclusion_count} domains\n")
        
        # Add auction source breakdown
        f.write("\nAuction Source Breakdown (All Domains):\n")
        f.write("-" * 50 + "\n")
        for source, count in auction_sources.items():
            percentage = (count / len(df) * 100)
            f.write(f"{source}: {count} domains ({percentage:.2f}%)\n")
            
        # Add previously sold domains auction source breakdown
        f.write("\nAuction Source Breakdown (Previously Sold Domains):\n")
        f.write("-" * 50 + "\n")
        for source, count in previously_sold_sources.items():
            percentage = (count / previously_sold_count * 100)
            f.write(f"{source}: {count} domains ({percentage:.2f}%)\n")
            
        # Add previously sold domains expiration date breakdown
        f.write("\nExpiration Date Breakdown (Previously Sold Domains):\n")
        f.write("-" * 50 + "\n")
        for date, count in previously_sold_expiry.items():
            percentage = (count / previously_sold_count * 100)
            f.write(f"{date}: {count} domains ({percentage:.2f}%)\n")
            
        # Add clean domains expiration date breakdown
        f.write("\nExpiration Date Breakdown (Domains in Text Files):\n")
        f.write("-" * 50 + "\n")
        for date, count in clean_domains_expiry.items():
            percentage = (count / len(clean_domains) * 100)
            f.write(f"{date}: {count} domains ({percentage:.2f}%)\n")
        
        # Add date range summary for clean domains
        if not clean_domains_df.empty and 'Expires' in clean_domains_df.columns:
            earliest_date = clean_domains_df['Expires'].min().date()
            latest_date = clean_domains_df['Expires'].max().date()
            f.write(f"\nDate Range for Domains in Text Files:\n")
            f.write("-" * 50 + "\n")
            f.write(f"Earliest Expiration: {earliest_date}\n")
            f.write(f"Latest Expiration: {latest_date}\n")
    
    logging.info(f"Report generated: {report_file}")
    return report_file

def is_expiring_within_week(expiry_date):
    """Check if a domain expires within the next week."""
    today = datetime.now()
    week_from_now = today + timedelta(days=7)
    return today <= expiry_date <= week_from_now

def process_domains():
    """Main function to process domains."""
    try:
        export_file = get_export_file()
        df = pd.read_csv(export_file)
        
        # Convert date columns to datetime
        df['Expires'] = pd.to_datetime(df['Expires'], format='%d/%m/%Y', errors='coerce')
        
        # Get date range from command line arguments
        if len(sys.argv) < 4:
            raise ValueError("Please provide start and end dates in DD/MM format")
        
        start_date = parse_date(sys.argv[2])
        end_date = parse_date(sys.argv[3])
        
        # Analyze domains
        results = analyze_domains(df)
        
        # Generate report
        generate_report(results, REPORTS_DIR, df, start_date, end_date)
        
        # Verify output files
        dodgy_domains = {entry['domain'] for entry in results['detailed_results']}
        if not verify_output_files(DOMAINS_DIR, dodgy_domains):
            logging.error("Verification failed - dodgy domains found in output files")
            return
        
        logging.info("Processing completed successfully")
        
    except Exception as e:
        logging.error(f"Error processing domains: {str(e)}")
        raise

if __name__ == "__main__":
    process_domains() 