"""
Advanced Google Maps Lead Scraper using Playwright
Dynamic extraction like Apollo - robust and adaptive
"""
import logging
import time
import json
import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from urllib.parse import quote, urlparse

from config import DELAY_MIN, DELAY_MAX
from utils import random_delay, clean_text, normalize_domain
from contact_extractor import extract_all_contacts, get_best_contact_email, get_best_phone
from industry_classifier import enhance_business_with_industry

logger = logging.getLogger(__name__)

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not installed. Install with: pip install playwright && playwright install")


class GoogleMapsScraper:
    """
    Advanced Google Maps scraper using Playwright.
    Dynamic extraction with multiple strategies - works like Apollo.
    """
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self._ensure_playwright()
    
    def _ensure_playwright(self):
        """Ensure Playwright is installed and available."""
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright is required. Install with:\n"
                "  pip install playwright\n"
                "  playwright install chromium"
            )
    
    def start_browser(self):
        """Start Playwright browser."""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
            context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            self.page = context.new_page()
            logger.info("Browser started successfully")
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise
    
    def close_browser(self):
        """Close browser and cleanup."""
        try:
            if self.page:
                self.page.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
    
    def search_businesses(self, keyword: str, city: str, country: str) -> List[Dict]:
        """
        Search for businesses on Google Maps and extract data.
        Uses multiple dynamic extraction strategies.
        """
        leads = []
        
        if not self.page:
            self.start_browser()
        
        try:
            query = f"{keyword} in {city}, {country}"
            logger.info(f"Searching: {query}")
            
            search_url = f"https://www.google.com/maps/search/{quote(query)}"
            
            # Navigate to page
            logger.debug(f"Navigating to: {search_url}")
            self.page.goto(search_url, wait_until='domcontentloaded', timeout=60000)
            
            # Wait for results to load
            logger.debug("Waiting for results to load...")
            try:
                # Wait for results panel or any content
                self.page.wait_for_selector('[role="feed"], [role="main"], div[jsaction]', timeout=15000)
            except PlaywrightTimeout:
                logger.warning("Results panel not found, continuing anyway...")
            
            random_delay(1, 2)  # Reduced delay for speed
            
            # Try multiple extraction strategies
            businesses = []
            
            # Strategy 1: Extract from rendered HTML
            businesses.extend(self._extract_from_html())
            
            # Strategy 2: Extract using JavaScript evaluation
            if not businesses:
                businesses.extend(self._extract_via_javascript())
            
            # Strategy 3: Click through listings if still no results
            if not businesses:
                businesses.extend(self._extract_by_clicking_listings())
            
            logger.info(f"Found {len(businesses)} businesses using dynamic extraction")
            
            # Add location metadata and classify industry
            for business in businesses:
                business['city'] = city
                business['country'] = country
                business['category'] = keyword  # Store keyword as category
                business['keyword'] = keyword
                business['source'] = 'google_maps'
                
                # Classify industry (companies that need tech support)
                business = enhance_business_with_industry(business)
            
            leads.extend(businesses)
            
        except PlaywrightTimeout:
            logger.error("Timeout loading page")
        except Exception as e:
            logger.error(f"Error searching businesses: {e}")
            import traceback
            logger.debug(traceback.format_exc())
        
        return leads
    
    def _extract_from_html(self) -> List[Dict]:
        """Extract businesses from rendered HTML - Strategy 1."""
        businesses = []
        
        try:
            # Get page HTML
            html = self.page.content()
            soup = BeautifulSoup(html, 'lxml')
            
            # Find all place links - most reliable method
            place_links = soup.find_all('a', href=re.compile(r'/maps/place/[^/]+'))
            
            seen_urls = set()
            
            for link in place_links:
                try:
                    href = link.get('href', '')
                    if not href:
                        continue
                    
                    # Make full URL
                    if href.startswith('/'):
                        full_url = f"https://www.google.com{href}"
                    else:
                        full_url = href
                    
                    # Skip duplicates
                    if full_url in seen_urls:
                        continue
                    seen_urls.add(full_url)
                    
                    # Extract business name - try multiple methods
                    name = ''
                    # Method 1: Link text
                    name = clean_text(link.get_text())
                    # Method 2: aria-label
                    if not name or len(name) < 3:
                        name = clean_text(link.get('aria-label', ''))
                    # Method 3: title
                    if not name or len(name) < 3:
                        name = clean_text(link.get('title', ''))
                    # Method 4: data-value or data-name
                    if not name or len(name) < 3:
                        name = clean_text(link.get('data-value', '') or link.get('data-name', ''))
                    
                    if not name or len(name) < 3:
                        continue
                    
                    # Get parent/sibling elements for additional info
                    container = link.find_parent(['div', 'article', 'section', 'li'])
                    container_text = container.get_text() if container else ''
                    
                    business = {
                        'name': name,
                        'address': self._extract_address(container_text),
                        'phone': self._extract_phone(container_text),
                        'website': '',
                        'category': '',
                        'rating': self._extract_rating(container_text),
                        'email': '',
                        'maps_url': full_url,
                    }
                    
                    businesses.append(business)
                    
                except Exception as e:
                    logger.debug(f"Error processing link: {e}")
                    continue
            
            logger.debug(f"Extracted {len(businesses)} businesses from HTML")
            
        except Exception as e:
            logger.error(f"Error extracting from HTML: {e}")
        
        return businesses
    
    def _extract_via_javascript(self) -> List[Dict]:
        """Extract businesses using JavaScript - Strategy 2."""
        businesses = []
        
        try:
            # Use JavaScript to find business listings
            js_code = """
            () => {
                const businesses = [];
                const links = document.querySelectorAll('a[href*="/maps/place/"]');
                links.forEach(link => {
                    const href = link.href || link.getAttribute('href');
                    if (!href || !href.includes('/maps/place/')) return;
                    
                    const name = link.textContent?.trim() || 
                                link.getAttribute('aria-label') || 
                                link.getAttribute('title') || '';
                    
                    if (name && name.length > 2) {
                        businesses.push({
                            name: name,
                            url: href.startsWith('http') ? href : 'https://www.google.com' + href
                        });
                    }
                });
                return businesses;
            }
            """
            
            results = self.page.evaluate(js_code)
            
            for item in results:
                try:
                    business = {
                        'name': clean_text(item.get('name', '')),
                        'address': '',
                        'phone': '',
                        'website': '',
                        'category': '',
                        'rating': '',
                        'email': '',
                        'maps_url': item.get('url', ''),
                    }
                    
                    if business['name']:
                        businesses.append(business)
                except Exception:
                    continue
            
            logger.debug(f"Extracted {len(businesses)} businesses via JavaScript")
            
        except Exception as e:
            logger.debug(f"Error extracting via JavaScript: {e}")
        
        return businesses
    
    def _extract_by_clicking_listings(self) -> List[Dict]:
        """Extract by clicking on listings and reading details - Strategy 3."""
        businesses = []
        
        try:
            # Find clickable listing elements
            listing_selectors = [
                '[role="feed"] > div > div > a[href*="/maps/place/"]',
                '[role="feed"] a[href*="/maps/place/"]',
                'a[href*="/maps/place/"]',
            ]
            
            links = []
            for selector in listing_selectors:
                try:
                    found = self.page.locator(selector).all()
                    if found:
                        links = found[:20]  # Limit to first 20
                        break
                except Exception:
                    continue
            
            logger.debug(f"Found {len(links)} clickable listings")
            
            for i, link in enumerate(links[:10]):  # Process first 10
                try:
                    # Get href
                    href = link.get_attribute('href')
                    if not href:
                        continue
                    
                    if href.startswith('/'):
                        full_url = f"https://www.google.com{href}"
                    else:
                        full_url = href
                    
                    # Get name before clicking
                    try:
                        name = link.inner_text() or link.get_attribute('aria-label') or ''
                    except:
                        name = ''
                    name = clean_text(name)
                    
                    if not name or len(name) < 3:
                        continue
                    
                    business = {
                        'name': name,
                        'address': '',
                        'phone': '',
                        'website': '',
                        'category': '',
                        'rating': '',
                        'email': '',
                        'maps_url': full_url,
                    }
                    
                    businesses.append(business)
                    
                except Exception as e:
                    logger.debug(f"Error processing listing {i}: {e}")
                    continue
            
            logger.debug(f"Extracted {len(businesses)} businesses by clicking")
            
        except Exception as e:
            logger.debug(f"Error extracting by clicking: {e}")
        
        return businesses
    
    def _extract_address(self, text: str) -> str:
        """Extract address from text using patterns."""
        if not text:
            return ''
        
        patterns = [
            r'\d+\s+[A-Za-z0-9\s,]+(?:St|Street|Ave|Avenue|Blvd|Boulevard|Rd|Road|Dr|Drive|Ln|Lane|Way|Pl|Place)[A-Za-z\s,]*',
            r'\d+\s+[A-Za-z\s]+(?:,\s*[A-Z]{2})?\s+\d{5}(?:-\d{4})?',
            r'[A-Za-z\s]+(?:St|Street|Ave|Avenue|Blvd|Boulevard),\s*[A-Za-z\s]+',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                addr = clean_text(match.group(0))
                if len(addr) > 10:  # Reasonable address length
                    return addr
        
        return ''
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number from text."""
        if not text:
            return ''
        
        patterns = [
            r'\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
            r'\+?\d{10,15}',
            r'\(\d{3}\)\s?\d{3}[-.\s]?\d{4}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                phone = clean_text(match.group(0))
                digits = re.sub(r'[^\d]', '', phone)
                if len(digits) >= 10:  # Valid phone has at least 10 digits
                    return phone
        
        return ''
    
    def _extract_rating(self, text: str) -> str:
        """Extract rating from text."""
        if not text:
            return ''
        
        patterns = [
            r'(\d+\.?\d*)\s*(?:star|★|⭐|rating)',
            r'rating[:\s]*(\d+\.?\d*)',
            r'(\d\.\d)\s*\([0-9,]+',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                rating = match.group(1)
                try:
                    # Validate rating (typically 1-5)
                    rating_float = float(rating)
                    if 1.0 <= rating_float <= 5.0:
                        return str(rating)
                except ValueError:
                    pass
        
        return ''
    
    def enrich_business_data(self, business: Dict) -> Dict:
        """
        Enrich business by visiting detail page and extracting:
        - Website
        - Email addresses
        - Phone numbers
        - WhatsApp numbers
        - Executive contacts (CEO, CTO, Founder)
        """
        if not business.get('maps_url') or not self.page:
            return business
        
        try:
            # Visit Google Maps detail page
            logger.debug(f"Enriching business: {business.get('name', 'Unknown')}")
            self.page.goto(business['maps_url'], wait_until='domcontentloaded', timeout=20000)
            random_delay(1, 2)  # Reduced delay
            
            html = self.page.content()
            soup = BeautifulSoup(html, 'lxml')
            
            # Extract website from Maps page
            if not business.get('website'):
                links = soup.find_all('a', href=re.compile(r'^https?://'))
                for link in links:
                    href = link.get('href', '')
                    if href and 'google.com' not in href and 'maps' not in href.lower() and 'place' not in href.lower():
                        business['website'] = clean_text(href)
                        break
            
            # Extract phone from Maps page if not already found
            if not business.get('phone'):
                phone_elements = soup.find_all(['a', 'span', 'div'], string=re.compile(r'\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'))
                for elem in phone_elements:
                    phone_text = elem.get_text()
                    phone_match = re.search(r'\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}', phone_text)
                    if phone_match:
                        phone = phone_match.group(0).strip()
                        digits = re.sub(r'[^\d]', '', phone)
                        if len(digits) >= 10:
                            business['phone'] = phone
                            break
            
            # Extract comprehensive contact info from website
            if business.get('website'):
                try:
                    logger.debug(f"Extracting contacts from website: {business['website']}")
                    # Use faster settings: shorter timeout, fewer pages
                    from config import ENRICH_TIMEOUT, ENRICH_MAX_PAGES
                    contacts = extract_all_contacts(business['website'], timeout=ENRICH_TIMEOUT, max_pages=ENRICH_MAX_PAGES)
                    
                    # Set best email
                    if not business.get('email'):
                        business['email'] = get_best_contact_email(contacts)
                    
                    # Set best phone
                    if not business.get('phone'):
                        business['phone'] = get_best_phone(contacts)
                    
                    # Store WhatsApp if found
                    whatsapp_numbers = contacts.get('whatsapp', [])
                    if whatsapp_numbers:
                        business['whatsapp'] = whatsapp_numbers[0]
                    
                    # Store all emails found
                    all_emails = contacts.get('emails', [])
                    if all_emails:
                        business['all_emails'] = ', '.join(all_emails[:5])  # Limit to 5
                    
                    # Store executive contacts (use data_cleaner for strict validation)
                    # Note: extract_executives needs raw HTML, so we'll use it from the page
                    # For now, store executives from contacts but they'll be cleaned in sanitize_lead
                    executives = contacts.get('executives', [])
                    if executives:
                        # Format executives properly
                        exec_info = []
                        for exec_data in executives[:3]:  # Limit to 3 executives
                            if isinstance(exec_data, dict):
                                exec_str = exec_data.get('name', '')
                                if exec_data.get('title'):
                                    exec_str += f" ({exec_data['title']})"
                                if exec_data.get('email'):
                                    exec_str += f": {exec_data['email']}"
                                if exec_str:
                                    exec_info.append(exec_str)
                        business['executives'] = ' | '.join(exec_info) if exec_info else ''
                    
                    logger.debug(f"Found {len(all_emails)} emails, {len(whatsapp_numbers)} WhatsApp, {len(executives)} executives")
                    
                except Exception as e:
                    logger.debug(f"Error extracting contacts from website: {e}")
            
        except Exception as e:
            logger.debug(f"Error enriching business: {e}")
        
        return business
