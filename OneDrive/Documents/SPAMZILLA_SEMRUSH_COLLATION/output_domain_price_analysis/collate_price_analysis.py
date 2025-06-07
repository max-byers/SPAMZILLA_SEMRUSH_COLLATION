import pandas as pd
import glob
import os
import traceback
from functools import wraps
from typing import List, Tuple, Dict, Optional

def handle_errors(func):
    """Decorator to handle common error patterns in a consistent way."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error in {func.__name__}:")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print("Full traceback:")
            print(traceback.format_exc())
            return None
    return wrapper

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Optimized data cleaning using vectorized operations."""
    # Replace NaN and empty values with 'N/A' in one operation
    df = df.fillna('N/A').replace(r'^\s*$', 'N/A', regex=True)
    
    # Clean price values by removing '$' and converting to float
    if 'Price' in df.columns:
        df['Price'] = df['Price'].astype(str).str.replace('$', '').str.replace(',', '')
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    
    # Merge Expirary and Expiry columns into a single Expiry column
    if 'Expirary' in df.columns and 'Expiry' in df.columns:
        # Combine both columns, preferring non-N/A values
        df['Expiry'] = df.apply(lambda row: row['Expiry'] if row['Expiry'] != 'N/A' else row['Expirary'], axis=1)
        # Drop the Expirary column
        df = df.drop('Expirary', axis=1)
    elif 'Expirary' in df.columns:
        # Rename Expirary to Expiry if Expiry doesn't exist
        df = df.rename(columns={'Expirary': 'Expiry'})
    
    # Clean numeric columns
    numeric_columns = [
        'Everything avg AS', 'Everything median AS',
        'Everything avg ext links', 'Everything median ext links',
        'Quality avg AS', 'Quality median AS',
        'Quality avg ext links', 'Quality median ext links'
    ]
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

@handle_errors
def read_csv_files(file_paths: List[str], dtype: Optional[Dict] = None) -> List[pd.DataFrame]:
    """Read multiple CSV files with optimized settings."""
    dfs = []
    for file in file_paths:
        # Read price column as string initially
        if dtype and 'Price' in dtype:
            dtype = dtype.copy()
            dtype['Price'] = str
        
        df = pd.read_csv(file, dtype=dtype)
        df['Source_File'] = os.path.basename(file)
        dfs.append(clean_dataframe(df))
    return dfs

@handle_errors
def add_domains_with_prices(domain_price_list: List[Tuple[str, float]]) -> None:
    """Add domains with prices using optimized DataFrame operations."""
    # Load files with optimized settings
    domains_with_prices = pd.read_csv('domains_with_prices.csv')
    no_price_domains = pd.read_csv('no_price_domains.csv')
    collated = pd.read_csv('collated_price_analysis.csv')
    
    # Create new entries DataFrame
    new_entries = pd.DataFrame(domain_price_list, columns=['Name', 'Price'])
    
    # Update domains_with_prices by merging with new entries
    domains_with_prices = pd.merge(
        domains_with_prices,
        new_entries,
        on='Name',
        how='outer',
        suffixes=('', '_new')
    )
    # Update prices with new values where available
    domains_with_prices['Price'] = domains_with_prices['Price_new'].fillna(domains_with_prices['Price'])
    domains_with_prices = domains_with_prices.drop('Price_new', axis=1)
    
    # Update no_price_domains by removing domains that now have prices
    no_price_domains = no_price_domains[~no_price_domains['Name'].isin(new_entries['Name'])]
    
    # Update collated file using merge for better performance
    price_updates = pd.merge(collated, new_entries, on='Name', how='left', suffixes=('', '_new'))
    collated['Price'] = price_updates['Price_new'].fillna(collated['Price'])
    
    # Save all files at once
    pd.concat([
        no_price_domains.to_csv('no_price_domains.csv', index=False),
        domains_with_prices.to_csv('domains_with_prices.csv', index=False),
        collated.to_csv('collated_price_analysis.csv', index=False)
    ])
    
    print(f"Updated {len(new_entries)} domains in domains_with_prices.csv and updated other files.")

