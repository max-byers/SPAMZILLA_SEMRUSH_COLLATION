import csv
from datetime import datetime
import os

def get_domains_from_text_file(file_path='bidding_strategy/domain_names'):
    """
    Read domains from a text file.
    
    :param file_path: Path to the text file containing domain names
    :return: List of domain names
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Read lines, strip whitespace, and remove any empty lines
            domains = [line.strip() for line in f if line.strip()]
        return sorted(domains)
    except FileNotFoundError:
        print(f"Error: Domain list file not found at {file_path}")
        return []
    except Exception as e:
        print(f"Error reading domain list: {e}")
        return []

def generate_bidding_analysis_csv(domains, output_dir='bidding_strategy'):
    """
    Generate a bidding analysis CSV file with the given domains.
    
    :param domains: List of domain names to include in the analysis
    :param output_dir: Directory to save the output file
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Create filename with current date
    today = datetime.now().strftime('%Y-%m-%d')
    filename = os.path.join(output_dir, f'{today}_bidding_analysis.csv')
    
    # Prepare CSV headers
    headers = ['Domain', 'Project Bid', 'Actual Bid', 'Notes', 'Priority']
    
    # Write the CSV file
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        # Write headers
        csvwriter.writerow(headers)
        
        # Write domains with empty columns
        for domain in domains:
            csvwriter.writerow([domain, '', '', '', ''])
    
    print(f"Bidding analysis CSV generated: {filename}")
    return filename

def main():
    # Get domains from text file
    domains = get_domains_from_text_file()
    
    if domains:
        # Generate the CSV
        generate_bidding_analysis_csv(domains)
    else:
        print("No domains found. CSV generation aborted.")

if __name__ == '__main__':
    main() 