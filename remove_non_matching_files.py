import os

# Define the target directory
target_dir = "30_05-6_05_SEMRUSH_backlinks"

# Function to check if file matches the backlinks pattern
# Only matches files that follow the pattern '[domain]-backlinks'
def is_backlink_file(filename):
    return filename.endswith("-backlinks")

# Process files
removed_files = []
for filename in os.listdir(target_dir):
    file_path = os.path.join(target_dir, filename)
    
    # Check if it's a file and does not match our criteria
    if os.path.isfile(file_path) and not is_backlink_file(filename):
        # Remove the file
        os.remove(file_path)
        removed_files.append(filename)

# Print summary
print(f"Successfully removed {len(removed_files)} files from {target_dir}:")
for file in removed_files:
    print(f"- {file}") 