"""
Advanced Contact Extractor - Finds emails, phones, WhatsApp, and executive contacts
"""
import requests
import re
import logging
from typing import List, Dict, Set
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from config import EXCLUDED_EMAIL_DOMAINS
from utils import random_delay
from data_cleaner import clean_emails

logger = logging.getLogger(__name__)

# Session for requests
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})


def extract_all_contacts(url: str, timeout: int = 8, max_pages: int = 3) -> Dict[str, List[str]]:
    """
    Extract all contact information from a website.
    Returns dict with: emails, phones, whatsapp, executives
    """
    if not url:
        return {'emails': [], 'phones': [], 'whatsapp': [], 'executives': []}
    
    # Normalize URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    contacts = {
        'emails': set(),
        'phones': set(),
        'whatsapp': set(),
        'executives': []
    }
    
    # Pages to check (reduced for speed - focus on most important pages)
    pages_to_check = [
        url,  # Homepage (always check)
        urljoin(url, '/contact'),  # Contact page (most important for emails)
        urljoin(url, '/contact-us'),  # Alternative contact page
        # Only check team/leadership if homepage doesn't have enough info
        # urljoin(url, '/about'),
        # urljoin(url, '/team'),
    ]
    
    # Limit number of pages to check
    pages_to_check = pages_to_check[:max_pages]
    
    for page_url in pages_to_check:
        try:
            page_contacts = _extract_contacts_from_page(page_url, timeout)
            
            # Merge contacts
            contacts['emails'].update(page_contacts['emails'])
            contacts['phones'].update(page_contacts['phones'])
            contacts['whatsapp'].update(page_contacts['whatsapp'])
            contacts['executives'].extend(page_contacts['executives'])
            
            random_delay(0.5, 1)  # Reduced delay for speed
            
        except Exception as e:
            logger.debug(f"Error extracting from {page_url}: {e}")
            continue
    
    # Convert sets to lists and filter
    return {
        'emails': _filter_emails(list(contacts['emails'])),
        'phones': list(contacts['phones']),
        'whatsapp': list(contacts['whatsapp']),
        'executives': _deduplicate_executives(contacts['executives'])
    }


