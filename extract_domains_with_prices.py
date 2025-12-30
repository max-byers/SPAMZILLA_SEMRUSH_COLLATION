import csv

# Load prices from all_prices_combined.csv
price_map = {}
with open('all_prices_combined.csv', newline='', encoding='utf-8') as pricefile:
    reader = csv.DictReader(pricefile)
    for row in reader:
        name = row['Name'].strip()
        price = row['Price'].strip()
        if price:
            price_map[name] = price

# Update collated_price_analysis.csv with prices from all_prices_combined.csv
input_path = 'output_domain_price_analysis/collated_price_analysis.csv'
rows = []
with open(input_path, newline='', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames
    for row in reader:
        name = row['Name'].strip()
        if name in price_map:
            row['Price'] = price_map[name]
        rows.append(row)

with open(input_path, 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

with open('domains_with_prices.csv', 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=['Name', 'Price'])
    writer.writeheader()
    for row in reader:
        price = row.get('Price', '').strip()
        if price:
            try:
                price_int = str(int(float(price)))
            except ValueError:
                price_int = price  # fallback to original if conversion fails
            writer.writerow({'Name': row['Name'], 'Price': price_int}) 