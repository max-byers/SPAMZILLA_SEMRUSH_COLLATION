import pandas as pd
import os

def process_backlink_data(summary_file):
    """
    Process backlink data from summary.csv.
    
    Args:
        summary_file (str): Path to summary.csv containing backlink data
        
    Returns:
        pd.DataFrame: DataFrame with backlink metrics
    """
    print("\nProcessing backlink data...")
    
    # Read the summary file
    df_backlinks = pd.read_csv(summary_file)
    
    # Clean up domain names by removing the -backlinks suffix
    df_backlinks['Domain'] = df_backlinks['Domain name'].str.replace('-backlinks$', '', regex=True)
    
    # Drop the original Domain name column
    df_backlinks = df_backlinks.drop('Domain name', axis=1)
    
    # Ensure domain names are in lowercase
    df_backlinks['Domain'] = df_backlinks['Domain'].str.lower()
    
    print(f"Successfully processed backlink data for {len(df_backlinks)} domains")
    
    return df_backlinks

if __name__ == "__main__":
    # Example usage
    base_dir = os.getcwd()
    summary_file = os.path.join(base_dir, "summary.csv")
    
    try:
        result = process_backlink_data(summary_file)
        print("\nSample of processed data:")
        print(result.head())
    except Exception as e:
        print(f"Error processing backlink data: {e}")