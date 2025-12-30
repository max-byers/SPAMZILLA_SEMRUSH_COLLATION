File Organization Scripts Documentation
=====================================

This directory contains the main script for organizing downloaded SEMRUSH backlink files.

main.py
-------
Purpose: Central script for organizing today's downloaded SEMRUSH backlink files.
Functionality:
- Creates two folders with today's date:
  * [date]_SEMRUSH_backlinks (for files ending with -backlinks.csv)
  * [date]_SEMRUSH_outbounds (for files ending with -backlinks_outgoing_domains.csv)
- Sources files from C:\Users\Max Byers\Downloads
- Only processes files downloaded today
- Moves files to appropriate folders based on their naming pattern
- Provides detailed logging of all operations
- Generates a summary of processed and skipped files

Usage:
------
1. Run the script from the command line:
   ```
   python main.py
   ```

2. The script will:
   - Create today's date folders
   - Find all CSV files downloaded today in your Downloads folder
   - Move them to the appropriate folders based on their naming pattern
   - Provide a detailed log of all operations

Dependencies:
------------
- Python 3.x
- Standard library modules: os, shutil, datetime, logging
- No external dependencies required 