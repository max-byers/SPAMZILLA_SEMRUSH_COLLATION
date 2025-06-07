import requests
import time
import os
import csv
from datetime import datetime

# --- YOUR GOOGLE API SETUP ---
API_KEY = "AIzaSyCgisj5V2n6RRfMN_BbmAZ-qk4MWsC1f9A"
CSE_ID = "73119d70c3f674328"
# -----------------------------

# --- FUNCTION TO CHECK IF DOMAIN IS INDEXED ---
def is_indexed(domain):
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={CSE_ID}&q=site:{domain}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return "Indexed" if "items" in data else "Not Indexed"
    else:
        return f"Error {response.status_code}"

# --- FUNCTION TO APPEND RESULTS TO EXISTING CSV ---
def append_to_existing_csv(filename, results):
    # Check if file exists
    file_exists = os.path.isfile(filename)
    
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Open file in append mode
    with open(filename, 'a', newline='') as outfile:
        writer = csv.writer(outfile)
        
        # Write header if file is new
        if not file_exists:
            writer.writerow(['timestamp', 'domain', 'indexed'])
        
        # Write results
        for domain, status in results:
            binary_status = 1 if status == "Indexed" else 0
            writer.writerow([timestamp, domain, binary_status])

# --- MAIN WORKFLOW ---
def main():
    input_file = 'input_domains.txt'   # Your input text file
    output_file = 'output_results.csv' # Results file
    binary_file = 'binary_results.csv' # Binary results file
    append_file = 'historical_results.csv'  # File to append results to
    results = []
    binary_results = []

    # Read domains from input TXT
    with open(input_file, 'r') as infile:
        domains = [line.strip() for line in infile if line.strip()]
        print("\nDomains to be processed:")
        for domain in domains:
            print(f"  - {domain}")
        print("\nStarting processing...\n")

    # Check each domain
    for domain in domains:
        status = is_indexed(domain)
        print(f"{domain}: {status}")
        results.append((domain, status))
        # Convert status to binary (1 for indexed, 0 for not indexed)
        binary_status = 1 if status == "Indexed" else 0
        binary_results.append(binary_status)
        time.sleep(1)  # Respect API limits (free tier)

    # Write detailed results to output CSV
    with open(output_file, 'w', newline='') as outfile:
        outfile.write('domain,status\n')
        for domain, status in results:
            outfile.write(f"{domain},{status}\n")

    # Write binary results to separate CSV
    with open(binary_file, 'w', newline='') as outfile:
        outfile.write('indexed\n')
        for status in binary_results:
            outfile.write(f"{status}\n")
            
    # Append results to historical CSV
    append_to_existing_csv(append_file, results)
    print(f"\nResults have been appended to {append_file}")

# --- RUN ---
if __name__ == "__main__":
    main()