def _extract_contacts_from_page(url: str, timeout: int = 15) -> Dict[str, Set]:
    """Extract contacts from a single page."""
    contacts = {
        'emails': set(),
        'phones': set(),
        'whatsapp': set(),
        'executives': []
    }
    
    try:
        response = session.get(url, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        
        # Only process HTML
        content_type = response.headers.get('Content-Type', '').lower()
        if 'text/html' not in content_type:
            return contacts
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style tags
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract emails using data_cleaner (parses HTML properly, not raw text)
        # This prevents emails merged with phone numbers or UI text
        emails = clean_emails(response.text)  # Use raw HTML response
        contacts['emails'].update(emails)
        
        # Extract phones
        phones = _extract_phone_numbers(text)
        contacts['phones'].update(phones)
        
        # Extract WhatsApp numbers
        whatsapp = _extract_whatsapp_numbers(text, soup)
        contacts['whatsapp'].update(whatsapp)
        
        # Extract executive contacts (CEO, CTO, Founder, etc.)
        executives = _extract_executive_contacts(soup, text)
        contacts['executives'].extend(executives)
        
        # Also check mailto links
        mailto_links = soup.find_all('a', href=re.compile(r'^mailto:', re.I))
        for link in mailto_links:
            href = link.get('href', '')
            email_match = re.search(r'mailto:([^\?]+)', href, re.I)
            if email_match:
                email = email_match.group(1).strip().lower()
                domain = email.split('@')[1] if '@' in email else ''
                if domain and domain not in EXCLUDED_EMAIL_DOMAINS:
                    contacts['emails'].add(email)
        
        # Check data attributes and meta tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            content = meta.get('content', '')
            if content:
                # Use clean_emails for consistency (creates minimal HTML wrapper)
                meta_html = f"<p>{content}</p>"
                emails = clean_emails(meta_html)
                contacts['emails'].update(emails)
        
    except requests.exceptions.RequestException as e:
        logger.debug(f"Request error for {url}: {e}")
    except Exception as e:
        logger.debug(f"Error parsing {url}: {e}")
    
    return contacts


def _extract_phone_numbers(text: str) -> Set[str]:
    """Extract phone numbers from text."""
    phones = set()
    
    patterns = [
        r'\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
        r'\+?\d{10,15}',
        r'\(\d{3}\)\s?\d{3}[-.\s]?\d{4}',
        r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            phone = match.strip()
            digits = re.sub(r'[^\d]', '', phone)
            # Valid phone: 10-15 digits
            if 10 <= len(digits) <= 15:
                phones.add(phone)
    
    return phones


def _extract_whatsapp_numbers(text: str, soup: BeautifulSoup) -> Set[str]:
    """Extract WhatsApp numbers from text and links."""
    whatsapp_numbers = set()
    
    # Look for WhatsApp links
    whatsapp_links = soup.find_all('a', href=re.compile(r'wa\.me|whatsapp\.com|api\.whatsapp\.com', re.I))
    for link in whatsapp_links:
        href = link.get('href', '')
        # Extract number from WhatsApp URL
        number_match = re.search(r'(\d{10,15})', href)
        if number_match:
            whatsapp_numbers.add(number_match.group(1))
    
    # Look for WhatsApp text patterns
    whatsapp_patterns = [
        r'whatsapp[:\s]*(\+?\d{10,15})',
        r'wa[:\s]*(\+?\d{10,15})',
    ]
    
    text_lower = text.lower()
    for pattern in whatsapp_patterns:
        matches = re.findall(pattern, text_lower, re.I)
        for match in matches:
            whatsapp_numbers.add(match)
    
    return whatsapp_numbers


def _extract_executive_contacts(soup: BeautifulSoup, text: str) -> List[Dict]:
    """Extract executive contacts (CEO, CTO, Founder, etc.)."""
    executives = []
    
    # Executive titles to look for
    executive_titles = [
        r'CEO|Chief Executive Officer',
        r'CTO|Chief Technology Officer',
        r'CFO|Chief Financial Officer',
        r'Founder|Co-Founder|CoFounder',
        r'President',
        r'Managing Director|MD',
        r'Owner',
        r'Director',
    ]
    
    # Look for name + title patterns in text
    for title_pattern in executive_titles:
        # Pattern: Name (Title) or Title: Name
        patterns = [
            rf'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s*[\(\-]?\s*{title_pattern}',
            rf'{title_pattern}[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.I)
            for match in matches:
                name = match.strip()
                if len(name.split()) >= 2:  # At least first and last name
                    executives.append({
                        'name': name,
                        'title': title_pattern.replace('|', '/'),
                        'email': '',
                        'phone': ''
                    })
    
    # Look for executive sections in HTML
    executive_sections = soup.find_all(['div', 'section'], class_=re.compile(r'team|executive|leader|founder|ceo|cto', re.I))
    
    for section in executive_sections:
        try:
            # Try to find name
            name_elem = section.find(['h1', 'h2', 'h3', 'h4', 'strong', 'span'], class_=re.compile(r'name', re.I))
            if not name_elem:
                name_elem = section.find(['h1', 'h2', 'h3', 'h4'])
            
            name = name_elem.get_text().strip() if name_elem else ''
            
            # Try to find title
            title_elem = section.find(['p', 'span', 'div'], class_=re.compile(r'title|role|position', re.I))
            title = title_elem.get_text().strip() if title_elem else ''
            
            # Check if title matches executive pattern
            if name and any(re.search(t.replace('|', '/'), title, re.I) for t in executive_titles):
                # Try to find email in this section
                email = ''
                email_elem = section.find('a', href=re.compile(r'mailto:', re.I))
                if email_elem:
                    email_match = re.search(r'mailto:([^\?]+)', email_elem.get('href', ''), re.I)
                    if email_match:
                        email = email_match.group(1).strip().lower()
                
                executives.append({
                    'name': name,
                    'title': title,
                    'email': email,
                    'phone': ''
                })
        except Exception:
            continue
    
    return executives


def _filter_emails(emails: List[str]) -> List[str]:
    """Filter out excluded email domains."""
    filtered = []
    for email in emails:
        domain = email.split('@')[1].lower() if '@' in email else ''
        if domain and domain not in EXCLUDED_EMAIL_DOMAINS:
            filtered.append(email.lower())
    return list(set(filtered))  # Remove duplicates


def _deduplicate_executives(executives: List[Dict]) -> List[Dict]:
    """Remove duplicate executives."""
    seen = set()
    unique = []
    for exec_info in executives:
        key = exec_info.get('name', '').lower()
        if key and key not in seen:
            seen.add(key)
            unique.append(exec_info)
    return unique


def extract_executive_emails(website: str) -> List[Dict]:
    """
    Specifically extract executive email addresses.
    Returns list of dicts with name, title, email.
    """
    contacts = extract_all_contacts(website)
    
    # Try to find emails for executives
    executives_with_emails = []
    
    for exec_info in contacts['executives']:
        name = exec_info.get('name', '')
        if not name:
            continue
        
        # Try common email patterns for executives
        # e.g., firstname@company.com, firstname.lastname@company.com, etc.
        # This would require domain extraction and name parsing
        # For now, return executives found, emails will be in contacts['emails']
        
        executives_with_emails.append(exec_info)
    
    return executives_with_emails


def get_best_contact_email(contacts: Dict) -> str:
    """Get the best/business email from contacts."""
    emails = contacts.get('emails', [])
    
    if not emails:
        return ''
    
    # Prefer business emails
    preferred = ['info@', 'contact@', 'hello@', 'sales@', 'support@']
    
    for pref in preferred:
        for email in emails:
            if email.lower().startswith(pref):
                return email
    
    # Return first email
    return emails[0] if emails else ''


def get_best_phone(contacts: Dict) -> str:
    """Get the best phone number from contacts."""
    phones = contacts.get('phones', [])
    whatsapp = contacts.get('whatsapp', [])
    
    # Prefer WhatsApp if available
    if whatsapp:
        return whatsapp[0]
    
    # Return first phone
    return phones[0] if phones else ''