@handle_errors
def cross_reference_domains() -> None:
    """Cross-reference domains using optimized merge operations."""
    print("\nCross-referencing domains between files...")
    
    # Read files with optimized settings
    domains_with_prices = pd.read_csv('domains_with_prices.csv')
    no_price_domains = pd.read_csv('no_price_domains.csv')
    
    # Use merge for better performance
    matching_domains = pd.merge(domains_with_prices, no_price_domains, on='Name', how='inner')
    
    if len(matching_domains) > 0:
        print(f"\nFound {len(matching_domains)} domains that appear in both files:")
        for _, row in matching_domains.iterrows():
            print(f"Domain: {row['Name']}, Price: {row['Price']}")
        
        # Update no_price_domains in memory
        no_price_domains = no_price_domains[~no_price_domains['Name'].isin(matching_domains['Name'])]
        no_price_domains.to_csv('no_price_domains.csv', index=False)
        print(f"\nRemoved {len(matching_domains)} domains from no_price_domains.csv")
    else:
        print("\nNo matching domains found between the files.")

@handle_errors
def update_prices_from_files(collated_df: pd.DataFrame, no_price_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Update prices using optimized DataFrame operations."""
    print("\nChecking for price updates...")
    
    # Get CSV files excluding collated and no_price files
    csv_files = [f for f in glob.glob('*.csv') 
                if 'collat' not in f.lower() and 'no_price_domains' not in f.lower()]
    
    # Read all files at once with optimized settings
    dfs = read_csv_files(csv_files)
    
    # Create price mapping using dictionary comprehension
    domain_prices = {
        row['Name']: row['Price']
        for df in dfs
        for _, row in df.iterrows()
        if row['Name'] in no_price_df['Name'].values and row['Price'] != 'N/A'
    }
    
    # Update prices using merge for better performance
    price_updates = pd.DataFrame(list(domain_prices.items()), columns=['Name', 'Price'])
    collated_df = pd.merge(collated_df, price_updates, on='Name', how='left', suffixes=('', '_new'))
    collated_df['Price'] = collated_df['Price_new'].fillna(collated_df['Price'])
    collated_df = collated_df.drop('Price_new', axis=1)
    
    # Update no_price_df
    no_price_df = no_price_df[~no_price_df['Name'].isin(domain_prices.keys())]
    
    updates_made = len(domain_prices)
    print(f"\nUpdated {updates_made} domains with new prices")
    print(f"Removed {updates_made} domains from no_price_domains.csv")
    
    return collated_df, no_price_df

@handle_errors
def collate_price_analysis() -> None:
    """Main function to collate price analysis with optimized operations."""
    # Get CSV files
    csv_files = [f for f in glob.glob('*.csv') 
                if 'collat' not in f.lower() and 'no_price_domains' not in f.lower()]
    
    print(f"\nFound {len(csv_files)} CSV files to process:")
    for file in csv_files:
        print(f"- {file}")
    
    if not csv_files:
        print("No CSV files found in the current folder")
        return
    
    # Read all files at once with optimized settings
    dfs = read_csv_files(csv_files)
    
    if not dfs:
        print("No valid data to combine")
        return
    
    # Combine all dataframes
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Create masks for price/no-price domains
    no_price_mask = (
        combined_df['Price'].isna() |
        (combined_df['Price'] == 'N/A') |
        (combined_df['Price'].astype(str).str.strip() == '')
    )
    
    # Create and save no_price_domains.csv
    no_price_df = combined_df[no_price_mask][['Name']].drop_duplicates()
    no_price_df.to_csv('no_price_domains.csv', index=False)
    print(f"\nCreated no_price_domains.csv with {len(no_price_df)} unique domains without prices")
    
    # Create and save domains_with_prices.csv
    domains_with_prices_df = combined_df[~no_price_mask][['Name', 'Price']].drop_duplicates()
    domains_with_prices_df.to_csv('domains_with_prices.csv', index=False)
    print(f"\nCreated domains_with_prices.csv with {len(domains_with_prices_df)} unique domains with prices")
    
    # Function to count non-empty values in a row
    def count_non_empty(row):
        return row.notna().sum()
    
    # Group by domain and keep the row with the most non-empty values
    combined_df['non_empty_count'] = combined_df.apply(count_non_empty, axis=1)
    combined_df = combined_df.sort_values('non_empty_count', ascending=False)
    combined_df = combined_df.drop_duplicates(subset=['Name'], keep='first')
    combined_df = combined_df.drop('non_empty_count', axis=1)
    
    # Handle Expiry column
    if 'Expirary' in combined_df.columns and 'Expiry' in combined_df.columns:
        # Combine both columns, preferring non-N/A values
        combined_df['Expiry'] = combined_df.apply(
            lambda row: row['Expiry'] if row['Expiry'] != 'N/A' else row['Expirary'], 
            axis=1
        )
        # Drop the Expirary column
        combined_df = combined_df.drop('Expirary', axis=1)
    elif 'Expirary' in combined_df.columns:
        # Rename Expirary to Expiry if Expiry doesn't exist
        combined_df = combined_df.rename(columns={'Expirary': 'Expiry'})
    
    # Columns to remove
    columns_to_remove = [
        'Indexed', 'Drops', 'MT', 'English %', 'Potentially spam',
        'Everything backlinks', 'Everything domains', 'Quality backlinks', 'Quality domains',
        'Everything avg AS', 'Everything median AS', 'Everything avg ext links', 'Everything median ext links',
        'Quality avg AS', 'Quality median AS', 'Quality avg ext links', 'Quality median ext links',
        'Follow %'
    ]
    for col in columns_to_remove:
        if col in combined_df.columns:
            combined_df = combined_df.drop(col, axis=1)
    
    # Remove decimal places from ratio columns (e.g., S (BL/RD), M (BL/RD), etc.)
    ratio_columns = [col for col in combined_df.columns if 'BL/RD' in col]
    for col in ratio_columns:
        if col in combined_df.columns:
            # Convert to numeric, round, and convert to int (if possible)
            combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce').round(0).astype('Int64')
    
    # Save combined data
    combined_df.to_csv('collated_price_analysis.csv', index=False)
    print(f"\nCombined data saved to: collated_price_analysis.csv")
    print(f"Total rows: {len(combined_df)}")
    print(f"Total unique domains: {combined_df['Name'].nunique()}")
    
    # Update prices and cross-reference
    combined_df, no_price_df = update_prices_from_files(combined_df, no_price_df)
    cross_reference_domains()

@handle_errors
def move_domains_with_prices_from_no_price() -> None:
    """Move domains with prices using optimized DataFrame operations."""
    # Load files with optimized settings
    domains_with_prices = pd.read_csv('domains_with_prices.csv')
    no_price_domains = pd.read_csv('no_price_domains.csv')
    collated = pd.read_csv('collated_price_analysis.csv')
    
    # Find domains with prices using vectorized operations
    mask_with_price = no_price_domains['Price'].notna() & (no_price_domains['Price'].astype(str).str.strip() != '')
    domains_to_move = no_price_domains[mask_with_price].copy()
    
    if not domains_to_move.empty:
        # Update all DataFrames in memory
        domains_with_prices = pd.concat([domains_with_prices, domains_to_move[['Name', 'Price']]], ignore_index=True)
        domains_with_prices = domains_with_prices.drop_duplicates(subset=['Name'], keep='last')
        
        # Update collated file using merge
        price_updates = pd.merge(collated, domains_to_move, on='Name', how='left', suffixes=('', '_new'))
        collated['Price'] = price_updates['Price_new'].fillna(collated['Price'])
        
        # Update no_price_domains
        no_price_domains = no_price_domains[~mask_with_price]
        
        # Save all files at once
        pd.concat([
            no_price_domains.to_csv('no_price_domains.csv', index=False),
            domains_with_prices.to_csv('domains_with_prices.csv', index=False),
            collated.to_csv('collated_price_analysis.csv', index=False)
        ])
        
        print(f"Moved {len(domains_to_move)} domains with prices from no_price_domains.csv to domains_with_prices.csv and updated collated_price_analysis.csv.")
    else:
        print("No domains with prices found in no_price_domains.csv.")

if __name__ == "__main__":
    collate_price_analysis() 