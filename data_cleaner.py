"""
Data Cleaning Module for Google Maps Lead Scraper

Purpose: Clean and sanitize scraped data to ensure high quality before saving.
This module addresses common data quality issues:
- Emails merged with phone numbers or text
- Junk executive data
- Industry classification from wrong sources
- Domain normalization issues
"""

import re
import logging
from typing import List, Dict, Set, Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Excluded email domains (personal emails)
EXCLUDED_EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com",
    "icloud.com", "protonmail.com", "mail.com", "yandex.com", "zoho.com",
    "gmx.com", "ymail.com", "live.com", "msn.com"
]

# Words to exclude from emails (common UI text, errors, placeholders)
EXCLUDED_EMAIL_WORDS = [
    'read', 'failure', 'error', 'example', 'test', 'sample', 'placeholder',
    'click', 'here', 'view', 'show', 'more', 'less', 'close', 'open',
    'submit', 'send', 'contact', 'us', 'email', 'mail', 'phone', 'call'
]

# Executive titles (case-insensitive matching)
EXECUTIVE_TITLES = [
    'CEO', 'Chief Executive Officer',
    'CTO', 'Chief Technology Officer',
    'CFO', 'Chief Financial Officer',
    'COO', 'Chief Operating Officer',
    'Founder', 'Co-Founder', 'CoFounder',
    'President',
    'Managing Director', 'MD',
    'Director',
    'Owner'
]


def clean_emails(raw_html: str) -> List[str]:
    """
    Extract clean emails from HTML content.
    
    CRITICAL: Never run regex on full page text - parse HTML first!
    This prevents emails merged with phone numbers or UI text.
    
    Strategy:
    1. Parse HTML with BeautifulSoup
    2. Extract text ONLY from semantic elements (<a>, <p>, <span>, <li>)
    3. Apply strict email regex on cleaned text
    4. Filter out invalid patterns (emails merged with words/numbers)
    5. Remove personal email domains
    
    Args:
        raw_html: Raw HTML content from webpage
        
    Returns:
        List of unique, lowercase, valid business emails
    """
    if not raw_html:
        return []
    
    emails = set()
    
    try:
        # Parse HTML - this separates structure from text
        soup = BeautifulSoup(raw_html, 'html.parser')
        
        # Remove script, style, and noscript tags (they contain no real emails)
        for tag in soup(['script', 'style', 'noscript', 'meta']):
            tag.decompose()
        
        # Extract text from semantic elements only
        # These are most likely to contain actual contact emails
        semantic_elements = soup.find_all(['a', 'p', 'span', 'li', 'td', 'div'])
        
        for element in semantic_elements:
            # Get text content and any href attributes (mailto links)
            text = element.get_text(separator=' ', strip=True)
            href = element.get('href', '')
            
            # Extract from mailto links (most reliable)
            if href.startswith('mailto:'):
                mailto_match = re.search(r'mailto:([^\?&]+)', href, re.I)
                if mailto_match:
                    email = mailto_match.group(1).strip()
                    if _is_valid_email(email):
                        emails.add(email.lower())
            
            # Extract from text content using strict regex
            # Only check text blocks that are reasonable length (not entire page)
            if text and 5 <= len(text) <= 200:
                # Strict email regex - must match standard email format
                email_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
                matches = re.findall(email_pattern, text)
                
                for email in matches:
                    # Additional validation: ensure email is not merged with words/numbers
                    if _is_valid_email(email):
                        emails.add(email.lower())
    
    except Exception as e:
        logger.debug(f"Error parsing HTML for emails: {e}")
    
    # Final filtering: remove personal emails and invalid patterns
    cleaned_emails = []
    for email in emails:
        domain = email.split('@')[1] if '@' in email else ''
        
        # Skip personal email domains
        if domain.lower() in EXCLUDED_EMAIL_DOMAINS:
            continue
        
        # Skip if email contains excluded words (common in UI text)
        email_lower = email.lower()
        if any(word in email_lower for word in EXCLUDED_EMAIL_WORDS):
            continue
        
        # Validate: email should not be merged with numbers (like "213-221-1247hello@domain.com")
        # Check if email starts immediately after digits or ends with letters
        if re.search(r'^\d+[a-zA-Z]|[a-zA-Z]\d+@', email):
            continue
        
        cleaned_emails.append(email)
    
    # Return unique, sorted list
    return sorted(list(set(cleaned_emails)))


def _is_valid_email(email: str) -> bool:
    """
    Validate email format and content.
    
    Checks:
    - Standard email format (user@domain.tld)
    - Not empty
    - Domain has valid TLD (at least 2 characters)
    - Email doesn't contain obvious junk
    """
    if not email or not isinstance(email, str):
        return False
    
    email = email.strip().lower()
    
    # Must contain exactly one @
    if email.count('@') != 1:
        return False
    
    # Basic format check
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False
    
    # Split to check parts
    parts = email.split('@')
    if len(parts) != 2:
        return False
    
    local, domain = parts
    
    # Local part should not be empty
    if not local or len(local) < 1:
        return False
    
    # Domain should have valid structure
    if not domain or '.' not in domain:
        return False
    
    # Domain should not be in excluded list
    if domain in EXCLUDED_EMAIL_DOMAINS:
        return False
    
    # Domain TLD should be at least 2 chars
    tld = domain.split('.')[-1]
    if len(tld) < 2:
        return False
    
    return True


