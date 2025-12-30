# Setup Requirements for SPAMZILLA_SEMRUSH_COLLATION Project

This document outlines all APIs, external services, and resources that need to be set up for someone else to run this codebase successfully.

---

## 🔑 API Keys & External Services

### 1. **Google Custom Search API** (REQUIRED)
**Used in:**
- `spam_checker/main.py` (lines 33-34, 36-49)
- `INDEX_CHECKER/main.py` (lines 12-13, 21-28)

**What it does:**
- Checks if domains are indexed in Google search results
- Used for domain indexing verification

**Setup Required:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the "Custom Search API"
4. Create credentials (API Key)
5. Create a Custom Search Engine at [Google Programmable Search](https://programmablesearchengine.google.com/)
6. Get your Custom Search Engine ID (CSE ID)

**Current Configuration:**
- API Key: Currently hardcoded in files (should be moved to environment variables)
- CSE ID: Currently hardcoded in files (should be moved to environment variables)

**Files to Update:**
- `spam_checker/main.py` - Replace API_KEY and CSE_ID on lines 33-34
- `INDEX_CHECKER/main.py` - Replace API_KEY and CSE_ID on lines 12-13

**Rate Limits:**
- Free tier: 100 queries per day
- Paid tier: $5 per 1,000 queries
- Code includes rate limiting (1 second delay between requests)

---

### 2. **OpenAI API** (OPTIONAL - Only if using `testing_suitability.py`)
**Used in:**
- `testing_suitability.py` (lines 16, 20, 114-123)

**What it does:**
- Uses GPT-4o to analyze domain names for suitability
- Checks for non-literate words, full names, locations, trademarks, etc.

**Setup Required:**
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Add credits to your account (pay-as-you-go)

**Current Configuration:**
- API Key: Currently hardcoded in `testing_suitability.py` line 16 (should be moved to environment variables)

**Files to Update:**
- `testing_suitability.py` - Replace API_KEY on line 16

**Cost Information:**
- GPT-4o pricing: ~$0.0025 per 1K input tokens, ~$0.01 per 1K output tokens
- Script processes domains in batches of 25 to control costs
- Includes caching to avoid re-analyzing domains

---

## 📦 Python Package Dependencies

### Core Dependencies (from `requirements.txt`)
```bash
pandas>=1.5.0
nltk>=3.8.1
```

### Additional Dependencies (not in requirements.txt but used in codebase)
These should be added to `requirements.txt`:

```bash
requests          # For HTTP requests (Google API, web scraping)
openai            # For OpenAI GPT-4 API (if using testing_suitability.py)
beautifulsoup4    # For HTML parsing (CONTENT/scrape_urls)
lxml              # HTML parser backend for BeautifulSoup
openpyxl          # For Excel file operations (IDENTIFY_SUSPICIOUS_BACKLINKS)
numpy             # Used in various analysis scripts
```

### Recommended Complete `requirements.txt`:
```txt
pandas>=1.5.0
nltk>=3.8.1
requests>=2.28.0
openai>=1.0.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
openpyxl>=3.1.0
numpy>=1.24.0
```

---

## 📚 NLTK Data Downloads

**Required NLTK Data:**
The codebase uses NLTK but doesn't explicitly download data. You may need to download NLTK data if any scripts use it:

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
```

**Note:** Check if any scripts actually use NLTK functionality. If not, this dependency may be optional.

---

## 🔧 Configuration Files

### Files with Hardcoded Paths (Need to be Updated)
Several configuration files contain hardcoded paths that reference the original user's system:

1. **`domain_price_analysis/config.py`**
   - Line 5: `BASE_DIR = r"C:/Users/Max Byers/OneDrive/Documents/SPAMZILLA_SEMRUSH_COLLATION"`
   - Update to match new user's directory structure

2. **`SEMRUSH_200_domains/scripts/config.py`**
   - Line 7: `DEFAULT_EXPORTS_DIR = r"C:\Users\Max Byers\OneDrive\Documents\SPAMZILLA_SEMRUSH_COLLATION\SPAMZILLA_DOMAIN_EXPORTS"`
   - Update to match new user's directory structure

3. **Various `config.py` files** in subdirectories may have relative paths that need adjustment

---

## 📁 Directory Structure Requirements

The codebase expects certain directories to exist:

- `SPAM_EXPORTS/` - Contains Spamzilla export CSV files
- `SPAMZILLA_DOMAIN_EXPORTS/` - Contains domain export files
- `INDEX_CHECKER/` - Contains index checking scripts
- `CONTENT/` - Contains web scraping scripts
- `BACKLINK_CSV_FILES/` - Contains backlink data
- `SUMMARY/` - Contains summary files
- Various `*_SEMRUSH_comparison/` directories - SEMRUSH data folders
- Various `*_SEMRUSH_backlinks/` directories - SEMRUSH backlink data
- Various `*_SEMRUSH_outbounds/` directories - SEMRUSH outbound data

---

## 🔐 Security Recommendations

### ⚠️ **CRITICAL: Remove Hardcoded API Keys**

**Before sharing the project, you should:**

1. **Create a `.env` file** (add to `.gitignore`):
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   GOOGLE_CSE_ID=your_cse_id_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

2. **Install python-dotenv**:
   ```bash
   pip install python-dotenv
   ```

3. **Update code to use environment variables:**
   - Replace hardcoded API keys with `os.getenv('GOOGLE_API_KEY')`
   - Replace hardcoded CSE IDs with `os.getenv('GOOGLE_CSE_ID')`
   - Replace hardcoded OpenAI keys with `os.getenv('OPENAI_API_KEY')`

4. **Create a `.env.example` file:**
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   GOOGLE_CSE_ID=your_cse_id_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

---

## 📋 Setup Checklist for New User

- [ ] Install Python 3.8+ 
- [ ] Install all Python packages from `requirements.txt`
- [ ] Download NLTK data (if needed)
- [ ] Set up Google Cloud Console account
- [ ] Enable Google Custom Search API
- [ ] Create Google Custom Search Engine and get CSE ID
- [ ] Get Google API Key
- [ ] (Optional) Set up OpenAI account and get API key (if using `testing_suitability.py`)
- [ ] Update all hardcoded paths in `config.py` files
- [ ] Create `.env` file with API keys (recommended)
- [ ] Update code to use environment variables instead of hardcoded keys
- [ ] Ensure all required directories exist or create them
- [ ] Test with sample data files

---

## 💰 Cost Estimates

### Google Custom Search API
- **Free Tier:** 100 queries/day
- **Paid:** $5 per 1,000 queries after free tier
- **Estimated Monthly Cost:** Depends on usage (likely $0-$50 for moderate use)

### OpenAI API (if used)
- **GPT-4o:** ~$0.0025 per 1K input tokens, ~$0.01 per 1K output tokens
- **Estimated Cost:** ~$0.10-$0.50 per 25 domains analyzed
- **Script includes caching** to minimize costs

---

## 📝 Additional Notes

1. **Rate Limiting:** The code includes rate limiting for Google API (1 second delay), but be aware of daily limits
2. **Caching:** `testing_suitability.py` includes caching to avoid re-analyzing domains
3. **File Paths:** Many scripts use relative paths that assume a specific directory structure
4. **Data Files:** The project expects various CSV and Excel files in specific directories - ensure these are available or adjust paths accordingly

---

## 🆘 Troubleshooting

**Common Issues:**
- **API Key Errors:** Ensure API keys are correctly set in environment variables or config files
- **Rate Limit Errors:** Google API has daily limits - wait 24 hours or upgrade to paid tier
- **Import Errors:** Ensure all Python packages are installed: `pip install -r requirements.txt`
- **File Not Found Errors:** Check that all required directories and data files exist
- **Path Errors:** Update all hardcoded paths in config files to match new system

---

**Last Updated:** Based on codebase analysis as of project sharing date

