# 🤖 Beauty Brand AI Agent Telegram Bot

A powerful Telegram bot with AI agent capabilities for scraping Indonesian beauty brands (UMKM focus), finding contact information, and automating WhatsApp outreach.

## 🌟 Features

### 🔍 AI-Powered Brand Scraping
- Scrape Indonesian beauty brands with focus on UMKM (micro, small, medium enterprises)
- Intelligent categorization of business sizes
- Extract comprehensive brand information including:
  - Company names and websites
  - Product categories
  - Business locations
  - Contact information

### 📞 Contact Information Extraction
- Find WhatsApp numbers with high accuracy
- Extract email addresses
- Discover social media profiles
- Validate all contact information
- Support for Indonesian phone number formats

### 📱 WhatsApp Automation
- Send automated WhatsApp messages
- Bulk messaging capabilities
- Message templates for different purposes
- WhatsApp Web integration
- Rate limiting to avoid blocks

### 🗄️ Database Management
- SQLite database for storing brand data
- Contact management and validation
- Outreach logging and tracking
- Data export to CSV
- Statistics and analytics

### 🤖 AI Agent Integration
- CrewAI framework integration
- LangChain for advanced NLP
- OpenAI GPT integration
- Intelligent search and analysis
- Context-aware responses

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Chrome browser (for WhatsApp automation)
- Telegram Bot Token
- OpenAI API Key (optional but recommended)
- SerpAPI Key (optional for enhanced search)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd telegram-bot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your configuration:
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   OPENAI_API_KEY=your_openai_key_here
   SERPAPI_KEY=your_serpapi_key_here  # Optional
   ```

4. **Get a Telegram Bot Token:**
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Create a new bot with `/newbot`
   - Copy the token to your `.env` file

5. **Run the bot:**
   ```bash
   python main.py
   ```

## 🛠️ Configuration

### Required API Keys

1. **Telegram Bot Token** (Required)
   - Get from [@BotFather](https://t.me/botfather)

2. **OpenAI API Key** (Recommended)
   - Sign up at [OpenAI](https://platform.openai.com/)
   - Enables advanced AI features

3. **SerpAPI Key** (Optional)
   - Sign up at [SerpAPI](https://serpapi.com/)
   - Enhances Google search capabilities

### Environment Variables

```env
# Required
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# AI Features (Recommended)
OPENAI_API_KEY=your_openai_api_key

# Enhanced Search (Optional)
SERPAPI_KEY=your_serpapi_key

# WhatsApp Configuration
WHATSAPP_SEND_DELAY=10

# Scraping Settings
SCRAPING_DELAY=2
MAX_RESULTS_PER_SEARCH=50
USER_AGENT=Mozilla/5.0...

