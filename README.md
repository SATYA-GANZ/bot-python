# Indonesian Brand Scraper Bot 🇮🇩

A comprehensive Python bot designed to scrape and analyze Indonesian local brands from multiple sources. This tool helps researchers, marketers, and business analysts discover and track Indonesian brands across various industries.

## 🚀 Features

- **Multi-source Scraping**: Scrapes from Wikipedia, StartupRanking, news sites, and social media
- **Intelligent Categorization**: Automatically categorizes brands by industry (E-commerce, Fintech, Food & Beverage, etc.)
- **Data Analysis**: Provides insights into brand trends, emerging companies, and market analysis
- **Multiple Output Formats**: Exports data in JSON, CSV, and Excel formats
- **Visualization**: Creates charts and graphs for data analysis
- **Command Line Interface**: Easy-to-use CLI with multiple commands
- **Asynchronous Processing**: Efficient scraping with async support
- **Rate Limiting**: Respectful scraping with built-in delays

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Chrome browser (for Selenium)
- ChromeDriver (for Selenium)

### Setup

1. **Clone or download the project files**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Install ChromeDriver** (for Selenium):
   - Download from: https://chromedriver.chromium.org/
   - Add to your PATH or place in project directory

4. **Optional: Install additional NLTK data**:
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

## 🎯 Quick Start

### Basic Scraping
```bash
# Simple scraping with default settings
python main.py scrape

# Scrape with specific output formats
python main.py scrape --output-format json csv excel

# Run complete pipeline (scrape + analyze)
python main.py full-pipeline --visualize
```

### Search for Specific Brands
```bash
# Search for Indonesian fashion brands
python main.py search --query "brand fashion indonesia" --num-results 20

# Search for Indonesian tech startups
python main.py search --query "startup teknologi indonesia" --num-results 15
```

### Data Analysis
```bash
# Analyze existing data
python main.py analyze --input-file scraped_data/indonesian_brands_20231201_120000.json --visualize --export-insights
```

## 📋 Usage Examples

### 1. Comprehensive Brand Discovery
```bash
# Discover brands across all categories with visualization
python main.py full-pipeline --output-format json csv --visualize
```

### 2. Industry-Specific Research
```bash
# Focus on specific categories
python main.py scrape --categories "Technology,E-commerce,Fintech" --max-results 50
```

### 3. Targeted Search
```bash
# Search for specific brand types
python main.py search --query "unicorn startup indonesia" --num-results 10
python main.py search --query "brand makanan lokal indonesia" --num-results 15
```

### 4. Data Analysis Only
```bash
# Analyze previously scraped data
python main.py analyze --input-file scraped_data/brands.json --visualize --export-insights
```

## 📊 Output Data Structure

The scraper generates structured data with the following fields:

```json
{
  "name": "Brand Name",
  "summary": "Brand description and details",
  "url": "Source URL",
  "source": "Data source (Wikipedia, StartupRanking, etc.)",
  "category": "Brand category (Technology, Fashion, etc.)",
  "scraped_at": "2023-12-01T12:00:00"
}
```

## 🎨 Data Sources

- **Wikipedia**: Indonesian brand categories and company pages
- **StartupRanking**: Indonesian startup database
- **News Sites**: CNBC Indonesia, Daily Social
- **Google Search**: Targeted searches for specific brand types
- **Social Media**: Brand mentions on Instagram, Twitter, LinkedIn

## 📈 Analysis Features

The analyzer provides:

- **Brand Categorization**: Automatic classification by industry
- **Emerging Brand Detection**: Identifies potentially rising brands
- **Keyword Analysis**: Most common terms in brand descriptions
- **Source Distribution**: Analysis of data source coverage
- **Trend Visualization**: Charts and graphs of brand data
- **Export Capabilities**: Detailed insights in JSON format

## 🛠️ Advanced Configuration

