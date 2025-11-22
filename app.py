# app.py
"""
Workforce Analytics & Employee Management System
- Role-based login
- Employee CRUD
- Mood tracking
- Task management
- Workforce analytics dashboards
- PDF export system
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
# Initialize DB
# -------------------------
try:
    db.initialize_all_tables()
except Exception as e:
    st.error("❌ Failed to initialize database.")
    st.exception(e)
    st.stop()

# -------------------------
# Login
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
# Sidebar Filters
# -------------------------
st.sidebar.header("Filters")
st.sidebar.markdown(f"Logged in as: **{username}** ({role})")

def safe_opts(df_local, col):
    return ["All"] + sorted(df_local[col].dropna().unique().tolist()) if col in df_local.columns else ["All"]

f_dept   = st.sidebar.selectbox("Department", safe_opts(df, "Department"))
f_status = st.sidebar.selectbox("Status", safe_opts(df, "Status"))
f_gender = st.sidebar.selectbox("Gender", ["All", "Male", "Female"])
f_role   = st.sidebar.selectbox("Role", safe_opts(df, "Role"))

# -------------------------
# CSV Upload
# -------------------------
if role in ("Admin", "Manager"):
    st.sidebar.header("📁 Import CSV")
    upload = st.sidebar.file_uploader("Upload CSV", type=["csv"])
    if upload:
        try:
            df_u = pd.read_csv(upload)
            required = ["Name","Age","Gender","Department","Role","Skills","Join_Date","Resign_Date","Status","Salary","Location"]
            for col in required:
                if col not in df_u.columns:
                    df_u[col] = ""
            for _, row in df_u.iterrows():
                db.add_employee(row.to_dict())
            st.success("CSV imported successfully!")
            st.session_state["refresh_flag"] = random.random()
        except Exception as e:
            st.error("CSV import failed.")
            st.exception(e)

# -------------------------
# Apply Filters
# -------------------------
filtered = df.copy()
if f_dept != "All":   filtered = filtered[filtered["Department"] == f_dept]
if f_status != "All": filtered = filtered[filtered["Status"] == f_status]
if f_gender != "All": filtered = filtered[filtered["Gender"] == f_gender]
if f_role != "All":   filtered = filtered[filtered["Role"] == f_role]

# -------------------------
# Employee Records Table
# -------------------------
st.title("👩‍💼 Workforce Analytics System")
st.header("1️⃣ Employee Records")

search = st.text_input("Search (Name / Role / Skills / ID)").lower().strip()
disp = filtered.copy()
if search:
    cond = (
        disp["Name"].astype(str).str.lower().str.contains(search, na=False) |
        disp["Role"].astype(str).str.lower().str.contains(search, na=False) |
        disp["Skills"].astype(str).str.lower().str.contains(search, na=False) |
        disp["Emp_ID"].astype(str).str.contains(search, na=False)
    )
    disp = disp[cond]

sort_col = st.selectbox("Sort by", disp.columns.tolist(), index=0)
sort_order = st.radio("Order", ["Ascending", "Descending"], horizontal=True) == "Ascending"
try: disp = disp.sort_values(sort_col, ascending=sort_order)
except: pass

st.dataframe(disp[["Emp_ID","Name","Department","Role","Join_Date","Status"]], height=420)
st.markdown("---")

# -------------------------
# Summary Metrics
# -------------------------
st.header("2️⃣ Workforce Summary")
summary = get_summary(filtered)
c1, c2, c3 = st.columns(3)
c1.metric("Total", summary["total"])
c2.metric("Active", summary["active"])
c3.metric("Resigned", summary["resigned"])
st.markdown("---")

# -------------------------
# Charts
# -------------------------
# Department
st.header("3️⃣ Department Distribution")
dept_fig = None
if not filtered.empty:
    dept_counts = department_distribution(filtered)
    fig, ax = plt.subplots(figsize=(8,4))
    ax.bar(dept_counts.index, dept_counts.values)
    ax.set_xlabel("Department")
    ax.set_ylabel("Employees")
    ax.set_title("Employees by Department")
    plt.xticks(rotation=30)
    st.pyplot(fig)
    dept_fig = fig
else: st.info("No data available.")
st.markdown("---")

# Gender
st.header("4️⃣ Gender Ratio")
gender_fig = None
if not filtered.empty:
    g = gender_ratio(filtered)
    fig, ax = plt.subplots(figsize=(5,5))
    ax.pie(g.values, labels=g.index, autopct="%1.1f%%")
    ax.set_title("Gender Split")
    st.pyplot(fig)
    gender_fig = fig
else: st.info("No data available.")
st.markdown("---")

# Salary
st.header("5️⃣ Average Salary by Department")
salary_fig = None
if not filtered.empty:
    sal = average_salary_by_dept(filtered)
    fig, ax = plt.subplots(figsize=(8,4))
    ax.bar(sal.index, sal.values)
    ax.set_xlabel("Department")
    ax.set_ylabel("Average Salary")
    ax.set_title("Department-wise Salary")
    plt.xticks(rotation=30)
    st.pyplot(fig)
    salary_fig = fig
else: st.info("No data available.")
st.markdown("---")

# -------------------------
# PDF Export
# -------------------------
st.subheader("📄 Download Workforce PDF")
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
            dept_fig=dept_fig,
            gender_fig=gender_fig,
            salary_fig=salary_fig,
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
