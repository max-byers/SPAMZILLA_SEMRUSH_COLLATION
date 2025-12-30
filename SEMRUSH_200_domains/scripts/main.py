import os
import glob
import pandas as pd
from datetime import datetime, timedelta
import logging
import time

from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

# Directory setup
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
REPORTS_DIR = os.path.join(ROOT_DIR, 'reports')
DOMAINS_DIR = os.path.join(ROOT_DIR, 'domains')
DATA_DIR = os.path.join(ROOT_DIR, 'data')

for d in [REPORTS_DIR, DOMAINS_DIR, DATA_DIR]:
    os.makedirs(d, exist_ok=True)

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

REQUIRED_COLUMNS = {'Name', 'SZ Drops', 'Age', 'Source', 'Expires'}

def load_domains_df(csv_path):
    """Load and validate domain DataFrame."""
    df = pd.read_csv(csv_path)
    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    if missing_cols:
        raise ValueError(f"CSV is missing columns: {missing_cols}")
    return df

def find_dodgy_domains(df):
    """Return set of dodgy domains and details."""
    dodgy_domains = set()
    details = []
    category_matches = {cat: 0 for cat in DODGY_KEYWORDS}

    for _, row in df.iterrows():
        domain = str(row['Name']).lower()
        matches = []
        matched_cats = set()
        for cat, keywords in DODGY_KEYWORDS.items():
            for word in keywords:
                if word in domain:
                    matches.append(word)
                    matched_cats.add(cat)
        if matches:
            dodgy_domains.add(domain)
            for cat in matched_cats:
                category_matches[cat] += 1
            details.append({
                'domain': domain,
                'matched_keywords': ', '.join(matches),
                'matched_categories': ', '.join(matched_cats)
            })
    return dodgy_domains, category_matches, details

def get_clean_domains(df, dodgy_domains):
    """Return a list of domain names that pass all exclusion filters."""
    clean = []
    excessive_drops = 0
    age_drop_excluded = 0
    today = pd.Timestamp.now().date()
    for _, row in df.iterrows():
        domain = str(row['Name']).lower()
        sz_drops = row['SZ Drops']
        age = row['Age']
        if domain in dodgy_domains:
            continue
        if not pd.isna(sz_drops) and sz_drops > 4:
            excessive_drops += 1
            continue
        # Exclude if age/drops ratio <= 1 (and drops not zero/NaN)
        if not pd.isna(age) and not pd.isna(sz_drops) and sz_drops:
            try:
                if float(age) / float(sz_drops) <= 1:
                    age_drop_excluded += 1
                    continue
            except Exception:
                continue
        clean.append(row['Name'])
    return clean, excessive_drops, age_drop_excluded

def daily_expiry_breakdown(df, clean_domains):
    """Return a dict of expiry date counts for the next 7 days."""
    expiry_counts = {}
    today = pd.Timestamp.now().date()
    for i in range(8):
        expiry_counts[today + timedelta(days=i)] = 0
    for _, row in df.iterrows():
        if row['Name'] not in clean_domains:
            continue
        expiry_date = row['Expires']
        if pd.isnull(expiry_date):
            continue
        try:
            # Handles most common formats robustly
            date_obj = pd.to_datetime(expiry_date, errors='coerce').date()
        except Exception:
            continue
        if today <= date_obj <= today + timedelta(days=7):
            expiry_counts[date_obj] += 1
    return expiry_counts

def write_clean_domains(clean_domains, out_dir, batch_size=200, force=False):
    """Write clean domains to text files, batching them."""
    os.makedirs(out_dir, exist_ok=True)
    files = [f for f in os.listdir(out_dir) if f.startswith("domains_") and f.endswith(".txt")]
    
    # Always remove existing files
    if files:
        for f in files:
            os.remove(os.path.join(out_dir, f))
    
    # Log the number of clean domains before writing
    logging.info(f"Writing {len(clean_domains)} clean domains...")
    
    for idx in range(0, len(clean_domains), batch_size):
        chunk = clean_domains[idx:idx+batch_size]
        out_path = os.path.join(out_dir, f"domains_{idx // batch_size + 1}.txt")
        with open(out_path, 'w', encoding='utf-8') as fp:
            for domain in chunk:
                fp.write(f"{domain}\n")
    logging.info(f"Wrote {len(clean_domains)} clean domains into files (batch size {batch_size}).")
    return True

