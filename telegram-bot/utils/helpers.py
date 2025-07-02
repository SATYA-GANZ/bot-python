"""
Helper utilities for Beauty Brand Bot
"""

import re
import logging
from typing import Dict, Any, List, Optional
import phonenumbers
from phonenumbers import NumberParseException
from email_validator import validate_email, EmailNotValidError
from urllib.parse import urlparse
import unicodedata

logger = logging.getLogger(__name__)

def format_brand_info(brand: Dict[str, Any]) -> str:
    """Format brand information for display in Telegram"""
    try:
        output = []
        
        # Brand name
        name = brand.get('name', 'Unknown Brand')
        output.append(f"**🏢 {name}**")
        
        # Category
        category = brand.get('category', '')
        if category:
            output.append(f"📂 **Category:** {category}")
        
        # Business type
        business_type = brand.get('business_type', '')
        if business_type:
            output.append(f"🏭 **Type:** {business_type}")
        
        # Location
        location = brand.get('location', '')
        if location:
            output.append(f"📍 **Location:** {location}")
        
        # Website
        website = brand.get('website', '')
        if website:
            output.append(f"🌐 **Website:** {website}")
        
        # Contacts
        contacts = brand.get('contacts', [])
        whatsapp_numbers = brand.get('whatsapp_numbers', [])
        phone_numbers = brand.get('phone_numbers', [])
        email_addresses = brand.get('email_addresses', [])
        
        if whatsapp_numbers:
            output.append(f"📱 **WhatsApp:** {', '.join(whatsapp_numbers)}")
        
        if phone_numbers:
            output.append(f"📞 **Phone:** {', '.join(phone_numbers)}")
        
        if email_addresses:
            output.append(f"📧 **Email:** {', '.join(email_addresses)}")
        
        if contacts and not any([whatsapp_numbers, phone_numbers, email_addresses]):
            contact_str = ', '.join(contacts[:3])  # Show first 3 contacts
            if len(contacts) > 3:
                contact_str += f" (+{len(contacts)-3} more)"
            output.append(f"📞 **Contacts:** {contact_str}")
        
        # Social media
        social_media = brand.get('social_media', [])
        if social_media:
            social_str = ', '.join(social_media[:2])  # Show first 2 social media
            if len(social_media) > 2:
                social_str += f" (+{len(social_media)-2} more)"
            output.append(f"🌟 **Social:** {social_str}")
        
        # Description
        description = brand.get('description', '')
        if description:
            # Truncate long descriptions
            if len(description) > 100:
                description = description[:100] + "..."
            output.append(f"📝 **Description:** {description}")
        
        # Timestamps
        scraped_at = brand.get('scraped_at', '')
        if scraped_at:
            output.append(f"🕒 **Found:** {format_timestamp(scraped_at)}")
        
        return '\n'.join(output)
        
    except Exception as e:
        logger.error(f"Error formatting brand info: {e}")
        return f"**Brand:** {brand.get('name', 'Unknown')}\n❌ Error formatting information"

def format_timestamp(timestamp_str: str) -> str:
    """Format timestamp for display"""
    try:
        from datetime import datetime
        
        # Try different timestamp formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f"
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(timestamp_str, fmt)
                return dt.strftime("%d %b %Y")
            except ValueError:
                continue
        
        return timestamp_str  # Return as-is if parsing fails
        
    except Exception:
        return timestamp_str

def validate_phone_number(phone: str) -> bool:
    """Validate Indonesian phone number"""
    try:
        if not phone:
            return False
        
        # Clean the phone number
        cleaned = clean_phone_number(phone)
        if not cleaned:
            return False
        
        # Parse with phonenumbers library
        try:
            parsed = phonenumbers.parse(cleaned, 'ID')
            return phonenumbers.is_valid_number(parsed)
        except NumberParseException:
            pass
        
        # Basic validation for Indonesian numbers
        if cleaned.startswith('+62'):
            # Indonesian number should be 12-15 digits total
            digits_only = re.sub(r'[^\d]', '', cleaned)
            return len(digits_only) >= 11 and len(digits_only) <= 15
        
        return False
        
    except Exception as e:
        logger.error(f"Error validating phone number {phone}: {e}")
        return False

