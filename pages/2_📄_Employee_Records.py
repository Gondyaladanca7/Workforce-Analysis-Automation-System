# Employee Records Page
"""
Employee Records — Workforce Analytics System
Displays all employee records in a searchable, filterable, and sortable table.
Integrates with utils.database and utils.analytics.
"""

import streamlit as st
import pandas as pd
from utils import database as db

# -------------------------
st.set_page_config(page_title="Employee Records", page_icon="📄", layout="wide")
st.title("📄 Employee Records")

# -------------------------
# Load employee data
try:
    df = db.fetch_employees()
except Exception as e:
    st.error("Failed to fetch employee data from database.")
    st.exception(e)
    df = pd.DataFrame(columns=["Emp_ID","Name","Age","Gender","Department","Role",
                               "Skills","Join_Date","Resign_Date","Status","Salary","Location"])

# -------------------------
# Sidebar Filters
st.sidebar.header("🔍 Filter Employee Data")

def safe_options(df_local, col):
    if col in df_local.columns:
        opts = sorted(df_local[col].dropna().unique().tolist())
        return ["All"] + opts
    return ["All"]

selected_dept = st.sidebar.selectbox("Department", safe_options(df, "Department"))
selected_status = st.sidebar.selectbox("Status", safe_options(df, "Status"))
selected_gender = st.sidebar.selectbox("Gender", safe_options(df, "Gender"))
selected_role = st.sidebar.selectbox("Role", safe_options(df, "Role"))
selected_skills = st.sidebar.selectbox("Skills", safe_options(df, "Skills"))

# Apply filters
filtered_df = df.copy()
if selected_dept != "All":
    filtered_df = filtered_df[filtered_df["Department"] == selected_dept]
if selected_status != "All":
    filtered_df = filtered_df[filtered_df["Status"] == selected_status]
if selected_gender != "All":
    filtered_df = filtered_df[filtered_df["Gender"] == selected_gender]
if selected_role != "All":
    filtered_df = filtered_df[filtered_df["Role"] == selected_role]
if selected_skills != "All":
    filtered_df = filtered_df[filtered_df["Skills"] == selected_skills]

# -------------------------
# Search
st.header("1️⃣ Search Employee Records")
search_term = st.text_input("Search by Name, ID, Skills, or Role").strip()
display_df = filtered_df.copy()

if search_term:
    cond = pd.Series([False]*len(display_df), index=display_df.index)
    for col in ["Name","Emp_ID","Skills","Role"]:
        if col in display_df.columns:
            cond = cond | display_df[col].astype(str).str.contains(search_term, case=False, na=False)
    display_df = display_df[cond]

# -------------------------
# Sorting
available_sort_cols = [c for c in ["Emp_ID","Name","Age","Salary","Join_Date","Department","Role","Skills"] if c in display_df.columns]
if not available_sort_cols:
    available_sort_cols = display_df.columns.tolist()

sort_col = st.selectbox("Sort by", options=available_sort_cols, index=0)
ascending = st.radio("Order", ["Ascending","Descending"], horizontal=True) == "Ascending"

try:
    if sort_col in display_df.columns:
        display_df = display_df.sort_values(by=sort_col, ascending=ascending, key=lambda s: s.astype(str))
except Exception:
    pass

# -------------------------
# Display Table
st.header("2️⃣ Employee Records Table")
try:
    styled = display_df.style.set_properties(**{"background-color":"white","color":"black"})
    st.dataframe(styled, height=500)
except Exception:
    st.dataframe(display_df, height=500)

# -------------------------
# Summary
st.header("3️⃣ Summary Statistics")
try:
    total = len(display_df)
    active = len(display_df[display_df["Status"]=="Active"]) if "Status" in display_df.columns else 0
    resigned = len(display_df[display_df["Status"]=="Resigned"]) if "Status" in display_df.columns else 0
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Employees", total)
    col2.metric("Active Employees", active)
    col3.metric("Resigned Employees", resigned)
except Exception as e:
    st.error("Error computing summary statistics.")
    st.exception(e)
