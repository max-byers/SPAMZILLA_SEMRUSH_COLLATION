"""
Spamzilla CSV Transformer - Complete Solution

This script combines all functionality for transforming Spamzilla CSV export files
into a simplified format with one row per domain, including spam classification.

Usage:
    python main.py input_file.csv [output_file.csv]
    If output_file.csv is not specified, it will be generated as "[date]_spam_checker.csv"
    in the output directory.
"""

import sys
import os
import pandas as pd
import csv
import re
import logging
from datetime import datetime
import shutil
import requests
import time

# Import the new configuration
from config import SpamzillaConfig

# Configure logging
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# --- Google API Configuration ---
API_KEY = "AIzaSyCgisj5V2n6RRfMN_BbmAZ-qk4MWsC1f9A"
CSE_ID = "73119d70c3f674328"

def is_indexed(domain):
    """Check if a domain is indexed in Google."""
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={CSE_ID}&q=site:{domain}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return 1 if "items" in data else 0
        else:
            log_warning(f"Error checking index status for {domain}: {response.status_code}")
            return 0
    except Exception as e:
        log_error(f"Exception checking index status for {domain}: {str(e)}")
        return 0

# Set up logger
logger = logging.getLogger('spamzilla_transformer')
logger.setLevel(LOG_LEVEL)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
logger.addHandler(console_handler)

# Define output directory
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Define spam keywords
SPAM_KEYWORDS = {
    'casino',
    # Pharma & Drugs
    'viagra', 'cialis', 'levitra', 'xanax', 'valium', 'vicodin', 'prozac', 'tamoxifen',
    'methotrexate', 'oxycodone', 'hydrocodone', 'celebrex', 'soma', 'adderall', 'tramadol',
    'trazodone', 'ritalin', 'klonopin', 'ambien', 'lorazepam', 'effexor', 'celexa', 'cymbalta',
    'chantix', 'sertraline', 'lipitor', 'zetia', 'zocor', 'abilify', 'zyprexa', 'nexium',
    'omeprazole', 'cyclobenzaprine', 'clomid', 'crestor', 'fioricet', 'lamictal', 'simvastatin',
    'diovan', 'naproxen', 'neurontin', 'wellbutrin', 'nasonex', 'seroquel', 'topamax', 'prednisone',
    'vistaril', 'ultram', 'phentermine', 'dulcolax', 'promethazine', 'gabapentin', 'fosamax',
    'metformin', 'oxcy', 'oxycontin', 'percocet', 'lotrel', 'hydroxyzine', 'amoxicillin',
    'cephalexin', 'clotrimazole', 'doxycycline',
    # Adult Content
    'porn', 'porno', 'xxx', 'sex', 'orgasm', 'pussy', 'vagina', 'dildo', 'cumshot', 'tits',
    'titties', 'shemale', 'incest', 'escort', 'escorts', 'webcam', 'camgirl', 'camgirls',
    'onlyfans', 'fansly', 'sextape', 'dickpics', 'gangbang', 'bdsm', 'anal', 'fetish',
    'pornstars', 'nudes', 'leaked nudes',
    # Gambling & Betting
    'online games', 'slots', 'slot machine', 'blackjack', "hold'em", 'poker', 'roulette',
    'sports betting', 'betting odds', 'sportsbook', 'crypto casino', 'crypto betting',
    'crypto gambling', 'betfair', 'bookmaker', 'gambling site',
    # Financial / Loan Scams
    'cheap loan', 'cheap meds', 'cheap drugs', 'payday loan', 'payday advance',
    'debt consolidation', 'cash advance', 'free ipad', 'free iphone', 'free gift card',
    'forex signals', 'binary options', 'stock trading tips', 'make money fast',
    'work from home', 'easy loans', 'fast cash', 'mortgage refinancing',
    # Counterfeit & Luxury Brand Spam
    'replica watches', 'fake rolex', 'fake handbags', 'fake passport', 'counterfeit goods',
    'louis vuitton', 'gucci', 'hermes', 'prada', 'chanel', 'burberry', 'rolex replica',
    'oakley replica', 'rayban replica',
    # Tech Spam / Malware
    'hacking tools', 'malware download', 'torrent download', 'phishing site', 'keylogger',
    'trojan virus', 'botnet hosting',
    # Health Spam
    'miracle cure', 'weight loss pills', 'penis enlargement', 'testosterone booster', 'hgh',
    'steroids online', 'sarms', 'peptides', 'detox tea', 'cbd oil', 'kratom', 'delta-8',
    'delta-9', 'ayahuasca retreat', 'shrooms online',
    # Suspicious words
    'drug online', 'no prescription', 'prescription meds', 'pharmacy online',
    'online pharmacy', 'internet pharmacy',
    # Risky Social Trends
    'telegram drugs', 'whatsapp dealer', 'snapchat nudes', 'tiktok followers buy',
    'instagram likes buy',
    # Technical difficulties
    'archive.org snapshots with status 403'
}

