# data_processing.py
import pandas as pd
import numpy as np
import re
import traceback
from datetime import datetime, timedelta
import os


def create_processed_dataframe(df_merged):
    """
    Process the merged dataframe to create the final dataframe with all metrics.
    Maps source column names to expected column names.

    Args:
        df_merged: DataFrame containing merged Spamzilla and SEMrush data

    Returns:
        DataFrame: Processed dataframe with all metrics and flags in correct order
    """
    print(f"Merged dataframe has {len(df_merged)} rows and {len(df_merged.columns)} columns")
    print("Column names in merged data:", df_merged.columns.tolist())

    # Debug SEMRUSH data mapping
    print("\nDebug SEMRUSH data mapping:")
    semrush_cols = [col for col in df_merged.columns if 'SEM' in col]
    print(f"SEMRUSH columns in merged data: {semrush_cols}")

    # Inspect some SEMRUSH values
    if 'SEM Traffic' in df_merged.columns and 'SEM Keywords' in df_merged.columns:
        print("\nSample SEMRUSH values for 5 rows:")
        for i in range(min(5, len(df_merged))):
            name = df_merged['name'].iloc[i] if 'name' in df_merged.columns else 'Unknown'
            traffic = df_merged['SEM Traffic'].iloc[i]
            keywords = df_merged['SEM Keywords'].iloc[i]
            print(f"  Domain: {name}, SEM Traffic: {traffic}, SEM Keywords: {keywords}")

    # Check if domains with Authority Score (AS) have SEM data
    if 'Authority Score' in df_merged.columns and 'SEM Traffic' in df_merged.columns:
        has_as = df_merged['Authority Score'].notna() & (df_merged['Authority Score'] > 0)
        has_sem = df_merged['SEM Traffic'].notna() & (df_merged['SEM Traffic'] > 0)
        both = has_as & has_sem
        print(f"\nDomains with both AS and SEM data: {both.sum()} of {len(df_merged)}")

        # Sample of domains with AS but no SEM data
        as_no_sem = has_as & ~has_sem
        print(f"Domains with AS but no SEM data: {as_no_sem.sum()} of {len(df_merged)}")
        if as_no_sem.sum() > 0:
            print("Sample domains with AS but no SEM data:")
            sample = df_merged[as_no_sem].head(3)
            for _, row in sample.iterrows():
                name = row['name'] if 'name' in row else 'Unknown'
                as_val = row['Authority Score']
                traffic = row['SEM Traffic']
                print(f"  Domain: {name}, AS: {as_val}, SEM Traffic: {traffic}")

    # Create a copy to avoid modifying the original
    df = df_merged.copy()

    # Standardize domain name column
    if 'name' in df.columns:
        df = df.rename(columns={'name': 'Name'})
        print("Renamed 'name' column to 'Name'")

    # Map source data columns to expected columns
    # Based on the terminal output, here's how the columns should map
    column_mapping = {
        # Domain name (already handled above)
        # 'Name': 'Name',

        # Source/auction info
        'Source': 'Source',  # Source/auction site information

        # Authority metrics
        'Moz DA': 'DA',
        'Authority Score': 'AS',  # SEMrush Authority Score
        'Ahrefs DR': 'DR',
        'Ahrefs UR': 'UR',
        'TF': 'TF',  # Already matches
        'CF': 'CF',  # Already matches

        # Referring domains
        'SEM Keywords': 'S RD',  # Assuming S RD is SEMrush RD
        'Majestic RD': 'M RD',  # Majestic Referring Domains
        'Ahrefs RD': 'A RD',  # Ahrefs Referring Domains

        # Backlinks
        'SEM Traffic': 'S BL',  # Assuming S BL is SEMrush BL
        'Majestic BL': 'M BL',  # Majestic Backlinks
        'Ahrefs BL': 'A BL',  # Ahrefs Backlinks
        'IPs': 'IP\'S',  # IP addresses

        # Spam Score and other metrics
        'SZ Score': 'SZ',  # SpamZilla Score
        'Age': 'Age',  # Already matches
        'Google Index': 'Indexed',  # Google indexing status
        'SZ Drops': 'Drops',  # Number of drops
        'Majestic Topics': 'MT',  # Majestic Topics

        # Additional metrics
        'Follow links': 'Follow %',  # Will need calculation

        # Expiry date
        'Expires': 'Expiry'  # Domain expiry date
    }

    # Create a dictionary to track what mappings were applied
    applied_mappings = {}

    # Apply column mappings where source columns exist
    for source_col, target_col in column_mapping.items():
        if source_col in df.columns:
            df[target_col] = df[source_col]
            applied_mappings[target_col] = source_col
            print(f"Mapped '{source_col}' to '{target_col}'")

    # Fix for SEMRUSH data - use Domains and Backlinks from SEMrush directly
    print("\nUpdating SEMRUSH column mappings...")
    if 'Domains' in df_merged.columns:
        df['S RD'] = df_merged['Domains']  # SEMRUSH referring domains
        print("Mapped 'Domains' to 'S RD'")
    if 'Backlinks' in df_merged.columns:
        df['S BL'] = df_merged['Backlinks']  # SEMRUSH backlinks
        print("Mapped 'Backlinks' to 'S BL'")

    # Calculate Follow % if we have the necessary columns
    if 'Follow links' in df.columns and 'Nofollow links' in df.columns:
        try:
            follow = pd.to_numeric(df['Follow links'], errors='coerce').fillna(0)
            nofollow = pd.to_numeric(df['Nofollow links'], errors='coerce').fillna(0)
            total = follow + nofollow
            # Avoid division by zero
            df['Follow %'] = np.where(total > 0, follow / total, 0)
            print("Calculated 'Follow %' from 'Follow links' and 'Nofollow links'")
        except Exception as e:
            print(f"Error calculating 'Follow %': {e}")

    # Calculate S (BL/RD) and M (BL/RD) ratios if we have the necessary columns
    # S (BL/RD) - SEMrush Backlinks to Referring Domains ratio
    if 'S BL' in df.columns and 'S RD' in df.columns:
        try:
            s_bl = pd.to_numeric(df['S BL'], errors='coerce').fillna(0)
            s_rd = pd.to_numeric(df['S RD'], errors='coerce').fillna(0)
            df['S (BL/RD)'] = np.where(s_rd > 0, s_bl / s_rd, 0)
            print("Calculated 'S (BL/RD)' ratio")
        except Exception as e:
            print(f"Error calculating 'S (BL/RD)': {e}")

    # M (BL/RD) - Majestic Backlinks to Referring Domains ratio
    if 'M BL' in df.columns and 'M RD' in df.columns:
        try:
            m_bl = pd.to_numeric(df['M BL'], errors='coerce').fillna(0)
            m_rd = pd.to_numeric(df['M RD'], errors='coerce').fillna(0)
            df['M (BL/RD)'] = np.where(m_rd > 0, m_bl / m_rd, 0)
            print("Calculated 'M (BL/RD)' ratio")
        except Exception as e:
            print(f"Error calculating 'M (BL/RD)': {e}")

    # Sample of Majestic Languages data for debugging
    print("\nSample of 5 Majestic Languages entries:")
    if 'Majestic Languages' in df.columns:
        for i in range(min(5, len(df))):
            print(f"  {df['Majestic Languages'].iloc[i]}")

    # Improved English percentage extraction - no defaults
    if 'Majestic Languages' in df.columns:
        try:
            print("Extracting English % from Majestic Languages (no defaults)...")
            english_count = 0
            for i, row in df.iterrows():
                lang_data = str(row['Majestic Languages']).lower()
                if 'english' in lang_data:
                    # Try more patterns to extract percentage
                    # Pattern 1: "english: 85%"
                    match1 = re.search(r'english:?\s*(\d+)%', lang_data)
                    # Pattern 2: "english (85%)"
                    match2 = re.search(r'english\s*\((\d+)%\)', lang_data)
                    # Pattern 3: "85% english"
                    match3 = re.search(r'(\d+)%\s*english', lang_data)

                    if match1:
                        df.at[i, 'English %'] = match1.group(1) + '%'
                        english_count += 1
                    elif match2:
                        df.at[i, 'English %'] = match2.group(1) + '%'
                        english_count += 1
                    elif match3:
                        df.at[i, 'English %'] = match3.group(1) + '%'
                        english_count += 1
                    # No else clause - no default value if percentage can't be extracted
                # No else clause - leave empty if no English mentioned

            print(f"  Found {english_count} domains with explicit English language percentages")

            # Print a sample of the extracted percentages
            print("Sample of 5 extracted English percentages:")
            english_indices = [i for i, v in enumerate(df['English %'].notna()) if v]
            sample_indices = english_indices[:min(5, len(english_indices))] if english_indices else []
            for i in sample_indices:
                print(
                    f"  Domain: {df['Name'].iloc[i]}, English %: {df['English %'].iloc[i]}, Source: {df['Majestic Languages'].iloc[i]}")

        except Exception as e:
            print(f"Error extracting 'English %': {e}")
            traceback.print_exc()

    # Alternative: try Site Languages if English % is empty
    if 'Site Languages' in df.columns:
        try:
            # Only process rows that don't already have English % data
            mask = df['English %'].isna() | (df['English %'] == '')
            if mask.sum() > 0:
                print(f"Trying to extract English % from Site Languages for {mask.sum()} domains...")
                extracted_count = 0

                for i in df.index[mask]:
                    lang_data = str(df.at[i, 'Site Languages']).lower()
                    if 'english' in lang_data:
                        # Try to extract percentage if available
                        match = re.search(r'english[:\s-]+(\d+)%', lang_data)
                        if match:
                            df.at[i, 'English %'] = match.group(1) + '%'
                            extracted_count += 1

                print(f"  Extracted {extracted_count} additional English percentages from Site Languages")
        except Exception as e:
            print(f"Error extracting 'English %' from 'Site Languages': {e}")

    # Calculate Variance between authority metrics
    if all(col in df.columns for col in ['DA', 'AS', 'DR']):
        try:
            # Convert to numeric for calculation
            da_values = pd.to_numeric(df['DA'], errors='coerce').fillna(0)
            as_values = pd.to_numeric(df['AS'], errors='coerce').fillna(0)
            dr_values = pd.to_numeric(df['DR'], errors='coerce').fillna(0)

            # Calculate variance (max - min)
            df['Variance'] = np.maximum.reduce([da_values, as_values, dr_values]) - np.minimum.reduce(
                [da_values, as_values, dr_values])
            print("Calculated 'Variance' between DA, AS, and DR")
        except Exception as e:
            print(f"Error calculating 'Variance': {e}")

    # Initialize potential spam column
    df['Potentially spam'] = ''

    # Check Majestic Topics (MT) for prohibited topics
    if 'MT' in df.columns:
        # Expanded list of prohibited topics with more variations and keywords
        prohibited_topics = [
            # Adult/Mature content
            'adult', 'porn', 'xxx', 'sex', 'erotic', 'escort', 'dating', 'mature',
            'casino', 'gambling', 'bet', 'poker', 'slots', 'lottery', 'wager', 'bingo',

            # Pharmaceutical/Drugs
            'pharmacy', 'drug', 'pill', 'medication', 'prescription', 'med', 'pharma',
            'viagra', 'cialis', 'supplement', 'weight loss',

            # Gambling
            'casino', 'gambling', 'bet', 'betting', 'poker', 'slot', 'slots', 'roulette',
            'blackjack', 'lottery', 'wager', 'wagering', 'bookmaker', 'sportsbook',

            # Loans/Financial schemes
            'loan', 'payday', 'credit', 'debt', 'mortgage', 'finance', 'cash advance',
            'quick cash', 'fast money', 'easy money', 'pawnshop',

            # Questionable practices
            'hack', 'crack', 'keygen', 'warez', 'torrent', 'pirate', 'bootleg',
            'counterfeit', 'fake', 'replica', 'piracy', 'cheat',

            # Political/Controversial
            'politic', 'racism', 'extremist', 'partisan', 'supremacist', 'terrorist',
            'propaganda', 'conspiracy', 'radical',
        ]

        # Check if MT contains any prohibited topics (case insensitive)
        df['MT'] = df['MT'].fillna('').astype(str)
        for index, row in df.iterrows():
            mt_content = row['MT'].lower()
            found_topics = []

            for topic in prohibited_topics:
                # Use word boundary matching to avoid partial matches
                if re.search(r'\b' + re.escape(topic) + r'\b', mt_content):
                    found_topics.append(topic)

            if found_topics:
                df.at[index, 'Potentially spam'] += f"Questionable Majestic topics: {', '.join(found_topics)}. "

    # Check name for potential personal names
    df['Name'] = df['Name'].fillna('').astype(str)
    name_pattern = r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'
    for index, row in df.iterrows():
        domain = row['Name'].lower()
        # Remove TLD and common domain parts for name checking
        cleaned_domain = re.sub(r'\.(com|net|org|io|co|us|uk|de|fr|info|biz|xyz|site|online)$', '', domain)

        # Split by common separators
        parts = re.split(r'[-_.]', cleaned_domain)

        # Check for first+last name pattern in domain parts
        if any(re.search(name_pattern, part, re.IGNORECASE) for part in parts):
            df.at[index, 'Potentially spam'] += "Possible personal name in domain. "

    # Check for age (domains less than 6 months old might be risky)
    if 'Age' in df.columns:
        try:
            age_values = pd.to_numeric(df['Age'], errors='coerce')
            for index, age in enumerate(age_values):
                if not pd.isna(age) and age < 0.5:  # Less than 6 months
                    df.at[index, 'Potentially spam'] += f"Very new domain (Age: {age} years). "
        except Exception as e:
            print(f"Error processing Age column: {e}")

    # Check for very high spam scores - changed threshold to 20+
    if 'SZ' in df.columns:
        try:
            sz_values = pd.to_numeric(df['SZ'], errors='coerce')
            for index, sz in enumerate(sz_values):
                if not pd.isna(sz) and sz > 20:  # Changed threshold to 20+
                    df.at[index, 'Potentially spam'] += f"High spam score (SZ: {sz}). "
        except Exception as e:
            print(f"Error processing SZ column: {e}")

    # Check for large discrepancies between metrics - changed threshold to 40
    if 'Variance' in df.columns:
        try:
            variance_values = pd.to_numeric(df['Variance'], errors='coerce')
            for index, variance in enumerate(variance_values):
                if not pd.isna(variance) and variance > 40:  # Changed threshold to 40
                    df.at[index, 'Potentially spam'] += f"High variance between metrics ({variance}). "
        except Exception as e:
            print(f"Error processing Variance: {e}")

    # Process expiry dates - add 10 hours to all expiry dates
    if 'Expiry' in df.columns:
        try:
            # Convert to datetime first (if not already)
            df['Expiry'] = pd.to_datetime(df['Expiry'], errors='coerce')

            # Add 10 hours to non-null dates
            mask = ~df['Expiry'].isna()
            if any(mask):
                df.loc[mask, 'Expiry'] = df.loc[mask, 'Expiry'] + pd.Timedelta(hours=10)
            print("Added 10 hours to Expiry dates")
        except Exception as e:
            print(f"Error processing Expiry dates: {e}")

    # Trim trailing spaces from Potentially spam column
    df['Potentially spam'] = df['Potentially spam'].str.strip()

    # Print out mappings that were applied for debugging
    print("\nActual column mappings applied:")
    for target, source in applied_mappings.items():
        print(f"  {source} → {target}")

    # Reorder columns to match required format
    # First ensure all required columns exist (with empty values if needed)
    required_columns = [
        'Name', 'Source', 'Potentially spam', 'DA', 'AS', 'DR', 'UR', 'TF', 'CF',
        'S RD', 'M RD', 'A RD', 'S BL', 'M BL', 'A BL', 'IP\'S', 'SZ', 'Variance',
        'Follow %', 'S (BL/RD)', 'M (BL/RD)', 'Age', 'Indexed', 'Drops', 'MT',
        'English %', 'Expiry'
    ]

    # Create missing columns but keep existing ones as they are
    for col in required_columns:
        if col not in df.columns:
            print(f"Creating missing column: {col}")
            df[col] = ''

    # Print info about the processed dataframe
    print(f"\nProcessed dataframe has {len(df)} rows")
    print("Column types after processing:")
    for col in required_columns:
        if col in df.columns:
            print(f"  {col}: {df[col].dtype}")

    # Return DataFrame with columns in specified order
    return df[required_columns]


