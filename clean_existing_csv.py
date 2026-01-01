"""
Standalone script to clean existing CSV files.

Usage:
    python clean_existing_csv.py input.csv output_clean.csv
    python clean_existing_csv.py business_leads.csv business_leads_clean.csv
"""

import sys
import csv
import logging
from pathlib import Path
from data_cleaner import sanitize_lead, is_valid_lead

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def clean_csv(input_path: str, output_path: str):
    """
    Clean an existing CSV file using data_cleaner module.
    
    Args:
        input_path: Path to input CSV file
        output_path: Path to output cleaned CSV file
    """
    input_file = Path(input_path)
    
    if not input_file.exists():
        logger.error(f"Input file not found: {input_path}")
        return
    
    logger.info(f"Reading from: {input_path}")
    logger.info(f"Writing to: {output_path}")
    
    cleaned_count = 0
    skipped_count = 0
    total_count = 0
    
    try:
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            
            if not fieldnames:
                logger.error("CSV file has no headers")
                return
            
            # Write cleaned data
            with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                
                for row in reader:
                    total_count += 1
                    
                    # Convert row to dict and sanitize
                    sanitized = sanitize_lead(row)
                    
                    # Validate lead
                    if is_valid_lead(sanitized):
                        # Write only fields that exist in original CSV
                        output_row = {}
                        for field in fieldnames:
                            output_row[field] = sanitized.get(field, row.get(field, ''))
                        
                        writer.writerow(output_row)
                        cleaned_count += 1
                    else:
                        skipped_count += 1
                        logger.debug(f"Skipped invalid lead: {row.get('name', 'Unknown')}")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Cleaning complete!")
        logger.info(f"Total rows processed: {total_count}")
        logger.info(f"Cleaned rows saved: {cleaned_count}")
        logger.info(f"Skipped rows: {skipped_count}")
        logger.info(f"{'='*60}")
        
    except Exception as e:
        logger.error(f"Error cleaning CSV: {e}")
        import traceback
        logger.error(traceback.format_exc())


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: python clean_existing_csv.py <input.csv> <output_clean.csv>")
        print("\nExample:")
        print("  python clean_existing_csv.py exports/business_leads.csv exports/business_leads_clean.csv")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    clean_csv(input_path, output_path)


if __name__ == "__main__":
    main()