POTENTIAL_SPAM_KEYWORDS = {
    'buy cheap', 'click here', 'free trial', 'buy now', 'order now', 'limited offer',
    'processing error', 'insufficient archive.org history'
}

def log_info(message):
    """Log an info message"""
    logger.info(message)

def log_warning(message):
    """Log a warning message"""
    logger.warning(message)

def log_error(message):
    """Log an error message"""
    logger.error(message)

def read_csv_file(file_path, encoding='utf-8'):
    """Read a CSV file with the specified encoding and return a pandas DataFrame."""
    try:
        # Try reading with specified encoding
        df = pd.read_csv(file_path, encoding=encoding)

        # Verify required columns exist
        required_columns = ['Domain Name', 'Spam message']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise ValueError(f"Required columns missing in CSV: {', '.join(missing_columns)}")

        log_info(f"Successfully read CSV with {len(df)} rows and {len(df.columns)} columns")
        log_info(f"Found {df['Domain Name'].nunique()} unique domain(s) in the file")

        return df

    except UnicodeDecodeError:
        log_warning(f"UTF-8 encoding failed, trying alternative encodings...")
        try:
            df = pd.read_csv(file_path, encoding='cp1252')
            log_info("Successfully read file with cp1252 encoding")
            return df
        except Exception as e:
            log_error(f"Failed to read with alternative encoding: {str(e)}")
            raise

    except Exception as e:
        log_error(f"Error reading CSV file: {str(e)}")
        raise

def process_spam_messages(domain_rows):
    """Extract and process all spam messages for a domain."""
    spam_messages = domain_rows['Spam message'].dropna()
    if len(spam_messages) == 0:
        return "", "", 0, ""

    unique_messages = spam_messages.unique()
    filtered_messages = [msg for msg in unique_messages if msg and not pd.isna(msg) and str(msg).strip()]

    flagged_items = []
    message_contents = []
    is_spam = 0
    potential_spam_msg = ""

    for message in filtered_messages:
        message_str = str(message).lower()
        
        # Remove URLs from the message
        message_str = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', message_str)
        message_str = re.sub(r'<http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+>', '', message_str)
        
        # Remove redundant parts
        message_str = re.sub(r'snapshot\s*<\s*text\s*:\s*badword\s*in\s*\(.*?\)', '', message_str)
        message_str = re.sub(r'anchors\s*:\s*badword\s*in\s*\(.*?\)', '', message_str)
        message_str = message_str.strip()
        
        # Check for spam keywords
        for keyword in SPAM_KEYWORDS:
            if keyword.lower() in message_str:
                is_spam = 1
                break
                
        # Check for potential spam keywords
        for keyword in POTENTIAL_SPAM_KEYWORDS:
            if keyword.lower() in message_str and not is_spam:  # Only mark as potential if not already spam
                potential_spam_msg = message_str
                break
        
        brackets = re.findall(r'\[(.*?)\]', message_str)

        if brackets:
            flagged_items.extend(brackets)
            clean_message = re.sub(r'\[.*?\]', '', message_str).strip()
            message_contents.append(clean_message)
        else:
            message_contents.append(message_str)

    unique_flagged = []
    for item in flagged_items:
        if item not in unique_flagged:
            unique_flagged.append(item)

    flagged_str = " | ".join(unique_flagged) if unique_flagged else ""
    message_str = " | ".join(message_contents) if message_contents else ""

    return flagged_str, message_str, is_spam, potential_spam_msg

