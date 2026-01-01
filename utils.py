"""
Utility functions for the scraper
"""
import random
import time
import json
import os
import logging
from typing import Optional, List
from fake_useragent import UserAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Initialize UserAgent
try:
    ua = UserAgent()
except Exception:
    ua = None


def random_delay(min_seconds: float = None, max_seconds: float = None) -> None:
    """
    Wait for a random amount of time between min_seconds and max_seconds.
    Uses config defaults if not specified.
    """
    from config import DELAY_MIN, DELAY_MAX
    
    min_sec = min_seconds if min_seconds is not None else DELAY_MIN
    max_sec = max_seconds if max_seconds is not None else DELAY_MAX
    
    delay = random.uniform(min_sec, max_sec)
    logger.debug(f"Waiting {delay:.2f} seconds...")
    time.sleep(delay)


def get_random_user_agent() -> str:
    """
    Get a random user agent string.
    """
    from config import USER_AGENTS
    
    if ua:
        try:
            return ua.random
        except Exception:
            pass
    
    return random.choice(USER_AGENTS)


def get_proxy() -> Optional[str]:
    """
    Get a random proxy from the list if proxies are enabled.
    """
    from config import USE_PROXIES, PROXY_LIST
    
    if not USE_PROXIES or not PROXY_LIST:
        return None
    
    return random.choice(PROXY_LIST)


def save_resume_state(state: dict, filename: str = None) -> None:
    """
    Save scraper state to resume later.
    """
    from config import RESUME_FILE
    
    filepath = filename or RESUME_FILE
    
    try:
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        logger.info(f"Resume state saved to {filepath}")
    except Exception as e:
        logger.error(f"Failed to save resume state: {e}")


def load_resume_state(filename: str = None) -> Optional[dict]:
    """
    Load scraper state to resume scraping.
    """
    from config import RESUME_FILE
    
    filepath = filename or RESUME_FILE
    
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, 'r') as f:
            state = json.load(f)
        logger.info(f"Resume state loaded from {filepath}")
        return state
    except Exception as e:
        logger.error(f"Failed to load resume state: {e}")
        return None


def normalize_domain(url: str) -> str:
    """
    Extract and normalize domain from URL for duplicate detection.
    """
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        domain = domain.replace('www.', '').lower().strip('/')
        return domain
    except Exception:
        return url.lower().strip()


def clean_text(text: str) -> str:
    """
    Clean and normalize text extracted from web pages.
    """
    if not text:
        return ""
    
    text = text.strip()
    text = ' '.join(text.split())  # Normalize whitespace
    return text


def extract_emails_from_text(text: str, excluded_domains: List[str] = None) -> List[str]:
    """
    Extract email addresses from text using regex.
    Filters out excluded domains (personal email providers).
    """
    import re
    from config import EXCLUDED_EMAIL_DOMAINS
    
    excluded = excluded_domains or EXCLUDED_EMAIL_DOMAINS
    emails = set()
    
    # Generic email pattern
    generic_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
    matches = re.findall(generic_pattern, text, re.IGNORECASE)
    
    for email in matches:
        email_lower = email.lower()
        if '@' not in email_lower:
            continue
        
        domain = email_lower.split('@')[1]
        
        # Filter out excluded domains (personal email providers)
        if domain and domain not in excluded:
            emails.add(email_lower)
    
    return list(emails)

