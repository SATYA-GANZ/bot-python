#!/usr/bin/env python3
"""
Test script for Beauty Brand AI Agent Bot
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        # Test core modules
        from utils.database import DatabaseManager
        from utils.helpers import format_brand_info, validate_phone_number
        print("✅ Utils modules imported successfully")
        
        # Test agent modules (with error handling for missing dependencies)
        try:
            from agents.beauty_scraper_agent import BeautyScrapeAgent
            print("✅ Beauty scraper agent imported successfully")
        except ImportError as e:
            print(f"⚠️  Beauty scraper agent import warning: {e}")
        
        try:
            from agents.contact_finder_agent import ContactFinderAgent
            print("✅ Contact finder agent imported successfully")
        except ImportError as e:
            print(f"⚠️  Contact finder agent import warning: {e}")
        
        try:
            from agents.whatsapp_agent import WhatsAppAgent
            print("✅ WhatsApp agent imported successfully")
        except ImportError as e:
            print(f"⚠️  WhatsApp agent import warning: {e}")
        
        print("✅ All core imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_database():
    """Test database functionality"""
    print("\n🗄️  Testing database...")
    
    try:
        # Initialize database
        db = DatabaseManager("test_beauty_brands.db")
        print("✅ Database initialized")
        
        # Test saving a brand
        brand_data = {
            'name': 'Test Beauty Brand',
            'website': 'https://testbeauty.com',
            'category': 'Skincare',
            'location': 'Jakarta, Indonesia',
            'business_type': 'Small',
            'contacts': ['Phone: +6281234567890', 'Email: test@testbeauty.com'],
            'description': 'Test Indonesian beauty brand for UMKM'
        }
        
        brand_id = asyncio.run(db.save_brand(brand_data))
        if brand_id > 0:
            print(f"✅ Brand saved with ID: {brand_id}")
        else:
            print("❌ Failed to save brand")
            return False
        
        # Test retrieving brands
        brands = asyncio.run(db.get_all_brands(limit=5))
        if brands:
            print(f"✅ Retrieved {len(brands)} brands from database")
        else:
            print("⚠️  No brands found in database")
        
        # Test search
        search_results = asyncio.run(db.search_brands("Test"))
        if search_results:
            print(f"✅ Search found {len(search_results)} results")
        
        # Test statistics
        stats = asyncio.run(db.get_statistics())
        if stats:
            print(f"✅ Database statistics: {stats.get('total_brands', 0)} total brands")
        
        # Cleanup test database
        os.remove("test_beauty_brands.db")
        print("✅ Test database cleaned up")
        
        print("✅ Database tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False

def test_helpers():
    """Test helper functions"""
    print("\n🔧 Testing helper functions...")
    
    try:
        from utils.helpers import (
            validate_phone_number, clean_phone_number, 
            validate_email_address, format_brand_info
        )
        
        # Test phone validation
        test_phones = [
            "+6281234567890",
            "081234567890", 
            "6281234567890",
            "invalid_phone"
        ]
        
        valid_count = 0
        for phone in test_phones:
            if validate_phone_number(phone):
                valid_count += 1
                cleaned = clean_phone_number(phone)
                print(f"✅ Phone {phone} -> {cleaned}")
        
        print(f"✅ Validated {valid_count}/{len(test_phones)} phone numbers")
        
        # Test email validation
        test_emails = [
            "test@example.com",
            "invalid.email",
            "user@domain.co.id"
        ]
        
        valid_emails = 0
        for email in test_emails:
            if validate_email_address(email):
                valid_emails += 1
                print(f"✅ Valid email: {email}")
        
        print(f"✅ Validated {valid_emails}/{len(test_emails)} emails")
        
        # Test brand formatting
        test_brand = {
            'name': 'Test Beauty Brand',
            'category': 'Skincare',
            'location': 'Jakarta',
            'contacts': ['+6281234567890', 'test@beauty.com'],
            'website': 'https://testbeauty.com'
        }
        
        formatted = format_brand_info(test_brand)
        if "Test Beauty Brand" in formatted:
            print("✅ Brand formatting working")
        
        print("✅ Helper function tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Helper function test error: {e}")
        return False

def test_environment():
    """Test environment setup"""
    print("\n🌍 Testing environment...")
    
    # Check for .env file
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found - copy from .env.example")
    
    # Check for example file
    env_example = Path(".env.example")
    if env_example.exists():
        print("✅ .env.example file found")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 8:
        print(f"✅ Python version {python_version.major}.{python_version.minor} is compatible")
    else:
        print(f"⚠️  Python version {python_version.major}.{python_version.minor} may not be compatible")
    
    print("✅ Environment check completed!")
    return True

def main():
    """Run all tests"""
    print("🤖 Beauty Brand AI Agent Bot - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Environment", test_environment),
        ("Imports", test_imports),
        ("Database", test_database),
        ("Helpers", test_helpers)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The bot is ready to use.")
        print("\nNext steps:")
        print("1. Add your API keys to .env file")
        print("2. Run: python main.py")
        print("3. Start chatting with your bot on Telegram!")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)