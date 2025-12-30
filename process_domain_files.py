import pandas as pd
import os
from pathlib import Path

# Define the domain prices
DOMAIN_PRICES = {
    'iprescribeexercise.com': 150,
    'joyofenjoy.com': 315
}

# Create the output directory
output_dir = Path('BACKLINK_CSV_FILES/MY_DOMAINS_EVERYTHING_QUALITY_SUMMARY')
output_dir.mkdir(parents=True, exist_ok=True)

# Process each domain file
all_data = []
for domain, price in DOMAIN_PRICES.items():
    input_file = f'MY_DOMAINS/{domain}-backlinks.csv'
    if os.path.exists(input_file):
        df = pd.read_csv(input_file)
        df['Domain'] = domain
        df['Price'] = price
        all_data.append(df)

# Combine all data
if all_data:
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Create summary statistics
    summary = combined_df.groupby('Domain').agg({
        'Price': 'first',
        'Source url': 'count',
        'Target url': 'nunique',
        'Source title': 'nunique',
        'Anchor': 'nunique'
    }).rename(columns={
        'Source url': 'Total Backlinks',
        'Target url': 'Unique Target URLs',
        'Source title': 'Unique Source Titles',
        'Anchor': 'Unique Anchors'
    })
    
    # Save the files
    combined_df.to_csv(output_dir / 'everything.csv', index=False)
    summary.to_csv(output_dir / 'summary.csv')
    
    # Create quality metrics
    quality_metrics = combined_df.groupby('Domain').agg({
        'Source url': 'count',
        'Target url': 'nunique',
        'Source title': 'nunique',
        'Anchor': 'nunique',
        'Price': 'first',
        'Page ascore': 'mean'
    }).rename(columns={
        'Source url': 'Total Backlinks',
        'Target url': 'Unique Target URLs',
        'Source title': 'Unique Source Titles',
        'Anchor': 'Unique Anchors',
        'Page ascore': 'Average Page Score'
    })
    
    quality_metrics.to_csv(output_dir / 'quality.csv') 