"""Utility script to clear resume state"""
import os
from config import RESUME_FILE

if os.path.exists(RESUME_FILE):
    os.remove(RESUME_FILE)
    print(f"✓ Cleared resume state file: {RESUME_FILE}")
    print("The scraper will start fresh on the next run.")
else:
    print(f"No resume state file found at: {RESUME_FILE}")

