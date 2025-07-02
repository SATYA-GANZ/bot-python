#!/usr/bin/env python3
"""
Simplified Indonesian Brand Scraper
A working demo version of the Indonesian brand scraper bot
"""

import requests
import time
import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import wikipedia

class SimpleIndonesianBrandScraper:
    """
    A simplified Indonesian brand scraper that works with minimal dependencies
    """
    
    def __init__(self):
        self.brands_data = []
        self.setup_logging()
        self.create_output_directory()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def create_output_directory(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists('scraped_data'):
            os.makedirs('scraped_data')
            self.logger.info("Created output directory: scraped_data")
    
    def make_request(self, url: str, retries: int = 3) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=headers, timeout=30)
                if response.status_code == 200:
                    return response
                else:
                    self.logger.warning(f"HTTP {response.status_code} for {url}")
            except Exception as e:
                self.logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                time.sleep(2 * (attempt + 1))
        
        return None
    
    def scrape_wikipedia_brands(self) -> List[Dict]:
        """Scrape Indonesian brands from Wikipedia"""
        self.logger.info("Scraping Wikipedia for Indonesian brands")
        brands = []
        
        try:
            # Set Wikipedia language to Indonesian
            wikipedia.set_lang("id")
            
            # Search for Indonesian brands
            search_queries = [
                "merek Indonesia",
                "perusahaan Indonesia", 
                "startup Indonesia",
                "brand lokal Indonesia"
            ]
            
            for query in search_queries:
                try:
                    search_results = wikipedia.search(query, results=5)
                    
                    for result in search_results:
                        try:
                            page = wikipedia.page(result)
                            brand_info = {
                                'name': page.title,
                                'summary': page.summary[:300] + "..." if len(page.summary) > 300 else page.summary,
                                'url': page.url,
                                'source': 'Wikipedia',
                                'category': 'General',
                                'search_query': query,
                                'scraped_at': datetime.now().isoformat()
                            }
                            brands.append(brand_info)
                            self.logger.info(f"Found brand: {page.title}")
                            time.sleep(1)  # Be respectful
                        except Exception as e:
                            self.logger.error(f"Failed to get Wikipedia page for {result}: {e}")
                            continue
                            
                except Exception as e:
                    self.logger.error(f"Wikipedia search failed for '{query}': {e}")
                    continue
                    
                time.sleep(2)  # Pause between search queries
                    
        except Exception as e:
            self.logger.error(f"Wikipedia scraping failed: {e}")
        
        return brands
    
    def scrape_news_websites(self) -> List[Dict]:
        """Scrape brand mentions from Indonesian news websites"""
        self.logger.info("Scraping Indonesian news sites for brand mentions")
        brands = []
        
        news_sites = {
            "Kompas": "https://www.kompas.com/",
            "Detik": "https://www.detik.com/"
        }
        
        for site_name, url in news_sites.items():
            try:
                response = self.make_request(url)
                if response:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for article titles that might contain brand names
                    articles = soup.find_all(['h1', 'h2', 'h3', 'a'])
                    
                    brand_keywords = ['startup', 'brand', 'perusahaan', 'teknologi', 'bisnis', 'UMKM']
                    
                    for article in articles[:10]:  # Limit results
                        title = article.get_text(strip=True)
                        if any(keyword.lower() in title.lower() for keyword in brand_keywords):
                            if len(title) > 20:  # Filter out very short titles
                                brand_info = {
                                    'name': title[:100] + "..." if len(title) > 100 else title,
                                    'summary': f'Brand/business mention found in {site_name}',
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
    
    def add_sample_known_brands(self) -> List[Dict]:
        """Add some well-known Indonesian brands for demonstration"""
        self.logger.info("Adding sample well-known Indonesian brands")
        
        known_brands = [
            {
                'name': 'Gojek',
                'summary': 'Indonesian on-demand multi-service platform and digital payment technology group',
                'url': 'https://www.gojek.com/',
                'source': 'Manual Entry',
                'category': 'Technology/Transportation',
                'scraped_at': datetime.now().isoformat()
            },
            {
                'name': 'Tokopedia',
                'summary': 'Indonesian e-commerce company, one of the largest marketplaces in Southeast Asia',
                'url': 'https://www.tokopedia.com/',
                'source': 'Manual Entry',
                'category': 'E-commerce',
                'scraped_at': datetime.now().isoformat()
            },
            {
                'name': 'Traveloka',
                'summary': 'Indonesian unicorn company that provides online travel booking services',
                'url': 'https://www.traveloka.com/',
                'source': 'Manual Entry',
                'category': 'Travel/Technology',
                'scraped_at': datetime.now().isoformat()
            },
            {
                'name': 'Bukalapak',
                'summary': 'Indonesian e-commerce company founded in 2010 by Achmad Zaky',
                'url': 'https://www.bukalapak.com/',
                'source': 'Manual Entry',
                'category': 'E-commerce',
                'scraped_at': datetime.now().isoformat()
            },
            {
                'name': 'Ruangguru',
                'summary': 'Indonesian ed-tech company providing learning management systems and educational content',
                'url': 'https://www.ruangguru.com/',
                'source': 'Manual Entry',
                'category': 'Education/Technology',
                'scraped_at': datetime.now().isoformat()
            }
        ]
        
        return known_brands
    
    def run_demo_scrape(self) -> List[Dict]:
        """Run a demonstration scraping session"""
        self.logger.info("Starting demonstration Indonesian brand scraping")
        all_brands = []
        
        # 1. Add known brands for demonstration
        try:
            known_brands = self.add_sample_known_brands()
            all_brands.extend(known_brands)
            self.logger.info(f"Added {len(known_brands)} known Indonesian brands")
        except Exception as e:
            self.logger.error(f"Failed to add known brands: {e}")
        
        # 2. Wikipedia scraping
        try:
            wikipedia_brands = self.scrape_wikipedia_brands()
            all_brands.extend(wikipedia_brands)
            self.logger.info(f"Found {len(wikipedia_brands)} brands from Wikipedia")
        except Exception as e:
            self.logger.error(f"Wikipedia scraping failed: {e}")
        
        # 3. News sites scraping (optional, might not work due to site protections)
        try:
            news_brands = self.scrape_news_websites()
            all_brands.extend(news_brands)
            self.logger.info(f"Found {len(news_brands)} brands from news sites")
        except Exception as e:
            self.logger.error(f"News sites scraping failed: {e}")
        
        # Remove duplicates based on name
        seen_names = set()
        unique_brands = []
        for brand in all_brands:
            if brand['name'] not in seen_names:
                seen_names.add(brand['name'])
                unique_brands.append(brand)
        
        self.brands_data = unique_brands
        self.logger.info(f"Total unique brands found: {len(unique_brands)}")
        return unique_brands
    
    def save_data(self, format: str = 'json'):
        """Save scraped data in specified format"""
        if not self.brands_data:
            self.logger.warning("No data to save")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == 'json':
            filename = f"scraped_data/indonesian_brands_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.brands_data, f, indent=2, ensure_ascii=False)
            
        elif format == 'csv':
            filename = f"scraped_data/indonesian_brands_{timestamp}.csv"
            # Simple CSV creation without pandas
            with open(filename, 'w', encoding='utf-8') as f:
                if self.brands_data:
                    # Write header
                    headers = list(self.brands_data[0].keys())
                    f.write(','.join(headers) + '\n')
                    
                    # Write data
                    for brand in self.brands_data:
                        values = [str(brand.get(h, '')).replace(',', ';') for h in headers]
                        f.write(','.join(values) + '\n')
        
        self.logger.info(f"Data saved to {filename}")
        return filename
    
    def get_brand_statistics(self) -> Dict:
        """Get statistics about scraped brands"""
        if not self.brands_data:
            return {}
        
        sources = {}
        categories = {}
        
        for brand in self.brands_data:
            source = brand.get('source', 'Unknown')
            category = brand.get('category', 'Unknown')
            
            sources[source] = sources.get(source, 0) + 1
            categories[category] = categories.get(category, 0) + 1
        
        stats = {
            'total_brands': len(self.brands_data),
            'sources': sources,
            'categories': categories,
            'scraping_date': datetime.now().isoformat()
        }
        
        return stats
    
    def print_summary(self):
        """Print summary of scraped data"""
        stats = self.get_brand_statistics()
        
        print("\n" + "="*60)
        print("🇮🇩 INDONESIAN BRAND SCRAPER SUMMARY")
        print("="*60)
        print(f"📊 Total brands found: {stats.get('total_brands', 0)}")
        
        print(f"\n📡 Sources breakdown:")
        for source, count in stats.get('sources', {}).items():
            print(f"   • {source}: {count}")
            
        print(f"\n🏷️  Categories breakdown:")
        for category, count in stats.get('categories', {}).items():
            print(f"   • {category}: {count}")
            
        print("="*60)
        
        # Print some sample brands
        if self.brands_data:
            print(f"\n🔍 Sample brands found:")
            for i, brand in enumerate(self.brands_data[:5], 1):
                print(f"   {i}. {brand['name']} ({brand['source']})")
                print(f"      Category: {brand['category']}")
                print(f"      Summary: {brand['summary'][:80]}...")
                print()
    
    def analyze_brands(self):
        """Simple analysis of brand data"""
        if not self.brands_data:
            print("❌ No data to analyze")
            return
        
        print("\n📈 BRAND ANALYSIS")
        print("="*40)
        
        # Find technology/startup brands
        tech_brands = [b for b in self.brands_data if 'teknologi' in b['summary'].lower() or 'startup' in b['summary'].lower() or 'Technology' in b['category']]
        print(f"🚀 Technology/Startup brands: {len(tech_brands)}")
        
        # Find e-commerce brands
        ecommerce_brands = [b for b in self.brands_data if 'e-commerce' in b['summary'].lower() or 'E-commerce' in b['category']]
        print(f"🛒 E-commerce brands: {len(ecommerce_brands)}")
        
        # Find unicorn mentions
        unicorn_brands = [b for b in self.brands_data if 'unicorn' in b['summary'].lower()]
        print(f"🦄 Unicorn company mentions: {len(unicorn_brands)}")
        
        # Most common words in summaries
        all_words = []
        for brand in self.brands_data:
            words = brand['summary'].lower().split()
            all_words.extend([w for w in words if len(w) > 4])
        
        word_counts = {}
        for word in all_words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        print(f"\n🔤 Common keywords:")
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        for word, count in sorted_words[:5]:
            print(f"   • {word}: {count} mentions")

def main():
    """Main function to demonstrate the scraper"""
    print("🇮🇩 INDONESIAN BRAND SCRAPER - DEMO VERSION")
    print("="*60)
    print("This is a simplified demo version of the Indonesian brand scraper.")
    print("It will collect brands from Wikipedia and demonstrate the functionality.\n")
    
    # Initialize scraper
    scraper = SimpleIndonesianBrandScraper()
    
    # Run scraping
    print("🚀 Starting brand discovery...")
    brands = scraper.run_demo_scrape()
    
    # Save data
    print("\n💾 Saving data...")
    scraper.save_data('json')
    scraper.save_data('csv')
    
    # Print summary
    scraper.print_summary()
    
    # Analyze brands
    scraper.analyze_brands()
    
    print(f"\n✅ Demo completed! Found {len(brands)} Indonesian brands")
    print("📁 Check the 'scraped_data' directory for output files")
    print("\nTo run the full version, install all dependencies and use main.py")

if __name__ == "__main__":
    main()