import time
import traceback
import streamlit as st
from auth import authenticate, register
from storage import save_query, get_query_history
from data.file_handler import load_file_data, suggest_questions  # You create this
from db.db_connector import get_databases, get_table_names, fetch_data  # You create this
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
        dbs = get_databases()
        selected_db = st.selectbox("Select a database", dbs)
        if selected_db:
            tables = get_table_names(selected_db)
            selected_tables = st.multiselect("Select tables", tables)
            for tbl in selected_tables:
                df = fetch_data(selected_db, tbl)
                st.write(f"### 🧮 Table: {tbl}")
                st.dataframe(df)
                suggested_questions_df = suggest_questions(df)
                dataframes.append((tbl, df,suggested_questions_df))

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
    