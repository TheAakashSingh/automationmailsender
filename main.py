"""
Main entry point for Google Maps Lead Scraper
"""
import sys
import logging
import signal
from typing import List, Dict

from config import TOP_CITIES_BY_COUNTRY, RESUME_FILE
from scraper import GoogleMapsScraper
from database import init_mongodb, save_lead, get_total_leads, close_mongodb, export_to_excel
from utils import save_resume_state, load_resume_state, random_delay

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Global scraper instance
scraper = None
stop_flag = False


def signal_handler(sig, frame):
    """
    Handle Ctrl+C gracefully.
    """
    global stop_flag
    logger.info("\nStopping scraper...")
    stop_flag = True
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def get_cities_for_country(country: str, custom_cities: List[str] = None) -> List[str]:
    """
    Get list of cities for a country.
    """
    if custom_cities:
        return custom_cities
    
    return TOP_CITIES_BY_COUNTRY.get(country, [])


def run_scraper(
    keywords: List[str],
    countries: List[str],
    cities_per_country: Dict[str, List[str]] = None,
    target_leads: int = 10000
):
    """
    Main scraping function.
    """
    global scraper, stop_flag
    
    # Initialize database
    init_mongodb()
    
    # Load resume state if exists
    resume_state = load_resume_state()
    
    # Initialize scraper
    scraper = GoogleMapsScraper()
    scraper.start_browser()
    
    try:
        total_scraped = get_total_leads()
        logger.info(f"Starting with {total_scraped} existing leads. Target: {target_leads}")
        
        # Resume from saved state
        keyword_idx = 0
        country_idx = 0
        city_idx = 0
        
        if resume_state:
            keyword = resume_state.get("current_keyword")
            country = resume_state.get("current_country")
            city = resume_state.get("current_city")
            
            # Find indices - only resume if keyword and country match current run
            if keyword in keywords:
                keyword_idx = keywords.index(keyword)
            else:
                # Reset if keyword doesn't match - start fresh
                logger.info(f"Resume state keyword '{keyword}' not in current keywords, starting fresh")
                resume_state = None
                keyword_idx = 0
                country_idx = 0
                city_idx = 0
            
            if resume_state and country in countries:
                country_idx = countries.index(country)
            elif resume_state:
                logger.info(f"Resume state country '{country}' not in current countries, starting fresh")
                resume_state = None
                keyword_idx = 0
                country_idx = 0
                city_idx = 0
            
            if resume_state:
                logger.info(f"Resuming from: {keyword} -> {country} -> {city}")
        
        # Main loop
        for kw_idx in range(keyword_idx, len(keywords)):
            if stop_flag:
                break
            
            keyword = keywords[kw_idx]
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing keyword: {keyword}")
            logger.info(f"{'='*60}\n")
            
            for country_idx_iter in range(country_idx if kw_idx == keyword_idx else 0, len(countries)):
                if stop_flag:
                    break
                
                country = countries[country_idx_iter]
                cities = get_cities_for_country(country, cities_per_country.get(country) if cities_per_country else None)
                
                if not cities:
                    logger.warning(f"No cities found for {country}, skipping...")
                    continue
                
                logger.info(f"\nProcessing country: {country}")
                logger.info(f"Cities to process: {len(cities)}")
                
                start_city_idx = city_idx if (kw_idx == keyword_idx and country_idx_iter == country_idx) else 0
                
                for city_idx_iter in range(start_city_idx, len(cities)):
                    if stop_flag:
                        break
                    
                    # Check if target reached
                    total_scraped = get_total_leads()
                    if total_scraped >= target_leads:
                        logger.info(f"\n{'='*60}")
                        logger.info(f"Target reached! Total leads: {total_scraped}")
                        logger.info(f"{'='*60}\n")
                        return
                    
                    city = cities[city_idx_iter]
                    logger.info(f"\n{'-'*60}")
                    logger.info(f"Processing: {keyword} -> {country} -> {city}")
                    logger.info(f"Total leads so far: {total_scraped}")
                    logger.info(f"{'-'*60}\n")
                    
                    # Save resume state
                    save_resume_state({
                        "current_keyword": keyword,
                        "current_country": country,
                        "current_city": city,
                        "total_leads": total_scraped
                    })
                    
                    try:
                        # Scrape businesses
                        leads = scraper.search_businesses(keyword, city, country)
                        
                        # Enrich and save leads
                        saved_count = 0
                        for idx, lead in enumerate(leads, 1):
                            logger.info(f"Enriching lead {idx}/{len(leads)}: {lead.get('name', 'Unknown')}")
                            
                            # Enrich with comprehensive contact info
                            try:
                                lead = scraper.enrich_business_data(lead)
                            except Exception as e:
                                logger.debug(f"Error enriching lead: {e}")
                            
                            if save_lead(lead):
                                saved_count += 1
                            
                            # Small delay between enrichments (reduced for speed)
                            random_delay(1, 2)
                        
                        logger.info(f"Saved {saved_count} new leads from {city}")
                        
                        # Small delay between cities (reduced for speed)
                        random_delay(3, 5)
                        
                    except Exception as e:
                        logger.error(f"Error scraping {city}: {e}")
                        continue
                
                # Reset city index for next country
                city_idx = 0
            
            # Reset country index for next keyword
            country_idx = 0
        
        # Final summary
        total_scraped = get_total_leads()
        logger.info(f"\n{'='*60}")
        logger.info(f"Scraping completed! Total leads: {total_scraped}")
        logger.info(f"{'='*60}\n")
        
        # Export to Excel
        excel_path = export_to_excel()
        if excel_path:
            logger.info(f"Excel export: {excel_path}")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        if scraper:
            scraper.close_browser()
        close_mongodb()


def main():
    """
    Command-line interface.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Google Maps Lead Scraper')
    parser.add_argument('--keywords', nargs='+', required=True, help='Keywords to search (e.g., "software company" "web development")')
    parser.add_argument('--countries', nargs='+', required=True, help='Countries to search (e.g., "United States" "United Kingdom")')
    parser.add_argument('--cities', type=str, help='JSON string with cities per country: {"United States": ["New York", "Los Angeles"]}')
    parser.add_argument('--target', type=int, default=10000, help='Target number of leads (default: 10000)')
    
    args = parser.parse_args()
    
    # Parse cities if provided
    cities_per_country = None
    if args.cities:
        import json
        try:
            cities_per_country = json.loads(args.cities)
        except Exception as e:
            logger.error(f"Invalid cities JSON: {e}")
            return
    
    # Run scraper
    run_scraper(
        keywords=args.keywords,
        countries=args.countries,
        cities_per_country=cities_per_country,
        target_leads=args.target
    )


if __name__ == "__main__":
    # Example usage if run without arguments (can be customized)
    if len(sys.argv) == 1:
        # Default example
        keywords = ["software company", "web development", "IT services"]
        countries = ["United States", "United Kingdom"]
        target_leads = 10000
        
        print("\n" + "="*60)
        print("Google Maps Lead Scraper")
        print("="*60)
        print(f"\nKeywords: {keywords}")
        print(f"Countries: {countries}")
        print(f"Target leads: {target_leads}")
        print("\nStarting scraper...\n")
        
        run_scraper(keywords, countries, None, target_leads)
    else:
        main()

