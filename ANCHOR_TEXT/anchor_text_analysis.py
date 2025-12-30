import os
import pandas as pd
import re
from datetime import datetime
from collections import defaultdict
from urllib.parse import urlparse
import logging

# Import configuration
from .config import (
    BACKLINKS_DIR, 
    OUTPUT_DIR, 
    MAX_ANCHOR_TEXTS, 
    NORMALIZATION_OPTIONS
)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('anchor_text_analysis.log')
    ]
)

def normalize_anchor_text(text):
    """Normalize anchor text for consistent comparison"""
    if not isinstance(text, str):
        logging.warning(f"Non-string anchor text found: {type(text)}")
        return ''
    
    # Apply normalization based on config
    if NORMALIZATION_OPTIONS.get('lowercase', True):
        text = text.lower()
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    # Remove common prefixes/suffixes
    text = text.strip('.,;:!?')
    
    # Remove HTML entities if configured
    if NORMALIZATION_OPTIONS.get('remove_html_entities', True):
        text = re.sub(r'&[a-zA-Z]+;', '', text)
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    
    logging.debug(f"Normalized anchor text: '{text}'")
    return text

def normalize_domain(url):
    """Normalize domain for consistent comparison"""
    try:
        parsed = urlparse(str(url))
        domain = parsed.netloc.lower()
        
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
            
        # Handle internationalized domain names
        try:
            domain = domain.encode('idna').decode('utf-8')
        except:
            logging.warning(f"Failed to encode IDN domain: {domain}")
            
        logging.debug(f"Normalized domain: {domain}")
        return domain
    except Exception as e:
        logging.error(f"Error parsing URL {url}: {str(e)}")
        return ''

def get_domain_file_mapping():
    """Get mapping of domains to their backlink files"""
    logging.info(f"Scanning directory: {BACKLINKS_DIR}")
    files = os.listdir(BACKLINKS_DIR)
    mapping = {}
    
    for f in files:
        if f.endswith("-backlinks.csv"):
            domain = f[:-14]
            mapping[domain] = os.path.join(BACKLINKS_DIR, f)
            logging.debug(f"Found backlink file for domain: {domain}")
    
    logging.info(f"Found {len(mapping)} domains with backlink files")
    return mapping

def extract_anchor_text_data_from_csv(domain, file_path):
    """Extract and normalize anchor text data from a CSV file"""
    logging.info(f"Processing file for domain: {domain}")
    
    if not os.path.exists(file_path):
        logging.error(f"Backlink file not found for domain: {domain}")
        return []
        
    try:
        df = pd.read_csv(file_path)
        logging.debug(f"Successfully read CSV file: {file_path}")
        logging.debug(f"Columns found: {list(df.columns)}")
        
        # Standardize column names
        df.columns = [col.strip().lower() for col in df.columns]
        
        # Find anchor and source url columns
        anchor_col = None
        source_url_col = None
        for col in df.columns:
            if col == 'anchor':
                anchor_col = col
            if col in ['source url', 'source_url']:
                source_url_col = col
                
        if anchor_col is None or source_url_col is None:
            logging.error(f"Missing required columns in {file_path}")
            logging.error(f"Available columns: {list(df.columns)}")
            return []
            
        # Normalize anchor texts and domains
        logging.info("Normalizing anchor texts and domains...")
        df['normalized_anchor'] = df[anchor_col].apply(normalize_anchor_text)
        df['ref_domain'] = df[source_url_col].apply(normalize_domain)
        
        # Remove empty or invalid entries
        df = df[df['normalized_anchor'].str.len() > 0]
        df = df[df['ref_domain'].str.len() > 0]
        
        # Group by normalized anchor text
        anchor_counts = df['normalized_anchor'].value_counts().to_dict()
        total = sum(anchor_counts.values())
        
        logging.info(f"Found {len(anchor_counts)} unique anchor texts")
        logging.debug(f"Total backlinks: {total}")
        
        anchor_data = []
        for anchor_text, count in anchor_counts.items():
            percentage = (count / total) * 100 if total else 0
            ref_domains = set(df[df['normalized_anchor'] == anchor_text]['ref_domain'].unique())
            
            anchor_data.append({
                'anchor_text': anchor_text,
                'percentage': percentage,
                'count': count,
                'ref_domains': ref_domains
            })
            
            logging.debug(f"Anchor text: {anchor_text}")
            logging.debug(f"  - Count: {count}")
            logging.debug(f"  - Percentage: {percentage:.2f}%")
            logging.debug(f"  - Unique referring domains: {len(ref_domains)}")
            
        return anchor_data
        
    except Exception as e:
        logging.error(f"Error processing file {file_path}: {str(e)}")
        logging.error("Stack trace:", exc_info=True)
        return []

def analyze_anchor_texts():
    """Main analysis function"""
    logging.info("Starting anchor text analysis")
    logging.info(f"Reading backlink files from: {BACKLINKS_DIR}")
    
    domain_file_map = get_domain_file_mapping()
    logging.info(f"Found {len(domain_file_map)} domains with backlink files")
    
    # Global mapping: anchor_text -> set(domains)
    global_anchor_domains = defaultdict(set)
    domain_anchor_data = {}
    
    for domain, file_path in domain_file_map.items():
        logging.info(f"\nProcessing domain: {domain}")
        anchor_data = extract_anchor_text_data_from_csv(domain, file_path)
        domain_anchor_data[domain] = anchor_data
        
        for item in anchor_data:
            global_anchor_domains[item['anchor_text']].add(domain)
            
    results = []
    max_anchors = MAX_ANCHOR_TEXTS  # Use the configurable value
    
    for domain, anchor_data in domain_anchor_data.items():
        logging.info(f"\nAnalyzing domain: {domain}")
        
        # Calculate domain-specific stats
        domain_stats = []
        for item in anchor_data:
            anchor_text = item['anchor_text']
            percentage = item['percentage']
            count = len(global_anchor_domains[anchor_text])
            
            domain_stats.append({
                'anchor_text': anchor_text,
                'percentage': percentage,
                'count': count
            })
            
        # Sort domain stats by percentage (descending)
        domain_stats_sorted = sorted(domain_stats, key=lambda x: x['percentage'], reverse=True)
        
        # Create a row for domains
        domains_row = {'Domain': domain}
        for i, item in enumerate(domain_stats_sorted[:max_anchors], 1):
            domains_row[f'ANCHOR {i}'] = item['anchor_text']
            domains_row[f'%{i}'] = f"{item['percentage']:.2f}%"
            domains_row[f'#{i}'] = item['count']
            
        results.append(domains_row)
        
    # Create DataFrame and save to CSV
    results_df = pd.DataFrame(results)
    column_order = ['Domain']
    for i in range(1, max_anchors + 1):
        column_order.extend([f'ANCHOR {i}', f'%{i}', f'#{i}'])
    results_df = results_df[column_order]
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    current_date = datetime.now().strftime('%Y%m%d')
    output_file = os.path.join(OUTPUT_DIR, f'{current_date}_anchor_text_analysis_results.csv')
    results_df.to_csv(output_file, index=False)
    
    logging.info(f"Analysis complete. Results saved to {output_file}")
    logging.info(f"Processed {len(results)} domains")
    logging.info(f"Total unique anchor texts found: {len(global_anchor_domains)}") 