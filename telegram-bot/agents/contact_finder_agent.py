"""
Contact Finder Agent - AI-powered contact information extraction
"""

import os
import re
import asyncio
import logging
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
import phonenumbers
from phonenumbers import NumberParseException
from email_validator import validate_email, EmailNotValidError

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_community.tools import DuckDuckGoSearchRun
from serpapi import GoogleSearch

logger = logging.getLogger(__name__)

class ContactFinderAgent:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.serpapi_key = os.getenv('SERPAPI_KEY')
        self.setup_llm()
        self.setup_tools()
        self.setup_agent()
    
    def setup_llm(self):
        """Initialize the language model"""
        self.llm = OpenAI(
            api_key=self.openai_api_key,
            temperature=0.3,  # Lower temperature for more factual responses
            max_tokens=1500
        )
    
    def setup_tools(self):
        """Setup tools for the agent"""
        self.search_tool = DuckDuckGoSearchRun()
        
        self.tools = [
            Tool(
                name="google_search",
                description="Search Google for contact information of companies",
                func=self.google_search
            ),
            Tool(
                name="duckduckgo_search",
                description="Search DuckDuckGo for company information",
                func=self.search_tool.run
            ),
            Tool(
                name="extract_contacts_from_url",
                description="Extract contact information from a specific URL",
                func=self.extract_contacts_from_url
            ),
            Tool(
                name="validate_contact",
                description="Validate phone numbers and email addresses",
                func=self.validate_contact_info
            )
        ]
    
    def setup_agent(self):
        """Setup the AI agent"""
        template = """
        You are an expert contact information researcher specializing in finding accurate WhatsApp numbers and email addresses for Indonesian beauty brands and UMKM companies.
        
        Your task is to:
        1. Search comprehensively for contact information
        2. Extract phone numbers (especially WhatsApp-enabled numbers)
        3. Find official email addresses
        4. Verify the accuracy of contact information
        5. Look for social media presence and alternative contact methods
        
        Search strategies:
        - Look for official websites first
        - Check social media profiles (Instagram, Facebook, TikTok)
        - Search for "kontak", "hubungi", "contact us" pages
        - Look for WhatsApp links (wa.me/)
        - Check business directories and marketplaces
        
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
    
    async def find_contacts(self, query: str) -> List[Dict[str, Any]]:
        """
        Main method to find contact information
        
        Args:
            query: Brand name, website URL, or company name
        """
        logger.info(f"Starting contact search for: {query}")
        
        try:
            # Use AI agent to search comprehensively
            agent_input = f"""
            Find comprehensive contact information for: "{query}"
            
            This could be a brand name, website URL, or company name, particularly focusing on Indonesian beauty brands or UMKM companies.
            
            Search for:
            1. WhatsApp numbers (prioritize these)
            2. Official email addresses
            3. Phone numbers
            4. Social media contacts
            5. Business location/address
            6. Website and online presence
            
            Be thorough and check multiple sources. Validate all contact information found.
            """
            
            result = self.agent_executor.run(agent_input)
            
            # Parse and structure the results
            contacts = self._parse_contact_results(result, query)
            
            return contacts
            
        except Exception as e:
            logger.error(f"Error in contact search: {e}")
            return []
    
    def google_search(self, query: str) -> str:
        """Search Google using SerpAPI"""
        try:
            if not self.serpapi_key:
                return "SerpAPI key not configured, using DuckDuckGo instead"
            
            search = GoogleSearch({
                "q": query,
                "api_key": self.serpapi_key,
                "num": 10,
                "hl": "id",  # Indonesian language
                "gl": "id"   # Indonesia location
            })
            
            results = search.get_dict()
            
            if "organic_results" in results:
                search_results = []
                for result in results["organic_results"][:5]:
                    search_results.append(f"Title: {result.get('title', '')}")
                    search_results.append(f"URL: {result.get('link', '')}")
                    search_results.append(f"Snippet: {result.get('snippet', '')}")
                    search_results.append("---")
                
                return "\n".join(search_results)
            else:
                return "No results found"
                
        except Exception as e:
            logger.error(f"Error in Google search: {e}")
            return f"Search error: {str(e)}"
    
    def extract_contacts_from_url(self, url: str) -> str:
        """Extract contact information from a specific URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text()
            
            # Extract various types of contact information
            contacts = self._extract_all_contacts(text_content, url)
            
            # Also check for contact pages
            contact_links = self._find_contact_pages(soup, url)
            
            result = {
                'url': url,
                'contacts': contacts,
                'contact_pages': contact_links,
                'title': soup.title.string if soup.title else ''
            }
            
            return str(result)
            
        except Exception as e:
            logger.error(f"Error extracting from URL {url}: {e}")
            return f"Error extracting from {url}: {str(e)}"
    
    def validate_contact_info(self, contact_info: str) -> str:
        """Validate phone numbers and email addresses"""
        try:
            results = {
                'valid_phones': [],
                'valid_emails': [],
                'valid_whatsapp': [],
                'invalid_contacts': []
            }
            
            lines = contact_info.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if it's a phone number
                if any(char.isdigit() for char in line):
                    validated_phone = self._validate_phone_number(line)
                    if validated_phone:
                        results['valid_phones'].append(validated_phone)
                        # Check if it's WhatsApp-enabled (Indonesian numbers)
                        if validated_phone.startswith('+62'):
                            results['valid_whatsapp'].append(validated_phone)
                    else:
                        results['invalid_contacts'].append(f"Invalid phone: {line}")
                
                # Check if it's an email
                elif '@' in line:
                    validated_email = self._validate_email_address(line)
                    if validated_email:
                        results['valid_emails'].append(validated_email)
                    else:
                        results['invalid_contacts'].append(f"Invalid email: {line}")
            
            return str(results)
            
        except Exception as e:
            logger.error(f"Error in validation: {e}")
            return f"Validation error: {str(e)}"
    
    def _extract_all_contacts(self, text: str, source_url: str = "") -> List[Dict[str, str]]:
        """Extract all types of contact information from text"""
        contacts = []
        
        # Indonesian phone number patterns
        phone_patterns = [
            r'\+62\s?8\d{8,11}',           # +62 8xxx format
            r'\+62\s?\d{2,3}\s?\d{7,8}',   # +62 area code format
            r'08\d{8,11}',                 # 08xxx format
            r'62\s?8\d{8,11}',             # 62 8xxx format
            r'\b\d{4}[-.\s]?\d{4}[-.\s]?\d{3,4}\b',  # Various formatted numbers
        ]
        
        # Email patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        # WhatsApp specific patterns
        whatsapp_patterns = [
            r'wa\.me/(\d+)',
            r'whatsapp.*?((?:\+62|62|08)\d{8,12})',
            r'WA.*?((?:\+62|62|08)\d{8,12})',
            r'hubungi.*?((?:\+62|62|08)\d{8,12})',
        ]
        
        # Social media patterns
        social_patterns = {
            'instagram': r'instagram\.com/([a-zA-Z0-9._]+)',
            'facebook': r'facebook\.com/([a-zA-Z0-9.]+)',
            'tiktok': r'tiktok\.com/@([a-zA-Z0-9._]+)',
            'youtube': r'youtube\.com/([a-zA-Z0-9]+)',
            'telegram': r't\.me/([a-zA-Z0-9_]+)',
        }
        
        # Extract phone numbers
        for pattern in phone_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                cleaned_phone = self._clean_phone_number(match)
                if cleaned_phone:
                    contacts.append({
                        'type': 'phone',
                        'value': cleaned_phone,
                        'source': source_url,
                        'raw': match
                    })
        
        # Extract emails
        email_matches = re.findall(email_pattern, text)
        for email in email_matches:
            if self._validate_email_address(email):
                contacts.append({
                    'type': 'email',
                    'value': email.lower(),
                    'source': source_url,
                    'raw': email
                })
        
        # Extract WhatsApp numbers
        for pattern in whatsapp_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    phone_num = match[1] if len(match) > 1 else match[0]
                else:
                    phone_num = match
                
                cleaned_phone = self._clean_phone_number(phone_num)
                if cleaned_phone:
                    contacts.append({
                        'type': 'whatsapp',
                        'value': cleaned_phone,
                        'source': source_url,
                        'raw': match
                    })
        
        # Extract social media
        for platform, pattern in social_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                contacts.append({
                    'type': f'social_{platform}',
                    'value': f"{platform}.com/{match}",
                    'source': source_url,
                    'raw': match
                })
        
        return contacts
    
    def _find_contact_pages(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Find potential contact pages"""
        contact_keywords = [
            'kontak', 'contact', 'hubungi', 'tentang', 'about',
            'alamat', 'address', 'telepon', 'phone', 'email'
        ]
        
        contact_links = []
        
        # Find links that might lead to contact pages
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text().lower().strip()
            
            if any(keyword in text for keyword in contact_keywords):
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    full_url = base_url.rstrip('/') + href
                elif href.startswith('http'):
                    full_url = href
                else:
                    continue
                
                contact_links.append(full_url)
        
        return list(set(contact_links))  # Remove duplicates
    
    def _clean_phone_number(self, phone: str) -> Optional[str]:
        """Clean and standardize phone number"""
        try:
            # Remove all non-digit characters except +
            cleaned = re.sub(r'[^\d+]', '', phone)
            
            # Handle Indonesian number formats
            if cleaned.startswith('08'):
                cleaned = '+62' + cleaned[1:]
            elif cleaned.startswith('62') and not cleaned.startswith('+62'):
                cleaned = '+' + cleaned
            elif cleaned.startswith('8') and len(cleaned) >= 9:
                cleaned = '+62' + cleaned
            
            # Validate with phonenumbers library
            try:
                parsed = phonenumbers.parse(cleaned, 'ID')
                if phonenumbers.is_valid_number(parsed):
                    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            except NumberParseException:
                pass
            
            # Basic validation for Indonesian numbers
            if cleaned.startswith('+62') and len(cleaned) >= 12 and len(cleaned) <= 15:
                return cleaned
            
            return None
            
        except Exception as e:
            logger.error(f"Error cleaning phone number {phone}: {e}")
            return None
    
    def _validate_phone_number(self, phone: str) -> Optional[str]:
        """Validate phone number format"""
        try:
            # Extract potential phone number from text
            phone_match = re.search(r'[\+62|08|62][\d\s\-\.]{8,14}', phone)
            if phone_match:
                return self._clean_phone_number(phone_match.group())
            return None
        except Exception:
            return None
    
    def _validate_email_address(self, email: str) -> Optional[str]:
        """Validate email address"""
        try:
            # Extract email from text
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email)
            if email_match:
                email_addr = email_match.group()
                validated = validate_email(email_addr)
                return validated.email
            return None
        except EmailNotValidError:
            return None
        except Exception:
            return None
    
    def _parse_contact_results(self, agent_result: str, original_query: str) -> List[Dict[str, Any]]:
        """Parse the AI agent's contact search results"""
        try:
            # Extract contacts from the agent's response
            all_contacts = self._extract_all_contacts(agent_result)
            
            # Group contacts by type and deduplicate
            grouped_contacts = {
                'whatsapp': [],
                'phone': [],
                'email': [],
                'social': []
            }
            
            seen_values = set()
            
            for contact in all_contacts:
                value = contact['value']
                contact_type = contact['type']
                
                if value not in seen_values:
                    seen_values.add(value)
                    
                    if contact_type == 'whatsapp' or (contact_type == 'phone' and value.startswith('+62')):
                        grouped_contacts['whatsapp'].append(value)
                    elif contact_type == 'phone':
                        grouped_contacts['phone'].append(value)
                    elif contact_type == 'email':
                        grouped_contacts['email'].append(value)
                    elif contact_type.startswith('social_'):
                        grouped_contacts['social'].append(f"{contact_type.replace('social_', '')}: {value}")
            
            # Create structured result
            result = {
                'query': original_query,
                'whatsapp_numbers': grouped_contacts['whatsapp'],
                'phone_numbers': grouped_contacts['phone'],
                'email_addresses': grouped_contacts['email'],
                'social_media': grouped_contacts['social'],
                'total_contacts_found': len(seen_values)
            }
            
            return [result] if any(grouped_contacts.values()) else []
            
        except Exception as e:
            logger.error(f"Error parsing contact results: {e}")
            return []