def determine_rejection_reasons(df_final, df_all):
    """
    Determine which domains should be rejected and track the reasons.

    Args:
        df_final: The processed dataframe with all domains
        df_all: Copy of all domains for reference

    Returns:
        tuple: (accepted_df, rejected_df) with rejected domains and their reasons
    """
    print("========================================")
    print("DETERMINE_REJECTION_REASONS FUNCTION CALLED")
    print(f"Received dataframe with {len(df_final)} rows")
    print("========================================")

    # Make a copy to avoid modifying the original
    df = df_final.copy()

    # Initialize rejection tracking if not already present
    if 'Reason' not in df.columns:
        df['Reason'] = ''

    # Process AS column for rejection
    if 'AS' in df.columns:
        try:
            as_values = pd.to_numeric(df['AS'], errors='coerce').fillna(0)
            mask = as_values < 5  # Using threshold of 5
            df.loc[mask, 'Reason'] += "Low Authority Score (AS<5). "
            print(f"Found {mask.sum()} domains with AS < 5")
        except Exception as e:
            print(f"Error checking AS values: {e}")

    # Process SZ column for rejection
    if 'SZ' in df.columns:
        try:
            sz_values = pd.to_numeric(df['SZ'], errors='coerce').fillna(0)
            mask = sz_values > 30  # Using threshold of 30
            df.loc[mask, 'Reason'] += "High Spam Score (SZ>30). "
            print(f"Found {mask.sum()} domains with SZ > 30")
        except Exception as e:
            print(f"Error checking SZ values: {e}")

    # Process English % column - only check domains with actual percentage values
    if 'English %' in df.columns:
        try:
            # Only process rows that have an English % value
            mask = df['English %'].notna() & (df['English %'] != '')
            if mask.sum() > 0:
                # Convert only the rows with values
                eng_df = df.loc[mask].copy()
                eng_values = eng_df['English %'].str.rstrip('%').astype('float') / 100
                low_eng_mask = eng_values < 0.5  # Less than 50% English

                # Only mark domains with actual low English percentage
                for idx in eng_df.index[low_eng_mask]:
                    df.at[idx, 'Reason'] += "Low English content (<50%). "

                print(
                    f"Found {low_eng_mask.sum()} domains with English < 50% (out of {mask.sum()} domains with English data)")
            else:
                print("No domains have English percentage data")

        except Exception as e:
            print(f"Error checking English values: {e}")
            traceback.print_exc()

    # Process Drops column
    if 'Drops' in df.columns:
        try:
            drops_values = pd.to_numeric(df['Drops'], errors='coerce')
            mask = drops_values > 2
            df.loc[mask, 'Reason'] += "Too many drops (>2). "
            print(f"Found {mask.sum()} domains with Drops > 2")
        except Exception as e:
            print(f"Error checking Drops values: {e}")

    # Check for prohibited topics in MT
    if 'MT' in df.columns:
        # Expanded list of strictly prohibited topics
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
            mask = age_values < 0.25  # Less than 3 months
            df.loc[mask, 'Reason'] += "Extremely new domain (<3 months). "
            print(f"Found {mask.sum()} domains with Age < 0.25 years")
        except Exception as e:
            print(f"Error checking Age values: {e}")

    # Check for domains present in previous day's analysis
    if 'In_Previous_Day' in df.columns:
        previous_day_count = df['In_Previous_Day'].sum()
        print(f"Found {previous_day_count} domains present in previous day's analysis")

    # Trim trailing spaces from Reason column
    df['Reason'] = df['Reason'].str.strip()

    # Separate accepted and rejected domains
    df_rejected = df[df['Reason'] != ''].copy()
    df_accepted = df[df['Reason'] == ''].copy()

    print(f"Split into {len(df_accepted)} accepted and {len(df_rejected)} rejected domains")

    # Drop the Reason column from accepted domains
    df_accepted = df_accepted.drop('Reason', axis=1)
    if 'In_Previous_Day' in df_accepted.columns:
        df_accepted = df_accepted.drop('In_Previous_Day', axis=1)

    # Ensure both dataframes have the correct column order
    accepted_columns = [
        'Name', 'Source', 'Potentially spam', 'DA', 'AS', 'DR', 'UR', 'TF', 'CF',
        'S RD', 'M RD', 'A RD', 'S BL', 'M BL', 'A BL', 'IP\'S', 'SZ', 'Variance',
        'Follow %', 'S (BL/RD)', 'M (BL/RD)', 'Age', 'Indexed', 'Drops', 'MT',
        'English %', 'Expiry'
    ]

    rejected_columns = [
        'Name', 'Source', 'Reason', 'DA', 'AS', 'DR', 'UR', 'TF', 'CF',
        'S RD', 'M RD', 'A RD', 'S BL', 'M BL', 'A BL', 'IP\'S', 'SZ', 'Variance',
        'Follow %', 'S (BL/RD)', 'M (BL/RD)', 'Age', 'Indexed', 'Drops', 'MT',
        'English %', 'Expiry'
    ]

    # Ensure all columns exist in both dataframes
    for col in accepted_columns:
        if col not in df_accepted.columns:
            df_accepted[col] = ''

    for col in rejected_columns:
        if col not in df_rejected.columns:
            df_rejected[col] = ''

    print("Completed determine_rejection_reasons function")
    # Return dataframes with columns in the specified order
    return df_accepted[accepted_columns], df_rejected[rejected_columns]