def clean_phone(text: str) -> str:
    """
    Clean phone number from text.
    
    Rules:
    - Keep only digits, +, spaces, hyphens, parentheses
    - Remove emails accidentally attached to phone numbers
    - Validate minimum length (8 digits minimum)
    - Normalize format
    
    Args:
        text: Raw text containing phone number
        
    Returns:
        Cleaned phone number or empty string
    """
    if not text:
        return ''
    
    # Extract phone patterns (various formats)
    # Match: +1-555-123-4567, (555) 123-4567, 555.123.4567, etc.
    phone_patterns = [
        r'\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
        r'\+?\d{10,15}',  # Simple digit sequences
        r'\(\d{3}\)\s?\d{3}[-.\s]?\d{4}',  # US format: (555) 123-4567
    ]
    
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            # Clean: keep only digits, +, spaces, hyphens, parentheses
            cleaned = re.sub(r'[^\d\+\s\-\(\)]', '', match)
            
            # Remove if email attached (contains @)
            if '@' in cleaned:
                continue
            
            # Extract digits for validation
            digits = re.sub(r'[^\d]', '', cleaned)
            
            # Validate: must have at least 8 digits (international minimum)
            # and not more than 15 (ITU-T E.164 maximum)
            if 8 <= len(digits) <= 15:
                # Normalize: prefer format with spaces/hyphens
                if len(digits) == 10:  # US format
                    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
                elif len(digits) == 11 and digits[0] == '1':  # US with country code
                    return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
                else:
                    # Return cleaned version
                    return cleaned.strip()
    
    return ''


def extract_executives(html: str) -> List[str]:
    """
    Extract executive contacts with STRICT validation.
    
    ONLY accept executives if ALL are present:
    - Person name (First Last format)
    - Role: CEO | CTO | Founder | Director
    - Email address
    
    DO NOT guess executives.
    DO NOT infer from titles alone.
    
    Args:
        html: HTML content from webpage
        
    Returns:
        List of formatted strings: "Name (Title): email@domain.com"
    """
    if not html:
        return []
    
    executives = []
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script/style tags
        for tag in soup(['script', 'style', 'noscript']):
            tag.decompose()
        
        # Look for executive sections (team, leadership, about)
        executive_sections = soup.find_all(['div', 'section', 'article'], 
                                          class_=re.compile(r'team|executive|leader|founder|ceo|cto|about', re.I))
        
        for section in executive_sections:
            # Find all person entries in this section
            person_elements = section.find_all(['div', 'article', 'li'], 
                                              class_=re.compile(r'person|member|executive|founder|team', re.I))
            
            for person in person_elements:
                # Extract name (from heading or strong/bold text)
                name_elem = person.find(['h1', 'h2', 'h3', 'h4', 'h5', 'strong', 'b'])
                if not name_elem:
                    # Try finding name in first text node
                    name_elem = person.find('span', class_=re.compile(r'name', re.I))
                
                if not name_elem:
                    continue
                
                name = name_elem.get_text(strip=True)
                
                # Validate name: must be "First Last" format (at least 2 words)
                name_parts = name.split()
                if len(name_parts) < 2:
                    continue
                
                # Name should start with capital letter
                if not re.match(r'^[A-Z]', name):
                    continue
                
                # Extract title/role
                title_elem = person.find(['p', 'span', 'div'], 
                                        class_=re.compile(r'title|role|position', re.I))
                if not title_elem:
                    # Search in all text of person element
                    person_text = person.get_text()
                    title_match = re.search(rf'({"|".join(EXECUTIVE_TITLES)})', person_text, re.I)
                    if title_match:
                        title = title_match.group(1)
                    else:
                        continue
                else:
                    title = title_elem.get_text(strip=True)
                
                # Validate title contains executive role
                title_upper = title.upper()
                is_executive = any(exec_title.upper() in title_upper for exec_title in EXECUTIVE_TITLES)
                if not is_executive:
                    continue
                
                # Extract email (required!)
                email = None
                
                # Check mailto links first (most reliable)
                mailto_link = person.find('a', href=re.compile(r'mailto:', re.I))
                if mailto_link:
                    mailto_match = re.search(r'mailto:([^\?&]+)', mailto_link.get('href', ''), re.I)
                    if mailto_match:
                        email = mailto_match.group(1).strip().lower()
                
                # If no mailto, search in person text
                if not email:
                    person_text = person.get_text()
                    email_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
                    email_matches = re.findall(email_pattern, person_text)
                    for match in email_matches:
                        if _is_valid_email(match):
                            email = match.lower()
                            break
                
                # CRITICAL: Only accept if ALL components present
                if name and title and email:
                    # Format: "Name (Title): email"
                    exec_str = f"{name} ({title}): {email}"
                    executives.append(exec_str)
    
    except Exception as e:
        logger.debug(f"Error extracting executives: {e}")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_executives = []
    for exec_str in executives:
        if exec_str not in seen:
            seen.add(exec_str)
            unique_executives.append(exec_str)
    
    return unique_executives


