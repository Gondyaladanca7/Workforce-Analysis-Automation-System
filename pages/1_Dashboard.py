# Dashboard Page
"""
Dashboard — Workforce Analytics System
Displays key metrics, charts, and quick summaries.
Integrates with utils.database and utils.analytics.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import database as db
from utils.analytics import get_summary, department_distribution, gender_ratio, average_salary_by_dept

# -------------------------
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("📊 Workforce Dashboard")

# -------------------------
# Load employee data
try:
    df = db.fetch_employees()
except Exception as e:
    st.error("Failed to fetch employee data from database.")
    st.exception(e)
    df = pd.DataFrame(columns=[
        "Emp_ID","Name","Age","Gender","Department","Role",
        "Skills","Join_Date","Resign_Date","Status","Salary","Location"
    ])

# -------------------------
# Summary Cards
st.header("1️⃣ Key Metrics")
try:
    total, active, resigned = get_summary(df) if not df.empty else (0,0,0)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Employees", total)
    col2.metric("Active Employees", active)
    col3.metric("Resigned Employees", resigned)
except Exception as e:
    st.error("Error computing summary metrics.")
    st.exception(e)

# -------------------------
# Department-wise Distribution
st.header("2️⃣ Department Distribution")
try:
    if not df.empty and "Department" in df.columns:
        dept_counts = department_distribution(df)
        st.bar_chart(dept_counts)
    else:
        st.info("No 'Department' data available.")
except Exception as e:
    st.error("Error plotting department distribution.")
    st.exception(e)

# -------------------------
# Skill Inventory & Role Mapping (Feature 2)
st.header("3️⃣ Skill Inventory & Role Mapping")

try:
    if not df.empty:
        # Extract all skills
        skill_list = []
        if "Skills" in df.columns:
            for s in df["Skills"].dropna():
                skill_list.extend([skill.strip() for skill in s.split(";") if skill.strip()])

        if skill_list:
            skill_counts = pd.Series(skill_list).value_counts()
            st.subheader("🔹 Skill Distribution")
            st.bar_chart(skill_counts)

        # Role mapping
        if "Role" in df.columns:
            role_counts = df["Role"].value_counts()
            st.subheader("🔹 Role Mapping")
            st.bar_chart(role_counts)
        else:
            st.info("No 'Role' column found.")
    else:
        st.info("No employee data to display Skill Inventory or Role Mapping.")
except Exception as e:
    st.error("Error generating Skill Inventory or Role Mapping charts.")
    st.exception(e)

# -------------------------
# Gender Ratio
st.header("4️⃣ Gender Ratio")
try:
    if not df.empty and "Gender" in df.columns:
        gender_counts = gender_ratio(df)
        fig, ax = plt.subplots()
        ax.pie(gender_counts, labels=gender_counts.index, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)
    else:
        st.info("No 'Gender' data available.")
except Exception as e:
    st.error("Error creating gender ratio chart.")
    st.exception(e)

# -------------------------
# Average Salary by Department
st.header("5️⃣ Average Salary by Department")
try:
    if not df.empty and "Department" in df.columns and "Salary" in df.columns:
        avg_salary = average_salary_by_dept(df)
        st.bar_chart(avg_salary)
    else:
        st.info("No 'Department' or 'Salary' data available.")
except Exception as e:
    st.error("Error plotting average salary by department.")
    st.exception(e)

# -------------------------
# Recent Employees Table
st.header("6️⃣ Recent Employees")
try:
    if not df.empty:
        recent_df = df.sort_values(by="Join_Date", ascending=False).head(10)
        st.dataframe(recent_df[["Emp_ID","Name","Department","Role","Join_Date","Status"]])
    else:
        st.info("No employee data to display.")
except Exception as e:
    st.error("Error displaying recent employees.")
    st.exception(e)
