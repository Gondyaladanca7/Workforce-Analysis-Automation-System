# app.py
"""
Workforce Analytics & Employee Management System
Full application file — copy & replace your existing app.py with this.
Authentication: simple bcrypt-based local login for user GOVIND / LADU (dev only).
Database: uses utils.database (SQLite) for persistence.
Analytics helpers: utils.analytics
PDF export: utils.pdf_export.generate_summary_pdf
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64
import datetime
import bcrypt
from utils.pdf_export import generate_summary_pdf
from utils.analytics import *   # get_summary, department_distribution, gender_ratio, average_salary_by_dept
from utils import database as db
from typing import Dict

# -------------------------
# Page config
# -------------------------
st.set_page_config(page_title="Workforce Analytics System", page_icon="👩‍💼", layout="wide")

# -------------------------
# Simple authentication (self-contained, avoids streamlit-authenticator version issues)
# Development usage only. Username: GOVIND, Password: LADU
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

# Dev credentials (change before any public deployment)
PLAIN_USERNAME = "GOVIND"
PLAIN_PASSWORD = "LADU"

# Compute bcrypt hash at runtime (ok for local dev)
stored_hash = bcrypt.hashpw(PLAIN_PASSWORD.encode("utf-8"), bcrypt.gensalt())

def check_credentials(username: str, password: str) -> bool:
    if username is None or password is None:
        return False
    if username.strip().upper() != PLAIN_USERNAME:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), stored_hash)
    except Exception:
        return False

# -------------------------
# Login UI (if not logged in)
# -------------------------
def show_login():
    st.title("🔐 Login — Workforce Analytics System")
    st.write("Use dev credentials for local testing.")
    col1, col2 = st.columns(2)
    with col1:
        username_input = st.text_input("Username")
    with col2:
        password_input = st.text_input("Password", type="password")

    if st.button("Login"):
        if check_credentials(username_input, password_input):
            st.session_state.logged_in = True
            st.session_state.user = username_input.strip().upper()
            st.rerun()
        else:
            st.error("Incorrect username or password")

# If not logged in, show login and stop
if not st.session_state.logged_in:
    show_login()
    st.stop()

# -------------------------
# Logged-in dashboard
# -------------------------
auth_user = st.session_state.user or PLAIN_USERNAME
st.sidebar.success(f"Welcome {auth_user} 👋")
st.title("👩‍💼 Workforce Analytics System")

# Logout button
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

# -------------------------
# Initialize DB & load data
# -------------------------
try:
    db.initialize_database()
except Exception as e:
    st.error("Failed to initialize database.")
    st.exception(e)
    st.stop()

try:
    df = db.fetch_employees()
except Exception as e:
    st.error("Failed to load employee data from database.")
    st.exception(e)
    # Create empty DataFrame with expected columns so UI still works
    df = pd.DataFrame(columns=["Emp_ID","Name","Age","Gender","Department","Role","Skills","Join_Date","Resign_Date","Status","Salary","Location"])

# -------------------------
# Sidebar: CSV upload (robust)
# -------------------------
st.sidebar.header("📁 Import Employee Data from CSV")
uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
if uploaded_file:
    try:
        df_uploaded = pd.read_csv(uploaded_file)

        # required columns with defaults (Emp_ID handled specially)
        required_cols: Dict[str, object] = {
            "Emp_ID": None,
            "Name": "NA",
            "Age": 0,
            "Gender": "NA",
            "Department": "NA",
            "Role": "NA",
            "Skills": "NA",
            "Join_Date": "",
            "Resign_Date": "",
            "Status": "Active",
            "Salary": 0.0,
            "Location": "NA"
        }

        # Add missing columns (except Emp_ID)
        for col, default in required_cols.items():
            if col not in df_uploaded.columns and col != "Emp_ID":
                df_uploaded[col] = default

        # Prepare existing IDs and next id generator
        existing_ids = set(df['Emp_ID'].dropna().astype(int).tolist()) if not df.empty else set()
        next_id = max(existing_ids) + 1 if existing_ids else 1

        # Ensure Emp_ID column exists (nullable)
        if "Emp_ID" not in df_uploaded.columns:
            df_uploaded["Emp_ID"] = [None] * len(df_uploaded)

        # Insert each row into DB safely
        for _, row in df_uploaded.iterrows():
            row_dict = row.to_dict()

            # Determine emp id
            try:
                eid = int(row_dict.get("Emp_ID")) if pd.notna(row_dict.get("Emp_ID")) else None
            except Exception:
                eid = None

            if eid is None or (eid in existing_ids):
                eid = next_id
                next_id += 1

            emp = {
                "Emp_ID": int(eid),
                "Name": str(row_dict.get("Name")) if pd.notna(row_dict.get("Name")) else required_cols["Name"],
                "Age": int(row_dict.get("Age")) if pd.notna(row_dict.get("Age")) else required_cols["Age"],
                "Gender": str(row_dict.get("Gender")) if pd.notna(row_dict.get("Gender")) else required_cols["Gender"],
                "Department": str(row_dict.get("Department")) if pd.notna(row_dict.get("Department")) else required_cols["Department"],
                "Role": str(row_dict.get("Role")) if pd.notna(row_dict.get("Role")) else required_cols["Role"],
                "Skills": str(row_dict.get("Skills")) if pd.notna(row_dict.get("Skills")) else required_cols["Skills"],
                "Join_Date": str(row_dict.get("Join_Date")) if pd.notna(row_dict.get("Join_Date")) else required_cols["Join_Date"],
                "Resign_Date": str(row_dict.get("Resign_Date")) if pd.notna(row_dict.get("Resign_Date")) else required_cols["Resign_Date"],
                "Status": str(row_dict.get("Status")) if pd.notna(row_dict.get("Status")) else required_cols["Status"],
                "Salary": float(row_dict.get("Salary")) if pd.notna(row_dict.get("Salary")) else float(required_cols["Salary"]),
                "Location": str(row_dict.get("Location")) if pd.notna(row_dict.get("Location")) else required_cols["Location"],
            }

            db.add_employee(emp)
            existing_ids.add(emp["Emp_ID"])

        st.success("CSV uploaded successfully and added to database!")
        st.rerun()

    except Exception as e:
        st.error("Failed to process CSV")
        st.exception(e)

# -------------------------
# Sidebar: Filters
# -------------------------
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
if selected_dept != "All" and "Department" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Department"] == selected_dept]
if selected_status != "All" and "Status" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Status"] == selected_status]
if selected_gender != "All" and "Gender" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Gender"] == selected_gender]
if selected_role != "All" and "Role" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Role"] == selected_role]
if selected_skills != "All" and "Skills" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Skills"] == selected_skills]

# -------------------------
# Main: Employee Table (search, sort, highlight)
# -------------------------
st.header("1️⃣ Raw Employee Data")

search_term = st.text_input("Search by Name, ID, Skills, or Role").strip()
display_df = filtered_df.copy()

if search_term:
    cond = pd.Series([False] * len(display_df), index=display_df.index)
    for col in ["Name", "Emp_ID", "Skills", "Role"]:
        if col in display_df.columns:
            cond = cond | display_df[col].astype(str).str.contains(search_term, case=False, na=False)
    display_df = display_df[cond]

# Sorting controls
available_sort_cols = [c for c in ["Emp_ID", "Name", "Age", "Salary", "Join_Date", "Department", "Role", "Skills"] if c in display_df.columns]
if not available_sort_cols:
    available_sort_cols = display_df.columns.tolist()
sort_col = st.selectbox("Sort by", options=available_sort_cols, index=0)
ascending = st.radio("Order", ["Ascending", "Descending"], horizontal=True) == "Ascending"

try:
    if sort_col in display_df.columns:
        display_df = display_df.sort_values(by=sort_col, ascending=ascending, key=lambda s: s.astype(str))
except Exception:
    pass

# Force plain white background & black font for table display
try:
    styled = display_df.style.set_properties(**{"background-color": "white", "color": "black"})
    st.dataframe(styled, height=420)
except Exception:
    st.dataframe(display_df, height=420)

# -------------------------
# Delete employee
# -------------------------
st.subheader("🗑️ Delete Employee")
delete_id = st.number_input("Enter Employee ID to delete", step=1, format="%d")
if st.button("Delete Employee"):
    try:
        if "Emp_ID" in df.columns and int(delete_id) in df["Emp_ID"].astype(int).values:
            db.delete_employee(int(delete_id))
            st.success(f"Employee ID {delete_id} deleted successfully!")
            st.rerun()
        else:
            st.warning(f"No employee found with ID {delete_id}")
    except Exception as e:
        st.error("Failed to delete employee.")
        st.exception(e)

# -------------------------
# Summary & Analytics
# -------------------------
st.header("2️⃣ Summary")
try:
    total, active, resigned = get_summary(filtered_df) if not filtered_df.empty else (0, 0, 0)
    st.write(f"Total Employees: **{total}**")
    st.write(f"Active Employees: **{active}**")
    st.write(f"Resigned Employees: **{resigned}**")
except Exception as e:
    st.error("Error computing summary.")
    st.exception(e)

# Department-wise count
st.header("3️⃣ Department-wise Employee Count")
try:
    if not filtered_df.empty and "Department" in filtered_df.columns:
        st.bar_chart(department_distribution(filtered_df))
    else:
        st.info("Department chart requires 'Department' column in data.")
except Exception as e:
    st.error("Error plotting department distribution.")
    st.exception(e)

# Gender Ratio
st.header("4️⃣ Gender Ratio")
try:
    if not filtered_df.empty and "Gender" in filtered_df.columns:
        gender = gender_ratio(filtered_df)
        fig, ax = plt.subplots()
        ax.pie(gender, labels=gender.index, autopct="%1.1f%%")
        st.pyplot(fig)
    else:
        st.info("Gender ratio requires 'Gender' column in data.")
except Exception as e:
    st.error("Error creating gender ratio plot.")
    st.exception(e)

# Average salary by department
st.header("5️⃣ Average Salary by Department")
try:
    if not filtered_df.empty and "Department" in filtered_df.columns and "Salary" in filtered_df.columns:
        st.bar_chart(average_salary_by_dept(filtered_df))
    else:
        st.info("Average salary chart requires 'Department' and 'Salary' columns.")
except Exception as e:
    st.error("Error plotting average salary by department.")
    st.exception(e)

# -------------------------
# Add New Employee Form
# -------------------------
st.sidebar.header("➕ Add New Employee")
with st.sidebar.form("add_employee_form"):
    try:
        next_emp_id = int(df["Emp_ID"].max()) + 1 if ("Emp_ID" in df.columns and not df["Emp_ID"].empty) else 1
    except Exception:
        next_emp_id = 1

    emp_id = st.number_input("Employee ID", value=next_emp_id, step=1, format="%d")
    emp_name = st.text_input("Name")
    age = st.number_input("Age", step=1, format="%d")
    gender_val = st.selectbox("Gender", ["Male", "Female", "Other"])
    department = st.selectbox("Department", sorted(df["Department"].dropna().unique().tolist())) if ("Department" in df.columns and not df["Department"].dropna().empty) else st.text_input("Department")
    role = st.text_input("Role")
    skills = st.text_input("Skills (semicolon separated)")
    join_date = st.date_input("Join Date")
    status = st.selectbox("Status", ["Active", "Resigned"])
    resign_date = st.date_input("Resign Date (if resigned)")
    if status == "Active":
        resign_date = ""
    salary = st.number_input("Salary", step=1000, format="%d")
    location = st.text_input("Location")

    submit = st.form_submit_button("Add Employee")
    if submit:
        new_row = {
            "Emp_ID": int(emp_id),
            "Name": emp_name or "NA",
            "Age": int(age),
            "Gender": gender_val or "NA",
            "Department": department or "NA",
            "Role": role or "NA",
            "Skills": skills or "NA",
            "Join_Date": str(join_date),
            "Resign_Date": str(resign_date) if status == "Resigned" else "",
            "Status": status,
            "Salary": float(salary),
            "Location": location or "NA"
        }
        try:
            db.add_employee(new_row)
            st.success(f"Employee {emp_name} added successfully!")
            st.rerun()
        except Exception as e:
            st.error("Failed to add employee.")
            st.exception(e)

# -------------------------
# Export Summary PDF
# -------------------------
st.subheader("📄 Export Summary Report")
if st.button("Download Summary PDF"):
    try:
        pdf_path = "summary_report.pdf"
        generate_summary_pdf(pdf_path, total, active, resigned)
        with open(pdf_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode("utf-8")
            href = f'<a href="data:application/pdf;base64,{base64_pdf}" download="summary_report.pdf">📥 Click here to download PDF</a>'
            st.markdown(href, unsafe_allow_html=True)
    except Exception as e:
        st.error("Failed to generate PDF.")
        st.exception(e)
