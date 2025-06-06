#!/bin/bash

set -e

echo "📁 Creating project folder structure..."

mkdir -p chatbot data dashboard prompts db utils

# Create empty or stub files
touch app.py
touch chatbot/agent.py
touch dashboard/dashboard_utils.py
touch data/sample.csv
touch prompts/prompt_templates.py
touch db/db_connector.py
touch utils/helpers.py
touch README.md


echo "✅ Folder structure and files created."

echo ""
echo "📝 Next steps:"
echo "1. Open 'app.py' and start building your Streamlit dashboard."
echo "2. Use 'chatbot/agent.py' for LLM chatbot logic."
echo "3. Add your data to 'data/sample.csv' or load dynamically."
