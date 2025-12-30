import os
import csv

# List of domains to keep
KEEP_DOMAINS = [
    'nurtureart.org',
    'forestcap.com',
    'earthponds.com',
    'classandtrash.com',
    'gardenguidepost.com',
    'multimedialearning.org',
    'neptunecoffee.com',
    'thecepblog.com'
]

def filter_csv_files_in_place(directory):
    # Iterate through all CSV files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            filepath = os.path.join(directory, filename)
            
            # Read the original file
            with open(filepath, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                headers = next(reader)  # Read headers
                rows = [row for row in reader if row[0] in KEEP_DOMAINS]
            
            # Write back to the same file
            with open(filepath, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                writer.writerows(rows)
            
            print(f"Filtered {filename}: {len(rows)} rows remaining")

# Directories to process
DIRECTORIES_TO_FILTER = [
    'output_domain_price_analysis',
    'SUMMARY'
]

# Process each directory
for directory in DIRECTORIES_TO_FILTER:
    if os.path.exists(directory):
        filter_csv_files_in_place(directory)

print("Filtering complete.")