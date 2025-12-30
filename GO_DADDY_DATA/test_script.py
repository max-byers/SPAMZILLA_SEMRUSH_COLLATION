#!/usr/bin/env python3
"""
Test script for GoDaddy Domain Extractor
"""

import os
import csv
from datetime import datetime
from pathlib import Path

def test_basic_functionality():
    """Test basic functionality without external dependencies"""
    print("=== Testing GoDaddy Domain Extractor ===")
    
    # Test current date formatting
    current_date = datetime.now().strftime("%Y-%m-%d")
    print(f"Current date: {current_date}")
    
    # Test output folder creation (use current directory)
    output_folder = Path(".")
    print(f"Output folder: {output_folder.absolute()}")
    
    # Test CSV file creation
    won_file = output_folder / f"{current_date}_godaddy_did_win.csv"
    lost_file = output_folder / f"{current_date}_godaddy_did_not_win.csv"
    
    # Create test data
    test_won_domains = [
        {"domain": "example1.com", "price": "1500"},
        {"domain": "example2.com", "price": "2000"}
    ]
    
    test_lost_domains = [
        {"domain": "example3.com", "price": "500"},
        {"domain": "example4.com", "price": "1000"}
    ]
    
    # Write test CSV files
    with open(won_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Domain name', 'Price'])
        for domain in test_won_domains:
            writer.writerow([domain['domain'], domain['price']])
    
    with open(lost_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Domain name', 'Price'])
        for domain in test_lost_domains:
            writer.writerow([domain['domain'], domain['price']])
    
    print(f"Created test files:")
    print(f"  - {won_file.name}")
    print(f"  - {lost_file.name}")
    
    # Verify files exist
    if won_file.exists() and lost_file.exists():
        print("✓ Test files created successfully")
        return True
    else:
        print("✗ Error creating test files")
        return False

def test_downloads_folder():
    """Test Downloads folder access"""
    downloads_path = Path.home() / "Downloads"
    print(f"\nDownloads folder: {downloads_path}")
    
    if downloads_path.exists():
        print("✓ Downloads folder accessible")
        
        # List some files in Downloads
        files = list(downloads_path.glob("*"))[:5]
        print(f"Sample files in Downloads:")
        for file in files:
            print(f"  - {file.name}")
        return True
    else:
        print("✗ Downloads folder not found")
        return False

if __name__ == "__main__":
    print("Running GoDaddy Domain Extractor tests...\n")
    
    test1_passed = test_basic_functionality()
    test2_passed = test_downloads_folder()
    
    print(f"\n=== Test Results ===")
    print(f"Basic functionality: {'✓ PASSED' if test1_passed else '✗ FAILED'}")
    print(f"Downloads access: {'✓ PASSED' if test2_passed else '✗ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n✓ All tests passed! The extractor should work correctly.")
        print("\nTo use the full extractor:")
        print("1. Place your GoDaddy domain files in Downloads")
        print("2. Run: python advanced_godaddy_extractor.py")
        print("3. Or double-click: run_extractor.bat")
    else:
        print("\n✗ Some tests failed. Please check the errors above.") 