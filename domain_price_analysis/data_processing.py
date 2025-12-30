# data_processing.py
import pandas as pd
import numpy as np
import re
import traceback
from datetime import datetime, timedelta


def create_processed_dataframe(df_merged):
    """
    Process the merged dataframe to create the final dataframe with all metrics.
    Only creates columns when there's relevant backlink data present.
    """
    print(f"Merged dataframe has {len(df_merged)} rows and {len(df_merged.columns)} columns")
    print("Column names in merged data:", df_merged.columns.tolist())

    # Create a copy to avoid modifying the original
    df = df_merged.copy()

    # Define all possible columns and their source mappings
    column_mapping = {
        'Name': None,  # Will be set from index
        'Quality domains': 'Quality domains',
        'Quality backlinks': 'Quality backlinks',
        'TF': 'TF',
        'CF': 'CF',
        'TF/CF': None,  # Calculated field
        'DR': 'Ahrefs DR',
        'UR': 'Ahrefs UR',
        'DA': 'Moz DA',
        'AS': 'Authority Score',
        'A RD': 'Ahrefs RD',
        'M RD': 'Majestic RD',
        'S RD': 'SEM Keywords',
        'IP\'S': 'IPs',
        'Age': 'Age',
        'A (BL/RD)': None,  # Calculated field
        'A BL': 'Ahrefs BL',
        'M BL': 'Majestic BL',
        'S BL': 'SEM Traffic',
        'Everything domains': 'Everything domains',
        'Everything backlinks': 'Everything backlinks',
        'SZ': 'SZ Score',
        'Expiry': 'Expires',
        'Source': 'Source'
    }

    # Initialize Name column from index
    df['Name'] = df.index

    # Apply column mappings where source columns exist and have data
    print("\n=== DEBUGGING COLUMN MAPPINGS ===")
    for target_col, source_col in column_mapping.items():
        if source_col and source_col in df.columns:
            # Only create column if there's actual data (not all null/empty)
            if df[source_col].notna().any():
                df[target_col] = df[source_col]
                print(f"Mapped '{source_col}' to '{target_col}'")
                
                # Debug the mapped data for key columns
                if target_col in ['S BL', 'S RD', 'M BL', 'M RD', 'DA', 'AS', 'DR']:
                    mapped_data = df[target_col]
                    print(f"  {target_col} data type: {mapped_data.dtype}")
                    print(f"  {target_col} non-null count: {mapped_data.notna().sum()}")
                    print(f"  {target_col} sample values: {mapped_data.head(3).tolist()}")
            else:
                print(f"Skipping '{target_col}' as '{source_col}' has no data")
        elif source_col is None:
            # For calculated fields, initialize with empty values
            df[target_col] = ''
            print(f"Initialized calculated field '{target_col}' with empty values")
        else:
            print(f"Source column '{source_col}' not found for target '{target_col}'")
    
    print("=== END COLUMN MAPPING DEBUG ===\n")

    # Calculate TF/CF ratio if we have the necessary columns
    print("\n=== DEBUGGING TF/CF CALCULATION ===")
    print(f"  'TF' in columns: {'TF' in df.columns}")
    print(f"  'CF' in columns: {'CF' in df.columns}")

    if 'TF' in df.columns and 'CF' in df.columns:
        try:
            tf_values = pd.to_numeric(df['TF'], errors='coerce').fillna(0)
            cf_values = pd.to_numeric(df['CF'], errors='coerce').fillna(0)
            
            print(f"  TF values (first 5): {tf_values.head().tolist()}")
            print(f"  CF values (first 5): {cf_values.head().tolist()}")
            print(f"  TF non-zero count: {(tf_values > 0).sum()}")
            print(f"  CF non-zero count: {(cf_values > 0).sum()}")
            
            df['TF/CF'] = np.where(cf_values > 0, tf_values / cf_values, 0)
            print(f"  Calculated TF/CF values (first 5): {df['TF/CF'].head().tolist()}")
            print(f"  TF/CF non-zero count: {(df['TF/CF'] > 0).sum()}")
            print("Calculated 'TF/CF' ratio")
        except Exception as e:
            print(f"Error calculating 'TF/CF': {e}")
            print(f"Exception details: {traceback.format_exc()}")
    else:
        print("  Missing required columns for TF/CF calculation")

    # Calculate A (BL/RD) ratio if we have the necessary columns
    print("\n=== DEBUGGING A (BL/RD) CALCULATION ===")
    print(f"  'A BL' in columns: {'A BL' in df.columns}")
    print(f"  'A RD' in columns: {'A RD' in df.columns}")

    if 'A BL' in df.columns and 'A RD' in df.columns:
        try:
            a_bl = pd.to_numeric(df['A BL'], errors='coerce').fillna(0)
            a_rd = pd.to_numeric(df['A RD'], errors='coerce').fillna(0)
            
            print(f"  A BL values (first 5): {a_bl.head().tolist()}")
            print(f"  A RD values (first 5): {a_rd.head().tolist()}")
            print(f"  A BL non-zero count: {(a_bl > 0).sum()}")
            print(f"  A RD non-zero count: {(a_rd > 0).sum()}")
            
            df['A (BL/RD)'] = np.where(a_rd > 0, a_bl / a_rd, 0)
            print(f"  Calculated A (BL/RD) values (first 5): {df['A (BL/RD)'].head().tolist()}")
            print(f"  A (BL/RD) non-zero count: {(df['A (BL/RD)'] > 0).sum()}")
            print("Calculated 'A (BL/RD)' ratio")
        except Exception as e:
            print(f"Error calculating 'A (BL/RD)': {e}")
            print(f"Exception details: {traceback.format_exc()}")
    else:
        print("  Missing required columns for A (BL/RD) calculation")

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

    # Calculate S (BL/RD) and M (BL/RD) ratios if we have the necessary columns
    print("\n=== DEBUGGING RATIO CALCULATIONS ===")
    print(f"Available columns: {df.columns.tolist()}")
    
    # Debug S (BL/RD) ratio calculation
    print(f"\nS (BL/RD) calculation:")
    print(f"  'S BL' in columns: {'S BL' in df.columns}")
    print(f"  'S RD' in columns: {'S RD' in df.columns}")
    
    if 'S BL' in df.columns and 'S RD' in df.columns:
        try:
            s_bl = pd.to_numeric(df['S BL'], errors='coerce').fillna(0)
            s_rd = pd.to_numeric(df['S RD'], errors='coerce').fillna(0)
            
            print(f"  S BL values (first 5): {s_bl.head().tolist()}")
            print(f"  S RD values (first 5): {s_rd.head().tolist()}")
            print(f"  S BL non-zero count: {(s_bl > 0).sum()}")
            print(f"  S RD non-zero count: {(s_rd > 0).sum()}")
            
            df['S (BL/RD)'] = np.where(s_rd > 0, s_bl / s_rd, 0)
            print(f"  Calculated S (BL/RD) values (first 5): {df['S (BL/RD)'].head().tolist()}")
            print(f"  S (BL/RD) non-zero count: {(df['S (BL/RD)'] > 0).sum()}")
            print("Calculated 'S (BL/RD)' ratio")
        except Exception as e:
            print(f"Error calculating 'S (BL/RD)': {e}")
            print(f"Exception details: {traceback.format_exc()}")
    else:
        print("  Missing required columns for S (BL/RD) calculation")

    # Debug M (BL/RD) ratio calculation
    print(f"\nM (BL/RD) calculation:")
    print(f"  'M BL' in columns: {'M BL' in df.columns}")
    print(f"  'M RD' in columns: {'M RD' in df.columns}")
    
    if 'M BL' in df.columns and 'M RD' in df.columns:
        try:
            m_bl = pd.to_numeric(df['M BL'], errors='coerce').fillna(0)
            m_rd = pd.to_numeric(df['M RD'], errors='coerce').fillna(0)
            
            print(f"  M BL values (first 5): {m_bl.head().tolist()}")
            print(f"  M RD values (first 5): {m_rd.head().tolist()}")
            print(f"  M BL non-zero count: {(m_bl > 0).sum()}")
            print(f"  M RD non-zero count: {(m_rd > 0).sum()}")
            
            df['M (BL/RD)'] = np.where(m_rd > 0, m_bl / m_rd, 0)
            print(f"  Calculated M (BL/RD) values (first 5): {df['M (BL/RD)'].head().tolist()}")
            print(f"  M (BL/RD) non-zero count: {(df['M (BL/RD)'] > 0).sum()}")
            print("Calculated 'M (BL/RD)' ratio")
        except Exception as e:
            print(f"Error calculating 'M (BL/RD)': {e}")
            print(f"Exception details: {traceback.format_exc()}")
    else:
        print("  Missing required columns for M (BL/RD) calculation")

    # Calculate Variance between authority metrics
    print(f"\n=== DEBUGGING VARIANCE CALCULATION ===")
    print(f"Required columns for variance: ['DA', 'AS', 'DR']")
    print(f"  'DA' in columns: {'DA' in df.columns}")
    print(f"  'AS' in columns: {'AS' in df.columns}")
    print(f"  'DR' in columns: {'DR' in df.columns}")
    
    if all(col in df.columns for col in ['DA', 'AS', 'DR']):
        try:
            da_values = pd.to_numeric(df['DA'], errors='coerce').fillna(0)
            as_values = pd.to_numeric(df['AS'], errors='coerce').fillna(0)
            dr_values = pd.to_numeric(df['DR'], errors='coerce').fillna(0)
            
            print(f"  DA values (first 5): {da_values.head().tolist()}")
            print(f"  AS values (first 5): {as_values.head().tolist()}")
            print(f"  DR values (first 5): {dr_values.head().tolist()}")
            print(f"  DA non-zero count: {(da_values > 0).sum()}")
            print(f"  AS non-zero count: {(as_values > 0).sum()}")
            print(f"  DR non-zero count: {(dr_values > 0).sum()}")
            
            # Calculate variance (max - min)
            max_values = np.maximum.reduce([da_values, as_values, dr_values])
            min_values = np.minimum.reduce([da_values, as_values, dr_values])
            df['Variance'] = max_values - min_values
            
            print(f"  Max values (first 5): {max_values.head().tolist()}")
            print(f"  Min values (first 5): {min_values.head().tolist()}")
            print(f"  Calculated Variance values (first 5): {df['Variance'].head().tolist()}")
            print(f"  Variance non-zero count: {(df['Variance'] > 0).sum()}")
            print("Calculated 'Variance' between DA, AS, and DR")
        except Exception as e:
            print(f"Error calculating 'Variance': {e}")
            print(f"Exception details: {traceback.format_exc()}")
    else:
        print("  Missing required columns for Variance calculation")
        missing_cols = [col for col in ['DA', 'AS', 'DR'] if col not in df.columns]
        print(f"  Missing columns: {missing_cols}")
    
    print("=== END DEBUGGING ===\n")

    # Remove any columns that are completely empty
    df = df.dropna(axis=1, how='all')
    
    # Debug final state of calculated columns
    print("\n=== FINAL DEBUGGING OF CALCULATED COLUMNS ===")
    calculated_columns = ['S (BL/RD)', 'M (BL/RD)', 'Variance', 'Follow %']
    for col in calculated_columns:
        if col in df.columns:
            print(f"{col}:")
            print(f"  Data type: {df[col].dtype}")
            print(f"  Non-null count: {df[col].notna().sum()}")
            print(f"  Non-zero count: {(df[col] != 0).sum() if df[col].dtype in ['float64', 'int64'] else 'N/A'}")
            print(f"  Sample values: {df[col].head(5).tolist()}")
        else:
            print(f"{col}: Column not found in final dataframe")
    
    print("=== END FINAL DEBUGGING ===\n")
    
    return df


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
    Prepare the dataframe for CSV output by ensuring correct column order and data types.
    """
    from config import REQUIRED_COLUMNS
    
    # Create a new DataFrame with only the required columns in the correct order
    new_df = pd.DataFrame(columns=REQUIRED_COLUMNS)
    
    # Copy data from the original DataFrame to the new one
    for col in REQUIRED_COLUMNS:
        if col in df.columns:
            new_df[col] = df[col]
        else:
            new_df[col] = ''
    
    # Calculate TF/CF ratio
    if 'TF' in df.columns and 'CF' in df.columns:
        tf_values = pd.to_numeric(df['TF'], errors='coerce')
        cf_values = pd.to_numeric(df['CF'], errors='coerce')
        new_df['TF/CF'] = np.where(
            (cf_values > 0) & (tf_values.notna()) & (cf_values.notna()),
            (tf_values / cf_values).round(2),
            ''
        )
    
    # Calculate A (BL/RD) ratio
    if 'A BL' in df.columns and 'A RD' in df.columns:
        a_bl = pd.to_numeric(df['A BL'], errors='coerce')
        a_rd = pd.to_numeric(df['A RD'], errors='coerce')
        new_df['A (BL/RD)'] = np.where(
            (a_rd > 0) & (a_bl.notna()) & (a_rd.notna()),
            (a_bl / a_rd).round(2),
            ''
        )
    
    # Convert numeric columns to appropriate format
    numeric_cols = ['DA', 'AS', 'DR', 'UR', 'TF', 'CF', 'TF/CF',
                   'S RD', 'M RD', 'A RD', 'S BL', 'M BL', 'A BL',
                   'IP\'S', 'A (BL/RD)', 'Everything domains',
                   'Everything backlinks', 'Quality domains', 'Quality backlinks']
    
    for col in numeric_cols:
        if col in new_df.columns:
            new_df[col] = pd.to_numeric(new_df[col], errors='coerce').round(2)
    
    # Format date columns
    if 'Expiry' in new_df.columns:
        new_df['Expiry'] = pd.to_datetime(new_df['Expiry']).dt.strftime('%Y-%m-%d')
    
    # Ensure the DataFrame has exactly the columns we want in the correct order
    return new_df[REQUIRED_COLUMNS]