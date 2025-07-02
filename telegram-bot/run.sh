#!/bin/bash

# Beauty Brand AI Agent Bot - Run Script

echo "🤖 Starting Beauty Brand AI Agent Bot..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure your API keys"
    exit 1
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Check if TELEGRAM_BOT_TOKEN is configured
if ! grep -q "^TELEGRAM_BOT_TOKEN=.*[^=]" .env; then
    echo "⚠️  TELEGRAM_BOT_TOKEN not configured in .env file"
    echo "Please add your Telegram Bot Token to .env file"
    echo "Get a token from @BotFather on Telegram"
    exit 1
fi

echo "✅ Environment configured"
echo "🚀 Starting the bot..."
echo ""
echo "Press Ctrl+C to stop the bot"
echo ""

# Run the bot
python main.py