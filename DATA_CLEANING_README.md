# Data Cleaning Module - Implementation Guide

## Overview

The `data_cleaner.py` module fixes data quality issues in scraped leads without changing the scraping flow.

## Key Features

### 1. Email Cleaning (`clean_emails`)
- **Never runs regex on raw page text** - parses HTML first with BeautifulSoup
- Extracts text only from semantic elements: `<a>`, `<p>`, `<span>`, `<li>`, `<td>`, `<div>`
- Applies strict email regex: `\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b`
- Removes emails merged with digits or words (e.g., "213-221-1247hello@domain.com")
- Filters out personal email domains (gmail, yahoo, etc.)
- Returns unique, lowercase emails only

### 2. Phone Cleaning (`clean_phone`)
- Keeps only digits, `+`, spaces, hyphens, parentheses
- Removes emails accidentally attached to phone numbers
- Validates minimum length (8 digits)
- Normalizes format (US numbers get formatted as (555) 123-4567)

### 3. Executive Extraction (`extract_executives`)
- **STRICT validation**: Only accepts if ALL present:
  - Person name (First Last format)
  - Role: CEO | CTO | Founder | Director
  - Email address
- Does NOT guess executives
- Does NOT infer from titles alone
- Output format: "John Smith (CTO): john@company.com"

### 4. Domain Normalization (`normalize_domain`)
- Uses `urlparse` to extract netloc
- Removes "www." prefix
- Converts to lowercase
- Returns empty string if invalid URL

### 5. Lead Sanitization (`sanitize_lead`)
- Applies all cleaning functions
- Validates data quality
- Ensures all fields are properly formatted
- Industry must come from keyword, not website content

## Integration

### Automatic Cleaning
The cleaning is automatically applied in `database.py`:
- `save_lead()` calls `sanitize_lead()` before saving
- Invalid leads (no domain AND no email) are skipped

### Cleaning Existing CSV Files

Use the standalone script to clean existing CSV files:

```bash
python clean_existing_csv.py input.csv output_clean.csv
```

Example:
```bash
python clean_existing_csv.py exports/business_leads.csv exports/business_leads_clean.csv
```

## Data Quality Rules

### Emails
- Must be valid format: `user@domain.tld`
- Domain must not be personal email provider
- Must not contain excluded words (read, failure, error, etc.)
- Must not be merged with phone numbers or other text

### Executives
- Must have: Name + Title + Email
- Name must be "First Last" format (at least 2 words)
- Title must match executive roles (CEO, CTO, Founder, etc.)
- Email must be valid and present

### Industry/Category
- Must come from search keyword only
- Must NOT be inferred from website content
- Length limited to prevent long sentences

### Domain
- Normalized to lowercase
- "www." removed
- Port numbers removed
- Invalid URLs return empty string

## Testing

Test the module:

```python
from data_cleaner import clean_emails, clean_phone, normalize_domain, sanitize_lead

# Test email extraction
html = '<p>Contact us at info@company.com</p>'
emails = clean_emails(html)
print(emails)  # ['info@company.com']

# Test phone cleaning
phone = clean_phone("555-1234hello")
print(phone)  # (555) 123-4

# Test domain normalization
domain = normalize_domain("https://www.Example.com/path")
print(domain)  # example.com
```

## Files Modified

1. **data_cleaner.py** (NEW) - Main cleaning module
2. **clean_existing_csv.py** (NEW) - Standalone CSV cleaning script
3. **database.py** - Integrated `sanitize_lead()` into `save_lead()`
4. **contact_extractor.py** - Uses `clean_emails()` instead of raw text regex

## Notes

- The cleaning is applied **before** saving to database/CSV
- No changes to scraping flow - only data quality improvements
- Existing CSV files can be cleaned using the standalone script
- All cleaning functions are idempotent (safe to run multiple times)

