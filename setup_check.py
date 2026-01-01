#!/usr/bin/env python3
"""
Setup verification script - Check if all dependencies are installed
"""
import sys

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("[X] Python 3.8+ is required. Current version: {}.{}".format(version.major, version.minor))
        return False
    print("[OK] Python version: {}.{}.{}".format(version.major, version.minor, version.micro))
    return True

def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"[OK] {package_name} is installed")
        return True
    except ImportError:
        print(f"[X] {package_name} is NOT installed")
        return False

def main():
    print("\n" + "="*60)
    print("Google Maps Lead Scraper - Setup Verification")
    print("="*60 + "\n")
    
    # Check Python version
    if not check_python_version():
        print("\nPlease upgrade to Python 3.8 or higher.")
        sys.exit(1)
    
    print("\nChecking dependencies...\n")
    
    # Required packages
    packages = [
        ("beautifulsoup4", "bs4"),
        ("requests", "requests"),
        ("pymongo", "pymongo"),
        ("pandas", "pandas"),
        ("openpyxl", "openpyxl"),
        ("lxml", "lxml"),
        ("fake-useragent", "fake_useragent"),
        ("playwright", "playwright"),
    ]
    
    missing_packages = []
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            missing_packages.append(package_name)
    
    print("\n" + "-"*60)
    
    if missing_packages:
        print(f"\n[X] Missing packages: {', '.join(missing_packages)}")
        print("\nTo install missing packages, run:")
        print("  pip install -r requirements.txt")
        print("\nOr install individually:")
        for pkg in missing_packages:
            print(f"  pip install {pkg}")
        sys.exit(1)
    else:
        print("\n[OK] All dependencies are installed!")
        print("\nYou're ready to use the scraper!")
        print("\nNext steps:")
        print("  1. Run from command line: python main.py --help")
        print("  2. Or use the launcher: python run_scraper.py")
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()

