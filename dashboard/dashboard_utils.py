import pandas as pd
import plotly.express as px
import streamlit as st

def load_data(file):
    return pd.read_csv(file)

def generate_dashboard(df):
    st.subheader("📊 Data Overview")
    st.write(df.head())

    # Auto generate simple chart
    numeric_cols = df.select_dtypes(include='number').columns
    if len(numeric_cols) >= 2:
        fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1])
        st.plotly_chart(fig)
