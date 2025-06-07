# data_processing.py
import pandas as pd
import numpy as np
import re
import traceback
from datetime import datetime, timedelta


def create_processed_dataframe(df_merged):
    """
    Process the merged dataframe to create the final dataframe with all metrics.
    """
    print(f"Merged dataframe has {len(df_merged)} rows and {len(df_merged.columns)} columns")
    print("Column names in merged data:", df_merged.columns.tolist())

    # Create a copy to avoid modifying the original
    df = df_merged.copy()

    # Initialize all required columns with empty values
    required_columns = [
        'Name', 'Source', 'Potentially spam', 'DA', 'AS', 'DR', 'UR', 'TF', 'CF',
        'S RD', 'M RD', 'A RD', 'S BL', 'M BL', 'A BL', 'IP\'S', 'SZ', 'Variance',
        'Follow %', 'S (BL/RD)', 'M (BL/RD)', 'Age', 'Indexed', 'Drops', 'MT',
        'English %', 'Expiry', 'Everything backlinks', 'Everything domains', 
        'Quality domains', 'Quality backlinks', 'Everything avg AS', 'Everything median AS',
        'Everything avg ext links', 'Everything median ext links', 'Quality avg AS',
        'Quality median AS', 'Quality avg ext links', 'Quality median ext links'
    ]
    
    for col in required_columns:
        if col not in df.columns:
            df[col] = ''

    # Map source data columns to expected columns
    column_mapping = {
        'Source': 'Source',
        'Moz DA': 'DA',
        'Authority Score': 'AS',
        'Ahrefs DR': 'DR',
        'Ahrefs UR': 'UR',
        'TF': 'TF',
        'CF': 'CF',
        'SEM Keywords': 'S RD',
        'Majestic RD': 'M RD',
        'Ahrefs RD': 'A RD',
        'SEM Traffic': 'S BL',
        'Majestic BL': 'M BL',
        'Ahrefs BL': 'A BL',
        'IPs': 'IP\'S',
        'SZ Score': 'SZ',
        'Age': 'Age',
        'Google Index': 'Indexed',
        'Majestic Topics': 'MT',
        'Follow links': 'Follow %',
        'Expires': 'Expiry',
        'Everything backlinks': 'Everything backlinks',
        'Everything domains': 'Everything domains',
        'Quality domains': 'Quality domains',
        'Quality backlinks': 'Quality backlinks'
    }

    # Apply column mappings where source columns exist
    for source_col, target_col in column_mapping.items():
        if source_col in df.columns:
            df[target_col] = df[source_col]
            print(f"Mapped '{source_col}' to '{target_col}'")
    
    # Calculate Follow % if we have the necessary columns
    if 'Follow links_temp' in df.columns and 'Nofollow links_temp' in df.columns:
        try:
            follow = pd.to_numeric(df['Follow links_temp'], errors='coerce').fillna(0)
            nofollow = pd.to_numeric(df['Nofollow links_temp'], errors='coerce').fillna(0)
            total = follow + nofollow
            df['Follow %'] = np.where(total > 0, follow / total, 0)
            print("Calculated 'Follow %' from 'Follow links' and 'Nofollow links'")
        except Exception as e:
            print(f"Error calculating 'Follow %': {e}")

    # Calculate S (BL/RD) ratio if we have the necessary columns
    if 'S BL' in df.columns and 'S RD' in df.columns:
        try:
            s_bl = pd.to_numeric(df['S BL'], errors='coerce').fillna(0)
            s_rd = pd.to_numeric(df['S RD'], errors='coerce').fillna(0)
            df['S (BL/RD)'] = np.where(s_rd > 0, s_bl / s_rd, 0)
            print("Calculated 'S (BL/RD)' ratio")
        except Exception as e:
            print(f"Error calculating 'S (BL/RD)': {e}")

    # Initialize potential spam column
    df['Potentially spam'] = ''

    # Clean up temporary columns
    temp_cols = ['Follow links_temp', 'Nofollow links_temp']
    for col in temp_cols:
        if col in df.columns:
            df = df.drop(col, axis=1)

    # Return DataFrame with only the required columns
    return df[required_columns]


