#!/bin/bash
# Setup script for Freight Intelligence Portal

echo "🚛 Setting up Freight Intelligence Portal..."

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Initialize database
echo "🗄️  Initializing database..."
python lib/database.py

# Create .streamlit config directory
mkdir -p .streamlit

echo "✅ Setup complete!"
echo ""
echo "To run the portal:"
echo "  source venv/bin/activate"
echo "  streamlit run app.py"
