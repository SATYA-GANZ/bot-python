"""
WhatsApp Agent - Automated WhatsApp messaging
"""

import os
import time
import asyncio
import logging
from typing import List, Dict, Any, Optional
import pyautogui
import pywhatkit as kit
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

class WhatsAppAgent:
    def __init__(self):
        self.send_delay = int(os.getenv('WHATSAPP_SEND_DELAY', '10'))
        self.driver = None
        self.is_web_logged_in = False
        
    async def send_message(self, phone_number: str, message: str, use_web: bool = True) -> bool:
        """
        Send WhatsApp message
        
        Args:
            phone_number: Phone number in international format (+62xxx)
            message: Message to send
            use_web: Whether to use WhatsApp Web (True) or pywhatkit (False)
        """
        try:
            if use_web:
                return await self._send_via_web(phone_number, message)
            else:
                return await self._send_via_pywhatkit(phone_number, message)
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return False
    
    async def send_bulk_messages(self, contacts: List[Dict[str, str]], delay_between: int = 30) -> Dict[str, int]:
        """
        Send bulk WhatsApp messages
        
        Args:
            contacts: List of contacts with 'phone' and 'message' keys
            delay_between: Delay between messages in seconds
        """
        results = {
            'sent': 0,
            'failed': 0,
            'total': len(contacts)
        }
        
        logger.info(f"Starting bulk message sending to {len(contacts)} contacts")
        
        for i, contact in enumerate(contacts):
            try:
                phone = contact.get('phone', '')
                message = contact.get('message', '')
                
                if not phone or not message:
                    logger.warning(f"Skipping contact {i+1}: missing phone or message")
                    results['failed'] += 1
                    continue
                
                logger.info(f"Sending message {i+1}/{len(contacts)} to {phone}")
                
                success = await self.send_message(phone, message)
                
                if success:
                    results['sent'] += 1
                    logger.info(f"✅ Message sent successfully to {phone}")
                else:
                    results['failed'] += 1
                    logger.error(f"❌ Failed to send message to {phone}")
                
                # Wait between messages to avoid being blocked
                if i < len(contacts) - 1:
                    logger.info(f"Waiting {delay_between} seconds before next message...")
                    await asyncio.sleep(delay_between)
                    
            except Exception as e:
                logger.error(f"Error sending to contact {i+1}: {e}")
                results['failed'] += 1
                continue
        
        logger.info(f"Bulk messaging completed: {results['sent']} sent, {results['failed']} failed")
        return results
    
    async def _send_via_web(self, phone_number: str, message: str) -> bool:
        """Send message via WhatsApp Web using Selenium"""
        try:
            # Initialize browser if not already done
            if not self.driver:
                await self._init_browser()
            
            # Format phone number
            clean_phone = phone_number.replace('+', '').replace(' ', '').replace('-', '')
            
            # Navigate to WhatsApp Web chat
            url = f"https://web.whatsapp.com/send?phone={clean_phone}&text={message}"
            self.driver.get(url)
            
            # Wait for page to load
            await asyncio.sleep(5)
            
            # Check if we need to scan QR code
            if self._check_qr_code_present():
                logger.warning("WhatsApp Web requires QR code scan. Please scan and try again.")
                return False
            
            # Wait for chat to load
            try:
                # Wait for the message input box
                message_box = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
                )
                
                # Clear any existing text and type the message
                message_box.clear()
                message_box.send_keys(message)
                
                # Wait a moment for the message to be typed
                await asyncio.sleep(2)
                
                # Send the message (Enter key)
                message_box.send_keys(Keys.ENTER)
                
                # Wait for message to be sent
                await asyncio.sleep(3)
                
                logger.info(f"Message sent successfully to {phone_number}")
                return True
                
            except Exception as e:
                logger.error(f"Error in WhatsApp Web interface: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error in WhatsApp Web sending: {e}")
            return False
    
    async def _send_via_pywhatkit(self, phone_number: str, message: str) -> bool:
        """Send message via pywhatkit (opens WhatsApp Web automatically)"""
        try:
            # Calculate time to send (current time + delay)
            now = time.localtime()
            send_hour = now.tm_hour
            send_minute = now.tm_min + 2  # Send 2 minutes from now
            
            if send_minute >= 60:
                send_hour += 1
                send_minute -= 60
            
            # Use pywhatkit to send message
            kit.sendwhatmsg(phone_number, message, send_hour, send_minute, 15, True, 2)
            
            # Wait for the message to be sent
            await asyncio.sleep(20)
            
            logger.info(f"Message sent via pywhatkit to {phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending via pywhatkit: {e}")
            return False
    
    async def _init_browser(self):
        """Initialize Chrome browser for WhatsApp Web"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Set user data directory to maintain session
            user_data_dir = os.path.expanduser("~/whatsapp_chrome_data")
            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
            
            self.driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            # Set window size
            self.driver.set_window_size(1200, 800)
            
            logger.info("Chrome browser initialized for WhatsApp Web")
            
        except Exception as e:
            logger.error(f"Error initializing browser: {e}")
            raise
    
    def _check_qr_code_present(self) -> bool:
        """Check if QR code is present (meaning not logged in)"""
        try:
            # Look for QR code canvas element
            qr_elements = self.driver.find_elements(By.XPATH, "//canvas[@aria-label='Scan me!']")
            return len(qr_elements) > 0
        except Exception:
            return False
    
    async def check_login_status(self) -> bool:
        """Check if WhatsApp Web is logged in"""
        try:
            if not self.driver:
                await self._init_browser()
            
            self.driver.get("https://web.whatsapp.com")
            await asyncio.sleep(5)
            
            # Check if we can find the main chat interface
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@id="main"]'))
                )
                self.is_web_logged_in = True
                logger.info("WhatsApp Web is logged in")
                return True
            except:
                self.is_web_logged_in = False
                logger.warning("WhatsApp Web is not logged in")
                return False
                
        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return False
    
    async def close_browser(self):
        """Close the browser"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
    
    def create_message_template(self, template_name: str, brand_info: Dict[str, Any]) -> str:
        """Create a personalized message template"""
        templates = {
            'introduction': f"""
Halo {brand_info.get('name', 'Brand')}! 👋

Saya tertarik dengan produk kecantikan yang Anda tawarkan. 
Boleh saya mendapatkan informasi lebih lanjut tentang:
• Katalog produk terbaru
• Harga dan paket yang tersedia
• Sistem reseller/distributor

Terima kasih! 🙏
            """.strip(),
            
            'collaboration': f"""
Halo {brand_info.get('name', 'Brand')}! 

Saya dari tim marketing yang sedang mencari partner brand kecantikan lokal berkualitas.
Apakah Anda terbuka untuk diskusi mengenai kolaborasi atau kemitraan?

Kami tertarik dengan:
• Program reseller
• Kolaborasi konten
• Event partnership

Mohon info lebih lanjut. Terima kasih! ✨
            """.strip(),
            
            'customer_inquiry': f"""
Halo! Saya customer yang tertarik dengan produk {brand_info.get('name', 'brand Anda')}.

Bisa tolong kirimkan informasi:
• Produk best seller
• Harga dan cara order
• Testimoni customer
• Lokasi toko/cara pengiriman

Ditunggu balasannya ya! 😊
            """.strip()
        }
        
        return templates.get(template_name, templates['introduction'])
    
    def format_phone_number(self, phone: str) -> str:
        """Format phone number for WhatsApp"""
        # Remove all non-digit characters except +
        cleaned = ''.join(char for char in phone if char.isdigit() or char == '+')
        
        # Ensure it starts with country code
        if cleaned.startswith('08'):
            return '+62' + cleaned[1:]
        elif cleaned.startswith('62') and not cleaned.startswith('+62'):
            return '+' + cleaned
        elif not cleaned.startswith('+'):
            return '+62' + cleaned
        
        return cleaned
    
    async def send_template_message(self, phone_number: str, template_name: str, brand_info: Dict[str, Any]) -> bool:
        """Send a templated message"""
        try:
            message = self.create_message_template(template_name, brand_info)
            return await self.send_message(phone_number, message)
        except Exception as e:
            logger.error(f"Error sending template message: {e}")
            return False
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass