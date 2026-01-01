# How to Use Data Cleaning

## Automatic Cleaning (New Leads)

**Good news!** Data cleaning is **automatically applied** to all new leads when scraping.

When you run the scraper:
```bash
python run_scraper.py
```

All leads are automatically cleaned before being saved. You don't need to do anything extra!

## Manual Cleaning (Existing CSV Files)

If you have an existing CSV file with bad data, you can clean it using the standalone script.

### Step 1: Run the cleaning script

```bash
python clean_existing_csv.py input_file.csv output_file_clean.csv
```

### Step 2: Examples

**Example 1: Clean the current CSV file**
```bash
python clean_existing_csv.py exports/business_leads.csv exports/business_leads_clean.csv
```

**Example 2: Clean a backup file**
```bash
python clean_existing_csv.py "exports/business_leads copy.csv" "exports/business_leads copy - CLEANED.csv"
```

**Example 3: Clean and overwrite (be careful!)**
```bash
python clean_existing_csv.py exports/business_leads.csv exports/business_leads_temp.csv
# Review the cleaned file, then rename if satisfied
```

### What Gets Cleaned

✅ **Emails:**
- Removes emails merged with phone numbers (e.g., "213-221-1247hello@domain.com")
- Removes emails with UI text (e.g., "info@company.comread")
- Filters personal email domains (gmail, yahoo, etc.)
- Returns only valid business emails

✅ **Phones:**
- Removes text attached to phone numbers
- Normalizes format
- Validates length

✅ **Executives:**
- Only keeps executives with: Name + Title + Email (all required)
- Removes junk like "Risk Fa (CTO/Chief Technology Officer)"
- Formats as "John Smith (CTO): john@company.com"

✅ **Domains:**
- Normalizes to lowercase
- Removes "www."
- Consistent format

✅ **Industry/Category:**
- Uses keyword only (not website content)
- Limits length to prevent long sentences

### Output

The script will show:
- Total rows processed
- Cleaned rows saved
- Skipped rows (invalid leads)

Example output:
```
2026-01-01 18:00:00 - INFO - Reading from: exports/business_leads.csv
2026-01-01 18:00:00 - INFO - Writing to: exports/business_leads_clean.csv
2026-01-01 18:00:15 - INFO - ============================================================
2026-01-01 18:00:15 - INFO - Cleaning complete!
2026-01-01 18:00:15 - INFO - Total rows processed: 64
2026-01-01 18:00:15 - INFO - Cleaned rows saved: 58
2026-01-01 18:00:15 - INFO - Skipped rows: 6
2026-01-01 18:00:15 - INFO - ============================================================
```

## Quick Start

**For new scraping:**
```bash
# Just run normally - cleaning is automatic!
python run_scraper.py
```

**For cleaning existing CSV:**
```bash
# Clean your existing file
python clean_existing_csv.py "exports/business_leads copy.csv" "exports/business_leads copy - CLEANED.csv"
```

## Notes

- The cleaning script **never modifies** your original file
- Always creates a new output file
- Review the cleaned file before using it
- Invalid leads (no domain AND no email) are skipped
- All cleaning is idempotent (safe to run multiple times)

