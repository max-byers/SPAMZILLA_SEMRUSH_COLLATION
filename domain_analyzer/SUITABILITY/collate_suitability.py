import pandas as pd
import os
from datetime import datetime

def collate_suitability_files():
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the accepted_domains_list folder
    input_dir = os.path.join(current_dir, 'accepted_domains_list')
    
    # List to store all dataframes
    dfs = []
    
    # Read all CSV files in the accepted_domains_list directory
    for filename in os.listdir(input_dir):
        if filename.endswith('.csv'):
            file_path = os.path.join(input_dir, filename)
            try:
                # Read the CSV file
                df = pd.read_csv(file_path)
                
                # Standardize column names
                if 'Suitable?' in df.columns:
                    df = df.rename(columns={'Suitable?': 'Suitability'})
                
                # Add source file information
                df['Source_File'] = filename
                
                dfs.append(df)
                print(f"Successfully processed: {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
    
    if not dfs:
        print("No CSV files found to process")
        return
    
    # Combine all dataframes
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Remove duplicates based on Name (domain)
    combined_df = combined_df.drop_duplicates(subset=['Name'], keep='last')
    
    # Convert Expiry to datetime for proper sorting
    combined_df['Expiry'] = pd.to_datetime(combined_df['Expiry'], format='%d/%m/%Y', errors='coerce')
    
    # Sort by Expiry date
    combined_df = combined_df.sort_values('Expiry')
    
    # Convert Expiry back to string format
    combined_df['Expiry'] = combined_df['Expiry'].dt.strftime('%d/%m/%Y')
    
    # Use fixed output filename
    output_file = os.path.join(current_dir, 'suitability_collated.csv')
    
    # Save to CSV
    combined_df.to_csv(output_file, index=False)
    print(f"\nCollation complete. Output saved to: {output_file}")
    print(f"Total unique domains: {len(combined_df)}")

    # Calculate metrics
    total_domains = len(combined_df)
    suitable_domains = combined_df['Suitability'].notna().sum()
    suitable_percentage = (suitable_domains / total_domains) * 100
    
    # Generate metrics text file with fixed name
    metrics_file = os.path.join(current_dir, 'suitability_report.txt')
    with open(metrics_file, 'w') as f:
        f.write("SUITABILITY ANALYSIS METRICS\n")
        f.write("==========================\n\n")
        f.write(f"Total unique domains: {total_domains}\n")
        f.write(f"Domains marked as suitable (1): {suitable_domains}\n")
        f.write(f"Percentage of suitable domains: {suitable_percentage:.2f}%\n")
        f.write("\n")
        # Add source file statistics
        f.write("Source File Statistics:\n")
        f.write("---------------------\n")
        source_stats = combined_df['Source_File'].value_counts()
        for source, count in source_stats.items():
            # Calculate the number of suitable domains for this source file
            suitable_count = combined_df[combined_df['Source_File'] == source]['Suitability'].notna().sum()
            percent = (suitable_count / count) * 100
            f.write(f"{source}: {count} domains ({percent:.2f}% suitable)\n")
    
    print(f"\nMetrics saved to: {metrics_file}")

if __name__ == "__main__":
    collate_suitability_files() 