#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "🚀 AIvengers Hackathon Project Setup Starting..."

# Step 1: Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Step 2: Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Step 3: Install required packages
echo "📥 Installing required Python packages..."
pip install streamlit pandas plotly matplotlib langchain pymysql psycopg2-binary openai

# Step 3.1: Install additional database drivers
echo "🗄️ Installing additional database drivers..."
pip install pymongo sqlite3

# Optional: FastAPI if needed
read -p "❓ Do you want to install FastAPI? (y/n): " install_fastapi
if [[ "$install_fastapi" == "y" ]]; then
    pip install fastapi uvicorn
fi

# Step 4: Initialize Git (optional)
read -p "❓ Initialize Git repo? (y/n): " init_git
if [[ "$init_git" == "y" ]]; then
    git init
    echo "venv/" > .gitignore
    echo "__pycache__/" >> .gitignore
    echo "*.pyc" >> .gitignore
    echo "*.sqlite3" >> .gitignore
    git add .
    git commit -m "Initial commit"
fi

# Step 5: Done
echo "✅ Setup complete!"

echo ""
echo "👉 Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run Streamlit app: streamlit run app.py"
echo "3. Start coding your dashboard & chatbot logic!"
