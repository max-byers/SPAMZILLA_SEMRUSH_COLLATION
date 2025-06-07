import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

class IndustryDetector:
    def __init__(self, keywords_file: str = "industry_keywords.txt"):
        self.keywords_file = Path(__file__).parent / keywords_file
        self.industry_keywords: Dict[str, Set[str]] = {}
        self.load_keywords()

    def load_keywords(self) -> None:
        """Load industry keywords from the keywords file."""
        current_category = None
        with open(self.keywords_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if ',' in line:
                    # This is a line with keywords
                    if current_category:
                        keywords = {k.strip().lower() for k in line.split(',')}
                        self.industry_keywords[current_category] = keywords
                else:
                    # This is a category line
                    current_category = line.strip('# ').lower()

    def analyze_domain(self, domain: str) -> List[Tuple[str, str]]:
        """
        Analyze a domain name for industry-related keywords.
        
        Args:
            domain: The domain name to analyze
            
        Returns:
            List of tuples containing (category, matched_keyword)
        """
        domain = domain.lower()
        # Replace hyphens, underscores, and dots with spaces for easier matching
        normalized = re.sub(r'[-_.]', ' ', domain)
        matches = []
        
        for category, keywords in self.industry_keywords.items():
            for keyword in keywords:
                # Match keyword as a whole word or as a substring separated by hyphens/underscores/dots
                pattern = r'(\b|\s|_|-|\.)' + re.escape(keyword) + r'(\b|\s|_|-|\.)'
                if re.search(pattern, ' ' + normalized + ' '):
                    matches.append((category, keyword))
        
        return matches

    def analyze_domains_from_file(self, input_file: str) -> Dict[str, List[Tuple[str, str]]]:
        """
        Analyze multiple domains from a file.
        
        Args:
            input_file: Path to file containing domains (one per line)
            
        Returns:
            Dictionary mapping domains to their matches
        """
        results = {}
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                domain = line.strip()
                if domain:
                    matches = self.analyze_domain(domain)
                    if matches:
                        results[domain] = matches
        return results

    def generate_report(self, results: Dict[str, List[Tuple[str, str]]], output_file: str) -> None:
        """
        Generate a report of the analysis results.
        
        Args:
            results: Dictionary of analysis results
            output_file: Path to write the report
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Domain Industry Analysis Report\n")
            f.write("=============================\n\n")
            
            for domain, matches in results.items():
                f.write(f"Domain: {domain}\n")
                f.write("Matched Industries:\n")
                for category, keyword in matches:
                    f.write(f"  - {category}: {keyword}\n")
                f.write("\n")

def main():
    detector = IndustryDetector()
    
    # Analyze the domain_list file
    domain_list_path = Path(__file__).parent / "domain_list"
    if domain_list_path.exists():
        print("\n=== Scanning domain_list for industry keywords ===\n")
        results = detector.analyze_domains_from_file(str(domain_list_path))
        if results:
            for domain, matches in results.items():
                print(f"Domain: {domain}")
                print("Matched Industries:")
                for category, keyword in matches:
                    print(f"  - {category}: {keyword}")
                print()
            print(f"Total domains with industry matches: {len(results)}")
        else:
            print("No industry keywords found in domain_list.")
        print("\n=== End of domain_list scan ===\n")
    else:
        print("domain_list file not found in SUITABILITY folder.")

    # Example usage
    test_domains = [
        "plumbing-services.com",
        "gaming-world.net",
        "tech-solutions.org",
        "food-delivery.com",
        "construction-pro.com",
        "medical-clinic.org",
        "auto-repair.net",
        "real-estate-agency.com"
    ]
    
    print("\n=== Domain Industry Analysis Results ===\n")
    
    # Analyze individual domains
    for domain in test_domains:
        matches = detector.analyze_domain(domain)
        if matches:
            print(f"\nDomain: {domain}")
            print("Matched Industries:")
            for category, keyword in matches:
                print(f"  - {category}: {keyword}")
        else:
            print(f"\nDomain: {domain}")
            print("  No industry matches found")
    
    print("\n=== End of Analysis ===\n")

if __name__ == "__main__":
    main() 