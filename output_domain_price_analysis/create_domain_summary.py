import pandas as pd
import os
import glob
from pathlib import Path

# Domain prices dictionary
DOMAIN_PRICES = {
    'iprescribeexercise.com': 150,
    'joyofenjoy.com': 315
}

def create_summary_sheets():
    # Create output directory if it doesn't exist
    output_dir = Path('BACKLINK_CSV_FILES/MY_DOMAINS_EVERYTHING_QUALITY_SUMMARY')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all backlink files from MY_DOMAINS directory
    backlink_files = glob.glob('MY_DOMAINS/*-backlinks.csv')
    
    for file in backlink_files:
        # Extract domain name from filename
        domain = os.path.basename(file).replace('-backlinks.csv', '')
        
        # Read the backlink file
        df = pd.read_csv(file)
        
        # Calculate metrics
        everything_metrics = {
            'Domain': domain,
            'Price': f"${DOMAIN_PRICES.get(domain, 'N/A')}",
            'Total Backlinks': len(df),
            'Unique Referring Domains': df['Source'].nunique(),
            'Average AS': df['AS'].mean() if 'AS' in df.columns else 'N/A',
            'Median AS': df['AS'].median() if 'AS' in df.columns else 'N/A',
            'Average External Links': df['External Links'].mean() if 'External Links' in df.columns else 'N/A',
            'Median External Links': df['External Links'].median() if 'External Links' in df.columns else 'N/A'
        }
        
        # Calculate quality metrics (assuming quality is based on certain criteria)
        quality_df = df[
            (df['AS'] > df['AS'].median()) if 'AS' in df.columns else True
        ]
        
        quality_metrics = {
            'Domain': domain,
            'Price': f"${DOMAIN_PRICES.get(domain, 'N/A')}",
            'Quality Backlinks': len(quality_df),
            'Quality Referring Domains': quality_df['Source'].nunique(),
            'Quality Average AS': quality_df['AS'].mean() if 'AS' in quality_df.columns else 'N/A',
            'Quality Median AS': quality_df['AS'].median() if 'AS' in quality_df.columns else 'N/A',
            'Quality Average External Links': quality_df['External Links'].mean() if 'External Links' in quality_df.columns else 'N/A',
            'Quality Median External Links': quality_df['External Links'].median() if 'External Links' in quality_df.columns else 'N/A'
        }
        
        # Create summary DataFrame
        summary_df = pd.DataFrame([everything_metrics, quality_metrics])
        
        # Save files
        everything_file = output_dir / f"{domain}_everything.csv"
        quality_file = output_dir / f"{domain}_quality.csv"
        summary_file = output_dir / f"{domain}_summary.csv"
        
        # Save individual files
        pd.DataFrame([everything_metrics]).to_csv(everything_file, index=False)
        pd.DataFrame([quality_metrics]).to_csv(quality_file, index=False)
        summary_df.to_csv(summary_file, index=False)
        
        print(f"Created summary files for {domain}")

if __name__ == "__main__":
    create_summary_sheets() 