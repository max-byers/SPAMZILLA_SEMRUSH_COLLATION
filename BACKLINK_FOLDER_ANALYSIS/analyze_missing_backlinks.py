import os
import sys
import glob

def analyze_missing_backlinks(domain_file):
    # Path to the backlinks folder
    backlinks_folder = "../1_06_SEMRUSH_backlinks"
    
    # Get the base name of the domain file without extension
    base_name = os.path.splitext(os.path.basename(domain_file))[0]
    
    # Read domain names from file
    with open(domain_file, 'r') as f:
        domains = [line.strip() for line in f if line.strip()]
    
    # Get list of existing backlink files
    existing_files = os.listdir(backlinks_folder)
    
    # Find missing files
    missing_files = []
    for domain in domains:
        expected_file = f"{domain}-backlinks.csv"
        if expected_file not in existing_files:
            missing_files.append(domain)
    
    # Write results to a file named after the input file
    output_file = f"missing_files_{base_name}.txt"
    with open(output_file, 'w') as f:
        if missing_files:
            f.write(f"Analysis of {domain_file}:\n")
            f.write("The following domains are missing backlink files:\n\n")
            for domain in missing_files:
                f.write(f"{domain}\n")
            f.write(f"\nTotal missing files: {len(missing_files)}\n")
        else:
            f.write(f"Analysis of {domain_file}:\n")
            f.write("No missing files found. All domains have corresponding backlink files.\n")
    
    return len(missing_files)

def main():
    try:
        # Find all files in the current directory (both with and without extensions)
        all_files = os.listdir('.')
        text_files = [f for f in all_files if f.endswith('.txt') or not os.path.splitext(f)[1]]
        
        if not text_files:
            print("No text files found in the current directory.")
            return
        
        total_missing = 0
        for text_file in text_files:
            if text_file.startswith("missing_files_"):
                continue  # Skip any existing missing files reports
            if text_file == "analyze_missing_backlinks.py":
                continue  # Skip the script file
                
            print(f"Processing {text_file}...")
            missing_count = analyze_missing_backlinks(text_file)
            total_missing += missing_count
            print(f"Completed analysis of {text_file}. Check missing_files_{os.path.splitext(text_file)[0]}.txt for results.")
        
        print(f"\nAnalysis complete. Total missing files across all lists: {total_missing}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 