# Spam Checker

A Python tool for processing and analyzing Spamzilla CSV export files to identify spam domains.

## Features

- Processes Spamzilla CSV export files
- Identifies spam domains based on keywords and patterns
- Consolidates multiple rows per domain into a single row
- Generates detailed reports with spam classification
- Supports collating multiple CSV files from date-based folders
- Organizes output files in a dedicated output directory

## Directory Structure

```
spam_checker/
├── main.py           # Main processing script
├── collator.py       # CSV file collation script
├── utils.py          # Utility functions
├── requirements.txt  # Python dependencies
├── output/          # Output directory for processed files
│   └── backups/     # Backup directory for existing files
└── README.md        # This file
```

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd spam_checker
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Processing a Single CSV File

To process a single Spamzilla CSV export file:

```bash
python main.py input_file.csv [output_file.csv]
```

If no output file is specified, it will generate a file named `YYYYMMDD_spam_checker.csv` in the output directory.

### Collating Multiple CSV Files

To collate multiple CSV files from date-based folders:

```bash
python collator.py
```

This will:
1. Find all folders matching the pattern `[date]_spam_checker`
2. Combine all CSV files in each folder
3. Create a collated file named `[date]_collated.csv` in the output directory

## Input File Format

The input CSV file should contain at least these columns:
- `Domain Name`
- `Spam message`

Optional columns:
- `Ahrefs Domain Rating`
- `SZ Score`

## Output File Format

The output CSV file contains these columns:
- `Domain Name`: The domain being checked
- `Flagged`: Any flagged items found in the spam messages
- `Message`: The processed spam message content
- `Spam`: Binary indicator (0 or 1) if the domain is marked as spam
- `Potential Spam`: Any potential spam messages found
- `Ahrefs DR`: The Ahrefs Domain Rating if available
- `SZ Score`: The Spamzilla score if available

## Output Directory

All processed files are stored in the `output` directory:
- Processed files are named `YYYYMMDD_spam_checker.csv`
- Collated files are named `YYYYMMDD_collated.csv`
- Backups of existing files are stored in `output/backups` with timestamps

## Logging

The tool creates a log file `spamzilla_transformer.log` with detailed information about the processing steps and any errors encountered.

## Error Handling

- The tool creates backups of existing files before overwriting them
- Detailed error messages are logged to both console and log file
- Failed operations are handled gracefully with appropriate error messages 