#!/bin/bash

echo "🚀 Setting up Skydiving Safety Agent environment..."

# 1. Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment (venv)..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists."
fi

# 2. Activate virtual environment
source venv/bin/activate

# 3. Upgrade pip and install requirements
echo "📥 Installing dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating a template .env file..."
    cat <<EOT > .env
GEMINI_API_KEY=your_gemini_api_key_here
OPEN_METEO_BASE_URL=https://api.open-meteo.com/v1/forecast
GEOCODING_BASE_URL=https://geocoding-api.open-meteo.com/v1/search
EOT
    echo "🔑 Please edit the '.env' file and add your GEMINI_API_KEY."
else
    echo "✅ .env file found."
fi

echo ""
echo "🎉 Setup complete!"
echo "To activate the environment and run the agent:"
echo "  source venv/bin/activate"
echo "  python agent.py -i"