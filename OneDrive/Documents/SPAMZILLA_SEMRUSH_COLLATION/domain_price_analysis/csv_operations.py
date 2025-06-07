"""
CSV file creation utilities for generating specific CSV files.
"""

import pandas as pd
import os
from datetime import datetime

def create_main_sheet_csv(df, output_dir, timestamp):
    """
    Creates the main CSV file for accepted domains.
    
    Args:
        df (pd.DataFrame): DataFrame containing the main sheet data
        output_dir (str): Directory to save the CSV file
        timestamp (str): Timestamp for the filename
        
    Returns:
        str: Path to the created CSV file
    """
    filename = f"accepted_domains_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)
    
    # Ensure proper data types and formatting
    df = df.copy()
    
    # Format percentage columns
    if 'English %' in df.columns:
        # Skip formatting if already in string format
        numeric_mask = pd.to_numeric(df['English %'], errors='coerce').notna()
        df.loc[numeric_mask, 'English %'] = df.loc[numeric_mask, 'English %'].map('{:.2%}'.format)
    if 'Follow %' in df.columns:
        # Skip formatting if already in string format
        numeric_mask = pd.to_numeric(df['Follow %'], errors='coerce').notna()
        df.loc[numeric_mask, 'Follow %'] = df.loc[numeric_mask, 'Follow %'].map('{:.2%}'.format)
    
    # Format date columns
    if 'Expiry' in df.columns:
        df['Expiry'] = pd.to_datetime(df['Expiry']).dt.strftime('%Y-%m-%d')
    
    # Save to CSV
    df.to_csv(filepath, index=False)
    return filepath

def create_rejected_sheet_csv(df, output_dir, timestamp):
    """
    Creates the CSV file for rejected domains.
    
    Args:
        df (pd.DataFrame): DataFrame containing the rejected domains data
        output_dir (str): Directory to save the CSV file
        timestamp (str): Timestamp for the filename
        
    Returns:
        str: Path to the created CSV file
    """
    filename = f"rejected_domains_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)
    
    # Format the dataframe
    df = df.copy()
    
    # Format date columns if present
    if 'Expiry' in df.columns:
        df['Expiry'] = pd.to_datetime(df['Expiry']).dt.strftime('%Y-%m-%d')
    
    # Save to CSV
    df.to_csv(filepath, index=False)
    return filepath

def create_spam_test_sheet_csv(df, output_dir, timestamp):
    """
    Creates the CSV file for spam test results.
    
    Args:
        df (pd.DataFrame): DataFrame containing the spam test results
        output_dir (str): Directory to save the CSV file
        timestamp (str): Timestamp for the filename
        
    Returns:
        str: Path to the created CSV file
    """
    filename = f"spam_test_results_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)
    
    # Format the dataframe
    df = df.copy()
    
    # Format percentage columns if present
    if 'English %' in df.columns:
        df['English %'] = df['English %'].map('{:.2%}'.format)
    
    # Save to CSV
    df.to_csv(filepath, index=False)
    return filepath 