# Bidding Analysis CSV Generator

## Purpose
This script generates a standardized CSV file for domain bidding analysis. It reads domain names from a text file and creates a CSV with the following columns:
- Domain
- Project Bid
- Actual Bid
- Notes
- Priority

## Usage

### Prerequisites
- Python 3.7+
- No external dependencies beyond standard library

### Preparing Domain List
1. Edit `domain_list.txt` to include your desired domains
2. Each domain should be on a new line
3. Domains will be sorted alphabetically when generating the CSV

### Running the Script
```bash
python create_bidding_analysis.py
```

### Output
The script generates a CSV file in the `bidding_strategy` directory with the current date, e.g., `2025-06-23_bidding_analysis.csv`

## Customization
- Modify `domain_list.txt` to change the list of domains
- Edit `create_bidding_analysis.py` to change file generation logic if needed

## Troubleshooting
- Ensure `domain_list.txt` exists in the same directory as the script
- Check that each domain is on a separate line
- Remove any blank lines or whitespace from the domain list 