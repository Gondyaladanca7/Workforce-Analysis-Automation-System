# app.py
"""
Workforce Analytics & Employee Management System
- Professional single-page dashboard
- Role-based login (Admin, Manager, HR, Employee)
- Employee CRUD & CSV import
- Mood tracking, Task management, Feedback
- Workforce analytics dashboards & PDF export
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import random
import io

# Local utilities
from utils import database as db
from utils.auth import require_login, logout_user, show_role_badge
from utils.analytics import get_summary, department_distribution, gender_ratio, average_salary_by_dept
from utils.pdf_export import generate_summary_pdf

st.set_page_config(page_title="Workforce Analytics System", page_icon="👩‍💼", layout="wide")

# -------------------------
# Initialize Database
# -------------------------
try:
    db.create_tables()  # Use create_tables() instead of initialize_all_tables
except Exception as e:
    st.error("❌ Failed to initialize database.")
    st.exception(e)
    st.stop()

# -------------------------
# Login / Role Badge / Logout
# -------------------------
require_login()
show_role_badge()
logout_user()

role = st.session_state.get("role", "Employee")
username = st.session_state.get("user", "Unknown")

# -------------------------
# Load Employees
# -------------------------
try:
    df = db.fetch_employees()
except Exception as e:
    df = pd.DataFrame()
    st.error("Failed to load employees.")
    st.exception(e)

# -------------------------
# Auto-generate employees if DB empty
# -------------------------
if df.empty:
    st.info("No employees found. Generating dataset...")

    def generate_employees(n=80):
        depts = ["HR", "IT", "Sales", "Finance", "Marketing", "Support"]
        roles = {
            "HR": ["HR Manager", "HR Executive"],
            "IT": ["Developer", "SysAdmin", "IT Manager"],
            "Sales": ["Sales Executive", "Sales Manager"],
            "Finance": ["Accountant", "Finance Manager"],
            "Marketing": ["Marketing Executive", "Marketing Manager"],
            "Support": ["Support Executive", "Support Manager"]
        }
        skills = ["Python", "SQL", "Excel", "PowerPoint", "Communication", "Leadership", "Analytics", "JavaScript"]
        names_m = ["John", "Alex", "Michael", "David", "Chris", "Liam"]
        names_f = ["Sophia", "Emma", "Chloe", "Ava", "Mia", "Isabella"]

        employees = []
        for _ in range(n):
            gender = random.choice(["Male", "Female"])
            name = random.choice(names_m if gender == "Male" else names_f)
            dept = random.choice(depts)
            role_c = random.choice(roles[dept])
            age = random.randint(22, 60)
            salary = random.randint(30000, 120000)
            location = random.choice(["Bangalore", "Delhi", "Mumbai", "Chennai", "Hyderabad"])
            join_dt = (datetime.datetime.now() - datetime.timedelta(days=random.randint(200, 3000))).strftime("%Y-%m-%d")
            status = random.choices(["Active", "Resigned"], weights=[80,20])[0]
            resign_dt = ""
            if status == "Resigned":
                resign_dt = (datetime.datetime.now() - datetime.timedelta(days=random.randint(30, 500))).strftime("%Y-%m-%d")
            emp = {
                "Name": name,
                "Age": age,
                "Gender": gender,
                "Department": dept,
                "Role": role_c,
                "Skills": ", ".join(random.sample(skills, 3)),
                "Join_Date": join_dt,
                "Resign_Date": resign_dt,
                "Status": status,
                "Salary": salary,
                "Location": location
            }
            employees.append(emp)
        return pd.DataFrame(employees)

    df_gen = generate_employees(80)
    for _, row in df_gen.iterrows():
        db.add_employee(row.to_dict())
    df = db.fetch_employees()
    st.success("✔ Realistic employees generated.")

# -------------------------
# Role-Based Sidebar Tabs
# -------------------------
tabs = []
if role in ["Admin", "Manager", "HR"]:
    tabs = ["Employees", "Tasks", "Mood Tracker", "Feedback", "Analytics"]
elif role == "Employee":
    tabs = ["Tasks", "Mood Tracker", "Feedback", "Analytics"]

tab = st.sidebar.radio("Select Module", tabs)

# -------------------------
# Employees Module
# -------------------------
if tab == "Employees" and role in ["Admin", "Manager", "HR"]:
    st.header("👩‍💼 Employee Management")

    # Filters
    st.sidebar.header("Filters")
    f_dept   = st.sidebar.selectbox("Department", ["All"] + sorted(df["Department"].dropna().unique()))
    f_status = st.sidebar.selectbox("Status", ["All"] + sorted(df["Status"].dropna().unique()))
    f_gender = st.sidebar.selectbox("Gender", ["All", "Male", "Female"])
    f_role   = st.sidebar.selectbox("Role", ["All"] + sorted(df["Role"].dropna().unique()))

    filtered = df.copy()
    if f_dept != "All": filtered = filtered[filtered["Department"] == f_dept]
    if f_status != "All": filtered = filtered[filtered["Status"] == f_status]
    if f_gender != "All": filtered = filtered[filtered["Gender"] == f_gender]
    if f_role != "All": filtered = filtered[filtered["Role"] == f_role]

    search = st.text_input("Search by Name / Role / Skills / ID").lower().strip()
    disp = filtered.copy()
    if search:
        mask = (
            disp["Name"].astype(str).str.lower().str.contains(search, na=False) |
            disp["Role"].astype(str).str.lower().str.contains(search, na=False) |
            disp["Skills"].astype(str).str.lower().str.contains(search, na=False) |
            disp["Emp_ID"].astype(str).str.contains(search, na=False)
        )
        disp = disp[mask]

    st.dataframe(disp[["Emp_ID","Name","Department","Role","Join_Date","Status"]], height=400)

    # CSV Upload
    st.subheader("📁 Import Employees CSV")
    upload = st.file_uploader("Upload CSV", type=["csv"])
    if upload:
        try:
            df_u = pd.read_csv(upload)
            required_cols = ["Name","Age","Gender","Department","Role","Skills","Join_Date","Resign_Date","Status","Salary","Location"]
            for col in required_cols:
                if col not in df_u.columns:
                    df_u[col] = ""
            for _, row in df_u.iterrows():
                db.add_employee(row.to_dict())
            st.success("CSV imported successfully!")
        except Exception as e:
            st.error("CSV import failed.")
            st.exception(e)

# -------------------------
# Tasks Module
# -------------------------
elif tab == "Tasks":
    from pages import tasks as task
    task.show()

# -------------------------
# Mood Tracker Module
# -------------------------
elif tab == "Mood Tracker":
    from pages import mood_tracker as mood
    mood.show()

# -------------------------
# Feedback Module
# -------------------------
elif tab == "Feedback":
    from pages import feedback as fb
    fb.show()

# -------------------------
# Analytics Module
# -------------------------
elif tab == "Analytics":
    st.header("📊 Workforce Analytics & Summary")
    filtered = df.copy()
    summary = get_summary(filtered)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Employees", summary["total"])
    c2.metric("Active", summary["active"])
    c3.metric("Resigned", summary["resigned"])

    # Department Distribution
    dept_counts = department_distribution(filtered)
    fig, ax = plt.subplots(figsize=(8,4))
    ax.bar(dept_counts.index, dept_counts.values)
    ax.set_xlabel("Department")
    ax.set_ylabel("Employees")
    ax.set_title("Employees by Department")
    plt.xticks(rotation=30)
    st.pyplot(fig)

    # Gender Ratio
    g = gender_ratio(filtered)
    fig2, ax2 = plt.subplots(figsize=(5,5))
    ax2.pie(g.values, labels=g.index, autopct="%1.1f%%")
    ax2.set_title("Gender Split")
    st.pyplot(fig2)

    # Average Salary
    sal = average_salary_by_dept(filtered)
    fig3, ax3 = plt.subplots(figsize=(8,4))
    ax3.bar(sal.index, sal.values)
    ax3.set_xlabel("Department")
    ax3.set_ylabel("Average Salary")
    ax3.set_title("Department-wise Salary")
    plt.xticks(rotation=30)
    st.pyplot(fig3)

    # PDF Export
    st.subheader("📄 Export PDF Summary")
    pdf_buffer = io.BytesIO()
    if st.button("Generate PDF"):
        try:
            generate_summary_pdf(
                buffer=pdf_buffer,
                total=summary["total"],
                active=summary["active"],
                resigned=summary["resigned"],
                df=filtered,
                mood_df=db.fetch_mood_logs(),
                dept_fig=fig,
                gender_fig=fig2,
                salary_fig=fig3,
                title="Workforce Summary Report"
            )
            st.download_button(
                label="Download PDF",
                data=pdf_buffer,
                file_name="workforce_summary_report.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error("Failed to generate PDF.")
            st.exception(e)
