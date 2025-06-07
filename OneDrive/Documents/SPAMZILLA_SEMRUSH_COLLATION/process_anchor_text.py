import os
import glob
import pandas as pd
from datetime import datetime
import csv

def get_latest_semrush_file():
    """Get the most recent SEMRUSH backlinks file from the ORGANISING_DOWNLOADED_FILES directory."""
    # Create directory if it doesn't exist
    os.makedirs('ORGANISING_DOWNLOADED_FILES/06_06_SEMRUSH_backlinks', exist_ok=True)
    
    # Find all SEMRUSH backlinks files
    pattern = os.path.join('ORGANISING_DOWNLOADED_FILES', '06_06_SEMRUSH_backlinks', '*-backlinks.csv')
    files = glob.glob(pattern)
    
    if not files:
        raise FileNotFoundError("No SEMRUSH backlinks files found in ORGANISING_DOWNLOADED_FILES/06_06_SEMRUSH_backlinks directory.")
    
    # Get the most recent file
    latest_file = max(files, key=os.path.getctime)
    return latest_file

def process_anchor_texts(df):
    """Process the DataFrame to create anchor text distributions for the root domain only."""
    # Filter to keep only rows where 'Target url' is the root domain (e.g., 'example.com')
    df['root_domain'] = df['Target url'].apply(lambda x: x.split('/')[0] if '/' in x else x)
    df = df[df['Target url'] == df['root_domain']]
    anchor_counts = df.groupby(['Target url', 'Anchor']).size().reset_index(name='count')
    total_backlinks = anchor_counts.groupby('Target url')['count'].sum().reset_index(name='total')
    anchor_counts = anchor_counts.merge(total_backlinks, on='Target url')
    anchor_counts['percentage'] = (anchor_counts['count'] / anchor_counts['total'] * 100).round(2)
    # Replace missing or empty anchor texts with 'nan' string
    anchor_counts['Anchor'] = anchor_counts['Anchor'].fillna('nan').replace('', 'nan')
    anchor_counts['formatted'] = anchor_counts.apply(
        lambda x: f"{x['Anchor']} - {x['percentage']}% - {x['count']}", axis=1
    )
    top_anchors = anchor_counts.sort_values(['Target url', 'count'], ascending=[True, False])
    top_anchors = top_anchors.groupby('Target url').head(10)
    result = []
    for domain in top_anchors['Target url'].unique():
        domain_data = top_anchors[top_anchors['Target url'] == domain]
        # Pad to 10 anchor texts, using 'nan' if fewer than 10
        formatted_anchors = domain_data['formatted'].tolist()
        if len(formatted_anchors) < 10:
            formatted_anchors += ['nan'] * (10 - len(formatted_anchors))
        else:
            formatted_anchors = formatted_anchors[:10]
        backlinks_row = [domain + ' - backlinks'] + formatted_anchors
        result.append(backlinks_row)
        domains_row = [domain + ' - domains'] + formatted_anchors
        result.append(domains_row)
    return result

def create_anchor_text_csv():
    """Create the anchor text CSV file."""
    # Get the latest SEMRUSH file
    latest_file = get_latest_semrush_file()
    
    # Read the CSV file
    df = pd.read_csv(latest_file)
    
    # Process the data
    result_rows = process_anchor_texts(df)
    
    # Create output directory if it doesn't exist
    os.makedirs('BACKLINK_CSV_FILES/ANCHOR_TEXT', exist_ok=True)
    
    # Generate output filename with current date
    current_date = datetime.now().strftime('%Y-%m-%d')
    output_file = f'BACKLINK_CSV_FILES/ANCHOR_TEXT/{current_date}_anchor_text_ALL.csv'
    
    # Write with header and proper quoting
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['', 1,2,3,4,5,6,7,8,9,10])
        for row in result_rows:
            writer.writerow(row)
    print(f"Anchor text CSV file created: {output_file}")

if __name__ == '__main__':
    create_anchor_text_csv() 