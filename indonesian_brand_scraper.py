"""
Indonesian Brand Scraper Bot
A comprehensive tool to scrape and find Indonesian local brands
"""

import requests
import time
import json
import csv
import pandas as pd
import asyncio
import aiohttp
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from googlesearch import search
import wikipedia

from config import *

class IndonesianBrandScraper:
    """
    A comprehensive bot to scrape Indonesian brand information
    """
    
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.brands_data = []
        self.setup_logging()
        self.create_output_directory()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def create_output_directory(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(OUTPUT_DIRECTORY):
            os.makedirs(OUTPUT_DIRECTORY)
            self.logger.info(f"Created output directory: {OUTPUT_DIRECTORY}")
    
    def get_selenium_driver(self):
        """Initialize Selenium WebDriver with options"""
        chrome_options = Options()
        for option in SELENIUM_OPTIONS:
            chrome_options.add_argument(option)
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            return driver
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome driver: {e}")
            return None
    
    def make_request(self, url: str, retries: int = MAX_RETRIES) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        headers = REQUEST_HEADERS.copy()
        headers['User-Agent'] = self.ua.random
        
        for attempt in range(retries):
            try:
                response = self.session.get(url, headers=headers, timeout=30)
                if response.status_code == 200:
                    return response
                else:
                    self.logger.warning(f"HTTP {response.status_code} for {url}")
            except Exception as e:
                self.logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                time.sleep(REQUEST_DELAY * (attempt + 1))
        
        return None
    
    async def async_request(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        """Make asynchronous HTTP request"""
        try:
            async with session.get(url, headers=REQUEST_HEADERS) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    self.logger.warning(f"HTTP {response.status} for {url}")
        except Exception as e:
            self.logger.error(f"Async request failed for {url}: {e}")
        return None
    
    def search_google_for_brands(self, query: str, num_results: int = 10) -> List[str]:
        """Search Google for Indonesian brands"""
        self.logger.info(f"Searching Google for: {query}")
        urls = []
        
        try:
            for url in search(query, num_results=num_results, lang="id", pause=2):
                urls.append(url)
                time.sleep(1)  # Be respectful to Google
        except Exception as e:
            self.logger.error(f"Google search failed: {e}")
        
        return urls
    
    def scrape_wikipedia_brands(self) -> List[Dict]:
        """Scrape Indonesian brands from Wikipedia"""
        self.logger.info("Scraping Wikipedia for Indonesian brands")
        brands = []
        
        try:
            # Search for Indonesian brands on Wikipedia
            wikipedia.set_lang("id")
            search_results = wikipedia.search("merek Indonesia", results=20)
            
            for result in search_results:
                try:
                    page = wikipedia.page(result)
                    brand_info = {
                        'name': page.title,
                        'summary': page.summary[:500] + "..." if len(page.summary) > 500 else page.summary,
                        'url': page.url,
                        'source': 'Wikipedia',
                        'category': 'General',
                        'scraped_at': datetime.now().isoformat()
                    }
                    brands.append(brand_info)
                    time.sleep(1)
                except Exception as e:
                    self.logger.error(f"Failed to get Wikipedia page for {result}: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Wikipedia search failed: {e}")
        
        return brands
    
    def scrape_startup_ranking(self) -> List[Dict]:
        """Scrape Indonesian startups from StartupRanking"""
        self.logger.info("Scraping StartupRanking for Indonesian startups")
        brands = []
        
        url = TARGET_WEBSITES["startup_ranking"]
        response = self.make_request(url)
        
        if response:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for startup listings
            startup_elements = soup.find_all('div', class_=['startup-item', 'company-item', 'startup'])
            
            for element in startup_elements[:20]:  # Limit to 20 results
                try:
                    name_elem = element.find(['h3', 'h4', 'a'], class_=['name', 'title', 'company-name'])
                    desc_elem = element.find(['p', 'div'], class_=['description', 'summary'])
                    
                    if name_elem:
                        brand_info = {
                            'name': name_elem.get_text(strip=True),
                            'summary': desc_elem.get_text(strip=True) if desc_elem else 'No description available',
                            'url': url,
                            'source': 'StartupRanking',
                            'category': 'Technology/Startup',
                            'scraped_at': datetime.now().isoformat()
                        }
                        brands.append(brand_info)
                except Exception as e:
                    self.logger.error(f"Error parsing startup element: {e}")
                    continue
        
        return brands
    
    def scrape_news_sites(self) -> List[Dict]:
        """Scrape brand mentions from Indonesian news sites"""
        self.logger.info("Scraping Indonesian news sites for brand mentions")
        brands = []
        
        news_sites = {
            "CNBC Indonesia": "https://www.cnbcindonesia.com/tech",
            "Daily Social": "https://dailysocial.id/"
        }
        
        for site_name, url in news_sites.items():
            try:
                response = self.make_request(url)
                if response:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for article titles that might contain brand names
                    articles = soup.find_all(['h1', 'h2', 'h3'], class_=['title', 'headline'])
                    
                    for article in articles[:10]:  # Limit results
                        title = article.get_text(strip=True)
                        if any(keyword in title.lower() for keyword in ['startup', 'brand', 'teknologi', 'aplikasi']):
                            brand_info = {
                                'name': title,
                                'summary': f'Brand mention found in {site_name}',
                                'url': url,
                                'source': site_name,
                                'category': 'News Mention',
                                'scraped_at': datetime.now().isoformat()
                            }
                            brands.append(brand_info)
                            
            except Exception as e:
                self.logger.error(f"Error scraping {site_name}: {e}")
                continue
        
        return brands
    
    def search_social_media_brands(self) -> List[Dict]:
        """Search for Indonesian brands mentioned on social media"""
        self.logger.info("Searching for Indonesian brands on social media")
        brands = []
        
        # Use Google search to find brand discussions
        for keyword in INDONESIAN_BRAND_KEYWORDS[:3]:  # Limit to 3 keywords
            search_query = f"{keyword} site:instagram.com OR site:twitter.com OR site:linkedin.com"
            urls = self.search_google_for_brands(search_query, 5)
            
            for url in urls:
                brand_info = {
                    'name': f'Social media mention: {keyword}',
                    'summary': f'Brand found through social media search for {keyword}',
                    'url': url,
                    'source': 'Social Media Search',
                    'category': 'Social Media',
                    'scraped_at': datetime.now().isoformat()
                }
                brands.append(brand_info)
        
        return brands
    
    def run_comprehensive_scrape(self) -> List[Dict]:
        """Run comprehensive scraping from all sources"""
        self.logger.info("Starting comprehensive Indonesian brand scraping")
        all_brands = []
        
        # 1. Wikipedia scraping
        try:
            wikipedia_brands = self.scrape_wikipedia_brands()
            all_brands.extend(wikipedia_brands)
            self.logger.info(f"Found {len(wikipedia_brands)} brands from Wikipedia")
        except Exception as e:
            self.logger.error(f"Wikipedia scraping failed: {e}")
        
        # 2. Startup ranking scraping
        try:
            startup_brands = self.scrape_startup_ranking()
            all_brands.extend(startup_brands)
            self.logger.info(f"Found {len(startup_brands)} brands from StartupRanking")
        except Exception as e:
            self.logger.error(f"StartupRanking scraping failed: {e}")
        
        # 3. News sites scraping
        try:
            news_brands = self.scrape_news_sites()
            all_brands.extend(news_brands)
            self.logger.info(f"Found {len(news_brands)} brands from news sites")
        except Exception as e:
            self.logger.error(f"News sites scraping failed: {e}")
        
        # 4. Social media search
        try:
            social_brands = self.search_social_media_brands()
            all_brands.extend(social_brands)
            self.logger.info(f"Found {len(social_brands)} brands from social media")
        except Exception as e:
            self.logger.error(f"Social media search failed: {e}")
        
        # 5. Google search for specific categories
        for category in BRAND_CATEGORIES[:3]:  # Limit to 3 categories
            try:
                search_query = f"brand {category.lower()} indonesia"
                urls = self.search_google_for_brands(search_query, 3)
                
                for url in urls:
                    brand_info = {
                        'name': f'{category} brand search result',
                        'summary': f'Indonesian {category} brand found through Google search',
                        'url': url,
                        'source': 'Google Search',
                        'category': category,
                        'scraped_at': datetime.now().isoformat()
                    }
                    all_brands.append(brand_info)
                    
            except Exception as e:
                self.logger.error(f"Google search for {category} failed: {e}")
                continue
        
        self.brands_data = all_brands
        self.logger.info(f"Total brands found: {len(all_brands)}")
        return all_brands
    
    def save_data(self, format: str = 'json'):
        """Save scraped data in specified format"""
        if not self.brands_data:
            self.logger.warning("No data to save")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == 'json':
            filename = f"{OUTPUT_DIRECTORY}/indonesian_brands_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.brands_data, f, indent=2, ensure_ascii=False)
            
        elif format == 'csv':
            filename = f"{OUTPUT_DIRECTORY}/indonesian_brands_{timestamp}.csv"
            df = pd.DataFrame(self.brands_data)
            df.to_csv(filename, index=False, encoding='utf-8')
            
        elif format == 'excel':
            filename = f"{OUTPUT_DIRECTORY}/indonesian_brands_{timestamp}.xlsx"
            df = pd.DataFrame(self.brands_data)
            df.to_excel(filename, index=False, engine='openpyxl')
        
        self.logger.info(f"Data saved to {filename}")
    
    def get_brand_statistics(self) -> Dict:
        """Get statistics about scraped brands"""
        if not self.brands_data:
            return {}
        
        df = pd.DataFrame(self.brands_data)
        
        stats = {
            'total_brands': len(self.brands_data),
            'sources': df['source'].value_counts().to_dict(),
            'categories': df['category'].value_counts().to_dict(),
            'scraping_date': datetime.now().isoformat()
        }
        
        return stats
    
    def print_summary(self):
        """Print summary of scraped data"""
        stats = self.get_brand_statistics()
        
        print("\n" + "="*50)
        print("INDONESIAN BRAND SCRAPER SUMMARY")
        print("="*50)
        print(f"Total brands found: {stats.get('total_brands', 0)}")
        print(f"\nSources breakdown:")
        for source, count in stats.get('sources', {}).items():
            print(f"  - {source}: {count}")
        print(f"\nCategories breakdown:")
        for category, count in stats.get('categories', {}).items():
            print(f"  - {category}: {count}")
        print("="*50)

if __name__ == "__main__":
    # Example usage
    scraper = IndonesianBrandScraper()
    
    # Run comprehensive scraping
    brands = scraper.run_comprehensive_scrape()
    
    # Save data in multiple formats
    scraper.save_data('json')
    scraper.save_data('csv')
    scraper.save_data('excel')
    
    # Print summary
    scraper.print_summary()