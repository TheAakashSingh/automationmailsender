"""
Email extraction module for business websites
"""
import requests
import re
import logging
from typing import List, Set
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from config import EXCLUDED_EMAIL_DOMAINS
from utils import random_delay, extract_emails_from_text

logger = logging.getLogger(__name__)

# Session for requests (with headers)
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})


def extract_emails_from_url(url: str, timeout: int = 10) -> List[str]:
    """
    Extract business emails from a website URL.
    Visits homepage, /contact, /about, /support pages.
    """
    if not url:
        return []
    
    # Normalize URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    emails = set()
    
    # Pages to check
    pages_to_check = [
        url,  # Homepage
        urljoin(url, '/contact'),
        urljoin(url, '/about'),
        urljoin(url, '/support'),
        urljoin(url, '/contact-us'),
        urljoin(url, '/get-in-touch'),
    ]
    
    for page_url in pages_to_check:
        try:
            page_emails = _extract_emails_from_page(page_url, timeout)
            emails.update(page_emails)
            
            # Small delay between page requests
            random_delay(2, 4)
            
        except Exception as e:
            logger.debug(f"Error extracting from {page_url}: {e}")
            continue
    
    # Filter out personal email domains
    filtered_emails = []
    for email in emails:
        domain = email.split('@')[1].lower() if '@' in email else ''
        if domain and domain not in EXCLUDED_EMAIL_DOMAINS:
            filtered_emails.append(email)
    
    logger.info(f"Found {len(filtered_emails)} emails from {url}")
    return filtered_emails


def _extract_emails_from_page(url: str, timeout: int = 10) -> Set[str]:
    """
    Extract emails from a single page.
    """
    emails = set()
    
    try:
        response = session.get(url, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        
        # Only process HTML content
        content_type = response.headers.get('Content-Type', '').lower()
        if 'text/html' not in content_type:
            return emails
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style tags
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Extract emails using regex
        extracted = extract_emails_from_text(text)
        emails.update(extracted)
        
        # Also check mailto links
        mailto_links = soup.find_all('a', href=re.compile(r'^mailto:', re.I))
        for link in mailto_links:
            href = link.get('href', '')
            email_match = re.search(r'mailto:([^\?]+)', href, re.I)
            if email_match:
                email = email_match.group(1).strip()
                if email and '@' in email:
                    domain = email.split('@')[1].lower()
                    if domain not in EXCLUDED_EMAIL_DOMAINS:
                        emails.add(email.lower())
        
        # Check for email in data attributes and meta tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            content = meta.get('content', '')
            if content:
                extracted = extract_emails_from_text(content)
                emails.update(extracted)
        
    except requests.exceptions.RequestException as e:
        logger.debug(f"Request error for {url}: {e}")
    except Exception as e:
        logger.debug(f"Error parsing {url}: {e}")
    
    return emails


def extract_first_email(emails: List[str]) -> str:
    """
    Get the first business email from the list.
    Prefers common business email prefixes.
    """
    if not emails:
        return ""
    
    # Prefer common business email prefixes
    preferred_prefixes = ['info@', 'sales@', 'contact@', 'support@', 'hello@', 'help@']
    
    for prefix in preferred_prefixes:
        for email in emails:
            if email.lower().startswith(prefix):
                return email
    
    # Return first email if no preferred found
    return emails[0]

