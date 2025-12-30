import pandas as pd
import os
from datetime import datetime, timedelta
from typing import Dict, Tuple, List
import sys

class SpamzillaAnalyzer:
    def __init__(self, input_file: str):
        self.input_file = input_file
        self.df = None
        self.sources = [
            "GoDaddy Auctions",
            "Namecheap Auctions",
            "Namejet Auctions",
            "Namesilo Auctions",
            "Sav.com Auctions"
        ]
        
    def load_data(self) -> bool:
        """Load and validate the input CSV file."""
        try:
            # Read the file in chunks to handle large files
            self.df = pd.read_csv(self.input_file, chunksize=10000)
            self.df = pd.concat(self.df, ignore_index=True)
            
            # Convert expiration date to datetime
            self.df['expiration_date'] = pd.to_datetime(self.df['Expires'])
            
            # Updated column names to match actual Spamzilla export
            required_columns = ['Name', 'Source', 'Ahrefs DR', 'SZ Drops', 'Moz DA', 'Expires']
            if not all(col in self.df.columns for col in required_columns):
                print(f"Error: Missing required columns in {self.input_file}")
                print(f"Found columns: {list(self.df.columns)}")
                return False
                
            print(f"Successfully loaded {len(self.df):,} rows from {self.input_file}")
            return True
        except Exception as e:
            print(f"Error loading file {self.input_file}: {str(e)}")
            return False

    def analyze_sources_by_date(self, date_group: pd.DataFrame) -> Dict[str, int]:
        """Count domains per source for a specific date group."""
        try:
            source_counts = {}
            for source in self.sources:
                count = len(date_group[date_group['Source'].str.contains(source, case=False, na=False)])
                source_counts[source] = count
            return source_counts
        except Exception as e:
            print(f"Error analyzing sources: {str(e)}")
            return {source: 0 for source in self.sources}

    def count_exclusive_domains_by_date(self, date_group: pd.DataFrame) -> Dict[str, int]:
        """Count domains exclusive to each source for a specific date group."""
        try:
            exclusive_counts = {}
            for source in self.sources:
                source_domains = set(date_group[date_group['Source'].str.contains(source, case=False, na=False)]['Name'])
                other_sources = [s for s in self.sources if s != source]
                for other_source in other_sources:
                    other_domains = set(date_group[date_group['Source'].str.contains(other_source, case=False, na=False)]['Name'])
                    source_domains = source_domains - other_domains
                exclusive_counts[source] = len(source_domains)
            return exclusive_counts
        except Exception as e:
            print(f"Error counting exclusive domains: {str(e)}")
            return {source: 0 for source in self.sources}

    def analyze_metrics_by_date(self, date_group: pd.DataFrame) -> Dict[str, Dict[str, Tuple[int, float]]]:
        """Analyze DR, Drops, and DA metrics for a specific date group, broken down by source."""
        try:
            metrics = {}
            
            # Convert columns to numeric, replacing non-numeric values with NaN
            date_group['Ahrefs DR'] = pd.to_numeric(date_group['Ahrefs DR'], errors='coerce')
            date_group['SZ Drops'] = pd.to_numeric(date_group['SZ Drops'], errors='coerce')
            date_group['Moz DA'] = pd.to_numeric(date_group['Moz DA'], errors='coerce')
            
            metric_mapping = {
                'DR': 'Ahrefs DR',
                'Drops': 'SZ Drops',
                'DA': 'Moz DA'
            }
            
            # Initialize metrics for each source
            for source in self.sources:
                metrics[source] = {}
                source_domains = date_group[date_group['Source'].str.contains(source, case=False, na=False)]
                source_total = len(source_domains)
                
                for metric, column in metric_mapping.items():
                    # Calculate metrics for this source
                    source_metric = source_domains[column]
                    count = len(source_metric[source_metric > 1])
                    percentage = (count / source_total) * 100 if source_total > 0 else 0
                    
                    metrics[source][metric] = {
                        'count_gt1': count,
                        'percentage_gt1': percentage
                    }
            
            return metrics
        except Exception as e:
            print(f"Error analyzing metrics: {str(e)}")
            return {source: {metric: {'count_gt1': 0, 'percentage_gt1': 0.0} 
                           for metric in ['DR', 'Drops', 'DA']} 
                   for source in self.sources}

    def generate_report(self) -> None:
        """Generate and save the analysis report grouped by expiration date and source."""
        if not self.load_data():
            return

        try:
            # Create output directory if it doesn't exist
            output_dir = "spamzilla_quantity"
            os.makedirs(output_dir, exist_ok=True)
            
            # Get the first date in the dataset
            first_date = self.df['expiration_date'].min().date()
            last_date = first_date + timedelta(days=6)  # Changed to 6 to get exactly 7 days
            
            # Filter data for the one-week period
            mask = (self.df['expiration_date'].dt.date >= first_date) & (self.df['expiration_date'].dt.date <= last_date)
            filtered_df = self.df[mask]
            
            # Create a date range for all 7 days
            date_range = pd.date_range(start=first_date, end=last_date)
            
            # Group data by expiration date
            grouped_data = filtered_df.groupby(filtered_df['expiration_date'].dt.date)
            
            # Prepare lists to store all rows
            all_rows = []
            zero_metrics_rows = []
            current_date_data = []
            
            # Analyze each date in the range
            for date in date_range:
                date = date.date()
                # Get the group for this date or create an empty group if no data exists
                group = grouped_data.get_group(date) if date in grouped_data.groups else pd.DataFrame(columns=filtered_df.columns)
                
                # Get analysis results for this date
                source_counts = self.analyze_sources_by_date(group)
                exclusive_counts = self.count_exclusive_domains_by_date(group)
                metrics = self.analyze_metrics_by_date(group)
                
                # Create a row for each source
                for source in self.sources:
                    source_key = source.lower().replace(' ', '_')
                    row_data = {
                        'Date': date.strftime('%Y-%m-%d'),
                        'Auctioneer': source,
                        'Total': source_counts[source],
                        'Exclusive': exclusive_counts[source]
                    }
                    
                    # Add metrics for this source
                    for metric in ['DR', 'Drops', 'DA']:
                        metric_data = metrics[source][metric]
                        row_data[metric] = metric_data['count_gt1']
                        row_data[f"{metric}_%"] = round(metric_data['percentage_gt1'])
                    
                    current_date_data.append(row_data)
                    all_rows.append(row_data)
                    
                    # Create zero metrics row if any metric is 0
                    if any(value == 0 for key, value in row_data.items() 
                          if key not in ['Date', 'Auctioneer']):
                        zero_row = row_data.copy()
                        # Replace non-zero values with empty strings
                        for key in zero_row:
                            if key not in ['Date', 'Auctioneer'] and zero_row[key] > 0:
                                zero_row[key] = ''
                        zero_metrics_rows.append(zero_row)
                
                # Add summary row after each date's data
                if current_date_data:
                    summary_row = {
                        'Date': date.strftime('%Y-%m-%d'),
                        'Auctioneer': 'TOTAL',
                        'Total': sum(row['Total'] for row in current_date_data),
                        'Exclusive': sum(row['Exclusive'] for row in current_date_data),
                        'DR': sum(row['DR'] for row in current_date_data),
                        'DR_%': round(sum(row['DR'] for row in current_date_data) / 
                                    sum(row['Total'] for row in current_date_data) * 100 
                                    if sum(row['Total'] for row in current_date_data) > 0 else 0),
                        'Drops': sum(row['Drops'] for row in current_date_data),
                        'Drops_%': round(sum(row['Drops'] for row in current_date_data) / 
                                       sum(row['Total'] for row in current_date_data) * 100 
                                       if sum(row['Total'] for row in current_date_data) > 0 else 0),
                        'DA': sum(row['DA'] for row in current_date_data),
                        'DA_%': round(sum(row['DA'] for row in current_date_data) / 
                                    sum(row['Total'] for row in current_date_data) * 100 
                                    if sum(row['Total'] for row in current_date_data) > 0 else 0)
                    }
                    all_rows.append(summary_row)
                    current_date_data = []  # Reset for next date
            
            # Create DataFrames from all rows
            main_df = pd.DataFrame(all_rows)
            zero_df = pd.DataFrame(zero_metrics_rows)
            
            # Sort both DataFrames
            main_df['sort_key'] = main_df.apply(
                lambda x: (x['Date'], 1 if x['Auctioneer'] == 'TOTAL' else 0, x['Auctioneer']), 
                axis=1
            )
            main_df = main_df.sort_values('sort_key').drop('sort_key', axis=1)
            
            zero_df['sort_key'] = zero_df.apply(
                lambda x: (x['Date'], x['Auctioneer']), 
                axis=1
            )
            zero_df = zero_df.sort_values('sort_key').drop('sort_key', axis=1)
            
            # Create empty columns for separation
            empty_cols = pd.DataFrame('', index=range(max(len(main_df), len(zero_df))), columns=['', ''])
            
            # Combine DataFrames
            combined_df = pd.concat([main_df, empty_cols, zero_df], axis=1)
            
            # Save to CSV
            current_date = datetime.now().strftime('%Y%m%d')
            output_file = os.path.join(output_dir, f"{current_date}_spamzilla_quantity.csv")
            combined_df.to_csv(output_file, index=False)
            
            # Print summary to terminal
            print("\n=== Spamzilla Analysis Results by Expiration Date and Source ===")
            print(f"File: {os.path.basename(self.input_file)}")
            print(f"Analysis Period: {first_date} to {last_date}\n")
            
            for _, row in main_df.iterrows():
                if row['Auctioneer'] == 'TOTAL':
                    print(f"\nDate: {row['Date']}")
                    print("=== TOTAL ===")
                else:
                    print(f"\nDate: {row['Date']}")
                    print(f"Source: {row['Auctioneer']}")
                print(f"Total Domains: {row['Total']:,}")
                print(f"Exclusive Domains: {row['Exclusive']:,}")
                print(f"DR > 1: {row['DR']:,} ({row['DR_%']}%)")
                print(f"Drops > 1: {row['Drops']:,} ({row['Drops_%']}%)")
                print(f"DA > 1: {row['DA']:,} ({row['DA_%']}%)")
            
            print(f"\nResults saved to: {output_file}")
            
        except Exception as e:
            print(f"Error generating report: {str(e)}")

def main():
    # If no input file is specified, use the default test file
    if len(sys.argv) == 1:
        input_file = "test_spamzilla_export.csv"
        print(f"No input file specified. Using default test file: {input_file}")
    elif len(sys.argv) == 2:
        input_file = sys.argv[1]
    else:
        print("Usage: python spamzilla_analyzer.py [input_file]")
        print("If no input file is specified, test_spamzilla_export.csv will be used")
        return
    
    analyzer = SpamzillaAnalyzer(input_file)
    analyzer.generate_report()

if __name__ == "__main__":
    main() 