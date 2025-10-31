# pages/1_📊_Dashboard.py
"""
📊 Workforce Dashboard
Displays key metrics, charts, and recent employee table.
Improved version with:
- datetime conversion for Join_Date
- safe Series handling for charts
- optional Department filter
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import database as db
from utils.analytics import get_summary, department_distribution, gender_ratio, average_salary_by_dept

# -------------------------
# Page config
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("📊 Workforce Dashboard")

# -------------------------
# Load employee data
try:
    df = db.fetch_employees()
    if not df.empty:
        # Convert Join_Date & Resign_Date to datetime
        df["Join_Date"] = pd.to_datetime(df["Join_Date"], errors="coerce")
        df["Resign_Date"] = pd.to_datetime(df["Resign_Date"], errors="coerce")
except Exception as e:
    st.error("Failed to fetch employee data from database.")
    st.exception(e)
    df = pd.DataFrame(columns=["Emp_ID","Name","Age","Gender","Department","Role",
                               "Skills","Join_Date","Resign_Date","Status","Salary","Location"])

# -------------------------
# Sidebar: Department filter
st.sidebar.header("🔍 Filter by Department")
departments = ["All"] + sorted(df["Department"].dropna().unique().tolist()) if not df.empty else ["All"]
selected_dept = st.sidebar.selectbox("Department", departments)

filtered_df = df.copy()
if selected_dept != "All":
    filtered_df = filtered_df[filtered_df["Department"] == selected_dept]

# -------------------------
# Summary Metrics
st.header("1️⃣ Key Metrics")
try:
    total, active, resigned = get_summary(filtered_df) if not filtered_df.empty else (0,0,0)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Employees", total)
    col2.metric("Active Employees", active)
    col3.metric("Resigned Employees", resigned)
except Exception as e:
    st.error("Error computing summary metrics.")
    st.exception(e)

# -------------------------
# Department Distribution
st.header("2️⃣ Department Distribution")
try:
    if not filtered_df.empty and "Department" in filtered_df.columns:
        dept_counts = department_distribution(filtered_df)
        if not dept_counts.empty:
            st.bar_chart(dept_counts, use_container_width=True)
        else:
            st.info("No department data to display.")
    else:
        st.info("No 'Department' data available.")
except Exception as e:
    st.error("Error plotting department distribution.")
    st.exception(e)

# -------------------------
# Gender Ratio
st.header("3️⃣ Gender Ratio")
try:
    if not filtered_df.empty and "Gender" in filtered_df.columns:
        gender_counts = gender_ratio(filtered_df)
        if not gender_counts.empty:
            fig, ax = plt.subplots()
            ax.pie(gender_counts, labels=gender_counts.index, autopct="%1.1f%%", startangle=90)
            ax.axis("equal")
            st.pyplot(fig)
        else:
            st.info("No gender data to display.")
    else:
        st.info("No 'Gender' data available.")
except Exception as e:
    st.error("Error creating gender ratio chart.")
    st.exception(e)

# -------------------------
# Average Salary by Department
st.header("4️⃣ Average Salary by Department")
try:
    if not filtered_df.empty and "Department" in filtered_df.columns and "Salary" in filtered_df.columns:
        avg_salary = average_salary_by_dept(filtered_df)
        if not avg_salary.empty:
            st.bar_chart(avg_salary, use_container_width=True)
        else:
            st.info("No salary data to display.")
    else:
        st.info("No 'Department' or 'Salary' data available.")
except Exception as e:
    st.error("Error plotting average salary by department.")
    st.exception(e)

# -------------------------
# Recent Employees Table
st.header("5️⃣ Recent Employees")
try:
    if not filtered_df.empty:
        recent_df = filtered_df.sort_values(by="Join_Date", ascending=False).head(10)
        st.dataframe(recent_df[["Emp_ID","Name","Department","Role","Join_Date","Status"]], use_container_width=True)
    else:
        st.info("No employee data to display.")
except Exception as e:
    st.error("Error displaying recent employees.")
    st.exception(e)
