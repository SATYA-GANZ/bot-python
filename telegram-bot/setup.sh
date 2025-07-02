#!/bin/bash

# Beauty Brand AI Agent Bot - Setup Script

echo "🤖 Beauty Brand AI Agent Bot Setup"
echo "=================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Check if virtual environment was created successfully
if [ ! -d "venv" ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

echo "✅ Virtual environment created"

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install some dependencies"
    echo "⚠️  This is normal for some optional packages"
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo "⚠️  Please edit .env file with your API keys"
else
    echo "✅ .env file already exists"
fi

# Run tests
echo "🧪 Running tests..."
python test_bot.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file with your API keys:"
    echo "   - TELEGRAM_BOT_TOKEN (required)"
    echo "   - OPENAI_API_KEY (recommended)"
    echo "   - SERPAPI_KEY (optional)"
    echo ""
    echo "2. To run the bot:"
    echo "   source venv/bin/activate"
    echo "   python main.py"
    echo ""
    echo "3. To get a Telegram Bot Token:"
    echo "   - Message @BotFather on Telegram"
    echo "   - Use /newbot command"
    echo "   - Copy the token to .env file"
else
    echo "⚠️  Some tests failed, but basic setup is complete"
    echo "Please check the test output above for any issues"
fi

echo ""
echo "📚 For more information, see README.md"