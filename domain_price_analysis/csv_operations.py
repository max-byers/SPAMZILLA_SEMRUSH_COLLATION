"""
CSV file creation utilities for generating specific CSV files.
"""

import pandas as pd
import os
from datetime import datetime
from config import REQUIRED_COLUMNS

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
    
    # Round all numeric columns to 2 decimal places
    numeric_cols = ['DA', 'AS', 'DR', 'UR', 'TF', 'CF', 'TF/CF',
                   'S RD', 'M RD', 'A RD', 'S BL', 'M BL', 'A BL',
                   'IP\'S', 'A (BL/RD)', 'Everything domains',
                   'Everything backlinks', 'Quality domains', 'Quality backlinks']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').round(2)
    
    # Format date columns
    if 'Expiry' in df.columns:
        df['Expiry'] = pd.to_datetime(df['Expiry']).dt.strftime('%Y-%m-%d')
    
    # Ensure all required columns exist
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = ''
    
    # Save to CSV with columns in the specified order
    df[REQUIRED_COLUMNS].to_csv(filepath, index=False)
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

    # Round all numeric columns to integers (no decimal places)
    for col in df.select_dtypes(include=["float", "float64", "int", "int64", "Int64"]):
        if col not in ['English %', 'Follow %']:
            df[col] = pd.to_numeric(df[col], errors='coerce').round(0).astype('Int64')

    # Format percentage columns as whole numbers with a percent sign
    if 'English %' in df.columns:
        numeric_mask = pd.to_numeric(df['English %'], errors='coerce').notna()
        df.loc[numeric_mask, 'English %'] = df.loc[numeric_mask, 'English %'].astype(float).round(0).astype('Int64').astype(str) + '%'
    if 'Follow %' in df.columns:
        numeric_mask = pd.to_numeric(df['Follow %'], errors='coerce').notna()
        df.loc[numeric_mask, 'Follow %'] = df.loc[numeric_mask, 'Follow %'].astype(float).round(0).astype('Int64').astype(str) + '%'
    
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

    # Round all numeric columns to integers (no decimal places)
    for col in df.select_dtypes(include=["float", "float64", "int", "int64", "Int64"]):
        if col not in ['English %', 'Follow %']:
            df[col] = pd.to_numeric(df[col], errors='coerce').round(0).astype('Int64')

    # Format percentage columns as whole numbers with a percent sign
    if 'English %' in df.columns:
        numeric_mask = pd.to_numeric(df['English %'], errors='coerce').notna()
        df.loc[numeric_mask, 'English %'] = df.loc[numeric_mask, 'English %'].astype(float).round(0).astype('Int64').astype(str) + '%'
    if 'Follow %' in df.columns:
        numeric_mask = pd.to_numeric(df['Follow %'], errors='coerce').notna()
        df.loc[numeric_mask, 'Follow %'] = df.loc[numeric_mask, 'Follow %'].astype(float).round(0).astype('Int64').astype(str) + '%'
    
    # Save to CSV
    df.to_csv(filepath, index=False)
    return filepath 