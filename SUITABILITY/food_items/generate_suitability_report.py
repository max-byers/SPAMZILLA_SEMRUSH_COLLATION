from food_domain_checker import analyze_domains
import json
from datetime import datetime

def read_domain_list(file_path):
    """Read domains from the domain list file."""
    with open(file_path, 'r') as f:
        domains = [line.strip() for line in f if line.strip()]
    return domains

def generate_report(domains, results):
    """Generate a detailed report of unsuitable domains."""
    total_domains = len(domains)
    food_related_count = len(results['food_related'])
    food_related_percentage = (food_related_count / total_domains) * 100

    report = f"""DOMAIN SUITABILITY ANALYSIS REPORT
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
=================================================

TOTAL DOMAINS ANALYZED: {total_domains}

FOOD-RELATED DOMAINS:
--------------------
Count: {food_related_count}
Percentage: {food_related_percentage:.2f}%

DETAILED BREAKDOWN:
------------------
"""
    
    # Add food-related domains with their terms
    report += "\nFood-Related Domains:\n"
    for domain in results['food_related']:
        terms = results['found_terms'][domain]
        report += f"- {domain} (terms: {', '.join(terms)})\n"
    
    return report

def main():
    # Read domains
    domains = read_domain_list('SUITABILITY/domain_list')
    
    # Analyze domains
    print("Analyzing domains...")
    results = analyze_domains(domains)
    
    # Generate report
    report = generate_report(domains, results)
    
    # Save report
    output_file = 'domain_suitability_report.txt'
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"Report generated and saved to {output_file}")

if __name__ == "__main__":
    main() 