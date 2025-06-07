import pandas as pd
import numpy as np
import os

def analyze_missing_metrics():
    # Read the collated data
    df = pd.read_csv('output_domain_price_analysis/collated_price_analysis.csv')
    
    # Get all columns except 'Name' and 'Source_File'
    metric_columns = [col for col in df.columns if col not in ['Name', 'Source_File']]
    
    # Calculate missing metrics for each domain
    missing_metrics = {}
    for _, row in df.iterrows():
        domain = row['Name']
        missing = [col for col in metric_columns if pd.isna(row[col]) or row[col] == 'N/A']
        if missing:
            missing_metrics[domain] = missing
    
    # Create output directory if it doesn't exist
    output_dir = 'output_domain_price_analysis'
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate report
    output_file = os.path.join(output_dir, 'missing_metrics_report.txt')
    with open(output_file, 'w') as f:
        f.write("MISSING METRICS ANALYSIS REPORT\n")
        f.write("=============================\n\n")
        
        # Overall statistics
        total_domains = len(df)
        domains_with_missing = len(missing_metrics)
        f.write(f"Total Domains Analyzed: {total_domains}\n")
        f.write(f"Domains with Missing Metrics: {domains_with_missing}\n")
        f.write(f"Percentage of Domains with Missing Data: {(domains_with_missing/total_domains)*100:.2f}%\n\n")
        
        # Missing metrics by column
        f.write("MISSING METRICS BY COLUMN\n")
        f.write("------------------------\n")
        for col in metric_columns:
            missing_count = df[col].isna().sum() + (df[col] == 'N/A').sum()
            f.write(f"{col}: {missing_count} missing values ({missing_count/total_domains*100:.2f}%)\n")
        
        # Detailed domain report
        f.write("\nDETAILED DOMAIN REPORT\n")
        f.write("---------------------\n")
        for domain, missing in missing_metrics.items():
            f.write(f"\nDomain: {domain}\n")
            f.write("Missing Metrics:\n")
            for metric in missing:
                f.write(f"- {metric}\n")
    
    print(f"Report has been generated at: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    analyze_missing_metrics() 