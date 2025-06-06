import pandas as pd
from typing import Dict

def load_file_data(uploaded_file):
    """
    Loads data from an uploaded file.
    Supports .csv and .xlsx.
    Returns a dict of {sheet_name: dataframe} to maintain consistency.
    """
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        return {"Sheet1": df}

    elif uploaded_file.name.endswith(".xlsx"):
        xls = pd.ExcelFile(uploaded_file)
        return {sheet: xls.parse(sheet) for sheet in xls.sheet_names}

    else:
        raise ValueError("Unsupported file format. Please upload .csv or .xlsx.")



import pandas as pd

def suggest_questions(df: pd.DataFrame, max_suggestions: int = 3) -> list:
    suggestions = []

    # Drop columns with too many missing values
    df = df.dropna(axis=1, thresh=len(df) * 0.7)

    # Detect types
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    datetime_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

    # Rank numeric by variance
    if numeric_cols:
        numeric_variance = df[numeric_cols].var().sort_values(ascending=False)
        top_numeric = numeric_variance.index.tolist()
    else:
        top_numeric = []

    # Rank categorical by number of unique values (but not too many)
    if categorical_cols:
        cat_unique_counts = df[categorical_cols].nunique()
        top_categoricals = cat_unique_counts[(cat_unique_counts > 1) & (cat_unique_counts < 50)].sort_values().index.tolist()
    else:
        top_categoricals = []

    # 1. Best numeric correlation
    if len(top_numeric) >= 2:
        corr_matrix = df[top_numeric].corr().abs()
        corr_matrix.values[[range(len(corr_matrix))]*2] = 0  # remove diagonal
        max_corr = corr_matrix.stack().idxmax()
        suggestions.append(f"How does '{max_corr[0]}' relate to '{max_corr[1]}'?")

    # 2. Best numeric + category combo
    if top_numeric and top_categoricals:
        suggestions.append(f"What is the average '{top_numeric[0]}' per '{top_categoricals[0]}'?")
        suggestions.append(f"Which '{top_categoricals[0]}' has the highest '{top_numeric[0]}'?")

    # 3. Time trends
    if datetime_cols and top_numeric:
        suggestions.append(f"Show the trend of '{top_numeric[0]}' over time using '{datetime_cols[0]}'.")

    # 4. General insight
    suggestions.append("What are the most important columns in this dataset?")
    suggestions.append("How many rows and columns does the dataset contain?")
    suggestions.append("Show the first 5 rows of the dataset.")

    # 5. Column-specific summaries
    for col in top_numeric[:2]:
        suggestions.append(f"What is the distribution and average of '{col}'?")
    for col in top_categoricals[:2]:
        suggestions.append(f"What are the top values in '{col}' and how often do they occur?")

    return suggestions[:max_suggestions]
