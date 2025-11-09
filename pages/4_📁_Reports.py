# Reports.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils import database as db
from utils.analytics import get_summary, department_distribution, average_salary_by_dept
from utils.pdf_export import generate_summary_pdf

sns.set_style("whitegrid")
st.set_page_config(page_title="Reports", page_icon="📁", layout="wide")
st.title("📁 Workforce Reports & Summary")

# -------------------------
# Load employees
# -------------------------
try:
    df = db.fetch_employees()
except:
    df = pd.DataFrame(columns=["Emp_ID","Name","Age","Gender","Department","Role",
                               "Skills","Join_Date","Resign_Date","Status","Salary","Location"])

# -------------------------
# Summary Metrics
# -------------------------
st.header("1️⃣ Key Metrics Summary")
total, active, resigned = get_summary(df) if not df.empty else (0,0,0)
col1, col2, col3 = st.columns(3)
col1.metric("Total Employees", total)
col2.metric("Active Employees", active)
col3.metric("Resigned Employees", resigned)

st.markdown("---")

# -------------------------
# Department Distribution
# -------------------------
st.header("2️⃣ Department Distribution")
if not df.empty and "Department" in df.columns:
    dept_fig, dept_ser = department_distribution(df)
    fig, ax = plt.subplots(figsize=(8,5))
    sns.barplot(x=dept_ser.index, y=dept_ser.values, palette="pastel", ax=ax)
    ax.set_xlabel("Department")
    ax.set_ylabel("Number of Employees")
    ax.set_title("Department-wise Employee Distribution")
    plt.xticks(rotation=45)
    st.pyplot(fig, use_container_width=True)

st.markdown("---")

# -------------------------
# Gender Ratio
# -------------------------
st.header("3️⃣ Gender Ratio")
if not df.empty and "Gender" in df.columns:
    gender_counts = df["Gender"].value_counts().reindex(["Male","Female"], fill_value=0)
    fig, ax = plt.subplots(figsize=(6,6))
    ax.pie(gender_counts.values, labels=gender_counts.index, autopct="%1.1f%%",
           startangle=90, colors=sns.color_palette("pastel"))
    ax.axis("equal")
    ax.set_title("Gender Distribution")
    st.pyplot(fig, use_container_width=True)

st.markdown("---")

# -------------------------
# Average Salary by Department
# -------------------------
st.header("4️⃣ Average Salary by Department")
if not df.empty and "Department" in df.columns and "Salary" in df.columns:
    avg_salary = average_salary_by_dept(df)
    fig, ax = plt.subplots(figsize=(8,5))
    sns.barplot(x=avg_salary.index, y=avg_salary.values, palette="pastel", ax=ax)
    ax.set_xlabel("Department")
    ax.set_ylabel("Average Salary")
    ax.set_title("Average Salary by Department")
    plt.xticks(rotation=45)
    st.pyplot(fig, use_container_width=True)

st.markdown("---")

# -------------------------
# PDF Export
# -------------------------
st.header("5️⃣ Export Summary PDF")
if st.button("📄 Download Summary PDF"):
    pdf_path = "workforce_summary_report.pdf"
    generate_summary_pdf(pdf_path, total, active, resigned, df)
    with open(pdf_path,"rb") as f:
        st.download_button("📥 Download PDF", f, file_name="workforce_summary_report.pdf", mime="application/pdf")
