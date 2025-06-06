# 📊 AIvengers Data Assistant

A powerful Streamlit-based data assistant application that uses Large Language Models (LLMs) to help users analyze and interact with their data through natural language queries.

## 🚀 Features

- **User Authentication**: Secure login and registration system
- **Multi-source Data Support**: 
  - Upload CSV/Excel files
  - Connect to databases (MySQL, PostgreSQL)
- **AI-Powered Analysis**: 
  - Natural language queries on your data
  - Automated data summaries
  - Suggested questions for exploration
- **Query History**: Track your previous questions and responses
- **Response Time Tracking**: Monitor query performance

## 🛠️ Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## 📦 Installation & Setup

### Option 1: Automatic Setup (Recommended)

1. **Clone or download the project**
2. **Run the setup script**:
   ```bash
   chmod +x setup_aivengers_project.sh
   ./setup_aivengers_project.sh
   ```
3. **Follow the prompts** for optional installations (FastAPI, Git initialization)

### Option 2: Manual Setup

1. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Upgrade pip**:
   ```bash
   pip install --upgrade pip
   ```

3. **Install required packages**:
   ```bash
   pip install streamlit pandas plotly matplotlib langchain pymysql psycopg2-binary openai
   ```

## 🏃‍♂️ How to Run

1. **Activate the virtual environment** (if not already activated):
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Start the Streamlit application**:
   ```bash
   streamlit run app.py
   ```

3. **Open your browser** and navigate to the URL shown in the terminal (usually `http://localhost:8501`)

## 📋 Usage Instructions

### First Time Setup
1. **Register a new account** or **login** with existing credentials
   - **Demo Credentials**: You can use `alice` / `password123` for testing
2. **Choose your data source**:
   - **Upload File**: Select CSV or Excel files from your computer
   - **Database**: Connect to your MySQL/PostgreSQL database

### Working with Data
1. **Upload or select your data**
2. **Review the data preview** and optional summaries
3. **Use suggested questions** or **ask custom queries** in natural language
4. **View your query history** in the sidebar

### Example Queries
- "What are the top 5 customers by sales?"
- "Show me the trend of revenue over time"
- "Which product category has the highest profit margin?"
- "Give me insights about customer demographics"

## 📁 Project Structure

```
aivengers/
├── app.py                 # Main Streamlit application
├── auth.py               # User authentication logic
├── storage.py            # Query history storage
├── setup_aivengers_project.sh  # Automated setup script
├── chatbot/              # LLM agent logic
├── data/                 # File handling utilities
├── db/                   # Database connection utilities
├── dashboard/            # Dashboard components
├── prompts/              # LLM prompts and templates
├── utils/                # Utility functions
├── user_data/            # User data storage
└── README.md             # This file
```

## 🔧 Configuration

### Database Configuration
- Configure your database connections in the `db/` directory
- Update connection parameters for your specific database setup

### LLM Configuration
- Set up your OpenAI API key or other LLM provider credentials
- Configure model parameters in the chatbot module

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   streamlit run app.py --server.port 8502
   ```

2. **Missing dependencies**:
   ```bash
   pip install -r requirements.txt  # If requirements.txt exists
   # Or reinstall manually using the setup script
   ```

3. **Database connection issues**:
   - Check your database credentials
   - Ensure your database server is running
   - Verify network connectivity

### Getting Help
- Check the terminal/console for error messages
- Review the Streamlit logs for detailed debugging information
- Ensure all required modules are properly installed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of the AIvengers Hackathon initiative.

---

**Happy Data Analyzing! 🎉**
