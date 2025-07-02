"""
Configuration file for Indonesian Brand Scraper Bot
"""

import os
from typing import List, Dict

# Search terms for Indonesian brands
INDONESIAN_BRAND_KEYWORDS = [
    "brand indonesia",
    "merek lokal indonesia", 
    "produk indonesia",
    "brand fashion indonesia",
    "startup indonesia",
    "umkm indonesia",
    "brand makanan indonesia",
    "brand kecantikan indonesia",
    "brand teknologi indonesia"
]

# Target websites for scraping
TARGET_WEBSITES = {
    "startup_ranking": "https://www.startupranking.com/countries/indonesia",
    "indonesian_brands": "https://id.wikipedia.org/wiki/Kategori:Merek_Indonesia",
    "business_news": "https://www.cnbcindonesia.com/",
    "tech_news": "https://dailysocial.id/",
    "fashion_brands": "https://www.fimela.com/fashion"
}

# Request settings
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Selenium settings
SELENIUM_OPTIONS = [
    '--headless',
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--window-size=1920,1080'
]

# Output settings
OUTPUT_FORMATS = ['json', 'csv', 'excel']
OUTPUT_DIRECTORY = 'scraped_data'

# Rate limiting (seconds between requests)
REQUEST_DELAY = 2
MAX_RETRIES = 3

# Categories to search for
BRAND_CATEGORIES = [
    "Fashion",
    "Food & Beverage", 
    "Technology",
    "Beauty & Cosmetics",
    "Automotive",
    "Healthcare",
    "Education",
    "E-commerce",
    "Fintech",
    "Gaming"
]