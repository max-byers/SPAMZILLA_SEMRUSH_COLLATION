import os
import pandas as pd
from datetime import datetime
from pathlib import Path

# Hardcoded dodgy keywords
DODGY_KEYWORDS = {
    'Adult': [
        'xxx', 'porn', 'adult', 'sex', 'escort', 'dating', 'nude', 'naked', 'viagra', 'cialis'
    ],
    'Gambling': [
        'bet', 'casino', 'poker', 'lotto', 'lottery', 'bingo', 'jackpot', 'gamble', 'wager', 'bookie'
    ],
    'Pharmaceutical': [
        'pharmacy', 'drug', 'prescription', 'medication', 'pill', 'tablet', 'capsule', 'antibiotic', 'painkiller', 'supplement'
    ]
}

def analyze_domains_with_debug(df):
    total_domains = len(df)
    unsuitable_domains = 0
    category_matches = {k: 0 for k in DODGY_KEYWORDS}
    detailed_results = []
    debug_flagged = False

    # Print first 10 domains and keywords for troubleshooting
    print("First 10 domains:", df['Name'].head(10).tolist())
    print("First 10 Adult keywords:", DODGY_KEYWORDS['Adult'][:10])
    print("First 10 Gambling keywords:", DODGY_KEYWORDS['Gambling'][:10])
    print("First 10 Pharmaceutical keywords:", DODGY_KEYWORDS['Pharmaceutical'][:10])

    # Print type and length of each domain (first 10)
    for i, row in enumerate(df.head(10).itertuples()):
        domain = getattr(row, 'Name')
        print(f"Domain {i}: '{domain}' (type: {type(domain)}, length: {len(str(domain))})")

    # Sample comparison for a known match
    sample_domain = 'pornstore32.com'
    sample_keyword = 'porn'
    print(f"Sample comparison: '{sample_keyword}' in '{sample_domain}'?", sample_keyword in sample_domain)

    for _, row in df.iterrows():
        domain = str(row['Name']).lower()
        matched_keywords = []
        matched_categories = set()
        for category, keywords in DODGY_KEYWORDS.items():
            for word in keywords:
                if word in domain:
                    matched_keywords.append(word)
                    matched_categories.add(category)
        if matched_keywords:
            debug_flagged = True
            print(f"DEBUG: Domain '{domain}' matched keywords: {matched_keywords} (categories: {list(matched_categories)})")
            unsuitable_domains += 1
            for category in matched_categories:
                category_matches[category] += 1
            detailed_results.append({
                'domain': domain,
                'matched_keywords': ', '.join(matched_keywords),
                'matched_categories': ', '.join(matched_categories)
            })

    if not debug_flagged:
        print("\nTROUBLESHOOTING: No domains were flagged as unsuitable.")
        print("First 5 domains:")
        print(df['Name'].head().tolist())
        print("First 5 Adult keywords:")
        print(DODGY_KEYWORDS['Adult'][:5])
        print("First 5 Gambling keywords:")
        print(DODGY_KEYWORDS['Gambling'][:5])
        print("First 5 Pharmaceutical keywords:")
        print(DODGY_KEYWORDS['Pharmaceutical'][:5])

    print(f"\nSUMMARY: Flagged {unsuitable_domains} out of {total_domains} domains as unsuitable.")
    return {
        'total_domains': total_domains,
        'unsuitable_domains': unsuitable_domains,
        'category_matches': category_matches,
        'detailed_results': detailed_results
    }

def remove_flagged_domains(latest_file, flagged_domains):
    df = pd.read_csv(latest_file)
    initial_count = len(df)
    cleaned_df = df[~df['Name'].str.lower().isin([d.lower() for d in flagged_domains])]
    cleaned_count = len(cleaned_df)
    cleaned_df.to_csv(latest_file, index=False)  # Overwrite the original file
    print(f"\nRemoved {initial_count - cleaned_count} flagged domains. Overwrote the original file: {latest_file}")
    return latest_file

def get_latest_original_export(exports_dir):
    # Only consider files that do not end with '_cleaned.csv'
    export_files = [f for f in exports_dir.glob('*.csv') if not str(f).endswith('_cleaned.csv')]
    if not export_files:
        raise FileNotFoundError('No original export files found.')
    return max(export_files, key=lambda x: x.stat().st_mtime)

def main():
    # Find the most recent original Spamzilla export file (not cleaned)
    exports_dir = Path('SPAMZILLA_DOMAIN_EXPORTS')
    latest_file = get_latest_original_export(exports_dir)
    print(f"Analyzing file: {latest_file}")
    df = pd.read_csv(latest_file)
    results = analyze_domains_with_debug(df)

    # Generate report
    output_dir = Path('DODGY_DOMAIN_NAMES/OUTPUT_SPAMZILLA_DOMAIN_FILES')
    output_dir.mkdir(exist_ok=True)
    date_str = datetime.now().strftime('%Y-%m-%d')
    report_file = output_dir / f"{date_str}_spamzilla_domain_data.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"Domain Analysis Report - {date_str}\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Total Domains Analyzed: {results['total_domains']}\n")
        f.write(f"Unsuitable Domains: {results['unsuitable_domains']}\n")
        f.write(f"Percentage Unsuitable: {(results['unsuitable_domains'] / results['total_domains'] * 100):.2f}%\n\n")
        f.write("Category Breakdown:\n")
        for category, count in results['category_matches'].items():
            f.write(f"{category}: {count} domains\n")
        f.write("\nDetailed Results (Unsuitable Domains):\n")
        f.write("-" * 50 + "\n")
        for entry in results['detailed_results']:
            f.write(f"Domain: {entry['domain']}\n")
            f.write(f"  Matched Keywords: {entry['matched_keywords']}\n")
            f.write(f"  Matched Categories: {entry['matched_categories']}\n\n")
    print(f"\nAnalysis complete. Report saved to: {report_file}")

    # Remove flagged domains and save cleaned file
    flagged_domains = [entry['domain'] for entry in results['detailed_results']]
    remove_flagged_domains(latest_file, flagged_domains)

if __name__ == "__main__":
    main() 