### Custom Search Terms
Edit `config.py` to modify search keywords:
```python
INDONESIAN_BRAND_KEYWORDS = [
    "brand indonesia",
    "startup indonesia",
    "umkm indonesia",
    # Add your custom terms
]
```

### Rate Limiting
Adjust scraping speed in `config.py`:
```python
REQUEST_DELAY = 2  # Seconds between requests
MAX_RETRIES = 3    # Number of retry attempts
```

### Categories
Modify brand categories:
```python
BRAND_CATEGORIES = [
    "Fashion",
    "Food & Beverage",
    "Technology",
    # Add your categories
]
```

## 📁 File Structure

```
indonesian-brand-scraper/
├── main.py                    # Main CLI entry point
├── indonesian_brand_scraper.py # Core scraping functionality
├── brand_analyzer.py          # Data analysis module
├── config.py                  # Configuration settings
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── scraped_data/             # Output directory
    ├── indonesian_brands_*.json
    ├── indonesian_brands_*.csv
    ├── indonesian_brands_*.xlsx
    ├── brand_analysis_*.json
    └── brand_analysis_*.png
```

## 🤖 API Usage

You can also use the scraper programmatically:

```python
from indonesian_brand_scraper import IndonesianBrandScraper
from brand_analyzer import BrandAnalyzer

# Initialize scraper
scraper = IndonesianBrandScraper()

# Run scraping
brands = scraper.run_comprehensive_scrape()

# Save data
scraper.save_data('json')
scraper.save_data('csv')

# Analyze data
analyzer = BrandAnalyzer()
analyzer.brands_data = brands
insights = analyzer.generate_insights()

# Print results
scraper.print_summary()
print(f"Found {len(brands)} Indonesian brands")
```

## ⚙️ Troubleshooting

### Common Issues

1. **ChromeDriver not found**:
   - Install ChromeDriver and add to PATH
   - Or place chromedriver executable in project directory

2. **Rate limiting errors**:
   - Increase `REQUEST_DELAY` in config.py
   - Reduce the number of concurrent requests

3. **No data found**:
   - Check internet connection
   - Verify target websites are accessible
   - Try different search terms

4. **NLTK errors**:
   - Run: `python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"`

### Performance Tips

- Use `--max-results` to limit scraping for testing
- Run scraping during off-peak hours
- Use specific categories instead of comprehensive scraping
- Save data in multiple formats for backup

## 🔍 Search Categories

The bot can find brands in these categories:

- **E-commerce**: Tokopedia, Shopee, Bukalapak, etc.
- **Fintech**: GoPay, OVO, Dana, Jenius, etc.
- **Transportation**: Gojek, Grab, Traveloka, etc.
- **Food & Beverage**: Indomie, local restaurant chains, etc.
- **Fashion**: Local clothing brands, accessories, etc.
- **Technology**: Software companies, startups, etc.
- **Media**: News outlets, content platforms, etc.
- **Gaming**: Indonesian game developers, etc.
- **Healthcare**: Health tech, medical companies, etc.
- **Education**: EdTech platforms, online learning, etc.

## 🌟 Example Use Cases

1. **Market Research**: Discover competitors in specific industries
2. **Investment Analysis**: Find emerging startups and growth companies
3. **Partnership Opportunities**: Identify potential business partners
4. **Academic Research**: Study Indonesian business ecosystem
5. **Journalism**: Research for articles about Indonesian business
6. **Business Development**: Find suppliers or distributors

## 📝 License

This project is open source. Please use responsibly and respect website terms of service.

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional data sources
- Better categorization algorithms
- Enhanced analysis features
- UI improvements
- API integrations

## ⚠️ Ethical Usage

Please use this tool responsibly:

- Respect website robots.txt files
- Don't overload servers with requests
- Use data for legitimate research purposes
- Follow applicable laws and regulations
- Give credit to data sources

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section
2. Review the configuration files
3. Test with smaller datasets first
4. Check internet connectivity and permissions

---

**Happy scraping! 🚀** Discover the vibrant Indonesian brand ecosystem with this powerful tool.