import os
import glob
import pandas as pd
from collections import defaultdict

def get_latest_collated_file():
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    collated_files = glob.glob(os.path.join(current_dir, 'collated_spamzilla_exports_*.csv'))
    if not collated_files:
        print("No collated Spamzilla exports file found")
        return None
    return max(collated_files, key=os.path.getctime)

def main():
    output_dir = os.path.dirname(os.path.abspath(__file__))
    collated_file = get_latest_collated_file()
    if not collated_file:
        print("No collated file found.")
        return

    # Read the collated CSV
    df = pd.read_csv(collated_file)
    if 'Name' not in df.columns or 'Expires' not in df.columns:
        print("CSV must contain 'Name' and 'Expires' columns.")
        return

    # Parse expiration dates
    df['Expires'] = pd.to_datetime(df['Expires'], errors='coerce')
    df = df.dropna(subset=['Expires'])

    # Group previously sold domains by expiration date
    sold_by_date = defaultdict(list)
    for _, row in df.iterrows():
        domain = str(row['Name']).strip()
        exp_date = row['Expires'].date()
        sold_by_date[exp_date].append(domain)

    # Write one file per expiration date
    for exp_date, domains in sold_by_date.items():
        out_path = os.path.join(output_dir, f"sold_domains_{exp_date}.txt")
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(f"Previously Sold Domains Expiring on {exp_date}\n")
            f.write("=" * 50 + "\n\n")
            for domain in sorted(domains):
                f.write(domain + "\n")
    print(f"Wrote {len(sold_by_date)} files to {output_dir}")

if __name__ == "__main__":
    main() 