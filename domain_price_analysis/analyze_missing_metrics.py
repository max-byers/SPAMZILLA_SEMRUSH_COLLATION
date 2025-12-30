import pandas as pd
import numpy as np
from datetime import datetime
import os

def analyze_missing_metrics():
    # Get the base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Read the collated price analysis file
    df = pd.read_csv(os.path.join(base_dir, '..', 'collated_price_analysis.csv'))
    
    # Get current date for the report filename
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # Initialize report content
    report_content = f"Missing Metrics Analysis Report - {current_date}\n"
    report_content += "=" * 50 + "\n\n"
    
    # List of columns to check for missing data
    columns_to_check = [
        'AS', 'DA', 'DR', 'UR', 'TF', 'CF', 'S RD', 'M RD', 'A RD',
        'S BL', 'M BL', 'A BL', 'IP\'S', 'SZ', 'Variance', 'Follow %',
        'S (BL/RD)', 'M (BL/RD)', 'Age', 'Indexed', 'Drops', 'MT',
        'English %', 'Expiry'
    ]
    
    # Analyze each column
    for column in columns_to_check:
        if column in df.columns:
            missing_count = df[column].isna().sum()
            total_count = len(df)
            missing_percentage = (missing_count / total_count) * 100
            
            report_content += f"\n{column}:\n"
            report_content += f"- Total domains: {total_count}\n"
            report_content += f"- Missing data: {missing_count} ({missing_percentage:.2f}%)\n"
            
            if missing_count > 0:
                # Get list of domains with missing data
                missing_domains = df[df[column].isna()]['Name'].tolist()
                report_content += "- Domains with missing data:\n"
                for domain in missing_domains:
                    report_content += f"  * {domain}\n"
        else:
            report_content += f"\n{column}:\n"
            report_content += "- Column not found in the dataset\n"
    
    # Write the report to a file
    report_filename = os.path.join(base_dir, f'missing_metrics_report_{current_date}.txt')
    with open(report_filename, 'w') as f:
        f.write(report_content)
    
    print(f"Report generated: {report_filename}")

if __name__ == "__main__":
    analyze_missing_metrics() 