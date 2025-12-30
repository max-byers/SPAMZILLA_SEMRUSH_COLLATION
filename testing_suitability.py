"""
Test script for domain suitability using OpenAI GPT-4 API.
This script analyzes domains from the Spamzilla export file using GPT-4.
"""

import os
import sys
import csv
import pandas as pd
import json
import time
from openai import OpenAI
from collections import defaultdict

# OpenAI API configuration - you should store this securely, not in the script
API_KEY = "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"


# Initialize the OpenAI client
client = OpenAI(api_key=API_KEY)

# Cache for API responses to minimize API calls
response_cache = {}
CACHE_FILE = "domain_suitability_cache.json"

# Load cache if it exists
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, 'r') as f:
            response_cache = json.load(f)
        print(f"Loaded {len(response_cache)} cached responses")
    except Exception as e:
        print(f"Error loading cache: {e}")
        response_cache = {}


def save_cache():
    """Save the response cache to a file"""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(response_cache, f)
        print(f"Saved {len(response_cache)} responses to cache")
    except Exception as e:
        print(f"Error saving cache: {e}")


def check_domain_suitability_with_gpt(domain):
    """
    Use GPT-4 to check if a domain is suitable.
    Returns (is_suitable, reason) tuple.
    """
    # Check cache first to minimize API calls
    if domain in response_cache:
        return response_cache[domain]

    # Prepare the refined prompt for GPT-4
    prompt = f"""Analyze the domain name "{domain}" for suitability based on these criteria:

1. NON-LITERATE WORDS:
   - Flag domains with random letter combinations that don't form recognizable words (e.g., "gjfkdlsx")
   - Exception: If the non-literate portion is 4 letters or less, consider it acceptable
   - Exception: If a domain combines literate words with short non-literate segments, it's acceptable (e.g., "thedjdd")

2. FULL NAMES:
   - Flag domains containing clear first+last name combinations (e.g., "johnsmith.com", "mary-jones.com")
   - Single names by themselves are acceptable

3. LOCATIONS:
   - Flag domains containing geographic locations (cities, countries, regions)
   - Exception: "Australia" and "Melbourne" are allowed locations
   - Flag location acronyms (e.g., "ny" for New York, "la" for Los Angeles)

4. BUSINESS INDICATORS (these make domains SUITABLE):
   - Restaurants: cafe, restaurant, bistro, diner, eatery, grill
   - Services: services, solutions, consulting, agency
   - Retail: shop, store, market, boutique, mart
   - Professional: studio, agency, company, firm, group, inc, llc
   - Specific Industries: brewery, winery, bakery, tech, media

5. CONCEPTUAL VS. SPECIFIC (preference for SUITABLE domains):
   - Prefer broad concepts that allow discussing various topics (e.g., "intelligence", "creative", "digital")
   - Less desirable are very specific items limiting content scope (e.g., "bread", "pencil")

6. BRAND/TRADEMARK CONCERNS:
   - Flag domains that clearly reference major brands or trademarks (e.g., "microsoft", "apple", "google")

Examples of UNSUITABLE domains:
- gjfkdlsx.com (non-literate random letters)
- johnsmith.com (full name)
- berlin-online.org (location)
- applemacbook.com (trademark)

Examples of SUITABLE domains:
- australiatravel.com (allowed location)
- melbournefood.com (allowed location)
- digitalservices.io (business/concept term)
- rootsandwings.com (compound words)
- stadiumsports.com (compound words)
- knowledgelink.com (compound words)
- thefvdv.com (short non-literate segment)

Output your conclusion in JSON format with these fields:
- suitable: true/false
- reason: explanation for why the domain is unsuitable, or null if suitable
- category: "non-literate", "full_name", "location", "trademark", or null if suitable
"""

    # Call the GPT-4 API with rate limiting
    max_retries = 3
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
                model="gpt-4o",  # Using GPT-4o instead of gpt-4
                messages=[
                    {"role": "system",
                     "content": "You are a domain name analyst that determines if domains are suitable based on specific criteria."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,  # Use 0 for more deterministic answers
                response_format={"type": "json_object"}
            )

            # Extract and parse the JSON response
            response_text = completion.choices[0].message.content
            result = json.loads(response_text)

            # Store result in expected format
            is_suitable = result.get('suitable', True)
            reason = result.get('reason') if not is_suitable else None

            # Cache the response
            response_cache[domain] = (is_suitable, reason)

            # Save to cache every 10 domains
            if len(response_cache) % 10 == 0:
                save_cache()

            return is_suitable, reason

        except Exception as e:
            print(f"API error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print("Max retries exceeded, skipping domain")
                return True, f"Error analyzing domain: {e}"


def get_suitability_data(domains, max_domains=None, skip_domains=0):
    """
    Process a list of domains and return suitability data using GPT-4.
    Optionally limit the number of domains to analyze to control API costs.

    Args:
        domains (list): List of domain names to check
        max_domains (int, optional): Maximum number of domains to analyze
        skip_domains (int, optional): Number of domains to skip from the beginning

    Returns:
        dict: Dictionary with domain names as keys and tuples (is_suitable, reason) as values
    """
    results = {}

    # Skip and limit domains if specified
    domains_to_check = domains[skip_domains:]
    if max_domains:
        domains_to_check = domains_to_check[:max_domains]

    print(f"Analyzing {len(domains_to_check)} domains with GPT-4 (skipping first {skip_domains})...")

    # Track statistics for reporting
    stats = {
        "total": len(domains_to_check),
        "unsuitable": 0,
        "reasons": defaultdict(int)
    }

    for i, domain in enumerate(domains_to_check):
        print(f"Analyzing domain {i + 1}/{len(domains_to_check)}: {domain}")
        is_suitable, reason = check_domain_suitability_with_gpt(domain)
        results[domain] = (is_suitable, reason)

        # Update stats
        if not is_suitable:
            stats["unsuitable"] += 1

            # Determine category from reason
            if reason:
                reason_lower = reason.lower()
                if "non-literate" in reason_lower or "random" in reason_lower or "gibberish" in reason_lower:
                    stats["reasons"]["non-literate"] += 1
                elif "full name" in reason_lower or "first name" in reason_lower and "last name" in reason_lower:
                    stats["reasons"]["full_name"] += 1
                elif "location" in reason_lower or "geographic" in reason_lower or "country" in reason_lower or "city" in reason_lower:
                    stats["reasons"]["location"] += 1
                elif "trademark" in reason_lower or "brand" in reason_lower:
                    stats["reasons"]["trademark"] += 1
                else:
                    stats["reasons"]["other"] += 1

    # Save the final cache
    save_cache()

    # Print summary statistics
    if stats["unsuitable"] > 0:
        print("\n===== DOMAIN SUITABILITY ANALYSIS =====")
        print(f"Found {stats['unsuitable']} unsuitable domains out of {stats['total']} total:")
        print(f"- Non-literate words: {stats['reasons']['non-literate']}")
        print(f"- Full names: {stats['reasons']['full_name']}")
        print(f"- Locations: {stats['reasons']['location']}")
        print(f"- Trademarks: {stats['reasons']['trademark']}")
        print(f"- Other reasons: {stats['reasons']['other']}")
        print("=========================================\n")

    return results


try:
    print("\n===== DOMAIN SUITABILITY ANALYSIS USING GPT-4o =====")

    # Path to the CSV file
    csv_file = 'export-133821_2025-04-08-05-55-43.csv'

    # Check if the file exists
    if not os.path.exists(csv_file):
        print(f"Error: File {csv_file} not found. Please make sure the file exists in the current directory.")
        sys.exit(1)

    print(f"Analyzing domains from {csv_file}...")

    # Read the CSV file
    try:
        # First try using pandas
        df = pd.read_csv(csv_file)

        # Check if we have a column that could contain domain names
        domain_col = None

        # Check standard column names for domain names
        for col_name in ['Name', 'name', 'Domain', 'domain', 'URL', 'url']:
            if col_name in df.columns:
                domain_col = col_name
                break

        # If standard names not found, use the first column
        if domain_col is None:
            domain_col = df.columns[0]

        print(f"Using column '{domain_col}' for domain names")

        # Read all domains from the file
        all_domains = df[domain_col].astype(str).tolist()

        # Get a count of already processed domains from the cache
        domains_already_processed = len([d for d in all_domains if d in response_cache])
        print(f"Found {domains_already_processed} domains already analyzed in cache")

        # Get the next batch of domains to process
        max_domains = 25  # Analyze 25 domains at a time
        skip_domains = domains_already_processed  # Skip domains we've already analyzed

        domains_to_check = all_domains[skip_domains:skip_domains + max_domains]
        print(
            f"Analyzing next {len(domains_to_check)} domains (domains {skip_domains + 1} to {skip_domains + len(domains_to_check)})")

        # Analyze the domains
        suitability_results = get_suitability_data(all_domains, max_domains, skip_domains)

    except Exception as e:
        print(f"Error reading with pandas: {e}")
        print("Trying with CSV modules...")

        # Fallback to using CSV modules
        all_domains = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            csv_reader = csv.reader(f)
            header = next(csv_reader)  # Skip header row

            # Read all domains from the first column
            for row in csv_reader:
                if row:  # Ensure the row has data
                    all_domains.append(row[0])

        # Get a count of already processed domains from the cache
        domains_already_processed = len([d for d in all_domains if d in response_cache])
        print(f"Found {domains_already_processed} domains already analyzed in cache")

        # Get the next batch of domains to process
        max_domains = 25  # Analyze 25 domains at a time
        skip_domains = domains_already_processed  # Skip domains we've already analyzed

        domains_to_check = all_domains[skip_domains:skip_domains + max_domains]
        print(
            f"Analyzing next {len(domains_to_check)} domains (domains {skip_domains + 1} to {skip_domains + len(domains_to_check)})")

        # Analyze the domains
        suitability_results = get_suitability_data(all_domains, max_domains, skip_domains)

    # Process and display results
    suitable_domains = []
    unsuitable_domains = []

    for domain, (is_suitable, reason) in suitability_results.items():
        if is_suitable:
            suitable_domains.append(domain)
        else:
            unsuitable_domains.append((domain, reason))

    # Create categories for reporting
    categories = {
        "non-literate": [],
        "full_name": [],
        "location": [],
        "trademark": [],
        "other": []
    }

    # Categorize unsuitable domains
    for domain, reason in unsuitable_domains:
        if reason:
            reason_lower = reason.lower()
            if "non-literate" in reason_lower or "random" in reason_lower or "gibberish" in reason_lower:
                categories["non-literate"].append((domain, reason))
            elif "full name" in reason_lower or ("first name" in reason_lower and "last name" in reason_lower):
                categories["full_name"].append((domain, reason))
            elif "location" in reason_lower or "geographic" in reason_lower or "country" in reason_lower or "city" in reason_lower:
                categories["location"].append((domain, reason))
            elif "trademark" in reason_lower or "brand" in reason_lower:
                categories["trademark"].append((domain, reason))
            else:
                categories["other"].append((domain, reason))

    # Print detailed results
    print("\n===== DOMAIN SUITABILITY ANALYSIS RESULTS =====")
    print(f"Total domains analyzed in this batch: {len(suitability_results)}")
    print(f"Suitable domains: {len(suitable_domains)} ({len(suitable_domains) / len(suitability_results):.1%})")
    print(f"Unsuitable domains: {len(unsuitable_domains)} ({len(unsuitable_domains) / len(suitability_results):.1%})")

    # Print top 10 suitable domains for reference
    print("\nSample of suitable domains:")
    for i, domain in enumerate(suitable_domains[:10]):
        print(f"  {i + 1}. {domain}")
    if len(suitable_domains) > 10:
        print(f"  ... and {len(suitable_domains) - 10} more")

    print("\nDomains by rejection category:")
    for category, domain_list in categories.items():
        if len(suitability_results) > 0:
            percentage = len(domain_list) / len(suitability_results)
        else:
            percentage = 0
        print(f"- {category}: {len(domain_list)} domains ({percentage:.1%})")

    # Print sample domains from each category
    print("\nSample unsuitable domains by category:")
    for category, domain_list in categories.items():
        if domain_list:
            print(f"\n{category.upper()}:")
            for i, (domain, reason) in enumerate(domain_list[:5]):  # Show up to 5 samples
                print(f"  {i + 1}. {domain} - {reason}")

            if len(domain_list) > 5:
                print(f"  ... and {len(domain_list) - 5} more")

    print("===================================")

    # Tell the user how many domains have been analyzed in total
    total_analyzed = len(response_cache)
    print(
        f"\nTotal domains analyzed so far: {total_analyzed}/{len(all_domains)} ({total_analyzed / len(all_domains):.1%})")
    print(f"Run this script again to analyze the next batch of domains.")

except Exception as e:
    print(f"Error running analysis: {e}")
    import traceback

    traceback.print_exc()
finally:
    # Always save the cache when exiting
    save_cache()