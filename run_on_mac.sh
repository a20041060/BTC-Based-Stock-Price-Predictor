#!/bin/bash

echo "🚀 Setting up BTC Stock Predictor for macOS..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install it using: brew install python"
    exit 1
fi

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies (this may take a few minutes due to AI libraries)..."
pip install -r requirements.txt

# Run the application
echo "📈 Starting BTC Stock Predictor (Streamlit Frontend + Django Backend Logic)..."
echo "✅ The app should open in your default browser automatically."
echo "   If not, visit http://localhost:8501"
streamlit run btc_stock_predictor_ui.py
# python manage.py migrate
# python manage.py runserver 0.0.0.0:8000
