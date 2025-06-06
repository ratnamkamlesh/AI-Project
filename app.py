import time
import traceback
import streamlit as st
from auth import authenticate, register
from storage import save_query, get_query_history
from data.file_handler import load_file_data, suggest_questions  # You create this
from db.db_connector import DatabaseConnector  # Updated import
from chatbot.agent import create_agent_for_dataframe_sheets, rephrase_prompts  # You create this
import logging
try:
    # Session state for login
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None

    # ----------------------------
    # LOGIN / REGISTER SECTION
    # ----------------------------
    if not st.session_state.logged_in:
        st.title("Login / Register")
        mode = st.radio("Select Mode", ["Login", "Register"])
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if mode == "Login":
            if st.button("Login"):
                if authenticate(username, password):
                    st.success("Logged in successfully!")
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        else:
            if st.button("Register"):
                if register(username, password):
                    st.success("User registered. You can now login.")
                else:
                    st.warning("Username already exists.")
        st.stop()

    # ----------------------------
    # MAIN APP SECTION
    # ----------------------------
    st.sidebar.title(f"Welcome, {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

    st.title("📊 Data Assistant with LLM")

    # ----------------------------
    # DATA SELECTION SECTION
    # ----------------------------
    source = st.radio("Choose data source:", ["Upload File", "Database"])

    dataframes = []

    if source == "Upload File":
        uploaded_files = st.file_uploader("Upload CSV or Excel file(s)", type=["csv", "xlsx"], accept_multiple_files=True)
        if uploaded_files:
            for file in uploaded_files:
                sheets = load_file_data(file)  # returns dict of sheet_name: dataframe
                for name, df in sheets.items():
                    st.write(f"### 📄 Sheet: {name}")
                    st.dataframe(df)
                    if st.checkbox(f"🔍 Generate summary for {name}?", key=f"summary_{name}"):
                        summary = create_agent_for_dataframe_sheets([(name, df, [])], "Give a short summary of this dataset.")
                        st.info(f"🧠 **Analysis of {name}**:\n\n{summary}")
                    suggested_questions_df = suggest_questions(df)
                    suggested_questions_df = rephrase_prompts(suggested_questions_df)
                    dataframes.append((name, df,suggested_questions_df))

    elif source == "Database":
        st.subheader("🗄️ Database Configuration")
        
        # Initialize session state for database connection
        if "db_connector" not in st.session_state:
            st.session_state.db_connector = None
        if "db_connected" not in st.session_state:
            st.session_state.db_connected = False

        # Database connection form
        with st.expander("Database Connection Settings", expanded=not st.session_state.db_connected):
            col1, col2 = st.columns(2)
            
            with col1:
                db_type = st.selectbox(
                    "Database Type", 
                    ["MySQL", "PostgreSQL", "MongoDB", "SQLite"],
                    help="Select your database type"
                )
                host = st.text_input(
                    "Host", 
                    value="localhost",
                    help="Database server hostname or IP address"
                )
                port = st.number_input(
                    "Port", 
                    value=3306 if db_type == "MySQL" else 5432 if db_type == "PostgreSQL" else 27017 if db_type == "MongoDB" else 0,
                    min_value=0,
                    max_value=65535,
                    help="Database server port number"
                )
            
            with col2:
                username = st.text_input(
                    "Username",
                    help="Database username"
                )
                password = st.text_input(
                    "Password", 
                    type="password",
                    help="Database password"
                )
                if db_type != "SQLite":
                    database = st.text_input(
                        "Database Name (optional)",
                        help="Leave empty to browse available databases"
                    )
                else:
                    database = st.text_input(
                        "Database File Path",
                        placeholder="/path/to/your/database.db",
                        help="Full path to SQLite database file"
                    )

            # Test Connection Button
            if st.button("🔌 Test Connection", type="primary"):
                if not host or (db_type != "SQLite" and not username):
                    st.error("Please fill in required fields (Host, Username)")
                else:
                    with st.spinner("Testing database connection..."):
                        try:
                            # For SQLite, use database path as host
                            if db_type == "SQLite":
                                connector = DatabaseConnector(db_type.lower(), database, 0, "", "", "")
                            else:
                                connector = DatabaseConnector(db_type.lower(), host, port, username, password, database)
                            
                            result = connector.test_connection()
                            
                            if result["success"]:
                                st.success(f"✅ {result['message']}")
                                st.session_state.db_connector = connector
                                st.session_state.db_connected = True
                                st.rerun()
                            else:
                                st.error(f"❌ Connection failed: {result['error']}")
                                if "traceback" in result:
                                    with st.expander("Error Details"):
                                        st.code(result["traceback"])
                        except Exception as e:
                            st.error(f"❌ Connection error: {str(e)}")

        # If connected, show database exploration
        if st.session_state.db_connected and st.session_state.db_connector:
            connector = st.session_state.db_connector
            
            st.success("🟢 Database Connected!")
            
            # Disconnect button
            if st.button("🔌 Disconnect", type="secondary"):
                st.session_state.db_connector = None
                st.session_state.db_connected = False
                st.rerun()

            # Get databases
            try:
                available_dbs = connector.get_databases()
                if available_dbs:
                    selected_db = st.selectbox("📁 Select Database", available_dbs)
                    
                    if selected_db:
                        # Get tables from selected database
                        tables = connector.get_tables(selected_db)
                        if tables:
                            selected_tables = st.multiselect(
                                "📊 Select Tables/Collections", 
                                tables,
                                help="Choose which tables to analyze"
                            )
                            
                            # Load selected tables
                            for table in selected_tables:
                                with st.spinner(f"Loading {table}..."):
                                    try:
                                        df = connector.fetch_data(table, selected_db)
                                        if not df.empty:
                                            st.write(f"### 🧮 Table: {table}")
                                            st.dataframe(df.head(100))  # Show first 100 rows
                                            st.info(f"📊 Shape: {df.shape[0]} rows × {df.shape[1]} columns")
                                            
                                            # Generate summary
                                            if st.checkbox(f"🔍 Generate summary for {table}?", key=f"db_summary_{table}"):
                                                summary = create_agent_for_dataframe_sheets([(table, df, [])], "Give a short summary of this dataset.")
                                                st.info(f"🧠 **Analysis of {table}**:\n\n{summary}")
                                            
                                            # Generate suggested questions
                                            suggested_questions_df = suggest_questions(df)
                                            suggested_questions_df = rephrase_prompts(suggested_questions_df)
                                            dataframes.append((table, df, suggested_questions_df))
                                        else:
                                            st.warning(f"Table {table} is empty or could not be loaded")
                                    except Exception as e:
                                        st.error(f"Error loading table {table}: {str(e)}")
                        else:
                            st.warning("No tables found in the selected database")
                else:
                    st.warning("No databases found or unable to retrieve database list")
            except Exception as e:
                st.error(f"Database error: {str(e)}")
                st.session_state.db_connected = False

        # Custom Query Section
        if st.session_state.db_connected and st.session_state.db_connector:
            st.subheader("📝 Custom Query")
            custom_query = st.text_area(
                "Enter SQL Query",
                placeholder="SELECT * FROM your_table WHERE condition = 'value'",
                help="Write your custom SQL query here"
            )
            
            if st.button("🚀 Execute Query") and custom_query.strip():
                with st.spinner("Executing query..."):
                    try:
                        df = st.session_state.db_connector.fetch_data(custom_query, selected_db if 'selected_db' in locals() else None)
                        if not df.empty:
                            st.success("Query executed successfully!")
                            st.dataframe(df)
                            st.info(f"📊 Result: {df.shape[0]} rows × {df.shape[1]} columns")
                            
                            # Add to dataframes for analysis
                            suggested_questions_df = suggest_questions(df)
                            dataframes.append(("Custom Query", df, suggested_questions_df))
                        else:
                            st.warning("Query returned no results")
                    except Exception as e:
                        st.error(f"Query execution failed: {str(e)}")

    # ----------------------------
    # QUESTION-ANSWER SECTION
    # ----------------------------
    if dataframes:
        all_suggestions = []
        for name, _, suggestions in dataframes:
            if suggestions:
                all_suggestions.extend([f"[{name}] {q}" for q in suggestions])

        selected_suggestion = None
        if all_suggestions:
            st.write("💡 Suggested Questions:")
            for sug in all_suggestions:
                if st.button(sug, key=sug):
                    st.session_state['question'] = sug
                    st.session_state['trigger_ask'] = True
                    st.rerun()

        question = st.text_input(
            "❓ Ask a question about the data", 
            value=st.session_state.get('question', '')  # <-- use session_state['question'] here
        )
        if st.button("Ask") or  st.session_state.get("trigger_ask", False) :
            try:
                print("sdhvhbbbb")
                start_time = time.time()  # ⏱️ Start timer
                print("question:", question)
                response = create_agent_for_dataframe_sheets(dataframes, question)
                print("response:", response)
                end_time = time.time()  # ⏱️ End timer
                response_time = round(end_time - start_time, 2)  # In seconds
                st.success("Answer:")
                st.write(response)
                save_query(st.session_state.username, question, response,response_time)
            except Exception as e:
                st.error(f"Error: {e}")

    # ----------------------------
    # HISTORY SECTION
    # ----------------------------
    if st.sidebar.checkbox("🕓 Show previous queries"):
        history = get_query_history(st.session_state.username)
        for item in reversed(history):
            st.markdown(f"**Q:** {item['query']}")
            st.markdown(f"**A:** {item['response']}")
            if "response_time" in item:
                st.markdown(f"⏱️ **Response Time:** {item['response_time']} seconds")
except Exception as e:
    logging.error(f"An error occurred: {e}")
    logging.exception("An error occurred in the Streamlit app.")
    logging.error("Traceback - {}".format(e, traceback.format_exc()))
    st.error(f"An error occurred: {e}")
    if st.session_state.logged_in:
        st.warning("Please try again or contact support if the issue persists.")
    