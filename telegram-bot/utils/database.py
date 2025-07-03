"""
Database Manager for Beauty Brand Bot
"""

import os
import sqlite3
import asyncio
import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "beauty_brands.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create brands table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS brands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    website TEXT,
                    category TEXT,
                    location TEXT,
                    business_type TEXT,
                    contacts TEXT,  -- JSON string of contact info
                    social_media TEXT,  -- JSON string of social media
                    description TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    notes TEXT
                )
                """)
                
                # Create contacts table (normalized)
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    brand_id INTEGER,
                    contact_type TEXT,  -- 'phone', 'email', 'whatsapp', 'social'
                    contact_value TEXT,
                    is_primary BOOLEAN DEFAULT 0,
                    is_verified BOOLEAN DEFAULT 0,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (brand_id) REFERENCES brands (id)
                )
                """)
                
                # Create outreach_log table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS outreach_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    brand_id INTEGER,
                    contact_value TEXT,
                    message_type TEXT,  -- 'whatsapp', 'email'
                    message_content TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT,  -- 'sent', 'failed', 'pending'
                    response_received BOOLEAN DEFAULT 0,
                    notes TEXT,
                    FOREIGN KEY (brand_id) REFERENCES brands (id)
                )
                """)
                
                # Create search_history table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    search_query TEXT,
                    search_type TEXT,  -- 'brand_scrape', 'contact_search'
                    results_count INTEGER,
                    search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_brands_name ON brands(name)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_brand_id ON contacts(brand_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_outreach_brand_id ON outreach_log(brand_id)")
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    async def save_brand(self, brand_data: Dict[str, Any]) -> int:
        """Save brand data to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if brand already exists
                cursor.execute(
                    "SELECT id FROM brands WHERE name = ? OR website = ?",
                    (brand_data.get('name', ''), brand_data.get('website', ''))
                )
                existing = cursor.fetchone()
                
                if existing:
                    brand_id = existing[0]
                    # Update existing brand
                    cursor.execute("""
                        UPDATE brands SET
                            website = ?, category = ?, location = ?, business_type = ?,
                            contacts = ?, description = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (
                        brand_data.get('website', ''),
                        brand_data.get('category', ''),
                        brand_data.get('location', ''),
                        brand_data.get('business_type', ''),
                        json.dumps(brand_data.get('contacts', [])),
                        brand_data.get('description', ''),
                        brand_id
                    ))
                    logger.info(f"Updated existing brand: {brand_data.get('name')}")
                else:
                    # Insert new brand
                    cursor.execute("""
                        INSERT INTO brands (name, website, category, location, business_type, contacts, description)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        brand_data.get('name', 'Unknown'),
                        brand_data.get('website', ''),
                        brand_data.get('category', ''),
                        brand_data.get('location', ''),
                        brand_data.get('business_type', ''),
                        json.dumps(brand_data.get('contacts', [])),
                        brand_data.get('description', '')
                    ))
                    brand_id = cursor.lastrowid
                    logger.info(f"Saved new brand: {brand_data.get('name')}")
                
                # Save individual contacts
                await self._save_contacts(cursor, brand_id, brand_data.get('contacts', []))
                
                conn.commit()
                return brand_id
                
        except Exception as e:
            logger.error(f"Error saving brand data: {e}")
            return 0
    
    async def _save_contacts(self, cursor, brand_id: int, contacts: List[str]):
        """Save individual contacts for a brand"""
        try:
            # Clear existing contacts for this brand
            cursor.execute("DELETE FROM contacts WHERE brand_id = ?", (brand_id,))
            
            for contact in contacts:
                contact_type = self._determine_contact_type(contact)
                contact_value = self._extract_contact_value(contact)
                
                if contact_value:
                    cursor.execute("""
                        INSERT INTO contacts (brand_id, contact_type, contact_value)
                        VALUES (?, ?, ?)
                    """, (brand_id, contact_type, contact_value))
                    
        except Exception as e:
            logger.error(f"Error saving contacts: {e}")
    
    def _determine_contact_type(self, contact: str) -> str:
        """Determine the type of contact (phone, email, whatsapp, social)"""
        contact_lower = contact.lower()
        
        if 'whatsapp' in contact_lower or 'wa.' in contact_lower:
            return 'whatsapp'
        elif '@' in contact:
            return 'email'
        elif any(char.isdigit() for char in contact):
            return 'phone'
        elif any(platform in contact_lower for platform in ['instagram', 'facebook', 'tiktok', 'youtube']):
            return 'social'
        else:
            return 'other'
    
    def _extract_contact_value(self, contact: str) -> str:
        """Extract the actual contact value from contact string"""
        # Remove prefixes like "Phone: ", "Email: ", etc.
        for prefix in ['phone:', 'email:', 'whatsapp:', 'wa:', 'social:']:
            if contact.lower().startswith(prefix):
                return contact[len(prefix):].strip()
        
        return contact.strip()
    
    async def get_all_brands(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all brands from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, name, website, category, location, business_type, 
                           contacts, description, scraped_at, updated_at
                    FROM brands 
                    WHERE is_active = 1
                    ORDER BY updated_at DESC
                    LIMIT ? OFFSET ?
                """, (limit, offset))
                
                brands = []
                for row in cursor.fetchall():
                    brand = {
                        'id': row[0],
                        'name': row[1],
                        'website': row[2],
                        'category': row[3],
                        'location': row[4],
                        'business_type': row[5],
                        'contacts': json.loads(row[6]) if row[6] else [],
                        'description': row[7],
                        'scraped_at': row[8],
                        'updated_at': row[9]
                    }
                    brands.append(brand)
                
                return brands
                
        except Exception as e:
            logger.error(f"Error getting brands: {e}")
            return []
    
    async def search_brands(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search brands by name, category, location, etc."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                base_query = """
                    SELECT id, name, website, category, location, business_type, 
                           contacts, description, scraped_at, updated_at
                    FROM brands 
                    WHERE is_active = 1
                """
                
                params = []
                conditions = []
                
                # Add search query condition
                if query:
                    conditions.append("(name LIKE ? OR category LIKE ? OR location LIKE ? OR description LIKE ?)")
                    search_param = f"%{query}%"
                    params.extend([search_param, search_param, search_param, search_param])
                
                # Add filters
                if filters:
                    if filters.get('category'):
                        conditions.append("category = ?")
                        params.append(filters['category'])
                    
                    if filters.get('business_type'):
                        conditions.append("business_type = ?")
                        params.append(filters['business_type'])
                    
                    if filters.get('location'):
                        conditions.append("location LIKE ?")
                        params.append(f"%{filters['location']}%")
                
                # Build final query
                if conditions:
                    base_query += " AND " + " AND ".join(conditions)
                
                base_query += " ORDER BY updated_at DESC LIMIT 50"
                
                cursor.execute(base_query, params)
                
                brands = []
                for row in cursor.fetchall():
                    brand = {
                        'id': row[0],
                        'name': row[1],
                        'website': row[2],
                        'category': row[3],
                        'location': row[4],
                        'business_type': row[5],
                        'contacts': json.loads(row[6]) if row[6] else [],
                        'description': row[7],
                        'scraped_at': row[8],
                        'updated_at': row[9]
                    }
                    brands.append(brand)
                
                return brands
                
        except Exception as e:
            logger.error(f"Error searching brands: {e}")
            return []
    
    async def get_contacts_by_type(self, contact_type: str = 'whatsapp') -> List[Dict[str, Any]]:
        """Get all contacts of a specific type"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT c.contact_value, c.contact_type, b.name, b.id
                    FROM contacts c
                    JOIN brands b ON c.brand_id = b.id
                    WHERE c.contact_type = ? AND b.is_active = 1
                    ORDER BY b.name
                """, (contact_type,))
                
                contacts = []
                for row in cursor.fetchall():
                    contact = {
                        'value': row[0],
                        'type': row[1],
                        'brand_name': row[2],
                        'brand_id': row[3]
                    }
                    contacts.append(contact)
                
                return contacts
                
        except Exception as e:
            logger.error(f"Error getting contacts by type: {e}")
            return []
    
    async def log_outreach(self, brand_id: int, contact_value: str, message_type: str, 
                          message_content: str, status: str) -> int:
        """Log outreach attempt"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO outreach_log (brand_id, contact_value, message_type, message_content, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (brand_id, contact_value, message_type, message_content, status))
                
                log_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"Logged outreach attempt: {message_type} to {contact_value}")
                return log_id
                
        except Exception as e:
            logger.error(f"Error logging outreach: {e}")
            return 0
    
    async def get_outreach_history(self, brand_id: int = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get outreach history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if brand_id:
                    cursor.execute("""
                        SELECT ol.*, b.name
                        FROM outreach_log ol
                        JOIN brands b ON ol.brand_id = b.id
                        WHERE ol.brand_id = ?
                        ORDER BY ol.sent_at DESC
                        LIMIT ?
                    """, (brand_id, limit))
                else:
                    cursor.execute("""
                        SELECT ol.*, b.name
                        FROM outreach_log ol
                        JOIN brands b ON ol.brand_id = b.id
                        ORDER BY ol.sent_at DESC
                        LIMIT ?
                    """, (limit,))
                
                history = []
                for row in cursor.fetchall():
                    record = {
                        'id': row[0],
                        'brand_id': row[1],
                        'contact_value': row[2],
                        'message_type': row[3],
                        'message_content': row[4],
                        'sent_at': row[5],
                        'status': row[6],
                        'response_received': row[7],
                        'notes': row[8],
                        'brand_name': row[9]
                    }
                    history.append(record)
                
                return history
                
        except Exception as e:
            logger.error(f"Error getting outreach history: {e}")
            return []
    
    async def export_to_csv(self, filename: str = None) -> str:
        """Export brands data to CSV"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"beauty_brands_export_{timestamp}.csv"
            
            brands = await self.get_all_brands(limit=10000)  # Get all brands
            
            if not brands:
                return "No data to export"
            
            # Convert to DataFrame
            df = pd.DataFrame(brands)
            
            # Flatten contacts column
            df['contacts'] = df['contacts'].apply(lambda x: '; '.join(x) if isinstance(x, list) else str(x))
            
            # Save to CSV
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            
            logger.info(f"Data exported to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return f"Export failed: {str(e)}"
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Total brands
                cursor.execute("SELECT COUNT(*) FROM brands WHERE is_active = 1")
                stats['total_brands'] = cursor.fetchone()[0]
                
                # Brands by business type
                cursor.execute("""
                    SELECT business_type, COUNT(*) 
                    FROM brands 
                    WHERE is_active = 1 
                    GROUP BY business_type
                """)
                stats['by_business_type'] = dict(cursor.fetchall())
                
                # Brands by category
                cursor.execute("""
                    SELECT category, COUNT(*) 
                    FROM brands 
                    WHERE is_active = 1 
                    GROUP BY category
                """)
                stats['by_category'] = dict(cursor.fetchall())
                
                # Total contacts
                cursor.execute("SELECT COUNT(*) FROM contacts")
                stats['total_contacts'] = cursor.fetchone()[0]
                
                # Contacts by type
                cursor.execute("""
                    SELECT contact_type, COUNT(*) 
                    FROM contacts 
                    GROUP BY contact_type
                """)
                stats['contacts_by_type'] = dict(cursor.fetchall())
                
                # Total outreach attempts
                cursor.execute("SELECT COUNT(*) FROM outreach_log")
                stats['total_outreach'] = cursor.fetchone()[0]
                
                # Recent activity (last 7 days)
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM brands 
                    WHERE scraped_at >= datetime('now', '-7 days')
                """)
                stats['recent_brands'] = cursor.fetchone()[0]
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    async def cleanup_old_data(self, days: int = 90):
        """Clean up old data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Archive old outreach logs
                cursor.execute("""
                    DELETE FROM outreach_log 
                    WHERE sent_at < datetime('now', '-{} days')
                """.format(days))
                
                # Archive old search history
                cursor.execute("""
                    DELETE FROM search_history 
                    WHERE search_date < datetime('now', '-{} days')
                """.format(days))
                
                conn.commit()
                logger.info(f"Cleaned up data older than {days} days")
                
        except Exception as e:
            logger.error(f"Error cleaning up data: {e}")
    
    def close(self):
        """Close database connection"""
        # SQLite connections are closed automatically in context managers
        pass