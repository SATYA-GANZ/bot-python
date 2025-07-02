#!/usr/bin/env python3
"""
Example Usage of Indonesian Brand Scraper Bot
Demonstrates various ways to use the scraper programmatically
"""

import os
import json
import time
from datetime import datetime

# Import our modules
from indonesian_brand_scraper import IndonesianBrandScraper
from brand_analyzer import BrandAnalyzer

def example_basic_scraping():
    """Example 1: Basic scraping"""
    print("="*60)
    print("EXAMPLE 1: BASIC SCRAPING")
    print("="*60)
    
    # Initialize the scraper
    scraper = IndonesianBrandScraper()
    
    print("🚀 Starting basic scraping...")
    
    # Run comprehensive scraping
    brands = scraper.run_comprehensive_scrape()
    
    # Print some results
    print(f"\n📊 Found {len(brands)} brands total")
    
    if brands:
        print("\n🔍 Sample brands found:")
        for i, brand in enumerate(brands[:5], 1):
            print(f"  {i}. {brand['name']} (Source: {brand['source']})")
    
    # Save data in different formats
    print("\n💾 Saving data...")
    scraper.save_data('json')
    scraper.save_data('csv')
    
    # Print summary
    scraper.print_summary()
    
    return brands

def example_wikipedia_only():
    """Example 2: Wikipedia-only scraping"""
    print("\n" + "="*60)
    print("EXAMPLE 2: WIKIPEDIA-ONLY SCRAPING")
    print("="*60)
    
    scraper = IndonesianBrandScraper()
    
    print("🔍 Scraping Wikipedia for Indonesian brands...")
    
    # Scrape only from Wikipedia
    wikipedia_brands = scraper.scrape_wikipedia_brands()
    
    print(f"📚 Found {len(wikipedia_brands)} brands from Wikipedia")
    
    if wikipedia_brands:
        print("\n📋 Wikipedia brands:")
        for i, brand in enumerate(wikipedia_brands[:3], 1):
            print(f"  {i}. {brand['name']}")
            print(f"     Summary: {brand['summary'][:100]}...")
            print()
    
    return wikipedia_brands

def example_targeted_search():
    """Example 3: Targeted Google search"""
    print("\n" + "="*60)
    print("EXAMPLE 3: TARGETED SEARCH")
    print("="*60)
    
    scraper = IndonesianBrandScraper()
    
    # Search for specific types of brands
    searches = [
        "startup fintech indonesia",
        "brand fashion lokal indonesia",
        "aplikasi buatan indonesia"
    ]
    
    all_results = []
    
    for query in searches:
        print(f"🔍 Searching for: {query}")
        
        # Search Google
        urls = scraper.search_google_for_brands(query, num_results=5)
        
        print(f"   Found {len(urls)} results")
        for i, url in enumerate(urls[:3], 1):
            print(f"   {i}. {url}")
        
        all_results.extend(urls)
        time.sleep(2)  # Be respectful
    
    print(f"\n📊 Total search results: {len(all_results)}")
    return all_results

def example_data_analysis():
    """Example 4: Data analysis"""
    print("\n" + "="*60)
    print("EXAMPLE 4: DATA ANALYSIS")
    print("="*60)
    
    # First, let's create some sample data or use existing data
    scraper = IndonesianBrandScraper()
    
    # Get some sample data (you can skip this if you have existing data)
    print("🔍 Getting sample data for analysis...")
    brands = scraper.scrape_wikipedia_brands()[:10]  # Just get a few for demo
    
    if not brands:
        print("❌ No data available for analysis")
        return
    
    # Initialize analyzer with data
    analyzer = BrandAnalyzer()
    analyzer.brands_data = brands
    
    print(f"📊 Analyzing {len(brands)} brands...")
    
    # Generate insights
    insights = analyzer.generate_insights()
    
    # Display insights
    print("\n📈 ANALYSIS RESULTS:")
    print(f"  Total brands: {insights['total_brands']}")
    print(f"  Data sources: {len(insights['source_distribution'])}")
    print(f"  Emerging brands: {len(insights['emerging_brands'])}")
    
    # Show top keywords
    if insights['top_keywords']:
        print(f"\n🔤 Top keywords:")
        for word, freq in insights['top_keywords'][:5]:
            print(f"   - {word}: {freq} mentions")
    
    # Show source distribution
    print(f"\n📡 Source distribution:")
    for source, count in insights['source_distribution'].items():
        print(f"   - {source}: {count} brands")
    
    # Export analysis
    filename = analyzer.export_analysis()
    print(f"\n💾 Analysis exported to: {filename}")
    
    return insights

