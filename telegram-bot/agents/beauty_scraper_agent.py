"""
Beauty Scraper Agent - AI-powered scraping of Indonesian beauty brands
"""

import os
import asyncio
import logging
import re
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_community.tools import DuckDuckGoSearchRun

logger = logging.getLogger(__name__)

class BeautyScrapeAgent:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.ua = UserAgent()
        self.setup_llm()
        self.setup_tools()
        self.setup_agent()
    
    def setup_llm(self):
        """Initialize the language model"""
        self.llm = OpenAI(
            api_key=self.openai_api_key,
            temperature=0.7,
            max_tokens=2000
        )
    
    def setup_tools(self):
        """Setup tools for the agent"""
        self.search_tool = DuckDuckGoSearchRun()
        
        self.tools = [
            Tool(
                name="web_search",
                description="Search the web for Indonesian beauty brands and UMKM companies",
                func=self.search_tool.run
            ),
            Tool(
                name="scrape_website",
                description="Scrape a website to extract beauty brand information",
                func=self.scrape_website
            ),
            Tool(
                name="extract_contacts",
                description="Extract contact information from scraped content",
                func=self.extract_contacts_from_text
            )
        ]
    
    def setup_agent(self):
        """Setup the AI agent"""
        template = """
        You are an expert AI agent specialized in finding Indonesian beauty brands, particularly UMKM (micro, small, and medium enterprises).
        
        Your task is to:
        1. Search for Indonesian beauty brands and cosmetics companies
        2. Focus on small to medium businesses (UMKM)
        3. Extract company information including:
           - Company name
           - Website URL
           - Product categories
           - Contact information (phone, email, WhatsApp)
           - Business size (small/medium/large)
           - Location
        
        Available tools: {tools}
        Tool names: {tool_names}
        
        Use the following format:
        
        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question
        
        Question: {input}
        {agent_scratchpad}
        """
        
        self.prompt = PromptTemplate.from_template(template)
        self.agent = create_react_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)
    
    async def scrape_beauty_brands(self, category: str = "all", max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Main method to scrape beauty brands
        
        Args:
            category: "small", "medium", or "all"
            max_results: Maximum number of results to return
        """
        logger.info(f"Starting beauty brand scraping for category: {category}")
        
        # Build search queries based on category
        search_queries = self._build_search_queries(category)
        
        all_brands = []
        
        for query in search_queries:
            try:
                logger.info(f"Processing query: {query}")
                
                # Use AI agent to search and process
                result = await self._process_search_query(query)
                
                if result:
                    all_brands.extend(result)
                
                # Respect rate limits
                await asyncio.sleep(2)
                
                if len(all_brands) >= max_results:
                    break
                    
            except Exception as e:
                logger.error(f"Error processing query '{query}': {e}")
                continue
        
        # Deduplicate and clean results
        cleaned_brands = self._clean_and_deduplicate(all_brands)
        
        return cleaned_brands[:max_results]
    
    def _build_search_queries(self, category: str) -> List[str]:
        """Build search queries based on category"""
        base_queries = [
            "brand kecantikan Indonesia UMKM",
            "produk kosmetik Indonesia small business",
            "skincare lokal Indonesia brand",
            "makeup brand Indonesia UMKM",
            "kosmetik halal Indonesia",
            "perawatan wajah Indonesia brand",
            "beauty brand Indonesia online shop",
            "produk kecantikan lokal Indonesia"
        ]
        
        if category == "small":
            additional_queries = [
                "UMKM kosmetik Indonesia",
                "usaha kecil produk kecantikan",
                "home industry kosmetik Indonesia",
                "startup beauty Indonesia"
            ]
        elif category == "medium":
            additional_queries = [
                "perusahaan kosmetik menengah Indonesia",
                "brand kecantikan established Indonesia",
                "distributor kosmetik Indonesia",
                "pabrik kosmetik Indonesia"
            ]
        else:  # all
            additional_queries = base_queries + [
                "UMKM kosmetik Indonesia",
                "perusahaan kosmetik Indonesia",
                "industri kecantikan Indonesia",
                "brand beauty Indonesia"
            ]
        
        return base_queries + additional_queries
    
    async def _process_search_query(self, query: str) -> List[Dict[str, Any]]:
        """Process a single search query using AI agent"""
        try:
            agent_input = f"""
            Search for Indonesian beauty brands using this query: "{query}"
            
            Focus on finding:
            1. Company websites and online presence
            2. Contact information (especially WhatsApp numbers)
            3. Product categories and business size
            4. Location and business details
            
            Return structured information about each brand found.
            """
            
            result = self.agent_executor.run(agent_input)
            
            # Parse the agent's response into structured data
            brands = self._parse_agent_response(result)
            
            return brands
            
        except Exception as e:
            logger.error(f"Error in agent processing: {e}")
            return []
    
    def scrape_website(self, url: str) -> str:
        """Scrape a website for beauty brand information"""
        try:
            # Setup headers
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract relevant information
            info = {
                'title': soup.title.string if soup.title else '',
                'description': '',
                'contact_info': [],
                'social_media': [],
                'products': []
            }
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                info['description'] = meta_desc.get('content', '')
            
            # Extract contact information
            text_content = soup.get_text()
            info['contact_info'] = self.extract_contacts_from_text(text_content)
            
            # Extract social media links
            social_patterns = {
                'instagram': r'instagram\.com/[\w\.]+',
                'facebook': r'facebook\.com/[\w\.]+',
                'whatsapp': r'wa\.me/[\d]+',
                'telegram': r't\.me/[\w]+',
                'tiktok': r'tiktok\.com/@[\w\.]+',
                'youtube': r'youtube\.com/[\w]+',
            }
            
            for platform, pattern in social_patterns.items():
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    info['social_media'].extend([f"{platform}: {match}" for match in matches])
            
            return str(info)
            
        except Exception as e:
            logger.error(f"Error scraping website {url}: {e}")
            return f"Error scraping {url}: {str(e)}"
    
    def extract_contacts_from_text(self, text: str) -> List[str]:
        """Extract contact information from text"""
        contacts = []
        
        # Phone number patterns (Indonesian)
        phone_patterns = [
            r'\+62\s?[\d\s\-]{9,13}',  # +62 format
            r'08[\d\s\-]{8,12}',        # 08 format
            r'62[\d\s\-]{9,13}',        # 62 format
        ]
        
        # Email patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        # WhatsApp patterns
        whatsapp_patterns = [
            r'wa\.me/[\d]+',
            r'whatsapp.*?(\+?62[\d\s\-]{9,13})',
            r'WA.*?(\+?62[\d\s\-]{9,13})',
        ]
        
        # Extract phone numbers
        for pattern in phone_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            contacts.extend([f"Phone: {match.strip()}" for match in matches])
        
        # Extract emails
        email_matches = re.findall(email_pattern, text)
        contacts.extend([f"Email: {match}" for match in email_matches])
        
        # Extract WhatsApp
        for pattern in whatsapp_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            contacts.extend([f"WhatsApp: {match}" for match in matches])
        
        return list(set(contacts))  # Remove duplicates
    
    def _parse_agent_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse the AI agent's response into structured data"""
        brands = []
        
        try:
            # This is a simplified parser - in production, you'd want more sophisticated parsing
            lines = response.split('\n')
            current_brand = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    if current_brand:
                        brands.append(current_brand)
                        current_brand = {}
                    continue
                
                # Parse different types of information
                if 'name:' in line.lower() or 'brand:' in line.lower():
                    current_brand['name'] = line.split(':', 1)[1].strip()
                elif 'website:' in line.lower() or 'url:' in line.lower():
                    current_brand['website'] = line.split(':', 1)[1].strip()
                elif 'phone:' in line.lower() or 'whatsapp:' in line.lower():
                    if 'contacts' not in current_brand:
                        current_brand['contacts'] = []
                    current_brand['contacts'].append(line)
                elif 'email:' in line.lower():
                    if 'contacts' not in current_brand:
                        current_brand['contacts'] = []
                    current_brand['contacts'].append(line)
                elif 'category:' in line.lower() or 'product:' in line.lower():
                    current_brand['category'] = line.split(':', 1)[1].strip()
                elif 'location:' in line.lower() or 'address:' in line.lower():
                    current_brand['location'] = line.split(':', 1)[1].strip()
            
            # Add last brand if exists
            if current_brand:
                brands.append(current_brand)
        
        except Exception as e:
            logger.error(f"Error parsing agent response: {e}")
        
        return brands
    
    def _clean_and_deduplicate(self, brands: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and deduplicate brand data"""
        seen = set()
        cleaned = []
        
        for brand in brands:
            # Create a unique identifier
            identifier = brand.get('name', '') + brand.get('website', '')
            
            if identifier and identifier not in seen:
                seen.add(identifier)
                
                # Clean and standardize the brand data
                cleaned_brand = {
                    'name': brand.get('name', 'Unknown'),
                    'website': brand.get('website', ''),
                    'category': brand.get('category', 'Beauty/Cosmetics'),
                    'location': brand.get('location', 'Indonesia'),
                    'contacts': brand.get('contacts', []),
                    'business_type': self._determine_business_type(brand),
                    'scraped_at': asyncio.get_event_loop().time()
                }
                
                cleaned.append(cleaned_brand)
        
        return cleaned
    
    def _determine_business_type(self, brand: Dict[str, Any]) -> str:
        """Determine if the business is small, medium, or large"""
        # Simple heuristic based on available information
        name = brand.get('name', '').lower()
        website = brand.get('website', '').lower()
        
        # Keywords that suggest different business sizes
        small_indicators = ['umkm', 'home', 'handmade', 'artisan', 'lokal', 'rumahan']
        medium_indicators = ['indonesia', 'jakarta', 'surabaya', 'bandung', 'enterprise']
        large_indicators = ['group', 'corporation', 'tbk', 'pt.', 'multinational']
        
        text_to_check = name + ' ' + website
        
        if any(indicator in text_to_check for indicator in large_indicators):
            return 'Large'
        elif any(indicator in text_to_check for indicator in medium_indicators):
            return 'Medium'
        elif any(indicator in text_to_check for indicator in small_indicators):
            return 'Small'
        else:
            return 'Unknown'