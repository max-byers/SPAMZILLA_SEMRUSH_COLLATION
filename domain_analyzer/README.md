# Domain Analyzer Configuration

## Manual File Selection

Open `config.py` and set the following variables:

### Spamzilla File
```python
# In config.py
SPAMZILLA_FILE = "export-133821_2025-05-11-06-40-03_cleaned.csv"
```
- The file must be located in the `SPAMZILLA_DOMAIN_EXPORTS` directory
- Copy the FULL filename exactly as it appears in the directory

### SEMRUSH Comparison Folder
```python
# In config.py
SEMRUSH_COMPARISON_FOLDER = "25_06_SEMRUSH_comparison"
```
- This will be located in the root directory
- Copy the FULL folder name exactly as it appears

## Fallback Behavior

- If no file/folder is specified, the script will automatically select the most recent file
- If the specified file/folder doesn't exist, the script will fall back to automatic selection

## Example Usage

```python
from domain_analyzer.analyzer import main

# Simply run the main function
main()
```

## Notes

- Always ensure the filename and folder name are exactly as they appear in the directory
- The configuration uses simple string variables for easy manual input 