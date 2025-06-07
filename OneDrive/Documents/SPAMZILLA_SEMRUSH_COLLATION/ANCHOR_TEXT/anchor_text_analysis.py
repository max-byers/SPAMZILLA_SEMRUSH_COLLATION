import os
import pandas as pd
from collections import Counter
from datetime import datetime
import glob

def get_latest_backlink_files():
    """Get all backlink files from the most recent SEMRUSH_backlinks directory."""
    backlink_dir = os.path.join('ORGANISING_DOWNLOADED_FILES', '*_SEMRUSH_backlinks')
    backlink_folders = glob.glob(backlink_dir)
    if not backlink_folders:
        raise FileNotFoundError("No backlink folders found")
    latest_folder = max(backlink_folders, key=os.path.getctime)
    return glob.glob(os.path.join(latest_folder, '*-backlinks.csv'))

def analyze_anchor_texts(backlink_files):
    """Analyze anchor texts for each domain and return top 10 rankings."""
    domain_analysis = {}
    
    for backlink_file in backlink_files:
        # Extract domain name from filename
        domain = os.path.basename(backlink_file).replace('-backlinks.csv', '')
        
        try:
            df = pd.read_csv(backlink_file)
            
            # Count anchor text occurrences
            anchor_counts = Counter(df['Anchor'])
            total_links = len(df)
            
            # Calculate percentages and get top 10
            anchor_stats = []
            for anchor, count in anchor_counts.most_common(10):
                percentage = (count / total_links) * 100
                anchor_stats.append(f"{anchor} - {percentage:.0f}% - {count}")
            
            # Store both backlinks and domains analysis
            domain_analysis[f"{domain} - backlinks"] = anchor_stats
            
            # For domains analysis, we need to count unique domains using each anchor text
            domain_anchors = {}
            for _, row in df.iterrows():
                anchor = row['Anchor']
                source_domain = row['Source']
                if anchor not in domain_anchors:
                    domain_anchors[anchor] = set()
                domain_anchors[anchor].add(source_domain)
            
            # Calculate domain percentages
            domain_stats = []
            for anchor, domains in sorted(domain_anchors.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
                percentage = (len(domains) / len(df['Source'].unique())) * 100
                domain_stats.append(f"{anchor} - {percentage:.0f}% - {len(domains)}")
            
            domain_analysis[f"{domain} - domains"] = domain_stats
            
        except Exception as e:
            print(f"Error processing {domain}: {str(e)}")
            continue
    
    return domain_analysis

def write_analysis_to_file(analysis, output_file):
    """Write the analysis results to a tab-separated file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write('\t' + '\t'.join(str(i) for i in range(1, 11)) + '\n')
        
        # Write data for each domain
        for domain, stats in analysis.items():
            f.write(f"{domain}\t" + '\t'.join(stats) + '\n')

def main():
    # Create output directory if it doesn't exist
    os.makedirs('ANCHOR_TEXT', exist_ok=True)
    
    # Get the latest backlink files
    backlink_files = get_latest_backlink_files()
    if not backlink_files:
        print("No backlink files found!")
        return
    
    print(f"Found {len(backlink_files)} backlink files to process...")
    
    # Analyze anchor texts
    analysis = analyze_anchor_texts(backlink_files)
    
    # Write results to file
    output_file = os.path.join('ANCHOR_TEXT', 'anchor_text_analysis.txt')
    write_analysis_to_file(analysis, output_file)
    print(f"Analysis complete. Results written to {output_file}")

if __name__ == "__main__":
    main() 