# Google Maps Lead Scraper

A powerful automation tool that extracts business leads from Google Maps using robust HTTP requests (no browser required!). This tool can extract 10,000+ worldwide business leads with contact information including emails, phone numbers, and addresses. Fast, lightweight, and reliable.

## Features

- ✅ **Google Maps Scraping**: Extracts business data directly from Google Maps using robust HTTP requests
- ✅ **Email Extraction**: Automatically extracts business emails from company websites
- ✅ **Large Scale**: Designed to scrape 10,000+ leads with automatic continuation
- ✅ **Fast & Reliable**: Uses Playwright (modern headless browser - faster and more reliable than Selenium!)
- ✅ **Resume Capability**: Automatically saves progress and can resume from last position
- ✅ **Multiple Storage**: Supports MongoDB and CSV storage
- ✅ **Export Options**: Export to CSV and Excel formats
- ✅ **Worldwide Coverage**: Supports multiple countries and cities
- ✅ **Robust Parsing**: Multiple extraction strategies for maximum data capture

## Tech Stack

- Python 3.8+
- Playwright (modern headless browser - faster than Selenium!)
- BeautifulSoup (HTML parsing)
- MongoDB (optional)
- Pandas & OpenPyXL (for Excel export)

## Installation

### 1. Clone or Download this Repository

```bash
git clone <repository-url>
cd automation_leads
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Playwright Browser

After installing Python dependencies, install the Playwright browser:

```bash
playwright install chromium
```

Or if the command doesn't work:

```bash
python -m playwright install chromium
```

This downloads the Chromium browser that Playwright uses (one-time setup).

### 4. Verify Installation

Run the setup verification script to check if everything is installed correctly:

```bash
python setup_check.py
```

This will verify that all required packages are installed.

### 5. (Optional) Setup MongoDB

If you want to use MongoDB for storage:

1. Install MongoDB: https://www.mongodb.com/try/download/community
2. Start MongoDB service
3. Update `config.py`:
   ```python
   MONGODB_ENABLED = True
   MONGODB_URI = "mongodb://localhost:27017/"
   ```

If MongoDB is not enabled, the tool will use CSV storage only (which works perfectly fine).

## Usage

### Method 1: Command Line

Run directly from command line:

```bash
# Basic usage
python main.py

# With custom parameters
python main.py --keywords "software company" "web development" --countries "United States" "United Kingdom" --target 10000
```

#### Command Line Arguments

```bash
python main.py \
  --keywords "keyword1" "keyword2" "keyword3" \
  --countries "Country1" "Country2" \
  --cities '{"Country1": ["City1", "City2"], "Country2": ["City3"]}' \
  --target 10000
```

**Arguments:**
- `--keywords`: Space-separated list of keywords to search
- `--countries`: Space-separated list of countries
- `--cities`: (Optional) JSON string with cities per country
- `--target`: (Optional) Target number of leads (default: 10000)

### Method 2: Python Script

You can also import and use the scraper programmatically:

```python
from main import run_scraper

keywords = ["software company", "web development", "IT services"]
countries = ["United States", "United Kingdom"]
target_leads = 10000