def verify_output_files(output_dir, dodgy_domains):
    """Verify no dodgy domains ended up in the output."""
    found = 0
    for file in os.listdir(output_dir):
        if file.startswith("domains_") and file.endswith(".txt"):
            with open(os.path.join(output_dir, file), 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip().lower() in dodgy_domains:
                        logging.error(f"Dodgy domain found in output: {line.strip()}")
                        found += 1
    if found:
        logging.error("Verification failed!")
    else:
        logging.info("Verification passed: no dodgy domains in output files.")
    return found == 0

def generate_report(df, dodgy_domains, category_matches, excessive_drops, age_drop_excluded, clean_domains, expiry_breakdown):
    date_str = datetime.now().strftime('%Y-%m-%d')
    out_path = os.path.join(REPORTS_DIR, f"{date_str}_domain_analysis_report.txt")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"Domain Analysis Report - {date_str}\n")
        f.write("="*60 + "\n\n")
        f.write(f"Total Domains: {len(df)}\n")
        f.write(f"Dodgy Domains: {len(dodgy_domains)}\n")
        f.write(f"Excessive Drops (>4): {excessive_drops}\n")
        f.write(f"Age/Drop Ratio <=1: {age_drop_excluded}\n")
        f.write(f"Clean Domains: {len(clean_domains)}\n\n")
        f.write("Category Breakdown:\n")
        for cat, count in category_matches.items():
            f.write(f"  {cat}: {count}\n")
        f.write("\nExpiry breakdown (next 7 days):\n")
        for d, cnt in sorted(expiry_breakdown.items()):
            f.write(f"  {d}: {cnt}\n")
        f.write("\nAuction Source Breakdown:\n")
        source_counts = df['Source'].value_counts()
        for source, count in source_counts.items():
            pct = count / len(df) * 100
            f.write(f"  {source}: {count} ({pct:.2f}%)\n")
    logging.info(f"Report written to {out_path}")

def process_domains(force=False):
    try:
        export_file = Config.get_export_file()
        logging.info(f"Processing file: {export_file}")
        
        # Detailed file diagnostics
        import os
        file_size = os.path.getsize(export_file)
        logging.info(f"File size: {file_size} bytes")
        
        # Print first few lines of the file
        with open(export_file, 'r', encoding='utf-8') as f:
            first_lines = [f.readline().strip() for _ in range(5)]
            logging.info("First 5 lines of the file:")
            for line in first_lines:
                logging.info(line)
        
        # Try reading with different encodings and print column details
        encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'iso-8859-1']
        
        for encoding in encodings_to_try:
            try:
                df = pd.read_csv(export_file, encoding=encoding)
                logging.info(f"Successfully read file with {encoding} encoding")
                
                # Detailed column and data diagnostics
                logging.info("DataFrame Information:")
                logging.info(f"Total rows: {len(df)}")
                logging.info("Columns:")
                for col in df.columns:
                    logging.info(f"- {col}: {df[col].dtype}")
                
                # Print first few rows:
                logging.info("\nFirst 5 rows:")
                pd.set_option('display.max_columns', None)
                pd.set_option('display.width', 1000)
                logging.info(df.head().to_string())
                
                break
            except Exception as e:
                logging.warning(f"Failed to read file with {encoding} encoding: {e}")
        else:
            raise ValueError("Could not read file with any of the attempted encodings")
        
        # Verify required columns
        missing_cols = REQUIRED_COLUMNS - set(df.columns)
        if missing_cols:
            raise ValueError(f"CSV is missing columns: {missing_cols}")
        
        # Detailed domain filtering logging
        dodgy_domains, category_matches, details = find_dodgy_domains(df)
        logging.info("\nDodgy Domain Details:")
        for detail in details:
            logging.info(f"Dodgy Domain: {detail['domain']} - Keywords: {detail['matched_keywords']}, Categories: {detail['matched_categories']}")
        
        logging.info(f"\nTotal Dodgy Domains: {len(dodgy_domains)}")
        logging.info("Dodgy Domain Categories:")
        for cat, count in category_matches.items():
            logging.info(f"  {cat}: {count}")
        
        clean_domains, excessive_drops, age_drop_excluded = get_clean_domains(df, dodgy_domains)
        
        logging.info("\nDomain Filtering Summary:")
        logging.info(f"Total Domains: {len(df)}")
        logging.info(f"Dodgy Domains Filtered: {len(dodgy_domains)}")
        logging.info(f"Domains with Excessive Drops (>4): {excessive_drops}")
        logging.info(f"Domains Excluded by Age/Drop Ratio: {age_drop_excluded}")
        logging.info(f"Clean Domains: {len(clean_domains)}")
        
        # Optional: Log first few clean domains
        logging.info("\nFirst 10 Clean Domains:")
        for domain in clean_domains[:10]:
            logging.info(domain)
        
        expiry_breakdown = daily_expiry_breakdown(df, clean_domains)
        write_clean_domains(clean_domains, DOMAINS_DIR, force=force)
        verify_output_files(DOMAINS_DIR, dodgy_domains)
        generate_report(df, dodgy_domains, category_matches, excessive_drops, age_drop_excluded, clean_domains, expiry_breakdown)
        logging.info("Done.")
    except Exception as e:
        logging.exception(f"Failed to process domains: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Process Spamzilla domains and output clean lists.')
    parser.add_argument('--force', action='store_true', help='Force overwrite of existing output files.')
    args = parser.parse_args()
    process_domains(force=args.force)