def normalize_domain(url: str) -> str:
    """
    Normalize domain from URL.
    
    Rules:
    - Extract netloc using urlparse
    - Remove "www." prefix
    - Convert to lowercase
    - Return empty string if invalid
    
    Args:
        url: Website URL
        
    Returns:
        Normalized domain name or empty string
    """
    if not url or not isinstance(url, str):
        return ''
    
    url = url.strip()
    
    # Add protocol if missing (urlparse needs it)
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        
        if not domain:
            return ''
        
        # Remove www. prefix (case-insensitive)
        domain = re.sub(r'^www\.', '', domain, flags=re.I)
        
        # Remove port if present
        domain = domain.split(':')[0]
        
        # Convert to lowercase
        domain = domain.lower()
        
        # Basic validation: should contain at least one dot
        if '.' not in domain:
            return ''
        
        return domain
    
    except Exception:
        return ''


def sanitize_lead(lead: Dict) -> Dict:
    """
    Sanitize a lead dictionary before saving.
    
    Applies all cleaning functions and validates data quality.
    
    Args:
        lead: Raw lead dictionary from scraper
        
    Returns:
        Sanitized lead dictionary
    """
    if not isinstance(lead, dict):
        return {}
    
    sanitized = {}
    
    # Copy basic fields (no cleaning needed)
    for field in ['name', 'city', 'country', 'rating', 'maps_url', 'source', 'scraped_at']:
        if field in lead:
            sanitized[field] = str(lead[field]).strip() if lead[field] else ''
    
    # Clean and normalize domain
    website = lead.get('website', '') or lead.get('maps_url', '')
    sanitized['domain'] = normalize_domain(website)
    sanitized['website'] = website.strip() if website else ''
    
    # Clean phone
    phone = lead.get('phone', '')
    sanitized['phone'] = clean_phone(phone) if phone else ''
    
    # Clean emails
    # Note: We don't have raw HTML here, so we work with already-extracted emails
    # If you have raw_html field, use clean_emails(raw_html) instead
    all_emails_raw = lead.get('all_emails', '')
    email_raw = lead.get('email', '')
    
    # Combine all email sources
    email_list = []
    if all_emails_raw:
        # Split comma-separated emails
        email_list.extend([e.strip() for e in str(all_emails_raw).split(',')])
    if email_raw:
        email_list.append(email_raw.strip())
    
    # Filter and clean emails
    cleaned_emails = []
    for email in email_list:
        if email and _is_valid_email(email):
            email_lower = email.lower()
            domain = email_lower.split('@')[1] if '@' in email_lower else ''
            if domain not in EXCLUDED_EMAIL_DOMAINS:
                cleaned_emails.append(email_lower)
    
    # Remove duplicates
    cleaned_emails = list(dict.fromkeys(cleaned_emails))  # Preserves order
    
    # Set email fields
    sanitized['all_emails'] = ', '.join(cleaned_emails) if cleaned_emails else ''
    sanitized['email'] = cleaned_emails[0] if cleaned_emails else ''
    
    # Clean executives
    executives_raw = lead.get('executives', '')
    if executives_raw:
        # If executives is already formatted string, try to parse
        # Otherwise, if you have raw HTML, use extract_executives(html)
        sanitized['executives'] = str(executives_raw).strip()
    else:
        sanitized['executives'] = ''
    
    # Clean industry/category - MUST come from keyword, not website content
    category = lead.get('category', '') or lead.get('keyword', '')
    sanitized['category'] = str(category).strip()[:100] if category else ''  # Limit length
    
    industry = lead.get('industry', '')
    # Industry should be a simple classification, not long text
    sanitized['industry'] = str(industry).strip().split(',')[0][:50] if industry else ''
    sanitized['all_industries'] = ''  # Clear this if it contains website content
    
    # Clean address
    address = lead.get('address', '')
    sanitized['address'] = str(address).strip()[:200] if address else ''
    
    # WhatsApp (if present)
    whatsapp = lead.get('whatsapp', '')
    sanitized['whatsapp'] = clean_phone(whatsapp) if whatsapp else ''
    
    return sanitized


def is_valid_lead(lead: Dict) -> bool:
    """
    Validate if a lead is worth saving.
    
    Drop lead if:
    - No domain AND no email
    - Email list empty (if emails are required)
    
    Args:
        lead: Sanitized lead dictionary
        
    Returns:
        True if lead should be saved, False otherwise
    """
    domain = lead.get('domain', '')
    email = lead.get('email', '')
    all_emails = lead.get('all_emails', '')
    
    # Must have at least domain OR email
    if not domain and not email:
        return False
    
    # Must have at least name
    name = lead.get('name', '').strip()
    if not name or len(name) < 2:
        return False
    
    return True

