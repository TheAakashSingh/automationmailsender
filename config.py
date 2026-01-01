"""
Configuration file for Google Maps Lead Scraper
"""
import os
from typing import List, Dict

# MongoDB Configuration
MONGODB_ENABLED = os.getenv("MONGODB_ENABLED", "False").lower() == "true"
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "leads_scraper")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "business_leads")

# CSV Configuration
CSV_FOLDER = "exports"
CSV_FILENAME = "business_leads.csv"
EXCEL_FILENAME = "business_leads.xlsx"

# Scraping Configuration (Optimized for speed)
DELAY_MIN = 2  # Reduced from 5 - Minimum delay between actions (seconds)
DELAY_MAX = 5  # Reduced from 15 - Maximum delay between actions (seconds)
SCROLL_PAUSE = 1  # Reduced from 2 - Pause after each scroll (seconds)
MAX_SCROLL_ATTEMPTS = 50  # Maximum scroll attempts per search
WAIT_TIMEOUT = 20  # Reduced from 30 - Wait timeout (seconds)

# Contact Extraction Speed Settings
ENRICH_ENABLED = True  # Set to False to skip contact enrichment (much faster)
ENRICH_TIMEOUT = 8  # Timeout for website requests (seconds) - reduced from 15
ENRICH_MAX_PAGES = 3  # Maximum pages to check per website (homepage + contact pages)

# Proxy Configuration
USE_PROXIES = False  # Set to True if using proxies
PROXY_LIST = []  # Add proxy list here if needed: ["ip:port", "ip:port"]

# Browser Configuration
HEADLESS = True  # Set to True for faster headless mode
WINDOW_SIZE = (1920, 1080)

# User Agents (will be randomly selected)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

# Top cities per country (will be used if cities not specified)
TOP_CITIES_BY_COUNTRY = {
    "United States": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"],
    "United Kingdom": ["London", "Manchester", "Birmingham", "Glasgow", "Liverpool", "Leeds", "Sheffield", "Edinburgh", "Bristol", "Cardiff"],
    "Canada": ["Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa", "Edmonton", "Winnipeg", "Quebec City", "Hamilton", "Kitchener"],
    "Australia": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Gold Coast", "Newcastle", "Canberra", "Sunshine Coast", "Wollongong"],
    "Germany": ["Berlin", "Munich", "Hamburg", "Frankfurt", "Cologne", "Stuttgart", "Düsseldorf", "Dortmund", "Essen", "Leipzig"],
    "France": ["Paris", "Marseille", "Lyon", "Toulouse", "Nice", "Nantes", "Strasbourg", "Montpellier", "Bordeaux", "Lille"],
    "India": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Surat"],
    "China": ["Shanghai", "Beijing", "Guangzhou", "Shenzhen", "Chengdu", "Hangzhou", "Wuhan", "Xi'an", "Nanjing", "Tianjin"],
    "United Arab Emirates": ["Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Ras Al Khaimah", "Fujairah", "Al Ain"],
    "Singapore": ["Singapore"],
    "Japan": ["Tokyo", "Osaka", "Yokohama", "Nagoya", "Sapporo", "Fukuoka", "Kobe", "Kyoto"],
    "South Korea": ["Seoul", "Busan", "Incheon", "Daegu", "Daejeon", "Gwangju"],
    "Brazil": ["São Paulo", "Rio de Janeiro", "Brasília", "Salvador", "Fortaleza", "Belo Horizonte", "Manaus", "Curitiba"],
    "Mexico": ["Mexico City", "Guadalajara", "Monterrey", "Puebla", "Tijuana", "León", "Juárez"],
    "Spain": ["Madrid", "Barcelona", "Valencia", "Seville", "Bilbao", "Málaga"],
    "Italy": ["Rome", "Milan", "Naples", "Turin", "Palermo", "Genoa", "Bologna"],
}

# Email extraction patterns (for reference, actual extraction uses regex in utils.py)
EMAIL_PATTERNS = [
    r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
]

# Excluded email domains (personal emails)
EXCLUDED_EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com",
    "icloud.com", "protonmail.com", "mail.com", "yandex.com", "zoho.com"
]

# Resume file (stores current progress)
RESUME_FILE = "scraper_state.json"

# Logging
LOG_FILE = "scraper.log"
LOG_LEVEL = "INFO"