def consolidate_domains(df):
    """Consolidate multiple rows per domain into a single row."""
    result_df = pd.DataFrame(columns=['Domain Name', 'Flagged', 'Message', 'Spam', 'Potential Spam', 
                                    'Ahrefs DR', 'Ahrefs BL', 'Ahrefs RD', 'Ahrefs Ref IPs', 
                                    'SZ Score', 'Indexed', 'Expiry Date'])
    unique_domains = df['Domain Name'].unique()
    log_info(f"Processing {len(unique_domains)} unique domain(s)")

    for domain in unique_domains:
        if pd.isna(domain) or domain == '':
            log_warning("Skipping empty domain name")
            continue

        domain_rows = df[df['Domain Name'] == domain]
        log_info(f"Processing domain: {domain} with {len(domain_rows)} entries")

        flagged_items, message_content, is_spam, potential_spam = process_spam_messages(domain_rows)
        
        # Get the first non-null value for Ahrefs metrics, SZ Score, and Expiry Date
        ahrefs_dr = ''
        ahrefs_bl = ''
        ahrefs_rd = ''
        ahrefs_ref_ips = ''
        sz_score = ''
        expiry_date = ''
        
        if 'Ahrefs Domain Rating' in domain_rows.columns:
            non_null_dr = domain_rows['Ahrefs Domain Rating'].dropna()
            if not non_null_dr.empty:
                ahrefs_dr = non_null_dr.iloc[0]
                if pd.notna(ahrefs_dr) and float(ahrefs_dr) <= 5:
                    is_spam = 1
                    if not flagged_items:
                        flagged_items = "Low DR"
                    else:
                        flagged_items = f"{flagged_items} | Low DR"

        if 'Ahrefs Backlinks' in domain_rows.columns:
            non_null_bl = domain_rows['Ahrefs Backlinks'].dropna()
            if not non_null_bl.empty:
                ahrefs_bl = non_null_bl.iloc[0]

        if 'Ahrefs Ref Domains' in domain_rows.columns:
            non_null_rd = domain_rows['Ahrefs Ref Domains'].dropna()
            if not non_null_rd.empty:
                ahrefs_rd = non_null_rd.iloc[0]

        if 'Ahrefs Ref IPs' in domain_rows.columns:
            non_null_ips = domain_rows['Ahrefs Ref IPs'].dropna()
            if not non_null_ips.empty:
                ahrefs_ref_ips = non_null_ips.iloc[0]
                
        if 'SZ Score' in domain_rows.columns:
            non_null_score = domain_rows['SZ Score'].dropna()
            if not non_null_score.empty:
                sz_score = non_null_score.iloc[0]

        # Get expiry date
        if 'Expiry Date' in domain_rows.columns:
            non_null_expiry = domain_rows['Expiry Date'].dropna()
            if not non_null_expiry.empty:
                expiry_date = non_null_expiry.iloc[0]

        # Check if domain is indexed
        indexed_status = is_indexed(domain)
        time.sleep(1)  # Respect API rate limits

        result_df = result_df._append({
            'Domain Name': domain,
            'Flagged': flagged_items,
            'Message': message_content,
            'Spam': is_spam,
            'Potential Spam': potential_spam,
            'Ahrefs DR': ahrefs_dr,
            'Ahrefs BL': ahrefs_bl,
            'Ahrefs RD': ahrefs_rd,
            'Ahrefs Ref IPs': ahrefs_ref_ips,
            'SZ Score': sz_score,
            'Indexed': indexed_status,
            'Expiry Date': expiry_date
        }, ignore_index=True)

    return result_df

def write_output_file(df, output_path, encoding='utf-8'):
    """Write the consolidated data to a CSV file."""
    try:
        # If output_path is just a filename, put it in the output directory
        if os.path.dirname(output_path) == '':
            output_path = os.path.join(OUTPUT_DIR, output_path)
            
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            log_info(f"Created output directory: {output_dir}")

        df.to_csv(output_path, index=False, encoding=encoding)

        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            log_info(f"Output file created successfully: {output_path} ({file_size} bytes)")
            log_info(f"Transformed {len(df)} domains to output file")
            return True
        else:
            log_error(f"Failed to create output file: {output_path}")
            return False

    except Exception as e:
        log_error(f"Error writing output file: {str(e)}")
        return False

