#!/usr/bin/env python3
"""
Setup script for Indonesian Brand Scraper Bot
Installs dependencies and prepares the environment
"""

import subprocess
import sys
import os
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    else:
        print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
        return True

def install_requirements():
    """Install Python requirements"""
    return run_command("pip install -r requirements.txt", "Installing Python dependencies")

def download_nltk_data():
    """Download required NLTK data"""
    try:
        import nltk
        print("🔧 Downloading NLTK data...")
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        print("✅ NLTK data downloaded successfully")
        return True
    except Exception as e:
        print(f"⚠️  NLTK data download failed: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ['scraped_data', 'logs']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"📁 Directory already exists: {directory}")
    
    return True

def check_chrome_driver():
    """Check if ChromeDriver is available"""
    try:
        result = subprocess.run("chromedriver --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ChromeDriver is available")
            print(f"Version: {result.stdout.strip()}")
            return True
        else:
            print("❌ ChromeDriver not found in PATH")
            return False
    except Exception as e:
        print(f"❌ Error checking ChromeDriver: {e}")
        return False

def install_chrome_driver():
    """Provide instructions for ChromeDriver installation"""
    system = platform.system().lower()
    
    print("\n" + "="*60)
    print("CHROMEDRIVER INSTALLATION INSTRUCTIONS")
    print("="*60)
    
    if system == "linux":
        print("For Ubuntu/Debian:")
        print("1. sudo apt-get update")
        print("2. sudo apt-get install -y wget unzip")
        print("3. wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE")
        print("4. wget https://chromedriver.storage.googleapis.com/$(cat LATEST_RELEASE)/chromedriver_linux64.zip")
        print("5. unzip chromedriver_linux64.zip")
        print("6. sudo mv chromedriver /usr/local/bin/")
        print("7. sudo chmod +x /usr/local/bin/chromedriver")
        
    elif system == "darwin":  # macOS
        print("For macOS:")
        print("1. brew install chromedriver")
        print("Or manually:")
        print("2. Download from https://chromedriver.chromium.org/")
        print("3. Move to /usr/local/bin/")
        
    elif system == "windows":
        print("For Windows:")
        print("1. Download ChromeDriver from https://chromedriver.chromium.org/")
        print("2. Extract chromedriver.exe")
        print("3. Add the folder to your PATH environment variable")
        print("4. Or place chromedriver.exe in this project directory")
    
    print("\nNote: Make sure your ChromeDriver version matches your Chrome browser version")
    print("="*60)

def test_installation():
    """Test if everything is working"""
    print("\n🧪 Testing installation...")
    
    try:
        # Test imports
        from indonesian_brand_scraper import IndonesianBrandScraper
        from brand_analyzer import BrandAnalyzer
        print("✅ Core modules imported successfully")
        
        # Test scraper initialization
        scraper = IndonesianBrandScraper()
        print("✅ Scraper initialized successfully")
        
        # Test analyzer initialization
        analyzer = BrandAnalyzer()
        print("✅ Analyzer initialized successfully")
        
        print("🎉 Installation test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Indonesian Brand Scraper Bot")
    print("="*50)
    
    success_count = 0
    total_steps = 6
    
    # 1. Check Python version
    if check_python_version():
        success_count += 1
    
    # 2. Install requirements
    if install_requirements():
        success_count += 1
    
    # 3. Download NLTK data
    if download_nltk_data():
        success_count += 1
    
    # 4. Create directories
    if create_directories():
        success_count += 1
    
    # 5. Check ChromeDriver
    if check_chrome_driver():
        success_count += 1
    else:
        install_chrome_driver()
    
    # 6. Test installation
    if test_installation():
        success_count += 1
    
    # Summary
    print("\n" + "="*50)
    print("SETUP SUMMARY")
    print("="*50)
    print(f"✅ Completed: {success_count}/{total_steps} steps")
    
    if success_count == total_steps:
        print("🎉 Setup completed successfully!")
        print("\nYou can now run the scraper:")
        print("  python main.py scrape")
        print("  python main.py full-pipeline --visualize")
        
    elif success_count >= total_steps - 1:
        print("⚠️  Setup mostly complete with minor issues")
        print("The scraper should work, but you may need to install ChromeDriver manually")
        
    else:
        print("❌ Setup incomplete. Please resolve the issues above")
        
    print("\nFor help, see README.md or run: python main.py --help")

if __name__ == "__main__":
    main()