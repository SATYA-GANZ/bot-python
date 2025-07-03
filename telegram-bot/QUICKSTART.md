# 🚀 Quick Start Guide

## 📁 What's Been Created

You now have a complete **Telegram Bot with AI Agent functionality** for scraping Indonesian beauty brands (UMKM focus) and automating WhatsApp outreach.

### 🏗️ Project Structure
```
telegram-bot/
├── 🤖 main.py                     # Main Telegram bot
├── 📋 requirements.txt            # Dependencies 
├── ⚙️ .env.example               # Environment template
├── 📚 README.md                  # Full documentation
├── 🧪 test_bot.py                # Test suite
├── 🔧 setup.sh                   # Auto setup script
├── ▶️ run.sh                     # Easy run script
├── 🤖 agents/                    # AI Agent modules
│   ├── beauty_scraper_agent.py   # Brand scraping
│   ├── contact_finder_agent.py   # Contact extraction  
│   └── whatsapp_agent.py         # WhatsApp automation
└── 🔧 utils/                     # Utility modules
    ├── database.py               # Data management
    └── helpers.py                # Helper functions
```

## ⚡ 3-Step Setup

### 1️⃣ Run Setup Script
```bash
cd telegram-bot
./setup.sh
```
This will:
- Create virtual environment
- Install all dependencies  
- Create `.env` file
- Run tests

### 2️⃣ Configure API Keys
Edit `.env` file:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENAI_API_KEY=your_openai_key_here      # Optional but recommended
SERPAPI_KEY=your_serpapi_key_here        # Optional
```

**Get Telegram Bot Token:**
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` 
3. Follow instructions
4. Copy token to `.env`

### 3️⃣ Start the Bot
```bash
./run.sh
```

## 🎯 Core Features

### 🔍 **Brand Scraping**
- Find Indonesian beauty brands
- Focus on UMKM (small/medium businesses)
- Extract company info, contacts, websites
- AI-powered categorization

### 📞 **Contact Discovery** 
- Find WhatsApp numbers (Indonesian format)
- Extract email addresses
- Discover social media profiles
- Validate all contact information

### 📱 **WhatsApp Automation**
- Send automated messages
- Bulk messaging capabilities
- Message templates in Indonesian
- WhatsApp Web integration

### 🗄️ **Data Management**
- SQLite database storage
- Export to CSV
- Outreach tracking
- Analytics and statistics

## 📱 Bot Commands

Start chat with your bot and use:

- `/start` - Main menu
- **🔍 Scrape Beauty Brands** - Find Indonesian beauty companies
- **📞 Find Contacts** - Extract contact info from brands/URLs
- **📱 WhatsApp Outreach** - Send automated messages
- **📊 View Database** - See collected data

## 🛠️ Usage Examples

### Finding Contacts
Send to bot: `Wardah cosmetics` or `https://wardahbeauty.com`
Bot will find: WhatsApp, emails, social media

### WhatsApp Messages
Send: `+6281234567890|Halo! Saya tertarik dengan produk kecantikan Anda.`

### Brand Scraping
Choose scraping type:
- **Medium Companies**: Established brands
- **Small/UMKM**: Micro/small businesses
- **All**: Comprehensive search

## 🔧 Advanced Configuration

### Custom Search Terms
Edit `agents/beauty_scraper_agent.py`:
```python
base_queries = [
    "brand kecantikan Indonesia UMKM",
    "your custom terms here",
    # Add more Indonesian beauty terms
]
```

### Message Templates
Edit `agents/whatsapp_agent.py`:
```python
templates = {
    'introduction': f"""
Halo {brand_name}! 👋
Saya tertarik dengan produk kecantikan Anda...
    """,
    # Add custom templates
}
```

## 🐛 Troubleshooting

### Bot Not Starting
- Check `TELEGRAM_BOT_TOKEN` in `.env`
- Run `./setup.sh` again
- Check internet connection

### WhatsApp Not Working
- Install Chrome browser
- Scan QR code on first run
- Use format: `+62xxx` for Indonesian numbers

### No Search Results
- Try Indonesian terms: "kosmetik", "kecantikan", "UMKM"
- Check internet connection
- Add OpenAI API key for better results

## 🎯 Quick Tips

### For Best Results:
1. **Use Indonesian search terms**: "skincare lokal", "kosmetik halal", "UMKM kecantikan"
2. **Target specific locations**: "Jakarta", "Surabaya", "Bandung"  
3. **Include business size**: "UMKM", "small business", "startup"

### WhatsApp Best Practices:
1. **Personalize messages** for each brand
2. **Wait 30+ seconds** between messages
3. **Use polite Indonesian** language
4. **Respect business hours**

### Database Management:
- Export data regularly: Use **📊 Export CSV** 
- Clean old data: Bot auto-manages
- Backup important contacts

## 🔄 Regular Maintenance

### Weekly:
- Export contact database
- Review outreach results
- Update search terms

### Monthly:  
- Clean old data
- Review and improve message templates
- Check for new UMKM directories

## 📈 Scaling Up

### For High Volume:
1. Add multiple Telegram bots
2. Use proxy for WhatsApp Web
3. Implement rate limiting
4. Add team member access

### Enhanced AI:
1. Upgrade OpenAI plan
2. Add SerpAPI for better search
3. Train custom models on Indonesian data
4. Add NLP for response analysis

## 🆘 Support

### If You Need Help:
1. Check `README.md` for full docs
2. Run `python test_bot.py` for diagnostics
3. Check logs in terminal
4. Verify all API keys are valid

### Common Solutions:
- **Module not found**: Run `./setup.sh`
- **Permission denied**: Run `chmod +x *.sh`
- **WhatsApp fails**: Check Chrome installation
- **No results**: Try different search terms

---

## 🎉 You're Ready!

Your AI-powered beauty brand scraping and outreach bot is ready! 

Focus on Indonesian UMKM beauty brands and build meaningful business relationships through automated but personalized outreach.

**Happy brand hunting! 🚀✨**