# AI Settings
MAX_ITERATIONS=5
TEMPERATURE=0.7
```

## 📱 Usage Guide

### Starting the Bot

1. Start a conversation with your bot on Telegram
2. Send `/start` to see the main menu
3. Use the interactive buttons to navigate features

### Main Features

#### 🔍 Brand Scraping
- **Medium Companies**: Established beauty brands
- **Small/UMKM**: Micro, small & medium enterprises  
- **All Beauty Brands**: Comprehensive search

The AI agent will search for Indonesian beauty brands and extract:
- Company information
- Contact details
- Business categorization
- Social media presence

#### 📞 Contact Finding
- Send a brand name or website URL
- AI will find WhatsApp numbers, emails, and social media
- All contacts are validated and verified
- Results are saved to the database

#### 📱 WhatsApp Outreach
- **Single Messages**: Send individual messages
- **Bulk Messages**: Send to multiple contacts from database
- **Message Templates**: Pre-built templates for different purposes

Format for single messages:
```
+6281234567890|Hello, I'm interested in your beauty products!
```

#### 📊 Database Management
- View stored brands
- Export data to CSV
- Track outreach attempts
- View statistics and analytics

### WhatsApp Setup

For WhatsApp automation to work:

1. **Install Chrome browser**
2. **First time setup:**
   - The bot will open WhatsApp Web
   - Scan the QR code with your phone
   - Keep the session logged in

3. **Message Templates:**
   - `introduction`: General inquiry template
   - `collaboration`: Business partnership template
   - `customer_inquiry`: Customer interest template

## 🏗️ Project Structure

```
telegram-bot/
├── main.py                 # Main bot application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── README.md              # This file
├── agents/                # AI agent modules
│   ├── __init__.py
│   ├── beauty_scraper_agent.py    # Brand scraping logic
│   ├── contact_finder_agent.py    # Contact extraction
│   └── whatsapp_agent.py          # WhatsApp automation
├── utils/                 # Utility modules
│   ├── __init__.py
│   ├── database.py        # Database management
│   └── helpers.py         # Helper functions
└── beauty_brands.db       # SQLite database (auto-created)
```

## 🧠 AI Agent Capabilities

### Beauty Scraper Agent
- Intelligent search query generation
- Multi-source data aggregation
- Business size categorization
- Contact information extraction
- Data validation and cleaning

### Contact Finder Agent
- Advanced contact discovery
- Phone number validation (Indonesian formats)
- Email address verification
- Social media profile detection
- Multi-platform search integration

### WhatsApp Agent
- Web automation using Selenium
- Alternative pywhatkit integration
- Template message generation
- Bulk messaging with rate limiting
- Session management

## 📊 Database Schema

### Tables
- **brands**: Core brand information
- **contacts**: Normalized contact data
- **outreach_log**: Message tracking
- **search_history**: Search analytics

### Key Features
- Automatic deduplication
- Contact validation
- Outreach tracking
- Export capabilities

## 🔧 Advanced Configuration

### Custom Search Queries
Modify search queries in `beauty_scraper_agent.py`:
```python
def _build_search_queries(self, category: str) -> List[str]:
    # Add your custom search terms here
    base_queries = [
        "your custom search terms",
        # ... existing queries
    ]
```

### Message Templates
Customize templates in `whatsapp_agent.py`:
```python
def create_message_template(self, template_name: str, brand_info: Dict[str, Any]) -> str:
    templates = {
        'your_template': f"""
        Your custom message template here
        Brand: {brand_info.get('name')}
        """,
        # ... existing templates
    }
```

## 🐛 Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check Telegram Bot Token
   - Verify internet connection
   - Check bot logs for errors

2. **WhatsApp automation failing**
   - Ensure Chrome is installed
   - Check if WhatsApp Web is logged in
   - Verify phone number format (+62xxx)

3. **AI features not working**
   - Verify OpenAI API key
   - Check API usage limits
   - Ensure sufficient credits

4. **Search not finding results**
   - Try different search terms
   - Check internet connection
   - Verify SerpAPI key (if using)

### Error Messages

- `TELEGRAM_BOT_TOKEN not found`: Add token to `.env` file
- `WhatsApp Web requires QR code scan`: Scan QR code in browser
- `Invalid phone number format`: Use +62xxx format for Indonesian numbers
- `OpenAI API error`: Check API key and usage limits

## 📈 Performance Tips

1. **Optimize Search Queries**
   - Use specific Indonesian terms
   - Include location keywords
   - Target UMKM-specific phrases

2. **WhatsApp Best Practices**
   - Use delays between messages (30+ seconds)
   - Avoid sending too many messages per hour
   - Use personalized message templates

3. **Database Maintenance**
   - Regular cleanup of old data
   - Export important data periodically
   - Monitor database size

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational and business purposes. Please ensure compliance with:
- Telegram Bot API Terms
- WhatsApp Business Terms
- OpenAI Usage Policies
- Indonesian data protection laws

## 🆘 Support

For support or questions:
1. Check this README
2. Review error logs
3. Test with simple examples first
4. Ensure all API keys are valid

## 🔄 Updates

The bot includes automatic features for:
- Database schema updates
- New search capabilities
- Enhanced AI prompts
- Improved contact validation

Stay updated with the latest Indonesian beauty brand trends and UMKM business patterns!

---

**⚠️ Important Notes:**
- Always respect website terms of service when scraping
- Use WhatsApp automation responsibly
- Verify contact information before outreach
- Follow Indonesian business communication norms
- Keep API keys secure and never share them