def determine_rejection_reasons(df_final, df_all, domains_to_analyze=None):
    """
    Determine which domains should be rejected and track the reasons.
    
    Args:
        df_final: The processed dataframe with all domains
        df_all: Copy of all domains for reference
        domains_to_analyze: List of domains to analyze (if None, analyze all domains)
    """
    print("========================================")
    print("DETERMINE_REJECTION_REASONS FUNCTION CALLED")
    print(f"Received dataframe with {len(df_final)} rows")
    if domains_to_analyze:
        print(f"Will analyze {len(domains_to_analyze)} specified domains")
    print("========================================")

    # Make a copy to avoid modifying the original
    df = df_final.copy()

    # Filter to only include specified domains if provided
    if domains_to_analyze:
        df = df[df['Name'].str.lower().isin([d.lower() for d in domains_to_analyze])].copy()
        print(f"Filtered to {len(df)} domains from the input list")

    # Initialize rejection tracking
    df['Reason'] = ''

    # Process AS column for rejection
    if 'AS' in df.columns:
        try:
            as_values = pd.to_numeric(df['AS'], errors='coerce').fillna(0)
            mask = as_values < 5
            df.loc[mask, 'Reason'] += "Low Authority Score (AS<5). "
            print(f"Found {mask.sum()} domains with AS < 5")
        except Exception as e:
            print(f"Error checking AS values: {e}")

    # Process SZ column for rejection
    if 'SZ' in df.columns:
        try:
            sz_values = pd.to_numeric(df['SZ'], errors='coerce').fillna(0)
            mask = sz_values > 30
            df.loc[mask, 'Reason'] += "High Spam Score (SZ>30). "
            print(f"Found {mask.sum()} domains with SZ > 30")
        except Exception as e:
            print(f"Error checking SZ values: {e}")

    # Check for prohibited topics in MT
    if 'MT' in df.columns:
        strictly_prohibited = [
            'adult', 'porn', 'xxx', 'sex', 'erotic', 'escort',
            'casino', 'gambling', 'bet', 'poker',
            'viagra', 'cialis', 'pharmacy',
            'warez', 'crack', 'keygen', 'torrent', 'pirate',
            'terrorist', 'extremist', 'supremacist'
        ]

        prohibited_count = 0
        for index, row in df.iterrows():
            mt_content = str(row['MT']).lower()
            found_topics = []

            for topic in strictly_prohibited:
                if re.search(r'\b' + re.escape(topic) + r'\b', mt_content):
                    found_topics.append(topic)

            if found_topics:
                df.at[index, 'Reason'] += f"Prohibited topics: {', '.join(found_topics)}. "
                prohibited_count += 1

        print(f"Found {prohibited_count} domains with prohibited topics")

    # Check for very new domains
    if 'Age' in df.columns:
        try:
            age_values = pd.to_numeric(df['Age'], errors='coerce')
            mask = age_values < 0.25
            df.loc[mask, 'Reason'] += "Extremely new domain (<3 months). "
            print(f"Found {mask.sum()} domains with Age < 0.25 years")
        except Exception as e:
            print(f"Error checking Age values: {e}")

    # Trim trailing spaces from Reason column
    df['Reason'] = df['Reason'].str.strip()

    # Separate accepted and rejected domains
    df_accepted = df[df['Reason'] == ''].copy()
    df_rejected = df[df['Reason'] != ''].copy()

    print(f"\nAccepted domains: {len(df_accepted)}")
    print(f"Rejected domains: {len(df_rejected)}")

    return df_accepted, df_rejected


def prepare_data_for_csv(df):
    """
    Prepares the dataframe for CSV export by ensuring proper data types and formatting.
    
    Args:
        df (pd.DataFrame): DataFrame to prepare for CSV export
        
    Returns:
        pd.DataFrame: Formatted DataFrame ready for CSV export
    """
    df = df.copy()
    
    # Convert numeric columns to appropriate format
    numeric_columns = ['DA', 'AS', 'DR', 'UR', 'TF', 'CF', 'S RD', 'M RD', 'A RD', 
                      'S BL', 'M BL', 'A BL', 'IP\'S', 'SZ', 'Variance', 'Age']
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # Format numeric columns to 2 decimal places
            df[col] = df[col].map('{:.2f}'.format)
    
    # Format percentage columns
    percentage_columns = ['English %', 'Follow %']
    for col in percentage_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].map('{:.2%}'.format)
    
    # Format date columns
    if 'Expiry' in df.columns:
        df['Expiry'] = pd.to_datetime(df['Expiry']).dt.strftime('%Y-%m-%d')
    
    # Clean up any NaN values
    df = df.replace({np.nan: '', pd.NaT: ''})
    
    return df