run_scraper(keywords, countries, None, target_leads)
```

## Configuration

Edit `config.py` to customize:

- **Delays**: Adjust `DELAY_MIN` and `DELAY_MAX` for timing between actions
- **Browser**: Set `HEADLESS = True` for headless mode (not recommended for anti-bot evasion)
- **MongoDB**: Configure MongoDB connection settings
- **Proxies**: Add proxy list and set `USE_PROXIES = True`
- **Cities**: Customize `TOP_CITIES_BY_COUNTRY` dictionary

## How It Works

1. **Search**: Opens Google Maps and searches for businesses using targeted keywords: `{keyword} in {city}, {country}`
   - Focuses on industries that need tech support: Insurance, Logistics, Shipping, Healthcare, Financial Services, etc.

2. **Scroll**: Automatically scrolls through the results panel to load all business listings

3. **Extract & Classify**: For each business:
   - Extracts: name, category, phone, website, address, city, country, rating, Google Maps URL
   - **Classifies industry** (Insurance, Logistics, Healthcare, etc.)
   - **Identifies if company needs tech support** based on industry
   - If website exists, visits the website and extracts:
     - All business emails (info@, sales@, contact@, etc.)
     - Phone numbers
     - WhatsApp numbers
     - **Executive contacts** (CEO, CTO, Founder emails)

4. **Store**: Saves leads to MongoDB and/or CSV file with industry classification

5. **Continue**: Automatically continues through all keywords → countries → cities until target is reached

6. **Resume**: Saves progress and can resume from last position if interrupted

## Output

### CSV File

Leads are saved to `exports/business_leads.csv` with the following columns:

- `name`: Business name
- `email`: Primary business email (best contact email)
- `all_emails`: All emails found (comma-separated)
- `phone`: Phone number
- `whatsapp`: WhatsApp number (if available)
- `executives`: CEO/CTO/Founder contacts with emails (pipe-separated)
- `website`: Website URL
- `category`: Business category/keyword used
- `industry`: Primary industry classification (Insurance, Logistics & Shipping, Healthcare, etc.)
- `all_industries`: All matching industries (comma-separated)
- `needs_tech_support`: Boolean - True if company typically needs tech/software support
- `address`: Full address
- `city`: City
- `country`: Country
- `rating`: Google rating
- `maps_url`: Google Maps URL
- `domain`: Normalized domain (for duplicate detection)
- `scraped_at`: Timestamp
- `source`: Source (always "google_maps")

### Excel Export

Use the dashboard export button or run:
```python
from database import export_to_excel
export_to_excel()
```

### MongoDB

If MongoDB is enabled, leads are stored in:
- Database: `leads_scraper`
- Collection: `business_leads`

## Important Notes

### Legal & Ethical Use

- This tool is for **internal business use only**
- Respect Google's Terms of Service
- Use reasonable delays and don't overload servers
- Respect robots.txt and website policies
- Only extract publicly available information

### Rate Limiting & Best Practices

- Random delays between requests (5-15 seconds)
- Rotating user agents for each request
- Lightweight HTTP requests (no browser overhead)
- Respectful scraping with reasonable delays

### Rate Limiting

- Default delays: 5-15 seconds between businesses
- 10-15 seconds delay between cities
- If you encounter captchas frequently, increase delays in `config.py`

### Resume Functionality

If scraping is interrupted (Ctrl+C), the tool saves progress to `scraper_state.json`. When you run again, it will automatically resume from the last position.

To start fresh, delete `scraper_state.json`.

## Troubleshooting

### Playwright Installation Issues

If you encounter Playwright errors:
- Make sure Playwright browser is installed: `playwright install chromium`
- Or: `python -m playwright install chromium`
- If installation fails, check your internet connection

### Browser Issues

If the browser doesn't start:
- Make sure Chromium is installed: `playwright install chromium`
- Check system permissions
- Try running with administrator privileges if needed

### Captcha Detection

If you see captchas frequently:
- Increase delays in `config.py` (DELAY_MIN, DELAY_MAX)
- Use proxies (configure in `config.py`)
- Reduce the number of requests per session
- Solve captcha manually and continue (the tool will pause)

### Missing Data

Some businesses may not have complete information. The tool handles missing fields gracefully:
- Empty fields are stored as empty strings
- Duplicates are automatically skipped (based on website domain)

### MongoDB Connection Issues

If MongoDB connection fails:
- The tool automatically falls back to CSV-only storage
- Check MongoDB is running: `mongosh` or `mongo`
- Verify connection string in `config.py`

## Example Output

```
2024-01-15 10:30:15 - INFO - Browser started successfully
2024-01-15 10:30:20 - INFO - Searching: software company in New York, United States
2024-01-15 10:30:25 - INFO - Search results loaded
2024-01-15 10:30:30 - INFO - Total businesses found: 125
2024-01-15 10:30:35 - INFO - Processing business 1/125
2024-01-15 10:30:42 - INFO - Extracted: ABC Software Solutions
2024-01-15 10:30:45 - INFO - Found 2 emails from https://abcsoftware.com
2024-01-15 10:30:50 - INFO - Lead saved to CSV: ABC Software Solutions
...
```

## Project Structure

```
automation_leads/
├── main.py                 # Main entry point and orchestration
├── scraper.py              # Google Maps scraper core
├── email_extractor.py      # Website email extraction
├── database.py             # MongoDB and CSV storage
├── utils.py                # Utility functions
├── config.py               # Configuration file
├── run_scraper.py          # Simple launcher script
├── setup_check.py          # Setup verification script
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── sample_output.csv       # Sample output format
├── .gitignore              # Git ignore file
├── exports/                # Output folder (created automatically)
│   ├── business_leads.csv
│   └── business_leads.xlsx
└── scraper_state.json      # Resume state (created automatically)
```

## License

This tool is for internal business use. Use responsibly and in accordance with applicable laws and terms of service.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review the logs in `scraper.log`
3. Check `scraper_state.json` for current progress

## Changelog

### Version 1.0
- Initial release
- Google Maps scraping
- Email extraction
- MongoDB and CSV storage
- GUI dashboard
- Resume capability
- Export to CSV/Excel

#   a u t o m a t i o n m a i l s e n d e r  
 