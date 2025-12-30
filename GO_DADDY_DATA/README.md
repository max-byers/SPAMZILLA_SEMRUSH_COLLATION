# GoDaddy Domain Extractor

This tool extracts domain names and prices from GoDaddy auction files and creates two CSV files:
- `[date]_godaddy_did_win.csv` - Domains you won
- `[date]_godaddy_did_not_win.csv` - Domains you didn't win

## Features

- Automatically scans your Downloads folder for domain files
- Supports CSV, Excel (.xlsx, .xls), and text files
- Extracts domain names and prices using pattern matching
- Allows manual input of domains
- Interactive editing of extracted data
- Creates properly formatted CSV files

## Quick Start

### Option 1: Run the batch file (Windows)
1. Double-click `run_extractor.bat`
2. Follow the on-screen prompts

### Option 2: Run manually
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the script:
   ```
   python advanced_godaddy_extractor.py
   ```

## How to Use

1. **Place your GoDaddy domain files in your Downloads folder**
   - The script will automatically find files with domain-related content
   - Supported formats: CSV, Excel (.xlsx, .xls), text files

2. **Run the script**
   - Choose from three options:
     - Process all files automatically
     - Select specific files
     - Enter domains manually

3. **Review and edit extracted data**
   - The script will show all extracted domains
   - You can edit prices and status (won/lost)
   - You can delete incorrect entries

4. **Generate CSV files**
   - Two CSV files will be created in the `GO_DADDY_DATA` folder
   - Files are named with the current date

## File Naming Convention

The generated CSV files follow this naming pattern:
- `YYYY-MM-DD_godaddy_did_win.csv`
- `YYYY-MM-DD_godaddy_did_not_win.csv`

## CSV Format

Both files contain the same columns:
- **Domain name**: The domain (e.g., example.com)
- **Price**: The auction price (if available)

## Manual Input Format

When entering domains manually, use this format:
```
domain.com,price,status
```

Examples:
- `example.com,1500,won`
- `test.com,500,lost`
- `sample.com,1000,unknown`

## Troubleshooting

- **No files found**: Make sure your domain files are in the Downloads folder
- **No domains extracted**: Check that your files contain domain names and prices
- **Import errors**: Install the required dependencies with `pip install -r requirements.txt`

## Files Included

- `advanced_godaddy_extractor.py` - Main script with full functionality
- `requirements.txt` - Python dependencies
- `run_extractor.bat` - Windows batch file for easy execution
- `test_script.py` - Test script to verify setup
- `README.md` - This instruction file 