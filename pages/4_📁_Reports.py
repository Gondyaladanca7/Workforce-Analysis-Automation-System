# Reports Page
"""
Reports — Workforce Analytics System
Generate comprehensive reports, visualize key metrics, and export PDF summaries.
Integrates with utils.database and utils.pdf_export.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64
from utils import database as db
from utils.analytics import get_summary, department_distribution, gender_ratio, average_salary_by_dept
from utils.pdf_export import generate_summary_pdf

# -------------------------
st.set_page_config(page_title="Reports", page_icon="📁", layout="wide")
st.title("📁 Workforce Reports & Summary")

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
# Summary Metrics
st.header("1️⃣ Key Metrics Summary")
try:
    total, active, resigned = get_summary(df) if not df.empty else (0, 0, 0)
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
        st.info("No 'Department' data available for chart.")
except Exception as e:
    st.error("Error plotting department distribution.")
    st.exception(e)

# -------------------------
# Gender Ratio
st.header("3️⃣ Gender Ratio")
try:
    if not df.empty and "Gender" in df.columns:
        gender_counts = gender_ratio(df)
        fig, ax = plt.subplots()
        ax.pie(gender_counts, labels=gender_counts.index, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)
    else:
        st.info("No 'Gender' data available for chart.")
except Exception as e:
    st.error("Error plotting gender ratio.")
    st.exception(e)

# -------------------------
# Average Salary by Department
st.header("4️⃣ Average Salary by Department")
try:
    if not df.empty and "Department" in df.columns and "Salary" in df.columns:
        avg_salary = average_salary_by_dept(df)
        st.bar_chart(avg_salary)
    else:
        st.info("No 'Department' or 'Salary' data available for chart.")
except Exception as e:
    st.error("Error plotting average salary by department.")
    st.exception(e)

# -------------------------
# Export Summary PDF
st.header("5️⃣ Export Complete Summary PDF")
st.write("Click the button below to download a professional summary report of your workforce.")

if st.button("📄 Download Summary PDF"):
    try:
        pdf_path = "workforce_summary_report.pdf"
        # ✅ Pass df as 4th argument
        generate_summary_pdf(pdf_path, total, active, resigned, df)
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 Download PDF",
                data=f,
                file_name="workforce_summary_report.pdf",
                mime="application/pdf"
            )
    except Exception as e:
        st.error("Failed to generate PDF.")
        st.exception(e)