def prepare_data_for_csv(df_accepted, df_rejected):
    """
    Prepares the dataframes for CSV export by ensuring proper data types and formatting.
    
    Args:
        df_accepted (pd.DataFrame): Accepted domains DataFrame to prepare for CSV export
        df_rejected (pd.DataFrame): Rejected domains DataFrame to prepare for CSV export
        
    Returns:
        tuple: (df_accepted, df_rejected, df_spam_test) formatted DataFrames ready for CSV export
    """
    def format_df(df):
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
    
    # Format both dataframes
    df_accepted = format_df(df_accepted)
    df_rejected = format_df(df_rejected)
    
    # Create spam test dataframe (copy of accepted domains)
    df_spam_test = df_accepted.copy()
    
    return df_accepted, df_rejected, df_spam_test


def generate_rejection_analysis(accepted_df, rejected_df, output_dir, timestamp):
    """
    Generates a detailed analysis report of domain rejections and acceptance ratios.
    
    Args:
        accepted_df (pd.DataFrame): DataFrame containing accepted domains
        rejected_df (pd.DataFrame): DataFrame containing rejected domains
        output_dir (str): Directory to save the analysis report
        timestamp (str): Timestamp for the filename
        
    Returns:
        str: Path to the created analysis file
    """
    total_domains = len(accepted_df) + len(rejected_df)
    acceptance_ratio = len(accepted_df) / total_domains * 100
    rejection_ratio = len(rejected_df) / total_domains * 100
    
    # Analyze rejection reasons
    rejection_reasons = {}
    for reason in rejected_df['Reason']:
        # Split multiple reasons
        reasons = [r.strip() for r in reason.split('.') if r.strip()]
        for r in reasons:
            if r in rejection_reasons:
                rejection_reasons[r] += 1
            else:
                rejection_reasons[r] = 1
    
    # Create analysis report
    report_lines = [
        "DOMAIN ANALYSIS REPORT",
        "=====================",
        f"\nTotal Domains Analyzed: {total_domains}",
        f"Accepted Domains: {len(accepted_df)} ({acceptance_ratio:.2f}%)",
        f"Rejected Domains: {len(rejected_df)} ({rejection_ratio:.2f}%)",
        "\nREJECTION REASONS ANALYSIS",
        "-------------------------",
    ]
    
    # Add rejection reasons with percentages
    for reason, count in sorted(rejection_reasons.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(rejected_df)) * 100
        report_lines.append(f"{reason}: {count} domains ({percentage:.2f}% of rejected)")
    
    # Add multiple rejection reasons analysis
    multiple_reasons = rejected_df[rejected_df['Reason'].str.count('\.') > 0]
    if len(multiple_reasons) > 0:
        report_lines.extend([
            "\nMULTIPLE REJECTION REASONS",
            "-------------------------",
            f"Domains rejected for multiple reasons: {len(multiple_reasons)} ({len(multiple_reasons)/len(rejected_df)*100:.2f}% of rejected)"
        ])
    
    # Write the report to a file
    filename = f"domain_analysis_{timestamp}.txt"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w') as f:
        f.write('\n'.join(report_lines))
    
    return filepath