"""
Database handler for storing leads (MongoDB and CSV)
"""
import os
import csv
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd

from config import (
    MONGODB_ENABLED, MONGODB_URI, MONGODB_DATABASE, MONGODB_COLLECTION,
    CSV_FOLDER, CSV_FILENAME, EXCEL_FILENAME
)

logger = logging.getLogger(__name__)

# MongoDB client (lazy initialization)
_mongo_client = None
_mongo_db = None
_mongo_collection = None


def init_mongodb():
    """
    Initialize MongoDB connection.
    """
    global _mongo_client, _mongo_db, _mongo_collection
    
    if not MONGODB_ENABLED:
        logger.info("MongoDB is disabled. Using CSV only.")
        return
    
    try:
        from pymongo import MongoClient
        
        _mongo_client = MongoClient(MONGODB_URI)
        _mongo_db = _mongo_client[MONGODB_DATABASE]
        _mongo_collection = _mongo_db[MONGODB_COLLECTION]
        
        # Create index on website domain for duplicate checking
        _mongo_collection.create_index("domain", unique=False)
        
        logger.info(f"MongoDB connected: {MONGODB_DATABASE}.{MONGODB_COLLECTION}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        logger.warning("Falling back to CSV storage only.")
        _mongo_client = None
        _mongo_db = None
        _mongo_collection = None


def ensure_csv_folder():
    """
    Ensure CSV export folder exists.
    """
    if not os.path.exists(CSV_FOLDER):
        os.makedirs(CSV_FOLDER)
        logger.info(f"Created folder: {CSV_FOLDER}")


def normalize_lead(lead: Dict) -> Dict:
    """
    Normalize and validate lead data.
    Note: lead is already sanitized by sanitize_lead() before this is called,
    so domain is already normalized.
    """
    from utils import clean_text
    
    normalized = {
        "name": clean_text(lead.get("name", "")),
        "email": clean_text(lead.get("email", "")),
        "all_emails": clean_text(lead.get("all_emails", "")),
        "phone": clean_text(lead.get("phone", "")),
        "whatsapp": clean_text(lead.get("whatsapp", "")),
        "executives": clean_text(lead.get("executives", "")),
        "website": clean_text(lead.get("website", "")),
        "category": clean_text(lead.get("category", "")),
        "industry": clean_text(lead.get("industry", "")),
        "all_industries": clean_text(lead.get("all_industries", "")),
        "needs_tech_support": lead.get("needs_tech_support", True),
        "address": clean_text(lead.get("address", "")),
        "city": clean_text(lead.get("city", "")),
        "country": clean_text(lead.get("country", "")),
        "rating": lead.get("rating", ""),
        "maps_url": lead.get("maps_url", ""),
        "domain": clean_text(lead.get("domain", "")),  # Already normalized in sanitize_lead
        "scraped_at": datetime.now().isoformat(),
        "source": "google_maps"
    }
    
    return normalized


def is_duplicate(lead: Dict) -> bool:
    """
    Check if lead already exists (by domain or website).
    """
    global _mongo_collection
    
    if not lead.get("domain") and not lead.get("website"):
        return False
    
    # Check MongoDB if enabled
    if _mongo_collection:
        try:
            query = {}
            if lead.get("domain"):
                query["domain"] = lead["domain"]
            elif lead.get("website"):
                query["website"] = lead["website"]
            
            if query and _mongo_collection.find_one(query):
                return True
        except Exception as e:
            logger.error(f"Error checking duplicate in MongoDB: {e}")
    
    # Check CSV file
    csv_path = os.path.join(CSV_FOLDER, CSV_FILENAME)
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            domain = lead.get("domain", "")
            website = lead.get("website", "")
            
            if domain:
                if "domain" in df.columns and (df["domain"] == domain).any():
                    return True
            if website:
                if "website" in df.columns and (df["website"] == website).any():
                    return True
        except Exception as e:
            logger.error(f"Error checking duplicate in CSV: {e}")
    
    return False


def save_lead(lead: Dict) -> bool:
    """
    Save a single lead to database (MongoDB and/or CSV).
    Returns True if saved, False if duplicate or error.
    """
    global _mongo_collection
    
    # Apply data cleaning/sanitization BEFORE normalization
    from data_cleaner import sanitize_lead, is_valid_lead
    
    # Sanitize the lead data
    lead = sanitize_lead(lead)
    
    # Validate lead quality
    if not is_valid_lead(lead):
        logger.debug(f"Invalid lead skipped (no domain/email): {lead.get('name', 'Unknown')}")
        return False
    
    normalized_lead = normalize_lead(lead)
    
    # Skip if duplicate
    if is_duplicate(normalized_lead):
        logger.debug(f"Duplicate lead skipped: {normalized_lead.get('name', 'Unknown')}")
        return False
    
    # Save to MongoDB
    if _mongo_collection:
        try:
            _mongo_collection.insert_one(normalized_lead.copy())
            logger.debug(f"Lead saved to MongoDB: {normalized_lead.get('name', 'Unknown')}")
        except Exception as e:
            logger.error(f"Error saving to MongoDB: {e}")
    
    # Save to CSV (append mode)
    ensure_csv_folder()
    csv_path = os.path.join(CSV_FOLDER, CSV_FILENAME)
    
    try:
        file_exists = os.path.exists(csv_path)
        
        # Prepare CSV row (exclude internal fields)
        csv_row = {
            "name": normalized_lead["name"],
            "email": normalized_lead["email"],
            "all_emails": normalized_lead.get("all_emails", ""),
            "phone": normalized_lead["phone"],
            "whatsapp": normalized_lead.get("whatsapp", ""),
            "executives": normalized_lead.get("executives", ""),
            "website": normalized_lead["website"],
            "category": normalized_lead["category"],
            "industry": normalized_lead.get("industry", ""),
            "all_industries": normalized_lead.get("all_industries", ""),
            "needs_tech_support": normalized_lead.get("needs_tech_support", True),
            "address": normalized_lead["address"],
            "city": normalized_lead["city"],
            "country": normalized_lead["country"],
            "rating": normalized_lead["rating"],
            "maps_url": normalized_lead["maps_url"],
            "domain": normalized_lead["domain"],
            "scraped_at": normalized_lead["scraped_at"],
            "source": normalized_lead["source"]
        }
        
        # Write to CSV
        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            fieldnames = list(csv_row.keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(csv_row)
        
        logger.info(f"Lead saved to CSV: {normalized_lead.get('name', 'Unknown')}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving to CSV: {e}")
        return False


def get_total_leads() -> int:
    """
    Get total number of leads saved.
    """
    global _mongo_collection
    
    count = 0
    
    # Count from MongoDB
    if _mongo_collection:
        try:
            count = _mongo_collection.count_documents({})
            return count
        except Exception as e:
            logger.error(f"Error counting MongoDB leads: {e}")
    
    # Count from CSV
    csv_path = os.path.join(CSV_FOLDER, CSV_FILENAME)
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            return len(df)
        except Exception as e:
            logger.error(f"Error counting CSV leads: {e}")
    
    return count


def export_to_excel() -> str:
    """
    Export CSV to Excel format.
    Returns path to Excel file.
    """
    csv_path = os.path.join(CSV_FOLDER, CSV_FILENAME)
    excel_path = os.path.join(CSV_FOLDER, EXCEL_FILENAME)
    
    if not os.path.exists(csv_path):
        logger.warning("CSV file not found for Excel export")
        return ""
    
    try:
        df = pd.read_csv(csv_path)
        df.to_excel(excel_path, index=False, engine='openpyxl')
        logger.info(f"Exported to Excel: {excel_path}")
        return excel_path
    except Exception as e:
        logger.error(f"Error exporting to Excel: {e}")
        return ""


def close_mongodb():
    """
    Close MongoDB connection.
    """
    global _mongo_client
    
    if _mongo_client:
        try:
            _mongo_client.close()
            logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB: {e}")

