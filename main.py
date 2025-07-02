#!/usr/bin/env python3
"""
Indonesian Brand Scraper Bot - Main Entry Point
A comprehensive tool to scrape and analyze Indonesian local brands
"""

import argparse
import sys
import os
import json
from datetime import datetime

from indonesian_brand_scraper import IndonesianBrandScraper
from brand_analyzer import BrandAnalyzer

def main():
    parser = argparse.ArgumentParser(
        description='Indonesian Brand Scraper Bot - Find and analyze Indonesian local brands',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py scrape --output-format json csv
  python main.py analyze --input-file scraped_data/brands.json
  python main.py scrape --categories "Fashion,Food & Beverage" --max-results 50
  python main.py full-pipeline --visualize
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape Indonesian brands')
    scrape_parser.add_argument('--output-format', nargs='+', choices=['json', 'csv', 'excel'], 
                              default=['json'], help='Output format(s)')
    scrape_parser.add_argument('--categories', type=str, 
                              help='Comma-separated list of categories to focus on')
    scrape_parser.add_argument('--max-results', type=int, default=100,
                              help='Maximum number of results to scrape')
    scrape_parser.add_argument('--sources', nargs='+', 
                              choices=['wikipedia', 'startup_ranking', 'news', 'social_media', 'google'],
                              default=['wikipedia', 'startup_ranking', 'news'],
                              help='Data sources to use')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze scraped brand data')
    analyze_parser.add_argument('--input-file', required=True,
                               help='Input file with scraped brand data')
    analyze_parser.add_argument('--visualize', action='store_true',
                               help='Create visualizations')
    analyze_parser.add_argument('--export-insights', action='store_true',
                               help='Export analysis insights to file')
    
    # Full pipeline command
    pipeline_parser = subparsers.add_parser('full-pipeline', help='Run complete scraping and analysis pipeline')
    pipeline_parser.add_argument('--output-format', nargs='+', choices=['json', 'csv', 'excel'], 
                                default=['json', 'csv'], help='Output format(s)')
    pipeline_parser.add_argument('--visualize', action='store_true',
                                help='Create visualizations')
    pipeline_parser.add_argument('--max-results', type=int, default=100,
                                help='Maximum number of results to scrape')
    
    # Search command for specific brands
    search_parser = subparsers.add_parser('search', help='Search for specific Indonesian brands')
    search_parser.add_argument('--query', required=True,
                              help='Search query for brands')
    search_parser.add_argument('--num-results', type=int, default=10,
                              help='Number of search results')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'scrape':
            run_scrape(args)
        elif args.command == 'analyze':
            run_analyze(args)
        elif args.command == 'full-pipeline':
            run_full_pipeline(args)
        elif args.command == 'search':
            run_search(args)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def run_scrape(args):
    """Run the scraping process"""
    print("🚀 Starting Indonesian Brand Scraper...")
    print(f"📊 Output formats: {', '.join(args.output_format)}")
    print(f"🎯 Max results: {args.max_results}")
    print(f"📡 Sources: {', '.join(args.sources)}")
    
    scraper = IndonesianBrandScraper()
    
    # Override max results if specified
    if hasattr(args, 'max_results'):
        # This would require modifying the scraper to accept max_results
        pass
    
    # Run scraping
    brands = scraper.run_comprehensive_scrape()
    
    # Save in requested formats
    for format_type in args.output_format:
        scraper.save_data(format_type)
    
    # Print summary
    scraper.print_summary()
    
    print(f"\n✅ Scraping completed! Found {len(brands)} brands")
    print(f"📁 Data saved in: {scraper.OUTPUT_DIRECTORY if hasattr(scraper, 'OUTPUT_DIRECTORY') else 'scraped_data'}")

def run_analyze(args):
    """Run the analysis process"""
    print(f"🔍 Analyzing brand data from: {args.input_file}")
    
    if not os.path.exists(args.input_file):
        print(f"❌ Error: File {args.input_file} not found")
        sys.exit(1)
    
    analyzer = BrandAnalyzer(args.input_file)
    
    # Generate insights
    insights = analyzer.generate_insights()
    
    print("\n📈 ANALYSIS RESULTS")
    print("=" * 50)
    print(f"Total brands analyzed: {insights['total_brands']}")
    print(f"Data sources: {len(insights['source_distribution'])}")
    print(f"Emerging brands found: {len(insights['emerging_brands'])}")
    
    # Print top categories
    categories = insights['brand_categories']
    if categories:
        print(f"\n🏷️  Top brand categories:")
        category_counts = {}
        for brand_cats in categories.values():
            for cat in brand_cats:
                category_counts[cat] = category_counts.get(cat, 0) + 1
        
        for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   - {cat}: {count} brands")
    
    # Print top keywords
    if insights['top_keywords']:
        print(f"\n🔤 Top keywords:")
        for word, freq in insights['top_keywords'][:5]:
            print(f"   - {word}: {freq} mentions")
    
    # Export insights if requested
    if args.export_insights:
        filename = analyzer.export_analysis()
        print(f"\n💾 Insights exported to: {filename}")
    
    # Create visualizations if requested
    if args.visualize:
        print("\n📊 Creating visualizations...")
        try:
            analyzer.create_visualizations()
            print("✅ Visualizations created successfully!")
        except Exception as e:
            print(f"⚠️  Could not create visualizations: {e}")

def run_full_pipeline(args):
    """Run the complete pipeline: scrape + analyze"""
    print("🔄 Running full pipeline: Scrape → Analyze")
    
    # Step 1: Scrape
    print("\n" + "="*50)
    print("STEP 1: SCRAPING")
    print("="*50)
    
    scraper = IndonesianBrandScraper()
    brands = scraper.run_comprehensive_scrape()
    
    # Save data
    json_file = None
    for format_type in args.output_format:
        scraper.save_data(format_type)
        if format_type == 'json':
            # Get the latest JSON file for analysis
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_file = f"scraped_data/indonesian_brands_{timestamp}.json"
    
    scraper.print_summary()
    
    # Step 2: Analyze
    if json_file and brands:
        print("\n" + "="*50)
        print("STEP 2: ANALYSIS")
        print("="*50)
        
        # Wait a moment for file to be written
        import time
        time.sleep(1)
        
        # Find the most recent JSON file if timestamp doesn't match exactly
        import glob
        json_files = glob.glob("scraped_data/indonesian_brands_*.json")
        if json_files:
            json_file = max(json_files, key=os.path.getctime)
        
        try:
            analyzer = BrandAnalyzer(json_file)
            insights = analyzer.generate_insights()
            
            print(f"📊 Analysis completed for {insights['total_brands']} brands")
            
            # Export insights
            analyzer.export_analysis()
            
            # Create visualizations if requested
            if args.visualize:
                print("📈 Creating visualizations...")
                try:
                    analyzer.create_visualizations()
                    print("✅ Visualizations created!")
                except Exception as e:
                    print(f"⚠️  Could not create visualizations: {e}")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
    
    print(f"\n🎉 Pipeline completed! Check the 'scraped_data' directory for results.")

def run_search(args):
    """Run a specific search for brands"""
    print(f"🔍 Searching for: {args.query}")
    
    scraper = IndonesianBrandScraper()
    
    # Use Google search functionality
    urls = scraper.search_google_for_brands(args.query, args.num_results)
    
    print(f"\n📋 Found {len(urls)} results:")
    for i, url in enumerate(urls, 1):
        print(f"{i:2}. {url}")
    
    # Save results
    search_results = {
        'query': args.query,
        'timestamp': datetime.now().isoformat(),
        'results': urls
    }
    
    filename = f"scraped_data/search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs('scraped_data', exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(search_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {filename}")

if __name__ == "__main__":
    main()