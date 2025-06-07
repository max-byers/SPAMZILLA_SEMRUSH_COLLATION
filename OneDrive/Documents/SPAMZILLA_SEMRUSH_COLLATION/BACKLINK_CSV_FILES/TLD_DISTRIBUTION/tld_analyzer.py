import pandas as pd
from urllib.parse import urlparse
from collections import Counter
from datetime import datetime
import os

def analyze_tlds(csv_file):
    # Read the CSV file
    df = pd.read_csv(csv_file)
    
    # Get all source URLs
    source_urls = df['Source url'].tolist()
    
    # Extract TLDs and unique domains
    tlds = []
    all_unique_domains = set()
    non_main_domains = set()
    edu_domains = set()
    gov_domains = set()
    
    for url in source_urls:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            tld = domain.split('.')[-1]
            tlds.append(tld)
            all_unique_domains.add(domain)
            if tld not in {'com', 'net', 'org'}:
                non_main_domains.add(domain)
            if tld == 'edu':
                edu_domains.add(domain)
            if tld == 'gov':
                gov_domains.add(domain)
        except:
            continue
    
    # Count total backlinks
    total_backlinks = len(tlds)
    
    # Count non-main TLD backlinks
    main_tlds = {'com', 'net', 'org'}
    non_main_tlds = [tld for tld in tlds if tld not in main_tlds]
    non_main_count = len(non_main_tlds)
    
    # Calculate percentages
    backlink_percentage = (non_main_count / total_backlinks) * 100 if total_backlinks else 0
    domain_percentage = (len(non_main_domains) / len(all_unique_domains)) * 100 if all_unique_domains else 0
    
    # Get domain name from CSV filename
    domain_name = os.path.basename(csv_file).split('-')[0]
    
    return {
        'Domain': domain_name,
        "% (non main TLD's) - backlinks": f"{backlink_percentage:.1f}% - {non_main_count}",
        "% (non main TLD's) - domains": f"{domain_percentage:.1f}% - {len(non_main_domains)}",
        "Unique .edu domains": len(edu_domains),
        "Unique .gov domains": len(gov_domains)
    }

def analyze_folder(folder_path):
    today = datetime.now().strftime('%Y-%m-%d')
    output_dir = os.path.join('BACKLINK_CSV_FILES', 'TLD_DISTRIBUTION')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'{today}_TLD_distribution.csv')
    results = []
    for file in os.listdir(folder_path):
        if file.endswith('.csv'):
            file_path = os.path.join(folder_path, file)
            try:
                result = analyze_tlds(file_path)
                results.append(result)
            except Exception as e:
                print(f"Error processing {file}: {e}")
    df_out = pd.DataFrame(results)
    df_out.to_csv(output_file, index=False)
    return df_out, output_file

if __name__ == "__main__":
    folder_path = "1_06_SEMRUSH_backlinks"
    df_out, output_file = analyze_folder(folder_path)
    print(df_out)
    print(f"Saved to: {output_file}") 