def clean_phone_number(phone: str) -> Optional[str]:
    """Clean and standardize phone number"""
    try:
        if not phone:
            return None
        
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Handle Indonesian number formats
        if cleaned.startswith('08'):
            # Convert 08xxx to +628xxx
            cleaned = '+62' + cleaned[1:]
        elif cleaned.startswith('62') and not cleaned.startswith('+62'):
            # Convert 62xxx to +62xxx
            cleaned = '+' + cleaned
        elif cleaned.startswith('8') and len(cleaned) >= 9:
            # Convert 8xxx to +628xxx
            cleaned = '+62' + cleaned
        elif not cleaned.startswith('+') and len(cleaned) >= 10:
            # Assume Indonesian number
            cleaned = '+62' + cleaned
        
        # Basic validation
        if cleaned.startswith('+62') and len(cleaned) >= 12 and len(cleaned) <= 15:
            return cleaned
        
        return None
        
    except Exception as e:
        logger.error(f"Error cleaning phone number {phone}: {e}")
        return None

def validate_email_address(email: str) -> bool:
    """Validate email address"""
    try:
        if not email:
            return False
        
        # Basic regex check first
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False
        
        # Use email-validator for more thorough validation
        try:
            validated = validate_email(email)
            return True
        except EmailNotValidError:
            return False
            
    except Exception as e:
        logger.error(f"Error validating email {email}: {e}")
        return False