def find_latest_domain_export_file():
    """Find the latest domain export file in the SPAMZILLA_DOMAIN_EXPORTS directory."""
    try:
        # Define the SPAMZILLA_DOMAIN_EXPORTS directory
        domain_exports_dir = os.path.join(os.path.dirname(__file__), '..', 'SPAMZILLA_DOMAIN_EXPORTS')
        
        if not os.path.exists(domain_exports_dir):
            log_error(f"SPAMZILLA_DOMAIN_EXPORTS directory not found: {domain_exports_dir}")
            return None
            
        # Get all CSV files in the directory
        csv_files = [f for f in os.listdir(domain_exports_dir) if f.endswith('.csv') and not f.endswith('_cleaned.csv')]
        
        if not csv_files:
            log_error("No domain export files found")
            return None
            
        # Sort files by modification time (newest first)
        latest_file = max(csv_files, key=lambda x: os.path.getmtime(os.path.join(domain_exports_dir, x)))
        file_path = os.path.join(domain_exports_dir, latest_file)
        
        log_info(f"Using latest domain export file: {latest_file}")
        return file_path
            
    except Exception as e:
        log_error(f"Error finding domain export file: {str(e)}")
        return None

def read_domain_export_file(file_path, encoding='utf-8'):
    """Read the domain export file containing expiry dates."""
    try:
        df = pd.read_csv(file_path, encoding=encoding)
        
        # Verify required columns exist
        required_columns = ['Name', 'Expires']  # Changed from 'Domain Name' to 'Name' and 'Expiry Date' to 'Expires'
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Required columns missing in domain export CSV: {', '.join(missing_columns)}")
            
        # Rename columns to match our expected format
        df = df.rename(columns={
            'Name': 'Domain Name',
            'Expires': 'Expiry Date'
        })
            
        log_info(f"Successfully read domain export CSV with {len(df)} rows")
        return df
        
    except UnicodeDecodeError:
        log_warning(f"UTF-8 encoding failed for domain export, trying alternative encodings...")
        try:
            df = pd.read_csv(file_path, encoding='cp1252')
            log_info("Successfully read domain export file with cp1252 encoding")
            return df
        except Exception as e:
            log_error(f"Failed to read domain export with alternative encoding: {str(e)}")
            raise
            
    except Exception as e:
        log_error(f"Error reading domain export CSV file: {str(e)}")
        raise

def transform_spamzilla_csv(input_file, output_file):
    """Main function to transform a Spamzilla CSV file."""
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")

        # Read the spam data
        log_info(f"Reading spam CSV file: {input_file}")
        spam_data = read_csv_file(input_file)
        
        # Read the domain export data
        domain_export_file = find_latest_domain_export_file()
        if not domain_export_file:
            raise FileNotFoundError("No domain export file found")
            
        log_info(f"Reading domain export file: {domain_export_file}")
        domain_data = read_domain_export_file(domain_export_file)
        
        # Merge the data
        log_info("Merging spam and domain data...")
        merged_data = pd.merge(
            spam_data,
            domain_data[['Domain Name', 'Expiry Date']],
            on='Domain Name',
            how='left'
        )

        log_info("Consolidating domain data...")
        consolidated_data = consolidate_domains(merged_data)

        log_info(f"Writing output to: {output_file}")
        write_output_file(consolidated_data, output_file)

        log_info("Transformation completed successfully!")
        return True

    except Exception as e:
        log_error(f"Error during transformation: {str(e)}")
        return False

def find_latest_spamzilla_file():
    """Find the latest Spamzilla export file in the SPAM_EXPORTS directory."""
    try:
        # Use the configured input file path
        input_file = SpamzillaConfig.get_input_file_path()
        
        if not os.path.exists(input_file):
            log_error(f"Configured input file not found: {input_file}")
            
            # List available files for user reference
            available_files = SpamzillaConfig.list_available_files()
            log_info(f"Available files: {available_files}")
            
            return None
        
        log_info(f"Using configured input file: {input_file}")
        return input_file
            
    except Exception as e:
        log_error(f"Error finding Spamzilla export file: {str(e)}")
        return None

def main():
    """Parse command line arguments and run the transformation."""
    # If no input file is specified via command line, use the configured file
    if len(sys.argv) < 2:
        input_file = find_latest_spamzilla_file()
        if not input_file:
            log_error("No input file specified and no valid configuration found")
            log_info("Usage: python main.py [input_file.csv] [output_file.csv]")
            log_info("Available files: " + ", ".join(SpamzillaConfig.list_available_files()))
            sys.exit(1)
    else:
        input_file = sys.argv[1]
    
    # Print the input file path at the start
    print(f"Input file: {input_file}")
    log_info(f"Using input file: {input_file}")
    
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        # Generate output filename based on current date
        current_date = datetime.now().strftime("%Y%m%d")
        output_file = f"{current_date}_spam_checker.csv"
        log_info(f"No output file specified, using default: {output_file} in output directory")

    success = transform_spamzilla_csv(input_file, output_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 