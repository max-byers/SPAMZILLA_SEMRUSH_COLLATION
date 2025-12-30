from food_domain_checker import analyze_domains
import json

def read_domain_list(file_path):
    """Read domains from the domain list file."""
    with open(file_path, 'r') as f:
        # Read lines and strip whitespace
        domains = [line.strip() for line in f if line.strip()]
    return domains

def save_results(results, output_file):
    """Save analysis results to a JSON file."""
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

def main():
    # Read domains from the file
    domains = read_domain_list('SUITABILITY/domain_list')
    
    # Analyze domains
    print(f"Analyzing {len(domains)} domains for food-related terms...")
    results = analyze_domains(domains)
    
    # Print summary
    print(f"\nFound {len(results['food_related'])} food-related domains out of {len(domains)} total domains")
    
    # Print food-related domains with their terms
    print("\nFood-related domains:")
    for domain in results['food_related']:
        terms = results['found_terms'][domain]
        print(f"- {domain} (terms: {', '.join(terms)})")
    
    # Save results to file
    output_file = 'food_domain_analysis.json'
    save_results(results, output_file)
    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    main() 