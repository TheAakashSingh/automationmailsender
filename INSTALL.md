# Installation Guide - Troubleshooting

## If you encounter SSL/Network errors during installation:

### Option 1: Update pip first (Recommended)
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Option 2: Install packages one by one
If batch installation fails, try installing packages individually:
```bash
pip install selenium
pip install undetected-chromedriver
pip install beautifulsoup4
pip install requests
pip install pymongo
pip install pandas
pip install openpyxl
pip install lxml
pip install fake-useragent
```

### Option 3: Use --trusted-host flag (if behind corporate firewall)
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Option 4: Python 3.13 Compatibility
If you're using Python 3.13 (very new), some packages might need newer versions. Try:
```bash
pip install --upgrade pip setuptools wheel
pip install selenium undetected-chromedriver beautifulsoup4 requests pymongo pandas openpyxl lxml fake-useragent
```

### Option 5: Install without version constraints
Edit `requirements.txt` and remove version numbers (use `>=` instead of `==`), then:
```bash
pip install -r requirements.txt
```

### Option 6: Use a virtual environment (Recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

## Minimum Required Packages (if pandas fails)
If pandas installation continues to fail, you can still use the scraper with CSV-only mode (MongoDB optional). The core packages needed are:
- selenium
- undetected-chromedriver
- beautifulsoup4
- requests
- fake-useragent

Pandas and openpyxl are only needed for Excel export. MongoDB (pymongo) is optional.

## Verify Installation
After installation, run:
```bash
python setup_check.py
```

This will verify all packages are installed correctly.

