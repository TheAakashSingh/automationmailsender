# Speed Optimization Guide

The scraper has been optimized for faster lead extraction. Here are the settings:

## Current Speed Settings

- **Delays**: 2-5 seconds (reduced from 5-15 seconds)
- **Enrichment Timeout**: 8 seconds per page (reduced from 15 seconds)
- **Max Pages Checked**: 3 pages per website (homepage + contact pages)
- **Headless Mode**: Enabled (faster browser operation)

## Speed vs Quality Trade-off

The scraper now prioritizes speed while still extracting:
- ✅ Business names, addresses, phones (from Google Maps)
- ✅ Websites (from Google Maps)
- ✅ Emails from homepage and contact pages
- ⚠️ Reduced: Only checks 3 pages instead of 11 pages per website
- ⚠️ Reduced: May miss some emails from team/leadership pages

## Further Speed Improvements

### Option 1: Disable Enrichment (Fastest - ~10x faster)
In `config.py`, set:
```python
ENRICH_ENABLED = False
```
This will:
- Extract business data from Google Maps only
- Skip website visits and email extraction
- Still get: names, addresses, phones, websites, industry classification

### Option 2: Reduce Cities per Country
Edit `run_scraper.py` to limit cities:
```python
cities_per_country = {
    "United States": ["New York", "Los Angeles", "Chicago"],  # Only 3 cities
}
```

### Option 3: Target Specific Industries Only
Edit `run_scraper.py` to use fewer keywords:
```python
keywords = [
    "insurance company",
    "logistics company",
    "shipping company",
]
```

## Expected Speed

With current optimizations:
- **With enrichment**: ~15-30 seconds per lead = ~40-80 hours for 10,000 leads
- **Without enrichment**: ~5-10 seconds per lead = ~14-28 hours for 10,000 leads

To reach 10,000 leads faster, consider:
1. Running multiple instances (different countries/keywords)
2. Using proxies for parallel scraping
3. Disabling enrichment and adding emails later in batch
4. Starting with fewer cities and expanding gradually

