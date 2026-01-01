#!/usr/bin/env python3
"""
Simple launcher script for the Google Maps Lead Scraper
Focused on finding companies that need technical/software support
"""
from main import run_scraper

if __name__ == "__main__":
    print("\n" + "="*70)
    print(" " * 10 + "Google Maps Lead Scraper - Tech Support Leads")
    print("="*70)
    print("\nFinding companies that need technical/software support:")
    print("  - Insurance companies")
    print("  - Logistics & Shipping companies")
    print("  - Supply chain companies")
    print("  - Manufacturing companies")
    print("  - Healthcare providers")
    print("  - Financial services")
    print("  - Real estate companies")
    print("\nDefault settings:")
    print("  Countries: United States, United Kingdom, Canada, Australia")
    print("  Target: 1,000 leads")
    print("\nTo customize, edit this file")
    print("\n" + "-"*70 + "\n")
    
    # Configuration - Keywords focused on companies needing tech support
    keywords = [
        # Insurance & Financial Services
        "insurance company",
        "insurance agency",
        "insurance broker",
        "insurance services",
        "financial services company",
        "accounting firm",
        "financial advisor",
        
        # Logistics & Shipping
        "logistics company",
        "shipping company",
        "freight company",
        "cargo company",
        "warehouse",
        "supply chain company",
        "3PL company",  # Third-party logistics
        "transportation company",
        "courier service",
        
        # Manufacturing & Distribution
        "manufacturing company",
        "distribution company",
        "wholesale company",
        "import export company",
        
        # Healthcare
        "healthcare provider",
        "hospital",
        "clinic",
        "medical practice",
        "pharmacy",
        
        # Real Estate
        "real estate company",
        "property management",
        "real estate agency",
        
        # Retail & E-commerce
        "retail store chain",
        "ecommerce company",
        "online retailer",
        
        # Professional Services
        "law firm",
        "consulting company",
        "marketing agency",
        "advertising agency",
    ]
    
    # Target countries (expandable)
    countries = [
        "United States",
        "United Kingdom",
        "Canada",
        "Australia",
        "Germany",
        "France",
        "United Arab Emirates",
        "Singapore",
    ]
    
    # Optional: Specify cities per country
    # If None, will use top cities from config.py
    cities_per_country = None
    
    target_leads = 1000
    
    # Start scraping
    try:
        run_scraper(
            keywords=keywords,
            countries=countries,
            cities_per_country=cities_per_country,
            target_leads=target_leads
        )
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