def example_custom_categories():
    """Example 5: Custom category analysis"""
    print("\n" + "="*60)
    print("EXAMPLE 5: CUSTOM CATEGORY ANALYSIS")
    print("="*60)
    
    # Create some sample brand data
    sample_brands = [
        {
            'name': 'Gojek',
            'summary': 'Indonesian ride-hailing and super app platform',
            'source': 'Manual',
            'category': 'Transportation',
            'scraped_at': datetime.now().isoformat()
        },
        {
            'name': 'Tokopedia',
            'summary': 'Leading Indonesian e-commerce marketplace',
            'source': 'Manual',
            'category': 'E-commerce',
            'scraped_at': datetime.now().isoformat()
        },
        {
            'name': 'Ruangguru',
            'summary': 'Indonesian online learning platform for education',
            'source': 'Manual',
            'category': 'Education',
            'scraped_at': datetime.now().isoformat()
        }
    ]
    
    # Analyze categories
    analyzer = BrandAnalyzer()
    analyzer.brands_data = sample_brands
    
    print("🏷️  Categorizing brands...")
    categories = analyzer.categorize_brands()
    
    print("\n📊 Brand categorization results:")
    for brand_name, brand_categories in categories.items():
        print(f"   - {brand_name}: {', '.join(brand_categories)}")
    
    # Find emerging brands
    print("\n🚀 Looking for emerging brands...")
    emerging = analyzer.find_emerging_brands()
    
    if emerging:
        print("🌟 Emerging brands found:")
        for brand in emerging:
            print(f"   - {brand['name']} (Score: {brand.get('emerging_score', 0)})")
    else:
        print("   No emerging brands detected in sample data")
    
    return categories

def example_export_formats():
    """Example 6: Different export formats"""
    print("\n" + "="*60)
    print("EXAMPLE 6: EXPORT FORMATS")
    print("="*60)
    
    # Create sample data
    scraper = IndonesianBrandScraper()
    
    # Get some real data (limited for demo)
    print("🔍 Getting data for export demo...")
    brands = scraper.scrape_wikipedia_brands()[:5]
    
    if not brands:
        print("❌ No data available for export demo")
        return
    
    scraper.brands_data = brands
    
    # Export in different formats
    print("💾 Exporting in different formats...")
    
    formats = ['json', 'csv', 'excel']
    exported_files = []
    
    for format_type in formats:
        try:
            scraper.save_data(format_type)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraped_data/indonesian_brands_{timestamp}.{format_type}"
            exported_files.append(filename)
            print(f"   ✅ Exported to {format_type.upper()} format")
        except Exception as e:
            print(f"   ❌ Failed to export to {format_type}: {e}")
    
    print(f"\n📁 Files exported to scraped_data/ directory")
    return exported_files

def main():
    """Run all examples"""
    print("🇮🇩 INDONESIAN BRAND SCRAPER - EXAMPLE USAGE")
    print("="*60)
    print("This script demonstrates various ways to use the scraper")
    print("="*60)
    
    try:
        # Run examples
        example_basic_scraping()
        time.sleep(2)
        
        example_wikipedia_only()
        time.sleep(2)
        
        example_targeted_search()
        time.sleep(2)
        
        example_data_analysis()
        time.sleep(2)
        
        example_custom_categories()
        time.sleep(2)
        
        example_export_formats()
        
        print("\n" + "="*60)
        print("🎉 ALL EXAMPLES COMPLETED!")
        print("="*60)
        print("Check the 'scraped_data' directory for output files")
        print("For more advanced usage, see the README.md file")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("Make sure you have run 'python setup.py' first")

if __name__ == "__main__":
    main()