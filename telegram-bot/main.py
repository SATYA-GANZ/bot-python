#!/usr/bin/env python3
"""
Telegram Bot with AI Agent for Indonesian Beauty Brand Scraping and Outreach
"""

import os
import logging
import asyncio
from typing import Dict, List, Any
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    filters,
    ContextTypes
)

from agents.beauty_scraper_agent import BeautyScrapeAgent
from agents.contact_finder_agent import ContactFinderAgent
from agents.whatsapp_agent import WhatsAppAgent
from utils.database import DatabaseManager
from utils.helpers import format_brand_info, validate_phone_number

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class BeautyBotAgent:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.scraper_agent = BeautyScrapeAgent()
        self.contact_agent = ContactFinderAgent()
        self.whatsapp_agent = WhatsAppAgent()
        self.db = DatabaseManager()
        
        # User sessions to track ongoing operations
        self.user_sessions: Dict[int, Dict] = {}
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        self.user_sessions[user_id] = {"stage": "menu"}
        
        keyboard = [
            [InlineKeyboardButton("🔍 Scrape Beauty Brands", callback_data="scrape_brands")],
            [InlineKeyboardButton("📞 Find Contacts", callback_data="find_contacts")],
            [InlineKeyboardButton("📱 WhatsApp Outreach", callback_data="whatsapp_outreach")],
            [InlineKeyboardButton("📊 View Database", callback_data="view_database")],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = """
🤖 **Welcome to Beauty Brand AI Agent Bot!**

This bot helps you:
• 🔍 Scrape Indonesian beauty brands (UMKM focus)
• 📞 Find contact information (WhatsApp, Email)
• 📱 Automate WhatsApp outreach
• 📊 Manage brand database

Choose an option below to get started:
        """
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        data = query.data
        
        if data == "scrape_brands":
            await self.handle_scrape_brands(query, user_id)
        elif data == "find_contacts":
            await self.handle_find_contacts(query, user_id)
        elif data == "whatsapp_outreach":
            await self.handle_whatsapp_outreach(query, user_id)
        elif data == "view_database":
            await self.handle_view_database(query, user_id)
        elif data == "help":
            await self.handle_help(query)
        elif data == "back_to_menu":
            await self.start_command(update, context)
    
    async def handle_scrape_brands(self, query, user_id: int):
        """Handle beauty brand scraping"""
        self.user_sessions[user_id] = {"stage": "scraping"}
        
        keyboard = [
            [InlineKeyboardButton("🏢 Medium Companies", callback_data="scrape_medium")],
            [InlineKeyboardButton("🏪 Small/UMKM", callback_data="scrape_small")],
            [InlineKeyboardButton("🌟 All Beauty Brands", callback_data="scrape_all")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = """
🔍 **Beauty Brand Scraping Options**

Choose the type of companies to scrape:
• 🏢 Medium Companies: Established beauty brands
• 🏪 Small/UMKM: Micro, Small & Medium Enterprises
• 🌟 All: Comprehensive search

The AI agent will search for Indonesian beauty brands and extract their information.
        """
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def handle_find_contacts(self, query, user_id: int):
        """Handle contact finding"""
        self.user_sessions[user_id] = {"stage": "finding_contacts"}
        
        text = """
📞 **Contact Information Finder**

Send me a brand name or website URL, and I'll find:
• 📱 WhatsApp numbers
• 📧 Email addresses
• 🌐 Social media contacts
• 🏢 Business information

Just type the brand name or URL after this message.
        """
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def handle_whatsapp_outreach(self, query, user_id: int):
        """Handle WhatsApp outreach"""
        self.user_sessions[user_id] = {"stage": "whatsapp_outreach"}
        
        text = """
📱 **WhatsApp Outreach Agent**

I can help you send automated WhatsApp messages to beauty brands.

**Available options:**
• 📤 Send single message
• 📊 Bulk message from database
• 📝 Create message templates

**Note:** Make sure WhatsApp Web is logged in on your browser for automation to work.

What would you like to do?
        """
        
        keyboard = [
            [InlineKeyboardButton("📤 Single Message", callback_data="wa_single")],
            [InlineKeyboardButton("📊 Bulk Messages", callback_data="wa_bulk")],
            [InlineKeyboardButton("📝 Message Templates", callback_data="wa_templates")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def handle_view_database(self, query, user_id: int):
        """Handle database viewing"""
        try:
            brands = await self.db.get_all_brands(limit=10)
            
            if not brands:
                text = "📊 **Database is empty**\n\nNo brands found. Start by scraping some beauty brands first!"
            else:
                text = "📊 **Recent Beauty Brands**\n\n"
                for brand in brands:
                    text += format_brand_info(brand)
                    text += "\n" + "─" * 30 + "\n"
        
        except Exception as e:
            text = f"❌ **Database Error**\n\nCouldn't fetch data: {str(e)}"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="view_database")],
            [InlineKeyboardButton("📊 Export CSV", callback_data="export_csv")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def handle_help(self, query):
        """Handle help command"""
        help_text = """
❓ **Beauty Brand AI Agent Help**

**Commands:**
• `/start` - Show main menu
• `/help` - Show this help message
• `/status` - Check bot status

**Features:**
1. **🔍 Brand Scraping**: AI-powered web scraping of Indonesian beauty brands
2. **📞 Contact Finding**: Extract WhatsApp numbers and emails
3. **📱 WhatsApp Automation**: Send automated messages
4. **📊 Database Management**: Store and manage brand data

**Setup Requirements:**
1. Get Telegram Bot Token from @BotFather
2. Get OpenAI API key for AI features
3. Install WhatsApp Web for automation
4. Configure environment variables

**Support:**
For technical support or feature requests, contact the developer.
        """
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages based on user session state"""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        if user_id not in self.user_sessions:
            await update.message.reply_text("Please start with /start command")
            return
        
        session = self.user_sessions[user_id]
        stage = session.get("stage", "menu")
        
        if stage == "finding_contacts":
            await self.process_contact_search(update, message_text)
        elif stage == "whatsapp_outreach":
            await self.process_whatsapp_message(update, message_text)
        else:
            await update.message.reply_text("Please use the menu buttons or /start command")
    
    async def process_contact_search(self, update: Update, query: str):
        """Process contact search request"""
        await update.message.reply_text("🔍 Searching for contact information... Please wait.")
        
        try:
            # Use AI agent to find contacts
            results = await self.contact_agent.find_contacts(query)
            
            if results:
                response = "📞 **Contact Information Found:**\n\n"
                for result in results:
                    response += format_brand_info(result)
                    response += "\n" + "─" * 30 + "\n"
                
                # Save to database
                await self.db.save_brand(results[0])
                
            else:
                response = "❌ No contact information found for the given query."
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in contact search: {e}")
            await update.message.reply_text(f"❌ Error occurred during search: {str(e)}")
    
    async def process_whatsapp_message(self, update: Update, message: str):
        """Process WhatsApp message request"""
        await update.message.reply_text("📱 Preparing WhatsApp message... Please wait.")
        
        try:
            # Parse message format: "phone_number|message"
            if "|" in message:
                phone, text = message.split("|", 1)
                phone = phone.strip()
                text = text.strip()
                
                if validate_phone_number(phone):
                    success = await self.whatsapp_agent.send_message(phone, text)
                    
                    if success:
                        await update.message.reply_text("✅ WhatsApp message sent successfully!")
                    else:
                        await update.message.reply_text("❌ Failed to send WhatsApp message. Check your setup.")
                else:
                    await update.message.reply_text("❌ Invalid phone number format. Use international format (+62xxx)")
            else:
                await update.message.reply_text(
                    "📱 **WhatsApp Message Format:**\n\n"
                    "Send: `phone_number|your_message`\n\n"
                    "Example: `+6281234567890|Hello, I'm interested in your beauty products!`",
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"Error in WhatsApp messaging: {e}")
            await update.message.reply_text(f"❌ Error occurred: {str(e)}")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update.message:
            await update.message.reply_text("❌ An error occurred. Please try again or contact support.")
    
    def run(self):
        """Run the bot"""
        if not self.token:
            logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
            return
        
        # Create application
        application = Application.builder().token(self.token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", lambda u, c: self.handle_help(u.callback_query)))
        application.add_handler(CallbackQueryHandler(self.button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Add error handler
        application.add_error_handler(self.error_handler)
        
        # Start the bot
        logger.info("Starting Beauty Brand AI Agent Bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = BeautyBotAgent()
    bot.run()