def validate_url(url: str) -> bool:
    """Validate URL format"""
    try:
        if not url:
            return False
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        parsed = urlparse(url)
        return bool(parsed.netloc)
        
    except Exception:
        return False

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    try:
        if not text:
            return ""
        
        # Normalize unicode characters
        text = unicodedata.normalize('NFKD', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove control characters
        text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C')
        
        return text
        
    except Exception as e:
        logger.error(f"Error cleaning text: {e}")
        return text

def extract_domain_from_url(url: str) -> str:
    """Extract domain from URL"""
    try:
        if not url:
            return ""
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return domain
        
    except Exception:
        return ""

def format_contact_list(contacts: List[str]) -> str:
    """Format a list of contacts for display"""
    try:
        if not contacts:
            return "No contacts found"
        
        formatted = []
        for contact in contacts[:5]:  # Show first 5 contacts
            # Clean up the contact string
            contact = contact.strip()
            if contact:
                formatted.append(f"• {contact}")
        
        if len(contacts) > 5:
            formatted.append(f"• ... and {len(contacts) - 5} more")
        
        return '\n'.join(formatted)
        
    except Exception as e:
        logger.error(f"Error formatting contact list: {e}")
        return "Error formatting contacts"

def extract_business_keywords(text: str) -> List[str]:
    """Extract business-related keywords from text"""
    try:
        # Keywords that indicate business type/category
        beauty_keywords = [
            'skincare', 'makeup', 'kosmetik', 'kecantikan', 'perawatan',
            'serum', 'moisturizer', 'cleanser', 'toner', 'masker',
            'foundation', 'lipstick', 'eyeshadow', 'blush', 'concealer',
            'sunscreen', 'essence', 'facial', 'body care', 'hair care',
            'natural', 'organic', 'halal', 'herbal', 'traditional'
        ]
        
        business_keywords = [
            'umkm', 'usaha', 'bisnis', 'brand', 'company', 'enterprise',
            'startup', 'home industry', 'small business', 'lokal',
            'indonesia', 'jakarta', 'surabaya', 'bandung', 'medan'
        ]
        
        all_keywords = beauty_keywords + business_keywords
        text_lower = text.lower()
        
        found_keywords = []
        for keyword in all_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
        
    except Exception as e:
        logger.error(f"Error extracting keywords: {e}")
        return []

def categorize_business_size(brand_info: Dict[str, Any]) -> str:
    """Categorize business size based on available information"""
    try:
        name = brand_info.get('name', '').lower()
        website = brand_info.get('website', '').lower()
        description = brand_info.get('description', '').lower()
        
        text_to_analyze = f"{name} {website} {description}"
        
        # Keywords that suggest different business sizes
        large_indicators = [
            'group', 'corporation', 'tbk', 'pt.', 'multinational',
            'international', 'holding', 'conglomerate'
        ]
        
        medium_indicators = [
            'company', 'enterprise', 'corporation', 'industry',
            'manufacturer', 'distributor', 'wholesale'
        ]
        
        small_indicators = [
            'umkm', 'home', 'handmade', 'artisan', 'lokal', 'rumahan',
            'startup', 'small', 'micro', 'personal', 'individual'
        ]
        
        # Check for large business indicators
        if any(indicator in text_to_analyze for indicator in large_indicators):
            return 'Large'
        
        # Check for medium business indicators
        elif any(indicator in text_to_analyze for indicator in medium_indicators):
            return 'Medium'
        
        # Check for small business indicators
        elif any(indicator in text_to_analyze for indicator in small_indicators):
            return 'Small'
        
        # Default classification based on other factors
        else:
            # If has professional website and multiple contact methods, likely medium
            if website and len(brand_info.get('contacts', [])) > 2:
                return 'Medium'
            else:
                return 'Small'  # Default to small for UMKM focus
        
    except Exception as e:
        logger.error(f"Error categorizing business size: {e}")
        return 'Unknown'

def format_whatsapp_number(phone: str) -> str:
    """Format phone number for WhatsApp API"""
    try:
        cleaned = clean_phone_number(phone)
        if cleaned:
            # Remove + for WhatsApp API
            return cleaned.replace('+', '')
        return phone
        
    except Exception:
        return phone

def create_contact_summary(brand_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a summary of contact information for a brand"""
    try:
        summary = {
            'brand_name': brand_data.get('name', 'Unknown'),
            'whatsapp_contacts': [],
            'email_contacts': [],
            'phone_contacts': [],
            'social_contacts': [],
            'has_website': bool(brand_data.get('website')),
            'total_contacts': 0
        }
        
        contacts = brand_data.get('contacts', [])
        
        for contact in contacts:
            contact_lower = contact.lower()
            
            if 'whatsapp' in contact_lower or 'wa.' in contact_lower:
                summary['whatsapp_contacts'].append(contact)
            elif '@' in contact:
                summary['email_contacts'].append(contact)
            elif any(char.isdigit() for char in contact):
                summary['phone_contacts'].append(contact)
            elif any(platform in contact_lower for platform in ['instagram', 'facebook', 'tiktok']):
                summary['social_contacts'].append(contact)
        
        # Also check specific contact type fields
        for field in ['whatsapp_numbers', 'email_addresses', 'phone_numbers', 'social_media']:
            field_data = brand_data.get(field, [])
            if field_data:
                if field == 'whatsapp_numbers':
                    summary['whatsapp_contacts'].extend(field_data)
                elif field == 'email_addresses':
                    summary['email_contacts'].extend(field_data)
                elif field == 'phone_numbers':
                    summary['phone_contacts'].extend(field_data)
                elif field == 'social_media':
                    summary['social_contacts'].extend(field_data)
        
        # Remove duplicates
        for key in ['whatsapp_contacts', 'email_contacts', 'phone_contacts', 'social_contacts']:
            summary[key] = list(set(summary[key]))
        
        # Calculate total
        summary['total_contacts'] = (
            len(summary['whatsapp_contacts']) +
            len(summary['email_contacts']) +
            len(summary['phone_contacts']) +
            len(summary['social_contacts'])
        )
        
        return summary
        
    except Exception as e:
        logger.error(f"Error creating contact summary: {e}")
        return {
            'brand_name': brand_data.get('name', 'Unknown'),
            'whatsapp_contacts': [],
            'email_contacts': [],
            'phone_contacts': [],
            'social_contacts': [],
            'has_website': False,
            'total_contacts': 0
        }

def generate_search_suggestions(query: str) -> List[str]:
    """Generate search suggestions based on query"""
    try:
        suggestions = []
        query_lower = query.lower()
        
        # Beauty category suggestions
        beauty_categories = [
            'skincare', 'makeup', 'cosmetics', 'beauty tools',
            'hair care', 'body care', 'fragrance', 'nail care'
        ]
        
        # Business type suggestions
        business_types = [
            'UMKM skincare', 'brand lokal makeup', 'kosmetik halal',
            'perawatan wajah alami', 'startup beauty Indonesia'
        ]
        
        # Location-based suggestions
        location_suggestions = [
            f'{query} Jakarta', f'{query} Surabaya', f'{query} Bandung',
            f'{query} Yogyakarta', f'{query} Indonesia'
        ]
        
        # Add relevant suggestions based on query
        if any(word in query_lower for word in ['beauty', 'kecantikan', 'kosmetik']):
            suggestions.extend(beauty_categories[:3])
        
        if any(word in query_lower for word in ['umkm', 'small', 'local', 'lokal']):
            suggestions.extend(business_types[:3])
        
        if len(query) > 3:  # Only add location suggestions for longer queries
            suggestions.extend(location_suggestions[:2])
        
        return suggestions[:5]  # Return max 5 suggestions
        
    except Exception as e:
        logger.error(f"Error generating search suggestions: {e}")
        return []