"""
Indonesian Brand Analyzer
Analyzes and processes scraped brand data to provide insights
"""

import pandas as pd
import json
import re
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from datetime import datetime
from typing import List, Dict, Tuple
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import logging

class BrandAnalyzer:
    """
    Analyzes scraped Indonesian brand data
    """
    
    def __init__(self, data_file: str = None):
        self.brands_data = []
        self.df = None
        self.setup_logging()
        
        if data_file:
            self.load_data(data_file)
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def load_data(self, file_path: str):
        """Load brand data from file"""
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.brands_data = json.load(f)
            elif file_path.endswith('.csv'):
                self.df = pd.read_csv(file_path)
                self.brands_data = self.df.to_dict('records')
            elif file_path.endswith('.xlsx'):
                self.df = pd.read_excel(file_path)
                self.brands_data = self.df.to_dict('records')
            
            self.df = pd.DataFrame(self.brands_data)
            self.logger.info(f"Loaded {len(self.brands_data)} brands from {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to load data from {file_path}: {e}")
    
    def categorize_brands(self) -> Dict[str, List[str]]:
        """Categorize brands based on keywords in their names and descriptions"""
        categories = {
            'E-commerce': ['tokopedia', 'shopee', 'bukalapak', 'blibli', 'lazada'],
            'Fintech': ['gopay', 'ovo', 'dana', 'jenius', 'akulaku', 'kredivo'],
            'Transportation': ['gojek', 'grab', 'uber', 'blue bird', 'traveloka'],
            'Food & Beverage': ['indomie', 'abc', 'sarimi', 'chitato', 'teh botol'],
            'Fashion': ['uniqlo', 'zara', 'h&m', 'cotton on', 'mango'],
            'Technology': ['telkom', 'indosat', 'xl', 'smartfren', 'biznet'],
            'Media': ['kompas', 'detik', 'liputan6', 'tempo', 'cnbc'],
            'Gaming': ['moonton', 'tencent', 'garena', 'mobile legends'],
            'Healthcare': ['halodoc', 'alodokter', 'good doctor', 'kimia farma'],
            'Education': ['ruangguru', 'zenius', 'quipper', 'skill academy']
        }
        
        brand_categories = {}
        
        for brand in self.brands_data:
            brand_name = brand.get('name', '').lower()
            brand_summary = brand.get('summary', '').lower()
            brand_text = f"{brand_name} {brand_summary}"
            
            assigned_categories = []
            
            for category, keywords in categories.items():
                for keyword in keywords:
                    if keyword in brand_text:
                        assigned_categories.append(category)
                        break
            
            # If no specific category found, try to infer from general keywords
            if not assigned_categories:
                if any(word in brand_text for word in ['teknologi', 'software', 'aplikasi', 'digital']):
                    assigned_categories.append('Technology')
                elif any(word in brand_text for word in ['makanan', 'minuman', 'kuliner', 'restaurant']):
                    assigned_categories.append('Food & Beverage')
                elif any(word in brand_text for word in ['fashion', 'pakaian', 'busana', 'clothing']):
                    assigned_categories.append('Fashion')
                else:
                    assigned_categories.append('Other')
            
            brand_categories[brand.get('name', 'Unknown')] = assigned_categories
        
        return brand_categories
    
    def extract_keywords(self, text_field: str = 'summary') -> List[Tuple[str, int]]:
        """Extract most common keywords from brand descriptions"""
        try:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            
            # Get Indonesian and English stopwords
            stop_words_id = set(stopwords.words('indonesian'))
            stop_words_en = set(stopwords.words('english'))
            stop_words = stop_words_id.union(stop_words_en)
            
            # Add custom stopwords
            custom_stopwords = {'brand', 'indonesia', 'indonesian', 'merek', 'produk', 'perusahaan', 'company'}
            stop_words = stop_words.union(custom_stopwords)
            
        except:
            # Fallback if NLTK is not available
            stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 
                         'dari', 'dan', 'atau', 'yang', 'di', 'ke', 'untuk', 'dengan', 'oleh',
                         'brand', 'indonesia', 'indonesian', 'merek', 'produk', 'perusahaan', 'company'}
        
        all_text = ""
        for brand in self.brands_data:
            text = brand.get(text_field, '')
            if text:
                all_text += " " + text.lower()
        
        # Simple tokenization if NLTK is not available
        try:
            words = word_tokenize(all_text.lower())
        except:
            words = re.findall(r'\b[a-zA-Z]+\b', all_text.lower())
        
        # Filter words
        filtered_words = [word for word in words if len(word) > 3 and word not in stop_words]
        
        # Count word frequency
        word_freq = Counter(filtered_words)
        
        return word_freq.most_common(20)
    
    def analyze_sources(self) -> Dict[str, int]:
        """Analyze distribution of data sources"""
        if not self.df is not None:
            self.df = pd.DataFrame(self.brands_data)
        
        source_counts = self.df['source'].value_counts().to_dict()
        return source_counts
    
    def find_emerging_brands(self) -> List[Dict]:
        """Identify potentially emerging brands based on recent mentions"""
        emerging_brands = []
        
        for brand in self.brands_data:
            # Look for indicators of emerging brands
            summary = brand.get('summary', '').lower()
            name = brand.get('name', '').lower()
            
            emerging_indicators = [
                'startup', 'baru', 'new', 'launching', 'inovasi', 'innovation',
                'pertama', 'first', 'revolusi', 'revolution', 'breakthrough',
                'unicorn', 'decacorn', 'investasi', 'investment', 'funding'
            ]
            
            score = sum(1 for indicator in emerging_indicators if indicator in f"{name} {summary}")
            
            if score >= 2:  # Brand mentions at least 2 emerging indicators
                brand_copy = brand.copy()
                brand_copy['emerging_score'] = score
                emerging_brands.append(brand_copy)
        
        # Sort by emerging score
        emerging_brands.sort(key=lambda x: x.get('emerging_score', 0), reverse=True)
        
        return emerging_brands[:10]  # Return top 10
    
    def generate_insights(self) -> Dict:
        """Generate comprehensive insights about Indonesian brands"""
        insights = {
            'total_brands': len(self.brands_data),
            'analysis_date': datetime.now().isoformat(),
            'source_distribution': self.analyze_sources(),
            'brand_categories': self.categorize_brands(),
            'top_keywords': self.extract_keywords(),
            'emerging_brands': self.find_emerging_brands(),
            'recommendations': []
        }
        
        # Generate recommendations based on analysis
        recommendations = []
        
        if insights['total_brands'] > 0:
            recommendations.append("Data collection successful - good coverage of Indonesian brands")
        
        if len(insights['source_distribution']) > 3:
            recommendations.append("Multiple data sources used - provides comprehensive coverage")
        
        if len(insights['emerging_brands']) > 0:
            recommendations.append(f"Found {len(insights['emerging_brands'])} potentially emerging brands worth monitoring")
        
        insights['recommendations'] = recommendations
        
        return insights
    
    def create_visualizations(self):
        """Create visualizations of brand data"""
        if not self.df is not None:
            self.df = pd.DataFrame(self.brands_data)
        
        plt.style.use('default')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Source distribution
        source_counts = self.df['source'].value_counts()
        axes[0, 0].pie(source_counts.values, labels=source_counts.index, autopct='%1.1f%%')
        axes[0, 0].set_title('Data Sources Distribution')
        
        # 2. Category distribution
        categories = self.categorize_brands()
        cat_counts = Counter()
        for brand_cats in categories.values():
            for cat in brand_cats:
                cat_counts[cat] += 1
        
        axes[0, 1].bar(cat_counts.keys(), cat_counts.values())
        axes[0, 1].set_title('Brand Categories Distribution')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 3. Keywords frequency
        keywords = self.extract_keywords()
        if keywords:
            words, freqs = zip(*keywords[:10])
            axes[1, 0].barh(words, freqs)
            axes[1, 0].set_title('Top 10 Keywords')
        
        # 4. Emerging brands score
        emerging = self.find_emerging_brands()
        if emerging:
            names = [brand['name'][:20] + '...' if len(brand['name']) > 20 else brand['name'] 
                    for brand in emerging[:10]]
            scores = [brand.get('emerging_score', 0) for brand in emerging[:10]]
            axes[1, 1].bar(range(len(names)), scores)
            axes[1, 1].set_xticks(range(len(names)))
            axes[1, 1].set_xticklabels(names, rotation=45, ha='right')
            axes[1, 1].set_title('Emerging Brands Score')
        
        plt.tight_layout()
        plt.savefig(f"scraped_data/brand_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png", 
                   dpi=300, bbox_inches='tight')
        plt.show()
    
    def export_analysis(self, filename: str = None):
        """Export analysis results to JSON file"""
        if not filename:
            filename = f"scraped_data/brand_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        insights = self.generate_insights()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Analysis exported to {filename}")
        return filename

if __name__ == "__main__":
    # Example usage
    analyzer = BrandAnalyzer()
    
    # If you have a data file from the scraper
    # analyzer.load_data('scraped_data/indonesian_brands_20231201_120000.json')
    
    # Generate insights
    insights = analyzer.generate_insights()
    print(json.dumps(insights, indent=2, ensure_ascii=False))
    
    # Export analysis
    analyzer.export_analysis()