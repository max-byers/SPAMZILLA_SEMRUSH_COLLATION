import pandas as pd
import ipaddress

def analyze_ip_octets(input_file, output_file):
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Extract IP addresses
    ip_addresses = df['IP Address'].dropna()
    
    # Split IP addresses into octets
    octets = ip_addresses.apply(lambda x: x.split('.'))
    
    # Convert octets to integers
    octet_df = pd.DataFrame(octets.tolist(), columns=['Octet1', 'Octet2', 'Octet3', 'Octet4'])
    octet_df = octet_df.astype(int)
    
    # Find unique values for each octet
    unique_octets = {
        'Unique 1 Number': len(set(octet_df['Octet1'])),
        'Unique 2 Number': len(set(octet_df['Octet2'])),
        'Unique 3 Number': len(set(octet_df['Octet3'])),
        'Unique 4 Number': len(set(octet_df['Octet4']))
    }
    
    # Create a DataFrame with the unique octet counts
    result_df = pd.DataFrame([unique_octets])
    
    # Save to CSV
    result_df.to_csv(output_file, index=False)
    
    # Print the results
    print("Unique Octet Analysis:")
    for key, value in unique_octets.items():
        print(f"{key}: {value}")
    
    return result_df

# Specify the input and output file paths
input_file = 'greatwaterfilters.com.au-backlinks_refips.csv'
output_file = 'ip_octet_unique_counts.csv'

# Run the analysis
result = analyze_ip_octets(input_file, output_file) 