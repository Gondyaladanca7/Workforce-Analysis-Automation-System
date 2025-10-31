# Add Employee Page
"""
Add Employee — Workforce Analytics System
Allows adding new employees via a form, validates inputs, and inserts into database.
Integrates with utils.database and utils.analytics.
"""

import streamlit as st
import pandas as pd
from datetime import date
from utils import database as db

# -------------------------
st.set_page_config(page_title="Add Employee", page_icon="➕", layout="wide")
st.title("➕ Add New Employee")

# -------------------------
# Load existing employee data to get next ID
try:
    df = db.fetch_employees()
except Exception as e:
    st.error("Failed to fetch employee data from database.")
    st.exception(e)
    df = pd.DataFrame(columns=["Emp_ID","Name","Age","Gender","Department","Role",
                               "Skills","Join_Date","Resign_Date","Status","Salary","Location"])

# -------------------------
# Sidebar: Employee Form
st.sidebar.header("Fill Employee Details")

with st.sidebar.form("add_employee_form"):
    # Auto-generate Employee ID
    try:
        next_emp_id = int(df["Emp_ID"].max()) + 1 if ("Emp_ID" in df.columns and not df["Emp_ID"].empty) else 1
    except Exception:
        next_emp_id = 1

    emp_id = st.number_input("Employee ID", value=next_emp_id, step=1, format="%d")
    emp_name = st.text_input("Full Name")
    age = st.number_input("Age", min_value=18, step=1, format="%d")
    gender_val = st.selectbox("Gender", ["Male", "Female", "Other"])
    department = st.text_input("Department")
    role = st.text_input("Role")
    skills = st.text_input("Skills (semicolon separated)")
    join_date = st.date_input("Join Date", value=date.today())
    status = st.selectbox("Status", ["Active", "Resigned"])
    resign_date = st.date_input("Resign Date (if resigned)", value=date.today())
    if status == "Active":
        resign_date = ""
    salary = st.number_input("Salary", min_value=0, step=1000, format="%d")
    location = st.text_input("Location")

    submit = st.form_submit_button("Add Employee")

# -------------------------
# Submit Handling
if submit:
    # Validate required fields
    if not emp_name.strip():
        st.warning("Employee Name is required.")
    elif not department.strip():
        st.warning("Department is required.")
    elif not role.strip():
        st.warning("Role is required.")
    else:
        # Prepare new employee dictionary
        new_row = {
            "Emp_ID": int(emp_id),
            "Name": emp_name.strip(),
            "Age": int(age),
            "Gender": gender_val,
            "Department": department.strip(),
            "Role": role.strip(),
            "Skills": skills.strip() if skills else "NA",
            "Join_Date": str(join_date),
            "Resign_Date": str(resign_date) if status == "Resigned" else "",
            "Status": status,
            "Salary": float(salary),
            "Location": location.strip() if location else "NA"
        }

        # Insert into database
        try:
            db.add_employee(new_row)
            st.success(f"Employee **{emp_name}** added successfully!")
            st.experimental_rerun()
        except Exception as e:
            st.error("Failed to add employee to database.")
            st.exception(e)

# -------------------------
# Optional: Show Recent Employees Table
st.header("📋 Recently Added Employees")
try:
    if not df.empty:
        recent_df = df.sort_values(by="Join_Date", ascending=False).head(10)
        st.dataframe(recent_df[["Emp_ID","Name","Department","Role","Join_Date","Status"]])
    else:
        st.info("No employees in database yet.")
except Exception as e:
    st.error("Error displaying recent employees.")
    st.exception(e)
